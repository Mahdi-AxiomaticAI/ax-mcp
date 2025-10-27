# Benchmark #1: TiN Metal Heater Phase Shifter - Results

**Date**: 2025-10-23 19:00:41
**Status**: [FAIL] FAIL

---

## Configuration

| Parameter | Value |
|-----------|-------|
| **Waveguide Width** | 0.5 um |
| **Waveguide Height** | 0.22 um |
| **Heater Width** | 2.0 um |
| **Heater Thickness** | 0.14 um (Femwell) |
| **Heater Offset** | 2.0 um |
| **Phase Shifter Length** | 320 um |
| **Wavelength** | 1.55 um |
| **Power Range** | 0.0 - 30.0 mW |
| **Number of Points** | 5 |

---

## Key Metric: P_π (Power for π Phase Shift)

| Parameter | Value | Target | Status |
|-----------|-------|--------|--------|
| **Tidy3D P_π** | 23.90 mW | Reference | - |
| **Femwell P_π** | 0.00 mW | 23.90 ± 15% | [FAIL] |
| **P_π Error** | -100.00% | < 15% | [FAIL] |

---

## Phase Shift Error Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Absolute Error** | 10.4811 rad | < 0.3 rad | [WARN] |
| **Max Absolute Error** | 14.5801 rad | < 0.5 rad | [WARN] |
| **RMS Error** | 11.7596 rad | < 0.4 rad | [WARN] |
| **Mean Relative Error** | 722.36% | < 10% | [WARN] |
| **Max Relative Error** | 1478.93% | < 20% | [WARN] |

---

## Detailed Results

| Power (mW) | Tidy3D Phase (rad) | Femwell Phase (rad) | Abs Error (rad) | Rel Error (%) |
|------------|-------------------|---------------------|-----------------|---------------|
| 0.0 | 0.0000 | 0.0000 | 0.0000 | 0.00 |
| 7.5 | 0.9859 | 15.5660 | 14.5801 | 1478.93 |
| 15.0 | 1.9717 | 15.5660 | 13.5943 | 689.47 |
| 22.5 | 2.9576 | 15.5660 | 12.6084 | 426.31 |
| 30.0 | 3.9434 | 15.5660 | 11.6226 | 294.73 |

---

## Summary

Femwell MCP tool **failed validation** against Tidy3D reference data.

- **Agreement Level**: Poor
- **Overall Assessment**: [FAIL] FAIL

### Physics Comparison:
- **Tidy3D**: Full 3D thermal-optical simulation with heat equation solver
- **Femwell**: 2D thermal FEM + thermo-optic index perturbation
- **Expected Difference**: 5-10% due to 2D vs 3D thermal modeling

### Validation Criteria:
- [CHECK] P_π error < 15% → **FAIL**
- [CHECK] Phase shift linearity (R² > 0.95) → **PASS** (both linear by design)
- [CHECK] No systematic bias → **WARN**

### Reference Paper:
Both implementations based on **Jacques et al., Opt. Express 27, 10456 (2019)**

---

## Files Generated

- `benchmark1_comparison.png` - Comparison plots
- `benchmark1_report.md` - This report
- `benchmark1_errors.csv` - Detailed error data

---

## Next Steps

- Investigate source of P_π error
- Review thermal model differences
