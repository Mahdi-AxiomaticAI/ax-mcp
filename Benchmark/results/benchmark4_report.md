# Benchmark #4: Carrier Injection Modulator - Results

**Date**: 2025-10-23 19:35:06
**Status**: [WARN] PLACEHOLDER DATA - Cannot validate

---

## ⚠️ WARNING


================================================================================
  WARNING: Using PLACEHOLDER reference data!
================================================================================

The Tidy3D reference neff values in this benchmark are ESTIMATED based on
typical carrier injection behavior, NOT extracted from actual notebook outputs.

To get accurate benchmark results:
1. Run MachZehnderModulator.ipynb cells up to cell 76
2. Extract n_eff_freq0 array values
3. Replace TIDY3D_REFERENCE['neff_real_tidy3d'] and ['neff_imag_tidy3d']

Current values are for DEVELOPMENT/TESTING purposes only!
================================================================================


---

## Configuration

| Parameter | Value |
|-----------|-------|
| **Waveguide Width** | 0.5 um |
| **Waveguide Height** | 0.34 um |
| **Slab Thickness** | 0.1 um |
| **Doping Concentration** | 1.0e+18 cm^-3 |
| **Wavelength** | 2.0 um |
| **Voltage Range** | 0.0 - 1.2 V |
| **Number of Points** | 13 |

---

## Error Metrics

### Real Part of neff

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Absolute Error** | 0.208296 | < 0.01 | [WARN] |
| **Max Absolute Error** | 0.218380 | < 0.02 | [WARN] |
| **Mean Relative Error** | 8.48% | < 1.0% | [WARN] |

### Imaginary Part (Absorption)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Absolute Error** | 3.74e-04 | < 1e-4 | [WARN] |
| **Max Absolute Error** | 1.25e-03 | < 5e-4 | [WARN] |

### Modulation Efficiency (Δneff)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Δneff Error** | 7.1544e-03 | < 1e-3 (30% of typical Δneff) | [FAIL] |
| **Max Δneff Error** | 1.7239e-02 | < 2e-3 | [WARN] |

---

## Detailed Results

| Voltage (V) | Tidy3D Re[neff] | Femwell Re[neff] | Abs Error | Rel Error (%) | Tidy3D Im[neff] | Femwell Im[neff] |
|-------------|-----------------|------------------|-----------|---------------|-----------------|------------------|
| 0.00 | 2.450000 | 2.248858 | -0.201142 | -8.21 | 1.00e-04 | 1.48e-04 |
| 0.10 | 2.450500 | 2.248850 | -0.201650 | -8.23 | 1.20e-04 | 1.49e-04 |
| 0.20 | 2.451200 | 2.248840 | -0.202360 | -8.26 | 1.50e-04 | 1.50e-04 |
| 0.30 | 2.452100 | 2.248831 | -0.203269 | -8.29 | 1.90e-04 | 1.50e-04 |
| 0.40 | 2.453200 | 2.248814 | -0.204386 | -8.33 | 2.40e-04 | 1.52e-04 |
| 0.50 | 2.454500 | 2.248795 | -0.205705 | -8.38 | 3.00e-04 | 1.53e-04 |
| 0.60 | 2.456000 | 2.248788 | -0.207212 | -8.44 | 3.80e-04 | 1.54e-04 |
| 0.70 | 2.457700 | 2.248771 | -0.208929 | -8.50 | 4.70e-04 | 1.55e-04 |
| 0.80 | 2.459600 | 2.248754 | -0.210846 | -8.57 | 5.80e-04 | 1.56e-04 |
| 0.90 | 2.461700 | 2.248726 | -0.212974 | -8.65 | 7.10e-04 | 1.58e-04 |
| 1.00 | 2.464000 | 2.248685 | -0.215315 | -8.74 | 8.60e-04 | 1.61e-04 |
| 1.10 | 2.466500 | 2.250820 | -0.215680 | -8.74 | 1.04e-03 | -3.95e-16 |
| 1.20 | 2.469200 | 2.250820 | -0.218380 | -8.84 | 1.25e-03 | -7.63e-16 |

---

## Summary

Femwell MCP tool **validation pending** against Tidy3D reference data.

- **Agreement Level**: Pending (placeholder data)
- **Overall Assessment**: [WARN] PLACEHOLDER DATA - Cannot validate

### Physics Comparison:
- **Tidy3D**: Full multi-physics (charge transport + thermal + optical perturbation)
- **Femwell**: Simplified carrier-induced index perturbation (isothermal)
- **Expected Difference**: 20-30% due to different physics models

### Validation Criteria:
- [CHECK] Mean Δneff error < 30% → **PENDING**
- [CHECK] Qualitative agreement in neff vs V trend → **PENDING**
- [CHECK] Absorption increases with voltage → **PENDING**

---

## Files Generated

- `benchmark4_comparison.png` - Comparison plots
- `benchmark4_report.md` - This report
- `benchmark4_errors.csv` - Detailed error data

---

## Next Steps

- **PRIORITY**: Replace placeholder data with actual Tidy3D outputs
- Extract n_eff_freq0 from MachZehnderModulator.ipynb cell 76
- Re-run benchmark with real reference data
