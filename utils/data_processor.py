import pandas as pd
from datetime import datetime
import requests

def transform_data(df, date, sky_type='clear_sky'):
    """
    Transforms the DataFrame by adding a datetime index and selecting specific columns.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame containing 'start', 'end', and sky condition columns.
    - date (str): The date in 'YYYY-MM-DD' format to be combined with 'start' times.
    - sky_type (str): The type of sky conditions to use ('clear_sky' or 'cloudy_sky').
    
    Returns:
    - pd.DataFrame: The transformed DataFrame with the desired columns and datetime index.
    """
    
    # Create the datetime column
    df['datetime'] = pd.to_datetime([f"{date} {time}" for time in df['start']])

    # Set datetime as the index
    df.set_index('datetime', inplace=True)

    # Select the correct sky condition columns
    df['dni'] = df[f'{sky_type}.dni']
    df['dhi'] = df[f'{sky_type}.dhi']
    df['ghi'] = df[f'{sky_type}.ghi']

    # Drop the original sky condition columns
    df.drop(columns=[f'{sky_type}.dni', f'{sky_type}.dhi', f'{sky_type}.ghi'], inplace=True)

    # Rearrange the columns
    df = df[['start', 'end', 'dni', 'dhi', 'ghi']]

    return df

# Example usage:
data = {
    "start": ["00:00", "01:00", "02:00", "03:00", "04:00"],
    "end": ["01:00", "02:00", "03:00", "04:00", "05:00"],
    "clear_sky.dni": [0, 0, 0, 0, 0],
    "clear_sky.dhi": [0, 0, 0, 0, 0],
    "clear_sky.ghi": [0, 0, 0, 0, 0],
    "cloudy_sky.dni": [0, 0, 0, 0, 0],
    "cloudy_sky.dhi": [0, 0, 0, 0, 0],
    "cloudy_sky.ghi": [0, 0, 0, 0, 0],
}

df = pd.DataFrame(data)
date = "2023-10-10"
result_df = transform_data(df, date, sky_type='clear_sky')

print(result_df.head())



def convert_to_unix_time(date_str):
    # Convert the date string to a datetime object
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    # Convert the datetime object to Unix time (seconds since epoch)
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
        for item in data.get('data', []):
            print(f"Time: {item.get('time')}, Solar Irradiance: {item.get('irradiance')} W/m²")
        return transform_data(data, start) 
    else:
        print(f"Failed to retrieve data. HTTP Status code: {response.status_code}")
        print("Response:", response.text)

# Example usage
lat = 52.5200  # Example latitude
lon = 13.4050  # Example longitude
start = "2023-08-01"
end = "2023-08-02"
tz = "UTC"  # Time zone, this might depend on the API's requirements
api_key = "your_openweather_api_key"

get_solar_irradiation(lat, lon, start, end, tz, api_key)
