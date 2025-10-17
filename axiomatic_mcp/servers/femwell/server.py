"""Axiomatic Femwell MCP server.

This server exposes tools that leverage Femwell to compute properties of
depletion waveguide modulators with PN junctions.

Tools provided:
- simulate_depletion_modulator: compute effective index and absorption vs voltage
  for a depletion waveguide modulator with PN junction.
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
        "This MCP server uses Femwell to simulate depletion waveguide modulators with PN junctions. "
        "It computes effective index and absorption as a function of applied voltage. "
        "CSV results and PNG plots are saved under 'mcp_output'."
    ),
    version="0.0.1",
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


def main() -> None:
    """Main entry point for the Femwell MCP server."""
    mcp.run()


