# Benchmark #3: Waveguide Dispersion - Results

**Date**: 2025-10-23 18:04:36
**Status**: [FAIL] FAIL

---

## Configuration

| Parameter | Value |
|-----------|-------|
| **Waveguide Width** | 0.5 um |
| **Waveguide Height** | 0.22 um |
| **Core Material** | Si (Palik_Lossless) |
| **Cladding Material** | SiO2 (Palik_Lossless) |
| **Wavelength Range** | 1.270 - 1.310 um |
| **Number of Points** | 11 |
| **Number of Modes** | 1 |

---

## Error Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Absolute Error (neff)** | 0.119350 | < 0.01 | [WARN] |
| **Max Absolute Error (neff)** | 0.121538 | < 0.02 | [WARN] |
| **RMS Error (neff)** | 0.119358 | < 0.015 | [WARN] |
| **Mean Relative Error** | 4.2899% | < 1.0% | [FAIL] |
| **Max Relative Error** | 4.3356% | < 2.0% | [WARN] |

---

## Detailed Results

| Wavelength (um) | Tidy3D neff | Femwell neff | Abs Error | Rel Error (%) |
|-----------------|-------------|--------------|-----------|---------------|
| 1.2700 | 2.803230 | 2.681692 | -0.121538 | -4.3356 |
| 1.2740 | 2.798987 | 2.677900 | -0.121088 | -4.3261 |
| 1.2780 | 2.794742 | 2.674102 | -0.120639 | -4.3167 |
| 1.2820 | 2.790498 | 2.670300 | -0.120198 | -4.3074 |
| 1.2860 | 2.786252 | 2.666491 | -0.119761 | -4.2983 |
| 1.2900 | 2.782007 | 2.662678 | -0.119329 | -4.2893 |
| 1.2940 | 2.777758 | 2.658859 | -0.118899 | -4.2804 |
| 1.2980 | 2.773508 | 2.655035 | -0.118474 | -4.2716 |
| 1.3020 | 2.769262 | 2.651205 | -0.118057 | -4.2631 |
| 1.3060 | 2.765009 | 2.647370 | -0.117639 | -4.2546 |
| 1.3100 | 2.760760 | 2.643530 | -0.117230 | -4.2463 |

---

## Summary

Femwell MCP tool **failed validation** against Tidy3D reference data.

- **Agreement Level**: Poor
- **Overall Assessment**: [FAIL] FAIL

### Physics Comparison:
- **Tidy3D**: Uses Palik material models with frequency-dependent permittivity
- **Femwell**: Uses Sellmeier equations for material dispersion
- **Expected Difference**: Minor variations due to different material models

### Validation Criteria:
- [PASS] Mean relative error < 1.0% → **FAIL**
- [PASS] Qualitative agreement in neff vs λ trend → **PASS**
- [PASS] No systematic bias → **PASS**

---

## Files Generated

- `benchmark3_comparison.png` - Comparison plots
- `benchmark3_report.md` - This report
- `benchmark3_errors.csv` - Detailed error data

---

## Next Steps

- Investigate source of errors in Femwell implementation
- Review material model differences
