import pandas as pd
from datetime import datetime,date
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



