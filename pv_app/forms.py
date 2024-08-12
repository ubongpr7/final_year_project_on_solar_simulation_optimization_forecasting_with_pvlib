
from django import forms
import pytz



class AddressForm(forms.Form):
    address = forms.CharField(
        label='Enter Address',
        max_length=255,
        widget=forms.TextInput(attrs={
            'id': 'address-input',
            'hx-get': '/get-address-suggestions/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#address-select',
            'hx-indicator': '#loading-indicator',
        })
    )


class PVTrackingForm(forms.Form):
    lat = forms.FloatField(
        label="Latitude",
        required=True,
        help_text="Enter the latitude for the location of the PV system."
    )
    lon = forms.FloatField(
        label="Longitude",
        required=True,
        help_text="Enter the longitude for the location of the PV system."
    )

    tz = forms.ChoiceField(
        label="Time Zone",
        choices=[(tz, tz) for tz in pytz.all_timezones],
        initial='US/Eastern',
        help_text="Select the time zone for the location of the PV system."
    )
    from_date = forms.DateField(
        label="From Date",
        initial="2024-08-23",
        widget=forms.TextInput(attrs={'type': 'date'}),
        help_text="Choose the start date for the tracking period."
    )
    to_date = forms.DateField(
        label="To Date",
        initial="2024-09-01",
        widget=forms.TextInput(attrs={'type': 'date'}),
        help_text="Choose the end date for the tracking period."
    )
    freq = forms.CharField(
        label="Frequency",
        initial='5min',
        help_text="Specify the frequency of the tracking data (e.g., '5min')."
    )
    max_angle = forms.FloatField(
        label="Maximum Angle",
        initial=90,
        help_text="Enter the maximum tilt angle for the solar panels."
    )
    axis_tilt = forms.FloatField(
        label="Axis Tilt",
        initial=0,
        help_text="Specify the tilt angle of the tracking axis."
    )
    axis_azimuth = forms.FloatField(
        label="Axis Azimuth",
        initial=180,
        help_text="Enter the azimuth angle of the tracking axis."
    )
    address = forms.CharField(
        label="Search Address",
        required=False,
        help_text="Enter an address to automatically update latitude and longitude."
    )



class DataUploadForm(forms.Form):
    file = forms.FileField(label='Upload CSV file')
