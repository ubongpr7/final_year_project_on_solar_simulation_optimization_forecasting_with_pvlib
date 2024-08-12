from django.shortcuts import render

from django.http import JsonResponse
from geopy.geocoders import Nominatim

from utils.pv import pv_tracking,interactive_map,get_lat_long
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import PVTrackingForm,AddressForm

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
        locations = geolocator.geocode(query, exactly_one=False, limit=10)  # Limit to 5 suggestions
        suggestions = []
        if locations:
            for location in locations:
                suggestions.append(location.address)
        return render(request, 'option.html', {'suggestions': suggestions})
    else:
        return render(request, 'option.html', {'suggestions': []})


def map_view(request):
    address = 'Nigeria'  
    map_html = get_lat_long(address)
    form = AddressForm()
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            map_html = get_lat_long(address)
            return render(request, 'map.html', {'form': form, 'map': map_html})
    else:
        form = AddressForm()

    return render(request, 'map.html', {'form': form, 'map': map_html})

class PVTrackingView(FormView):
    template_name = 'forms.html'
    form_class = PVTrackingForm
    success_url = '/'

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

        # Call the pv_tracking function
        result = pv_tracking(
            tz=tz,
            from_=from_,
            to_=to_,
            lat=lat,
            lon=lon,
            freq=freq,
            max_angle=max_angle,
            axis_tilt=axis_tilt,
            axis_azimuth=axis_azimuth
        )

        # Add result to context
        context = self.get_context_data(result=result)
        return self.render_to_response(context)
