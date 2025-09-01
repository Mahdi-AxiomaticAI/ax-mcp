"""
MZI Stage 1 Stand-alone Implementation (JAX)

Single directional-coupler pair with a top-arm delay ΔL. Matches the stage-1
transfer used inside the CWDM filter, with an optional wavelength-dependent
coupler slope.
"""

import jax
import jax.numpy as jnp

jax.config.update("jax_enable_x64", True)


def waveguide_effective_index(n0, n1, n2, lambda0, wl):
    d = wl - lambda0
    return n0 + n1 * d + n2 * d**2


def waveguide_group_index(n0, n1, n2, lambda0):
    d = 0.0
    return waveguide_effective_index(n0, n1, n2, lambda0, lambda0) - lambda0 * (n1 + 2 * n2 * d)


def coupler_kappa(k0, k1, lambda0, wl):
    return jnp.clip(k0 + k1 * (wl - lambda0), 0.0, 1.0)


def coupler_matrix(kappa):
    t = jnp.sqrt(1.0 - kappa)
    k = 1j * jnp.sqrt(kappa)
    return jnp.array([[t, k], [k, t]])


def delay_matrix_top(delta_L, wl, neff):
    phi = 2 * jnp.pi * neff * delta_L / wl
    return jnp.array([[jnp.exp(1j * phi), 0], [0, 1]])


@jax.jit
def mzi_stage1_transmission_port1_jax(
    wavelengths,
    n0, n1, n2, lambda0, delta_lambda,
    kappa_05, kappa_05_slope,
    delta_Loff=0.0,
):
    """Stage 1 with input at port 1 (top)."""
    ngr = waveguide_group_index(n0, n1, n2, lambda0)
    delta_L = 0.25 * lambda0**2 / (2 * delta_lambda * ngr) + delta_Loff
    input_vec = jnp.array([1.0, 0.0])

    def compute(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k = coupler_kappa(kappa_05, kappa_05_slope, lambda0, wl)
        T = coupler_matrix(k) @ delay_matrix_top(delta_L, wl, neff) @ coupler_matrix(k)
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    return jax.vmap(compute)(wavelengths)


@jax.jit
def mzi_stage1_transmission_port2_jax(
    wavelengths,
    n0, n1, n2, lambda0, delta_lambda,
    kappa_05, kappa_05_slope,
    delta_Loff=0.0,
):
    """Stage 1 with input at port 2 (bottom)."""
    ngr = waveguide_group_index(n0, n1, n2, lambda0)
    delta_L = 0.25 * lambda0**2 / (2 * delta_lambda * ngr) + delta_Loff
    input_vec = jnp.array([0.0, 1.0])

    def compute(wl):
        neff = waveguide_effective_index(n0, n1, n2, lambda0, wl)
        k = coupler_kappa(kappa_05, kappa_05_slope, lambda0, wl)
        T = coupler_matrix(k) @ delay_matrix_top(delta_L, wl, neff) @ coupler_matrix(k)
        out = T @ input_vec
        return jnp.abs(out[0])**2, jnp.abs(out[1])**2

    return jax.vmap(compute)(wavelengths)


def evaluate_mzi_stage1_jax(
    wavelengths,  # meters
    lambda0=1290e-9,
    delta_lambda=4.4e-9,
    n0=2.39, n1=-1.5e7, n2=1.2e13,
    kappa_05=0.5, kappa_05_slope=0.0,
    input_port=1,
    delta_Loff=0.0,
):
    """Return (T_top, T_bottom) for stage 1."""
    if input_port == 1:
        return mzi_stage1_transmission_port1_jax(
            wavelengths, n0, n1, n2, lambda0, delta_lambda, kappa_05, kappa_05_slope, delta_Loff
        )
    else:
        return mzi_stage1_transmission_port2_jax(
            wavelengths, n0, n1, n2, lambda0, delta_lambda, kappa_05, kappa_05_slope, delta_Loff
        )


