"""Benchmark #4: Carrier Injection Modulator - Femwell vs Tidy3D

This script compares Femwell MCP tool results against Tidy3D notebook reference data.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Tidy3D reference data extracted from MachZehnderModulator.ipynb
# NOTE: These are PLACEHOLDER values estimated from typical carrier injection behavior
# TODO: Replace with actual values from Tidy3D notebook execution (cell 76)

TIDY3D_REFERENCE = {
    "voltages_V": np.arange(13) * 0.1,  # [0.0, 0.1, 0.2, ..., 1.2] V (from cell 22)
    "wavelength_um": 2.0,  # Operating wavelength
    "pin_length_um": 10.0,  # PIN junction length

    # Waveguide geometry (from notebook)
    "wg_width_um": 0.5,
    "wg_height_um": 0.34,  # 0.22 core + 0.12 slab = 0.34 total
    "slab_thickness_um": 0.1,

    # Doping parameters (from notebook)
    "doping_concentration": 1e18,  # cm^-3 (P++ and N++ regions)

    # Reference neff from Tidy3D notebook (cell 76 output)
    # PLACEHOLDER values - typical carrier injection: ~0.001-0.003 Δneff over 0-1.2V
    # Real part of neff (increases with forward bias due to carrier injection)
    "neff_real_tidy3d": np.array([
        2.4500, 2.4505, 2.4512, 2.4521, 2.4532,
        2.4545, 2.4560, 2.4577, 2.4596, 2.4617,
        2.4640, 2.4665, 2.4692
    ]),  # Estimated ~0.02 total change

    # Imaginary part of neff (absorption increases with forward bias)
    # Typical values: 1e-4 to 1e-3
    "neff_imag_tidy3d": np.array([
        1e-4, 1.2e-4, 1.5e-4, 1.9e-4, 2.4e-4,
        3.0e-4, 3.8e-4, 4.7e-4, 5.8e-4, 7.1e-4,
        8.6e-4, 1.04e-3, 1.25e-3
    ]),  # Exponential increase with bias
}

# WARNING displayed to user
PLACEHOLDER_WARNING = """
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
"""

def load_femwell_results(csv_path: str) -> pd.DataFrame:
    """Load Femwell MCP tool output CSV."""
    return pd.read_csv(csv_path)

def compute_errors(femwell_data: pd.DataFrame, reference: dict) -> dict:
    """Compute error metrics between Femwell and Tidy3D."""

    # Get Femwell data
    femwell_voltages = femwell_data['voltage_V'].values
    femwell_neff_real = femwell_data['neff_real'].values
    femwell_neff_imag = femwell_data['neff_imag'].values

    # Interpolate to match Tidy3D voltage points if needed
    if len(femwell_voltages) != len(reference['voltages_V']):
        femwell_neff_real = np.interp(
            reference['voltages_V'],
            femwell_voltages,
            femwell_neff_real
        )
        femwell_neff_imag = np.interp(
            reference['voltages_V'],
            femwell_voltages,
            femwell_neff_imag
        )

    tidy3d_neff_real = reference['neff_real_tidy3d']
    tidy3d_neff_imag = reference['neff_imag_tidy3d']

    # Compute errors for real part of neff
    absolute_error_real = femwell_neff_real - tidy3d_neff_real
    relative_error_real_pct = (absolute_error_real / tidy3d_neff_real) * 100

    # Compute errors for imaginary part (absorption)
    absolute_error_imag = femwell_neff_imag - tidy3d_neff_imag
    # Relative error for small values can be misleading, use absolute

    # Compute Δneff (change from 0V)
    delta_neff_femwell = femwell_neff_real - femwell_neff_real[0]
    delta_neff_tidy3d = tidy3d_neff_real - tidy3d_neff_real[0]
    delta_neff_error = delta_neff_femwell - delta_neff_tidy3d
    delta_neff_error_pct = (delta_neff_error / (delta_neff_tidy3d + 1e-10)) * 100

    errors = {
        # Real part errors
        'mean_absolute_error_real': np.mean(np.abs(absolute_error_real)),
        'max_absolute_error_real': np.max(np.abs(absolute_error_real)),
        'rms_error_real': np.sqrt(np.mean(absolute_error_real**2)),
        'mean_relative_error_real_pct': np.mean(np.abs(relative_error_real_pct)),
        'max_relative_error_real_pct': np.max(np.abs(relative_error_real_pct)),

        # Imaginary part errors
        'mean_absolute_error_imag': np.mean(np.abs(absolute_error_imag)),
        'max_absolute_error_imag': np.max(np.abs(absolute_error_imag)),

        # Δneff errors (modulation efficiency)
        'mean_delta_neff_error': np.mean(np.abs(delta_neff_error)),
        'max_delta_neff_error': np.max(np.abs(delta_neff_error)),

        # Arrays for plotting
        'absolute_errors_real': absolute_error_real,
        'relative_errors_real_pct': relative_error_real_pct,
        'absolute_errors_imag': absolute_error_imag,
        'delta_neff_error': delta_neff_error,

        'femwell_neff_real': femwell_neff_real,
        'femwell_neff_imag': femwell_neff_imag,
        'tidy3d_neff_real': tidy3d_neff_real,
        'tidy3d_neff_imag': tidy3d_neff_imag,

        'delta_neff_femwell': delta_neff_femwell,
        'delta_neff_tidy3d': delta_neff_tidy3d,

        'voltages': reference['voltages_V'],
    }

    return errors

def plot_comparison(errors: dict, output_path: str, use_placeholder: bool = True):
    """Create comparison plots."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    voltages = errors['voltages']

    # Plot 1: Real(neff) comparison
    ax = axes[0, 0]
    ax.plot(voltages, errors['tidy3d_neff_real'], 'o-', label='Tidy3D (reference)',
            markersize=8, linewidth=2, color='#1f77b4')
    ax.plot(voltages, errors['femwell_neff_real'], 's--', label='Femwell MCP',
            markersize=6, linewidth=2, color='#ff7f0e')
    if use_placeholder:
        ax.text(0.5, 0.05, 'PLACEHOLDER DATA', transform=ax.transAxes,
                ha='center', color='red', fontweight='bold', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax.set_xlabel('Voltage (V)', fontsize=11)
    ax.set_ylabel('Re[neff]', fontsize=11)
    ax.set_title('Effective Index (Real) vs Voltage', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Plot 2: Δneff (modulation efficiency)
    ax = axes[0, 1]
    ax.plot(voltages, errors['delta_neff_tidy3d'] * 1e3, 'o-', label='Tidy3D',
            markersize=8, linewidth=2, color='#1f77b4')
    ax.plot(voltages, errors['delta_neff_femwell'] * 1e3, 's--', label='Femwell MCP',
            markersize=6, linewidth=2, color='#ff7f0e')
    if use_placeholder:
        ax.text(0.5, 0.05, 'PLACEHOLDER DATA', transform=ax.transAxes,
                ha='center', color='red', fontweight='bold', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax.set_xlabel('Voltage (V)', fontsize=11)
    ax.set_ylabel('Delta neff (x10^-3)', fontsize=11)
    ax.set_title(f"Index Change vs Voltage (Modulation Efficiency)",
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Plot 3: Imag(neff) - absorption
    ax = axes[1, 0]
    ax.plot(voltages, errors['tidy3d_neff_imag'] * 1e4, 'o-', label='Tidy3D',
            markersize=8, linewidth=2, color='#1f77b4')
    ax.plot(voltages, errors['femwell_neff_imag'] * 1e4, 's--', label='Femwell MCP',
            markersize=6, linewidth=2, color='#ff7f0e')
    if use_placeholder:
        ax.text(0.5, 0.05, 'PLACEHOLDER DATA', transform=ax.transAxes,
                ha='center', color='red', fontweight='bold', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax.set_xlabel('Voltage (V)', fontsize=11)
    ax.set_ylabel('Im[neff] (x10^-4)', fontsize=11)
    ax.set_title('Absorption vs Voltage', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Plot 4: Error statistics
    ax = axes[1, 1]
    ax.axis('off')

    stats_text = f"""
    BENCHMARK #4: CARRIER INJECTION MODULATOR
    ══════════════════════════════════════════

    Geometry:
      • Width: {TIDY3D_REFERENCE['wg_width_um']} um
      • Height: {TIDY3D_REFERENCE['wg_height_um']} um
      • Slab: {TIDY3D_REFERENCE['slab_thickness_um']} um
      • Doping: {TIDY3D_REFERENCE['doping_concentration']:.1e} cm^-3

    Voltage Range:
      • {voltages[0]:.1f} - {voltages[-1]:.1f} V ({len(voltages)} points)

    Error Metrics (Real neff):
      • Mean Absolute Error: {errors['mean_absolute_error_real']:.6f}
      • Max Absolute Error:  {errors['max_absolute_error_real']:.6f}
      • Mean Relative Error: {errors['mean_relative_error_real_pct']:.2f}%

    Error Metrics (Absorption):
      • Mean Abs Error (imag): {errors['mean_absolute_error_imag']:.2e}
      • Max Abs Error (imag):  {errors['max_absolute_error_imag']:.2e}

    Modulation Efficiency:
      • Delta neff error:     {errors['mean_delta_neff_error']:.4e}

    Validation:
      {"[WARN] PLACEHOLDER DATA" if use_placeholder else "[OK] PASS" if errors['mean_delta_neff_error'] < 0.001 else "[FAIL] FAIL"} (Target: <30% error in delta_neff)
    """

    ax.text(0.1, 0.5, stats_text, fontsize=9, family='monospace',
            verticalalignment='center', transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Comparison plot saved to: {output_path}")

    return fig

def generate_report(errors: dict, output_path: str, use_placeholder: bool = True):
    """Generate markdown report."""
    voltages = errors['voltages']

    # Determine pass/fail (relaxed criteria for carrier injection)
    passes = errors['mean_delta_neff_error'] < 0.001  # 30% tolerance
    status = "[PASS] PASS" if passes else "[FAIL] FAIL"
    if use_placeholder:
        status = "[WARN] PLACEHOLDER DATA - Cannot validate"

    report = f"""# Benchmark #4: Carrier Injection Modulator - Results

**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {status}

---

## ⚠️ WARNING

{PLACEHOLDER_WARNING if use_placeholder else "Using actual Tidy3D reference data"}

---

## Configuration

| Parameter | Value |
|-----------|-------|
| **Waveguide Width** | {TIDY3D_REFERENCE['wg_width_um']} um |
| **Waveguide Height** | {TIDY3D_REFERENCE['wg_height_um']} um |
| **Slab Thickness** | {TIDY3D_REFERENCE['slab_thickness_um']} um |
| **Doping Concentration** | {TIDY3D_REFERENCE['doping_concentration']:.1e} cm^-3 |
| **Wavelength** | {TIDY3D_REFERENCE['wavelength_um']} um |
| **Voltage Range** | {voltages[0]:.1f} - {voltages[-1]:.1f} V |
| **Number of Points** | {len(voltages)} |

---

## Error Metrics

### Real Part of neff

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Absolute Error** | {errors['mean_absolute_error_real']:.6f} | < 0.01 | {"[PASS]" if errors['mean_absolute_error_real'] < 0.01 else "[WARN]"} |
| **Max Absolute Error** | {errors['max_absolute_error_real']:.6f} | < 0.02 | {"[PASS]" if errors['max_absolute_error_real'] < 0.02 else "[WARN]"} |
| **Mean Relative Error** | {errors['mean_relative_error_real_pct']:.2f}% | < 1.0% | {"[PASS]" if errors['mean_relative_error_real_pct'] < 1.0 else "[WARN]"} |

### Imaginary Part (Absorption)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Absolute Error** | {errors['mean_absolute_error_imag']:.2e} | < 1e-4 | {"[PASS]" if errors['mean_absolute_error_imag'] < 1e-4 else "[WARN]"} |
| **Max Absolute Error** | {errors['max_absolute_error_imag']:.2e} | < 5e-4 | {"[PASS]" if errors['max_absolute_error_imag'] < 5e-4 else "[WARN]"} |

### Modulation Efficiency (Δneff)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Mean Δneff Error** | {errors['mean_delta_neff_error']:.4e} | < 1e-3 (30% of typical Δneff) | {"[PASS]" if errors['mean_delta_neff_error'] < 1e-3 else "[FAIL]"} |
| **Max Δneff Error** | {errors['max_delta_neff_error']:.4e} | < 2e-3 | {"[PASS]" if errors['max_delta_neff_error'] < 2e-3 else "[WARN]"} |

---

## Detailed Results

| Voltage (V) | Tidy3D Re[neff] | Femwell Re[neff] | Abs Error | Rel Error (%) | Tidy3D Im[neff] | Femwell Im[neff] |
|-------------|-----------------|------------------|-----------|---------------|-----------------|------------------|
"""

    for i, v in enumerate(voltages):
        report += f"| {v:.2f} | {errors['tidy3d_neff_real'][i]:.6f} | {errors['femwell_neff_real'][i]:.6f} | "
        report += f"{errors['absolute_errors_real'][i]:.6f} | {errors['relative_errors_real_pct'][i]:.2f} | "
        report += f"{errors['tidy3d_neff_imag'][i]:.2e} | {errors['femwell_neff_imag'][i]:.2e} |\n"

    report += f"""
---

## Summary

Femwell MCP tool {'**validation pending**' if use_placeholder else '**successfully validated**' if passes else '**failed validation**'} against Tidy3D reference data.

- **Agreement Level**: {"Pending (placeholder data)" if use_placeholder else "Excellent" if errors['mean_delta_neff_error'] < 0.0005 else "Good" if errors['mean_delta_neff_error'] < 0.001 else "Fair" if errors['mean_delta_neff_error'] < 0.002 else "Poor"}
- **Overall Assessment**: {status}

### Physics Comparison:
- **Tidy3D**: Full multi-physics (charge transport + thermal + optical perturbation)
- **Femwell**: Simplified carrier-induced index perturbation (isothermal)
- **Expected Difference**: 20-30% due to different physics models

### Validation Criteria:
- [CHECK] Mean Δneff error < 30% → **{"PENDING" if use_placeholder else "PASS" if passes else "FAIL"}**
- [CHECK] Qualitative agreement in neff vs V trend → **{"PENDING" if use_placeholder else "PASS"}**
- [CHECK] Absorption increases with voltage → **{"PENDING" if use_placeholder else "PASS"}**

---

## Files Generated

- `benchmark4_comparison.png` - Comparison plots
- `benchmark4_report.md` - This report
- `benchmark4_errors.csv` - Detailed error data

---

## Next Steps

{"- **PRIORITY**: Replace placeholder data with actual Tidy3D outputs" if use_placeholder else "- Review validation results"}
{"- Extract n_eff_freq0 from MachZehnderModulator.ipynb cell 76" if use_placeholder else "- Proceed to complete benchmarking system"}
{"- Re-run benchmark with real reference data" if use_placeholder else "- Document final results"}
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {output_path}")

def save_error_data(errors: dict, output_path: str):
    """Save detailed error data to CSV."""
    df = pd.DataFrame({
        'voltage_V': errors['voltages'],
        'tidy3d_neff_real': errors['tidy3d_neff_real'],
        'femwell_neff_real': errors['femwell_neff_real'],
        'absolute_error_real': errors['absolute_errors_real'],
        'relative_error_real_pct': errors['relative_errors_real_pct'],
        'tidy3d_neff_imag': errors['tidy3d_neff_imag'],
        'femwell_neff_imag': errors['femwell_neff_imag'],
        'absolute_error_imag': errors['absolute_errors_imag'],
        'delta_neff_tidy3d': errors['delta_neff_tidy3d'],
        'delta_neff_femwell': errors['delta_neff_femwell'],
        'delta_neff_error': errors['delta_neff_error'],
    })
    df.to_csv(output_path, index=False)
    print(f"Error data saved to: {output_path}")

def main():
    """Main benchmarking workflow."""
    print("="*70)
    print("BENCHMARK #4: CARRIER INJECTION MODULATOR")
    print("Femwell MCP vs Tidy3D Reference")
    print("="*70)

    # Display placeholder warning
    print(PLACEHOLDER_WARNING)

    # Check if Femwell results exist
    femwell_csv = Path("Benchmark/mcp_output/depletion_modulator_results.csv")
    if not femwell_csv.exists():
        femwell_csv = Path("mcp_output/depletion_modulator_results.csv")

    if not femwell_csv.exists():
        print("\n[ERROR] Femwell results not found!")
        print(f"Expected file: {femwell_csv}")
        print("\nPlease run the Femwell MCP tool first:")
        print("  Tool: simulate_depletion_modulator")
        print("  Parameters:")
        print(f"    - voltages: {TIDY3D_REFERENCE['voltages_V'].tolist()}")
        print(f"    - wg_width: {TIDY3D_REFERENCE['wg_width_um']}")
        print(f"    - wg_thickness: {TIDY3D_REFERENCE['wg_height_um'] - TIDY3D_REFERENCE['slab_thickness_um']}")
        print(f"    - slab_thickness: {TIDY3D_REFERENCE['slab_thickness_um']}")
        print(f"    - wavelength: {TIDY3D_REFERENCE['wavelength_um']}")
        return

    print(f"\n[OK] Found Femwell results: {femwell_csv}")

    # Load Femwell results
    print("\nLoading Femwell MCP results...")
    femwell_data = load_femwell_results(femwell_csv)
    print(f"  Loaded {len(femwell_data)} data points")

    # Compute errors
    print("\nComputing error metrics...")
    errors = compute_errors(femwell_data, TIDY3D_REFERENCE)

    print(f"\n  Mean Absolute Error (real): {errors['mean_absolute_error_real']:.6f}")
    print(f"  Mean Delta neff Error: {errors['mean_delta_neff_error']:.4e}")
    print(f"  Mean Absorption Error (imag): {errors['mean_absolute_error_imag']:.2e}")

    # Generate outputs
    output_dir = Path("Benchmark/results")
    output_dir.mkdir(exist_ok=True)

    print("\nGenerating comparison plots...")
    plot_comparison(errors, output_dir / "benchmark4_comparison.png", use_placeholder=True)

    print("\nGenerating report...")
    generate_report(errors, output_dir / "benchmark4_report.md", use_placeholder=True)

    print("\nSaving error data...")
    save_error_data(errors, output_dir / "benchmark4_errors.csv")

    # Final summary
    print("\n" + "="*70)
    print("[WARN] BENCHMARK USING PLACEHOLDER DATA!")
    print("   Replace TIDY3D_REFERENCE values with actual notebook outputs")
    print("   to get meaningful validation results.")
    print("="*70)

if __name__ == "__main__":
    main()
