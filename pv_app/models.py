from django.db import models
from django.utils import timezone
import pytz
import pvlib
import pandas as pd
import numpy as np
from django.utils.translation import gettext_lazy as _

class PVLocation(models.Model):
    """
    Represents the geographical location of the PV system.
    """
    LATITUDE_MAX_DIGITS = 9
    LATITUDE_DECIMAL_PLACES = 6
    LONGITUDE_MAX_DIGITS = 9
    LONGITUDE_DECIMAL_PLACES = 6

    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]

    latitude = models.DecimalField(
        max_digits=LATITUDE_MAX_DIGITS, 
        decimal_places=LATITUDE_DECIMAL_PLACES, 
        help_text="Latitude of the location in decimal degrees (e.g., 40.7128 for New York)."
    )
    longitude = models.DecimalField(
        max_digits=LONGITUDE_MAX_DIGITS, 
        decimal_places=LONGITUDE_DECIMAL_PLACES, 
        help_text="Longitude of the location in decimal degrees (e.g., -74.0060 for New York)."
    )
    timezone = models.CharField(
        max_length=63,  # max length for timezone strings
        help_text="Timezone of the location (e.g., 'Etc/GMT+5' for New York).",
        default='Etc/GMT+0',
        choices=TIMEZONE_CHOICES,
    )
    
    def __str__(self):
        return f"Location (Lat: {self.latitude}, Lon: {self.longitude})"

class PVModule(models.Model):
    """
    Represents a photovoltaic module with its parameters.
    """
    area = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Area of the PV module in square meters (A_c).",
        default=1.7
    )
    cells_in_series = models.PositiveIntegerField(
        help_text="Number of cells in series (N_s).",
        default=96
    )
    isc_ref = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Short-circuit current at reference conditions (I_sc_ref) in amperes.",
        default=5.1
    )
    voc_ref = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Open-circuit voltage at reference conditions (V_oc_ref) in volts.",
        default=59.4
    )
    imp_ref = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Current at maximum power point at reference conditions (I_mp_ref) in amperes.",
        default=4.8
    )
    vmp_ref = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Voltage at maximum power point at reference conditions (V_mp_ref) in volts.",
        default=48.3
    )
    alpha_sc = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        help_text="Temperature coefficient of short-circuit current (alpha_sc) in A/°C.",
        default=0.0045
    )
    beta_oc = models.DecimalField(
        max_digits=7, 
        decimal_places=5, 
        help_text="Temperature coefficient of open-circuit voltage (beta_oc) in V/°C.",
        default=-0.22216
    )
    a_ref = models.DecimalField(
        max_digits=7, 
        decimal_places=5, 
        help_text="Diode ideality factor multiplied by the thermal voltage at reference conditions (a_ref).",
        default=2.6373
    )
    i_l_ref = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        help_text="Light-generated current at reference conditions (I_L_ref) in amperes.",
        default=5.114
    )
    i_o_ref = models.DecimalField(
        max_digits=10, 
        decimal_places=10, 
        help_text="Saturation current at reference conditions (I_o_ref) in amperes.",
        default=8.196e-10
    )
    rs = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        help_text="Series resistance of the module (R_s) in ohms.",
        default=1.065
    )
    rsh_ref = models.DecimalField(
        max_digits=7, 
        decimal_places=2, 
        help_text="Shunt resistance at reference conditions (R_sh_ref) in ohms.",
        default=381.68
    )
    gamma_r = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        help_text="Temperature coefficient of power (gamma_r) in %/°C.",
        default=-0.476
    )
    noct = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        help_text="Nominal operating cell temperature (T_NOCT) in °C.",
        default=42.4
    )
    
    def __str__(self):
        return f"PV Module (Area: {self.area} m², Cells: {self.cells_in_series})"




class PVSimulation(models.Model):
    module = models.ForeignKey(PVModule, on_delete=models.CASCADE, help_text="The PV module used in the simulation.")
    location = models.ForeignKey(PVLocation, on_delete=models.CASCADE, help_text="The location of the PV system.")
    start_time = models.DateTimeField(help_text="Start time of the simulation in the user's local time.")
    end_time = models.DateTimeField(help_text="End time of the simulation in the user's local time.")
    ambient_temperature = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        help_text="Ambient temperature during the simulation in °C.",
        default=25.0
    )
    
    def save(self, *args, **kwargs):
        # Convert local time to UTC before saving
        if timezone.is_naive(self.start_time):
            self.start_time = timezone.make_aware(self.start_time, timezone.get_current_timezone())
        self.start_time = self.start_time.astimezone(timezone.utc)
        
        if timezone.is_naive(self.end_time):
            self.end_time = timezone.make_aware(self.end_time, timezone.get_current_timezone())
        self.end_time = self.end_time.astimezone(timezone.utc)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Simulation ({self.start_time} to {self.end_time}, Module: {self.module})"
    
    def run_simulation(self):
        # Convert latitude, longitude, and timezone
        latitude = float(self.location.latitude)
        longitude = float(self.location.longitude)
        timezone_str = self.location.timezone
        
        # Define the module parameters
        module_params = {
            'area': float(self.module.area),
            'cells_in_series': self.module.cells_in_series,
            'isc_ref': float(self.module.isc_ref),
            'voc_ref': float(self.module.voc_ref),
            'imp_ref': float(self.module.imp_ref),
            'vmp_ref': float(self.module.vmp_ref),
            'alpha_sc': float(self.module.alpha_sc),
            'beta_oc': float(self.module.beta_oc),
            'a_ref': float(self.module.a_ref),
            'i_l_ref': float(self.module.i_l_ref),
            'i_o_ref': float(self.module.i_o_ref),
            'rs': float(self.module.rs),
            'rsh_ref': float(self.module.rsh_ref),
            'gamma_r': float(self.module.gamma_r),
            'noct': float(self.module.noct)
        }
        
        # Set up the time range for the simulation
        times = pd.date_range(start=self.start_time, end=self.end_time, freq='H')
        
        # Create a PVLib location object
        location = pvlib.location.Location(latitude, longitude, timezone_str)
        
        # Generate the weather data (e.g., using a model or actual data)
        weather_data = {
            'temperature_air': np.full(len(times), self.ambient_temperature),
            'ghi': np.random.normal(500, 100, len(times))  # Example GHI data
        }
        
        # Create a DataFrame for weather data
        weather_df = pd.DataFrame(weather_data, index=times)
        
        # Create a PV System using PVLib's ModelChain
        pv_system = pvlib.pvsystem.PVSystem(
            module_parameters={
                'pdc0': module_params['imp_ref'] * module_params['vmp_ref'],
                'gamma_pdc': module_params['gamma_r'] / 100,
                'v_oc_ref': module_params['voc_ref'],
                'i_sc_ref': module_params['isc_ref']
            },
            temperature_coefficient=module_params['alpha_sc'],
            nominal_voltage=module_params['vmp_ref']
        )
        
        # Create an inverter model (optional)
        inverter = pvlib.inverter.Adams3000()
        
        # Set up the ModelChain
        model_chain = pvlib.modelchain.ModelChain(pv_system, location, inverter=inverter)
        
        # Run the ModelChain
        weather_df['dni'] = np.random.normal(700, 100, len(times))  # Direct Normal Irradiance (DNI) data
        weather_df['dhi'] = np.random.normal(100, 50, len(times))  # Diffuse Horizontal Irradiance (DHI) data
        
        # Run the model chain
        model_chain.run_model(weather_df)
        
        # Access the output
        power_output = model_chain.results.ac
        
        # Save the results to the database or return them
        result = {
            'times': times,
            'power_output': power_output
        }
        
        return result