"""Axiomatic DTS MCP server.

This server exposes tools to run simulations for photonic digital twin models
located in `src/axiomatic_dts/DT/`, and saves transmission results as CSV files
under the working directory's `mcp_output` folder.
"""

from __future__ import annotations

import csv
import os
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from .DT.multimode_ring_jax import (
    MultiModeRingParams,
    ModeParams,
    compute_multimode_response,
)
from .DT.mzi_filter_jax import evaluate_mzi_filter_jax


def _ensure_output_dir() -> str:
    """Ensure `mcp_output` exists in the current working directory and return its path."""
    out_dir = os.path.join(os.getcwd(), "mcp_output")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


mcp = FastMCP(
    name="Axiomatic DTS",
    instructions=(
        "This MCP server simulates photonic digital twin models (multimode ring resonator, "
        "MZI filter) and saves transmission spectra as CSV in the 'mcp_output' folder.\n\n"
        "TOOLS:\n"
        "- simulate_multimode_ring: compute wavelength vs transmission (linear and dB).\n"
        "- simulate_mzi_filter: compute 8-channel CWDM filter transmissions.\n"
        "- list_available_models: discover available models and parameters.\n\n"
        "USAGE NOTES:\n"
        "- Wavelength sweep is specified in nanometers via lam_start_nm/lam_stop_nm/num_points.\n"
        "- Outputs are saved as CSV with a header. Provide 'output_filename' to customize.\n"
        "- For ring filenames, consider your naming convention (e.g., include r<radius> and g<gap>)."
    ),
    version="0.0.1",
)


@mcp.tool(
    name="simulate_multimode_ring",
    description=(
        "Simulate a multimode ring resonator (up to 3 modes) with optional coherence, grating, "
        "and background fields. Saves CSV with columns: wavelength_nm, transmission_linear, transmission_dB."
    ),
    tags=["simulation", "photonic", "ring", "jax"],
)
async def simulate_multimode_ring(
    lam_start_nm: Annotated[float, "Starting wavelength in nm" ] = 1540.0,
    lam_stop_nm: Annotated[float, "Ending wavelength in nm"] = 1560.0,
    num_points: Annotated[int, "Number of points in the sweep"] = 2001,
    ring_radius_um: Annotated[float, "Ring radius in micrometers"] = 10000.0,
    # Modes
    enable_mode2: Annotated[bool, "Enable second mode"] = False,
    enable_mode3: Annotated[bool, "Enable third mode"] = False,
    mode1_neff: Annotated[float, "Mode 1 effective index"] = 2.40,
    mode1_alpha_dB_per_cm: Annotated[float, "Mode 1 loss (dB/cm)"] = 3.0,
    mode1_kappa: Annotated[float, "Mode 1 coupling coefficient (0..1)"] = 0.20,
    mode1_weight: Annotated[float, "Mode 1 relative field weight"] = 1.0,
    mode2_neff: Annotated[float, "Mode 2 effective index"] = 2.45,
    mode2_alpha_dB_per_cm: Annotated[float, "Mode 2 loss (dB/cm)"] = 3.0,
    mode2_kappa: Annotated[float, "Mode 2 coupling coefficient (0..1)"] = 0.15,
    mode2_weight: Annotated[float, "Mode 2 relative field weight"] = 0.6,
    mode3_neff: Annotated[float, "Mode 3 effective index"] = 2.50,
    mode3_alpha_dB_per_cm: Annotated[float, "Mode 3 loss (dB/cm)"] = 3.0,
    mode3_kappa: Annotated[float, "Mode 3 coupling coefficient (0..1)"] = 0.10,
    mode3_weight: Annotated[float, "Mode 3 relative field weight"] = 0.4,
    # Background/external paths
    r_facet: Annotated[float, "Facet reflection amplitude"] = 0.10,
    L_wg_um: Annotated[float, "Background waveguide length (um)"] = 200.0,
    enable_short_path: Annotated[bool, "Enable short background path"] = True,
    r_short: Annotated[float, "Short path reflection amplitude"] = 0.05,
    L_short_um: Annotated[float, "Short path length (um)"] = 50.0,
    enable_substrate: Annotated[bool, "Enable substrate path"] = False,
    r_sub: Annotated[float, "Substrate reflection amplitude"] = 0.02,
    L_sub_um: Annotated[float, "Substrate path length (um)"] = 300.0,
    # Effects and envelopes
    inter_mode_coherence: Annotated[float, "Inter-mode coherence (0=incoherent, 1=coherent)"] = 1.0,
    enable_grating: Annotated[bool, "Enable grating envelope"] = False,
    grating_center_nm: Annotated[float, "Grating center wavelength (nm)"] = 1550.0,
    grating_fwhm_nm: Annotated[float, "Grating FWHM (nm)"] = 20.0,
    grating_peak_loss_dB: Annotated[float, "Grating peak loss (dB)"] = 3.0,
    enable_finite_linewidth: Annotated[bool, "Enable source linewidth smoothing"] = False,
    source_linewidth_fwhm_nm: Annotated[float, "Source linewidth FWHM (nm)"] = 0.01,
    enable_pol_drift: Annotated[bool, "Enable polarization drift modulation"] = False,
    pol_drift_ampl: Annotated[float, "Polarization drift amplitude (relative)"] = 0.1,
    enable_mech_drift: Annotated[bool, "Enable mechanical drift phase"] = False,
    mech_drift_amp: Annotated[float, "Mechanical drift phase amplitude (rad)"] = 0.1,
    mech_drift_period_nm: Annotated[float, "Mechanical drift period (nm)"] = 200.0,
    enable_random_loss: Annotated[bool, "Enable smooth random loss"] = False,
    random_loss_scale: Annotated[float, "Random loss scale (relative)"] = 0.05,
    # Scalar adjustments
    insertion_loss_dB: Annotated[float, "Insertion loss (dB)"] = 0.0,
    offset_level: Annotated[float, "DC offset level (linear)"] = 0.0,
    random_phase_seed: Annotated[int, "Random phase seed for modes"] = 0,
    # Output
    output_filename: Annotated[str, "CSV filename (saved to mcp_output)"] = "ring_transmission.csv",
) -> ToolResult:
    """Run the multimode ring simulation and save results as CSV."""
    try:
        params = MultiModeRingParams(
            lam_start_nm=lam_start_nm,
            lam_stop_nm=lam_stop_nm,
            num_points=num_points,
            ring_radius_um=ring_radius_um,
            enable_mode2=enable_mode2,
            enable_mode3=enable_mode3,
            mode1=ModeParams(n_eff=mode1_neff, alpha_dB_per_cm=mode1_alpha_dB_per_cm, kappa=mode1_kappa, weight=mode1_weight),
            mode2=ModeParams(n_eff=mode2_neff, alpha_dB_per_cm=mode2_alpha_dB_per_cm, kappa=mode2_kappa, weight=mode2_weight),
            mode3=ModeParams(n_eff=mode3_neff, alpha_dB_per_cm=mode3_alpha_dB_per_cm, kappa=mode3_kappa, weight=mode3_weight),
            r_facet=r_facet,
            L_wg_um=L_wg_um,
            enable_short_path=enable_short_path,
            r_short=r_short,
            L_short_um=L_short_um,
            enable_substrate=enable_substrate,
            r_sub=r_sub,
            L_sub_um=L_sub_um,
            inter_mode_coherence=inter_mode_coherence,
            enable_grating=enable_grating,
            grating_center_nm=grating_center_nm,
            grating_fwhm_nm=grating_fwhm_nm,
            grating_peak_loss_dB=grating_peak_loss_dB,
            enable_finite_linewidth=enable_finite_linewidth,
            source_linewidth_fwhm_nm=source_linewidth_fwhm_nm,
            enable_pol_drift=enable_pol_drift,
            pol_drift_ampl=pol_drift_ampl,
            enable_mech_drift=enable_mech_drift,
            mech_drift_amp=mech_drift_amp,
            mech_drift_period_nm=mech_drift_period_nm,
            enable_random_loss=enable_random_loss,
            random_loss_scale=random_loss_scale,
            insertion_loss_dB=insertion_loss_dB,
            offset_level=offset_level,
            random_phase_seed=random_phase_seed,
        )

        wl_nm, I_linear, I_dB = compute_multimode_response(params)

        out_dir = _ensure_output_dir()
        out_path = os.path.join(out_dir, output_filename)

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["wavelength_nm", "transmission_linear", "transmission_dB"])
            for w, lin, db in zip(wl_nm.tolist(), I_linear.tolist(), I_dB.tolist()):
                writer.writerow([float(w), float(lin), float(db)])

        summary = (
            f"Multimode ring simulation completed. Saved CSV to: {out_path}\n"
            f"Points: {len(wl_nm.tolist())}; Wavelength range: {float(wl_nm[0]):.3f}–{float(wl_nm[-1]):.3f} nm"
        )
        return ToolResult(
            content=[TextContent(type="text", text=summary)],
            structured_content={"output_path": out_path},
        )

    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Simulation failed: {e!s}")])


@mcp.tool(
    name="simulate_mzi_filter",
    description=(
        "Simulate an 8-channel CWDM MZI filter and save CSV with columns: "
        "wavelength_nm, λ1, λ2, λ3, λ4, λ5, λ6, λ7, λ8."
    ),
    tags=["simulation", "photonic", "mzi", "filter", "jax"],
)
async def simulate_mzi_filter(
    lam_start_nm: Annotated[float, "Starting wavelength in nm"] = 1270.0,
    lam_stop_nm: Annotated[float, "Ending wavelength in nm"] = 1310.0,
    num_points: Annotated[int, "Number of points in the sweep"] = 4001,
    # Central wavelength and channel spacing (meters)
    lambda0: Annotated[float, "Central wavelength (m)"] = 1290e-9,
    delta_lambda: Annotated[float, "Channel spacing (m)"] = 4.4e-9,
    # Dispersion coefficients
    n0_1: Annotated[float, "Stage 1 n0"] = 2.39,
    n1_1: Annotated[float, "Stage 1 n1"] = -1.5e7,
    n2_1: Annotated[float, "Stage 1 n2"] = 1.2e13,
    n0_2: Annotated[float, "Stage 2 n0"] = 2.39,
    n1_2: Annotated[float, "Stage 2 n1"] = -1.5e7,
    n2_2: Annotated[float, "Stage 2 n2"] = 1.2e13,
    n0_3: Annotated[float, "Stage 3 n0"] = 2.39,
    n1_3: Annotated[float, "Stage 3 n1"] = -1.5e7,
    n2_3: Annotated[float, "Stage 3 n2"] = 1.2e13,
    # Coupling coefficients and optional slopes
    kappa_05: Annotated[float, "50% coupler nominal kappa"] = 0.5,
    kappa_05_slope: Annotated[float, "Slope for kappa_05 vs wavelength"] = 0.0,
    kappa_029: Annotated[float, "29% coupler nominal kappa"] = 0.29,
    kappa_029_slope: Annotated[float, "Slope for kappa_029 vs wavelength"] = 0.0,
    kappa_008: Annotated[float, "8% coupler nominal kappa"] = 0.08,
    kappa_008_slope: Annotated[float, "Slope for kappa_008 vs wavelength"] = 0.0,
    kappa_02: Annotated[float, "20% coupler nominal kappa"] = 0.2,
    kappa_02_slope: Annotated[float, "Slope for kappa_02 vs wavelength"] = 0.0,
    kappa_004: Annotated[float, "4% coupler nominal kappa"] = 0.04,
    kappa_004_slope: Annotated[float, "Slope for kappa_004 vs wavelength"] = 0.0,
    # Output
    output_filename: Annotated[str, "CSV filename (saved to mcp_output)"] = "mzi_transmission.csv",
) -> ToolResult:
    """Run the MZI filter simulation and save results as CSV."""
    try:
        import jax.numpy as jnp

        wl_nm = jnp.linspace(lam_start_nm, lam_stop_nm, num_points)
        wl_m = wl_nm * 1e-9

        channels = evaluate_mzi_filter_jax(
            wl_m,
            lambda0=lambda0,
            delta_lambda=delta_lambda,
            n0_1=n0_1, n1_1=n1_1, n2_1=n2_1,
            n0_2=n0_2, n1_2=n1_2, n2_2=n2_2,
            n0_3=n0_3, n1_3=n1_3, n2_3=n2_3,
            kappa_05=kappa_05, kappa_05_slope=kappa_05_slope,
            kappa_029=kappa_029, kappa_029_slope=kappa_029_slope,
            kappa_008=kappa_008, kappa_008_slope=kappa_008_slope,
            kappa_02=kappa_02, kappa_02_slope=kappa_02_slope,
            kappa_004=kappa_004, kappa_004_slope=kappa_004_slope,
        )

        # Enforce consistent channel order
        channel_keys = ["λ1", "λ2", "λ3", "λ4", "λ5", "λ6", "λ7", "λ8"]
        out_dir = _ensure_output_dir()
        out_path = os.path.join(out_dir, output_filename)

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["wavelength_nm"] + channel_keys)
            # Convert to lists once for efficiency
            wl_list = wl_nm.tolist()
            chan_lists = [channels[k].tolist() for k in channel_keys]
            for idx in range(len(wl_list)):
                row = [float(wl_list[idx])] + [float(chan_lists[cidx][idx]) for cidx in range(len(channel_keys))]
                writer.writerow(row)

        summary = (
            f"MZI filter simulation completed. Saved CSV to: {out_path}\n"
            f"Points: {len(wl_nm.tolist())}; Wavelength range: {float(wl_nm[0]):.3f}–{float(wl_nm[-1]):.3f} nm"
        )
        return ToolResult(
            content=[TextContent(type="text", text=summary)],
            structured_content={"output_path": out_path},
        )

    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Simulation failed: {e!s}")])


@mcp.tool(
    name="list_available_models",
    description="List available photonic DT models with brief descriptions and key parameters.",
    tags=["discovery", "models", "help"],
)
async def list_available_models() -> ToolResult:
    models = [
        {
            "name": "multimode_ring",
            "description": "All-pass ring with up to 3 modes; coherence, grating, and background fields.",
            "key_parameters": [
                "lam_start_nm", "lam_stop_nm", "num_points", "ring_radius_um",
                "mode*_neff", "mode*_alpha_dB_per_cm", "mode*_kappa", "mode*_weight",
                "inter_mode_coherence", "enable_grating",
            ],
            "output": "wavelength_nm, transmission_linear, transmission_dB",
        },
        {
            "name": "mzi_filter",
            "description": "3-stage cascaded MZI CWDM demultiplexer; 8 output channels.",
            "key_parameters": [
                "lam_start_nm", "lam_stop_nm", "num_points", "lambda0", "delta_lambda",
                "n*_*, kappa_*, *_slope",
            ],
            "output": "wavelength_nm, λ1..λ8",
        },
    ]

    text_lines = ["Available models:"]
    for m in models:
        text_lines.append(f"- {m['name']}: {m['description']}")
    text = "\n".join(text_lines)

    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content={"models": models},
    )


def main() -> None:
    """Main entry point for the Axiomatic DTS MCP server."""
    mcp.run()


