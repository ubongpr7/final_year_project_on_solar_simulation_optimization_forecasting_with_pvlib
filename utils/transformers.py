import pandas as pd
from datetime import datetime,date

def extract_weather_data(json_data):
    # Initialize an empty list to store the data
    data = []

    # Iterate through the weather data in the JSON
    for entry in json_data['list']:
        # Extract relevant information
        dt = datetime.datetime.utcfromtimestamp(entry['dt'])  # Convert UNIX timestamp to datetime
        temp = entry['main']['temp']
        feels_like = entry['main']['feels_like']
        pressure = entry['main']['pressure']
        humidity = entry['main']['humidity']
        temp_min = entry['main']['temp_min']
        temp_max = entry['main']['temp_max']
        wind_speed = entry['wind']['speed']
        wind_deg = entry['wind']['deg']
        wind_gust = entry['wind'].get('gust', None)  # Gust may not always be present
        clouds = entry['clouds']['all']
        weather_main = entry['weather'][0]['main']
        weather_description = entry['weather'][0]['description']
        rain = entry.get('rain', {}).get('1h', 0)  # Default to 0 if rain data is not available

        # Append the data to the list
        data.append({
            'datetime': dt,
            'temp': temp,
            'feels_like': feels_like,
            'pressure': pressure,
            'humidity': humidity,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'wind_speed': wind_speed,
            'wind_deg': wind_deg,
            'wind_gust': wind_gust,
            'clouds': clouds,
            'weather_main': weather_main,
            'weather_description': weather_description,
            'rain': rain
        })

    # Convert the list of data into a DataFrame
    df = pd.DataFrame(data)
    
    return df

