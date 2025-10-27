"""Benchmark #2: Doped Silicon Heater Phase Shifter - Full Workflow

This script:
1. Runs Femwell MCP tool (simulate_doped_si_heater_phase_shifter)
2. Runs benchmark comparison against Tidy3D reference
3. Generates comparison plots and reports

Usage:
    python run_benchmark2_doped_si_heater.py
"""

import sys
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiomatic_mcp.servers.femwell.tools.doped_si_heater import compute_doped_si_heater_phase_shifter

# Tidy3D-matching parameters from TransientThermoOpticShifter.ipynb (rib variant)
SIMULATION_PARAMS = {
    # Power sweep - matching Tidy3D notebook
    "powers_mW": list(np.linspace(0, 30, 11)),  # 0 to 30 mW (11 points for smooth curve)

    # Waveguide geometry (rib waveguide)
    "w_core": 0.5,      # um (core width)
    "h_core": 0.22,     # um (core height)
    "w_buffer": 0.8,    # um (slab width on each side)
    "h_buffer": 0.09,   # um (slab height)
    "h_box": 2.0,       # um (BOX layer)
    "h_clad": 2.8,      # um (cladding)

    # Doped Si heater geometry
    "w_heater": 1.0,    # um (heater width)

    # Simulation width
    "w_sim": 32,        # um (total simulation width - larger for rib)

    # Thermal conductivities (W/(m*K))
    "k_core": 90,       # Silicon core
    "k_box": 1.38,      # SiO2 BOX
    "k_clad": 1.38,     # SiO2 cladding
    "k_slab": 55,       # Doped silicon slab (lower due to doping)
    "k_heater": 55,     # N++ doped silicon heaters

    # Heater electrical conductivity
    "heater_resistivity": 1e5,  # S/m (N++ doped Si)

    # Thermo-optic coefficients (1/K)
    "dn_dT_core": 1.86e-4,  # Si at 1.55 um
    "dn_dT_clad": 1e-5,     # SiO2

    # Phase shifter length
    "phase_shifter_length": 320,  # um (from benchmark spec)

    # Operating wavelength
    "wavelength": 1.55,  # um
}

def run_femwell_simulation():
    """Run Femwell doped Si heater phase shifter simulation with Tidy3D-matching parameters."""

    print("\n" + "="*70)
    print("STEP 1: Run Femwell MCP Tool")
    print("-"*70)

    # Create output directory
    output_dir = Path("mcp_output")
    output_dir.mkdir(exist_ok=True)

    try:
        # Run Femwell simulation
        print(f"[INFO] Running Femwell doped Si heater phase shifter simulation...")
        print(f"  Power range: {SIMULATION_PARAMS['powers_mW'][0]:.2f} - {SIMULATION_PARAMS['powers_mW'][-1]:.2f} mW")
        print(f"  Number of power points: {len(SIMULATION_PARAMS['powers_mW'])}")
        print(f"  Core: {SIMULATION_PARAMS['w_core']} x {SIMULATION_PARAMS['h_core']} um")
        print(f"  Slab: {SIMULATION_PARAMS['w_buffer']*2 + SIMULATION_PARAMS['w_core']} um x {SIMULATION_PARAMS['h_buffer']} um")
        print(f"  Heater width: {SIMULATION_PARAMS['w_heater']} um N++ Si")
        print(f"  Phase shifter length: {SIMULATION_PARAMS['phase_shifter_length']} um")

        powers_mW, currents, neffs, phase_shifts, temperatures_2D, basis_list = compute_doped_si_heater_phase_shifter(**SIMULATION_PARAMS)

        print(f"\n[OK] Simulation completed successfully!")
        print(f"  Number of power points: {len(powers_mW)}")
        print(f"  Power range: {powers_mW[0]:.2f} to {powers_mW[-1]:.2f} mW")
        print(f"  Phase shift range: {phase_shifts[0]:.4f} to {phase_shifts[-1]:.4f} rad")
        print(f"  Phase shift range: {phase_shifts[0]/np.pi:.4f} to {phase_shifts[-1]/np.pi:.4f} pi")

        # Find P_pi
        if len(phase_shifts) > 1 and phase_shifts[-1] > np.pi:
            P_pi = np.interp(np.pi, phase_shifts, powers_mW)
            print(f"  P_pi (power for pi phase shift): {P_pi:.2f} mW")
        elif len(phase_shifts) > 1:
            # Extrapolate
            P_pi = np.pi / (phase_shifts[-1] / powers_mW[-1])
            print(f"  P_pi (extrapolated): {P_pi:.2f} mW")

        # Calculate neff change
        neff_change = neffs - neffs[0]

        # Save results to CSV (matching MCP tool output format)
        csv_path = output_dir / "doped_si_heater_results.csv"
        df = pd.DataFrame({
            'power_mW': powers_mW,
            'current_A': currents,
            'neff': neffs,
            'neff_change': neff_change,
            'phase_shift_rad': phase_shifts,
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
    benchmark_script = Path(__file__).parent / "benchmark_doped_si_heater.py"

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
    print("  BENCHMARK #2: DOPED SILICON HEATER PHASE SHIFTER")
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

    return 0

if __name__ == "__main__":
    sys.exit(main())
