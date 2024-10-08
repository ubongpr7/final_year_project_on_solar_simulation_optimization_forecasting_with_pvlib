from django.db import models
from django.utils import timezone
import pytz
from geopy.geocoders import Nominatim
import pvlib
# from pvlib.modelchain import  ac_models
import pandas as pd
import numpy as np
from django.utils.translation import gettext_lazy as _

from utils.extractors import fetch_all_weather_data
from utils.pv import get_lat_long, get_timezone_from_address
import pvlib
from django.conf  import settings
import pvlib
from retry_requests import retry
import requests_cache
import os

# Enable caching using requests_cache
cache_path = os.path.join(os.getcwd(), 'cache2')
requests_cache.install_cache(cache_name=cache_path, backend='sqlite', expire_after=3600)  # Cache expires after 1 hour

def get_cached_inverter_db():
    try:
        # Try retrieving the inverter DB from cache
        inverter_db = pvlib.pvsystem.retrieve_sam('cecinverter')
        return inverter_db
    except Exception as e:
        print(f"Error fetching inverter database: {e}")
        return None

def get_cached_module_db():
    try:
        # Try retrieving the module DB from cache
        module_db = pvlib.pvsystem.retrieve_sam('sandiamod')
        return module_db
    except Exception as e:
        print(f"Error fetching module database: {e}")
        return None

# Retrieve databases with caching
inverter_db = get_cached_inverter_db()
module_db = get_cached_module_db()


# Extract all available temperature model configurations from pvlib
temperature_model_choices = [
    (key, key.replace('_', ' ').title()) 
    for key in pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'].keys()
]

class PVLocation(models.Model):
    """
    Represents the geographical location of the PV system.
    """
    LATITUDE_MAX_DIGITS = 15
    LATITUDE_DECIMAL_PLACES = 12
    LONGITUDE_MAX_DIGITS = 15
    LONGITUDE_DECIMAL_PLACES = 12


    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]
    address= models.CharField(
    max_length=120,
    blank=True,
    null=True,
    help_text='Enter address'
    )
    latitude = models.DecimalField(
        max_digits=LATITUDE_MAX_DIGITS, 
        decimal_places=LATITUDE_DECIMAL_PLACES, 
        help_text="Latitude of the location in decimal degrees (e.g., 40.7128 for New York).",
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=LONGITUDE_MAX_DIGITS, 
        decimal_places=LONGITUDE_DECIMAL_PLACES, 
        help_text="Longitude of the location in decimal degrees (e.g., -74.0060 for New York).",
        blank=True

    )
    timezone = models.CharField(
        max_length=63,  # max length for timezone strings
        help_text="Timezone of the location (e.g., 'Etc/GMT+5' for New York).",
        default='Etc/GMT+0',
        choices=TIMEZONE_CHOICES,
    )
    class Meta:
        ordering=('address',)

    
    
    def get_address(self):
        geolocator = Nominatim(user_agent="abcd")
        location = geolocator.reverse(query=(self.latitude,self.longitude),exactly_one=True, limit=1)  
        return f'{location}'
    def save(self, *args, **kwargs):
        if not self.latitude:
            location=get_lat_long(self.address)
            self.latitude,self.longitude=location.latitude,location.longitude
        # elif not self.address:
        #     self.address= self.get_address
        if not self.timezone:
            self.timezone=get_timezone_from_address(self.address)
        if self.latitude and self.longitude:
            if not self.address:

                self.address=self.get_address


        super().save(*args, **kwargs)


    def __str__(self):

        return f"Location:{self.address}, lat: {self.latitude} lon:{self.longitude} "


# Retrieve inverter and module databases

inverter_choices = [(name, name) for name in inverter_db.keys()]
module_choices = [(name, name) for name in module_db.keys()]

class PVSimulation(models.Model):
    # Assuming you have these choices defined elsewhere
    inverter_choices = [(key, key.replace('_', ' ').title()) for key in inverter_db.keys()]
    module_choices = [(key, key.replace('_', ' ').title()) for key in module_db.keys()]
    
    location = models.ForeignKey(PVLocation, null=True, on_delete=models.SET_NULL)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    inverter = models.CharField(
        choices=inverter_choices,
        max_length=100,
        verbose_name="Choose Inverter",
        default=inverter_choices[0][0]  # Set default to the first choice
    )
    
    module = models.CharField(
        choices=module_choices,
        max_length=100,
        verbose_name="Choose Module",
        default=module_choices[0][0]  # Set default to the first choice
    )
    
    temperature_model = models.CharField(
        max_length=50,
        choices=temperature_model_choices,
        default='open_rack_glass_glass',
        help_text="Select the temperature model for the simulation"
    )
    modules_per_string=models.IntegerField(default=10)
    
    def run_simulation(self,):
        # Access location parameters
        latitude = float(self.location.latitude)
        longitude = float(self.location.longitude)
        timezone_str = self.location.timezone

        # Retrieve parameters from pvlib databases
        inverter_params = inverter_db[self.inverter]
        module_params = module_db[self.module]
        temp_model_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][self.temperature_model]

        # Ensure that start_time and end_time are timezone-aware
        if pd.Timestamp(self.start_time).tz is None:
            start_time = pd.to_datetime(self.start_time).tz_localize(timezone_str, ambiguous='NaT', nonexistent='NaT')
        else:
            start_time = pd.to_datetime(self.start_time).tz_convert(timezone_str)

        if pd.Timestamp(self.end_time).tz is None:
            end_time = pd.to_datetime(self.end_time).tz_localize(timezone_str, ambiguous='NaT', nonexistent='NaT')
        else:
            end_time = pd.to_datetime(self.end_time).tz_convert(timezone_str)

        # Create the PV system
        pv_system = pvlib.pvsystem.PVSystem(
            module_parameters=module_params,
            inverter_parameters=inverter_params,
            temperature_model_parameters=temp_model_params,
            modules_per_string=self.modules_per_string
        )

        # Fetch weather data with timezone-awareness
        location = pvlib.location.Location(latitude, longitude, timezone_str)
        weather_df = fetch_all_weather_data(start_time, end_time, latitude, longitude, timezone_str)
        daily_weather_df = fetch_all_weather_data(start_time, end_time, latitude, longitude, timezone_str,df_interval='daily')

        # Ensure that weather_df's index is localized to the correct timezone
        if weather_df.index.tz is None:
            weather_df.index = pd.to_datetime(weather_df.index).tz_localize(timezone_str, ambiguous='NaT', nonexistent='NaT')
        else:
            weather_df.index = weather_df.index.tz_convert(timezone_str)

        # Create a date range with explicit timezone
        times = pd.date_range(start=start_time, end=end_time, freq='h', tz=timezone_str)

        # Ensure that the weather_df contains only the required columns for the model chain
        required_weather_columns = ['dni', 'ghi', 'dhi']
        weather_df_filtered = weather_df[required_weather_columns]

        # Get clear sky data for the location
        sky = location.get_clearsky(times=times)

        # Set up and run the model chain
        model_chain = pvlib.modelchain.ModelChain(system=pv_system, location=location)

        # Run the model with actual weather data
        model_chain.run_model(weather_df_filtered)
        real_ac_power_output = model_chain.results.ac

        # Run the model with clear sky data
        model_chain.run_model(sky)
        clear_sky_ac_power_output = model_chain.results.ac

        # Merge the real AC power output and clear sky AC power output into the weather_df
        weather_df['ac_power_output'] = real_ac_power_output
        weather_df['clear_sky_ac_power_output'] = clear_sky_ac_power_output
        # Return the combined dataframe
        file_path = os.path.join(settings.BASE_DIR, 'data', f'weather_data_{self.location.latitude}.csv')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        weather_df.to_csv(file_path)
        return {'weather_df':weather_df,'daily_weather_df':daily_weather_df}

    
    def get_inverter_details(self):
        
        """
        Fetch details of the selected inverter from the pvlib inverter database.
        Returns a dictionary containing the specifications of the selected inverter.
        """
        # Retrieve the selected inverter details from the inverter database
        inverter_params = inverter_db[self.inverter]
        module_params = module_db[self.module]
        # Convert to a Pandas DataFrame for easy handling (optional)
        if inverter_params is not None:
            return pd.Series(inverter_params).to_dict()  # Return as dictionary
        
        return None
    def get_model_details(self):
        """
        Fetch details of the selected inverter from the pvlib inverter database.
        Returns a dictionary containing the specifications of the selected inverter.
        """
        # Retrieve the selected inverter details from the inverter database
        module_params = module_db[self.module]
        # Convert to a Pandas DataFrame for easy handling (optional)
        if module_params is not None:
            return pd.Series(module_params).to_dict()  # Return as dictionary
        
        return None
    def get_temp_details(self):
        """
        Fetch details of the selected inverter from the pvlib inverter database.
        Returns a dictionary containing the specifications of the selected inverter.
        """
        # Retrieve the selected inverter details from the inverter database
        temp_model_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][self.temperature_model]

        # Convert to a Pandas DataFrame for easy handling (optional)
        if temp_model_params is not None:
            return pd.Series(temp_model_params).to_dict()  # Return as dictionary
        
        return None
registerable_models=[PVLocation,PVSimulation]