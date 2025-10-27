# Tidy3D Benchmark Notebooks

This folder contains the Tidy3D reference notebooks used for benchmarking against Femwell MCP tools.

## Benchmark Mapping

### Benchmark #1: TiN Metal Heater Phase Shifter
- **Notebook**: `TransientThermoOpticShifter.ipynb`
- **Relevant Sections**: Strip waveguide variant (cells[32-33, 38, 40, 47])
- **Key Metrics**: P_π = 23.9 mW, phase vs power, temperature distribution
- **Femwell MCP Tool**: `simulate_metal_heater_phase_shifter`

### Benchmark #2: Doped Silicon Heater Phase Shifter
- **Notebook**: `TransientThermoOpticShifter.ipynb`
- **Relevant Sections**: Rib waveguide variant (cells[32-33, 38, 40, 62])
- **Key Metrics**: P_π = 25.2 mW, phase vs power, temperature distribution
- **Femwell MCP Tool**: `simulate_doped_si_heater_phase_shifter`

### Benchmark #3: Waveguide Dispersion
- **Notebook**: `wg_dispersion.ipynb`
- **Relevant Sections**: All cells (neff, ng vs wavelength)
- **Key Metrics**: neff(λ), ng(λ) for 0.5×0.22 μm Si waveguide, λ = 1.27-1.31 μm
- **Femwell MCP Tool**: `simulate_waveguide_dispersion`
- **Tidy3D MCP Tool**: `simulate_waveguide_dispersion` (already exists!)

### Benchmark #4: Carrier Injection Mach-Zehnder Modulator
- **Notebook**: `MachZehnderModulator.ipynb`
- **Relevant Sections**: Carrier density, I-V curves, neff vs voltage (cells[31, 33, 78, 80])
- **Key Metrics**: Δneff vs voltage, I-V characteristics, phase shift efficiency
- **Femwell MCP Tool**: `simulate_depletion_modulator`
- **Note**: Tidy3D includes both charge AND thermal effects (multi-physics)

---

## Usage

These notebooks serve as reference implementations for validation. To benchmark:

1. Run the Tidy3D notebook and extract reference data
2. Run the corresponding Femwell MCP tool with matching parameters
3. Compare results against validation metrics in `TOP_4_BENCHMARKS.md`

## Original Source

All notebooks copied from: `Tidy3D/example_library/`

**Date**: 2025-10-23