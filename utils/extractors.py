import pandas as pd
from datetime import datetime,date
import requests


def convert_unix_to_datetime(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')

def extract_weather_data_to_df(data):
    # Prepare a list to hold the rows of data
    weather_data = []

    for item in data.get('list', []):
        dt = convert_unix_to_datetime(item.get('dt'))
        temp = item['main'].get('temp')
        feels_like = item['main'].get('feels_like')
        pressure = item['main'].get('pressure')
        humidity = item['main'].get('humidity')
        temp_min = item['main'].get('temp_min')
        temp_max = item['main'].get('temp_max')
        wind_speed = item['wind'].get('speed')
        wind_deg = item['wind'].get('deg')
        clouds_all = item['clouds'].get('all')
        weather_main = item['weather'][0].get('main') if item.get('weather') else None
        weather_description = item['weather'][0].get('description') if item.get('weather') else None
        rain_1h = item['rain'].get('1h', 0) if item.get('rain') else 0

        # Append the extracted data as a row in the weather_data list
        weather_data.append([
            dt, temp, feels_like, pressure, humidity, temp_min, temp_max,
            wind_speed, wind_deg, clouds_all, weather_main, weather_description, rain_1h
        ])
    
    # Create a DataFrame from the collected data
    df = pd.DataFrame(weather_data, columns=[
        'datetime', 'temp', 'feels_like', 'pressure', 'humidity',
        'temp_min', 'temp_max', 'wind_speed', 'wind_deg', 'clouds_all',
        'weather_main', 'weather_description', 'rain_1h'
    ])
    
    return df

from datetime import datetime, date

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
        'APPID': api_key
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