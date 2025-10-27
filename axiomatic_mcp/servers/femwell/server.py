"""Axiomatic Femwell MCP server.

This server exposes tools that leverage Femwell to compute properties of
photonic devices including phase shifters and waveguide dispersion.

Tools provided:
- simulate_depletion_modulator: compute effective index and absorption vs voltage
  for a depletion waveguide modulator with PN junction.
- simulate_metal_heater_phase_shifter: compute phase shift vs current for TiN metal
  heater phase shifters.
- simulate_doped_si_heater_phase_shifter: compute phase shift vs current for doped
  silicon heater phase shifters.
- simulate_waveguide_dispersion: compute effective index and group index vs wavelength
  for waveguides.
"""

from __future__ import annotations

import csv
import os
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from .tools.depletion_modulator import (
    compute_depletion_modulator,
    get_epsilon_for_plot,
)
from .tools.metal_heater import compute_metal_heater_phase_shifter
from .tools.doped_si_heater import compute_doped_si_heater_phase_shifter
from .tools.waveguide_dispersion import compute_waveguide_dispersion


def _ensure_output_dir() -> str:
    """Ensure `mcp_output` exists in the current working directory and return its path."""
    out_dir = os.path.join(os.getcwd(), "mcp_output")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def _generate_depletion_modulator_code(**kwargs) -> str:
    """Generate Python code for depletion modulator simulation."""
    voltages_str = str(kwargs.get('voltages', [-3, -2, -1, 0, 1, 2, 3]))

    return f'''"""Generated code for depletion modulator simulation.

This script reproduces the simulation that was run via the MCP server.
"""

import csv
import numpy as np
from matplotlib import pyplot as plt
from axiomatic_mcp.servers.femwell.tools.depletion_modulator import (
    compute_depletion_modulator,
    get_epsilon_for_plot,
)

# Simulation parameters
voltages = {voltages_str}
xpn = {kwargs.get('xpn', 0.0)}
NA = {kwargs.get('NA', 1e18)}
ND = {kwargs.get('ND', 1e18)}
wavelength = {kwargs.get('wavelength', 1.55)}
wg_width = {kwargs.get('wg_width', 0.5)}
wg_thickness = {kwargs.get('wg_thickness', 0.22)}
slab_width = {kwargs.get('slab_width', 3.0)}
slab_thickness = {kwargs.get('slab_thickness', 0.09)}
clad_thickness = {kwargs.get('clad_thickness', 2.0)}
core_index = {kwargs.get('core_index', 3.45)}
slab_index = {kwargs.get('slab_index', 3.45)}
clad_index = {kwargs.get('clad_index', 1.444)}
num_modes = {kwargs.get('num_modes', 1)}
mode_order = {kwargs.get('mode_order', 2)}
enable_epsilon_plot = {kwargs.get('enable_epsilon_plot', False)}
epsilon_plot_voltage = {kwargs.get('epsilon_plot_voltage', 0.0)}
output_prefix = "{kwargs.get('output_prefix', 'depletion_modulator')}"

# Main simulation code
saved_files = []

# Compute modulator characteristics
voltages_array, neff_array, neff_change, absorption_dB_per_cm = compute_depletion_modulator(
    voltages=voltages,
    xpn=xpn,
    NA=NA,
    ND=ND,
    wavelength=wavelength,
    wg_width=wg_width,
    wg_thickness=wg_thickness,
    slab_width=slab_width,
    slab_thickness=slab_thickness,
    clad_thickness=clad_thickness,
    core_index=core_index,
    slab_index=slab_index,
    clad_index=clad_index,
    num_modes=num_modes,
    mode_order=mode_order,
)

# Save CSV data
csv_path = f"{{output_prefix}}_results.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["voltage_V", "neff_real", "neff_imag", "neff_change", "absorption_dB_per_cm"])
    for V, neff, dneff, alpha in zip(
        voltages_array.tolist(),
        neff_array.tolist(),
        neff_change.tolist(),
        absorption_dB_per_cm.tolist()
    ):
        writer.writerow([
            float(V),
            float(np.real(neff)),
            float(np.imag(neff)),
            float(dneff),
            float(alpha)
        ])
saved_files.append(csv_path)

# Create plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)

ax1.plot(voltages_array, np.real(neff_change), '.-')
ax1.set_xlabel('Voltage [V]')
ax1.set_ylabel('Effective Index Change')
ax1.set_title('Phase Modulation')
ax1.grid(True, alpha=0.3)

ax2.plot(voltages_array, absorption_dB_per_cm, '.-')
ax2.set_xlabel('Voltage [V]')
ax2.set_ylabel('Absorption [dB/cm]')
ax2.set_title('Absorption vs Voltage')
ax2.grid(True, alpha=0.3)

plot_path = f"{{output_prefix}}_modulation.png"
fig.savefig(plot_path, dpi=150)
plt.close(fig)
saved_files.append(plot_path)

# Epsilon plot
if enable_epsilon_plot:
    mesh, basis0, epsilon = get_epsilon_for_plot(
        voltage=epsilon_plot_voltage,
        xpn=xpn,
        NA=NA,
        ND=ND,
        wavelength=wavelength,
        wg_width=wg_width,
        wg_thickness=wg_thickness,
        slab_width=slab_width,
        slab_thickness=slab_thickness,
        clad_thickness=clad_thickness,
        core_index=core_index,
        slab_index=slab_index,
        clad_index=clad_index,
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)

    basis0.plot(np.real(epsilon), ax=ax1, colorbar=True)
    ax1.set_title(f'Real(ε) at {{epsilon_plot_voltage}}V')
    ax1.set_xlabel('x [µm]')
    ax1.set_ylabel('y [µm]')

    basis0.plot(np.imag(epsilon), ax=ax2, colorbar=True)
    ax2.set_title(f'Imag(ε) at {{epsilon_plot_voltage}}V')
    ax2.set_xlabel('x [µm]')
    ax2.set_ylabel('y [µm]')

    epsilon_plot_path = f"{{output_prefix}}_epsilon_V{{epsilon_plot_voltage}}.png"
    fig.savefig(epsilon_plot_path, dpi=150)
    plt.close(fig)
    saved_files.append(epsilon_plot_path)

print(f"Simulation completed. Saved {{len(saved_files)}} files: {{saved_files}}")
'''


mcp = FastMCP(
    name="Axiomatic Femwell",
    instructions=(
        "This MCP server uses Femwell to simulate photonic devices including: "
        "1) Depletion modulators with PN junctions (neff vs voltage), "
        "2) Metal heater phase shifters (phase shift vs current), "
        "3) Doped silicon heater phase shifters (phase shift vs current), "
        "4) Waveguide dispersion (neff, ng, GVD vs wavelength). "
        "CSV results and PNG plots are saved under 'mcp_output'."
    ),
    version="0.1.0",
)


@mcp.tool(
    name="simulate_depletion_modulator",
    description=(
        "Compute effective index and absorption vs voltage for a depletion waveguide modulator "
        "with PN junction using Femwell. Saves CSV/PNG files to 'mcp_output'."
    ),
    tags=["simulation", "photonic", "femwell", "modulator", "depletion"],
)
async def simulate_depletion_modulator(
    # Voltage sweep
    voltages: Annotated[list[float], "List of voltages to sweep (V)"] = None,
    # PN junction parameters
    xpn: Annotated[float, "PN junction position (µm)"] = 0.0,
    NA: Annotated[float, "Acceptor doping concentration (cm^-3)"] = 1e18,
    ND: Annotated[float, "Donor doping concentration (cm^-3)"] = 1e18,
    # Operating wavelength
    wavelength: Annotated[float, "Wavelength in micrometers"] = 1.55,
    # Geometry (micrometers)
    wg_width: Annotated[float, "Waveguide width in micrometers"] = 0.5,
    wg_thickness: Annotated[float, "Waveguide thickness in micrometers"] = 0.22,
    slab_width: Annotated[float, "Slab width in micrometers"] = 3.0,
    slab_thickness: Annotated[float, "Slab thickness in micrometers"] = 0.09,
    clad_thickness: Annotated[float, "Cladding thickness in micrometers"] = 2.0,
    # Material indices
    core_index: Annotated[float, "Refractive index of core"] = 3.45,
    slab_index: Annotated[float, "Refractive index of slab"] = 3.45,
    clad_index: Annotated[float, "Refractive index of cladding"] = 1.444,
    # Mode solver parameters
    num_modes: Annotated[int, "Number of modes to compute"] = 1,
    mode_order: Annotated[int, "Mode solver order"] = 2,
    # Plotting options
    enable_epsilon_plot: Annotated[bool, "Whether to save epsilon distribution plot"] = False,
    epsilon_plot_voltage: Annotated[float, "Voltage (V) for epsilon plot"] = 0.0,
    # Outputs
    output_prefix: Annotated[str, "Filename prefix for outputs (CSV/PNG)"] = "depletion_modulator",
) -> ToolResult:
    try:
        import numpy as np
        from matplotlib import pyplot as plt

        # Default voltage sweep if not provided
        if voltages is None:
            voltages = [-3, -2, -1, 0, 1, 2, 3]

        out_dir = _ensure_output_dir()

        saved_files: list[str] = []

        # Generate and save Python code
        code_content = _generate_depletion_modulator_code(**locals())
        code_path = os.path.join(out_dir, f"{output_prefix}_simulation.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        saved_files.append(code_path)

        # Compute modulator characteristics
        voltages_array, neff_array, neff_change, absorption_dB_per_cm = compute_depletion_modulator(
            voltages=voltages,
            xpn=xpn,
            NA=NA,
            ND=ND,
            wavelength=wavelength,
            wg_width=wg_width,
            wg_thickness=wg_thickness,
            slab_width=slab_width,
            slab_thickness=slab_thickness,
            clad_thickness=clad_thickness,
            core_index=core_index,
            slab_index=slab_index,
            clad_index=clad_index,
            num_modes=num_modes,
            mode_order=mode_order,
        )

        # Save CSV data
        csv_path = os.path.join(out_dir, f"{output_prefix}_results.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["voltage_V", "neff_real", "neff_imag", "neff_change", "absorption_dB_per_cm"])
            for V, neff, dneff, alpha in zip(
                voltages_array.tolist(),
                neff_array.tolist(),
                neff_change.tolist(),
                absorption_dB_per_cm.tolist()
            ):
                writer.writerow([
                    float(V),
                    float(np.real(neff)),
                    float(np.imag(neff)),
                    float(dneff),
                    float(alpha)
                ])
        saved_files.append(csv_path)

        # Create plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)

        ax1.plot(voltages_array, np.real(neff_change), '.-')
        ax1.set_xlabel('Voltage [V]')
        ax1.set_ylabel('Effective Index Change')
        ax1.set_title('Phase Modulation')
        ax1.grid(True, alpha=0.3)

        ax2.plot(voltages_array, absorption_dB_per_cm, '.-')
        ax2.set_xlabel('Voltage [V]')
        ax2.set_ylabel('Absorption [dB/cm]')
        ax2.set_title('Absorption vs Voltage')
        ax2.grid(True, alpha=0.3)

        plot_path = os.path.join(out_dir, f"{output_prefix}_modulation.png")
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)
        saved_files.append(plot_path)

        # Epsilon plot
        if enable_epsilon_plot:
            mesh, basis0, epsilon = get_epsilon_for_plot(
                voltage=epsilon_plot_voltage,
                xpn=xpn,
                NA=NA,
                ND=ND,
                wavelength=wavelength,
                wg_width=wg_width,
                wg_thickness=wg_thickness,
                slab_width=slab_width,
                slab_thickness=slab_thickness,
                clad_thickness=clad_thickness,
                core_index=core_index,
                slab_index=slab_index,
                clad_index=clad_index,
            )

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)

            basis0.plot(np.real(epsilon), ax=ax1, colorbar=True)
            ax1.set_title(f'Real(ε) at {epsilon_plot_voltage}V')
            ax1.set_xlabel('x [µm]')
            ax1.set_ylabel('y [µm]')

            basis0.plot(np.imag(epsilon), ax=ax2, colorbar=True)
            ax2.set_title(f'Imag(ε) at {epsilon_plot_voltage}V')
            ax2.set_xlabel('x [µm]')
            ax2.set_ylabel('y [µm]')

            epsilon_plot_path = os.path.join(out_dir, f"{output_prefix}_epsilon_V{epsilon_plot_voltage}.png")
            fig.savefig(epsilon_plot_path, dpi=150)
            plt.close(fig)
            saved_files.append(epsilon_plot_path)

        summary_lines = [
            "Depletion modulator simulation completed.",
            f"Saved {len(saved_files)} file(s) to: {out_dir}",
            f"Voltage range: {min(voltages)} to {max(voltages)} V",
            f"Δn_eff range: {min(neff_change):.6f} to {max(neff_change):.6f}",
            f"Absorption range: {min(absorption_dB_per_cm):.2f} to {max(absorption_dB_per_cm):.2f} dB/cm",
        ]
        return ToolResult(
            content=[TextContent(type="text", text="\n".join(summary_lines))],
            structured_content={
                "output_dir": out_dir,
                "saved_files": saved_files,
                "voltages_V": voltages_array.tolist(),
                "neff_real": np.real(neff_array).tolist(),
                "neff_imag": np.imag(neff_array).tolist(),
                "neff_change": neff_change.tolist(),
                "absorption_dB_per_cm": absorption_dB_per_cm.tolist(),
            },
        )

    except Exception as e:  # noqa: BLE001
        return ToolResult(content=[TextContent(type="text", text=f"Depletion modulator simulation failed: {e!s}")])


@mcp.tool(
    name="simulate_metal_heater_phase_shifter",
    description=(
        "Compute phase shift vs current for a TiN metal heater phase shifter using Femwell. "
        "Calculates thermal distribution and resulting phase shift for thermo-optic modulators. "
        "Saves CSV/PNG files to 'mcp_output'."
    ),
    tags=["simulation", "photonic", "femwell", "phase-shifter", "thermal", "heater"],
)
async def simulate_metal_heater_phase_shifter(
    # Current sweep
    currents: Annotated[list[float], "List of currents in amperes (A)"] = None,
    # Operating wavelength
    wavelength: Annotated[float, "Wavelength in micrometers"] = 1.55,
    phase_shifter_length: Annotated[float, "Phase shifter length in micrometers"] = 320.0,
    # Geometry (micrometers)
    w_sim: Annotated[float, "Simulation width in micrometers"] = 16.0,
    h_clad: Annotated[float, "Cladding height in micrometers"] = 2.8,
    h_box: Annotated[float, "BOX layer height in micrometers"] = 2.0,
    w_core: Annotated[float, "Core width in micrometers"] = 0.5,
    h_core: Annotated[float, "Core height in micrometers"] = 0.22,
    h_heater: Annotated[float, "Heater height in micrometers"] = 0.14,
    w_heater: Annotated[float, "Heater width in micrometers"] = 2.0,
    offset_heater: Annotated[float, "Heater offset from waveguide surface in micrometers"] = 2.0,
    # Thermal conductivities (W/(m*K))
    k_core: Annotated[float, "Thermal conductivity of core (W/(m*K))"] = 90.0,
    k_box: Annotated[float, "Thermal conductivity of BOX (W/(m*K))"] = 1.38,
    k_clad: Annotated[float, "Thermal conductivity of cladding (W/(m*K))"] = 1.38,
    k_heater: Annotated[float, "Thermal conductivity of heater (W/(m*K))"] = 28.0,
    # Thermo-optic coefficients (1/K)
    dn_dT_clad: Annotated[float, "Thermo-optic coefficient of cladding (1/K)"] = 1.00e-5,
    dn_dT_core: Annotated[float, "Thermo-optic coefficient of core (1/K)"] = 1.86e-4,
    # Heater electrical properties
    heater_resistivity: Annotated[float, "Heater electrical conductivity (S/m)"] = 2.3e6,
    # Outputs
    output_prefix: Annotated[str, "Filename prefix for outputs (CSV/PNG)"] = "metal_heater",
) -> ToolResult:
    try:
        import numpy as np
        from matplotlib import pyplot as plt

        # Default current sweep if not provided (0 to 7.4 mA)
        if currents is None:
            currents = list(np.linspace(0.0, 7.4e-3, 10))

        out_dir = _ensure_output_dir()
        saved_files: list[str] = []

        # Compute phase shifter characteristics
        currents_array, powers_mW, neffs, phase_shifts_rad, temps_list, basis_list = compute_metal_heater_phase_shifter(
            currents=currents,
            wavelength=wavelength,
            phase_shifter_length=phase_shifter_length,
            w_sim=w_sim,
            h_clad=h_clad,
            h_box=h_box,
            w_core=w_core,
            h_core=h_core,
            h_heater=h_heater,
            w_heater=w_heater,
            offset_heater=offset_heater,
            k_core=k_core,
            k_box=k_box,
            k_clad=k_clad,
            k_heater=k_heater,
            dn_dT_clad=dn_dT_clad,
            dn_dT_core=dn_dT_core,
            heater_resistivity=heater_resistivity,
        )

        # Save CSV data
        csv_path = os.path.join(out_dir, f"{output_prefix}_results.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["current_A", "power_mW", "neff", "phase_shift_rad", "phase_shift_pi"])
            for I, P, neff, phase_rad in zip(
                currents_array.tolist(),
                powers_mW.tolist(),
                neffs.tolist(),
                phase_shifts_rad.tolist()
            ):
                writer.writerow([
                    float(I),
                    float(P),
                    float(neff),
                    float(phase_rad),
                    float(phase_rad / np.pi)
                ])
        saved_files.append(csv_path)

        # Create plots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)

        # Plot 1: neff vs current
        ax1.plot(currents_array * 1e3, neffs, '.-')
        ax1.set_xlabel('Current [mA]')
        ax1.set_ylabel('Effective Index $n_{eff}$')
        ax1.set_title('Effective Index vs Current')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Phase shift vs current
        ax2.plot(currents_array * 1e3, phase_shifts_rad / np.pi, '.-')
        ax2.set_xlabel('Current [mA]')
        ax2.set_ylabel('Phase Shift [π rad]')
        ax2.set_title('Phase Shift vs Current')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='π phase shift')
        ax2.legend()

        # Plot 3: Phase shift vs power
        ax3.plot(powers_mW, phase_shifts_rad / np.pi, '.-')
        ax3.set_xlabel('Power [mW]')
        ax3.set_ylabel('Phase Shift [π rad]')
        ax3.set_title('Phase Shift vs Power')
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='π phase shift')
        ax3.legend()

        # Plot 4: Temperature distribution (last current)
        if len(temps_list) > 0 and len(basis_list) > 0:
            basis_list[-1].plot(temps_list[-1], ax=ax4, shading="gouraud", colorbar=True)
            ax4.set_title(f'Temperature @ I={currents_array[-1]*1e3:.2f} mA')
            ax4.set_xlabel('x [µm]')
            ax4.set_ylabel('y [µm]')

        plot_path = os.path.join(out_dir, f"{output_prefix}_phase_shift.png")
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)
        saved_files.append(plot_path)

        # Calculate P_pi (power for pi phase shift)
        # Find where phase shift crosses pi
        phase_pi_idx = np.where(phase_shifts_rad >= np.pi)[0]
        if len(phase_pi_idx) > 0:
            P_pi = powers_mW[phase_pi_idx[0]]
            I_pi = currents_array[phase_pi_idx[0]] * 1e3  # Convert to mA
        else:
            P_pi = None
            I_pi = None

        summary_lines = [
            "Metal heater phase shifter simulation completed.",
            f"Saved {len(saved_files)} file(s) to: {out_dir}",
            f"Current range: {min(currents_array)*1e3:.3f} to {max(currents_array)*1e3:.3f} mA",
            f"Phase shift range: {min(phase_shifts_rad)/np.pi:.3f}π to {max(phase_shifts_rad)/np.pi:.3f}π",
        ]
        if P_pi is not None:
            summary_lines.append(f"P_π = {P_pi:.2f} mW (I_π = {I_pi:.3f} mA)")
        else:
            summary_lines.append("P_π not reached in current range")

        return ToolResult(
            content=[TextContent(type="text", text="\n".join(summary_lines))],
            structured_content={
                "output_dir": out_dir,
                "saved_files": saved_files,
                "currents_A": currents_array.tolist(),
                "powers_mW": powers_mW.tolist(),
                "neffs": neffs.tolist(),
                "phase_shifts_rad": phase_shifts_rad.tolist(),
                "phase_shifts_pi": (phase_shifts_rad / np.pi).tolist(),
                "P_pi_mW": float(P_pi) if P_pi is not None else None,
                "I_pi_mA": float(I_pi) if I_pi is not None else None,
            },
        )

    except Exception as e:  # noqa: BLE001
        return ToolResult(content=[TextContent(type="text", text=f"Metal heater simulation failed: {e!s}")])


@mcp.tool(
    name="simulate_doped_si_heater_phase_shifter",
    description=(
        "Compute phase shift vs power for a doped silicon heater phase shifter using Femwell. "
        "Uses rib waveguide with lateral doped Si heaters. Calculates thermal distribution and "
        "resulting phase shift for thermo-optic modulators. Saves CSV/PNG files to 'mcp_output'."
    ),
    tags=["simulation", "photonic", "femwell", "phase-shifter", "thermal", "heater", "doped-silicon"],
)
async def simulate_doped_si_heater_phase_shifter(
    # Power sweep
    powers_mW: Annotated[list[float], "List of electrical powers in milliwatts (mW)"] = None,
    # Operating wavelength
    wavelength: Annotated[float, "Wavelength in micrometers"] = 1.55,
    phase_shifter_length: Annotated[float, "Phase shifter length in micrometers"] = 320.0,
    # Geometry (micrometers)
    w_sim: Annotated[float, "Simulation width in micrometers"] = 32.0,
    h_clad: Annotated[float, "Cladding height in micrometers"] = 2.8,
    h_box: Annotated[float, "BOX layer height in micrometers"] = 2.0,
    w_core: Annotated[float, "Core width in micrometers"] = 0.5,
    h_core: Annotated[float, "Core height in micrometers"] = 0.22,
    w_buffer: Annotated[float, "Buffer/slab width on each side in micrometers"] = 0.8,
    h_buffer: Annotated[float, "Buffer/slab height in micrometers"] = 0.09,
    w_heater: Annotated[float, "Heater width in micrometers"] = 1.0,
    # Thermal conductivities (W/(m*K))
    k_core: Annotated[float, "Thermal conductivity of core (W/(m*K))"] = 90.0,
    k_box: Annotated[float, "Thermal conductivity of BOX (W/(m*K))"] = 1.38,
    k_clad: Annotated[float, "Thermal conductivity of cladding (W/(m*K))"] = 1.38,
    k_slab: Annotated[float, "Thermal conductivity of slab (W/(m*K))"] = 55.0,
    k_heater: Annotated[float, "Thermal conductivity of heater (W/(m*K))"] = 55.0,
    # Thermo-optic coefficients (1/K)
    dn_dT_clad: Annotated[float, "Thermo-optic coefficient of cladding (1/K)"] = 1.00e-5,
    dn_dT_core: Annotated[float, "Thermo-optic coefficient of core (1/K)"] = 1.86e-4,
    # Heater electrical properties
    heater_resistivity: Annotated[float, "Heater electrical conductivity (S/m)"] = 1e5,
    # Outputs
    output_prefix: Annotated[str, "Filename prefix for outputs (CSV/PNG)"] = "doped_si_heater",
) -> ToolResult:
    try:
        import numpy as np
        from matplotlib import pyplot as plt

        # Default power sweep if not provided (0 to 30 mW)
        if powers_mW is None:
            powers_mW = list(np.linspace(0.0, 30.0, 10))

        out_dir = _ensure_output_dir()
        saved_files: list[str] = []

        # Compute phase shifter characteristics
        powers_mW_array, currents_A, neffs, phase_shifts_rad, temps_list, basis_list = compute_doped_si_heater_phase_shifter(
            powers_mW=powers_mW,
            wavelength=wavelength,
            phase_shifter_length=phase_shifter_length,
            w_sim=w_sim,
            h_clad=h_clad,
            h_box=h_box,
            w_core=w_core,
            h_core=h_core,
            w_buffer=w_buffer,
            h_buffer=h_buffer,
            w_heater=w_heater,
            k_core=k_core,
            k_box=k_box,
            k_clad=k_clad,
            k_slab=k_slab,
            k_heater=k_heater,
            dn_dT_clad=dn_dT_clad,
            dn_dT_core=dn_dT_core,
            heater_resistivity=heater_resistivity,
        )

        # Save CSV data
        csv_path = os.path.join(out_dir, f"{output_prefix}_results.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["power_mW", "current_A", "neff", "phase_shift_rad", "phase_shift_pi"])
            for P, I, neff, phase_rad in zip(
                powers_mW_array.tolist(),
                currents_A.tolist(),
                neffs.tolist(),
                phase_shifts_rad.tolist()
            ):
                writer.writerow([
                    float(P),
                    float(I),
                    float(neff),
                    float(phase_rad),
                    float(phase_rad / np.pi)
                ])
        saved_files.append(csv_path)

        # Create plots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)

        # Plot 1: neff vs power
        ax1.plot(powers_mW_array, neffs, '.-')
        ax1.set_xlabel('Power [mW]')
        ax1.set_ylabel('Effective Index $n_{eff}$')
        ax1.set_title('Effective Index vs Power')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Phase shift vs power
        ax2.plot(powers_mW_array, phase_shifts_rad / np.pi, '.-')
        ax2.set_xlabel('Power [mW]')
        ax2.set_ylabel('Phase Shift [π rad]')
        ax2.set_title('Phase Shift vs Power')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='π phase shift')
        ax2.legend()

        # Plot 3: Phase shift vs current
        ax3.plot(currents_A * 1e3, phase_shifts_rad / np.pi, '.-')
        ax3.set_xlabel('Current [mA]')
        ax3.set_ylabel('Phase Shift [π rad]')
        ax3.set_title('Phase Shift vs Current')
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='π phase shift')
        ax3.legend()

        # Plot 4: Temperature distribution (last power)
        if len(temps_list) > 0 and len(basis_list) > 0:
            basis_list[-1].plot(temps_list[-1], ax=ax4, shading="gouraud", colorbar=True)
            ax4.set_title(f'Temperature @ P={powers_mW_array[-1]:.2f} mW')
            ax4.set_xlabel('x [µm]')
            ax4.set_ylabel('y [µm]')

        plot_path = os.path.join(out_dir, f"{output_prefix}_phase_shift.png")
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)
        saved_files.append(plot_path)

        # Calculate P_pi (power for pi phase shift)
        phase_pi_idx = np.where(phase_shifts_rad >= np.pi)[0]
        if len(phase_pi_idx) > 0:
            P_pi = powers_mW_array[phase_pi_idx[0]]
            I_pi = currents_A[phase_pi_idx[0]] * 1e3  # Convert to mA
        else:
            P_pi = None
            I_pi = None

        summary_lines = [
            "Doped silicon heater phase shifter simulation completed.",
            f"Saved {len(saved_files)} file(s) to: {out_dir}",
            f"Power range: {min(powers_mW_array):.3f} to {max(powers_mW_array):.3f} mW",
            f"Phase shift range: {min(phase_shifts_rad)/np.pi:.3f}pi to {max(phase_shifts_rad)/np.pi:.3f}pi",
        ]
        if P_pi is not None:
            summary_lines.append(f"P_pi = {P_pi:.2f} mW (I_pi = {I_pi:.3f} mA)")
        else:
            summary_lines.append("P_pi not reached in power range")

        return ToolResult(
            content=[TextContent(type="text", text="\n".join(summary_lines))],
            structured_content={
                "output_dir": out_dir,
                "saved_files": saved_files,
                "powers_mW": powers_mW_array.tolist(),
                "currents_A": currents_A.tolist(),
                "neffs": neffs.tolist(),
                "phase_shifts_rad": phase_shifts_rad.tolist(),
                "phase_shifts_pi": (phase_shifts_rad / np.pi).tolist(),
                "P_pi_mW": float(P_pi) if P_pi is not None else None,
                "I_pi_mA": float(I_pi) if I_pi is not None else None,
            },
        )

    except Exception as e:  # noqa: BLE001
        return ToolResult(content=[TextContent(type="text", text=f"Doped Si heater simulation failed: {e!s}")])


@mcp.tool(
    name="simulate_waveguide_dispersion",
    description=(
        "Compute effective index, group index, and group velocity dispersion vs wavelength "
        "for dielectric waveguides using Femwell. Supports Si3N4, SiO2, Si, and custom materials. "
        "Saves CSV/PNG files to 'mcp_output'."
    ),
    tags=["simulation", "photonic", "femwell", "dispersion", "waveguide"],
)
async def simulate_waveguide_dispersion(
    # Wavelength sweep
    wavelengths: Annotated[list[float], "List of wavelengths in micrometers"] = None,
    # Geometry (micrometers)
    w_core: Annotated[float, "Core width in micrometers"] = 1.0,
    h_core: Annotated[float, "Core height in micrometers"] = 0.5,
    # Materials (use "Si3N4", "SiO2", "Si", "air", or numeric value for constant n)
    core_material: Annotated[str, "Core material (Si3N4/SiO2/Si/air or numeric)"] = "Si3N4",
    box_material: Annotated[str, "BOX material (Si3N4/SiO2/Si/air or numeric)"] = "SiO2",
    clad_material: Annotated[str, "Cladding material (Si3N4/SiO2/Si/air or numeric)"] = "air",
    # Mode solver parameters
    num_modes: Annotated[int, "Number of modes to compute"] = 2,
    # Outputs
    output_prefix: Annotated[str, "Filename prefix for outputs (CSV/PNG)"] = "waveguide_dispersion",
) -> ToolResult:
    try:
        import numpy as np
        from matplotlib import pyplot as plt

        # Default wavelength sweep if not provided (1.2 to 1.9 um, 20 points)
        if wavelengths is None:
            wavelengths = list(np.linspace(1.2, 1.9, 20))

        out_dir = _ensure_output_dir()
        saved_files: list[str] = []

        # Compute dispersion
        wavelengths_array, neffs, ng_array, gvd_array, te_fracs = compute_waveguide_dispersion(
            wavelengths=wavelengths,
            w_core=w_core,
            h_core=h_core,
            core_material=core_material,
            box_material=box_material,
            clad_material=clad_material,
            num_modes=num_modes,
        )

        # Save CSV data (one row per wavelength-mode combination)
        csv_path = os.path.join(out_dir, f"{output_prefix}_results.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["wavelength_um", "mode_index", "neff", "ng", "gvd_ps_nm_km", "te_fraction"])
            for i, wl in enumerate(wavelengths_array):
                for mode_idx in range(num_modes):
                    writer.writerow([
                        float(wl),
                        int(mode_idx),
                        float(neffs[i, mode_idx]),
                        float(ng_array[i, mode_idx]),
                        float(gvd_array[i, mode_idx]),
                        float(te_fracs[i, mode_idx]),
                    ])
        saved_files.append(csv_path)

        # Create plots
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4), constrained_layout=True)

        # Plot 1: Effective index vs wavelength
        ax1.set_xlabel('Wavelength [µm]')
        ax1.set_ylabel('Effective Refractive Index')
        ax1.set_title('Dispersion Relation')
        for mode_idx in range(num_modes):
            neff_mode = neffs[:, mode_idx]
            te_frac_mode = te_fracs[:, mode_idx]
            line = ax1.plot(wavelengths_array, neff_mode, '.-', label=f'Mode {mode_idx}')[0]
            ax1.scatter(wavelengths_array, neff_mode, c=te_frac_mode, cmap='cool', vmin=0, vmax=1, s=30)
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Plot 2: Group index vs wavelength
        ax2.set_xlabel('Wavelength [µm]')
        ax2.set_ylabel('Group Index $n_g$')
        ax2.set_title('Group Index')
        for mode_idx in range(num_modes):
            ng_mode = ng_array[:, mode_idx]
            te_frac_mode = te_fracs[:, mode_idx]
            line = ax2.plot(wavelengths_array, ng_mode, '.-', label=f'Mode {mode_idx}')[0]
            ax2.scatter(wavelengths_array, ng_mode, c=te_frac_mode, cmap='cool', vmin=0, vmax=1, s=30)
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        # Plot 3: GVD vs wavelength
        ax3.set_xlabel('Wavelength [µm]')
        ax3.set_ylabel('GVD $D$ [ps/(nm·km)]')
        ax3.set_title('Group Velocity Dispersion')
        for mode_idx in range(num_modes):
            gvd_mode = gvd_array[:, mode_idx]
            te_frac_mode = te_fracs[:, mode_idx]
            line = ax3.plot(wavelengths_array, gvd_mode, '.-', label=f'Mode {mode_idx}')[0]
            scatter = ax3.scatter(wavelengths_array, gvd_mode, c=te_frac_mode, cmap='cool', vmin=0, vmax=1, s=30)
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)

        # Add colorbar
        cbar = fig.colorbar(scatter, ax=[ax1, ax2, ax3], location='right', shrink=0.6)
        cbar.set_label('TE Fraction')

        plot_path = os.path.join(out_dir, f"{output_prefix}_dispersion.png")
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)
        saved_files.append(plot_path)

        summary_lines = [
            "Waveguide dispersion simulation completed.",
            f"Saved {len(saved_files)} file(s) to: {out_dir}",
            f"Wavelength range: {min(wavelengths_array):.3f} to {max(wavelengths_array):.3f} µm",
            f"Number of modes: {num_modes}",
            f"neff range (mode 0): {min(neffs[:, 0]):.4f} to {max(neffs[:, 0]):.4f}",
            f"ng range (mode 0): {min(ng_array[:, 0]):.4f} to {max(ng_array[:, 0]):.4f}",
        ]

        return ToolResult(
            content=[TextContent(type="text", text="\n".join(summary_lines))],
            structured_content={
                "output_dir": out_dir,
                "saved_files": saved_files,
                "wavelengths_um": wavelengths_array.tolist(),
                "neff": neffs.tolist(),
                "ng": ng_array.tolist(),
                "gvd_ps_nm_km": gvd_array.tolist(),
                "te_fraction": te_fracs.tolist(),
            },
        )

    except Exception as e:  # noqa: BLE001
        return ToolResult(content=[TextContent(type="text", text=f"Waveguide dispersion simulation failed: {e!s}")])


def main() -> None:
    """Main entry point for the Femwell MCP server."""
    mcp.run()


