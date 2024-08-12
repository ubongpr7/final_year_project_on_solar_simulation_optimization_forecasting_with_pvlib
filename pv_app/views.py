from django.shortcuts import render
from io import StringIO
from django.http import JsonResponse
from geopy.geocoders import Nominatim

from utils.pv import pv_tracking,interactive_map,get_lat_long
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
            lat = interactive_map(address)['lat']
            location = interactive_map(address).get('location',None)
            print('location: ',location)
            return render(request, 'map.html', {'form': form, 'map': map_html,'location':location})
            
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



from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import pandas as pd
from .forms import DataUploadForm
import plotly.express as px

from django.http import JsonResponse, HttpResponse
from django.views import View
import pandas as pd
from .forms import DataUploadForm

class DataUploadView(View):
    template_name = 'uploader.html'
    
    def get(self, request):
        form = DataUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_csv(file)  # Assuming CSV for simplicity
            request.session['data'] = df.to_json()  # Save DataFrame in session
            columns = df.columns.tolist()
            return render(request, 'plotter.html', {'columns': columns})
        return HttpResponse("Invalid file format", status=400)

class ViewSampleDataView(View):
    def get(self, request):
        sample_count = int(request.GET.get('sample_count', 5))
        df = pd.read_json(request.session.get('data'))
        sample_data = df.head(sample_count).to_html(classes='table table-striped')
        return HttpResponse(sample_data)

def get_columns_view(request):
    df = pd.read_json(StringIO(request.session.get('data')))
    columns = df.columns.tolist()

    plot_form = PlotForm()
    plot_form.fields['x_column'].choices = [(col, col) for col in columns]
    plot_form.fields['y_column'].choices = [(col, col) for col in columns]

    return render(request, 'cols.html', {'plot_form': plot_form})


import plotly.express as px
from django.http import JsonResponse
from django.shortcuts import render

def plot_data_view(request):
    df = pd.read_json(StringIO(request.session.get('data')))

    plot_type = request.POST.get('plot_type')
    x_column = request.POST.get('x_column')
    y_column = request.POST.get('y_column')

    fig = None
    if plot_type == 'scatter':
        fig = px.scatter(df, x=x_column, y=y_column)
    elif plot_type == 'bar':
        fig = px.bar(df, x=x_column, y=y_column)
    elif plot_type == 'line':
        fig = px.line(df, x=x_column, y=y_column)
    # Add more plot types as needed

    graph_html = fig.to_html()

    return render(request,'plot.html',{'plot': graph_html})

class CleanAndVisualizeView(View):
    def post(self, request):
        action = request.POST.get('action')
        column = request.POST.get('column')
        df = pd.read_json(request.session.get('data'))
        
        if action == 'fillna_zero':
            df[column] = df[column].fillna(0)
        elif action == 'fillna_mean':
            df[column] = df[column].fillna(df[column].mean())
        elif action == 'convert_datetime':
            df[column] = pd.to_datetime(df[column])
        
        request.session['data'] = df.to_json()  # Update session data

        return HttpResponse("Success")

    def get(self, request):
        df = pd.read_json(StringIO(request.session.get('data')))
        print(df.index)
        # df = pd.read_json(request.session.get('data'))
        column = request.GET.get('column')
        fig = px.scatter(df, y=column,x=df.date)
        plot_html = fig.to_html()

        return HttpResponse(plot_html)
