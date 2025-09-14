"""Waveguide dispersion utilities using Tidy3D.

Provides parameterized functions to compute effective index (neff) and group index (ng)
for rectangular dielectric waveguides as a function of wavelength. Based on the 
wg_dispersion.ipynb notebook functionality.
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


def make_rect_dielectric_waveguide(
    wavelengths_um,
    *,
    wg_width_um: float,
    wg_height_um: float,
    core_medium,
    clad_medium,
    sidewall_angle_deg: float,
    num_modes: int = 1,
):
    """Create a Tidy3D rectangular dielectric waveguide object."""
    td, waveguide = _get_td_and_waveguide()
    return waveguide.RectangularDielectric(
        wavelength=wavelengths_um,
        core_width=wg_width_um,
        core_thickness=wg_height_um,
        core_medium=core_medium,
        clad_medium=clad_medium,
        sidewall_angle=sidewall_angle_deg,
        mode_spec=td.ModeSpec(num_modes=num_modes, group_index_step=True),
    )


def compute_waveguide_dispersion(
    *,
    core_material_family: str,
    core_material_model: str,
    clad_material_family: str,
    clad_material_model: str,
    wg_width_um: float,
    wg_height_um: float,
    sidewall_angle_deg: float,
    lam_start_um: float,
    lam_stop_um: float,
    num_wavelength_points: int,
    num_modes: int = 1,
):
    """Compute effective index and group index as a function of wavelength.

    Returns:
        tuple: (wavelengths_um: np.ndarray, neff: np.ndarray, ng: np.ndarray, strip_object)
    """
    core_medium = resolve_material(core_material_family, core_material_model)
    clad_medium = resolve_material(clad_material_family, clad_material_model)

    wavelengths_um = np.linspace(lam_start_um, lam_stop_um, num_wavelength_points)
    neff_arr = np.zeros((num_wavelength_points, num_modes))
    ng_arr = np.zeros((num_wavelength_points, num_modes))
    
    # Calculate modes for each wavelength individually using a for loop
    strip_objects = []
    for i, wavelength_um in enumerate(wavelengths_um):
        strip = make_rect_dielectric_waveguide(
            wavelength_um,
            wg_width_um=wg_width_um,
            wg_height_um=wg_height_um,
            core_medium=core_medium,
            clad_medium=clad_medium,
            sidewall_angle_deg=sidewall_angle_deg,
            num_modes=num_modes,
        )
        
        # Extract effective index and group index for this wavelength
        neff_arr[i, :] = np.squeeze(strip.n_eff.values)
        ng_arr[i, :] = np.squeeze(strip.n_group.values)
        strip_objects.append(strip)
    
    # Squeeze arrays if only one mode
    if num_modes == 1:
        neff_arr = np.squeeze(neff_arr)
        ng_arr = np.squeeze(ng_arr)
    
    return wavelengths_um, neff_arr, ng_arr, strip_objects[-1]


def get_waveguide_for_mode_plot(
    *,
    core_material_family: str,
    core_material_model: str,
    clad_material_family: str,
    clad_material_model: str,
    wg_width_um: float,
    wg_height_um: float,
    sidewall_angle_deg: float,
    wavelength_um: float,
    num_modes: int = 1,
):
    """Create and return a waveguide object for mode plotting at one wavelength."""
    core_medium = resolve_material(core_material_family, core_material_model)
    clad_medium = resolve_material(clad_material_family, clad_material_model)

    return make_rect_dielectric_waveguide(
        wavelength_um,
        wg_width_um=wg_width_um,
        wg_height_um=wg_height_um,
        core_medium=core_medium,
        clad_medium=clad_medium,
        sidewall_angle_deg=sidewall_angle_deg,
        num_modes=num_modes,
    )