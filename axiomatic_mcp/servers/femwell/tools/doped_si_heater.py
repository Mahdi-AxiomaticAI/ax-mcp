"""Doped silicon heater phase shifter utilities using femwell.

Provides parameterized functions to compute thermal distribution and
phase shift characteristics of doped silicon heater phase shifters.
Based on the si_heater_phase_shifter.py example.
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


def create_doped_si_heater_mesh(
    *,
    w_sim: float = 32.0,
    h_clad: float = 2.8,
    h_box: float = 2.0,
    w_core: float = 0.5,
    h_core: float = 0.22,
    w_buffer: float = 0.8,
    h_buffer: float = 0.09,
    w_heater: float = 1.0,
    core_resolution: float = 0.01,
    heater_resolution: float = 0.01,
    default_resolution_max: float = 0.4,
):
    """Create mesh for doped silicon heater phase shifter structure.

    This creates a rib waveguide with lateral doped silicon heaters.

    Args:
        w_sim: Simulation width in micrometers
        h_clad: Cladding height in micrometers
        h_box: BOX layer height in micrometers
        w_core: Core width in micrometers
        h_core: Core height in micrometers
        w_buffer: Buffer/slab width on each side in micrometers
        h_buffer: Buffer/slab height in micrometers
        w_heater: Heater width in micrometers
        core_resolution: Mesh resolution for core
        heater_resolution: Mesh resolution for heaters
        default_resolution_max: Maximum default mesh resolution

    Returns:
        tuple: (mesh, polygons) - The created mesh object and polygon dict
    """
    deps = _get_femwell_deps()
    OrderedDict = deps['OrderedDict']
    LineString = deps['LineString']
    Polygon = deps['Polygon']
    from_meshio = deps['from_meshio']
    mesh_from_OrderedDict = deps['mesh_from_OrderedDict']

    polygons = OrderedDict(
        bottom=LineString([(-w_sim / 2, -h_box), (w_sim / 2, -h_box)]),
        core=Polygon(
            [
                (-w_core / 2, 0),
                (-w_core / 2, h_core),
                (w_core / 2, h_core),
                (w_core / 2, 0),
            ]
        ),
        slab_l=Polygon(
            [
                (-w_core / 2 - w_buffer, 0),
                (-w_core / 2 - w_buffer, h_buffer),
                (-w_core / 2, h_buffer),
                (-w_core / 2, 0),
            ]
        ),
        slab_r=Polygon(
            [
                (+w_core / 2 + w_buffer, 0),
                (+w_core / 2 + w_buffer, h_buffer),
                (+w_core / 2, h_buffer),
                (+w_core / 2, 0),
            ]
        ),
        heater_l=Polygon(
            [
                (-w_core / 2 - w_buffer - w_heater, 0),
                (-w_core / 2 - w_buffer - w_heater, h_buffer),
                (-w_core / 2 - w_buffer, h_buffer),
                (-w_core / 2 - w_buffer, 0),
            ]
        ),
        heater_r=Polygon(
            [
                (w_core / 2 + w_buffer + w_heater, 0),
                (w_core / 2 + w_buffer + w_heater, h_buffer),
                (w_core / 2 + w_buffer, h_buffer),
                (w_core / 2 + w_buffer, 0),
            ]
        ),
        clad=Polygon(
            [
                (-w_sim / 2, 0),
                (-w_sim / 2, h_clad),
                (w_sim / 2, h_clad),
                (w_sim / 2, 0),
            ]
        ),
        box=Polygon(
            [
                (-w_sim / 2, 0),
                (-w_sim / 2, -h_box),
                (w_sim / 2, -h_box),
                (w_sim / 2, 0),
            ]
        ),
    )

    resolutions = {
        'core': {'resolution': core_resolution, 'distance': 1},
        'clad': {'resolution': default_resolution_max, 'distance': 1},
        'box': {'resolution': default_resolution_max, 'distance': 1},
        'heater_l': {'resolution': heater_resolution, 'distance': 1},
        'heater_r': {'resolution': heater_resolution, 'distance': 1},
    }

    mesh = from_meshio(mesh_from_OrderedDict(polygons, resolutions, default_resolution_max=default_resolution_max))

    return mesh, polygons


def compute_doped_si_heater_phase_shifter(
    *,
    powers_mW: list[float] | np.ndarray,
    wavelength: float = 1.55,
    phase_shifter_length: float = 320.0,
    w_sim: float = 32.0,
    h_clad: float = 2.8,
    h_box: float = 2.0,
    w_core: float = 0.5,
    h_core: float = 0.22,
    w_buffer: float = 0.8,
    h_buffer: float = 0.09,
    w_heater: float = 1.0,
    # Thermal conductivities (W/(m*K) -> converted to W/(um*K) internally)
    k_core: float = 90.0,
    k_box: float = 1.38,
    k_clad: float = 1.38,
    k_slab: float = 55.0,
    k_heater: float = 55.0,
    # Thermo-optic coefficients (1/K)
    dn_dT_clad: float = 1.00e-5,
    dn_dT_core: float = 1.86e-4,
    # Base refractive indices
    n_clad: float = 1.444,
    n_core: float = 3.4777,
    # Heater electrical properties
    heater_resistivity: float = 1e5,  # S/m (doped Si)
    # Temperature boundary
    T_ambient: float = 303.0,  # K
    num_modes: int = 1,
):
    """Compute phase shift vs power for doped silicon heater phase shifter.

    Args:
        powers_mW: Array of electrical powers in milliwatts
        wavelength: Wavelength in micrometers
        phase_shifter_length: Length of phase shifter in micrometers
        w_sim: Simulation width in micrometers
        h_clad: Cladding height in micrometers
        h_box: BOX layer height in micrometers
        w_core: Core width in micrometers
        h_core: Core height in micrometers
        w_buffer: Buffer/slab width on each side in micrometers
        h_buffer: Buffer/slab height in micrometers
        w_heater: Heater width in micrometers
        k_core: Thermal conductivity of core (W/(m*K))
        k_box: Thermal conductivity of BOX (W/(m*K))
        k_clad: Thermal conductivity of cladding (W/(m*K))
        k_slab: Thermal conductivity of slab (W/(m*K))
        k_heater: Thermal conductivity of heater (W/(m*K))
        dn_dT_clad: Thermo-optic coefficient of cladding (1/K)
        dn_dT_core: Thermo-optic coefficient of core (1/K)
        n_clad: Base refractive index of cladding
        n_core: Base refractive index of core
        heater_resistivity: Heater electrical conductivity (S/m)
        T_ambient: Ambient temperature (K)
        num_modes: Number of modes to compute

    Returns:
        tuple: (powers_mW_array, currents_A, neffs, phase_shifts_rad, temperatures_2D_list, basis_list)
            - powers_mW_array: Input powers (mW)
            - currents_A: Corresponding currents (A)
            - neffs: Effective indices for each power
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
    mesh, polygons = create_doped_si_heater_mesh(
        w_sim=w_sim,
        h_clad=h_clad,
        h_box=h_box,
        w_core=w_core,
        h_core=h_core,
        w_buffer=w_buffer,
        h_buffer=h_buffer,
        w_heater=w_heater,
    )

    powers_mW_array = np.asarray(powers_mW)
    total_heater_area = polygons["heater_l"].area + polygons["heater_r"].area

    # Calculate currents from powers
    # P = I^2 * R/L = I^2 / (sigma * A_total) for unit length
    # For 2D: P [W/um] = I^2 / (sigma [S/m] * A [um^2]) * 1e6
    # Given power in mW and length in um:
    # P_total [W] = P_per_length [W/um] * L [um] = I^2 / (sigma * A_total * 1e-12)
    # I = sqrt(P_total * sigma * A_total * 1e-12)
    # where P_total in W, A_total in um^2
    currents_A = np.sqrt(
        powers_mW_array * 1e-3 * heater_resistivity * total_heater_area * 1e-12 / (phase_shifter_length * 1e-6)
    )

    neffs = []
    temperatures_2D_list = []
    basis_list = []

    for current in currents_A:
        # Set up thermal conductivity
        basis0 = Basis(mesh, ElementTriP0(), intorder=4)
        thermal_conductivity_p0 = basis0.zeros()
        for domain, value in {
            "core": k_core,
            "box": k_box,
            "clad": k_clad,
            "slab_l": k_slab,
            "slab_r": k_slab,
            "heater_l": k_heater,
            "heater_r": k_heater,
        }.items():
            thermal_conductivity_p0[basis0.get_dofs(elements=domain)] = value
        thermal_conductivity_p0 *= 1e-12  # Convert from W/(m*K) to W/(um*K)

        # Current density (same for both heaters)
        current_density = current / total_heater_area

        # Solve thermal equation
        basis, temperature = solve_thermal(
            basis0,
            thermal_conductivity_p0,
            specific_conductivity={"heater_l": heater_resistivity, "heater_r": heater_resistivity},
            current_densities={"heater_l": current_density, "heater_r": current_density},
            fixed_boundaries={"bottom": T_ambient},
        )

        # Store temperature and basis for plotting
        temperatures_2D_list.append(temperature)
        basis_list.append(basis)

        # Project temperature onto P0 basis and compute epsilon
        temperature0 = basis0.project(basis.interpolate(temperature))
        epsilon = basis0.zeros() + (n_clad + dn_dT_clad * (temperature0 - T_ambient)) ** 2

        # Core and slabs have same thermo-optic coefficient (all silicon)
        for domain in ["core", "slab_l", "slab_r"]:
            epsilon[basis0.get_dofs(elements=domain)] = (
                n_core + dn_dT_core * (temperature0[basis0.get_dofs(elements=domain)] - T_ambient)
            ) ** 2

        # Compute modes
        modes = compute_modes(basis0, epsilon, wavelength=wavelength, num_modes=num_modes)
        neffs.append(np.real(modes[0].n_eff))

    neffs_array = np.array(neffs)

    # Calculate phase shifts
    phase_shifts_rad = 2 * np.pi / wavelength * (neffs_array - neffs_array[0]) * phase_shifter_length

    return powers_mW_array, currents_A, neffs_array, phase_shifts_rad, temperatures_2D_list, basis_list
