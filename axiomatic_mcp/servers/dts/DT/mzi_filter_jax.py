"""
MZI Filter Model with JAX Implementation

Consolidated module containing device models and filter evaluation functions
for Mach-Zehnder Interferometer (MZI) based optical filters.
"""

import jax
import jax.numpy as jnp
from jax import lax
import numpy as np

jax.config.update("jax_enable_x64", True)

# ============================================================================
# Device Model Functions
# ============================================================================

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
def mzi_transmission_jax(
    wavelengths, stages, delta_Loff, input_port,
    n0, n1, n2, lambda0, delta_lambda,
    k1, k1_slope=0.0,
    k2=0.0, k2_slope=0.0,
    k3=0.0, k3_slope=0.0,
    k4=0.0, k4_slope=0.0
):
    """Calculate MZI transmission for different stage configurations."""
    ngr = waveguide_group_index(n0, n1, n2, lambda0)

    delta_L = jnp.select(
        [stages == 1, stages == 2, stages == 3],
        [
            0.25 * lambda0**2 / (2 * delta_lambda * ngr) + delta_Loff,
            0.5 * lambda0**2 / (2 * delta_lambda * ngr) + delta_Loff,
            lambda0**2 / (2 * delta_lambda * ngr),
        ]
    )
    two_delta_L = 2 * delta_L
    two_delta_L_pi = two_delta_L + 0.5 * lambda0 / n0

    input_vec = jnp.where(
        (stages == 3) | (input_port == 1),
        jnp.array([1.0, 0.0]),
        jnp.array([0.0, 1.0])
    )

    def stage1(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k = coupler_kappa(k1, k1_slope, lambda0, wl)
        T = coupler_matrix(k) @ delay_matrix_top(delta_L, wl, neff) @ coupler_matrix(k)
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    def stage2(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k1_ = coupler_kappa(k1, k1_slope, lambda0, wl)
        k2_ = coupler_kappa(k2, k2_slope, lambda0, wl)
        k3_ = coupler_kappa(k3, k3_slope, lambda0, wl)
        T = (
            coupler_matrix(k3_) @ delay_matrix_bottom(two_delta_L, wl, neff) @
            coupler_matrix(k2_) @ delay_matrix_top(delta_L, wl, neff) @
            coupler_matrix(k1_)
        )
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    def stage3(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k1_ = coupler_kappa(k1, k1_slope, lambda0, wl)
        k2_ = coupler_kappa(k3, k3_slope, lambda0, wl)
        k3_ = coupler_kappa(k3, k3_slope, lambda0, wl)
        k4_ = coupler_kappa(k4, k4_slope, lambda0, wl)
        T = (
            coupler_matrix(k4_) @ delay_matrix_bottom(two_delta_L_pi, wl, neff) @
            coupler_matrix(k3_) @ delay_matrix_bottom(two_delta_L, wl, neff) @
            coupler_matrix(k2_) @ delay_matrix_top(delta_L, wl, neff) @
            coupler_matrix(k1_)
        )
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    def compute(wl):
        return lax.switch(stages - 1, [stage1, stage2, stage3], wl)

    return jax.vmap(compute)(wavelengths)

# ============================================================================
# Filter Evaluation Function
# ============================================================================

def evaluate_mzi_filter_jax(
    wavelengths,  # in meters  
    lambda0=1290e-9,
    delta_lambda=4.4e-9,
    # Stage parameters
    n0_1=2.39, n1_1=-1.5e7, n2_1=1.2e13,
    n0_2=2.39, n1_2=-1.5e7, n2_2=1.2e13,
    n0_3=2.39, n1_3=-1.5e7, n2_3=1.2e13,
    # Coupling coefficients
    kappa_05=0.5, kappa_05_slope=0.0,
    kappa_029=0.29, kappa_029_slope=0.0,
    kappa_008=0.08, kappa_008_slope=0.0,
    kappa_02=0.2, kappa_02_slope=0.0,
    kappa_004=0.04, kappa_004_slope=0.0
):
    """
    Evaluate MZI filter with 8 output channels.
    
    Returns:
        dict: Output transmission for channels λ1 through λ8
    """
    # Stage 3
    T1_3, T2_3 = mzi_transmission_jax(
        wavelengths, stages=3, delta_Loff=0, input_port=1,
        n0=n0_3, n1=n1_3, n2=n2_3, lambda0=lambda0, delta_lambda=delta_lambda,
        k1=kappa_05, k1_slope=kappa_05_slope,
        k3=kappa_02, k3_slope=kappa_02_slope,
        k4=kappa_004, k4_slope=kappa_004_slope
    )

    # Stage 2A (for λ1, λ3, λ5, λ7)
    T1_2A, T2_2A = mzi_transmission_jax(
        wavelengths, stages=2, delta_Loff=0.0 * lambda0 / n0_2, input_port=1,
        n0=n0_2, n1=n1_2, n2=n2_2, lambda0=lambda0, delta_lambda=delta_lambda,
        k1=kappa_05, k1_slope=kappa_05_slope,
        k2=kappa_029, k2_slope=kappa_029_slope,
        k3=kappa_008, k3_slope=kappa_008_slope
    )
    
    # Stage 2B (for λ2, λ4, λ6, λ8)
    T1_2B, T2_2B = mzi_transmission_jax(
        wavelengths, stages=2, delta_Loff=0.75 * lambda0 / n0_2, input_port=2,
        n0=n0_2, n1=n1_2, n2=n2_2, lambda0=lambda0, delta_lambda=delta_lambda,
        k1=kappa_05, k1_slope=kappa_05_slope,
        k2=kappa_029, k2_slope=kappa_029_slope,
        k3=kappa_008, k3_slope=kappa_008_slope
    )

    # Stage 1 configurations
    T1_1A, T2_1A = mzi_transmission_jax(  # λ1, λ5
        wavelengths, stages=1, delta_Loff=0.0 * lambda0 / n0_1, input_port=1,
        n0=n0_1, n1=n1_1, n2=n2_1, lambda0=lambda0, delta_lambda=delta_lambda,
        k1=kappa_05, k1_slope=kappa_05_slope
    )
    T1_1B, T2_1B = mzi_transmission_jax(  # λ3, λ7
        wavelengths, stages=1, delta_Loff=0.25 * lambda0 / n0_1, input_port=2,
        n0=n0_1, n1=n1_1, n2=n2_1, lambda0=lambda0, delta_lambda=delta_lambda,
        k1=kappa_05, k1_slope=kappa_05_slope
    )
    T1_1C, T2_1C = mzi_transmission_jax(  # λ2, λ6
        wavelengths, stages=1, delta_Loff=0.125 * lambda0 / n0_1, input_port=1,
        n0=n0_1, n1=n1_1, n2=n2_1, lambda0=lambda0, delta_lambda=delta_lambda,
        k1=kappa_05, k1_slope=kappa_05_slope
    )
    T1_1D, T2_1D = mzi_transmission_jax(  # λ4, λ8
        wavelengths, stages=1, delta_Loff=0.375 * lambda0 / n0_1, input_port=2,
        n0=n0_1, n1=n1_1, n2=n2_1, lambda0=lambda0, delta_lambda=delta_lambda,
        k1=kappa_05, k1_slope=kappa_05_slope
    )

    # Combine stages for each output channel
    return {
        'λ1': T2_3 * T2_2A * T1_1A,
        'λ2': T1_3 * T2_2B * T1_1C,
        'λ3': T2_3 * T1_2A * T2_1B,
        'λ4': T1_3 * T1_2B * T2_1D,
        'λ5': T2_3 * T2_2A * T2_1A,
        'λ6': T1_3 * T2_2B * T2_1C,
        'λ7': T2_3 * T1_2A * T1_1B,
        'λ8': T1_3 * T1_2B * T1_1D
    }
