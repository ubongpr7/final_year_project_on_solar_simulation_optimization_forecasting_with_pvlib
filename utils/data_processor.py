import pandas as pd

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

import requests
# pro.openweathermap.org/data/2.5/weather?q=London,uk&APPID=297b91bc87fac0f26c4d65efa6eb2443
def get_solar_irradiation(lat, lon, date, interval, tz, api_key='297b91bc87fac0f26c4d65efa6eb2443'):
    url = "https://pro.openweathermap.org/energy/1.0/solar/interval_data"
    params = {
        'lat': lat,
        'lon': lon,
        'date': date,
        'interval': interval,
        'tz': tz,
        'appid': api_key
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Solar Irradiation Data for {lat}, {lon} on {date}:")
        for item in data.get('data', []):
            print(f"Time: {item.get('time')}, Solar Irradiance: {item.get('irradiance')} W/m²")
            return transform_data(data,date) 
    else:
        print(f"Failed to retrieve data. HTTP Status code: {response.status_code}")
        print("Response:", response.text)

# Example usage
api_key = "YOUR_API_KEY"
latitude = 6.5244  # Replace with your latitude
longitude = 3.3792  # Replace with your longitude
date = "2022-01-01"  # Replace with your desired date
interval = "1h"  # Options: hourly, daily
tz = "UTC"  # Time zone

semi_df=get_solar_irradiation(latitude, longitude, date, interval, tz, )

print(semi_df)