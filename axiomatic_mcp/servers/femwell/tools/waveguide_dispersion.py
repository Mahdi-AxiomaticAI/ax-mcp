"""Waveguide dispersion utilities using femwell.

Provides parameterized functions to compute effective index, group index,
and group velocity dispersion vs wavelength for dielectric waveguides.
Based on the vary_wavelength.py example.
"""

from __future__ import annotations

import numpy as np
from numpy.polynomial import Polynomial
from scipy.constants import speed_of_light


def _get_femwell_deps():
    """Import-heavy modules are loaded lazily to allow server registration without deps."""
    from collections import OrderedDict
    from shapely.geometry import box
    from shapely.ops import clip_by_rect
    from skfem import Basis, ElementTriP0
    from skfem.io.meshio import from_meshio
    from femwell.maxwell.waveguide import compute_modes
    from femwell.mesh import mesh_from_OrderedDict

    return {
        'OrderedDict': OrderedDict,
        'box': box,
        'clip_by_rect': clip_by_rect,
        'Basis': Basis,
        'ElementTriP0': ElementTriP0,
        'from_meshio': from_meshio,
        'compute_modes': compute_modes,
        'mesh_from_OrderedDict': mesh_from_OrderedDict,
    }


def n_silicon_nitride(wavelength: float) -> float:
    """Sellmeier equation for Si3N4 refractive index.

    Args:
        wavelength: Wavelength in micrometers

    Returns:
        Refractive index at given wavelength
    """
    x = wavelength
    return (1 + 3.0249 / (1 - (0.1353406 / x) ** 2) + 40314 / (1 - (1239.842 / x) ** 2)) ** 0.5


def n_silicon_dioxide(wavelength: float) -> float:
    """Sellmeier equation for SiO2 refractive index.

    Args:
        wavelength: Wavelength in micrometers

    Returns:
        Refractive index at given wavelength
    """
    x = wavelength
    return (
        1
        + 0.6961663 / (1 - (0.0684043 / x) ** 2)
        + 0.4079426 / (1 - (0.1162414 / x) ** 2)
        + 0.8974794 / (1 - (9.896161 / x) ** 2)
    ) ** 0.5


def create_waveguide_mesh(
    *,
    w_core: float = 1.0,
    h_core: float = 0.5,
    buffer_size: float = 1.0,
    core_resolution: float = 0.1,
    default_resolution_max: float = 0.6,
):
    """Create mesh for rectangular waveguide with box and cladding.

    Args:
        w_core: Core width in micrometers
        h_core: Core height in micrometers
        buffer_size: Buffer region size around core in micrometers
        core_resolution: Mesh resolution for core
        default_resolution_max: Maximum default mesh resolution

    Returns:
        mesh: The created mesh object
    """
    deps = _get_femwell_deps()
    OrderedDict = deps['OrderedDict']
    box = deps['box']
    clip_by_rect = deps['clip_by_rect']
    from_meshio = deps['from_meshio']
    mesh_from_OrderedDict = deps['mesh_from_OrderedDict']

    # Create core geometry
    core = box(0, 0, w_core, h_core)

    # Create surrounding regions using buffer and clipping
    polygons = OrderedDict(
        core=core,
        box=clip_by_rect(core.buffer(buffer_size, resolution=4), -np.inf, -np.inf, np.inf, 0),
        clad=clip_by_rect(core.buffer(buffer_size, resolution=4), -np.inf, 0, np.inf, np.inf),
    )

    resolutions = {
        'core': {'resolution': core_resolution, 'distance': 1}
    }

    mesh = from_meshio(
        mesh_from_OrderedDict(polygons, resolutions, default_resolution_max=default_resolution_max)
    )

    return mesh


def compute_waveguide_dispersion(
    *,
    wavelengths: list[float] | np.ndarray,
    w_core: float = 1.0,
    h_core: float = 0.5,
    core_material: str = "Si3N4",
    box_material: str = "SiO2",
    clad_material: str = "air",
    num_modes: int = 2,
    polynomial_degree: int = 4,
):
    """Compute effective index, group index, and GVD vs wavelength.

    Args:
        wavelengths: Array of wavelengths in micrometers
        w_core: Core width in micrometers
        h_core: Core height in micrometers
        core_material: Core material ("Si3N4", "Si", or custom float for fixed n)
        box_material: BOX material ("SiO2", "Si3N4", or custom float)
        clad_material: Cladding material ("air", "SiO2", or custom float)
        num_modes: Number of modes to compute
        polynomial_degree: Polynomial degree for group velocity calculation

    Returns:
        tuple: (wavelengths_array, neffs_array, ng_array, gvd_array, te_fracs_array)
            - wavelengths_array: Wavelength array (um)
            - neffs_array: Effective indices [wavelengths, modes]
            - ng_array: Group indices [wavelengths, modes]
            - gvd_array: Group velocity dispersion [wavelengths, modes] (ps/(nm*km))
            - te_fracs_array: TE fraction [wavelengths, modes]
    """
    deps = _get_femwell_deps()
    Basis = deps['Basis']
    ElementTriP0 = deps['ElementTriP0']
    compute_modes = deps['compute_modes']

    # Material index functions
    material_funcs = {
        "Si3N4": n_silicon_nitride,
        "SiO2": n_silicon_dioxide,
        "air": lambda wl: 1.0,
        "Si": lambda wl: 3.48,  # Approximate, wavelength-independent
    }

    # Get material functions or use constant values
    def get_n(material, wavelength):
        if material in material_funcs:
            return material_funcs[material](wavelength)
        else:
            return float(material)  # Treat as constant refractive index

    # Create mesh once
    mesh = create_waveguide_mesh(w_core=w_core, h_core=h_core)

    wavelengths_array = np.asarray(wavelengths)
    all_neffs = np.zeros((len(wavelengths_array), num_modes))
    all_te_fracs = np.zeros((len(wavelengths_array), num_modes))

    # Sweep wavelengths
    for i, wavelength in enumerate(wavelengths_array):
        basis0 = Basis(mesh, ElementTriP0())
        epsilon = basis0.zeros(dtype=complex)

        # Set epsilon for each domain
        for subdomain, material in {
            "core": core_material,
            "box": box_material,
            "clad": clad_material,
        }.items():
            n = get_n(material, wavelength)
            epsilon[basis0.get_dofs(elements=subdomain)] = n ** 2

        # Compute modes
        modes = compute_modes(basis0, epsilon, wavelength=wavelength, num_modes=num_modes)
        all_neffs[i] = np.real([mode.n_eff for mode in modes])
        all_te_fracs[i, :] = [mode.te_fraction for mode in modes]

    # Calculate group index for each mode
    ng_array = np.zeros_like(all_neffs)
    gvd_array = np.zeros_like(all_neffs)

    for mode_idx in range(num_modes):
        neffs_mode = all_neffs[:, mode_idx]

        # Fit polynomial to neff vs wavelength
        fit = Polynomial.fit(wavelengths_array, neffs_mode, deg=polynomial_degree)

        # Group index: ng = neff - lambda * dneff/dlambda
        dneff_dlambda = fit.deriv(1)(wavelengths_array)
        ng_array[:, mode_idx] = neffs_mode - wavelengths_array * dneff_dlambda

        # Group velocity dispersion: D = (lambda^2 / c) * d^2neff/dlambda^2
        # Units: ps/(nm*km) when lambda in um
        d2neff_dlambda2 = fit.deriv(2)(wavelengths_array)
        # Convert: lambda^2 in um^2, result in ps/(nm*km)
        # D = -lambda/c * dvg/dlambda = lambda^2/c * d2neff/dlambda2
        # With lambda in um, c in m/s: D [ps/(nm*km)] = lambda^2 * d2neff/dlambda2 * 1e6
        gvd_array[:, mode_idx] = (wavelengths_array ** 2) * d2neff_dlambda2 * 1e6

    return wavelengths_array, all_neffs, ng_array, gvd_array, all_te_fracs