"""Plot Femwell depletion modulator results vs Tidy3D reference data"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load Femwell results
femwell_data = pd.read_csv('mcp_output/mzi_depletion_modulator_results.csv')

# Tidy3D reference data (PLACEHOLDER - from benchmark_carrier_injection.py)
tidy3d_voltages = np.arange(13) * 0.1  # [0.0, 0.1, 0.2, ..., 1.2] V
tidy3d_neff_real = np.array([
    2.4500, 2.4505, 2.4512, 2.4521, 2.4532,
    2.4545, 2.4560, 2.4577, 2.4596, 2.4617,
    2.4640, 2.4665, 2.4692
])
tidy3d_neff_imag = np.array([
    1e-4, 1.2e-4, 1.5e-4, 1.9e-4, 2.4e-4,
    3.0e-4, 3.8e-4, 4.7e-4, 5.8e-4, 7.1e-4,
    8.6e-4, 1.04e-3, 1.25e-3
])

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Real part of neff vs voltage
ax = axes[0, 0]
ax.plot(tidy3d_voltages, tidy3d_neff_real, 'o-', label='Tidy3D (placeholder)',
        markersize=8, linewidth=2, color='#1f77b4')
ax.plot(femwell_data['voltage_V'], femwell_data['neff_real'], 's--', label='Femwell MCP',
        markersize=6, linewidth=2, color='#ff7f0e')
ax.set_xlabel('Voltage (V)', fontsize=11)
ax.set_ylabel('Real(neff)', fontsize=11)
ax.set_title('Effective Index vs Voltage', fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Plot 2: Imaginary part of neff (absorption) vs voltage
ax = axes[0, 1]
ax.plot(tidy3d_voltages, tidy3d_neff_imag*1e4, 'o-', label='Tidy3D (placeholder)',
        markersize=8, linewidth=2, color='#1f77b4')
ax.plot(femwell_data['voltage_V'], femwell_data['neff_imag']*1e4, 's--', label='Femwell MCP',
        markersize=6, linewidth=2, color='#ff7f0e')
ax.set_xlabel('Voltage (V)', fontsize=11)
ax.set_ylabel('Imag(neff) x 10^4', fontsize=11)
ax.set_title('Absorption vs Voltage', fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Plot 3: Delta neff (modulation efficiency)
ax = axes[1, 0]
tidy3d_delta_neff = tidy3d_neff_real - tidy3d_neff_real[0]
femwell_delta_neff = femwell_data['neff_change'].values
ax.plot(tidy3d_voltages, tidy3d_delta_neff*1e3, 'o-', label='Tidy3D (placeholder)',
        markersize=8, linewidth=2, color='#1f77b4')
ax.plot(femwell_data['voltage_V'], femwell_delta_neff*1e3, 's--', label='Femwell MCP',
        markersize=6, linewidth=2, color='#ff7f0e')
ax.set_xlabel('Voltage (V)', fontsize=11)
ax.set_ylabel('Delta neff x 10^3', fontsize=11)
ax.set_title('Index Change (Modulation Efficiency)', fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Plot 4: Absorption in dB/cm
ax = axes[1, 1]
tidy3d_absorption = 2 * np.pi / 2.0 * tidy3d_neff_imag / (np.log(10) / 10) * 1e4  # Convert to dB/cm
ax.plot(tidy3d_voltages, tidy3d_absorption, 'o-', label='Tidy3D (placeholder)',
        markersize=8, linewidth=2, color='#1f77b4')
ax.plot(femwell_data['voltage_V'], femwell_data['absorption_dB_per_cm'], 's--', label='Femwell MCP',
        markersize=6, linewidth=2, color='#ff7f0e')
ax.set_xlabel('Voltage (V)', fontsize=11)
ax.set_ylabel('Absorption (dB/cm)', fontsize=11)
ax.set_title('Optical Loss vs Voltage', fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mcp_output/depletion_modulator_comparison.png', dpi=300, bbox_inches='tight')
print("Comparison plot saved to: mcp_output/depletion_modulator_comparison.png")

# Print summary statistics
print("\n" + "="*70)
print("DEPLETION MODULATOR COMPARISON SUMMARY")
print("="*70)
print("\nFemwell Results:")
print(f"  Voltage range: {femwell_data['voltage_V'].min():.1f} - {femwell_data['voltage_V'].max():.1f} V")
print(f"  neff range: {femwell_data['neff_real'].min():.6f} - {femwell_data['neff_real'].max():.6f}")
print(f"  Delta neff (0V to 1.0V): {femwell_data['neff_change'].iloc[10]:.6f}")
print(f"  Absorption range: {femwell_data['absorption_dB_per_cm'].min():.2f} - {femwell_data['absorption_dB_per_cm'].iloc[10]:.2f} dB/cm")

print("\nTidy3D Reference (PLACEHOLDER):")
print(f"  Voltage range: {tidy3d_voltages.min():.1f} - {tidy3d_voltages.max():.1f} V")
print(f"  neff range: {tidy3d_neff_real.min():.6f} - {tidy3d_neff_real.max():.6f}")
print(f"  Delta neff (0V to 1.2V): {tidy3d_delta_neff[-1]:.6f}")

print("\n" + "="*70)
print("WARNING: Tidy3D reference data is PLACEHOLDER (not from actual notebook)")
print("="*70)

plt.show()
