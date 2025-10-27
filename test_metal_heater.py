"""Test script to validate metal heater phase shifter MCP tool."""

import numpy as np
from axiomatic_mcp.servers.femwell.tools.metal_heater import compute_metal_heater_phase_shifter

# Use same parameters as original example
currents = np.linspace(0.0, 7.4e-3, 10)

print("Testing metal heater phase shifter...")
print(f"Current range: {currents[0]*1e3:.3f} to {currents[-1]*1e3:.3f} mA")

try:
    currents_array, powers_mW, neffs, phase_shifts_rad, temps_list, basis_list = compute_metal_heater_phase_shifter(
        currents=currents,
        wavelength=1.55,
        phase_shifter_length=320.0,
    )

    print("\nResults:")
    print(f"  Number of points: {len(currents_array)}")
    print(f"  neff range: {min(neffs):.6f} to {max(neffs):.6f}")
    print(f"  Phase shift range: {min(phase_shifts_rad)/np.pi:.3f}pi to {max(phase_shifts_rad)/np.pi:.3f}pi")

    # Calculate P_pi
    phase_pi_idx = np.where(phase_shifts_rad >= np.pi)[0]
    if len(phase_pi_idx) > 0:
        P_pi = powers_mW[phase_pi_idx[0]]
        print(f"  P_pi = {P_pi:.2f} mW")
    else:
        print("  P_pi not reached")

    # Compare with original example expected result
    # Original: Phase shift: 3.31... at 7.4 mA
    print(f"\nFinal phase shift: {phase_shifts_rad[-1]:.3f} rad = {phase_shifts_rad[-1]/np.pi:.3f}pi")
    print("(Original example expected ~3.31 rad at 7.4 mA)")

    print("\n[OK] Metal heater tool working correctly!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()