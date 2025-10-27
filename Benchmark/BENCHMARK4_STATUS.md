# Benchmark #4: Carrier Injection Modulator - Implementation Complete

**Date**: 2025-10-23
**Status**: ✅ INFRASTRUCTURE READY - Awaiting Real Tidy3D Data

---

## Summary

Successfully implemented the complete benchmarking infrastructure for **Benchmark #4: Carrier Injection Modulator**. The system runs Femwell's depletion modulator simulation and compares it against Tidy3D reference data.

### Key Achievement

✅ **Fully automated benchmark workflow** from simulation → comparison → reporting

---

## Files Created

### 1. Benchmark Comparison Script
**File**: `Benchmark/benchmark_carrier_injection.py` (442 lines)

**Features**:
- Loads Femwell MCP tool results from CSV
- Compares against Tidy3D reference data
- Computes comprehensive error metrics:
  - Real(neff): mean/max absolute error, relative error %
  - Imag(neff): absorption comparison
  - Δneff: modulation efficiency error
- Generates 4-panel comparison plot with:
  1. Real(neff) vs Voltage
  2. Δneff vs Voltage (modulation efficiency)
  3. Absorption vs Voltage
  4. Error statistics summary
- Generates detailed markdown report
- Exports error data to CSV

**Special Feature**: Built-in placeholder data warning system

### 2. Workflow Automation Script
**File**: `Benchmark/run_benchmark4_carrier_injection.py` (136 lines)

**Features**:
- Step 1: Runs Femwell `compute_depletion_modulator()` with Tidy3D-matching parameters
- Step 2: Automatically calls comparison script
- Saves results to `mcp_output/depletion_modulator_results.csv`
- Error handling and progress reporting

---

## Simulation Results (Femwell)

### Configuration
- **Voltage sweep**: 0.0 to 1.2 V (13 points) - matches Tidy3D notebook
- **Wavelength**: 2.0 μm (IR operation)
- **Waveguide**: 0.5 × 0.22 μm strip with 0.1 μm slab
- **Doping**: NA = ND = 1e18 cm⁻³ (PN junction)

### Results
- **neff range**: 2.248685 to 2.250820
- **Δneff (0V → 1.2V)**: 0.001961
- **Absorption range**: 0 to 44 dB/cm (high at forward bias)

### Physics Observations
1. **Moderate modulation**: ~0.002 Δneff is reasonable for PN junction at 2 μm wavelength
2. **Absorption increases with voltage**: Expected behavior for forward bias carrier injection
3. **Note**: Femwell uses isothermal approximation (no Joule heating)

---

## Current Limitation: Placeholder Reference Data

⚠️ **The benchmark currently uses ESTIMATED Tidy3D reference values**, not real data from the notebook.

### Why Placeholder Data?

The MachZehnderModulator.ipynb notebook:
- Computes `n_eff_freq0` in cell 76 but only plots it (doesn't print)
- Output data is embedded in notebook execution state
- Extracting requires either:
  1. Re-running the notebook with Tidy3D cloud API
  2. Reading saved simulation results from Tidy3D servers
  3. Manual extraction from plot images

### What the Placeholder Assumes

Based on typical carrier injection behavior (estimated):
- **Real(neff)**: 2.4500 → 2.4692 (Δneff ≈ 0.02)
- **Imag(neff)**: 1e-4 → 1.25e-3 (exponential absorption increase)

### How to Replace with Real Data

1. **Run MachZehnderModulator.ipynb** up to cell 76
2. **Extract values**:
   ```python
   # From cell 76
   n_eff_freq0 = [md.n_complex.sel(f=freq0, mode_index=0).values
                  for _, md in ms_data.items()]

   print("Real(neff):", [np.real(x) for x in n_eff_freq0])
   print("Imag(neff):", [np.imag(x) for x in n_eff_freq0])
   ```

3. **Update** `TIDY3D_REFERENCE` dictionary in `benchmark_carrier_injection.py`:
   ```python
   "neff_real_tidy3d": np.array([...]),  # Replace with actual values
   "neff_imag_tidy3d": np.array([...]),  # Replace with actual values
   ```

4. **Re-run**: `python run_benchmark4_carrier_injection.py`

---

## Generated Outputs

All files saved to `Benchmark/results/`:

### 1. Comparison Plot
**File**: `benchmark4_comparison.png`

**4-panel layout**:
- Top-left: Real(neff) vs Voltage (Tidy3D vs Femwell)
- Top-right: Δneff vs Voltage (modulation efficiency)
- Bottom-left: Absorption vs Voltage
- Bottom-right: Error statistics summary

**Visual warnings**: Yellow "PLACEHOLDER DATA" labels on all plots

### 2. Detailed Report
**File**: `benchmark4_report.md`

**Contents**:
- Configuration parameters table
- Error metrics tables (real neff, absorption, modulation efficiency)
- Point-by-point comparison table (13 voltage points)
- Physics comparison notes
- Validation criteria assessment
- Next steps instructions

**Status**: [WARN] PLACEHOLDER DATA - Cannot validate

### 3. Error Data Export
**File**: `benchmark4_errors.csv`

**Columns**:
- voltage_V
- tidy3d_neff_real / femwell_neff_real
- absolute_error_real / relative_error_real_pct
- tidy3d_neff_imag / femwell_neff_imag
- absolute_error_imag
- delta_neff_tidy3d / delta_neff_femwell / delta_neff_error

---

## Comparison with Placeholder Data

### Current Error Metrics (Placeholder Comparison)

| Metric | Value | Notes |
|--------|-------|-------|
| **Mean Absolute Error (real)** | 0.208296 | Very large - due to placeholder |
| **Mean Relative Error (real)** | 8.48% | Exceeds 30% target - placeholder issue |
| **Mean Δneff Error** | 7.15e-03 | Large - placeholder assumes 10× larger Δneff |
| **Mean Absorption Error** | 3.74e-04 | Moderate |

**Conclusion**: These errors are **meaningless** until real Tidy3D data is used.

### Expected Error with Real Data

Based on Benchmark #4 documentation (TOP_4_BENCHMARKS.md):

| Metric | Expected Range | Reason |
|--------|---------------|--------|
| **Δneff error** | < 30% | Physics differences (isothermal vs multi-physics) |
| **Absorption trend** | Qualitative match | Both show increase with voltage |
| **I-V characteristics** | Qualitative match | PN junction forward bias |

**Note**: Femwell (isothermal) vs Tidy3D (charge + thermal) → expect 20-30% differences

---

## Technical Implementation Notes

### Function Import Path Fixed

Initial error:
```python
from axiomatic_mcp.servers.femwell.compute_depletion_modulator import compute_depletion_modulator
# ModuleNotFoundError
```

**Corrected**:
```python
from axiomatic_mcp.servers.femwell.tools.depletion_modulator import compute_depletion_modulator
```

### Return Value Handling

The `compute_depletion_modulator()` function returns:
```python
(voltages_array, neff_array, neff_change, absorption_dB_per_cm)
```

Where:
- `neff_array`: Complex array (real + imag)
- `neff_change`: Real part change from 0V
- `absorption_dB_per_cm`: Converted from imaginary part via k_to_alpha_dB

### CSV Format

Matches MCP server output format:
```
voltage_V,neff_real,neff_imag,neff_change,absorption_dB_per_cm
0.0,2.248685,0.000001,0.000000,0.019
0.1,2.248815,0.000003,0.000130,0.524
...
```

---

## Validation Criteria (From Benchmark Spec)

### Primary Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Δneff (0 to 1.2V)** | ±30% | Check modulation efficiency |
| **Absorption trend** | Increases with voltage | Qualitative match |
| **I-V curve shape** | Forward bias exponential | Qualitative match |
| **Phase shift linearity** | R² > 0.9 | Linear with power |

### Physics Comparison

| Feature | Tidy3D | Femwell |
|---------|--------|---------|
| **Charge transport** | Full P++-P-P++ solver | Analytical PN depletion |
| **Thermal effects** | Joule heating included | Isothermal approximation |
| **Optical perturbation** | Full-wave 3D FDTD | FEM mode solver + Δε |
| **Doping profile** | Asymmetric P++-P-P++ | Symmetric PN |

**Expected agreement**: 20-30% error due to simplified physics in Femwell

---

## Next Steps

### Immediate (Required for Validation)

1. ✅ Benchmark infrastructure complete
2. ⚠️ **PRIORITY**: Extract real Tidy3D reference data
   - Run MachZehnderModulator.ipynb (requires Tidy3D cloud API key)
   - Extract n_eff_freq0 from cell 76 outputs
   - Update TIDY3D_REFERENCE in benchmark_carrier_injection.py
3. 🔄 Re-run benchmark with real data
4. 📊 Analyze validation results

### Optional Enhancements

1. **Add I-V curve comparison** (if available in Tidy3D notebook)
2. **Add phase shift vs power plot** (compute from Δneff)
3. **Add carrier density distribution plot** (for visual validation)
4. **Automate Tidy3D data extraction** (parse notebook execution outputs)

---

## Integration with Benchmark System

### Status vs Other Benchmarks

| Benchmark | Status | Notes |
|-----------|--------|-------|
| **#3: Waveguide Dispersion** | ✅ Complete | Has real Tidy3D data, validated |
| **#4: Carrier Injection** | ⚠️ Infrastructure ready | Needs real Tidy3D data |
| **#1: TiN Metal Heater** | 📋 Planned | Similar to #3, should be straightforward |
| **#2: Doped Si Heater** | 📋 Planned | Similar to #1, reuse template |

### Benchmark Workflow Template

Benchmark #4 follows the same structure as Benchmark #3:

```python
# 1. Define REFERENCE data (from Tidy3D notebook)
TIDY3D_REFERENCE = {...}

# 2. Run Femwell simulation
def run_femwell_simulation():
    result = compute_tool_function(**params)
    save_to_csv(result)

# 3. Compute errors
def compute_errors(femwell_data, reference):
    errors = compute_all_metrics(...)
    return errors

# 4. Generate plots and reports
plot_comparison(errors, output_path)
generate_report(errors, output_path)
```

**Reusable for Benchmarks #1 and #2!**

---

## Summary of Achievement

### What Works Now ✅

1. **Automated Femwell simulation** - Runs depletion modulator with Tidy3D-matching params
2. **CSV data export** - Saves neff vs voltage results
3. **Error computation** - Comprehensive metrics (real, imag, Δneff)
4. **Comparison plots** - Professional 4-panel visualization
5. **Markdown reports** - Detailed validation documentation
6. **Placeholder warnings** - Clear indication of data status

### What's Missing ⚠️

1. **Real Tidy3D reference data** - Currently using estimated placeholders
2. **Validation assessment** - Cannot determine pass/fail without real data

### Time Investment

- **Infrastructure development**: ~2 hours
- **Debugging import paths**: 15 min
- **Testing and documentation**: 30 min
- **Total**: ~3 hours

### When Real Data is Available

- **Re-run time**: < 2 minutes
- **Validation analysis**: 5-10 minutes

---

## Conclusion

✅ **Benchmark #4 infrastructure is complete and working correctly.**

The benchmarking system successfully:
- Runs Femwell simulations with Tidy3D-matching parameters
- Generates comparison plots and detailed reports
- Provides clear warnings about placeholder data

**Next critical step**: Extract real neff vs voltage data from MachZehnderModulator.ipynb to enable actual validation.

Once real data is available, simply update the `TIDY3D_REFERENCE` dictionary and re-run the benchmark to get quantitative validation results.

---

**Implementation Date**: 2025-10-23
**Status**: Ready for real data validation
**Confidence**: High (infrastructure validated with placeholder data)
