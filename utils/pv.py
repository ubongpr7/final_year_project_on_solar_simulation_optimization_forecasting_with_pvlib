from pvlib import solarposition, tracking
import pandas as pd
import plotly.express as plt
import folium 
import geocoder

def get_lat_long(address):
    g = geocoder.google(address) 
    if g.ok:
        return g
    return None

def interactive_map(address='Ondo'):
    m = folium.Map(location=[7, 7], zoom_start=8)
    
    location= get_lat_long(address)
    if location:
        lat = location.lat
        lng = location.lng
        country = location.country
        if lat == None or lng == None:
            return {'search_status':'failed','map':m._repr_html_()}

        # Create Map Object

        folium.Marker([lat, lng], tooltip='Click for more',
                    popup=country).add_to(m)
        # Get HTML Representation of Map Object
        m = m._repr_html_()
        m= folium.Map(location=[7,7],zoom_start=8)
        return  {'search_status':'success','map':m._repr_html_()}
    return {'search_status':'failed','map':m._repr_html_()}
    


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