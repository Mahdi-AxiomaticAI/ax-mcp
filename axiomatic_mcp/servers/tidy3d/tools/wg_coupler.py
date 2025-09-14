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


def get_powercoupling(
    wavelengths,
    *,
    wg_widths: tuple[float, float] = (0.5, 0.5),
    wg_height: float = 0.22,
    wg_gap: float = 0.2,
    coupler_length: float = 50.0,
    wg_medium,
    cladding_medium,
    polarization: str = 'te',
):
    """Calculate power coupling between 2 waveguides - following notebook approach.

    Args:
        wavelengths: wavelengths [um] - can be single value or array
        wg_widths: waveguide widths as a tuple [um]
        wg_height: waveguide thickness [um]
        wg_gap: gap between the coupling waveguides [um]
        coupler_length: Length of the coupling between the wgs [um]
        wg_medium: core material
        cladding_medium: cladding material
        polarization: 'te' or 'tm'

    Returns:
        p_coupling: power coupling values (same shape as wavelengths)
        coupled: waveguide object for mode analysis
    """
    td, waveguide = _get_td_and_waveguide()

    # Ensure wavelengths is a list/array
    if np.isscalar(wavelengths):
        wavelengths = [wavelengths]

    coupled = waveguide.RectangularDielectric(
        wavelength=wavelengths,
        core_width=wg_widths,
        core_thickness=wg_height,
        core_medium=wg_medium,
        clad_medium=cladding_medium,
        gap=wg_gap,
        sidewall_angle=0.0,
        mode_spec=td.ModeSpec(num_modes=2, filter_pol=polarization),
    )

    n1 = coupled.n_eff.values[:, 0]
    n2 = coupled.n_eff.values[:, 1]
    p_coupling = np.sin(np.pi * coupler_length * np.abs(n1 - n2) / wavelengths) ** 2

    return p_coupling, coupled


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

    # Calculate coupling for all wavelengths at once - following notebook approach
    p_coupling, _ = get_powercoupling(
        wavelengths_um,
        wg_widths=(wg_width1_um, wg_width2_um),
        wg_height=wg_height_um,
        wg_gap=wg_gap_um,
        coupler_length=coupler_length_um,
        wg_medium=core_medium,
        cladding_medium=clad_medium,
        polarization=polarization,
    )

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
    p_coupling = np.zeros(num_length_points)

    # Calculate coupling for each length using notebook approach
    for i, length_um in enumerate(lengths_um):
        p_coupling[i], _ = get_powercoupling(
            wavelength_um,
            wg_widths=(wg_width1_um, wg_width2_um),
            wg_height=wg_height_um,
            wg_gap=wg_gap_um,
            coupler_length=length_um,
            wg_medium=core_medium,
            cladding_medium=clad_medium,
            polarization=polarization,
        )
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

    _, coupled = get_powercoupling(
        wavelength_um,
        wg_widths=(wg_width1_um, wg_width2_um),
        wg_height=wg_height_um,
        wg_gap=wg_gap_um,
        coupler_length=1.0,  # Dummy length for mode plotting
        wg_medium=core_medium,
        cladding_medium=clad_medium,
        polarization=polarization,
    )
    return coupled


