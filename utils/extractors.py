import pandas as pd
from datetime import datetime,date
import requests


import openmeteo_requests
import requests_cache
import pandas as pd
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


# def fetch_weather_data_meteo(latitude, longitude, start_date, end_date):
#     # Setup the Open-Meteo API client with cache and retry on error
#     cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
#     retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
#     openmeteo = openmeteo_requests.Client(session=retry_session)
#     hourly_vars = "temperature_2m,dewpoint_2m,relative_humidity_2m,surface_pressure,precipitation,snowfall,windspeed_10m,winddirection_10m,windgusts_10m,cloudcover,shortwave_radiation,direct_radiation,direct_normal_irradiance,diffuse_radiation,global_tilted_irradiance"
#     # hourly_vars = "temperature_2m,dewpoint_2m,relative_humidity_2m,surface_pressure,precipitation,snowfall,windspeed_10m,winddirection_10m,windgusts_10m,cloudcover,shortwave_radiation,visibility,evapotranspiration,soil_temperature_0_7cm,soil_moisture_0_7cm"

#     # Construct the API request URL and parameters
#     url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
#     params = {
#         "latitude": latitude,
#         "longitude": longitude,
#         "start_date": start_date,
#         "end_date": end_date,
#         "hourly": hourly_vars
#     }

#     # Make the API request
#     responses = openmeteo.weather_api(url, params=params)

#     # Process the response for the first location (modify for multiple locations if needed)
#     response = responses[0]

#     # Extract hourly data
#     hourly = response.Hourly()
#     hourly_data = {
#         "date": pd.date_range(
#             start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
#             end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
#             freq=pd.Timedelta(seconds=hourly.Interval()),
#             inclusive="left"
#         )
#     }

#     # Extract and add all requested variables to the DataFrame
#     for i, var in enumerate(hourly_vars.split(',')):
#         variable_name = var.strip()
#         variable_values = hourly.Variables(i).ValuesAsNumpy()
#         hourly_data[variable_name] = variable_values

#     # Convert the data to a DataFrame
#     hourly_dataframe = pd.DataFrame(data=hourly_data)

#     return hourly_dataframe
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

def process_weather_response(response):
    """
    Process the weather API response and convert it to a DataFrame.
    """
    hourly = response.Hourly()
    hourly_data = {
        "datetime": pd.to_datetime(hourly.Time(), unit="s", utc=True),
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
    return pd.DataFrame(hourly_data)

def fetch_all_weather_data(start_date, end_date, latitude, longitude):
    """
    Fetch weather data for a range of dates, handling up to 30 days at a time.
    """
    date_ranges = generate_date_ranges(start_date, end_date, delta_days=30)
    all_data_frames = []
    
    for start, end in date_ranges:
        print(f"Fetching data from {start} to {end}")
        response = fetch_weather_data(start, end, latitude, longitude)
        df = process_weather_response(response)
        all_data_frames.append(df)
    
    # Combine all DataFrames into one
    all_data = pd.concat(all_data_frames, ignore_index=True)
    all_data.set_index('datetime', inplace=True)
    return all_data

# Example usage
latitude = 52.52
longitude = 13.41
start_date = date(2021,9,8)
end_date = date(2022,6,7)
weather_data_df = fetch_all_weather_data(start_date, end_date, latitude, longitude)
print(f"example of weather data from meteo\n: {weather_data_df}")
