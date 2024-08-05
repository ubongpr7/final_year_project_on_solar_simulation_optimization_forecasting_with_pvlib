import flet as ft
import pvlib
import pandas as pd
from pvlib import location
from scipy.optimize import minimize

def pv_optimization_page(page):
    def submit(e):
        parameters = {
            'A_c': float(area.value),
            'N_s': int(cells.value),
            'I_sc_ref': float(isc.value),
            'V_oc_ref': float(voc.value),
            'I_mp_ref': float(imp.value),
            'V_mp_ref': float(vmp.value),
            'alpha_sc': float(alpha.value),
            'beta_oc': float(beta.value),
            'a_ref': float(aref.value),
            'I_L_ref': float(iref.value),
            'I_o_ref': float(io.value),
            'R_s': float(rs.value),
            'R_sh_ref': float(rsh.value),
            'gamma_r': float(gamma.value),
            'T_NOCT': float(noct.value)
        }

        # Define the location and time for the simulation
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
            'N_s': parameters['N_s'],
            'I_sc_ref': parameters['I_sc_ref'],
            'V_oc_ref': parameters['V_oc_ref'],
            'I_mp_ref': parameters['I_mp_ref'],
            'V_mp_ref': parameters['V_mp_ref'],
            'alpha_sc': parameters['alpha_sc'],
            'beta_oc': parameters['beta_oc'],
            'a_ref': parameters['a_ref'],
            'I_L_ref': parameters['I_L_ref'],
            'I_o_ref': parameters['I_o_ref'],
            'R_s': parameters['R_s'],
            'R_sh_ref': parameters['R_sh_ref'],
            'gamma_r': parameters['gamma_r']
        }

        def simulate_performance(params):
            module_parameters['R_s'] = params[0]
            module_parameters['R_sh_ref'] = params[1]
            effective_irradiance = clearsky['poa_global']
            temperature_cell = pvlib.temperature.sapm_cell(effective_irradiance, temperature_air, parameters['T_NOCT'])
            single_diode_params = pvlib.pvsystem.calcparams_desoto(
                effective_irradiance,
                temperature_cell,
                **module_parameters
            )
            iv_curve = pvlib.pvsystem.singlediode(*single_diode_params)
            energy_yield = iv_curve['p_mp'].sum()  # Sum of power over the day
            return -energy_yield  # Negative because we want to maximize energy yield

        # Initial guess for R_s and R_sh_ref
        initial_guess = [parameters['R_s'], parameters['R_sh_ref']]
        bounds = [(0.1, 2), (10, 1000)]  # Example bounds for R_s and R_sh_ref

        # Perform optimization
        result = minimize(simulate_performance, initial_guess, bounds=bounds, method='L-BFGS-B')
        optimized_R_s, optimized_R_sh_ref = result.x

        # Displaying the results
        results_text.value = (
            f"PV system optimized successfully!\n"
            f"Optimized R_s: {optimized_R_s:.3f} Ohms\n"
            f"Optimized R_sh_ref: {optimized_R_sh_ref:.2f} Ohms\n"
            f"Maximized Energy Yield: {-result.fun / 1000:.2f} kWh"
        )
        page.update()

    area = ft.TextField(label="Area (A_c)", value="1.7")
    cells = ft.TextField(label="Number of Cells (N_s)", value="96")
    isc = ft.TextField(label="I_sc_ref", value="5.1")
    voc = ft.TextField(label="V_oc_ref", value="59.4")
    imp = ft.TextField(label="I_mp_ref", value="4.8")
    vmp = ft.TextField(label="V_mp_ref", value="48.3")
    alpha = ft.TextField(label="alpha_sc", value="0.0045")
    beta = ft.TextField(label="beta_oc", value="-0.22216")
    aref = ft.TextField(label="a_ref", value="2.6373")
    iref = ft.TextField(label="I_L_ref", value="5.114")
    io = ft.TextField(label="I_o_ref", value="8.196e-10")
    rs = ft.TextField(label="R_s", value="1.065")
    rsh = ft.TextField(label="R_sh_ref", value="381.68")
    gamma = ft.TextField(label="gamma_r", value="-0.476")
    noct = ft.TextField(label="T_NOCT", value="42.4")

    results_text = ft.Text("")

    page.add(ft.Column([
        area, cells, isc, voc, imp, vmp, alpha, beta, aref, iref, io, rs, rsh, gamma, noct,
        ft.TextButton("Submit", on_click=submit),
        results_text
    ]))

app = ft.App(pv_optimization_page)
app.run()
