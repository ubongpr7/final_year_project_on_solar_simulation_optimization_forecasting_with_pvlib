from django.forms import modelform_factory
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import FormView
from django.urls import reverse_lazy
from geopy.geocoders import Nominatim
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import PVModule
from .forms import PVTrackingForm, AddressForm, PlotForm
from utils.pv import interactive_map, get_timezone_from_address, plot_temperature, plot_wind_speed, plot_ghi, plot_dni, plot_relative_humidity, plot_pressure, plot_dhi, pv_tracking
from django.views.generic import TemplateView

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.apps import apps
from django.db import transaction
from django.forms import modelform_factory

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
        return modelform_factory(self.get_model(), fields='__all__')

    def dispatch(self, request, *args, **kwargs):
        management_dispatch_dispatcher(self, request)
        if not request.user.has_perm(f'{self.kwargs["app_name"]}.change_{self.kwargs["model_name"]}'):
            if request.htmx:
                return HttpResponse('<div hx-swap-oob="true" id="error-message"><h2>404</h2> <h3>User does not have permission to update this item </h3></div>')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_template(self):
        return ['common/htmx/create.html'] if self.request.htmx else ['common/create.html']

    def form_valid(self, form):
        try:
            with transaction.atomic():
                if hasattr(self.get_model(), 'profile'):
                    form.instance.profile = self.request.user.company or self.request.user.profile
                if hasattr(self.get_model(), 'updated_by'):
                    form.instance.updated_by = self.request.user
                
                response = super().form_valid(form)
                if self.request.htmx:
                    return HttpResponse('<div hx-swap-oob="true" id="success-message">Item updated successfully</div>')
                return response
        except Exception as error:
            form.add_error(None, error)
            return render_templete(self.request, 'common/htmx/create.html', 'common/create.html', self.get_context_data())

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
        context['ajax_url'] = f'/update/{self.kwargs["app_name"]}/{self.kwargs["model_name"]}/{self.kwargs["pk"]}/'
        context['get_url'] = f'/list/{self.kwargs["app_name"]}/{self.kwargs["model_name"]}/'
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
        return modelform_factory(self.get_model(), fields='__all__')

    def dispatch(self, request, *args, **kwargs):
        management_dispatch_dispatcher(self, request)
        if not request.user.has_perm(f'{self.kwargs["app_name"]}.add_{self.kwargs["model_name"]}'):
            if request.htmx:
                return HttpResponse('<div hx-swap-oob="true" id="error-message"><h2>404</h2> <h3>User does not have permission to create this item </h3></div>')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_template(self):
        return render_templete(self.request, 'common/htmx/create.html', 'common/create.html', self.get_context_data())

    def form_valid(self, form):
        try:
            with transaction.atomic():
                if hasattr(self.get_model(), 'profile'):
                    form.instance.profile = self.request.user.company or self.request.user.profile
                if hasattr(self.get_model(), 'created_by'):
                    form.instance.created_by = self.request.user
                
                response = super().form_valid(form)
                if self.request.htmx:
                    return HttpResponse('<div hx-swap-oob="true" id="success-message">Item created Successfully</div>')
                return response
        except Exception as error:
            form.add_error(None, error)
            return render(self.request, 'common/htmx/create.html', self.get_context_data())

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
        return context

# Generic List View
class GenericListView(ListView):
    paginate_by = 10
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        context['get_url'] = f'/list/{self.kwargs["app_name"]}/{self.kwargs["model_name"]}/'
        context['page_obj'] = context['paginator'].get_page(page)
        get_context_heper(self, context)
        return context

    def get_template_names(self):
        return ['common/htmx/tabula_list.html'] if hasattr(self.request, 'htmx') and self.request.htmx else ['common/tabula_list.html']

    def get_queryset(self):
        model = self.get_model()
        queryset = model.objects.all()
        return queryset

    def get_model(self):
        model_name = self.kwargs['model_name']
        app_name = self.kwargs['app_name']
        return apps.get_model(app_name, model_name)

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

