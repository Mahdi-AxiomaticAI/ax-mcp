"""Depletion waveguide modulator utilities using femwell.

Provides parameterized functions to compute effective index, absorption,
and modulation characteristics of PN junction depletion modulators.
Based on the depletion_waveguide.ipynb notebook functionality.
"""

from __future__ import annotations

import numpy as np


def _get_femwell_deps():
    """Import-heavy modules are loaded lazily to allow server registration without deps."""
    from collections import OrderedDict
    import shapely
    from skfem import Basis, ElementTriP0
    from skfem.io.meshio import from_meshio
    from femwell.maxwell.waveguide import compute_modes
    from femwell.mesh import mesh_from_OrderedDict
    from femwell.pn_analytical import index_pn_junction, k_to_alpha_dB

    return {
        'OrderedDict': OrderedDict,
        'shapely': shapely,
        'Basis': Basis,
        'ElementTriP0': ElementTriP0,
        'from_meshio': from_meshio,
        'compute_modes': compute_modes,
        'mesh_from_OrderedDict': mesh_from_OrderedDict,
        'index_pn_junction': index_pn_junction,
        'k_to_alpha_dB': k_to_alpha_dB,
    }


def create_depletion_waveguide_mesh(
    *,
    wg_width: float = 0.5,
    wg_thickness: float = 0.22,
    slab_width: float = 3.0,
    slab_thickness: float = 0.09,
    clad_thickness: float = 2.0,
    core_resolution: float = 0.02,
    core_distance: float = 0.5,
    slab_resolution: float = 0.04,
    slab_distance: float = 0.5,
    default_resolution_max: float = 10.0,
):
    """Create mesh for depletion waveguide structure.

    Args:
        wg_width: Waveguide width in micrometers
        wg_thickness: Waveguide thickness in micrometers
        slab_width: Slab width in micrometers
        slab_thickness: Slab thickness in micrometers
        clad_thickness: Cladding thickness in micrometers
        core_resolution: Mesh resolution for core
        core_distance: Mesh distance parameter for core
        slab_resolution: Mesh resolution for slab
        slab_distance: Mesh distance parameter for slab
        default_resolution_max: Maximum default mesh resolution

    Returns:
        mesh: The created mesh object
    """
    deps = _get_femwell_deps()
    OrderedDict = deps['OrderedDict']
    shapely = deps['shapely']
    from_meshio = deps['from_meshio']
    mesh_from_OrderedDict = deps['mesh_from_OrderedDict']

    # Create geometry
    core = shapely.geometry.box(
        -wg_width / 2, -wg_thickness / 2,
        wg_width / 2, wg_thickness / 2
    )
    slab = shapely.geometry.box(
        -slab_width / 2, -wg_thickness / 2,
        slab_width / 2, -wg_thickness / 2 + slab_thickness
    )
    clad = shapely.geometry.box(
        -slab_width / 2, -clad_thickness / 2,
        slab_width / 2, clad_thickness / 2
    )

    polygons = OrderedDict(
        core=core,
        slab=slab,
        clad=clad,
    )

    resolutions = {
        'core': {'resolution': core_resolution, 'distance': core_distance},
        'slab': {'resolution': slab_resolution, 'distance': slab_distance},
    }

    mesh = from_meshio(
        mesh_from_OrderedDict(polygons, resolutions, default_resolution_max=default_resolution_max)
    )

    return mesh


def define_epsilon(
    mesh,
    *,
    voltage: float,
    xpn: float,
    NA: float,
    ND: float,
    wavelength: float,
    core_index: float = 3.45,
    slab_index: float = 3.45,
    clad_index: float = 1.444,
):
    """Define epsilon (permittivity) distribution for the depletion waveguide.

    Args:
        mesh: The mesh object
        voltage: Applied voltage in volts
        xpn: PN junction position
        NA: Acceptor doping concentration (cm^-3)
        ND: Donor doping concentration (cm^-3)
        wavelength: Wavelength in micrometers
        core_index: Refractive index of core
        slab_index: Refractive index of slab
        clad_index: Refractive index of cladding

    Returns:
        tuple: (basis0, epsilon) - basis and epsilon array
    """
    deps = _get_femwell_deps()
    Basis = deps['Basis']
    ElementTriP0 = deps['ElementTriP0']
    index_pn_junction = deps['index_pn_junction']

    basis0 = Basis(mesh, ElementTriP0())
    epsilon = basis0.zeros(dtype=complex)

    # Set base indices for core and slab
    for subdomain, n in {'core': core_index, 'slab': slab_index}.items():
        epsilon[basis0.get_dofs(elements=subdomain)] = n

    # Add PN junction contribution
    epsilon += basis0.project(
        lambda x: index_pn_junction(x[0], xpn, NA, ND, voltage, wavelength),
        dtype=complex,
    )

    # Set cladding index
    for subdomain, n in {'clad': clad_index}.items():
        epsilon[basis0.get_dofs(elements=subdomain)] = n

    # Square to get epsilon
    epsilon *= epsilon

    return basis0, epsilon


def compute_depletion_modulator(
    *,
    voltages: list[float],
    xpn: float = 0.0,
    NA: float = 1e18,
    ND: float = 1e18,
    wavelength: float = 1.55,
    wg_width: float = 0.5,
    wg_thickness: float = 0.22,
    slab_width: float = 3.0,
    slab_thickness: float = 0.09,
    clad_thickness: float = 2.0,
    core_index: float = 3.45,
    slab_index: float = 3.45,
    clad_index: float = 1.444,
    num_modes: int = 1,
    mode_order: int = 2,
):
    """Compute effective index and absorption as a function of voltage.

    Args:
        voltages: List of voltages to sweep
        xpn: PN junction position
        NA: Acceptor doping concentration (cm^-3)
        ND: Donor doping concentration (cm^-3)
        wavelength: Wavelength in micrometers
        wg_width: Waveguide width in micrometers
        wg_thickness: Waveguide thickness in micrometers
        slab_width: Slab width in micrometers
        slab_thickness: Slab thickness in micrometers
        clad_thickness: Cladding thickness in micrometers
        core_index: Refractive index of core
        slab_index: Refractive index of slab
        clad_index: Refractive index of cladding
        num_modes: Number of modes to compute
        mode_order: Mode solver order

    Returns:
        tuple: (voltages_array, neff_array, neff_change_array, absorption_dB_per_cm_array)
    """
    deps = _get_femwell_deps()
    compute_modes = deps['compute_modes']
    k_to_alpha_dB = deps['k_to_alpha_dB']

    # Create mesh once
    mesh = create_depletion_waveguide_mesh(
        wg_width=wg_width,
        wg_thickness=wg_thickness,
        slab_width=slab_width,
        slab_thickness=slab_thickness,
        clad_thickness=clad_thickness,
    )

    neff_vs_V = []

    for V in voltages:
        basis0, epsilon = define_epsilon(
            mesh,
            voltage=V,
            xpn=xpn,
            NA=NA,
            ND=ND,
            wavelength=wavelength,
            core_index=core_index,
            slab_index=slab_index,
            clad_index=clad_index,
        )
        modes = compute_modes(basis0, epsilon, wavelength=wavelength, num_modes=num_modes, order=mode_order)
        neff_vs_V.append(modes[0].n_eff)

    voltages_array = np.array(voltages)
    neff_array = np.array(neff_vs_V)
    neff_change = np.real(neff_array) - np.real(neff_array[0])
    absorption_dB_per_cm = k_to_alpha_dB(np.imag(neff_array), wavelength)

    return voltages_array, neff_array, neff_change, absorption_dB_per_cm


def get_epsilon_for_plot(
    *,
    voltage: float,
    xpn: float = 0.0,
    NA: float = 1e18,
    ND: float = 1e18,
    wavelength: float = 1.55,
    wg_width: float = 0.5,
    wg_thickness: float = 0.22,
    slab_width: float = 3.0,
    slab_thickness: float = 0.09,
    clad_thickness: float = 2.0,
    core_index: float = 3.45,
    slab_index: float = 3.45,
    clad_index: float = 1.444,
):
    """Get epsilon distribution for plotting at a single voltage.

    Returns:
        tuple: (mesh, basis0, epsilon)
    """
    mesh = create_depletion_waveguide_mesh(
        wg_width=wg_width,
        wg_thickness=wg_thickness,
        slab_width=slab_width,
        slab_thickness=slab_thickness,
        clad_thickness=clad_thickness,
    )

    basis0, epsilon = define_epsilon(
        mesh,
        voltage=voltage,
        xpn=xpn,
        NA=NA,
        ND=ND,
        wavelength=wavelength,
        core_index=core_index,
        slab_index=slab_index,
        clad_index=clad_index,
    )

    return mesh, basis0, epsilon
