import pandas as pd
import pyplot.express as px
from pvlib import location,irradiance,solarposition
import numpy as np 
def get_times(start,end,freq,tz):
    return pd.date_range(start=start,end=end,freq=freq,tz=tz)
def get_irradiance(lat,lon,tz,start,end):
    location_obj = location.Location(lat,lon,tz)
    times=get_times(start,end,'5min',tz)
    solar_position=location_obj.get_solarposition(times)
    clearsky=location_obj.get_clearsky(times)
    POA_irradiance=irradiance.get_total_irradiance(
        surface_tilt=solar_position['apparent_zenith'],
        surface_azimuth=solar_position['azimuth'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi']
    )
    df= pd.Dataframe(
        {
            'datetime':POA_irradiance.index,
            'poa_global':POA_irradiance['poa_global'],
            'poa_direct':POA_irradiance['poa_direct'],
            'poa_diffuse':POA_irradiance['poa_diffuse'],
            'temp_air':clearsky['temp_air'],
            'wind_speed':clearsky['wind_speed'],
            'wind_direction':clearsky['wind_direction'],
            'pressure':clearsky['pressure'],
            'relative_humidity':clearsky['relative_humidity'],
            'ghi':clearsky['ghi'],
            'dni':clearsky['dni'],
            'dhi':clearsky['dhi']
        },
        index=POA_irradiance.index,
        columns={
            'time','poa_global','poa_direct','poa_diffuse','temp_air','wind_speed','wind_direction','pressure','relative_humidity','ghi','dni','dhi'
        }
    )
    df.set_index('datetime',inplace=True)
    return df

# Sun ploar plot Analema 
# it can be used to estimate where to get max e from sun at any time of the day.

def sun_plot(lat,lon,tz,start,end):
    times=get_times(start,end,'H',tz)
    solar_position=solarposition.get_solarposition(times,lat,lon)
    # remove nighttimes

    solar_position=solar_position['apparent_elevation'> o,:]
    # draw the analema loop
    ax=plt.subplot(1,1,1,projection='polar')
    points= ax.scatter(np.radians(solar_position.azimuth),solar_position.apparent_elevation,s=2,label=None,c=solar_position.index.dayofyear,vmin=1,)
    ax.figure.colorbar(points)  

    for hours in np.unique(solar_position.index.hour):
        subset=solar_position[solar_position.index.hour==hours,:]
        r=subset.apparent_zenith
        position = solar_position.loc[r.idxmin(),:]
        label =date.strftime('%Y-%m-%d')
        ax.plot(np.radians(position.azimuth),position.apparent_elevation,label=label)
    
    
    



