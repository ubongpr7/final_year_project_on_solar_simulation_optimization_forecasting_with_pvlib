from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import FormView
from django.urls import reverse_lazy
from geopy.geocoders import Nominatim

from .forms import PVTrackingForm, AddressForm, PlotForm
from utils.pv import interactive_map, get_timezone_from_address, plot_temperature, plot_wind_speed, plot_ghi, plot_dni, plot_relative_humidity, plot_pressure, plot_dhi, pv_tracking

# Create your views here.
def home(request):
    context = {
        'map': interactive_map().get('map'),
    }
    return render(request, 'index.html', context)


def get_address_suggestions(request):
    query = request.GET.get('address', '')
    suggestions = []

    if query:
        geolocator = Nominatim(user_agent="abcd")
        locations = geolocator.geocode(query, exactly_one=False, limit=100)  # Limit to 100 suggestions

        if locations:
            suggestions = [location.address for location in locations]

    return render(request, 'options.html', {'suggestions': suggestions})


def map_view(request):
    address = 'Nigeria'
    form = AddressForm(request.POST or None)
    map_html = interactive_map(address)['map']
    latitude, longitude, timezone, location = None, None, None, None

    if request.method == 'POST' and form.is_valid():
        address = form.cleaned_data['address']
        map_data = interactive_map(address)
        map_html = map_data['map']
        location = map_data.get('location', None)

        if location:
            latitude, longitude = location.latitude, location.longitude
            timezone = get_timezone_from_address(address)

    context = {
        'form': form,
        'map': map_html,
        'latitude': latitude,
        'longitude': longitude,
        'timezone': timezone,
        'location': location,
    }
    return render(request, 'map.html', context)


class PVTrackingView(FormView):
    template_name = 'forms.html'
    form_class = PVTrackingForm
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        visualizer = request.GET.get('visualizer', None)
        request.session['visualizer'] = visualizer
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        visualizer = self.request.session.get('visualizer')
        result, graph_title = self.get_plot_result(visualizer, cleaned_data)
        context = self.get_context_data(result=result, graph_title=graph_title)
        return self.render_to_response(context)

    def get_plot_result(self, visualizer, data):
        """Return the appropriate plot result and title based on the visualizer type."""
        plot_functions = {
            'temp_air': (plot_temperature, 'Temperature Variation Over Time'),
            'wind_speed': (plot_wind_speed, 'Wind Speed Variation Over Time'),
            'ghi': (plot_ghi, 'GHI Variation Over Time'),
            'dni': (plot_dni, 'DNI Variation Over Time'),
            'relative_humidity': (plot_relative_humidity, 'Humidity Variation Over Time'),
            'pressure': (plot_pressure, 'Pressure Variation Over Time'),
            'dhi': (plot_dhi, 'DHI Variation Over Time'),
            'true_tracker': (pv_tracking, 'True Tracking Angle'),
        }

        plot_func, title = plot_functions.get(visualizer, (None, ''))

        if plot_func:
            if visualizer == 'true_tracker':
                result = plot_func(
                    tz=data['tz'],
                    from_=data['from_date'],
                    to_=data['to_date'],
                    lat=data['lat'],
                    lon=data['lon'],
                    freq=f"{data['freq']}min",
                    max_angle=data['max_angle'],
                    axis_tilt=data['axis_tilt'],
                    axis_azimuth=data['axis_azimuth'],
                    color=data['plot_color'],
                    plot_type=data['plot_type'],
                    title=data['location'],
                )
            else:
                result = plot_func(
                    tz=data['tz'],
                    from_=data['from_date'],
                    to_=data['to_date'],
                    lat=data['lat'],
                    lon=data['lon'],
                    color=data['plot_color'],
                    plot_type=data['plot_type'],
                    title=data['location'],
                )
        else:
            result = None

        return result, title

