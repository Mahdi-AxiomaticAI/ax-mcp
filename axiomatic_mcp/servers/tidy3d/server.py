"""Axiomatic Tidy3D MCP server.

This server exposes tools that leverage Ansys Tidy3D to compute properties of
waveguide couplers and single waveguide dispersion.

Tools provided:
- simulate_waveguide_coupler: compute coupling vs wavelength and/or vs length,
  and optionally export two mode-field plots.
- simulate_waveguide_dispersion: compute effective index and group index vs wavelength
  for a single rectangular waveguide.
"""

from __future__ import annotations

import csv
import os
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from .tools.wg_coupler import (
    compute_coupling_vs_length,
    compute_coupling_vs_wavelength,
    get_coupled_for_mode_plot,
)
from .tools.wg_dispersion import (
    compute_waveguide_dispersion,
    get_waveguide_for_mode_plot,
)


def _ensure_output_dir() -> str:
    """Ensure `mcp_output` exists in the current working directory and return its path."""
    out_dir = os.path.join(os.getcwd(), "mcp_output")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def _generate_coupler_code(**kwargs) -> str:
    """Generate Python code for waveguide coupler simulation."""
    return f'''"""Generated code for waveguide coupler simulation.

This script reproduces the simulation that was run via the MCP server.
"""

import csv
import numpy as np
from matplotlib import pyplot as plt
from axiomatic_mcp.servers.tidy3d.tools.wg_coupler import (
    compute_coupling_vs_wavelength,
    compute_coupling_vs_length,
    get_coupled_for_mode_plot,
)

# Simulation parameters
core_material_family = "{kwargs.get('core_material_family', 'cSi')}"
core_material_model = "{kwargs.get('core_material_model', 'Palik_Lossless')}"
clad_material_family = "{kwargs.get('clad_material_family', 'SiO2')}"
clad_material_model = "{kwargs.get('clad_material_model', 'Palik_Lossless')}"
wg_width1_um = {kwargs.get('wg_width1_um', 0.5)}
wg_width2_um = {kwargs.get('wg_width2_um', 0.5)}
wg_height_um = {kwargs.get('wg_height_um', 0.22)}
wg_gap_um = {kwargs.get('wg_gap_um', 0.2)}
coupler_length_um = {kwargs.get('coupler_length_um', 50.0)}
sidewall_angle_deg = {kwargs.get('sidewall_angle_deg', 0.0)}
polarization = "{kwargs.get('polarization', 'te')}"
enable_coupling_vs_wavelength = {kwargs.get('enable_coupling_vs_wavelength', True)}
lam_start_um = {kwargs.get('lam_start_um', 1.27)}
lam_stop_um = {kwargs.get('lam_stop_um', 1.31)}
num_wavelength_points = {kwargs.get('num_wavelength_points', 100)}
enable_coupling_vs_length = {kwargs.get('enable_coupling_vs_length', True)}
length_start_um = {kwargs.get('length_start_um', 0.0)}
length_stop_um = {kwargs.get('length_stop_um', 100.0)}
num_length_points = {kwargs.get('num_length_points', 21)}
length_wavelength_um = {kwargs.get('length_wavelength_um', 1.31)}
enable_mode_plots = {kwargs.get('enable_mode_plots', False)}
mode_plot_wavelength_um = {kwargs.get('mode_plot_wavelength_um', 1.3)}
output_prefix = "{kwargs.get('output_prefix', 'wg_coupler')}"

# Main simulation code
saved_files = []

# Coupling vs wavelength
if enable_coupling_vs_wavelength:
    wls_um, p_coupling_wl = compute_coupling_vs_wavelength(
        core_material_family=core_material_family,
        core_material_model=core_material_model,
        clad_material_family=clad_material_family,
        clad_material_model=clad_material_model,
        wg_width1_um=wg_width1_um,
        wg_width2_um=wg_width2_um,
        wg_height_um=wg_height_um,
        wg_gap_um=wg_gap_um,
        coupler_length_um=coupler_length_um,
        sidewall_angle_deg=sidewall_angle_deg,
        polarization=polarization,
        lam_start_um=lam_start_um,
        lam_stop_um=lam_stop_um,
        num_wavelength_points=num_wavelength_points,
    )

    csv_path_wl = f"{{output_prefix}}_coupling_vs_wavelength.csv"
    with open(csv_path_wl, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["wavelength_um", "power_coupling"])
        for lam, pc in zip(wls_um.tolist(), p_coupling_wl.tolist()):
            writer.writerow([float(lam), float(pc)])
    saved_files.append(csv_path_wl)

    # Save plot
    fig, ax = plt.subplots(figsize=(5, 3.2), constrained_layout=True)
    ax.plot(wls_um, p_coupling_wl, ".-")
    ax.set_xlabel("Wavelength [µm]")
    ax.set_ylabel("Power coupling [a.u.]")
    ax.set_title("Coupling vs wavelength")
    plot_path_wl = f"{{output_prefix}}_coupling_vs_wavelength.png"
    fig.savefig(plot_path_wl, dpi=150)
    plt.close(fig)
    saved_files.append(plot_path_wl)

# Coupling vs length
if enable_coupling_vs_length:
    lengths_um, p_coupling_len = compute_coupling_vs_length(
        core_material_family=core_material_family,
        core_material_model=core_material_model,
        clad_material_family=clad_material_family,
        clad_material_model=clad_material_model,
        wg_width1_um=wg_width1_um,
        wg_width2_um=wg_width2_um,
        wg_height_um=wg_height_um,
        wg_gap_um=wg_gap_um,
        sidewall_angle_deg=sidewall_angle_deg,
        polarization=polarization,
        length_start_um=length_start_um,
        length_stop_um=length_stop_um,
        num_length_points=num_length_points,
        wavelength_um=length_wavelength_um,
    )

    csv_path_len = f"{{output_prefix}}_coupling_vs_length.csv"
    with open(csv_path_len, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["length_um", "power_coupling"])
        for L, pc in zip(lengths_um.tolist(), p_coupling_len.tolist()):
            writer.writerow([float(L), float(pc)])
    saved_files.append(csv_path_len)

    # Save plot
    fig, ax = plt.subplots(figsize=(5, 3.2), constrained_layout=True)
    ax.plot(lengths_um, p_coupling_len, ".-")
    ax.set_xlabel("Coupler length [µm]")
    ax.set_ylabel("Power coupling [a.u.]")
    ax.set_title("Coupling vs length")
    plot_path_len = f"{{output_prefix}}_coupling_vs_length.png"
    fig.savefig(plot_path_len, dpi=150)
    plt.close(fig)
    saved_files.append(plot_path_len)

# Mode plots
if enable_mode_plots:
    coupled = get_coupled_for_mode_plot(
        core_material_family=core_material_family,
        core_material_model=core_material_model,
        clad_material_family=clad_material_family,
        clad_material_model=clad_material_model,
        wg_width1_um=wg_width1_um,
        wg_width2_um=wg_width2_um,
        wg_height_um=wg_height_um,
        wg_gap_um=wg_gap_um,
        sidewall_angle_deg=sidewall_angle_deg,
        polarization=polarization,
        wavelength_um=mode_plot_wavelength_um,
    )

    from matplotlib import pyplot as pyplot

    fig, ax = pyplot.subplots(1, 2, figsize=(8, 4), tight_layout=True)
    coupled.plot_field("Ey", mode_index=0, ax=ax[0])
    ax[0].set_title("Ey mode 0")
    coupled.plot_field("Ey", mode_index=1, ax=ax[1])
    ax[1].set_title("Ey mode 1")
    mode_plot_path = f"{{output_prefix}}_modes_Ey.png"
    fig.savefig(mode_plot_path, dpi=150)
    pyplot.close(fig)
    saved_files.append(mode_plot_path)

print(f"Simulation completed. Saved {{len(saved_files)}} files: {{saved_files}}")
'''


def _generate_dispersion_code(**kwargs) -> str:
    """Generate Python code for waveguide dispersion simulation."""
    return f'''"""Generated code for waveguide dispersion simulation.

This script reproduces the simulation that was run via the MCP server.
"""

import csv
import numpy as np
from matplotlib import pyplot as plt
from axiomatic_mcp.servers.tidy3d.tools.wg_dispersion import (
    compute_waveguide_dispersion,
    get_waveguide_for_mode_plot,
)

# Simulation parameters
core_material_family = "{kwargs.get('core_material_family', 'cSi')}"
core_material_model = "{kwargs.get('core_material_model', 'Palik_Lossless')}"
clad_material_family = "{kwargs.get('clad_material_family', 'SiO2')}"
clad_material_model = "{kwargs.get('clad_material_model', 'Palik_Lossless')}"
wg_width_um = {kwargs.get('wg_width_um', 0.5)}
wg_height_um = {kwargs.get('wg_height_um', 0.22)}
sidewall_angle_deg = {kwargs.get('sidewall_angle_deg', 0.0)}
num_modes = {kwargs.get('num_modes', 1)}
lam_start_um = {kwargs.get('lam_start_um', 1.26)}
lam_stop_um = {kwargs.get('lam_stop_um', 1.36)}
num_wavelength_points = {kwargs.get('num_wavelength_points', 11)}
enable_mode_plots = {kwargs.get('enable_mode_plots', False)}
mode_plot_wavelength_um = {kwargs.get('mode_plot_wavelength_um', 1.3)}
output_prefix = "{kwargs.get('output_prefix', 'wg_dispersion')}"

# Main simulation code
saved_files = []

# Compute dispersion
wls_um, neff_arr, ng_arr, strip = compute_waveguide_dispersion(
    core_material_family=core_material_family,
    core_material_model=core_material_model,
    clad_material_family=clad_material_family,
    clad_material_model=clad_material_model,
    wg_width_um=wg_width_um,
    wg_height_um=wg_height_um,
    sidewall_angle_deg=sidewall_angle_deg,
    lam_start_um=lam_start_um,
    lam_stop_um=lam_stop_um,
    num_wavelength_points=num_wavelength_points,
    num_modes=num_modes,
)

# Save CSV data
csv_path = f"{{output_prefix}}_dispersion.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if num_modes == 1:
        writer.writerow(["wavelength_um", "neff", "ng"])
        for lam, neff, ng in zip(wls_um.tolist(), neff_arr.tolist(), ng_arr.tolist()):
            writer.writerow([float(lam), float(neff), float(ng)])
    else:
        header = ["wavelength_um"]
        for i in range(num_modes):
            header.extend([f"neff_mode_{{i}}", f"ng_mode_{{i}}"])
        writer.writerow(header)
        
        for i, lam in enumerate(wls_um.tolist()):
            row = [float(lam)]
            for mode_idx in range(num_modes):
                row.extend([float(neff_arr[i, mode_idx]), float(ng_arr[i, mode_idx])])
            writer.writerow(row)
saved_files.append(csv_path)

# Create dispersion plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)

if num_modes == 1:
    ax1.plot(wls_um, neff_arr, '.-')
    ax2.plot(wls_um, ng_arr, '.-')
else:
    for mode_idx in range(num_modes):
        ax1.plot(wls_um, neff_arr[:, mode_idx], '.-', label=f'Mode {{mode_idx}}')
        ax2.plot(wls_um, ng_arr[:, mode_idx], '.-', label=f'Mode {{mode_idx}}')
    ax1.legend()
    ax2.legend()
    
ax1.set_xlabel('Wavelength [µm]')
ax1.set_ylabel('Effective Index')
ax1.set_title('Effective Index vs Wavelength')

ax2.set_xlabel('Wavelength [µm]')
ax2.set_ylabel('Group Index')
ax2.set_title('Group Index vs Wavelength')

plot_path = f"{{output_prefix}}_dispersion.png"
fig.savefig(plot_path, dpi=150)
plt.close(fig)
saved_files.append(plot_path)

# Mode plots
if enable_mode_plots:
    strip_plot = get_waveguide_for_mode_plot(
        core_material_family=core_material_family,
        core_material_model=core_material_model,
        clad_material_family=clad_material_family,
        clad_material_model=clad_material_model,
        wg_width_um=wg_width_um,
        wg_height_um=wg_height_um,
        sidewall_angle_deg=sidewall_angle_deg,
        wavelength_um=mode_plot_wavelength_um,
        num_modes=num_modes,
    )

    fig, axes = plt.subplots(1, num_modes + 1, figsize=(4 * (num_modes + 1), 4), constrained_layout=True)
    if num_modes == 1:
        axes = [axes[0], axes[1]]
    
    strip_plot.plot_eps(ax=axes[0], x=0)
    strip_plot.plot_grid(ax=axes[0], x=0)
    axes[0].set_title('Waveguide Structure')
    
    freqs = strip_plot.mode_solver.freqs
    for mode_idx in range(num_modes):
        strip_plot.plot_structures(x=0.0, ax=axes[mode_idx + 1])
        strip_plot.plot_field("Ey", mode_index=mode_idx, ax=axes[mode_idx + 1], 
                            f=freqs[0], val="abs")
        axes[mode_idx + 1].set_title(f'Mode {{mode_idx}} |Ey|')
    
    mode_plot_path = f"{{output_prefix}}_modes.png"
    fig.savefig(mode_plot_path, dpi=150)
    plt.close(fig)
    saved_files.append(mode_plot_path)

print(f"Simulation completed. Saved {{len(saved_files)}} files: {{saved_files}}")
'''


mcp = FastMCP(
    name="Axiomatic Tidy3D",
    instructions=(
        "This MCP server runs compact Tidy3D-based waveguide calculations: "
        "coupling vs wavelength/length for coupled waveguides, dispersion (neff/ng vs wavelength) "
        "for single waveguides, and optional mode plots. "
        "CSV results and PNG plots are saved under 'mcp_output'."
    ),
    version="0.0.1",
)


@mcp.tool(
    name="simulate_waveguide_coupler",
    description=(
        "Compute evanescent coupling for a pair of rectangular dielectric waveguides using Tidy3D. "
        "Supports coupling vs wavelength and/or vs length, with optional mode-field plots. "
        "Saves CSV/PNG files to 'mcp_output'."
    ),
    tags=["simulation", "photonic", "tidy3d", "waveguide", "coupler"],
)
async def simulate_waveguide_coupler(
    # Materials (see td.material_library)
    core_material_family: Annotated[str, "Core material family key in Tidy3D library (e.g., cSi, Si3N4)"] = "cSi",
    core_material_model: Annotated[str, "Core material model key (e.g., Palik_Lossless)"] = "Palik_Lossless",
    clad_material_family: Annotated[str, "Cladding material family key (e.g., SiO2)"] = "SiO2",
    clad_material_model: Annotated[str, "Cladding material model key (e.g., Palik_Lossless)"] = "Palik_Lossless",
    # Geometry (micrometers)
    wg_width1_um: Annotated[float, "Width of waveguide 1 in micrometers"] = 0.5,
    wg_width2_um: Annotated[float, "Width of waveguide 2 in micrometers"] = 0.5,
    wg_height_um: Annotated[float, "Core thickness in micrometers"] = 0.22,
    wg_gap_um: Annotated[float, "Gap between the two cores in micrometers"] = 0.2,
    coupler_length_um: Annotated[float, "Interaction length in micrometers"] = 50.0,
    sidewall_angle_deg: Annotated[float, "Sidewall angle in degrees (0 = vertical)"] = 0.0,
    polarization: Annotated[str, "Mode polarization filter: 'te' or 'tm'"] = "te",
    # Wavelength sweep (micrometers)
    enable_coupling_vs_wavelength: Annotated[bool, "Whether to compute coupling vs wavelength"] = True,
    lam_start_um: Annotated[float, "Start wavelength in micrometers"] = 1.26,
    lam_stop_um: Annotated[float, "Stop wavelength in micrometers"] = 1.36,
    num_wavelength_points: Annotated[int, "Number of wavelength points"] = 100,
    # Length sweep (micrometers)
    enable_coupling_vs_length: Annotated[bool, "Whether to compute coupling vs length"] = True,
    length_start_um: Annotated[float, "Start length in micrometers"] = 0.0,
    length_stop_um: Annotated[float, "Stop length in micrometers"] = 100.0,
    num_length_points: Annotated[int, "Number of length points"] = 21,
    length_wavelength_um: Annotated[float, "Wavelength (µm) for the length sweep"] = 1.31,
    # Mode plotting
    enable_mode_plots: Annotated[bool, "Whether to save mode field plots (Ey) for the two lowest TE/TM modes"] = False,
    mode_plot_wavelength_um: Annotated[float, "Wavelength (µm) for mode plots"] = 1.31,
    # Outputs
    output_prefix: Annotated[str, "Filename prefix for outputs (CSV/PNG)"] = "wg_coupler",
) -> ToolResult:
    try:
        import numpy as np
        from matplotlib import pyplot as plt

        out_dir = _ensure_output_dir()

        saved_files: list[str] = []

        # Generate and save Python code
        code_content = _generate_coupler_code(**locals())
        code_path = os.path.join(out_dir, f"{output_prefix}_coupler_simulation.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        saved_files.append(code_path)

        # Coupling vs wavelength
        if enable_coupling_vs_wavelength:
            wls_um, p_coupling_wl = compute_coupling_vs_wavelength(
                core_material_family=core_material_family,
                core_material_model=core_material_model,
                clad_material_family=clad_material_family,
                clad_material_model=clad_material_model,
                wg_width1_um=wg_width1_um,
                wg_width2_um=wg_width2_um,
                wg_height_um=wg_height_um,
                wg_gap_um=wg_gap_um,
                coupler_length_um=coupler_length_um,
                sidewall_angle_deg=sidewall_angle_deg,
                polarization=polarization,
                lam_start_um=lam_start_um,
                lam_stop_um=lam_stop_um,
                num_wavelength_points=num_wavelength_points,
            )

            csv_path_wl = os.path.join(out_dir, f"{output_prefix}_coupling_vs_wavelength.csv")
            with open(csv_path_wl, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["wavelength_um", "power_coupling"])
                for lam, pc in zip(wls_um.tolist(), p_coupling_wl.tolist()):
                    writer.writerow([float(lam), float(pc)])
            saved_files.append(csv_path_wl)

            # Save plot
            fig, ax = plt.subplots(figsize=(5, 3.2), constrained_layout=True)
            ax.plot(wls_um, p_coupling_wl, ".-")
            ax.set_xlabel("Wavelength [µm]")
            ax.set_ylabel("Power coupling [a.u.]")
            ax.set_title("Coupling vs wavelength")
            plot_path_wl = os.path.join(out_dir, f"{output_prefix}_coupling_vs_wavelength.png")
            fig.savefig(plot_path_wl, dpi=150)
            plt.close(fig)
            saved_files.append(plot_path_wl)

        # Coupling vs length
        if enable_coupling_vs_length:
            lengths_um, p_coupling_len = compute_coupling_vs_length(
                core_material_family=core_material_family,
                core_material_model=core_material_model,
                clad_material_family=clad_material_family,
                clad_material_model=clad_material_model,
                wg_width1_um=wg_width1_um,
                wg_width2_um=wg_width2_um,
                wg_height_um=wg_height_um,
                wg_gap_um=wg_gap_um,
                sidewall_angle_deg=sidewall_angle_deg,
                polarization=polarization,
                length_start_um=length_start_um,
                length_stop_um=length_stop_um,
                num_length_points=num_length_points,
                wavelength_um=length_wavelength_um,
            )

            csv_path_len = os.path.join(out_dir, f"{output_prefix}_coupling_vs_length.csv")
            with open(csv_path_len, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["length_um", "power_coupling"])
                for L, pc in zip(lengths_um.tolist(), p_coupling_len.tolist()):
                    writer.writerow([float(L), float(pc)])
            saved_files.append(csv_path_len)

            # Save plot
            fig, ax = plt.subplots(figsize=(5, 3.2), constrained_layout=True)
            ax.plot(lengths_um, p_coupling_len, ".-")
            ax.set_xlabel("Coupler length [µm]")
            ax.set_ylabel("Power coupling [a.u.]")
            ax.set_title("Coupling vs length")
            plot_path_len = os.path.join(out_dir, f"{output_prefix}_coupling_vs_length.png")
            fig.savefig(plot_path_len, dpi=150)
            plt.close(fig)
            saved_files.append(plot_path_len)

        # Mode plots
        if enable_mode_plots:
            coupled = get_coupled_for_mode_plot(
                core_material_family=core_material_family,
                core_material_model=core_material_model,
                clad_material_family=clad_material_family,
                clad_material_model=clad_material_model,
                wg_width1_um=wg_width1_um,
                wg_width2_um=wg_width2_um,
                wg_height_um=wg_height_um,
                wg_gap_um=wg_gap_um,
                sidewall_angle_deg=sidewall_angle_deg,
                polarization=polarization,
                wavelength_um=mode_plot_wavelength_um,
            )

            from matplotlib import pyplot as pyplot

            fig, ax = pyplot.subplots(1, 2, figsize=(8, 4), tight_layout=True)
            coupled.plot_field("Ey", mode_index=0, ax=ax[0])
            ax[0].set_title("Ey mode 0")
            coupled.plot_field("Ey", mode_index=1, ax=ax[1])
            ax[1].set_title("Ey mode 1")
            mode_plot_path = os.path.join(out_dir, f"{output_prefix}_modes_Ey.png")
            fig.savefig(mode_plot_path, dpi=150)
            pyplot.close(fig)
            saved_files.append(mode_plot_path)

        summary_lines = [
            "Waveguide coupler simulation completed.",
            f"Saved {len(saved_files)} file(s) to: {out_dir}",
        ]
        return ToolResult(
            content=[TextContent(type="text", text="\n".join(summary_lines))],
            structured_content={
                "output_dir": out_dir,
                "saved_files": saved_files,
            },
        )

    except Exception as e:  # noqa: BLE001
        return ToolResult(content=[TextContent(type="text", text=f"Simulation failed: {e!s}")])


@mcp.tool(
    name="simulate_waveguide_dispersion",
    description=(
        "Compute effective index and group index vs wavelength for a rectangular dielectric waveguide using Tidy3D. "
        "Supports optional mode-field plots. "
        "Saves CSV/PNG files to 'mcp_output'."
    ),
    tags=["simulation", "photonic", "tidy3d", "waveguide", "dispersion"],
)
async def simulate_waveguide_dispersion(
    # Materials (see td.material_library)
    core_material_family: Annotated[str, "Core material family key in Tidy3D library (e.g., cSi, Si3N4)"] = "cSi",
    core_material_model: Annotated[str, "Core material model key (e.g., Palik_Lossless)"] = "Palik_Lossless",
    clad_material_family: Annotated[str, "Cladding material family key (e.g., SiO2)"] = "SiO2",
    clad_material_model: Annotated[str, "Cladding material model key (e.g., Palik_Lossless)"] = "Palik_Lossless",
    # Geometry (micrometers)
    wg_width_um: Annotated[float, "Waveguide width in micrometers"] = 0.5,
    wg_height_um: Annotated[float, "Waveguide thickness in micrometers"] = 0.22,
    sidewall_angle_deg: Annotated[float, "Sidewall angle in degrees (0 = vertical)"] = 0.0,
    num_modes: Annotated[int, "Number of modes to compute"] = 1,
    # Wavelength sweep (micrometers)
    lam_start_um: Annotated[float, "Start wavelength in micrometers"] = 1.26,
    lam_stop_um: Annotated[float, "Stop wavelength in micrometers"] = 1.36,
    num_wavelength_points: Annotated[int, "Number of wavelength points"] = 11,
    # Mode plotting
    enable_mode_plots: Annotated[bool, "Whether to save mode field plots (Ey) and waveguide structure"] = False,
    mode_plot_wavelength_um: Annotated[float, "Wavelength (µm) for mode plots"] = 1.31,
    # Outputs
    output_prefix: Annotated[str, "Filename prefix for outputs (CSV/PNG)"] = "wg_dispersion",
) -> ToolResult:
    try:
        import numpy as np
        from matplotlib import pyplot as plt

        out_dir = _ensure_output_dir()

        saved_files: list[str] = []

        # Generate and save Python code
        code_content = _generate_dispersion_code(**locals())
        code_path = os.path.join(out_dir, f"{output_prefix}_dispersion_simulation.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        saved_files.append(code_path)

        # Compute dispersion
        wls_um, neff_arr, ng_arr, strip = compute_waveguide_dispersion(
            core_material_family=core_material_family,
            core_material_model=core_material_model,
            clad_material_family=clad_material_family,
            clad_material_model=clad_material_model,
            wg_width_um=wg_width_um,
            wg_height_um=wg_height_um,
            sidewall_angle_deg=sidewall_angle_deg,
            lam_start_um=lam_start_um,
            lam_stop_um=lam_stop_um,
            num_wavelength_points=num_wavelength_points,
            num_modes=num_modes,
        )

        # Save CSV data
        csv_path = os.path.join(out_dir, f"{output_prefix}_dispersion.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if num_modes == 1:
                writer.writerow(["wavelength_um", "neff", "ng"])
                for lam, neff, ng in zip(wls_um.tolist(), neff_arr.tolist(), ng_arr.tolist()):
                    writer.writerow([float(lam), float(neff), float(ng)])
            else:
                # Multi-mode case: create columns for each mode
                header = ["wavelength_um"]
                for i in range(num_modes):
                    header.extend([f"neff_mode_{i}", f"ng_mode_{i}"])
                writer.writerow(header)
                
                for i, lam in enumerate(wls_um.tolist()):
                    row = [float(lam)]
                    for mode_idx in range(num_modes):
                        row.extend([float(neff_arr[i, mode_idx]), float(ng_arr[i, mode_idx])])
                    writer.writerow(row)
        saved_files.append(csv_path)

        # Create dispersion plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
        
        if num_modes == 1:
            ax1.plot(wls_um, neff_arr, '.-')
            ax2.plot(wls_um, ng_arr, '.-')
        else:
            for mode_idx in range(num_modes):
                ax1.plot(wls_um, neff_arr[:, mode_idx], '.-', label=f'Mode {mode_idx}')
                ax2.plot(wls_um, ng_arr[:, mode_idx], '.-', label=f'Mode {mode_idx}')
            ax1.legend()
            ax2.legend()
            
        ax1.set_xlabel('Wavelength [µm]')
        ax1.set_ylabel('Effective Index')
        ax1.set_title('Effective Index vs Wavelength')
        
        ax2.set_xlabel('Wavelength [µm]')
        ax2.set_ylabel('Group Index')
        ax2.set_title('Group Index vs Wavelength')
        
        plot_path = os.path.join(out_dir, f"{output_prefix}_dispersion.png")
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)
        saved_files.append(plot_path)

        # Mode plots
        if enable_mode_plots:
            # Get waveguide for mode plotting
            strip_plot = get_waveguide_for_mode_plot(
                core_material_family=core_material_family,
                core_material_model=core_material_model,
                clad_material_family=clad_material_family,
                clad_material_model=clad_material_model,
                wg_width_um=wg_width_um,
                wg_height_um=wg_height_um,
                sidewall_angle_deg=sidewall_angle_deg,
                wavelength_um=mode_plot_wavelength_um,
                num_modes=num_modes,
            )

            # Create structure and mode plots
            fig, axes = plt.subplots(1, num_modes + 1, figsize=(4 * (num_modes + 1), 4), constrained_layout=True)
            if num_modes == 1:
                axes = [axes[0], axes[1]]  # Ensure axes is always a list
            
            # Structure plot
            strip_plot.plot_eps(ax=axes[0], x=0)
            strip_plot.plot_grid(ax=axes[0], x=0)
            axes[0].set_title('Waveguide Structure')
            
            # Mode field plots
            freqs = strip_plot.mode_solver.freqs
            for mode_idx in range(num_modes):
                strip_plot.plot_structures(x=0.0, ax=axes[mode_idx + 1])
                strip_plot.plot_field("Ey", mode_index=mode_idx, ax=axes[mode_idx + 1], 
                                    f=freqs[0], val="abs")
                axes[mode_idx + 1].set_title(f'Mode {mode_idx} |Ey|')
            
            mode_plot_path = os.path.join(out_dir, f"{output_prefix}_modes.png")
            fig.savefig(mode_plot_path, dpi=150)
            plt.close(fig)
            saved_files.append(mode_plot_path)

        summary_lines = [
            "Waveguide dispersion simulation completed.",
            f"Saved {len(saved_files)} file(s) to: {out_dir}",
        ]
        return ToolResult(
            content=[TextContent(type="text", text="\n".join(summary_lines))],
            structured_content={
                "output_dir": out_dir,
                "saved_files": saved_files,
                "wavelengths_um": wls_um.tolist(),
                "neff": neff_arr.tolist() if num_modes == 1 else neff_arr.tolist(),
                "ng": ng_arr.tolist() if num_modes == 1 else ng_arr.tolist(),
            },
        )

    except Exception as e:  # noqa: BLE001
        return ToolResult(content=[TextContent(type="text", text=f"Dispersion simulation failed: {e!s}")])


def main() -> None:
    """Main entry point for the Tidy3D MCP server."""
    mcp.run()


