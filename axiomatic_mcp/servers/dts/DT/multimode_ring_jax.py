"""
JAX-based multimode ring resonator model (up to 3 modes) with partial coherence.

Features:
- Up to 3 ring modes, each with its own effective index, loss, coupling, weight
- Partial inter-mode coherence blending between incoherent and coherent sums
- Optional external reflection paths (facet, short path, substrate) as background fields
- Optional laser linewidth broadening (Gaussian in wavelength)
- Optional grating envelope (Gaussian loss in dB)
- Optional insertion loss and DC offset
- Optional slow drifts (polarization, mechanical) and random loss

Outputs linear power and dB spectra versus wavelength (nm)

Note: This is a compact, differentiable JAX reimplementation inspired by a notebook
multimode simulator. Some physical effects are simplified for clarity and stability.
Calibrate parameters to measurements for best fit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import jax
import jax.numpy as jnp


@dataclass
class ModeParams:
    """One ring mode parameters.

    - n_eff: effective index
    - alpha_dB_per_cm: power loss in dB/cm
    - kappa: cross-coupling amplitude (0..1); self-coupling t = sqrt(max(0, 1-k^2))
    - weight: relative field weight for this mode (used in field sum)
    """
    n_eff: float
    alpha_dB_per_cm: float
    kappa: float
    weight: float


@dataclass
class MultiModeRingParams:
    """Global parameters for the multimode simulation."""

    # wavelength sweep (nm)
    lam_start_nm: float = 1540.0
    lam_stop_nm: float = 1560.0
    num_points: int = 2001

    # up to three modes
    enable_mode2: bool = False
    enable_mode3: bool = False
    mode1: ModeParams = field(default_factory=lambda: ModeParams(n_eff=2.40, alpha_dB_per_cm=3.0, kappa=0.20, weight=1.0))
    mode2: ModeParams = field(default_factory=lambda: ModeParams(n_eff=2.45, alpha_dB_per_cm=3.0, kappa=0.15, weight=0.6))
    mode3: ModeParams = field(default_factory=lambda: ModeParams(n_eff=2.50, alpha_dB_per_cm=3.0, kappa=0.10, weight=0.4))

    # ring geometry
    ring_radius_um: float = 10_000.0  # micrometers; 10_000 μm = 10 mm? default will be overridden

    # background facet/waveguide loss (as an external field component)
    r_facet: float = 0.10
    L_wg_um: float = 200.0

    # optional external reflections (background fields)
    enable_short_path: bool = True
    r_short: float = 0.05
    L_short_um: float = 50.0

    enable_substrate: bool = False
    r_sub: float = 0.02
    L_sub_um: float = 300.0

    # inter-mode coherence blending (0=incoherent intensity sum, 1=fully coherent field sum)
    inter_mode_coherence: float = 1.0

    # finite laser linewidth (Gaussian in wavelength)
    enable_finite_linewidth: bool = False
    source_linewidth_fwhm_nm: float = 0.01

    # grating envelope (Gaussian loss in dB)
    enable_grating: bool = False
    grating_center_nm: float = 1550.0
    grating_fwhm_nm: float = 20.0
    grating_peak_loss_dB: float = 3.0

    # insertion loss and DC offset
    insertion_loss_dB: float = 0.0
    offset_level: float = 0.0

    # random initial phases for modes (seed)
    random_phase_seed: int = 0

    # slow drifts & random loss
    enable_pol_drift: bool = False
    pol_drift_ampl: float = 0.1  # relative amplitude modulation

    enable_mech_drift: bool = False
    mech_drift_amp: float = 0.1  # phase perturbation amplitude (rad)
    mech_drift_period_nm: float = 200.0

    enable_random_loss: bool = False
    random_loss_scale: float = 0.05


def _power_dB_to_field_amplitude(power_dB: jnp.ndarray) -> jnp.ndarray:
    return jnp.power(10.0, -power_dB / 20.0)


def _alpha_dBcm_to_roundtrip_field(alpha_dB_per_cm: float, L_m: jnp.ndarray) -> jnp.ndarray:
    # power loss in dB: alpha [dB/cm] * L[cm]; field amplitude = 10^(-dB/20)
    L_cm = L_m * 100.0
    power_dB = alpha_dB_per_cm * L_cm
    return _power_dB_to_field_amplitude(power_dB)


def _ring_field_allpass(wl_nm: jnp.ndarray, n_eff: float, a_rt: float, kappa: float) -> jnp.ndarray:
    """All-pass ring through field for one mode."""
    t = jnp.sqrt(jnp.clip(1.0 - kappa * kappa, 1e-8, 1.0))
    L_m = 0.0  # placeholder; phase uses n_eff and radius, handled outside via phi
    # Phase phi will be provided externally (since it's common for a given n_eff, radius and wl)
    raise NotImplementedError


def _ring_field_mode(
    wl_nm: jnp.ndarray,
    n_eff: float,
    kappa: float,
    alpha_dB_per_cm: float,
    ring_radius_um: float,
    extra_phase: jnp.ndarray,
) -> jnp.ndarray:
    """Compute through-field for one mode, including propagation loss and phase."""
    wl_m = wl_nm * 1e-9
    L_m = 2.0 * jnp.pi * (ring_radius_um * 1e-6)
    a = _alpha_dBcm_to_roundtrip_field(alpha_dB_per_cm, L_m)
    t = jnp.sqrt(jnp.clip(1.0 - kappa * kappa, 1e-8, 1.0))
    phi = 2.0 * jnp.pi * n_eff * L_m / wl_m + extra_phase
    ej = jnp.exp(-1j * phi)
    H = (t - a * ej) / (1.0 - a * t * ej)
    return H


def _gaussian_kernel(x: jnp.ndarray, fwhm: float) -> jnp.ndarray:
    sigma = fwhm / (2.0 * jnp.sqrt(2.0 * jnp.log(2.0)))
    g = jnp.exp(-0.5 * (x / sigma) ** 2)
    g = g / jnp.sum(g)
    return g


def _apply_linewidth_smoothing(wl_nm: jnp.ndarray, power: jnp.ndarray, fwhm_nm: float) -> jnp.ndarray:
    if fwhm_nm <= 0:
        return power
    # build kernel on the same grid; choose +/- 4 sigma window
    sigma = fwhm_nm / (2.0 * jnp.sqrt(2.0 * jnp.log(2.0)))
    half_span = jnp.maximum(3.0 * sigma, 3.0)  # at least a few points
    x = jnp.arange(-50, 51, dtype=wl_nm.dtype)  # 101-point kernel in index units
    # Map index step to nm spacing
    dw = (wl_nm[-1] - wl_nm[0]) / (wl_nm.shape[0] - 1)
    kernel = _gaussian_kernel(x * dw, fwhm_nm)
    # Use FFT convolution for speed
    pad = kernel.shape[0] // 2
    p_pad = jnp.pad(power, (pad, pad), mode="edge")
    # depthwise 1D conv via lax
    kernel_flip = kernel[::-1]
    out = jax.lax.conv_general_dilated(
        p_pad[None, None, :],
        kernel_flip[None, None, :],
        window_strides=(1,),
        padding="VALID",
        dimension_numbers=("NCH", "OIH", "NCH"),
    )[0, 0]
    return out


def _grating_envelope_dB(wl_nm: jnp.ndarray, center_nm: float, fwhm_nm: float, peak_loss_dB: float) -> jnp.ndarray:
    if fwhm_nm <= 0 or peak_loss_dB <= 0:
        return jnp.zeros_like(wl_nm)
    sigma = fwhm_nm / (2.0 * jnp.sqrt(2.0 * jnp.log(2.0)))
    return peak_loss_dB * jnp.exp(-0.5 * ((wl_nm - center_nm) / sigma) ** 2)


def _external_background_field(
    wl_nm: jnp.ndarray,
    n_eff_bg: float,
    paths: Tuple[Tuple[float, float], ...],  # sequence of (r_ampl, length_um)
) -> jnp.ndarray:
    wl_m = wl_nm * 1e-9
    E = jnp.zeros_like(wl_m, dtype=jnp.complex128)
    for r_ampl, L_um in paths:
        if r_ampl <= 0 or L_um <= 0:
            continue
        L_m = L_um * 1e-6
        phi = 2.0 * jnp.pi * n_eff_bg * L_m / wl_m
        E = E + r_ampl * jnp.exp(-1j * phi)
    return E


def compute_multimode_response(
    params: MultiModeRingParams,
) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """Compute multimode transmission.

    Returns (wavelength_nm, power_linear, power_dB)
    """
    # wavelength grid
    wl = jnp.linspace(params.lam_start_nm, params.lam_stop_nm, params.num_points)

    # random initial phases (fixed seed)
    key = jax.random.PRNGKey(params.random_phase_seed)
    phi0 = jax.random.uniform(key, shape=(3,), minval=0.0, maxval=2.0 * jnp.pi)

    # mechanical drift phase vs wavelength
    extra_phase = 0.0
    if params.enable_mech_drift and params.mech_drift_period_nm > 0:
        extra_phase = params.mech_drift_amp * jnp.sin(2.0 * jnp.pi * (wl - wl[0]) / params.mech_drift_period_nm)

    # Assemble active modes
    modes: Tuple[ModeParams, ...] = (params.mode1,)
    if params.enable_mode2:
        modes = modes + (params.mode2,)
    if params.enable_mode3:
        modes = modes + (params.mode3,)

    # Compute ring fields per mode
    E_modes = []
    weights = []
    for i, m in enumerate(modes):
        E_m = _ring_field_mode(
            wl_nm=wl,
            n_eff=m.n_eff,
            kappa=m.kappa,
            alpha_dB_per_cm=m.alpha_dB_per_cm,
            ring_radius_um=params.ring_radius_um,
            extra_phase=extra_phase + phi0[i],
        )
        E_modes.append(E_m)
        weights.append(m.weight)
    if len(E_modes) == 0:
        # fallback to single default mode
        m = params.mode1
        E_modes = [
            _ring_field_mode(wl, m.n_eff, m.kappa, m.alpha_dB_per_cm, params.ring_radius_um, extra_phase + phi0[0])
        ]
        weights = [m.weight]

    E_modes = jnp.stack(E_modes, axis=0)  # [M, N]
    weights = jnp.asarray(weights).reshape((-1, 1))  # [M,1]

    # Background external fields
    bg_paths = [(params.r_facet, params.L_wg_um)]
    if params.enable_short_path:
        bg_paths.append((params.r_short, params.L_short_um))
    if params.enable_substrate:
        bg_paths.append((params.r_sub, params.L_sub_um))
    E_bg = _external_background_field(wl, n_eff_bg=1.45, paths=tuple(bg_paths))

    # Combine modes with partial coherence
    # Incoherent sum of intensities (modes only)
    I_incoh = jnp.sum((weights**2) * jnp.abs(E_modes) ** 2, axis=0)
    # Fully coherent sum (fields) for modes
    E_coh = jnp.sum(weights * E_modes, axis=0)
    gamma = jnp.clip(params.inter_mode_coherence, 0.0, 1.0)

    # Background intensity
    I_bg = jnp.abs(E_bg) ** 2

    # Incoherent total intensity (modes + background)
    I_incoh_total = I_incoh + I_bg

    # Coherent total intensity (modes + background)
    E_total_coh = E_coh + E_bg
    I_coh_total = jnp.abs(E_total_coh) ** 2

    # Blend incoherent/coherent contributions
    I_total = (1.0 - gamma) * I_incoh_total + gamma * I_coh_total

    # Grating envelope (loss in dB)
    if params.enable_grating:
        loss_dB = _grating_envelope_dB(wl, params.grating_center_nm, params.grating_fwhm_nm, params.grating_peak_loss_dB)
        I_total = I_total * jnp.power(10.0, -loss_dB / 10.0)

    # Polarization drift as slow amplitude modulation
    if params.enable_pol_drift and params.pol_drift_ampl != 0.0:
        mod = 1.0 + params.pol_drift_ampl * jnp.sin(2.0 * jnp.pi * (wl - wl[0]) / (params.mech_drift_period_nm * 4.0))
        I_total = I_total * mod

    # Random loss: smooth multiplicative jitter
    if params.enable_random_loss and params.random_loss_scale > 0.0:
        # low-frequency noise via filtered random
        key2 = jax.random.PRNGKey(params.random_phase_seed + 1)
        noise = jax.random.normal(key2, shape=wl.shape)
        kernel = _gaussian_kernel(jnp.linspace(-1.0, 1.0, 41), 0.2)
        pad = kernel.shape[0] // 2
        n_pad = jnp.pad(noise, (pad, pad), mode="edge")
        filt = jax.lax.conv_general_dilated(
            n_pad[None, None, :], kernel[::-1][None, None, :], (1,), "VALID", ("NCH", "OIH", "NCH")
        )[0, 0]
        I_total = I_total * (1.0 + params.random_loss_scale * filt / jnp.max(jnp.abs(filt) + 1e-6))

    # Insertion loss and offset
    I_total = I_total * jnp.power(10.0, -params.insertion_loss_dB / 10.0) + params.offset_level

    # Linewidth smoothing
    if params.enable_finite_linewidth and params.source_linewidth_fwhm_nm > 0.0:
        I_total = _apply_linewidth_smoothing(wl, I_total, params.source_linewidth_fwhm_nm)

    # Normalize to max 0 dB scale for readability
    I_total = jnp.clip(I_total, 1e-16, jnp.inf)
    I_dB = 10.0 * jnp.log10(I_total / jnp.max(I_total))
    return wl, I_total, I_dB


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    p = MultiModeRingParams(
        lam_start_nm=1560.0, lam_stop_nm=1580.0, num_points=10001,
        enable_mode2=True, enable_mode3=False,
        mode1=ModeParams(n_eff=2.40, alpha_dB_per_cm=3.0, kappa=0.20, weight=1.0),
        mode2=ModeParams(n_eff=2.59, alpha_dB_per_cm=3.0, kappa=0.15, weight=0.6),
        ring_radius_um=500.0,
        enable_grating=True, grating_center_nm=1580.0, grating_fwhm_nm=150.0, grating_peak_loss_dB=3.0,
        inter_mode_coherence=0.002,
        enable_finite_linewidth=False, source_linewidth_fwhm_nm=0.01,
    )
    wl, I, I_dB = compute_multimode_response(p)
    plt.figure(figsize=(12, 4))
    plt.plot(wl, I_dB)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Relative Transmission (dB)")
    plt.title("Multimode Ring (JAX) – Relative dB")
    plt.grid(True, alpha=0.3, linestyle="--")
    plt.tight_layout()
    plt.show()


