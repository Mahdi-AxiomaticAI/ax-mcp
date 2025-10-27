# Tidy3D Example Library - Categorized Summary

A comprehensive collection of photonic device simulations using Tidy3D FDTD and mode solvers, focusing on integrated photonics and RF photonics applications.

---

## 📚 Table of Contents

1. [Photonic Waveguides & Gratings](#photonic-waveguides--gratings)
2. [RF & Microwave Devices](#rf--microwave-devices)
3. [Thermo-Optic Devices](#thermo-optic-devices)
4. [Electro-Optic Modulators](#electro-optic-modulators)

---

## Photonic Waveguides & Gratings

### BiosensorGrating.ipynb
**Description:** Biosensor application using photonic grating structures

**Key Features:**
- Grating-based sensing mechanisms
- Wavelength-dependent transmission analysis
- Sensitivity optimization for biomolecule detection
- Integration with microfluidic systems

**Applications:** Label-free biosensing, medical diagnostics, environmental monitoring

**Difficulty:** ⭐⭐⭐ Advanced

---

### BraggGratings.ipynb
**Description:** Bragg grating filter design and analysis

**Key Parameters:**
- Periodic corrugations for wavelength selectivity
- Grating period and duty cycle optimization
- Stopband and passband characteristics
- Temperature and fabrication tolerance analysis

**Physical Principles:**
- Distributed Bragg reflection
- Photonic bandgap formation
- Wavelength-selective filtering

**Outputs:**
- Transmission/reflection spectra
- Group delay characteristics
- Bandwidth and extinction ratio

**Applications:** Wavelength filters, dispersion compensators, laser stabilization, optical sensing

**Difficulty:** ⭐⭐⭐ Advanced

---

## RF & Microwave Devices

### CPWRFPhotonics1.ipynb
**Description:** Co-planar waveguide (CPW) for RF photonics applications - Part 1: Basic transmission line analysis

**Key Parameters:**
- Frequency range: 1–65 GHz (201 points)
- CPW dimensions:
  - Signal trace width (WS): 30 μm
  - Gap (G): 5 μm
  - Ground trace width (WG): 350 μm
  - Conductor thickness (T): 1 μm
  - Length (L): 2000 μm

**Materials:**
- Substrate: εᵣ = 4.5 (lossless dielectric)
- Metal: Lossy metal with conductivity σ = 41 S/μm

**Workflow:**
1. **2D Mode Analysis:**
   - Effective refractive index (neff)
   - Attenuation coefficient (α) in dB/cm
   - Characteristic impedance (Z₀)
   - RLCG transmission line parameters

2. **3D FDTD Analysis:**
   - S-parameter extraction (S₁₁, S₂₁)
   - Port matching and reflection analysis
   - Field distribution visualization

**Advanced Features:**
- `LayerRefinementSpec` for automatic mesh refinement at metallic edges
- `WavePort` excitation with voltage/current integrals
- `TerminalComponentModeler` for full S-matrix extraction
- PML boundary conditions with quarter-wavelength padding

**Validation:**
- Benchmarked against commercial FEM and FIT solvers
- Agreement within ±0.5% for neff
- Agreement within ±5% for attenuation and impedance

**Outputs:**
- neff vs frequency
- α (dB/cm) vs frequency
- Z₀ (real and imaginary) vs frequency
- R, L, G, C distributed parameters vs frequency
- S-parameters (magnitude and phase)

**Applications:** RF photonic modulators, high-speed interconnects, microwave-to-optical conversion

**Difficulty:** ⭐⭐⭐ Advanced

**References:** Demonstrates typical Tidy3D RF workflow for transmission line modeling

---

### HybridMicrostripCPWBandpassFilter.ipynb
**Description:** Hybrid microstrip/co-planar waveguide (CPW) ultra-wideband (UWB) bandpass filter

**Key Parameters:**
- Target passband: 3.1–10.6 GHz (UWB spectrum authorized by FCC)
- Filter topology: 5-pole design
- Substrate: RT-Duroid 6010 (εᵣ = 10.8, h = 0.635 mm)
- Metal: Copper with σ = 60 S/μm

**Design Architecture:**
- **Top layer:** Microstrip signal line with tapered overlap sections
- **Bottom layer:** CPW with three segments
  - Wide CPW gap (S₁ = 1.1 mm)
  - Long section (L₁ = 17.54 mm, W₁ = 0.92 mm + 2S₁)
  - Middle section (L₂ = 16.9 mm, W₂ = 0.92 mm)
  - Short sections (L₃ = 9.18 mm, W₃ = 0.92 mm)
- **Coupling region:** Microstrip-to-CPW vertical coupling (overlap length = 3.7 mm)

**Pole Distribution:**
- 2 poles: Microstrip-CPW coupling (input/output)
- 3 poles: CPW gap width and length variations

**Simulation Setup:**
- Frequency sweep: 1–13 GHz (401 points)
- 3D FDTD with `LumpedPort` excitations (50 Ω)
- Symmetry: (0, 1, 0) for computational efficiency
- `LayerRefinementSpec`: min_steps_along_axis=2, corner refinement dl=T/2
- PML on all sides for radiation absorption

**Performance Metrics:**
- **Insertion loss (|S₂₁|²):** Near-flat passband across UWB
- **Return loss (|S₁₁|²):** < -10 dB in passband
- **Group delay:** 0.3–0.6 ns variation (< 0.3 ns total variation)

**Validation:**
- Excellent agreement with commercial FEM solver
- Consistent with experimental results from reference paper

**Outputs:**
- S₁₁, S₂₁ vs frequency (magnitude in dB)
- Group delay: τg(ω) = -Δφ/Δω
- Field distributions (E-field) in microstrip and CPW planes

**Applications:** UWB communication systems, radar, high-speed wireless links

**Difficulty:** ⭐⭐⭐⭐ Expert

**Reference:** Wang et al., IEEE MWCL 15(12), 844-846 (2005)

**Cost:** ~0.72 FlexCredits (estimated)

---

## Thermo-Optic Devices

### MachZehnderModulator.ipynb
**Description:** Mach-Zehnder interferometer modulator with thermo-optic phase shifters

**Key Parameters:**
- Wavelength: 1.55 μm
- Platform: Silicon-on-insulator (SOI)
- Modulation mechanism: Thermo-optic effect
- Phase shifter designs: TiN metal heater and doped silicon heater

**MZI Architecture:**
- Input/output: 50/50 beam splitters (directional couplers)
- Arms: Balanced path lengths with phase shifters
- Modulation: Push-pull or single-arm operation

**Applications:** Optical communications, photonic switching, signal processing

**Difficulty:** ⭐⭐⭐⭐ Expert

---

### ThermoOpticDopedModulator.ipynb
**Description:** Thermo-optic modulator with doped silicon (p++-p-p++) junction heater

**Key Parameters:**
- Wavelength: 2 μm
- Waveguide: 0.5 μm × 0.34 μm silicon core, 0.1 μm slab
- Doping regions:
  - **p region (center):** NA = 3.5×10¹⁷ cm⁻³
  - **p++ regions (sides):** NA = 0.85×10²⁰ cm⁻³
  - Junction interface: ±1.75 μm from waveguide center
- Phase shifter length: 320 μm
- Bias range: 0–5 V (0.5 V steps)

**Multi-Physics Workflow:**
1. **Charge Simulation (DC Isothermal):**
   - **Solver:** Tidy3D Charge with `IsothermalSteadyChargeDCAnalysis`
   - **Material:** `SemiconductorMedium` with Shockley-Read-Hall recombination
   - **Doping:** `ConstantDoping` boxes (additive)
   - **Boundary conditions:** `VoltageBC` on auxiliary conductor structures
   - **Convergence:** rel_tol = 1×10⁻¹⁰, abs_tol = 1×10¹⁰, convergence_dv = 0.5
   - **Outputs:** Free carrier density (electrons, holes), potential field, I-V curve

2. **Heat Simulation (Steady-State):**
   - **Input power:** P = V × I (from Charge simulation)
   - **Volumetric heat source:** Applied to waveguide + slabs + side regions
   - **Boundary conditions:**
     - Temperature BC: 300 K at substrate interface
     - Convection BC: h = 10 W/(m²·K) at SiO₂/air interface
   - **Mesh:** `DistanceUnstructuredGrid` with dl_min = 0.033 μm
   - **Outputs:** Temperature distribution T(x, y)

3. **Optical Perturbation (Mode Solving):**
   - **Perturbed mediums:** `PerturbationMedium` with charge and thermal perturbations
   - **Charge-induced Δn and Δk:** Empirical relations (Nedeljkovic et al., 2011)
     - Electrons: Δn ∝ Nₑ⁰·⁹⁹², Δk ∝ Nₑ¹·¹⁴⁹
     - Holes: Δn ∝ Nₕ⁰·⁸⁴¹, Δk ∝ Nₕ¹·¹¹⁹
   - **Thermo-optic effect:** Si dn/dT = 1.76×10⁻⁴ K⁻¹
   - **Mode solver:** Compute neff and attenuation for each bias point

**Material Properties:**
| Material | Thermal Conductivity (W/m·K) | Specific Heat (J/kg·K) | Thermo-Optic Coeff (K⁻¹) |
|----------|------------------------------|------------------------|---------------------------|
| Si (undoped) | 90×10⁻⁶ | 711 | 1.76×10⁻⁴ |
| Si (doped p++) | 25×10⁻⁶ | 711 | - |
| SiO₂ | 1.38×10⁻⁶ | 709 | 1.00×10⁻⁵ |

**Performance (100 μm waveguide):**
- **Pπ (π-shift power):** ~3.5 mW
- **Phase shift:** Linear with power, ~π at 3.5 mW
- **Attenuation:** Minimal loss at low bias, increases with higher doping activation

**Outputs:**
- Hole and electron density distributions
- Potential field across junction
- I-V characteristic curve
- Temperature distribution for each bias
- Effective refractive index (real and imaginary) vs power
- Phase shift vs power
- Transmission loss (dB) vs power

**Applications:** Mid-infrared photonics, sensing, free-space communications, integrated modulators

**Difficulty:** ⭐⭐⭐⭐ Expert

**Reference:** Zhong et al., Opt. Express 29, 23508-23516 (2021)

---

### TransientThermoOpticShifter.ipynb
**Description:** Transient (time-domain) thermal analysis of thermo-optic phase shifters: TiN metal heater vs. N++ doped silicon heater

**Key Parameters:**
- Wavelength: 1.55 μm
- Platform: Silicon-on-insulator (SOI)
- Comparison: Two heater designs
  1. **Strip waveguide + TiN metal heater**
  2. **Rib waveguide + N++ doped silicon heaters**

**Strip Waveguide + TiN Heater:**
- Waveguide: 0.5 μm × 0.22 μm silicon
- Heater: 2 μm × 0.2 μm TiN, 2 μm above waveguide
- Heater power for π-shift (Pπ): 23.9 mW

**Rib Waveguide + Doped Silicon Heaters:**
- Waveguide: 0.5 μm × 0.22 μm core, 0.09 μm slab
- Heaters: Two 1 μm × 0.09 μm N++ Si strips, 0.8 μm buffer from core
- Heater power for π-shift (Pπ): 25.2 mW

**Material Properties:**
| Material | Thermal Conductivity (W/m·K) | Specific Heat (J/kg·K) | Density (kg/m³) |
|----------|------------------------------|------------------------|-----------------|
| Si (waveguide) | 90×10⁻⁶ | 711 | 2.33×10¹⁸ |
| Si (slab) | 55×10⁻⁶ | 711 | 2.33×10¹⁸ |
| Si (bulk) | 148×10⁻⁶ | 711 | 2.33×10¹⁸ |
| TiN | 28×10⁻⁶ | 598 | 5.24×10¹⁸ |
| N++ Si | 25×10⁻⁶ | 711 | 2.33×10¹⁸ |
| SiO₂ | 1.38×10⁻⁶ | 709 | 2.20×10¹⁸ |
| Air | 0.026×10⁻⁶ | 1006 | 1.18×10¹⁵ |

**Thermo-Optic Coefficients:**
- Si: dn/dT = 1.8×10⁻⁴ K⁻¹
- SiO₂: dn/dT = 1.0×10⁻⁵ K⁻¹

**Simulation Workflow:**

1. **Steady-State Heat Power Sweep:**
   - Heat input: 0–30 mW (5 steps)
   - Determine Pπ by interpolating phase shift vs power
   - Boundary conditions:
     - Bottom (substrate): Fixed temperature 300 K
     - Top (SiO₂/air): Convection h = 10 W/(m²·K)

2. **Steady-State at Pπ:**
   - Apply Pπ to heaters
   - Compute steady-state temperature distribution
   - Visualize 2D temperature field and 1D profile

3. **Transient Heat Analysis:**
   - **Solver:** `UnsteadyHeatAnalysis` with `UnsteadySpec`
   - **Time parameters:**
     - Time step: 1 μs
     - Total time: 60 μs
     - Initial temperature: 300 K
   - **Outputs:** Temperature evolution T(x, y, t)

4. **Optical Perturbation & Mode Solving:**
   - **Perturbed mediums:** Apply steady-state T-field to optical mediums
   - **Mode solver:** Compute neff and attenuation
   - **Phase shifter length:** 320 μm

**Performance Metrics:**
- **Pπ:** 23.9 mW (TiN) vs. 25.2 mW (N++ Si)
- **Thermal time constant (1/e):**
  - TiN: ~10 μs (faster response)
  - N++ Si: ~12 μs (slower response)
- **Attenuation:**
  - TiN: 0.0 dB/cm (negligible loss)
  - N++ Si: 0.315 dB/cm (higher absorption in doped regions)

**Outputs:**
- Phase shift vs heater power
- Temperature distribution (2D and 1D profiles)
- Transient temperature vs time: ΔT/ΔTπ
- Mode field profiles (E-field magnitude)
- Loss comparison

**Validation:**
- Good agreement with Jacques et al. (2019)
- Transient behavior matches 1/e time constants

**Applications:** High-speed optical switches, tunable filters, programmable photonic circuits

**Difficulty:** ⭐⭐⭐⭐ Expert

**Reference:** Jacques et al., Opt. Express 27, 10456-10471 (2019)

**Interactive Features:** ipywidgets slider for visualizing temperature evolution over time

---

## Quick Reference Table

| **Example** | **Category** | **Difficulty** | **Physics** | **Typical Runtime** |
|-------------|--------------|----------------|-------------|---------------------|
| BiosensorGrating.ipynb | Photonic | ⭐⭐⭐ | FDTD | 5-10 min |
| BraggGratings.ipynb | Photonic | ⭐⭐⭐ | FDTD | 5-10 min |
| CPWRFPhotonics1.ipynb | RF/Microwave | ⭐⭐⭐ | Mode + FDTD | 10-20 min |
| HybridMicrostripCPWBandpassFilter.ipynb | RF/Microwave | ⭐⭐⭐⭐ | FDTD + S-matrix | 20-30 min |
| MachZehnderModulator.ipynb | Thermo-optic | ⭐⭐⭐⭐ | Heat + Optics | 15-25 min |
| ThermoOpticDopedModulator.ipynb | Thermo-optic | ⭐⭐⭐⭐ | Charge + Heat + Optics | 30-60 min |
| TransientThermoOpticShifter.ipynb | Thermo-optic | ⭐⭐⭐⭐ | Transient Heat + Optics | 20-40 min |

---

## Physics Solvers Used

### FDTD (Finite-Difference Time-Domain)
- Full-wave 3D electromagnetic simulation
- Used for: S-parameters, field distributions, transmission/reflection
- Tools: `Simulation`, `TerminalComponentModeler`, `WavePort`, `LumpedPort`

### Mode Solver
- 2D eigenmode analysis
- Used for: Effective index, attenuation, group index, mode profiles
- Tools: `ModeSolver`, `ModeSpec`

### Heat Solver
- Steady-state and transient thermal analysis
- Used for: Temperature distributions, thermal time constants
- Tools: `HeatChargeSimulation`, `SteadyHeatAnalysis`, `UnsteadyHeatAnalysis`

### Charge Solver
- Semiconductor drift-diffusion equations
- Used for: Free carrier distributions, I-V characteristics
- Tools: `SemiconductorMedium`, `IsothermalSteadyChargeDCAnalysis`

### Multi-Physics Coupling
- Sequential coupling: Charge → Heat → Optics
- Perturbation mediums: `PerturbationMedium`, `MultiPhysicsMedium`
- Tools: `perturbed_mediums_copy()`, `IndexPerturbation`

---

## Material Library

### Optical Properties (λ = 1.55 μm)
- **Silicon (Si):** n = 3.476
- **Silicon (doped):** n = 3.072, k = 0.137
- **Silicon Dioxide (SiO₂):** n = 1.444
- **Titanium Nitride (TiN):** Metal (surface impedance BC)

### Thermal Properties
- **Crystalline Silicon:** κ = 148 W/(m·K)
- **Doped Silicon (waveguide):** κ = 90 W/(m·K)
- **Doped Silicon (slab):** κ = 55 W/(m·K)
- **Doped Silicon (N++):** κ = 25 W/(m·K)
- **Silicon Dioxide:** κ = 1.38 W/(m·K)
- **Titanium Nitride:** κ = 28 W/(m·K)

### Thermo-Optic Coefficients
- **Silicon:** dn/dT = 1.76–1.8×10⁻⁴ K⁻¹
- **Silicon Dioxide:** dn/dT = 1.0×10⁻⁵ K⁻¹

---

## Dependencies

```bash
pip install tidy3d matplotlib numpy scipy ipywidgets
```

**Core Libraries:**
- `tidy3d` - Main simulation engine (FDTD, mode, heat, charge solvers)
- `tidy3d.web` - Cloud simulation management
- `tidy3d.plugins.mode` - Mode solver utilities
- `tidy3d.plugins.smatrix` - S-matrix and RF tools
- `tidy3d.plugins.microwave` - Microwave impedance calculations
- `matplotlib` - Visualization
- `numpy` - Numerical computing
- `ipywidgets` - Interactive visualization (optional)

---

## Running Examples

All examples are Jupyter notebooks (.ipynb):

```bash
# Launch Jupyter
jupyter notebook example_library/CPWRFPhotonics1.ipynb

# Or use JupyterLab
jupyter lab example_library/
```

**Cloud Computing:**
- Tidy3D simulations run on Flexcompute's cloud servers
- Requires Tidy3D account and FlexCredits
- Cost estimates provided before each simulation run
- Use `web.run()` for individual simulations
- Use `web.Batch()` for parameter sweeps

---

## Key Features of Tidy3D

### Automatic Mesh Refinement
- `GridSpec.auto()`: Wavelength-based automatic meshing
- `LayerRefinementSpec`: Edge and corner refinement for metallic structures
- `DistanceUnstructuredGrid`: Unstructured mesh for heat/charge simulations

### Advanced Boundary Conditions
- PML (Perfectly Matched Layer) for wave absorption
- `ConvectionBC`: Convective heat transfer
- `TemperatureBC`: Fixed temperature boundaries
- `VoltageBC`: Electrical potential boundaries

### Multi-Physics Coupling
- `MultiPhysicsMedium`: Unified material definition for charge, heat, and optics
- `PerturbationMedium`: Automatic optical property updates from charge/heat data
- Seamless data transfer between solvers via `perturbed_mediums_copy()`

### Excitation Methods
- `WavePort`: Eigenmode excitation with impedance matching
- `LumpedPort`: Lumped element excitation for RF/microwave
- `HeatSource`: Volumetric heat generation
- `VoltageBC`: DC voltage sources for charge simulations

### Data Analysis
- S-parameters (magnitude, phase, group delay)
- Mode parameters (neff, ng, loss, mode profiles)
- Temperature distributions (2D/3D, transient)
- Free carrier distributions (electrons, holes)
- I-V characteristics

---

## Best Practices

### For FDTD Simulations:
1. Use symmetry when possible to reduce computational cost
2. Set `shutoff` < 1e-7 for accurate S-parameters
3. Apply `LayerRefinementSpec` for metallic structures
4. Use PML boundaries with λ/4 padding

### For Heat Simulations:
1. Define proper boundary conditions (temperature, convection)
2. Use `DistanceUnstructuredGrid` for efficient meshing
3. Apply volumetric heat sources to structures (not mediums)
4. For transient: Choose time_step based on thermal time constants

### For Charge Simulations:
1. Define doping profiles with additive `ConstantDoping` boxes
2. Set appropriate tolerance: rel_tol=1e-10, abs_tol based on carrier density scale
3. Use auxiliary conductor structures for `VoltageBC` placement
4. Use `convergence_dv` to limit voltage sweep step size

### For Multi-Physics:
1. Run simulations sequentially: Charge → Heat → Optics
2. Interpolate data to common grid before perturbation
3. Use `MultiPhysicsMedium` for consistent material properties
4. Validate each physics stage before coupling

---

## Contributing

When adding new examples, follow this structure:
1. **Header:** Title and description
2. **Imports:** Organized library imports
3. **Parameters:** Clearly defined geometric and material parameters
4. **Geometry:** Structure and scene creation
5. **Simulation:** Solver configuration and execution
6. **Post-processing:** Calculations, plots, and analysis
7. **References:** Citation to original papers

---

## License

These examples are part of the Tidy3D open-source project. Please cite original papers when using these simulations in research.

For more details: [Tidy3D Documentation](https://docs.flexcompute.com/projects/tidy3d/)

**Account Setup:**
- Create account at [Tidy3D Simulation Cloud](https://tidy3d.simulation.cloud/)
- Free tier available with trial FlexCredits
- Educational and research discounts available

---

## Additional Resources

- **Tidy3D Examples Gallery:** [Flexcompute Examples](https://www.flexcompute.com/tidy3d/examples/)
- **API Documentation:** [Tidy3D API Reference](https://docs.flexcompute.com/projects/tidy3d/en/latest/api/)
- **Community Forum:** [Tidy3D Forum](https://www.flexcompute.com/tidy3d/community/)
- **Tutorials:** Step-by-step guides for beginners

---

## Summary of Simulation Types

| **Type** | **Examples** | **Use Cases** |
|----------|--------------|---------------|
| FDTD Only | BiosensorGrating, BraggGratings | Spectral analysis, transmission/reflection |
| Mode + FDTD | CPWRFPhotonics1 | Transmission line characterization, waveguide analysis |
| FDTD + S-matrix | HybridMicrostripCPWBandpassFilter | RF filter design, impedance matching |
| Heat + Optics | MachZehnderModulator, TransientThermoOpticShifter | Thermal phase shifters, power budget |
| Charge + Heat + Optics | ThermoOpticDopedModulator | Active devices with electrical injection |