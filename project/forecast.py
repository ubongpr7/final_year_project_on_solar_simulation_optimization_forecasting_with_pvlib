import flet as ft
import pvlib
import pandas as pd
from pvlib import location

def energy_forecasting_page(page):
    def submit(e):
        parameters = {
            'A_c': float(area.value),
            'I_sc_ref': float(isc.value),
            'V_oc_ref': float(voc.value),
            'I_mp_ref': float(imp.value),
            'V_mp_ref': float(vmp.value),
            'alpha_sc': float(alpha.value),
            'beta_oc': float(beta.value),
            'gamma_r': float(gamma.value),
            'T_NOCT': float(noct.value)
        }
        
        # Location of the PV system
        lat, lon = 40.7128, -74.0060  # Example: New York City
        tz = 'Etc/GMT+5'
        site = location.Location(lat, lon, tz=tz)

        # Generate times at hourly intervals for one day
        times = pd.date_range('2023-06-21 00:00:00', '2023-06-21 23:59:00', freq='H', tz=tz)

        # Get clear sky data
        clearsky = site.get_clearsky(times)

        # Assume ambient temperature is constant (25 C) for simplicity
        temperature_air = 25
        temperature_module = temperature_air + (parameters['T_NOCT'] - 20) / 800 * clearsky['ghi']

        # Using pvlib to create a PV module
        module_parameters = {
            'A_c': parameters['A_c'],
            'N_s': 96,
            'I_sc_ref': parameters['I_sc_ref'],
            'V_oc_ref': parameters['V_oc_ref'],
            'I_mp_ref': parameters['I_mp_ref'],
            'V_mp_ref': parameters['V_mp_ref'],
            'alpha_sc': parameters['alpha_sc'],
            'beta_oc': parameters['beta_oc'],
            'gamma_r': parameters['gamma_r']
        }

        # Simulate the performance
        effective_irradiance = clearsky['poa_global']
        temperature_cell = pvlib.temperature.sapm_cell(effective_irradiance, temperature_air, parameters['T_NOCT'])

        single_diode_params = pvlib.pvsystem.calcparams_desoto(
            effective_irradiance,
            temperature_cell,
            **module_parameters
        )

        iv_curve = pvlib.pvsystem.singlediode(*single_diode_params)
        energy_yield = iv_curve['p_mp'].sum()  # Sum of power over the day

        # Displaying the results
        results_text.value = (
            f"Energy yield forecast generated successfully!\n"
            f"Total Energy Yield: {energy_yield / 1000:.2f} kWh"
        )
        page.update()

    area = ft.TextField(label="Area (A_c)", value="1.7")
    isc = ft.TextField(label="I_sc_ref", value="5.1")
    voc = ft.TextField(label="V_oc_ref", value="59.4")
    imp = ft.TextField(label="I_mp_ref", value="4.8")
    vmp = ft.TextField(label="V_mp_ref", value="48.3")
    alpha = ft.TextField(label="alpha_sc", value="0.0045")
    beta = ft.TextField(label="beta_oc", value="-0.22216")
    gamma = ft.TextField(label="gamma_r", value="-0.476")
    noct = ft.TextField(label="T_NOCT", value="42.4")

    results_text = ft.Text("")

    page.add(ft.Column([
        area, isc, voc, imp, vmp, alpha, beta, gamma, noct,
        ft.TextButton("Submit", on_click=submit),
        results_text
    ]))

app = ft.App(energy_forecasting_page)
app.run()
