"""Benchmark #1: TiN Metal Heater Phase Shifter - Full Workflow

This script:
1. Runs Femwell MCP tool (simulate_metal_heater_phase_shifter)
2. Runs benchmark comparison against Tidy3D reference
3. Generates comparison plots and reports

Usage:
    python run_benchmark1_metal_heater.py
"""

import sys
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiomatic_mcp.servers.femwell.tools.metal_heater import compute_metal_heater_phase_shifter

# Tidy3D-matching parameters from TransientThermoOpticShifter.ipynb
SIMULATION_PARAMS = {
    # Current sweep - need to determine range for 0-30 mW power
    # P = I^2 * R, where R depends on heater geometry
    # For TiN heater: typical resistance ~few hundred ohms
    # To achieve 30 mW: I = sqrt(P/R) ≈ sqrt(0.03/300) ≈ 0.01 A = 10 mA
    "currents": list(np.linspace(0, 0.015, 11)),  # 0 to 15 mA (conservative)

    # Waveguide geometry (from notebook)
    "w_core": 0.5,  # um
    "h_core": 0.22,  # um
    "h_box": 2.0,  # um (BOX layer)
    "h_clad": 2.8,  # um (cladding)

    # TiN heater geometry
    "w_heater": 2.0,  # um (from benchmark spec)
    "h_heater": 0.14,  # um (Femwell parameter)
    "offset_heater": 2.0,  # um (distance from waveguide surface)

    # Simulation width
    "w_sim": 16,  # um (total simulation width)

    # Thermal conductivities (W/(m*K))
    "k_core": 90,    # Silicon
    "k_box": 1.38,   # SiO2
    "k_clad": 1.38,  # SiO2
    "k_heater": 28,  # TiN

    # Heater electrical conductivity
    "heater_resistivity": 2.3e6,  # S/m (TiN)

    # Thermo-optic coefficients (1/K)
    "dn_dT_core": 1.86e-4,  # Si at 1.55 um
    "dn_dT_clad": 1e-5,     # SiO2

    # Phase shifter length
    "phase_shifter_length": 320,  # um (from benchmark spec)

    # Operating wavelength
    "wavelength": 1.55,  # um
}

def run_femwell_simulation():
    """Run Femwell metal heater phase shifter simulation with Tidy3D-matching parameters."""

    print("\n" + "="*70)
    print("STEP 1: Run Femwell MCP Tool")
    print("-"*70)

    # Create output directory
    output_dir = Path("mcp_output")
    output_dir.mkdir(exist_ok=True)

    try:
        # Run Femwell simulation
        print(f"[INFO] Running Femwell metal heater phase shifter simulation...")
        print(f"  Current range: {SIMULATION_PARAMS['currents'][0]:.4f} - {SIMULATION_PARAMS['currents'][-1]:.4f} A")
        print(f"  Number of current points: {len(SIMULATION_PARAMS['currents'])}")
        print(f"  Waveguide: {SIMULATION_PARAMS['w_core']} x {SIMULATION_PARAMS['h_core']} um")
        print(f"  Heater: {SIMULATION_PARAMS['w_heater']} x {SIMULATION_PARAMS['h_heater']} um TiN")
        print(f"  Phase shifter length: {SIMULATION_PARAMS['phase_shifter_length']} um")

        currents, power_mW, neffs, phase_shifts, temperatures_2D, basis_list = compute_metal_heater_phase_shifter(**SIMULATION_PARAMS)

        print(f"\n[OK] Simulation completed successfully!")

        # Calculate neff change and corrected power BEFORE displaying
        neff_change = neffs - neffs[0]

        # WORKAROUND: Power from tool is per-unit-length, need to calculate total power
        heater_length_um = SIMULATION_PARAMS['phase_shifter_length']
        heater_width_um = SIMULATION_PARAMS['w_heater']
        heater_thickness_um = SIMULATION_PARAMS['h_heater']
        heater_resistivity_Sm = SIMULATION_PARAMS['heater_resistivity']
        heater_area_um2 = heater_width_um * heater_thickness_um
        heater_resistance_Ohm = (1 / heater_resistivity_Sm) * heater_length_um * 1e-6 / (heater_area_um2 * 1e-12)
        power_mW_corrected = (currents ** 2) * heater_resistance_Ohm * 1000

        # Display summary
        print(f"  Number of current points: {len(currents)}")
        print(f"  Current range: {currents[0]:.4f} to {currents[-1]:.4f} A")
        print(f"  Power range: {power_mW_corrected[0]:.2f} to {power_mW_corrected[-1]:.2f} mW")
        print(f"  Phase shift range: {phase_shifts[0]:.4f} to {phase_shifts[-1]:.4f} rad")
        print(f"  Phase shift range: {phase_shifts[0]/np.pi:.4f} to {phase_shifts[-1]/np.pi:.4f} pi")

        # Find P_π
        if len(phase_shifts) > 1:
            P_pi = np.interp(np.pi, phase_shifts, power_mW_corrected)
            print(f"  P_pi (power for pi phase shift): {P_pi:.2f} mW")

        # Calculate neff change
        neff_change = neffs - neffs[0]

        # WORKAROUND: Power from tool is per-unit-length, need to multiply by length
        # The tool returns power per micron, need total power for the heater
        # For a heater of length L (in phase shifter direction), total P = P_per_length * L
        # However, for 2D simulation, we need to estimate based on current and resistance
        # P = I^2 * R, where R = resistivity * length / area
        # Use typical heater length = phase_shifter_length
        heater_length_um = SIMULATION_PARAMS['phase_shifter_length']
        heater_width_um = SIMULATION_PARAMS['w_heater']
        heater_thickness_um = SIMULATION_PARAMS['h_heater']
        heater_resistivity_Sm = SIMULATION_PARAMS['heater_resistivity']

        # Calculate resistance: R = rho * L / A, where rho = 1/sigma
        # A = width * thickness
        heater_area_um2 = heater_width_um * heater_thickness_um
        # Convert: 1/(S/m) = Ohm*m, need Ohm*um
        heater_resistance_Ohm = (1 / heater_resistivity_Sm) * heater_length_um * 1e-6 / (heater_area_um2 * 1e-12)

        # Calculate power: P = I^2 * R
        power_mW_corrected = (currents ** 2) * heater_resistance_Ohm * 1000  # Convert W to mW

        # Save results to CSV (matching MCP tool output format)
        csv_path = output_dir / "metal_heater_results.csv"
        df = pd.DataFrame({
            'current_A': currents,
            'phase_shift_rad': phase_shifts,
            'power_mW': power_mW_corrected,
            'power_mW_from_tool': power_mW,  # Keep original for reference
            'neff': neffs,
            'neff_change': neff_change,
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
    benchmark_script = Path(__file__).parent / "benchmark_metal_heater.py"

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
    print("  BENCHMARK #1: TIN METAL HEATER PHASE SHIFTER")
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
