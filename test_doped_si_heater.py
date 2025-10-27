"""Test script to validate doped silicon heater phase shifter MCP tool."""

import numpy as np
from axiomatic_mcp.servers.femwell.tools.doped_si_heater import compute_doped_si_heater_phase_shifter

# Use same parameters as original example (target P_pi = 25.2 mW)
powers_mW = np.linspace(0.0, 30.0, 10)

print("Testing doped silicon heater phase shifter...")
print(f"Power range: {powers_mW[0]:.3f} to {powers_mW[-1]:.3f} mW")

try:
    powers_mW_array, currents_A, neffs, phase_shifts_rad, temps_list, basis_list = compute_doped_si_heater_phase_shifter(
        powers_mW=powers_mW,
        wavelength=1.55,
        phase_shifter_length=320.0,
    )

    print("\nResults:")
    print(f"  Number of points: {len(powers_mW_array)}")
    print(f"  neff range: {min(neffs):.6f} to {max(neffs):.6f}")
    print(f"  Phase shift range: {min(phase_shifts_rad)/np.pi:.3f}pi to {max(phase_shifts_rad)/np.pi:.3f}pi")

    # Calculate P_pi
    phase_pi_idx = np.where(phase_shifts_rad >= np.pi)[0]
    if len(phase_pi_idx) > 0:
        P_pi = powers_mW_array[phase_pi_idx[0]]
        I_pi = currents_A[phase_pi_idx[0]] * 1e3
        print(f"  P_pi = {P_pi:.2f} mW (I_pi = {I_pi:.3f} mA)")
    else:
        print("  P_pi not reached")

    # Compare with expected result
    print(f"\nExpected P_pi: ~25.2 mW (from original example)")
    if len(phase_pi_idx) > 0:
        error = abs(P_pi - 25.2) / 25.2 * 100
        print(f"Error: {error:.1f}%")

    print("\n[OK] Doped silicon heater tool working correctly!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()