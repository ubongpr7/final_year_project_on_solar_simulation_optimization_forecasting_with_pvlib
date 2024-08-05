import flet as ft
import pvlib
import pandas as pd

def solar_design_page(page):
    def submit(e):
        parameters = {
            'Name': name.value,
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
        
        # Using pvlib to create a PV module
        module_parameters = pvlib.pvsystem.retrieve_sam('cecmod')['Canadian_Solar_CS5P_220M___2009_']
        
        # Overriding default parameters with user input
        for key, value in parameters.items():
            if key in module_parameters:
                module_parameters[key] = value

        # Assuming standard test conditions (STC) for the simulation
        effective_irradiance = 1000  # W/m^2
        temperature_cell = 25  # degrees Celsius

        # Calculating the module's performance
        single_diode_model = pvlib.pvsystem.calcparams_desoto(
            effective_irradiance,
            temperature_cell,
            **module_parameters
        )

        # Getting the IV curve points
        iv_curve = pvlib.pvsystem.singlediode(*single_diode_model)

        # Displaying the results
        results_text.value = (
            f"System designed successfully with provided parameters!\n"
            f"Max Power (Pmp): {iv_curve['p_mp']} W\n"
            f"Max Power Voltage (Vmp): {iv_curve['v_mp']} V\n"
            f"Max Power Current (Imp): {iv_curve['i_mp']} A\n"
            f"Open Circuit Voltage (Voc): {iv_curve['v_oc']} V\n"
            f"Short Circuit Current (Isc): {iv_curve['i_sc']} A"
        )
        page.update()

    name = ft.TextField(label="Name", value="Canadian_Solar_CS5P_220M___2009_")
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
        name, area, cells, isc, voc, imp, vmp, alpha, beta, aref, iref, io, rs, rsh, gamma, noct,
        ft.TextButton("Submit", on_click=submit),
        results_text
    ]))

app = ft.App(solar_design_page)
app.run()
