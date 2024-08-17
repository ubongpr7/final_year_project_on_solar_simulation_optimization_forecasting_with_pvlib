import pandas as pd
from datetime import datetime,date
import requests


import openmeteo_requests
import requests_cache
from datetime import datetime, timedelta
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)




def convert_unix_to_datetime(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')


def convert_to_unix_time(date_str):
    if isinstance(date_str, (datetime, date)):
        if isinstance(date_str, date):
            dt = datetime.combine(date_str, datetime.min.time())  # Convert date to datetime
        else:
            dt = date_str  # It’s already a datetime object
    else:
        dt = datetime.strptime(date_str, "%Y-%m-%d")  # Convert string to datetime
    
    unix_time = int(dt.timestamp())
    return unix_time


def get_solar_irradiation(lat, lon, start, end, tz, api_key='297b91bc87fac0f26c4d65efa6eb2443'):
    
    # Convert start and end dates from yyyy-mm-dd to Unix time
    start_unix = convert_to_unix_time(start)
    end_unix = convert_to_unix_time(end)
    
    url = "https://history.openweathermap.org/data/2.5/history/city"
    params = {
        'lat': lat,
        'lon': lon,
        'date': start_unix,
        'end': end_unix,
        'tz': tz,
        'APPID': api_key,
        'type': 'hour',
        'units': 'metric'
    }
    
    response = requests.get(url, params=params)
    print(f'Response Status Code: {response.status_code}')

         
    if response.status_code == 200:
        data = response.json()
        print(f"Solar Irradiation Data for {lat}, {lon} from {start} to {end}:")
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None


from datetime import datetime, timedelta

def generate_date_ranges(start_date, end_date, delta_days=30):
    """
    Generate a list of date ranges, each with a maximum length of delta_days.
    """
    # If start_date and end_date are datetime.date objects, convert them to datetime
    if isinstance(start_date, datetime):
        start = start_date
    else:
        start = datetime.combine(start_date, datetime.min.time())
    
    if isinstance(end_date, datetime):
        end = end_date
    else:
        end = datetime.combine(end_date, datetime.min.time())
    
    ranges = []

    # Handle the case where the range is shorter than delta_days
    if (end - start).days <= delta_days:
        ranges.append((start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))
    else:
        while start < end:
            range_end = min(start + timedelta(days=delta_days - 1), end)
            ranges.append((start.strftime("%Y-%m-%d"), range_end.strftime("%Y-%m-%d")))
            start = range_end + timedelta(days=1)
    
    return ranges

def fetch_weather_data(start_date, end_date, latitude, longitude):
    """
    Fetch weather data from Open-Meteo API for a given date range and location.
    """
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,dewpoint_2m,relative_humidity_2m,surface_pressure,precipitation,snowfall,windspeed_10m,winddirection_10m,windgusts_10m,cloudcover,shortwave_radiation,direct_radiation,direct_normal_irradiance,diffuse_radiation,global_tilted_irradiance"
    }
    responses = openmeteo.weather_api(url, params=params)
    return responses[0]

def process_weather_response(response, user_timezone="Europe/Berlin"):
    """
    Process the weather API response and convert it to a DataFrame with correctly spaced datetime indices.
    """
    hourly = response.Hourly()

    # If `hourly.Time()` returns a single timestamp
    first_timestamp = pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert(user_timezone)

    # Assuming the interval between data points is 1 hour (3600 seconds)
    interval_seconds = 3600

    # Generate the datetime index using the first timestamp and the number of periods
    date_range = pd.date_range(
        start=first_timestamp,
        periods=len(hourly.Variables(0).ValuesAsNumpy()),  # Assuming the number of periods matches the length of data
        freq=pd.Timedelta(seconds=interval_seconds)
    )
    
    # Create a dictionary for the DataFrame
    hourly_data = {
        "datetime": date_range,
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "dewpoint_2m": hourly.Variables(1).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(2).ValuesAsNumpy(),
        "surface_pressure": hourly.Variables(3).ValuesAsNumpy(),
        "precipitation": hourly.Variables(4).ValuesAsNumpy(),
        "snowfall": hourly.Variables(5).ValuesAsNumpy(),
        "windspeed_10m": hourly.Variables(6).ValuesAsNumpy(),
        "winddirection_10m": hourly.Variables(7).ValuesAsNumpy(),
        "windgusts_10m": hourly.Variables(8).ValuesAsNumpy(),
        "cloudcover": hourly.Variables(9).ValuesAsNumpy(),
        "shortwave_radiation": hourly.Variables(10).ValuesAsNumpy(),
        "direct_radiation": hourly.Variables(11).ValuesAsNumpy(),
        "direct_normal_irradiance": hourly.Variables(12).ValuesAsNumpy(),
        "diffuse_radiation": hourly.Variables(13).ValuesAsNumpy(),
        "global_tilted_irradiance": hourly.Variables(14).ValuesAsNumpy()
    }
    
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(hourly_data)
    
    # Set datetime as the index
    # df.set_index("datetime", inplace=True)
    
    return df


def fetch_all_weather_data(start_date, end_date, latitude, longitude,user_timezone):
    """
    Fetch weather data for a range of dates, handling up to 30 days at a time.
    """
    date_ranges = generate_date_ranges(start_date, end_date, delta_days=30)
    all_data_frames = []
    
    for start, end in date_ranges:
        print(f"Fetching data from {start} to {end}")
        response = fetch_weather_data(start, end, latitude, longitude)
        df = process_weather_response(response,user_timezone)
        all_data_frames.append(df)
    
    # Combine all DataFrames into one
    all_data = pd.concat(all_data_frames, ignore_index=True)
    all_data.set_index('datetime', inplace=True)
    return all_data
