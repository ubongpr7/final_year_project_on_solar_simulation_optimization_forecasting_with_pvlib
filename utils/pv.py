import datetime
import pandas as pd
import pytz
import requests_cache
from folium import Map, Marker
from geopy.geocoders import Nominatim
from pvlib import solarposition, tracking
from pvlib.iotools import pvgis
from timezonefinder import TimezoneFinder
from .helper import generate_plot

# Cache requests to avoid repeated API calls
requests_cache.install_cache('pvgis_requests_cache', backend='sqlite')

# Initialize Geolocator
geolocator = Nominatim(user_agent="solar_app")


def get_timezone(lat, lng):
    """
    Get the timezone for a given latitude and longitude.

    Parameters:
    - lat: float, latitude of the location
    - lng: float, longitude of the location

    Returns:
    - str, timezone string
    """
    tf = TimezoneFinder()
    return tf.timezone_at(lng=lng, lat=lat)


def get_timezone_from_address(address):
    """
    Get the timezone from a given address.

    Parameters:
    - address: str, the address to geocode

    Returns:
    - timezone: timezone object if found, else None
    """
    location = geolocator.geocode(address)
    if location is None:
        return None

    timezone_str = str(get_timezone(location.latitude, location.longitude))
    if timezone_str is None:
        return None

    return pytz.timezone(timezone_str)


def get_lat_long(address):
    """
    Get latitude and longitude from a given address.

    Parameters:
    - address: str, the address to geocode

    Returns:
    - location: geopy Location object if found, else None
    """
    location = geolocator.geocode(address)
    if location:
        return location
    return None


def interactive_map(address='Ondo, Nigeria'):
    """
    Generate an interactive map centered on a given address.

    Parameters:
    - address: str, address to center the map

    Returns:
    - dict: dictionary containing search status and map HTML representation
    """
    m = Map(location=[10, 0], zoom_start=10)
    location = get_lat_long(address)

    if location:
        lat, lng = location.latitude, location.longitude
        if lat is None or lng is None:
            return {'search_status': 'failed', 'map': m._repr_html_()}

        m = Map(location=[lat, lng], zoom_start=10)
        Marker([lat, lng], tooltip='Click for more', popup=address).add_to(m)
        return {'search_status': 'success', 'map': m._repr_html_(), 'location': location}
    
    return {'search_status': 'failed', 'map': m._repr_html_()}


def pv_tracking(tz='US/Eastern', color=None, plot_type='line', from_='2024-08-23', to_='2024-09-01', lat=40, lon=-89, freq='5min', max_angle=90, axis_tilt=0, axis_azimuth=180):
    """
    Generate a plot of solar panel tracking angles over time.

    Parameters:
    - tz: str, time zone of the location
    - color: str, color of the plot line
    - plot_type: str, type of plot (e.g., 'line')
    - from_: str, start date in YYYY-MM-DD format
    - to_: str, end date in YYYY-MM-DD format
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - freq: str, frequency of data points
    - max_angle: float, maximum tilt angle for the solar panel
    - axis_tilt: float, tilt of the axis
    - axis_azimuth: float, azimuth of the axis

    Returns:
    - dict: dictionary containing plot HTML representation
    """
    times = pd.date_range(from_, to_, freq=freq, tz=tz)
    solpos = solarposition.get_solarposition(times, lat, lon)

    truetracking_angles = tracking.singleaxis(
        apparent_zenith=solpos['apparent_zenith'],
        apparent_azimuth=solpos['azimuth'],
        axis_tilt=axis_tilt,
        axis_azimuth=axis_azimuth,
        max_angle=max_angle,
        backtrack=False
    ).fillna({'tracker_theta': 0})

    fig = generate_plot(
        df=truetracking_angles,
        y='tracker_theta',
        title='True Tracking Angle',
        labels={'x': 'Time', 'y': 'Tracking angle'},
        color=color,
        plot_type=plot_type,
    )
    return {"fig": fig.to_html(), "sample": "sample"}


def climate_plots(lat, lon, y_, plot_type='line', tz='UTC', title='Ambient Temperature', color='#603a47'):
    """
    Fetch TMY weather data for the given location and plot the specified variable.

    Parameters:
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - y_: str, column to plot (e.g., 'temp_air', 'wind_speed')
    - plot_type: str, type of plot (e.g., 'line')
    - tz: str, time zone of the location
    - title: str, title of the plot
    - color: str, color of the plot line

    Returns:
    - dict: dictionary containing plot HTML representation
    """
    weather, _, info, _ = pvgis.get_pvgis_tmy(lat, lon, map_variables=True)
    
    # Rename columns to more descriptive names
    weather = weather.rename(columns={
        'G(h)': 'ghi',
        'Gb(n)': 'dni',
        'Gd(h)': 'dhi',
        'T2m': 'temp_air',
        'WS10m': 'wind_speed'
    }).fillna({
        'ghi': weather['ghi'].mean(),
        'dhi': weather['dhi'].mean(),
        'temp_air': weather['temp_air'].mean(),
        'wind_speed': weather['wind_speed'].mean(),
        'pressure': weather['pressure'].mean(),
        'relative_humidity': weather['relative_humidity'].mean(),
    })

    fig = generate_plot(
        df=weather,
        y=y_,
        title=title,
        labels={'x': 'Time', 'y': y_},
        color=color,
        plot_type=plot_type,
    )
    return {"fig": fig.to_html(), "sample": "sample"}


def plot_temperature(lat, lon, plot_type='line', tz='UTC', title='Ambient Temperature', color='#603a47'):
    """
    Plot the ambient temperature.

    Parameters:
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - plot_type: str, type of plot (e.g., 'line')
    - tz: str, time zone of the location
    - title: str, title of the plot
    - color: str, color of the plot line

    Returns:
    - dict: dictionary containing plot HTML representation
    """
    return climate_plots(lat, lon, 'temp_air', plot_type, tz, title, color)


def plot_wind_speed(lat, lon, plot_type='line', tz='UTC', title='Wind Speed', color='#603a47'):
    """
    Plot the wind speed.

    Parameters:
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - plot_type: str, type of plot (e.g., 'line')
    - tz: str, time zone of the location
    - title: str, title of the plot
    - color: str, color of the plot line

    Returns:
    - dict: dictionary containing plot HTML representation
    """
    return climate_plots(lat, lon, 'wind_speed', plot_type, tz, title, color)


def plot_ghi(lat, lon, plot_type='line', tz='UTC', title='Global Horizontal Irradiance (GHI)', color='#603a47'):
    """
    Plot the Global Horizontal Irradiance (GHI).

    Parameters:
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - plot_type: str, type of plot (e.g., 'line')
    - tz: str, time zone of the location
    - title: str, title of the plot
    - color: str, color of the plot line

    Returns:
    - dict: dictionary containing plot HTML representation
    """
    return climate_plots(lat, lon, 'ghi', plot_type, tz, title, color)


def plot_dni(lat, lon, plot_type='line', tz='UTC', title='Direct Normal Irradiance (DNI)', color='#603a47'):
    """
    Plot the Direct Normal Irradiance (DNI).

    Parameters:
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - plot_type: str, type of plot (e.g., 'line')
    - tz: str, time zone of the location
    - title: str, title of the plot
    - color: str, color of the plot line

    Returns:
    - dict: dictionary containing plot HTML representation
    """
    return climate_plots(lat, lon, 'dni', plot_type, tz, title, color)


def plot_dhi(lat, lon, plot_type='line', tz='UTC', title='Diffuse Horizontal Irradiance (DHI)', color='#603a47'):
    """
    Plot the Diffuse Horizontal Irradiance (DHI).

    Parameters:
    - lat: float, latitude of the location
    - lon: float, longitude of the location
    - plot_type: str, type of plot (e.g., 'line')
    - tz: str, time zone of the location
    - title: str, title of the plot
    - color: str, color of the plot line

    Returns:
    - dict: dictionary containing plot HTML representation
    """
    return climate_plots(lat, lon, 'dhi', plot_type, tz, title, color)
