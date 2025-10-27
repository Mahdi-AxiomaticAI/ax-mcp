# Femwell Example Library - Categorized Summary

A comprehensive collection of photonic device simulation examples using Femwell finite element methods.

---

## 📚 Table of Contents

1. [Basic Waveguide Analysis](#basic-waveguide-analysis)
2. [Dispersion Engineering](#dispersion-engineering)
3. [Coupling & Overlap](#coupling--overlap)
4. [Periodic Structures](#periodic-structures)
5. [Thermo-Optic Devices](#thermo-optic-devices)
6. [Electro-Optic Devices](#electro-optic-devices)
7. [RF/Microwave Structures](#rfmicrowave-structures)

---

## Basic Waveguide Analysis

### waveguide_modes.py
**Description:** Fundamental optical waveguide mode calculations

**Key Parameters:**
- Geometry: 2.5 μm × 0.3 μm silicon nitride core
- Wavelength: 1.55 μm
- Materials: Si₃N₄ core (n=1.9963), SiO₂ box (n=1.444), air clad (n=1.0)

**Outputs:**
- Effective refractive index
- E-field and H-field distributions
- Mode intensity profiles
- Power confinement factors

**Applications:** Starting point for waveguide design, mode analysis, and field visualization

**Difficulty:** ⭐ Beginner

---

## Dispersion Engineering

### vary_wavelength.py
**Description:** Wavelength-dependent waveguide properties and dispersion analysis

**Key Parameters:**
- Wavelength range: 1.2–1.9 μm (20 points)
- Core: 1 μm × 0.5 μm Si₃N₄
- Number of modes: 2

**Material Models:**
- Si₃N₄: Sellmeier equation (valid 0.31–5.507 μm)
- SiO₂: Sellmeier equation (valid 0.21–6.7 μm)

**Outputs:**
- Effective refractive index vs wavelength
- Group velocity (vg) vs wavelength
- Group velocity dispersion coefficient (D) vs wavelength
- TE/TM fraction for each mode

**Applications:** Broadband waveguide design, dispersion engineering for nonlinear optics

**Difficulty:** ⭐⭐ Intermediate

---

### calculate_GVD.py
**Description:** Precision GVD calculation reproducing Klenner et al. (2016)

**Key Parameters:**
- Wavelength range: 500–2500 nm (50 nm steps)
- Core: 0.88 μm × 0.69 μm Si₃N₄
- Polynomial fitting: 3rd order spline, 2nd derivative

**Validation:**
- Includes reference data comparison from published paper
- CSV reference data: `../reference_data/Klenner/GVD.csv`

**Outputs:**
- Effective refractive index fitting curve
- Second derivative of neff
- GVD parameter in ps/(nm·km)

**Applications:** Ultrafast optics, frequency comb design, soliton generation

**Difficulty:** ⭐⭐⭐ Advanced

---

## Coupling & Overlap

### fiber_overlap.py
**Description:** Fiber-to-chip coupling efficiency calculation

**Key Parameters:**
- Waveguide: 0.2 μm × 0.3 μm Si₃N₄
- Fiber MFD sweep: 2–20 μm (100 points)
- Wavelength: 1.55 μm

**Method:**
- Gaussian fiber mode approximation
- Overlap integral between waveguide mode and fiber mode
- In-plane field component (Ey) used for TE-like modes

**Outputs:**
- Coupling efficiency vs mode field diameter
- Optimal MFD for maximum coupling

**Applications:** Fiber-to-chip interface design, packaging optimization

**Difficulty:** ⭐⭐ Intermediate

---

### coupled_mode_theory.py
**Description:** Directional coupler simulation using coupled mode theory

**Key Parameters:**
- Waveguide 1 width: 0.45 μm
- Waveguide 2 width: 0.46 μm (intentional asymmetry)
- Gap: 0.4 μm
- Core height: 0.22 μm
- Wavelength: 1.55 μm

**Analysis:**
- Symmetric and asymmetric supermodes
- Coupling coefficients (κ)
- Overlap integrals
- Power transfer length calculation

**Outputs:**
- Mode effective indices (symmetric/asymmetric)
- Coupling length: Lc = π / (2Δβ)
- Power transfer dynamics over propagation

**Applications:** Optical couplers, beam splitters, Mach-Zehnder interferometers

**Status:** ⚠️ Under construction (per code comment)

**Difficulty:** ⭐⭐⭐ Advanced

---

## Periodic Structures

### bragg_filter.py
**Description:** Bragg grating filter simulation with periodic boundary conditions

**Key Parameters:**
- Unit cell period: a = 0.330 μm
- Structure height: b = 0.7 μm
- Hole height: c = 0.2 μm
- k₀ = 0.7/a (normalized frequency)

**Method:**
- 2D periodic mode solver
- Bloch boundary conditions (left-right periodic)
- Eigenmode solution for periodic structures

**Materials:**
- Background: n = 1.45
- Structure: n = 3.5

**Outputs:**
- Band structure (k vs frequency)
- Bloch modes with periodic extension visualization
- Photonic band gaps

**Applications:** Wavelength-selective filters, photonic crystal cavities, slow light structures

**Reference:** Notaros et al., IEEE JSTQE (2015)

**Difficulty:** ⭐⭐⭐⭐ Expert

---

### grating_coupler.py
**Description:** Surface grating coupler for vertical fiber coupling

**Key Parameters:**
- Grating period: a = 0.47 μm
- Structure layers:
  - h1 = 0.26 μm (tall features)
  - h2 = 0.20 μm (medium features)
  - h3 = 0.02 μm (thin base layer)
- PML thickness: 2 μm (top/bottom absorption)

**Advanced Features:**
- Perfectly matched layer (PML) implementation
- Complex permittivity for absorption: ε += 4i·(|y|-h+pml)²/pml²
- Multiple feature heights in unit cell

**Outputs:**
- Complex eigenvalues (real and imaginary k)
- Radiation modes with periodic extension
- Coupling strength and directionality

**Applications:** Vertical fiber-to-chip coupling, wafer-scale testing interfaces

**Reference:** Notaros et al. (2015)

**Difficulty:** ⭐⭐⭐⭐ Expert

---

## Thermo-Optic Devices

### metal_heater_phase_shifter.py
**Description:** TiN metal heater thermal phase shifter (steady-state)

**Key Parameters:**
- Waveguide: 0.5 μm × 0.22 μm silicon
- Heater: 2 μm × 0.14 μm TiN
- Heater offset: 2 μm above waveguide
- Phase shifter length: 320 μm
- Current range: 0–7.4 mA

**Thermal Properties:**
| Material | Thermal Conductivity | Thermo-Optic Coeff. |
|----------|---------------------|---------------------|
| Si core  | 90 W/(m·K)          | dn/dT = 1.86×10⁻⁴ K⁻¹ |
| TiN      | 28 W/(m·K)          | Conductivity: 2.3×10⁶ S/m |
| SiO₂     | 1.38 W/(m·K)        | dn/dT = 1.00×10⁻⁵ K⁻¹ |

**Outputs:**
- Temperature distribution at each current
- Effective refractive index vs current
- Phase shift: Δφ = (2π/λ)·ΔneffL

**Performance:**
- Typical phase shift: ~π at maximum current
- Compact design with low thermal crosstalk

**Applications:** MZI switches, tunable filters, programmable photonic circuits

**Reference:** Jacques et al., Opt. Express 27, 10456 (2019)

**Difficulty:** ⭐⭐⭐ Advanced

---

### metal_heater_phase_shifter_transient.py
**Description:** Time-resolved TiN heater dynamics

**Key Parameters:**
- Similar geometry to steady-state version
- Time step: Δt = 0.1 μs
- Total steps: 100
- Pulsed current: ON (0–10% time), OFF (10–50%), ON (50–100%)

**Thermal Diffusivity:**
| Material | α (m²/s) |
|----------|----------|
| TiN      | 28/(598×5240) = 8.98×10⁻⁶ |
| SiO₂     | 1.38/(709×2203) = 8.83×10⁻⁷ |
| Si       | 148/(711×2330) = 8.93×10⁻⁵ |

**Outputs:**
- Average core temperature vs time
- Dynamic phase shift (exact and perturbation approximation)
- Thermal rise/fall time constants

**Analysis Methods:**
- Exact: Full mode solve at each time step
- Approximate: Perturbation theory Δneff ≈ ∫ε₀·Δε·|E|²

**Applications:** Switching speed analysis, thermal crosstalk studies, modulation bandwidth

**Difficulty:** ⭐⭐⭐⭐ Expert

---

### si_heater_phase_shifter.py
**Description:** Doped silicon resistive heater phase shifter

**Key Parameters:**
- Waveguide: 0.5 μm × 0.22 μm silicon
- Symmetric heaters: 1 μm × 0.09 μm each side
- Buffer spacing: 0.8 μm from core
- Power: 25.2 mW total

**Material Properties:**
| Material | Thermal Conductivity | Conductivity |
|----------|---------------------|--------------|
| Si core  | 90 W/(m·K)          | - |
| Doped Si | 55 W/(m·K)          | 1×10⁵ S/m |
| SiO₂     | 1.38 W/(m·K)        | - |

**Advantages:**
- CMOS-compatible fabrication
- No metal deposition required
- Integrated with waveguide layer

**Disadvantages:**
- Lower electrical conductivity → higher voltage required
- Lower thermal conductivity in doped regions

**Applications:** Monolithic PICs, CMOS foundry-compatible thermal tuning

**Reference:** Jacques et al. (2019)

**Difficulty:** ⭐⭐⭐ Advanced

---

## Electro-Optic Devices

### coulomb.py
**Description:** Lithium niobate (LiNbO₃) electro-optic phase shifter

**Key Parameters:**
- Core width: 1.532 μm (x-cut LiNbO₃ thin film)
- Electrode gap: 2×2.629 μm = 5.258 μm center-to-center
- Electrode width: 4.4 μm
- Electrode height: 1.8 μm
- Voltage range: 0–100 V

**Physical Effects:**
1. **Coulomb/Poisson Solve:**
   - Electric field distribution from electrode potentials
   - Dielectric constants: εdc(LiNbO₃ slab) = 28.4, εdc(core) = 7.5

2. **Pockels Effect:**
   - Δn = 0.5·n³·r₃₃·E
   - r₃₃ = 31×10⁻¹² m/V (electro-optic coefficient)
   - Base refractive index: n₀(slab) = 2.211

**Outputs:**
- Electric potential and field distribution
- Voltage-dependent effective refractive index
- Linear electro-optic tuning curve

**Advantages:**
- High-speed modulation (>100 GHz)
- Low propagation loss
- Strong Pockels effect

**Applications:** High-speed modulators, EO frequency shifters, quantum photonics

**Reference:** Han et al., Opt. Express 30 (2022)

**Difficulty:** ⭐⭐⭐⭐ Expert

---

## RF/Microwave Structures

### microstrip_waveguide_vary_gap.py
**Description:** Coupled microstrip transmission lines with gap variation

**Key Parameters:**
- Frequency range: 1–16 GHz (16 points)
- Gap sweep: [0.02, 0.06, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0] mm
- Strip widths: 0.6 mm (both)
- Substrate: 0.64 mm thick, εᵣ = 9.9
- Strip thickness: 0.005 mm (conductor loss: 18 μS/mm)

**Method:**
- 2D cross-section FEM with metallic boundaries
- Even and odd mode calculation
- Frequency-dependent effective permittivity

**Outputs:**
- εeff vs frequency for even/odd modes
- Coupling strength vs gap spacing
- Mode hybridization analysis

**Applications:**
- RF directional couplers
- Crosstalk analysis in high-speed PCBs
- Coupled-line filters

**Reference:** Jansen et al., IEEE Trans. MTT 26 (1978)

**Difficulty:** ⭐⭐⭐ Advanced

---

### microstrip_waveguide_vary_width.py
**Description:** Single microstrip characteristic impedance vs width

**Key Parameters:**
- Frequency range: 1–16 GHz (16 points)
- Width sweep: 0.04, 0.4, 3.0 mm (expandable list in code)
- Substrate: 0.64 mm, εᵣ = 9.9
- Strip thickness: 0.005 mm

**Calculations:**
1. **Effective Permittivity:**
   - εeff = n²eff from mode solver

2. **Characteristic Impedance:**
   - Current integration along conductor boundary
   - Z₀ = V²/P = (∮H·dl)⁻²

**Outputs:**
- εeff vs frequency for each width
- Z₀ vs frequency for each width
- Design curves for impedance matching

**Applications:**
- Impedance-controlled interconnects
- Transmission line design
- Matching network optimization

**Difficulty:** ⭐⭐⭐ Advanced

---

## Quick Reference Table

| **Example** | **Category** | **Difficulty** | **Solve Type** | **Typical Runtime** |
|-------------|--------------|----------------|----------------|---------------------|
| waveguide_modes.py | Basic | ⭐ | Eigenmode | <1 min |
| vary_wavelength.py | Dispersion | ⭐⭐ | Eigenmode sweep | 1-2 min |
| calculate_GVD.py | Dispersion | ⭐⭐⭐ | Eigenmode sweep | 2-5 min |
| fiber_overlap.py | Coupling | ⭐⭐ | Eigenmode + integral | 2-3 min |
| coupled_mode_theory.py | Coupling | ⭐⭐⭐ | Eigenmode + ODE | 5-10 min |
| bragg_filter.py | Periodic | ⭐⭐⭐⭐ | Periodic eigenmode | 3-5 min |
| grating_coupler.py | Periodic | ⭐⭐⭐⭐ | Periodic + PML | 5-10 min |
| metal_heater_phase_shifter.py | Thermo-optic | ⭐⭐⭐ | Thermal + optical | 3-5 min |
| metal_heater_phase_shifter_transient.py | Thermo-optic | ⭐⭐⭐⭐ | Transient thermal | 10-20 min |
| si_heater_phase_shifter.py | Thermo-optic | ⭐⭐⭐ | Thermal + optical | 2-3 min |
| coulomb.py | Electro-optic | ⭐⭐⭐⭐ | Coulomb + optical | 2-5 min |
| microstrip_waveguide_vary_gap.py | RF/Microwave | ⭐⭐⭐ | Eigenmode sweep | 10-20 min |
| microstrip_waveguide_vary_width.py | RF/Microwave | ⭐⭐⭐ | Eigenmode sweep | 5-10 min |

---

## Material Library

### Common Refractive Indices (λ = 1.55 μm)
- **Silicon (Si):** n = 3.4777
- **Silicon Nitride (Si₃N₄):** n = 1.9963
- **Silicon Dioxide (SiO₂):** n = 1.444
- **Lithium Niobate (LiNbO₃):** n = 2.211 (ordinary), 1.989 (extraordinary)
- **Air:** n = 1.0

### Thermal Conductivities
- **Crystalline Silicon:** 148 W/(m·K)
- **Doped Silicon:** 55–90 W/(m·K)
- **Silicon Dioxide:** 1.38 W/(m·K)
- **Titanium Nitride (TiN):** 28 W/(m·K)

### Thermo-Optic Coefficients
- **Silicon:** dn/dT = 1.86×10⁻⁴ K⁻¹
- **Silicon Dioxide:** dn/dT = 1.00×10⁻⁵ K⁻¹

---

## Dependencies

```bash
pip install femwell scikit-fem shapely numpy scipy matplotlib tqdm
```

**Core Libraries:**
- `femwell` - Photonic FEM simulation engine
- `scikit-fem (skfem)` - Finite element framework
- `shapely` - Computational geometry
- `numpy` - Numerical computing
- `scipy` - Scientific algorithms
- `matplotlib` - Visualization
- `tqdm` - Progress bars

---

## Running Examples

All examples are formatted as Jupytext percent-formatted notebooks:

```python
# Direct execution
python example_library/waveguide_modes.py

# Or convert to Jupyter notebook
jupytext --to ipynb example_library/waveguide_modes.py
jupyter notebook example_library/waveguide_modes.ipynb
```

---

## Contributing

When adding new examples, follow this structure:
1. **Header:** Jupyter metadata block
2. **Title:** Markdown cell with example name
3. **Description:** Brief overview and references
4. **Imports:** Organized library imports
5. **Geometry:** Shapely polygon definitions
6. **Mesh:** Resolution specifications
7. **Physics:** Material properties and solver calls
8. **Post-processing:** Calculations and plots
9. **Bibliography:** Citation references

---

## License

These examples are part of the Femwell open-source project. Please cite original papers when using these simulations in research.

For more details: [Femwell Documentation](https://femwell.readthedocs.io/)