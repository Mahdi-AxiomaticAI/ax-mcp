"""Run Benchmark #3: Waveguide Dispersion

This script calls the Femwell MCP tool and then runs the benchmark comparison.
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path to import Femwell tool
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiomatic_mcp.servers.femwell.tools.waveguide_dispersion import compute_waveguide_dispersion

def run_femwell_simulation():
    """Run Femwell waveguide dispersion simulation with Tidy3D-matching parameters."""
    print("="*70)
    print("RUNNING FEMWELL MCP TOOL: simulate_waveguide_dispersion")
    print("="*70)

    # Parameters matching Tidy3D notebook
    wavelengths = np.linspace(1.270, 1.310, 11)

    print("\nParameters:")
    print(f"  Core material: Si")
    print(f"  Box material: SiO2")
    print(f"  Clad material: SiO2")
    print(f"  Waveguide width: 0.5 um")
    print(f"  Waveguide height: 0.22 um")
    print(f"  Wavelengths: {wavelengths[0]:.3f} - {wavelengths[-1]:.3f} um ({len(wavelengths)} points)")
    print(f"  Number of modes: 1")

    print("\nRunning simulation...")

    try:
        # Run Femwell simulation
        wavelengths_array, neffs, ng_array, gvd_array, te_fracs = compute_waveguide_dispersion(
            wavelengths=wavelengths.tolist(),
            w_core=0.5,
            h_core=0.22,
            core_material="Si",
            box_material="SiO2",
            clad_material="SiO2",
            num_modes=1,
            polynomial_degree=4,
        )

        print("\n[OK] Simulation completed successfully!")
        print(f"  Number of wavelength points: {len(wavelengths_array)}")
        print(f"  neff range: {min(neffs[:, 0]):.6f} to {max(neffs[:, 0]):.6f}")
        print(f"  ng range: {min(ng_array[:, 0]):.6f} to {max(ng_array[:, 0]):.6f}")

        # Save results to CSV (matching MCP tool output format)
        import pandas as pd
        from pathlib import Path

        output_dir = Path("mcp_output")
        output_dir.mkdir(exist_ok=True)

        # Create DataFrame with results
        df_rows = []
        for i in range(len(wavelengths_array)):
            for mode_idx in range(neffs.shape[1]):
                df_rows.append({
                    'wavelength_um': wavelengths_array[i],
                    'mode_index': mode_idx,
                    'neff_real': neffs[i, mode_idx],
                    'neff_imag': 0.0,  # Femwell doesn't compute imaginary part for lossless
                    'n_group': ng_array[i, mode_idx],
                    'gvd_ps_nm_km': gvd_array[i, mode_idx],
                    'te_fraction': te_fracs[i, mode_idx],
                })

        df = pd.DataFrame(df_rows)
        output_csv = output_dir / "wg_dispersion_data.csv"
        df.to_csv(output_csv, index=False)

        print(f"\n[OK] Results saved to: {output_csv}")

        return True

    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_benchmark():
    """Run the benchmark comparison."""
    print("\n" + "="*70)
    print("RUNNING BENCHMARK COMPARISON")
    print("="*70)

    # Import and run benchmark script
    import subprocess
    import os
    benchmark_script = Path(__file__).parent / "benchmark_waveguide_dispersion.py"
    result = subprocess.run(
        [sys.executable, str(benchmark_script)],
        capture_output=False,
        cwd=Path(__file__).parent.parent  # Run from repo root
    )

    return result.returncode == 0

def main():
    """Main workflow."""
    print("\n" + "="*70)
    print("  BENCHMARK #3: WAVEGUIDE DISPERSION")
    print("  Femwell vs Tidy3D Validation")
    print("="*70 + "\n")

    # Step 1: Run Femwell simulation
    print("STEP 1: Run Femwell MCP Tool")
    print("-" * 70)
    success = run_femwell_simulation()

    if not success:
        print("\n[ERROR] Femwell simulation failed. Cannot proceed with benchmark.")
        return 1

    # Step 2: Run benchmark comparison
    print("\n\nSTEP 2: Compare Results Against Tidy3D Reference")
    print("-" * 70)
    success = run_benchmark()

    if success:
        print("\n\n" + "="*70)
        print("  [SUCCESS] BENCHMARK #3 COMPLETE!")
        print("  Check Benchmark/results/ for detailed reports")
        print("="*70 + "\n")
        return 0
    else:
        print("\n\n[ERROR] Benchmark comparison failed.")
        return 1

if __name__ == "__main__":
    exit(main())
