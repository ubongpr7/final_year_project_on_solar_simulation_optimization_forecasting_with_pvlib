import flet as ft
import pvlib
import pandas as pd
from pvlib import location

def performance_benchmarking_page(page):
    def submit(e):
        parameters = {
            'A_c': float(area.value),
            'I_sc_ref': float(isc.value),
            'V_oc_ref': float(voc.value),
            'I_mp_ref': float(imp.value),
            'V_mp_ref': float(vmp.value),
            'R_s': float(rs.value),
            'R_sh_ref': float(rsh.value),
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
            'alpha_sc': 0.0045,
            'beta_oc': -0.22216,
            'R_s': parameters['R_s'],
            'R_sh_ref': parameters['R_sh_ref'],
            'gamma_r': parameters['gamma_r']
        }

        # Simulate the performance under clear sky conditions
        effective_irradiance_clear = clearsky['poa_global']
        temperature_cell_clear = pvlib.temperature.sapm_cell(effective_irradiance_clear, temperature_air, parameters['T_NOCT'])

        single_diode_params_clear = pvlib.pvsystem.calcparams_desoto(
            effective_irradiance_clear,
            temperature_cell_clear,
            **module_parameters
        )

        iv_curve_clear = pvlib.pvsystem.singlediode(*single_diode_params_clear)
        energy_yield_clear = iv_curve_clear['p_mp'].sum()  # Sum of power over the day

        # Actual weather data (for simplicity, we use the clear sky data)
        actual_irradiance = clearsky['poa_global']
        temperature_cell_actual = pvlib.temperature.sapm_cell(actual_irradiance, temperature_air, parameters['T_NOCT'])

        single_diode_params_actual = pvlib.pvsystem.calcparams_desoto(
            actual_irradiance,
            temperature_cell_actual,
            **module_parameters
        )

        iv_curve_actual = pvlib.pvsystem.singlediode(*single_diode_params_actual)
        energy_yield_actual = iv_curve_actual['p_mp'].sum()  # Sum of power over the day

        # Benchmark results
        performance_ratio = (energy_yield_actual / energy_yield_clear) * 100

        # Displaying the results
        results_text.value = (
            f"Performance Benchmark generated successfully!\n"
            f"Total Energy Yield (Clear Sky): {energy_yield_clear / 1000:.2f} kWh\n"
            f"Total Energy Yield (Actual): {energy_yield_actual / 1000:.2f} kWh\n"
            f"Performance Ratio: {performance_ratio:.2f} %"
        )
        page.update()

    area = ft.TextField(label="Area (A_c)", value="1.7")
    isc = ft.TextField(label="I_sc_ref", value="5.1")
    voc = ft.TextField(label="V_oc_ref", value="59.4")
    imp = ft.TextField(label="I_mp_ref", value="4.8")
    vmp = ft.TextField(label="V_mp_ref", value="48.3")
    rs = ft.TextField(label="R_s", value="1.065")
    rsh = ft.TextField(label="R_sh_ref", value="381.68")
    gamma = ft.TextField(label="gamma_r", value="-0.476")
    noct = ft.TextField(label="T_NOCT", value="42.4")

    results_text = ft.Text("")

    page.add(ft.Column([
        area, isc, voc, imp, vmp, rs, rsh, gamma, noct,
        ft.TextButton("Submit", on_click=submit),
        results_text
    ]))

app = ft.App(performance_benchmarking_page)
app.run()
