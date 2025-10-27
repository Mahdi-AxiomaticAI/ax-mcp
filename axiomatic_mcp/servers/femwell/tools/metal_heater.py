"""Metal heater phase shifter utilities using femwell.

Provides parameterized functions to compute thermal distribution and
phase shift characteristics of TiN metal heater phase shifters.
Based on the metal_heater_phase_shifter.py example.
"""

from __future__ import annotations

import numpy as np


def _get_femwell_deps():
    """Import-heavy modules are loaded lazily to allow server registration without deps."""
    from collections import OrderedDict
    from shapely.geometry import LineString, Polygon
    from skfem import Basis, ElementTriP0
    from skfem.io.meshio import from_meshio
    from femwell.maxwell.waveguide import compute_modes
    from femwell.mesh import mesh_from_OrderedDict
    from femwell.thermal import solve_thermal

    return {
        'OrderedDict': OrderedDict,
        'LineString': LineString,
        'Polygon': Polygon,
        'Basis': Basis,
        'ElementTriP0': ElementTriP0,
        'from_meshio': from_meshio,
        'compute_modes': compute_modes,
        'mesh_from_OrderedDict': mesh_from_OrderedDict,
        'solve_thermal': solve_thermal,
    }


def create_metal_heater_mesh(
    *,
    w_sim: float = 16.0,
    h_clad: float = 2.8,
    h_box: float = 2.0,
    w_core: float = 0.5,
    h_core: float = 0.22,
    h_heater: float = 0.14,
    w_heater: float = 2.0,
    offset_heater: float = 2.0,
    h_silicon: float = 0.5,
    core_resolution: float = 0.04,
    heater_resolution: float = 0.1,
    default_resolution_max: float = 0.6,
):
    """Create mesh for metal heater phase shifter structure.

    Args:
        w_sim: Simulation width in micrometers
        h_clad: Cladding height in micrometers
        h_box: BOX layer height in micrometers
        w_core: Core width in micrometers
        h_core: Core height in micrometers
        h_heater: Heater height in micrometers
        w_heater: Heater width in micrometers
        offset_heater: Heater offset from core center in micrometers
        h_silicon: Silicon substrate height in micrometers
        core_resolution: Mesh resolution for core
        heater_resolution: Mesh resolution for heater
        default_resolution_max: Maximum default mesh resolution

    Returns:
        mesh: The created mesh object
    """
    deps = _get_femwell_deps()
    OrderedDict = deps['OrderedDict']
    LineString = deps['LineString']
    Polygon = deps['Polygon']
    from_meshio = deps['from_meshio']
    mesh_from_OrderedDict = deps['mesh_from_OrderedDict']

    # Adjust offset to be from waveguide surface
    offset_heater_abs = offset_heater + (h_core + h_heater) / 2

    polygons = OrderedDict(
        bottom=LineString(
            [
                (-w_sim / 2, -h_core / 2 - h_box - h_silicon),
                (w_sim / 2, -h_core / 2 - h_box - h_silicon),
            ]
        ),
        core=Polygon(
            [
                (-w_core / 2, -h_core / 2),
                (-w_core / 2, h_core / 2),
                (w_core / 2, h_core / 2),
                (w_core / 2, -h_core / 2),
            ]
        ),
        heater=Polygon(
            [
                (-w_heater / 2, -h_heater / 2 + offset_heater_abs),
                (-w_heater / 2, h_heater / 2 + offset_heater_abs),
                (w_heater / 2, h_heater / 2 + offset_heater_abs),
                (w_heater / 2, -h_heater / 2 + offset_heater_abs),
            ]
        ),
        clad=Polygon(
            [
                (-w_sim / 2, -h_core / 2),
                (-w_sim / 2, -h_core / 2 + h_clad),
                (w_sim / 2, -h_core / 2 + h_clad),
                (w_sim / 2, -h_core / 2),
            ]
        ),
        box=Polygon(
            [
                (-w_sim / 2, -h_core / 2),
                (-w_sim / 2, -h_core / 2 - h_box),
                (w_sim / 2, -h_core / 2 - h_box),
                (w_sim / 2, -h_core / 2),
            ]
        ),
        wafer=Polygon(
            [
                (-w_sim / 2, -h_core / 2 - h_box - h_silicon),
                (-w_sim / 2, -h_core / 2 - h_box),
                (w_sim / 2, -h_core / 2 - h_box),
                (w_sim / 2, -h_core / 2 - h_box - h_silicon),
            ]
        ),
    )

    resolutions = {
        'core': {'resolution': core_resolution, 'distance': 1},
        'clad': {'resolution': default_resolution_max, 'distance': 1},
        'box': {'resolution': default_resolution_max, 'distance': 1},
        'heater': {'resolution': heater_resolution, 'distance': 1},
    }

    mesh = from_meshio(mesh_from_OrderedDict(polygons, resolutions, default_resolution_max=default_resolution_max))

    return mesh, polygons


def compute_metal_heater_phase_shifter(
    *,
    currents: list[float] | np.ndarray,
    wavelength: float = 1.55,
    phase_shifter_length: float = 320.0,
    w_sim: float = 16.0,
    h_clad: float = 2.8,
    h_box: float = 2.0,
    w_core: float = 0.5,
    h_core: float = 0.22,
    h_heater: float = 0.14,
    w_heater: float = 2.0,
    offset_heater: float = 2.0,
    h_silicon: float = 0.5,
    # Thermal conductivities (W/(m*K) -> converted to W/(um*K) internally)
    k_core: float = 90.0,
    k_box: float = 1.38,
    k_clad: float = 1.38,
    k_heater: float = 28.0,
    k_wafer: float = 148.0,
    # Thermo-optic coefficients (1/K)
    dn_dT_clad: float = 1.00e-5,
    dn_dT_core: float = 1.86e-4,
    # Base refractive indices
    n_clad: float = 1.444,
    n_core: float = 3.4777,
    # Heater electrical properties
    heater_resistivity: float = 2.3e6,  # S/m
    num_modes: int = 1,
):
    """Compute phase shift vs current for metal heater phase shifter.

    Args:
        currents: Array of currents in amperes
        wavelength: Wavelength in micrometers
        phase_shifter_length: Length of phase shifter in micrometers
        w_sim: Simulation width in micrometers
        h_clad: Cladding height in micrometers
        h_box: BOX layer height in micrometers
        w_core: Core width in micrometers
        h_core: Core height in micrometers
        h_heater: Heater height in micrometers
        w_heater: Heater width in micrometers
        offset_heater: Heater offset from waveguide surface in micrometers
        h_silicon: Silicon substrate height in micrometers
        k_core: Thermal conductivity of core (W/(m*K))
        k_box: Thermal conductivity of BOX (W/(m*K))
        k_clad: Thermal conductivity of cladding (W/(m*K))
        k_heater: Thermal conductivity of heater (W/(m*K))
        k_wafer: Thermal conductivity of wafer (W/(m*K))
        dn_dT_clad: Thermo-optic coefficient of cladding (1/K)
        dn_dT_core: Thermo-optic coefficient of core (1/K)
        n_clad: Base refractive index of cladding
        n_core: Base refractive index of core
        heater_resistivity: Heater electrical conductivity (S/m)
        num_modes: Number of modes to compute

    Returns:
        tuple: (currents_array, powers_mW, neffs, phase_shifts_rad, temperatures_2D_list, basis_list)
            - currents_array: Input currents (A)
            - powers_mW: Electrical power dissipated (mW)
            - neffs: Effective indices for each current
            - phase_shifts_rad: Phase shifts in radians
            - temperatures_2D_list: List of temperature distributions (for plotting)
            - basis_list: List of basis objects (for plotting)
    """
    deps = _get_femwell_deps()
    Basis = deps['Basis']
    ElementTriP0 = deps['ElementTriP0']
    solve_thermal = deps['solve_thermal']
    compute_modes = deps['compute_modes']

    # Create mesh once
    mesh, polygons = create_metal_heater_mesh(
        w_sim=w_sim,
        h_clad=h_clad,
        h_box=h_box,
        w_core=w_core,
        h_core=h_core,
        h_heater=h_heater,
        w_heater=w_heater,
        offset_heater=offset_heater,
        h_silicon=h_silicon,
    )

    currents_array = np.asarray(currents)
    heater_area = polygons["heater"].area
    current_densities = currents_array / heater_area

    neffs = []
    temperatures_2D_list = []
    basis_list = []

    for current_density in current_densities:
        # Set up thermal conductivity
        basis0 = Basis(mesh, ElementTriP0(), intorder=4)
        thermal_conductivity_p0 = basis0.zeros()
        for domain, value in {
            "core": k_core,
            "box": k_box,
            "clad": k_clad,
            "heater": k_heater,
            "wafer": k_wafer,
        }.items():
            thermal_conductivity_p0[basis0.get_dofs(elements=domain)] = value
        thermal_conductivity_p0 *= 1e-12  # Convert from W/(m*K) to W/(um*K)

        # Solve thermal equation
        basis, temperature = solve_thermal(
            basis0,
            thermal_conductivity_p0,
            specific_conductivity={"heater": heater_resistivity},
            current_densities={"heater": current_density},
            fixed_boundaries={"bottom": 0},
        )

        # Store temperature and basis for plotting
        temperatures_2D_list.append(temperature)
        basis_list.append(basis)

        # Project temperature onto P0 basis and compute epsilon
        temperature0 = basis0.project(basis.interpolate(temperature))
        epsilon = basis0.zeros() + (n_clad + dn_dT_clad * temperature0) ** 2
        epsilon[basis0.get_dofs(elements="core")] = (
            n_core + dn_dT_core * temperature0[basis0.get_dofs(elements="core")]
        ) ** 2

        # Compute modes
        modes = compute_modes(basis0, epsilon, wavelength=wavelength, num_modes=num_modes)
        neffs.append(np.real(modes[0].n_eff))

    neffs_array = np.array(neffs)

    # Calculate phase shifts
    phase_shifts_rad = 2 * np.pi / wavelength * (neffs_array - neffs_array[0]) * phase_shifter_length

    # Calculate electrical power (V*I), where V = I*R = I*(1/sigma)*(L/A)
    # For 2D simulation, power per unit length
    # P = I^2 * R/L = I^2 / (sigma * A)
    # For unit length in z: P_per_length = current_density^2 / sigma * area
    powers_mW = (currents_array**2 / heater_resistivity / heater_area) * 1e3  # Convert to mW

    return currents_array, powers_mW, neffs_array, phase_shifts_rad, temperatures_2D_list, basis_list
