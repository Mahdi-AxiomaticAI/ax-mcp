"""Waveguide coupler utilities using Tidy3D.

Provides parameterized functions to compute power coupling between two parallel
rectangular dielectric waveguides and to construct mode solver objects for
field visualization. Mirrors the style used by DTS DT modules (computation-only;
file I/O done in the server).
"""

from __future__ import annotations

import numpy as np


def _get_td_and_waveguide():
    """Import-heavy modules are loaded lazily to allow server registration without deps."""
    import tidy3d as td  # noqa: WPS433
    from tidy3d.plugins import waveguide  # noqa: WPS433

    return td, waveguide


def resolve_material(family: str, model: str):
    """Resolve a Tidy3D material from the library.

    Args:
        family: Material family key (e.g., "cSi", "SiO2", "Si3N4").
        model: Model key within the family (e.g., "Palik_Lossless").

    Returns:
        Tidy3D medium object.
    """
    td, _ = _get_td_and_waveguide()
    try:
        return td.material_library[family][model]
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Material not found: {family}/{model}") from exc


def make_coupled_rect_dielectric(
    wavelengths_um,
    *,
    wg_width1_um: float,
    wg_width2_um: float,
    wg_height_um: float,
    wg_gap_um: float,
    core_medium,
    clad_medium,
    sidewall_angle_deg: float,
    polarization: str,
):
    """Create a Tidy3D rectangular dielectric coupled waveguide object."""
    td, waveguide = _get_td_and_waveguide()
    return waveguide.RectangularDielectric(
        wavelength=wavelengths_um,
        core_width=(wg_width1_um, wg_width2_um),
        core_thickness=wg_height_um,
        core_medium=core_medium,
        clad_medium=clad_medium,
        gap=wg_gap_um,
        sidewall_angle=sidewall_angle_deg,
        mode_spec=td.ModeSpec(num_modes=2, filter_pol=polarization),
    )


def compute_coupling_vs_wavelength(
    *,
    core_material_family: str,
    core_material_model: str,
    clad_material_family: str,
    clad_material_model: str,
    wg_width1_um: float,
    wg_width2_um: float,
    wg_height_um: float,
    wg_gap_um: float,
    coupler_length_um: float,
    sidewall_angle_deg: float,
    polarization: str,
    lam_start_um: float,
    lam_stop_um: float,
    num_wavelength_points: int,
):
    """Compute power coupling as a function of wavelength.

    Returns:
        (wavelengths_um: np.ndarray, power_coupling: np.ndarray)
    """
    core_medium = resolve_material(core_material_family, core_material_model)
    clad_medium = resolve_material(clad_material_family, clad_material_model)

    wavelengths_um = np.linspace(lam_start_um, lam_stop_um, num_wavelength_points)
    coupled = make_coupled_rect_dielectric(
        wavelengths_um,
        wg_width1_um=wg_width1_um,
        wg_width2_um=wg_width2_um,
        wg_height_um=wg_height_um,
        wg_gap_um=wg_gap_um,
        core_medium=core_medium,
        clad_medium=clad_medium,
        sidewall_angle_deg=sidewall_angle_deg,
        polarization=polarization,
    )

    n1 = coupled.n_eff.values[:, 0]
    n2 = coupled.n_eff.values[:, 1]
    p_coupling = np.sin(np.pi * coupler_length_um * (n1 - n2) / wavelengths_um) ** 2
    return wavelengths_um, p_coupling


def compute_coupling_vs_length(
    *,
    core_material_family: str,
    core_material_model: str,
    clad_material_family: str,
    clad_material_model: str,
    wg_width1_um: float,
    wg_width2_um: float,
    wg_height_um: float,
    wg_gap_um: float,
    sidewall_angle_deg: float,
    polarization: str,
    length_start_um: float,
    length_stop_um: float,
    num_length_points: int,
    wavelength_um: float,
):
    """Compute power coupling as a function of coupler length for a single wavelength.

    Returns:
        (lengths_um: np.ndarray, power_coupling: np.ndarray)
    """
    core_medium = resolve_material(core_material_family, core_material_model)
    clad_medium = resolve_material(clad_material_family, clad_material_model)

    lengths_um = np.linspace(length_start_um, length_stop_um, num_length_points)
    coupled = make_coupled_rect_dielectric(
        wavelength_um,
        wg_width1_um=wg_width1_um,
        wg_width2_um=wg_width2_um,
        wg_height_um=wg_height_um,
        wg_gap_um=wg_gap_um,
        core_medium=core_medium,
        clad_medium=clad_medium,
        sidewall_angle_deg=sidewall_angle_deg,
        polarization=polarization,
    )
    n1 = float(coupled.n_eff.values[0, 0])
    n2 = float(coupled.n_eff.values[0, 1])
    p_coupling = np.sin(np.pi * lengths_um * (n1 - n2) / wavelength_um) ** 2
    return lengths_um, p_coupling


def get_coupled_for_mode_plot(
    *,
    core_material_family: str,
    core_material_model: str,
    clad_material_family: str,
    clad_material_model: str,
    wg_width1_um: float,
    wg_width2_um: float,
    wg_height_um: float,
    wg_gap_um: float,
    sidewall_angle_deg: float,
    polarization: str,
    wavelength_um: float,
):
    """Create and return a coupled waveguide object for mode plotting at one wavelength."""
    core_medium = resolve_material(core_material_family, core_material_model)
    clad_medium = resolve_material(clad_material_family, clad_material_model)

    return make_coupled_rect_dielectric(
        wavelength_um,
        wg_width1_um=wg_width1_um,
        wg_width2_um=wg_width2_um,
        wg_height_um=wg_height_um,
        wg_gap_um=wg_gap_um,
        core_medium=core_medium,
        clad_medium=clad_medium,
        sidewall_angle_deg=sidewall_angle_deg,
        polarization=polarization,
    )


