from pvlib import solarposition, tracking
import pandas as pd
import plotly.express as plt
import folium 
import geocoder
import folium
import geocoder
from geopy.geocoders import Nominatim
import tzwhere
import pytz
import datetime
from .helper import *
import requests_cache
import plotly.express as px
import pandas as pd
import pvlib
from pvlib.iotools import pvgis
from pvlib.location import Location


import pandas as pd
# from pvlib.forecast import GFS
from pvlib.location import Location

geolocator = Nominatim(user_agent="abcd")
from timezonefinder import TimezoneFinder

def get_timezone(lat, lng):
  tf = TimezoneFinder()
  return tf.timezone_at(lng=lng, lat=lat)

def get_timezone_from_address(address):
    location = geolocator.geocode(address)

    if location is None:
        return None

    latitude, longitude = location.latitude, location.longitude
    timezone_str=str(get_timezone(latitude, longitude ))
    if timezone_str is None:
        return None

    timezone = pytz.timezone(timezone_str)
    return timezone

# Example usage:
address = "New York City, NY, USA"
timezone = get_timezone_from_address(address)

if timezone:
    now = datetime.datetime.now(timezone)
    print(now)

def get_address(coordinates):
    location = geolocator.reverse(coordinates, format="address")

def get_lat_long(address):
    # geolocator = Nominatim(user_agent="abcd")

    location = geolocator.geocode(address)
    if location:
        print(location.latitude, location.longitude)
        return location
    else:
        return None


def interactive_map(address='Ondo, Nigeria'):
    # Create a base map centered around Nigeria
    m = folium.Map(location=[10, 0], zoom_start=10)
    
    location = get_lat_long(address)
    if location:
        print(location)
        lat, lng = location.latitude, location.longitude
        if lat is None or lng is None:
            print('failed lat' )
            return {'search_status': 'failed', 'map': m._repr_html_()}

        # Add a marker on the map
        else:
            print('success')
            m = folium.Map(location=[lat, lng], zoom_start=10)

            folium.Marker([lat, lng], tooltip='Click for more',
                      popup=address).add_to(m)
        
            # Return the HTML representation of the map
            return {'search_status': 'success', 'map': m._repr_html_(),'location':location}
            # return {'search_status': 'success    '}
    else:
        return {'search_status': 'failed', 'map': m._repr_html_()}
 


def pv_tracking(tz='US/Eastern',color=None,plot_type='line',from_='2024-08-23',to_='2024-09-01',lat=40,lon=-89,freq='5min',max_angle=90,axis_tilt=0,axis_azimuth=180):

    tz = tz
    # lat, lon = 40, -80

    times = pd.date_range(
        from_,
        to_, 
        freq=freq,
        tz=tz
    )
    solpos = solarposition.get_solarposition(times, lat, lon)

    truetracking_angles = tracking.singleaxis(
        apparent_zenith=solpos['apparent_zenith'],
        apparent_azimuth=solpos['azimuth'],
        axis_tilt=axis_tilt,
        axis_azimuth=axis_azimuth,
        max_angle=max_angle,
        backtrack=False,  # for true-tracking
        # gcr=0.5  # irrelevant for true-tracking
        ) 

    truetracking_angles = truetracking_angles.fillna({'tracker_theta':0})
    df_month=truetracking_angles.groupby(truetracking_angles.index.month).mean()
    fig = generate_plot(
        x=truetracking_angles.index,
        y=truetracking_angles.tracker_theta,
        title='True Tracking Angle',
        labels={'x':'Time','y':'Tracking angle'},
        color=color,
        # df=df_month,
        plot_type=plot_type,
    )
    return {"fig":fig.to_html(),"sample":"sample"}




# Cache requests to avoid repeated API calls
requests_cache.install_cache('pvgis_requests_cache', backend='sqlite')





def climate_plots(lat, lon,y_,plot_type='line', tz='UTC', title='Ambient Temperature', color='#603a47'):
    """
    Fetches TMY weather data for the given location and plots the ambient temperature.

    Parameters:
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - tz: str, time zone of the location (default 'UTC')
    - title: str, title of the plot (default 'Ambient Temperature')
    - color: str, color of the plot line (default '#603a47')
    """
    # Fetch TMY weather data from PVGIS

    # Create a Plotly line plot for ambient temperature
        
    weather, _, info, _ = pvgis.get_pvgis_tmy(lat, lon, map_variables=True)

    # Rename columns to more descriptive names
    weather = weather.rename(
        columns={
            'G(h)': 'ghi',
            'Gb(n)': 'dni',
            'Gd(h)': 'dhi',
            'T2m': 'temp_air',
            'WS10m': 'wind_speed'
        })
    weather=weather.fillna({
        'ghi':weather['ghi'].mean(),
        'dhi':weather['dhi'].mean(),
        'temp_air':weather['temp_air'].mean(),
        'wind_speed':weather['wind_speed'].mean(),
        'pressure':weather['pressure'].mean(),
        'relative_humidity':weather['relative_humidity'].mean(),

    })
    print(weather.columns)
    weather['month']=weather.index.month
    df_month = weather.groupby('month').mean()

    fig = generate_plot(
        x=weather.index,
        y=weather[y_],
        df=df_month,
        title=title,
        labels={'x': 'Time', 'y': y_},
        color=color,
        plot_type=plot_type,
    )

    return {"fig":fig.to_html(),"sample":"sample"}




def plot_temperature(lat, lon,plot_type='line', tz='UTC', title='Ambient Temperature', color='#603a47'):
    return climate_plots(lat=lat, lon=lon,plot_type=plot_type,y_='temp_air' ,tz=tz, title=title, color=color)

def plot_wind_speed(lat, lon,plot_type='line', tz='UTC', title='Ambient Wind', color='#603a47'):
    return climate_plots(lat=lat, lon=lon,plot_type=plot_type,y_='wind_speed' ,tz=tz, title=title, color=color)


def plot_ghi(lat, lon,plot_type='line', tz='UTC', title='Ambient GHI', color='#603a47'):
    return climate_plots(lat=lat, lon=lon,plot_type=plot_type,y_='ghi' ,tz=tz, title=title, color=color)

def plot_dni(lat, lon,plot_type='line', tz='UTC', title='Ambient DNI', color='#603a47'):
    return climate_plots(lat=lat, lon=lon,plot_type=plot_type,y_='dni' ,tz=tz, title=title, color=color)

def plot_dhi(lat, lon,plot_type='line', tz='UTC', title='Ambient Temperature', color='#603a47'):
    return climate_plots(lat=lat, lon=lon,plot_type=plot_type,y_='dhi' ,tz=tz, title=title, color=color,)


def plot_relative_humidity(lat, lon,plot_type='line', tz='UTC', title='Relative Humidity', color='#603a47'):
    return climate_plots(lat=lat, lon=lon,plot_type=plot_type,y_='relative_humidity' ,tz=tz, title=title, color=color,)

def plot_pressure(lat, lon,plot_type='line', tz='UTC', title='Presure Variation', color='#603a47'):
    return climate_plots(lat=lat, lon=lon,plot_type=plot_type,y_='pressure' ,tz=tz, title=title, color=color,)
