"""
MZI Five-Coupler Stand-alone Implementation (JAX)

Coupler order (left-to-right along cascade):
  C1=0.50, C2=0.13, C3=0.12, C4=0.50, C5=0.25 by default.

Delay sequence from image (between couplers):
  T(ΔL) after C1, then B(2ΔL), then B(2ΔL+π), then B(2ΔL):
  T = C5 @ B(2ΔL) @ C4 @ B(2ΔL+π) @ C3 @ B(2ΔL) @ C2 @ T(ΔL) @ C1
"""

import jax
import jax.numpy as jnp

jax.config.update("jax_enable_x64", True)


def waveguide_effective_index(n0, n1, n2, lambda0, wl):
    d = wl - lambda0
    return n0 + n1 * d + n2 * d * d


def waveguide_group_index(n0, n1, n2, lambda0):
    d = 0.0
    return waveguide_effective_index(n0, n1, n2, lambda0, lambda0) - lambda0 * (n1 + 2.0 * n2 * d)


def coupler_kappa(k0, k1, lambda0, wl):
    return jnp.clip(k0 + k1 * (wl - lambda0), 0.0, 1.0)


def coupler_matrix(kappa):
    t = jnp.sqrt(1.0 - kappa)
    k = 1j * jnp.sqrt(kappa)
    return jnp.array([[t, k], [k, t]])


def delay_matrix_top(delta_L, wl, neff):
    phi = 2.0 * jnp.pi * neff * delta_L / wl
    return jnp.array([[jnp.exp(1j * phi), 0], [0, 1]])


def delay_matrix_bottom(delta_L, wl, neff):
    phi = 2.0 * jnp.pi * neff * delta_L / wl
    return jnp.array([[1, 0], [0, jnp.exp(1j * phi)]])


@jax.jit
def mzi_5c_transmission_port1_jax(
    wavelengths,
    n0, n1, n2, lambda0, delta_lambda,
    kappa_c1, kappa_c1_slope,
    kappa_c2, kappa_c2_slope,
    kappa_c3, kappa_c3_slope,
    kappa_c4, kappa_c4_slope,
    kappa_c5, kappa_c5_slope,
):
    """Calculate 5-coupler MZI transmission with input port 1 (top)."""
    ngr = waveguide_group_index(n0, n1, n2, lambda0)
    delta_L = lambda0**2 / (2 * delta_lambda * ngr)
    two_delta_L = 2.0 * delta_L
    l_pi = 0.5 * lambda0 / n0

    input_vec = jnp.array([1.0, 0.0])

    def five_cascade(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k1 = coupler_kappa(kappa_c1, kappa_c1_slope, lambda0, wl)
        k2 = coupler_kappa(kappa_c2, kappa_c2_slope, lambda0, wl)
        k3 = coupler_kappa(kappa_c3, kappa_c3_slope, lambda0, wl)
        k4 = coupler_kappa(kappa_c4, kappa_c4_slope, lambda0, wl)
        k5 = coupler_kappa(kappa_c5, kappa_c5_slope, lambda0, wl)
        # Delays sequence: [ΔL (top), 2ΔL (bottom), (Lπ - 2ΔL) (bottom), (-2ΔL) (bottom)]
        T = (
            coupler_matrix(k5) @ delay_matrix_bottom(+two_delta_L, wl, neff) @
            coupler_matrix(k4) @ delay_matrix_bottom(-l_pi +two_delta_L, wl, neff) @
            coupler_matrix(k3) @ delay_matrix_bottom(-two_delta_L, wl, neff) @
            coupler_matrix(k2) @ delay_matrix_bottom(-delta_L, wl, neff) @
            coupler_matrix(k1)
        )
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    return jax.vmap(five_cascade)(wavelengths)


@jax.jit
def mzi_5c_transmission_port2_jax(
    wavelengths,
    n0, n1, n2, lambda0, delta_lambda,
    kappa_c1, kappa_c1_slope,
    kappa_c2, kappa_c2_slope,
    kappa_c3, kappa_c3_slope,
    kappa_c4, kappa_c4_slope,
    kappa_c5, kappa_c5_slope,
):
    """Calculate 5-coupler MZI transmission with input port 2 (bottom)."""
    ngr = waveguide_group_index(n0, n1, n2, lambda0)
    delta_L = lambda0**2 / (2 * delta_lambda * ngr)
    two_delta_L = 2.0 * delta_L
    l_pi = 0.5 * lambda0 / n0

    input_vec = jnp.array([0.0, 1.0])

    def five_cascade(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k1 = coupler_kappa(kappa_c1, kappa_c1_slope, lambda0, wl)
        k2 = coupler_kappa(kappa_c2, kappa_c2_slope, lambda0, wl)
        k3 = coupler_kappa(kappa_c3, kappa_c3_slope, lambda0, wl)
        k4 = coupler_kappa(kappa_c4, kappa_c4_slope, lambda0, wl)
        k5 = coupler_kappa(kappa_c5, kappa_c5_slope, lambda0, wl)
        # Delays sequence: [ΔL (top), 2ΔL (bottom), (Lπ - 2ΔL) (bottom), (-2ΔL) (bottom)]
        T = (
            coupler_matrix(k5) @ delay_matrix_bottom(two_delta_L, wl, neff) @
            coupler_matrix(k4) @ delay_matrix_bottom(-l_pi + two_delta_L, wl, neff) @
            coupler_matrix(k3) @ delay_matrix_bottom(-two_delta_L, wl, neff) @
            coupler_matrix(k2) @ delay_matrix_bottom(-delta_L, wl, neff) @
            coupler_matrix(k1)
        )
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    return jax.vmap(five_cascade)(wavelengths)


def evaluate_mzi_filter_5c_jax(
    wavelengths,  # in meters
    lambda0=1300e-9,
    delta_lambda=10e-9,
    n0=2.39, n1=-1.5e7, n2=1.2e13,
    # Couplers C1..C5 in left-to-right order
    kappa_c1: float = 0.50,
    kappa_c1_slope: float = 0.0,
    kappa_c2: float = 0.13,
    kappa_c2_slope: float = 0.0,
    kappa_c3: float = 0.12,
    kappa_c3_slope: float = 0.0,
    kappa_c4: float = 0.50,
    kappa_c4_slope: float = 0.0,
    kappa_c5: float = 0.25,
    kappa_c5_slope: float = 0.0,
    input_port: int = 1,
):
    """
    Evaluate 5-coupler MZI transmission.

    Returns:
        tuple: (T_top, T_bottom) transmission arrays
    """
    if input_port == 1:
        return mzi_5c_transmission_port1_jax(
            wavelengths,
            n0, n1, n2, lambda0, delta_lambda,
            kappa_c1, kappa_c1_slope,
            kappa_c2, kappa_c2_slope,
            kappa_c3, kappa_c3_slope,
            kappa_c4, kappa_c4_slope,
            kappa_c5, kappa_c5_slope,
        )
    else:
        return mzi_5c_transmission_port2_jax(
            wavelengths,
            n0, n1, n2, lambda0, delta_lambda,
            kappa_c1, kappa_c1_slope,
            kappa_c2, kappa_c2_slope,
            kappa_c3, kappa_c3_slope,
            kappa_c4, kappa_c4_slope,
            kappa_c5, kappa_c5_slope,
        )


