
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


PLOT_CHOICES = [
    ('scatter', 'Scatter Plot'),
    ('bar', 'Bar Chart'),
    ('line', 'Line Chart'),
    # Add more plot types as needed
]

class PlotForm(forms.Form):
    plot_type = forms.ChoiceField(choices=PLOT_CHOICES, label="Select Plot Type")
    x_column = forms.ChoiceField(label="Select X-axis Column")
    y_column = forms.ChoiceField(label="Select Y-axis Column", required=False)
import pytz
from django import forms

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
    freq = forms.IntegerField(
        label="Frequency (minutes)",
        initial=5,
        help_text="Specify the frequency of the tracking data in minutes (e.g., 5)."
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
    # Add a field to select the plot type
    plot_type = forms.ChoiceField(
        label="Plot Type",
        choices=[
            ('line', 'Line'),
            ('scatter', 'Scatter'),
            ('bar', 'Bar'),
            ('area', 'Area'),
            ('histogram', 'Histogram'),
            ('box', 'Box'),
            ('violin', 'Violin'),
            ('pie', 'Pie'),
            # ('density_contour', 'Density Contour'),
            # ('funnel', 'Funnel'),
            # ('heatmap', 'Heatmap')
        ],
        initial='line',
        help_text="Select the type of plot you want to generate."
    )

    # Add a field to select the plot color
    plot_color = forms.ChoiceField(
        label="Plot Color",
        choices=[
            ('#1f77b4', 'Blue'),
            ('#ff7f0e', 'Orange'),
            ('#2ca02c', 'Green'),
            ('#d62728', 'Red'),
            ('#9467bd', 'Purple'),
            ('#8c564b', 'Brown'),
            ('#e377c2', 'Pink'),
            ('#7f7f7f', 'Gray'),
            ('#bcbd22', 'Olive'),
            ('#17becf', 'Cyan'),
            ('#f3a712', 'Gold'),
            ('#ffb5e8', 'Light Pink'),
            ('#bdb2ff', 'Light Purple'),
            ('#ffcbf2', 'Light Rose'),
            ('#a7c957', 'Avocado Green'),
            ('#00bbf9', 'Sky Blue'),
            ('#ff006e', 'Hot Pink'),
            ('#8338ec', 'Violet')
        ],
        initial='#1f77b4',
        help_text="Select the color for your plot."
    )
    location = forms.CharField(widget=forms.HiddenInput())



class DataUploadForm(forms.Form):
    file = forms.FileField(label='Upload CSV file')
