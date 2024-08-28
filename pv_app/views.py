from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.forms import modelform_factory
from django.apps import apps
from django.db import transaction
from django.template.loader import render_to_string

from geopy.geocoders import Nominatim
from plotly.offline import plot
import plotly.graph_objs as go

from utils.helper import generate_plot

from .models import PVSimulation
from .forms import PVSimulationForm, PVTrackingForm, AddressForm, PlotForm, PlotTypeForm
from utils.pv import (
    interactive_map, get_timezone_from_address, plot_puv_index_max, plot_temperature, plot_uv_index_clear_sky_max, 
    plot_wind_speed, plot_ghi, plot_dni, plot_relative_humidity, 
    plot_pressure, plot_dhi, pv_tracking
)

# Create your views here.

# Helper functions for context and permissions
def management_dispatch_dispatcher(self, request):
    # Your implementation for custom dispatch logic
    pass

def get_context_heper(self, context):
    # Your implementation for custom context logic
    pass

def render_templete(request, htmtx_template, default_template, context):
    # Your implementation for rendering templates
    return render(request, htmtx_template, context) if request.htmx else render(request, default_template, context)

# Generic Detail View
class GenericDetailView(DetailView):
    template_name = 'common/htmx/detail.html'
    context_object_name = 'item'

    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        return apps.get_model(app_name, model_name)

    def get_object(self, queryset=None):
        model = self.get_model()
        return model.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name']=self.kwargs['model_name']
        context['app_name']=self.kwargs['app_name']
        context['plot_type']=PlotTypeForm
        context['title']=self.kwargs['model_name'].title()

        get_context_heper(self, context)
        return context

# Generic Update View
class GenericUpdateView(UpdateView):
    template_name = 'common/htmx/create.html'
    success_url = '/'

    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        return apps.get_model(app_name, model_name)

    def get_object(self):
        model = self.get_model()
        return model.objects.get(pk=self.kwargs['pk'])

    def get_form_class(self):
        if self.kwargs['model_name']== 'pvsimulation':
            return PVSimulationForm
        return modelform_factory(self.get_model(), fields='__all__')

    
    def get_template(self):
        return ['common/htmx/create.html'] if self.request.htmx else ['common/create.html']

    def form_valid(self, form):
        response = super().form_valid(form)
        context = self.get_context_data( graph_title=self.kwargs['model_name'].title())
        return self.render_to_response(context)

        # if self.request.htmx:
        #     return HttpResponse('<div hx-swap-oob="true" id="success-message">Item updated successfully</div>')
        
    def form_invalid(self, form):
        try:
            if self.request.htmx:
                return render(self.request, 'common/htmx/create.html', self.get_context_data())
            return super().form_invalid(form)
        except Exception as error:
            form.add_error("name", error)
            return render(self.request, 'common/htmx/create.html', self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        get_context_heper(self, context)
        
        context['done_url'] = self.success_url
        return context

# Generic Create View
class GenericCreateView(CreateView):
    template_name = 'common/htmx/create.html'
    success_url = '/'

    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        return apps.get_model(app_name, model_name)

    def get_form_class(self):
        if self.kwargs['model_name']== 'pvsimulation':
            return PVSimulationForm
        return modelform_factory(self.get_model(), fields='__all__')


    def get_template(self):
        return render_templete(self.request, 'common/htmx/create.html', 'common/create.html', self.get_context_data())

    def form_valid(self, form):
            created_object =form.save()
            context = self.get_context_data(form=form)
            return redirect(reverse_lazy('pv_app:generic_detail', kwargs={
            'app_name': self.kwargs['app_name'],
            'model_name': self.kwargs['model_name'],
            'pk': created_object.pk
        }))
    def form_invalid(self, form):
        try:
            if self.request.htmx:
                return render(self.request, 'common/htmx/create.html', self.get_context_data())
            return super().form_invalid(form)
        except Exception as error:
            form.add_error("name", error)
            return render(self.request, 'common/htmx/create.html', self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        get_context_heper(self, context)
        context['ajax_url'] = f'/add/{self.kwargs["app_name"]}/{self.kwargs["model_name"]}/'
        context['get_url'] = f'/list/{self.kwargs["app_name"]}/{self.kwargs["model_name"]}/'

        context['done_url'] = self.success_url
        context['model_name'] =self.kwargs['model_name']
        context['app_name'] =self.kwargs['app_name']
        return context


class GenericListView(ListView):
    paginate_by = 10
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        context['page_obj'] = context['paginator'].get_page(page)
        context['base_url'] = f'/list/{self.kwargs["app_name"]}/{self.kwargs["model_name"]}'
        context['app_name']=self.kwargs['app_name']
        context['model_name']=self.kwargs['model_name']
        context['title']=self.kwargs['model_name'].title()
        get_context_heper(self, context)
        return context

    def get_template_names(self):
        if hasattr(self.request, 'htmx') and self.request.htmx:
            return ['common/htmx/list.html']
        return ['common/list.html']

    def get_queryset(self):
        model = self.get_model()
        queryset = model.objects.all()
        return queryset

    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        model = apps.get_model(app_name, model_name)
        print(f"Retrieved model: {model}")  # Debugging line
        return model

def run_simulation_view(request):
    if request.method == 'POST':
        form = PVSimulationForm(request.POST)
        if form.is_valid():
            # Save the simulation object
            simulation = form.save()

            # Run the simulation (method from the model)
            result = simulation.run_simulation()

            # Redirect to the results page or render the results in the same template
            return render(request, 'simulation_results.html', {'result': result, 'simulation': simulation})
    else:
        form = PVSimulationForm()

    return render(request, 'simulation_form.html', {'form': form})

# Dynamic Delete View
def dynamic_delete(request, app_name, model_name, pk):
    model = apps.get_model(app_name, model_name)
    obj = model.objects.get(pk=pk)
    if request.method == 'POST':
        obj.delete()
        return HttpResponse('<div hx-swap-oob="true" id="success-message">Item deleted Successfully</div>')
    
    del_url = f'/delete/{app_name}/{model_name}/{pk}/'
    context = {
        "obj": obj,
        'del_url': del_url,
        "app_label": app_name,
        "model_label": model_name,
        'pk': pk
    }
    return render(request, 'common/confirm_delete.html', context)


import plotly.graph_objects as go

def update_graph_view(request, simulation_id):
    # Fetch the selected simulation
    simulation = PVSimulation.objects.get(id=simulation_id)

    # Get selected variables and plot type from the request
    selected_variables = request.GET.getlist('variables')
    plot_type = 'line'
    plot_type_uv = request.GET.get('plot_type', 'line')  # Default to 'line'
    
    # Run the simulation once and get the result
    simulation_result = simulation.run_simulation()
    result = simulation_result.get('weather_df')
    daily = simulation_result.get('daily_weather_df')
    
    if result is None or daily is None:
        return render(request, 'graph.html', {'graph': 'No data available'})

    # Create Plotly traces based on selected variables and plot type
    traces = []

    for variable in selected_variables:
        try:
            if variable == 'ac_power_output':
                traces.append(create_trace(result.index, result['ac_power_output'], plot_type, 'AC Power Output', secondary_y=True))
            # elif variable == 'clear_sky_ac_power_output':
                # traces.append(create_trace(result.index, result['clear_sky_ac_power_output'], plot_type, 'Clear sky AC Power Output', secondary_y=True))
            elif variable == 'uv_index':
                traces.append(create_trace(daily.index, daily['uv_index_max'], plot_type, 'Daily UV Max', ))
            elif variable == 'uv_index_clear_sky_max':
                traces.append(create_trace(daily.index, daily['uv_index_clear_sky_max'], plot_type, 'Daily UV Max for Clear Sky', ))
            elif variable == 'dni':
                traces.append(create_trace(result.index, result['dni'], plot_type, 'DNI'))
            elif variable == 'dhi':
                traces.append(create_trace(result.index, result['dhi'], plot_type, 'DHI'))
            elif variable == 'ghi':
                traces.append(create_trace(result.index, result['ghi'], plot_type, 'GHI'))
            elif variable == 'pressure':
                traces.append(create_trace(result.index, result['surface_pressure'], plot_type, 'Surface Pressure'))
            elif variable == 'relative_humidity_2m':
                traces.append(create_trace(result.index, result['relative_humidity_2m'], plot_type, 'Relative Humidity 2m'))
            elif variable == 'windspeed_10m':
                traces.append(create_trace(result.index, result['windspeed_10m'], plot_type, 'Wind Speed 10m'))
            elif variable == 'temperature_2m':
                traces.append(create_trace(result.index, result['temperature_2m'], plot_type, 'Temperature 2m'))
            elif variable == 'uv-summary':
                fig=generate_plot(y='uv_index_max',df=daily,plot_type=plot_type_uv,location=simulation.location.address,)
                return render(request, 'graph.html', {'graph':fig.to_html()})
        except KeyError:
            # Handle missing columns in the dataset
            return render(request, 'graph.html', {'graph': f'Error: {variable} data is not available'})

    # Create the figure and add the traces
    fig = go.Figure()

    for trace in traces:
        fig.add_trace(trace)

    # Add secondary y-axis for AC power output if applicable
    if any('AC Power Output' in trace.name for trace in traces):
        fig.update_layout(
            yaxis2=dict(
                title='AC Power Output',
                titlefont=dict(color='rgba(255,0,0,0.8)'),
                tickfont=dict(color='rgba(255,0,0,0.8)'),
                overlaying='y',
                side='right'
            )
        )

    # General figure layout updates
    fig.update_layout(
        height=700,
        title='PV Simulation Results',
        xaxis_title='Time',
        yaxis_title='Primary Axis',
        legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1)
    )

    # Convert the plot to HTML
    graph_html = fig.to_html()

    # Return the updated graph HTML in the response
    return render(request, 'graph.html', {'graph': graph_html})


def create_trace(x, y, plot_type, name, secondary_y=False):
    """
    Create a Plotly trace with optional secondary y-axis.
    """
    trace = None
    if plot_type == 'line':
        trace = go.Scatter(x=x, y=y, mode='lines', name=name, yaxis='y2' if secondary_y else 'y')
    elif plot_type == 'bar':
        trace = go.Bar(x=x, y=y, name=name, yaxis='y2' if secondary_y else 'y')
    else:
        raise ValueError(f"Unsupported plot type: {plot_type}")
    
    return trace


class SimulationInterfaceView(TemplateView):
    template_name = 'simulation_interface.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_create_url'] = reverse_lazy('generic_create', kwargs={'app_name': 'pv_app', 'model_name': 'pvlocation'})
        context['system_create_url'] = reverse_lazy('generic_create', kwargs={'app_name': 'pv_app', 'model_name': 'pvsystem'})
        context['inverter_create_url'] = reverse_lazy('generic_create', kwargs={'app_name': 'pv_app', 'model_name': 'inverter'})
        context['modelchain_create_url'] = reverse_lazy('generic_create', kwargs={'app_name': 'pv_app', 'model_name': 'modelchain'})
        context['location_list_url'] = reverse_lazy('generic_list', kwargs={'app_name': 'pv_app', 'model_name': 'pvlocation'})
        context['system_list_url'] = reverse_lazy('generic_list', kwargs={'app_name': 'pv_app', 'model_name': 'pvsystem'})
        context['inverter_list_url'] = reverse_lazy('generic_list', kwargs={'app_name': 'pv_app', 'model_name': 'inverter'})
        context['modelchain_list_url'] = reverse_lazy('generic_list', kwargs={'app_name': 'pv_app', 'model_name': 'modelchain'})
        return context


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

    

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        visualizer = form.cleaned_data['visualizer']
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
            'uv_index_clear_sky_max': (plot_uv_index_clear_sky_max, 'UV Clear Sky Variation Over Time'),
            'uv_index_max': (plot_puv_index_max, 'UV Variation Over Time'),
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

