from django.shortcuts import render

from utils.pv import pv_tracking,interactive_map
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import PVTrackingForm

# Create your views here.
def home(request):
    context={
        'pv_tracking':pv_tracking(),
        'map':interactive_map().get('map'),
    }
    return render(request,'index.html',context)



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
