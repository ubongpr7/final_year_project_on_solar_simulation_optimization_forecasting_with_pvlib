from django.db import models
from django.utils import timezone
import pytz
class PVLocation(models.Model):
    """
    Represents the geographical location of the PV system.
    """
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        help_text="Latitude of the location in decimal degrees (e.g., 40.7128 for New York)."
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        help_text="Longitude of the location in decimal degrees (e.g., -74.0060 for New York)."
    )
    timezone = models.CharField(
        max_length=15, 
        help_text="Timezone of the location (e.g., 'Etc/GMT+5' for New York).",
        default='Etc/GMT+0',
        choices=pytz.all_timezones,

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
    """
    Represents a simulation run for a PV system.
    """
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
        # Simulation logic goes here
        pass
