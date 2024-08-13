from django.shortcuts import render
from io import StringIO
from django.http import JsonResponse
from geopy.geocoders import Nominatim

from utils.pv import *
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import PVTrackingForm,AddressForm,PlotForm

# Create your views here.
def home(request):
    context={
        'pv_tracking':pv_tracking(),
        'map':interactive_map().get('map'),
    }
    return render(request,'index.html',context)


def get_address_suggestions(request):
    query = request.GET.get('address', '')
    print(query)
    if query:
        geolocator = Nominatim(user_agent="abcd")
        locations = geolocator.geocode(query, exactly_one=False, limit=100)  # Limit to 5 suggestions
        suggestions = []
        if locations:
            for location in locations:
                suggestions.append(location.address)
        return render(request, 'options.html', {'suggestions': suggestions})
    else:
        return render(request, 'options.html', {'suggestions': []})


def map_view(request):
    address = 'Nigeria'  
    map_html = interactive_map(address)['map']
    form = AddressForm()
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            map_html = interactive_map(address)['map']
            location = interactive_map(address).get('location',None)
            print('location: ',location)
            latitude=location.latitude
            longitude=location.longitude
            timezone=get_timezone_from_address(address)
            print('timezone: ',timezone)
            context = {
                'form': form,
                'map': map_html,
                'latitude':latitude,
                'longitude':longitude,
                'timezone':timezone,
                'location':location,
                
                }

            return render(request, 'map.html', context)

    else:
        form = AddressForm()
    
    return render(request, 'map.html', {'form': form, 'map': map_html})

class PVTrackingView(FormView):
    template_name = 'forms.html'
    form_class = PVTrackingForm
    success_url = '/'
    def get(self, request, *args, **kwargs):
        # Check for URL parameters
        visualizer = request.GET.get('visualizer', None)
        request.session['visualizer'] = visualizer
        return super().get(request, *args, **kwargs)
    

    def form_valid(self, form):
        # Get cleaned data from the form
        tz = form.cleaned_data['tz']
        from_ = form.cleaned_data['from_date']
        to_ = form.cleaned_data['to_date']
        lat = form.cleaned_data['lat']
        lon = form.cleaned_data['lon']
        freq = form.cleaned_data['freq']
        max_angle = form.cleaned_data['max_angle']
        axis_tilt = form.cleaned_data['axis_tilt']
        axis_azimuth = form.cleaned_data['axis_azimuth']
        plot_color = form.cleaned_data['plot_color']
        plot_type = form.cleaned_data['plot_type']

        # Call the pv_tracking function
        visualizer=self.request.session.get('visualizer')
        graph_title=''
        result=''   
        if visualizer=='temp':
            result = plot_temperature(
            tz=tz,
            color=plot_color,
            plot_type=plot_type,
            # from_=from_,
            # to_=to_,
            lat=lat,
            lon=lon,
            )
            graph_title='Temperature Variation Over Time'
        elif visualizer=='wind':
            result=plot_wind_speed(
            tz=tz,
            color=plot_color,
            plot_type=plot_type,
            # from_=from_,
            # to_=to_,
            lat=lat,
            lon=lon,
            )
            graph_title='Wind Speed Variation Over Time'
        elif visualizer=='gni':
            result=plot_gni(
            tz=tz,
            color=plot_color,
            plot_type=plot_type,
            
            lat=lat,
            lon=lon,
            )
            graph_title='GNI Variation Over Time'
        elif visualizer=='dni':
            result=plot_dni(
            tz=tz,
            color=plot_color,
            plot_type=plot_type,
            
            lat=lat,
            lon=lon,
            )
            graph_title='DNI Variation Over Time'
        elif visualizer=='dhi':
            result=plot_dhi(
            tz=tz,
            color=plot_color,
            plot_type=plot_type,
            
            lat=lat,
            lon=lon,
            )
            graph_title='DHI Variation Over Time'

        elif visualizer=='true_tracker':

            result = pv_tracking(
                tz=tz,
                from_=from_,
                to_=to_,
                lat=lat,
                color=plot_color,
                plot_type=plot_type,
                lon=lon,
                freq=f'{freq}min',
                max_angle=max_angle,
                axis_tilt=axis_tilt,
                axis_azimuth=axis_azimuth
            )
            graph_title='True Tracking Angle'




        context = self.get_context_data(result=result,graph_title=graph_title)
        return self.render_to_response(context)


