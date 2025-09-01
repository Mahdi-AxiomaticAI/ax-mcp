
"""
MZI Stage 3 Stand-alone Implementation (JAX) - Fixed Version

Single stage 3 MZI with default parameters from the 8-channel filter.
"""

import jax
import jax.numpy as jnp
import numpy as np

jax.config.update("jax_enable_x64", True)

def waveguide_effective_index(n0, n1, n2, lambda0, wl):
    """Calculate effective index with wavelength dispersion."""
    d = wl - lambda0
    return n0 + n1 * d + n2 * d**2

def waveguide_group_index(n0, n1, n2, lambda0):
    """Calculate group index at central wavelength."""
    d = 0.0  # wl = lambda0
    return waveguide_effective_index(n0, n1, n2, lambda0, lambda0) - lambda0 * (n1 + 2 * n2 * d)

def coupler_kappa(k0, k1, lambda0, wl):
    """Calculate coupling coefficient with wavelength dependence."""
    return jnp.clip(k0 + k1 * (wl - lambda0), 0.0, 1.0)

def coupler_matrix(kappa):
    """Coupler transfer matrix."""
    t = jnp.sqrt(1.0 - kappa)
    k = 1j * jnp.sqrt(kappa)
    return jnp.array([[t, k], [k, t]])

def delay_matrix_top(delta_L, wl, neff):
    """Phase delay matrix for top waveguide."""
    phi = 2 * jnp.pi * neff * delta_L / wl
    return jnp.array([[jnp.exp(1j * phi), 0], [0, 1]])

def delay_matrix_bottom(delta_L, wl, neff):
    """Phase delay matrix for bottom waveguide."""
    phi = 2 * jnp.pi * neff * delta_L / wl
    return jnp.array([[1, 0], [0, jnp.exp(1j * phi)]])

@jax.jit
def mzi_stage3_transmission_port1_jax(
    wavelengths,
    n0, n1, n2, lambda0, delta_lambda,
    kappa_05, kappa_05_slope,
    kappa_02, kappa_02_slope,
    kappa_004, kappa_004_slope
):
    """Calculate stage 3 MZI transmission with input port 1."""
    ngr = waveguide_group_index(n0, n1, n2, lambda0)
    
    delta_L = lambda0**2 / (2 * delta_lambda * ngr)
    two_delta_L = 2 * delta_L
    two_delta_L_pi = two_delta_L + 0.5 * lambda0 / n0

    input_vec = jnp.array([1.0, 0.0])

    def stage3(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k1_ = coupler_kappa(kappa_05, kappa_05_slope, lambda0, wl)
        k2_ = coupler_kappa(kappa_02, kappa_02_slope, lambda0, wl)  # k3 in original
        k3_ = coupler_kappa(kappa_004, kappa_004_slope, lambda0, wl)  # k4 in original
        T = (
            coupler_matrix(k3_) @ delay_matrix_bottom(two_delta_L_pi, wl, neff) @
            coupler_matrix(k2_) @ delay_matrix_bottom(two_delta_L, wl, neff) @
            coupler_matrix(k1_) @ delay_matrix_top(delta_L, wl, neff) @
            coupler_matrix(k1_)
        )
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    return jax.vmap(stage3)(wavelengths)

@jax.jit
def mzi_stage3_transmission_port2_jax(
    wavelengths,
    n0, n1, n2, lambda0, delta_lambda,
    kappa_05, kappa_05_slope,
    kappa_02, kappa_02_slope,
    kappa_004, kappa_004_slope
):
    """Calculate stage 3 MZI transmission with input port 2."""
    ngr = waveguide_group_index(n0, n1, n2, lambda0)
    
    delta_L = lambda0**2 / (2 * delta_lambda * ngr)
    two_delta_L = 2 * delta_L
    two_delta_L_pi = two_delta_L + 0.5 * lambda0 / n0

    input_vec = jnp.array([0.0, 1.0])

    def stage3(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k1_ = coupler_kappa(kappa_05, kappa_05_slope, lambda0, wl)
        k2_ = coupler_kappa(kappa_02, kappa_02_slope, lambda0, wl)  # k3 in original
        k3_ = coupler_kappa(kappa_004, kappa_004_slope, lambda0, wl)  # k4 in original
        T = (
            coupler_matrix(k3_) @ delay_matrix_bottom(two_delta_L_pi, wl, neff) @
            coupler_matrix(k2_) @ delay_matrix_bottom(two_delta_L, wl, neff) @
            coupler_matrix(k1_) @ delay_matrix_top(delta_L, wl, neff) @
            coupler_matrix(k1_)
        )
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    return jax.vmap(stage3)(wavelengths)

def evaluate_mzi_stage3_jax(
    wavelengths,  # in meters
    lambda0=1290e-9,
    delta_lambda=4.4e-9,
    n0=2.39, n1=-1.5e7, n2=1.2e13,
    kappa_05=0.5, kappa_05_slope=0.0,
    kappa_02=0.2, kappa_02_slope=0.0,
    kappa_004=0.04, kappa_004_slope=0.0,
    input_port=1
):
    """
    Evaluate stage 3 MZI transmission.
    
    Returns:
        tuple: (T_top, T_bottom) transmission arrays
    """
    if input_port == 1:
        return mzi_stage3_transmission_port1_jax(
            wavelengths, n0, n1, n2, lambda0, delta_lambda,
            kappa_05, kappa_05_slope, kappa_02, kappa_02_slope,
            kappa_004, kappa_004_slope
        )
    else:
        return mzi_stage3_transmission_port2_jax(
            wavelengths, n0, n1, n2, lambda0, delta_lambda,
            kappa_05, kappa_05_slope, kappa_02, kappa_02_slope,
            kappa_004, kappa_004_slope
        )