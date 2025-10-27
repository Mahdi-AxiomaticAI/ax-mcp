# Femwell MCP Validation Report

**Benchmarking Against Tidy3D Reference Simulations**

*Date: 2025-10-24*

---

## Table of Contents
1. [Introduction](#introduction)
2. [Benchmark #1: TiN Metal Heater Phase Shifter](#benchmark-1-tin-metal-heater-phase-shifter)
3. [Benchmark #2: Doped Silicon Heater Phase Shifter](#benchmark-2-doped-silicon-heater-phase-shifter)
4. [Benchmark #3: Waveguide Dispersion](#benchmark-3-waveguide-dispersion)
5. [Benchmark #4: PN Junction Depletion Modulator](#benchmark-4-pn-junction-depletion-modulator)
6. [Summary and Recommendations](#summary-and-recommendations)

---

## Abstract

This report presents validation results for the Femwell Model Connectivity Protocol (MCP) tools against Tidy3D reference simulations. We benchmark three key photonic devices: (1) TiN metal heater phase shifter, (2) doped silicon heater phase shifter, and (3) PN junction depletion modulator. The validation focuses on comparing phase shift characteristics, modulation efficiency, and effective index modulation against established Tidy3D notebooks.

---

## Introduction

### Motivation

The Femwell MCP server provides computational tools for simulating photonic devices using finite element methods. To ensure accuracy and reliability, we validate these tools against Tidy3D, a well-established FDTD-based photonic simulation platform with comprehensive validation against experimental data.

### Benchmarking Methodology

For each device, we:
1. Extract reference data from Tidy3D Jupyter notebooks
2. Configure Femwell MCP tools with matching geometric and material parameters
3. Compare key performance metrics (phase shift, effective index, modulation efficiency)
4. Assess agreement within defined tolerance criteria (typically ±15% for phase shifters)

### Validation Criteria

- **✅ PASS**: Key metric error < 15%
- **⚠️ WARN**: Key metric error 15-30%
- **❌ FAIL**: Key metric error > 30%

---

## Benchmark #1: TiN Metal Heater Phase Shifter

### Overview

The TiN metal heater phase shifter uses resistive heating to induce thermal modulation of the waveguide effective index. Both Femwell and Tidy3D implementations are based on Jacques et al., *Opt. Express* 27, 10456 (2019).

### Device Configuration

| Parameter | Value | Unit |
|-----------|-------|------|
| **Waveguide width** | 0.5 | μm |
| **Waveguide height** | 0.22 | μm |
| **Heater width** | 2.0 | μm |
| **Heater thickness** | 0.14 | μm |
| **Heater offset** | 2.0 | μm |
| **Phase shifter length** | 320 | μm |
| **Wavelength** | 1.55 | μm |
| **Material** | Si core, TiN heater, SiO₂ cladding |

### Reference Data

Reference phase shift data extracted from Tidy3D `TransientThermoOpticShifter.ipynb`:
- Power range: 0 – 30 mW (5 points)
- P_π (Tidy3D): 23.9 mW
- Linear phase-power relationship

### Results

![Benchmark #1: TiN Metal Heater Comparison](results/benchmark1_comparison.png)

**Figure 1**: TiN metal heater phase shifter comparison between Tidy3D reference and Femwell MCP results.

### Performance Metrics

| Metric | Tidy3D | Femwell | Error |
|--------|--------|---------|-------|
| **P_π (mW)** | 23.90 | 0.00 | ❌ **-100%** |
| **Mean Absolute Error** | -- | 10.48 rad | ❌ **FAIL** |
| **Max Absolute Error** | -- | 14.58 rad | ❌ **FAIL** |
| **Mean Relative Error** | -- | 722% | ❌ **FAIL** |

### Status: ❌ **FAIL**

**Issue**: Femwell phase shift values are constant at 15.57 rad for all non-zero power levels, indicating a computational or configuration error. The tool does not correctly capture the linear phase-power relationship.

**Root Cause Analysis**:
- Phase shifts stuck at constant value (15.57 rad) for P > 0
- Power calculation issue: tool returns power per unit length, needs multiplication by device length
- Thermal-optical coupling may not be properly integrated

---

## Benchmark #2: Doped Silicon Heater Phase Shifter

### Overview

The doped silicon heater phase shifter uses N++ doped silicon regions as resistive heaters in a rib waveguide configuration. This design offers better thermal coupling compared to metal heaters.

### Device Configuration

| Parameter | Value | Unit |
|-----------|-------|------|
| **Core width** | 0.5 | μm |
| **Core height** | 0.22 | μm |
| **Slab height** | 0.09 | μm |
| **Slab width (each side)** | 0.8 | μm |
| **Heater width** | 1.0 | μm |
| **Phase shifter length** | 320 | μm |
| **Wavelength** | 1.55 | μm |
| **Material** | Si rib waveguide, N++ Si heaters |

### Reference Data

Reference phase shift data extracted from Tidy3D `TransientThermoOpticShifter.ipynb` (rib variant):
- Power range: 0 – 30 mW (5 points)
- P_π (Tidy3D): 25.2 mW
- Linear phase-power relationship

### Results

![Benchmark #2: Doped Silicon Heater Comparison](results/benchmark2_comparison.png)

**Figure 2**: Doped silicon heater phase shifter comparison between Tidy3D reference and Femwell MCP results.

### Performance Metrics

| Metric | Tidy3D | Femwell | Error |
|--------|--------|---------|-------|
| **P_π (mW)** | 25.20 | 24.40 | ✅ **-3.18%** |
| **Mean Absolute Error** | -- | 0.062 rad | ✅ **PASS** |
| **Max Absolute Error** | -- | 0.104 rad | ✅ **PASS** |
| **Mean Relative Error** | -- | 2.85% | ✅ **PASS** |

### Status: ✅ **PASS**

**Excellent agreement**. Femwell MCP tool successfully predicts P_π within 3.2% of Tidy3D reference. Phase shift linearity and magnitude show excellent correspondence. This validates the doped silicon heater implementation for thermo-optic phase shifter design.

---

## Benchmark #3: Waveguide Dispersion

### Overview

Waveguide dispersion characterization validates the mode solver's ability to compute effective index (n_eff) and group index (n_g) as a function of wavelength. This is fundamental to all other device simulations.

### Device Configuration

| Parameter | Value | Unit |
|-----------|-------|------|
| **Waveguide width** | 0.5 | μm |
| **Waveguide height** | 0.22 | μm |
| **Wavelength range** | 1.27 – 1.31 | μm |
| **Material** | Si core, SiO₂ cladding |
| **Number of points** | 11 | -- |

### Reference Data

Reference extracted from Tidy3D `wg_dispersion.ipynb`:
- Si strip waveguide: 0.5 × 0.22 μm
- Materials: Si (Palik_Lossless), SiO₂ cladding
- Mode solver: FEM

### Results

![Benchmark #3: Waveguide Dispersion Comparison](results/benchmark3_comparison.png)

**Figure 3**: Waveguide dispersion comparison between Tidy3D reference and Femwell MCP results.

### Performance Metrics

| Metric | Value |
|--------|-------|
| **Mean n_eff error** | < 0.1% |
| **Mean n_g error** | < 1% |
| **Status** | ✅ **PASS** |

### Status: ✅ **PASS**

Effective index and group index show excellent agreement across the wavelength range. Mean relative error < 1% validates the Femwell mode solver for waveguide dispersion calculations.

---

## Benchmark #4: PN Junction Depletion Modulator

### Overview

The PN junction depletion modulator uses carrier depletion/injection to modulate the waveguide effective index. This device is critical for high-speed optical modulators.

### Device Configuration

| Parameter | Value | Unit |
|-----------|-------|------|
| **Waveguide width** | 0.5 | μm |
| **Waveguide thickness** | 0.22 | μm |
| **Slab thickness** | 0.1 | μm |
| **Wavelength** | 2.0 | μm |
| **Doping (N_A = N_D)** | 10¹⁸ | cm⁻³ |
| **PN junction position** | 0.0 | μm |
| **Voltage range** | 0 – 1.2 | V |

### Reference Data

**⚠️ Note**: Reference data from Tidy3D `MachZehnderModulator.ipynb` is currently **PLACEHOLDER** data. Actual neff vs voltage values need to be extracted from notebook execution (cell 76).

### Results

![Benchmark #4: Depletion Modulator Comparison](../mcp_output/depletion_modulator_comparison.png)

**Figure 4**: PN junction depletion modulator comparison. **WARNING: Tidy3D data is placeholder, not actual notebook output.**

### Femwell Results

| Parameter | 0V | 1.0V | Change |
|-----------|-------|-------|--------|
| **Real(n_eff)** | 2.248858 | 2.248685 | -0.000174 |
| **Imag(n_eff) × 10⁴** | 1.48 | 1.61 | +0.13 |
| **Absorption (dB/cm)** | 40.46 | 44.03 | +3.57 |

### Key Observations

1. **Small modulation**: Δn_eff = -1.74 × 10⁻⁴ at 1.0V is 100× smaller than expected carrier injection values
2. **Numerical instability**: Sudden jump in neff and absorption drop at 1.1-1.2V suggests convergence issues
3. **Physics mismatch**: Femwell shows depletion behavior (decreasing neff), while Tidy3D notebook expects carrier injection (increasing neff)

### Status: ⚠️ **INCOMPLETE**

Cannot fully validate without actual Tidy3D reference data. Preliminary results suggest:
- Femwell tool runs successfully but shows unexpected physics
- Need actual neff values from Tidy3D notebook for quantitative comparison
- Possible physics model mismatch (depletion vs injection)

---

## Summary and Recommendations

### Validation Summary

| Benchmark | Device | Status | Key Metric Error |
|-----------|--------|--------|------------------|
| **#1** | TiN Metal Heater | ❌ **FAIL** | P_π error: -100% |
| **#2** | Doped Si Heater | ✅ **PASS** | P_π error: -3.2% |
| **#3** | Waveguide Dispersion | ✅ **PASS** | n_eff error: <1% |
| **#4** | Depletion Modulator | ⚠️ **INCOMPLETE** | Awaiting reference data |

### Key Findings

- ✅ **Success**: Doped silicon heater and waveguide dispersion tools show excellent agreement with Tidy3D
- ❌ **Issue**: TiN metal heater tool has a critical bug preventing correct phase shift calculation
- ⚠️ **Pending**: Depletion modulator needs actual Tidy3D reference data for validation

### Recommendations

#### Priority 1: Debug TiN Metal Heater Phase Shifter Tool

- Investigate why phase shifts are constant (15.57 rad) for non-zero power
- Check power calculation: verify total power vs power per unit length
- Review thermal-optical coupling implementation

#### Priority 2: Extract Actual Tidy3D Reference Data for Depletion Modulator

- Run `MachZehnderModulator.ipynb` through cell 76
- Extract `n_eff_freq0` array values (real and imaginary parts)
- Replace placeholder data in benchmark comparison

#### Priority 3: Investigate Depletion Modulator Physics Model

- Verify forward vs reverse bias configuration
- Check if Tidy3D uses carrier injection (forward) vs Femwell depletion (reverse)
- Align voltage polarity and physics assumptions

#### Priority 4: Extend Validation to Additional Devices

- Ring resonators
- Mach-Zehnder interferometers
- Directional couplers

### Validation Confidence

Based on 2 out of 3 completed benchmarks passing:

- **High confidence**: Waveguide dispersion, thermo-optic phase shifters (doped Si)
- **Low confidence**: Thermo-optic phase shifters (metal heater)
- **Unknown**: Electro-optic modulators (depletion/injection)

---

## Conclusion

The Femwell MCP validation campaign demonstrates strong performance for waveguide dispersion and doped silicon heater phase shifters, with errors well within acceptable tolerances (<5%). However, the TiN metal heater implementation requires immediate attention to resolve computational issues preventing accurate phase shift predictions.

The depletion modulator benchmark remains incomplete pending actual Tidy3D reference data extraction. Preliminary results suggest potential physics model mismatches that require careful investigation.

Overall, Femwell MCP shows promise as a rapid prototyping tool for photonic device simulation, with the caveat that each tool should be individually validated before use in production workflows.

---

## Appendix: Formulas and Definitions

### Phase Shift Calculation

Phase shift due to effective index change:

```
Δφ = (2π/λ) × Δn_eff × L
```

where λ is wavelength, Δn_eff is effective index change, and L is device length.

### Power for π Phase Shift

The power required to achieve π radians phase shift (P_π) is a key figure of merit:

```
P_π = power at Δφ = π
```

### Absorption Coefficient

Conversion from imaginary part of neff to absorption:

```
α [dB/cm] = (4π / λ ln(10)) × Im(n_eff) × 10⁴
```

### Thermal-Optic Coefficient

Temperature-induced index change:

```
Δn = (dn/dT) × ΔT
```

For silicon at 1.55 μm: dn/dT = 1.86 × 10⁻⁴ K⁻¹

---

## Data Files

All benchmark data files are available in the repository:

- `Benchmark/results/benchmark1_comparison.png`
- `Benchmark/results/benchmark1_report.md`
- `Benchmark/results/benchmark2_comparison.png`
- `Benchmark/results/benchmark2_report.md`
- `Benchmark/results/benchmark3_comparison.png`
- `Benchmark/results/benchmark3_report.md`
- `mcp_output/mzi_depletion_modulator_results.csv`
- `mcp_output/depletion_modulator_comparison.png`

---

**Report Generated**: 2025-10-24
**Validation Status**: 2/3 benchmarks passed, 1 failed, 1 incomplete
