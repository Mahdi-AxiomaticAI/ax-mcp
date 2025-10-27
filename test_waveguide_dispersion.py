"""Test script to validate waveguide dispersion MCP tool."""

import numpy as np
from axiomatic_mcp.servers.femwell.tools.waveguide_dispersion import compute_waveguide_dispersion

# Use same parameters as original example
wavelengths = np.linspace(1.2, 1.9, 20)

print("Testing waveguide dispersion...")
print(f"Wavelength range: {wavelengths[0]:.3f} to {wavelengths[-1]:.3f} um")
print(f"Number of points: {len(wavelengths)}")

try:
    wavelengths_array, neffs, ng_array, gvd_array, te_fracs = compute_waveguide_dispersion(
        wavelengths=wavelengths,
        w_core=1.0,
        h_core=0.5,
        core_material="Si3N4",
        box_material="SiO2",
        clad_material="air",
        num_modes=2,
    )

    print("\nResults:")
    print(f"  Number of wavelength points: {len(wavelengths_array)}")
    print(f"  Number of modes: {neffs.shape[1]}")
    print(f"\nMode 0:")
    print(f"  neff range: {min(neffs[:, 0]):.6f} to {max(neffs[:, 0]):.6f}")
    print(f"  ng range: {min(ng_array[:, 0]):.6f} to {max(ng_array[:, 0]):.6f}")
    print(f"  GVD range: {min(gvd_array[:, 0]):.3f} to {max(gvd_array[:, 0]):.3f} ps/(nm*km)")
    print(f"  TE fraction range: {min(te_fracs[:, 0]):.3f} to {max(te_fracs[:, 0]):.3f}")

    print(f"\nMode 1:")
    print(f"  neff range: {min(neffs[:, 1]):.6f} to {max(neffs[:, 1]):.6f}")
    print(f"  ng range: {min(ng_array[:, 1]):.6f} to {max(ng_array[:, 1]):.6f}")
    print(f"  GVD range: {min(gvd_array[:, 1]):.3f} to {max(gvd_array[:, 1]):.3f} ps/(nm*km)")
    print(f"  TE fraction range: {min(te_fracs[:, 1]):.3f} to {max(te_fracs[:, 1]):.3f}")

    print("\n[OK] Waveguide dispersion tool working correctly!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
