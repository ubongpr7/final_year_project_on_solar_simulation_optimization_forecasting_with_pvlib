import requests_cache

import plotly.express as  px
import pandas as pd
import pvlib
from pvlib import pvgis
from pvlib.location import Location

requests_cache.install_cache('pvgis_requests_cache', backend='sqlite')


weather, _, info, _ = pvgis.get_pvgis_tmy(lat, lon, map_variables=True)


weather = weather.rename(
    columns={
        'G(h)': 'ghi',
        'Gb(n)': 'dni',
        'Gd(h)': 'dhi',
        'T2m': 'temp_air',
        'WS10m': 'wind_speed'
        })
    
# Ambient temperature
weather.temp_air.plot(title='Ambient temperature in %s\n%s' % (LOCATION, weather_source), color='#603a47')