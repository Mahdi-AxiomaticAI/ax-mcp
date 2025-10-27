"""Benchmark #4: Carrier Injection Modulator - Full Workflow

This script:
1. Runs Femwell MCP tool (simulate_depletion_modulator)
2. Runs benchmark comparison against Tidy3D reference
3. Generates comparison plots and reports

Usage:
    python run_benchmark4_carrier_injection.py
"""

import sys
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiomatic_mcp.servers.femwell.tools.depletion_modulator import compute_depletion_modulator

# Tidy3D-matching parameters from MachZehnderModulator.ipynb
SIMULATION_PARAMS = {
    # Voltage sweep (from notebook cell 22)
    "voltages": list(np.arange(13) * 0.1),  # [0.0, 0.1, ..., 1.2] V

    # Waveguide geometry (from notebook)
    "wg_width": 0.5,  # um
    "wg_thickness": 0.22,  # um (core only, without slab)
    "slab_width": 3.0,  # um
    "slab_thickness": 0.1,  # um
    "clad_thickness": 2.0,  # um

    # Materials (approximate for Si/SiO2)
    "core_index": 3.45,  # Si at 2.0 um
    "slab_index": 3.45,  # Si
    "clad_index": 1.444,  # SiO2

    # Doping (P++-P-P++ junction in Tidy3D, simplified to PN in Femwell)
    "xpn": 0.0,  # PN junction at waveguide center
    "NA": 1e18,  # Acceptor doping (cm^-3)
    "ND": 1e18,  # Donor doping (cm^-3)

    # Simulation parameters
    "wavelength": 2.0,  # um (from notebook)
    "num_modes": 1,
    "mode_order": 2,
}

def run_femwell_simulation():
    """Run Femwell depletion modulator simulation with Tidy3D-matching parameters."""

    print("\n" + "="*70)
    print("STEP 1: Run Femwell MCP Tool")
    print("-"*70)

    # Create output directory
    output_dir = Path("mcp_output")
    output_dir.mkdir(exist_ok=True)

    try:
        # Run Femwell simulation
        print(f"[INFO] Running Femwell depletion modulator simulation...")
        print(f"  Voltage range: {SIMULATION_PARAMS['voltages'][0]:.1f} - {SIMULATION_PARAMS['voltages'][-1]:.1f} V")
        print(f"  Number of voltage points: {len(SIMULATION_PARAMS['voltages'])}")
        print(f"  Waveguide: {SIMULATION_PARAMS['wg_width']} x {SIMULATION_PARAMS['wg_thickness']} um")
        print(f"  Wavelength: {SIMULATION_PARAMS['wavelength']} um")

        voltages_array, neff_array, neff_change, absorption_dB_per_cm = compute_depletion_modulator(**SIMULATION_PARAMS)

        print(f"\n[OK] Simulation completed successfully!")

        # Display summary
        print(f"  Number of voltage points: {len(voltages_array)}")
        print(f"  neff range: {np.real(neff_array).min():.6f} to {np.real(neff_array).max():.6f}")
        print(f"  Delta neff (0V to {SIMULATION_PARAMS['voltages'][-1]:.1f}V): {neff_change[-1]:.6f}")
        print(f"  Absorption range: {absorption_dB_per_cm.min():.3f} to {absorption_dB_per_cm.max():.3f} dB/cm")

        # Save results to CSV (matching MCP tool output format)
        csv_path = output_dir / "depletion_modulator_results.csv"
        df = pd.DataFrame({
            'voltage_V': voltages_array,
            'neff_real': np.real(neff_array),
            'neff_imag': np.imag(neff_array),
            'neff_change': neff_change,
            'absorption_dB_per_cm': absorption_dB_per_cm,
        })
        df.to_csv(csv_path, index=False)

        print(f"\n[OK] Results saved to: {csv_path}")

        return True

    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_benchmark():
    """Run benchmark comparison script."""

    print("\n" + "="*70)
    print("STEP 2: Compare Results Against Tidy3D Reference")
    print("-"*70)

    # Path to benchmark comparison script
    benchmark_script = Path(__file__).parent / "benchmark_carrier_injection.py"

    if not benchmark_script.exists():
        print(f"[ERROR] Benchmark script not found: {benchmark_script}")
        return False

    # Run benchmark script as subprocess
    result = subprocess.run(
        [sys.executable, str(benchmark_script)],
        capture_output=False,  # Show output directly
        cwd=Path(__file__).parent.parent  # Run from repo root
    )

    return result.returncode == 0

def main():
    """Main workflow."""

    print("="*70)
    print("  BENCHMARK #4: CARRIER INJECTION MODULATOR")
    print("  Femwell vs Tidy3D Validation")
    print("="*70)

    # Step 1: Run Femwell simulation
    success = run_femwell_simulation()

    if not success:
        print("\n" + "="*70)
        print("[ERROR] BENCHMARK FAILED - Simulation error")
        print("="*70)
        return 1

    # Step 2: Run benchmark comparison
    success = run_benchmark()

    if not success:
        print("\n" + "="*70)
        print("[WARN] BENCHMARK COMPARISON ISSUE")
        print("="*70)
        return 1

    print("\n" + "="*70)
    print("[INFO] BENCHMARK COMPLETED")
    print("="*70)
    print("\nIMPORTANT: This benchmark uses PLACEHOLDER Tidy3D reference data!")
    print("To get accurate validation:")
    print("  1. Run MachZehnderModulator.ipynb up to cell 76")
    print("  2. Extract n_eff_freq0 array values")
    print("  3. Update TIDY3D_REFERENCE in benchmark_carrier_injection.py")
    print("  4. Re-run this benchmark")
    print("="*70)

    return 0

if __name__ == "__main__":
    sys.exit(main())
