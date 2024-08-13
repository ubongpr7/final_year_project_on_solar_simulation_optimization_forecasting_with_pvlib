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
 


def pv_tracking(tz='US/Eastern',from_='2024-08-23',to_='2024-09-01',lat=40,lon=-89,freq='5min',max_angle=90,axis_tilt=0,axis_azimuth=180):

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
    fig= plt.line(
    #    truetracking_angles,
        x=truetracking_angles.index,
        y=truetracking_angles.tracker_theta,
        title='True Tracking Angle',
        labels={'x':'Time','y':'Tracking angle'}
    )
    return fig.to_html()



# def plot_temperature(tz='US/Eastern', from_='2024-08-23', to_='2024-09-01', lat=40, lon=-89, freq='5min'):
#     """
#     Plot temperature variation over a specified time period for a given location.

#     Parameters:
#     - tz (str): Time zone.
#     - from_ (str): Start date in YYYY-MM-DD format.
#     - to_ (str): End date in YYYY-MM-DD format.
#     - lat (float): Latitude of the location.
#     - lon (float): Longitude of the location.
#     - freq (str): Frequency of data points (e.g., '5min', '1H').

#     Returns:
#     - HTML representation of the plot.
#     """
#     # Define location
#     location = Location(latitude=lat, longitude=lon, tz=tz)

#     # Use GFS model to get weather data
#     model = GFS()
#     start = pd.Timestamp(from_, tz=tz)
#     end = pd.Timestamp(to_, tz=tz)

#     # Get weather data
#     weather_data = model.get_processed_data(location.latitude, location.longitude, start, end)

#     # Resample the data to the desired frequency
#     weather_data_resampled = weather_data['temp_air'].resample(freq).mean()



#     fig= plt.line(
#         x=weather_data_resampled.index,
#         y=weather_data_resampled.values,
#         title='Temperature Variation Over Time',
#         labels={'x':'Time','y':'Temperature (°C)'}
#     )
#     return fig.to_html()


import requests_cache
import plotly.express as px
import pandas as pd
import pvlib
from pvlib.iotools import pvgis
from pvlib.location import Location

# Cache requests to avoid repeated API calls
requests_cache.install_cache('pvgis_requests_cache', backend='sqlite')

def plot_temperature(lat, lon, tz='UTC', title='Ambient Temperature', color='#603a47'):
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

    # Create a Plotly line plot for ambient temperature
    fig = px.line(
        # weather,
        x=weather.index,
        y=weather['temp_air'],
        title=title,
        labels={'x': 'Time', 'temp_air': 'Temperature (°C)'},
        line_shape='linear',
        color_discrete_sequence=[color]
    )

    return fig.to_html()

# # Example usage
# lat = 40.0
# lon = -89.0
# html_plot = plot_temperature(lat, lon, tz='US/Eastern', title='Ambient Temperature in New York')
# print(html_plot)
