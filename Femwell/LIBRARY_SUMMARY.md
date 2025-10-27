# Femwell Example Library

This directory contains a comprehensive collection of photonic simulation examples using the Femwell framework. These examples demonstrate various optical and electro-optical device simulations using finite element methods (FEM).

## Overview

Femwell is a Python library for simulating photonic devices using finite element methods. The examples in this library cover waveguide modes, thermal effects, electro-optic effects, coupling, dispersion, and periodic structures.

---

## Examples Summary

### 1. **waveguide_modes.py**
**Category:** Basic Waveguide Analysis

**Description:** Demonstrates fundamental optical waveguide mode calculations for a silicon nitride waveguide.

**Key Features:**
- Calculates effective refractive index of waveguide modes
- Computes mode field profiles (E-field, intensity)
- Calculates power confinement and confinement factors
- Geometry: 2.5 μm × 0.3 μm silicon nitride core

**Use Case:** Starting point for understanding waveguide mode calculations and field visualization.

---

### 2. **vary_wavelength.py**
**Category:** Dispersion Analysis

**Description:** Analyzes wavelength-dependent properties of silicon nitride waveguides, including dispersion characteristics.

**Key Features:**
- Wavelength sweep from 1.2 to 1.9 μm
- Calculates effective refractive index vs wavelength
- Computes group velocity and group velocity dispersion (GVD)
- Material dispersion using Sellmeier equations for Si₃N₄ and SiO₂

**Use Case:** Design of dispersion-engineered waveguides for nonlinear optics and broadband applications.

---

### 3. **calculate_GVD.py**
**Category:** Dispersion Engineering

**Description:** Reproduces Figure 2e from Klenner et al. (2016), calculating group velocity dispersion for silicon nitride waveguides.

**Key Features:**
- Detailed GVD calculation from 500 to 2500 nm
- Second derivative fitting for accurate dispersion parameter extraction
- Validation against published reference data
- Waveguide geometry: 0.88 μm × 0.69 μm Si₃N₄

**Use Case:** Precision dispersion engineering for ultrafast optics and frequency comb applications.

---

### 4. **fiber_overlap.py**
**Category:** Coupling Efficiency

**Description:** Calculates overlap integral between waveguide modes and Gaussian fiber modes.

**Key Features:**
- Mode field diameter (MFD) sweep from 2 to 20 μm
- Coupling efficiency calculation using overlap integrals
- Small silicon nitride waveguide (0.2 μm × 0.3 μm)
- Optimal fiber coupling design

**Use Case:** Design of fiber-to-chip coupling interfaces and optimization of coupling efficiency.

---

### 5. **coupled_mode_theory.py**
**Category:** Directional Couplers

**Description:** Simulates coupled waveguides using coupled mode theory for directional coupler design.

**Key Features:**
- Two-waveguide system with different widths (0.45 μm and 0.46 μm)
- Coupling coefficient calculation
- Power transfer length calculation
- Symmetric and asymmetric mode analysis

**Use Case:** Design of optical couplers, switches, and interferometric devices. (Note: Example marked as under construction)

---

### 6. **grating_coupler.py**
**Category:** Periodic Structures

**Description:** Reproduces grating coupler simulation from Notaros et al. (2015) using 2D periodic mode solver.

**Key Features:**
- Periodic boundary conditions with unit cell period a = 0.47 μm
- Grating structure with etched holes
- Complex eigenmode solving for leaky modes
- Perfectly matched layer (PML) implementation

**Use Case:** Design of surface grating couplers for vertical fiber coupling.

---

### 7. **bragg_filter.py**
**Category:** Periodic Structures

**Description:** Simulates Bragg filters using 2D periodic mode solver.

**Key Features:**
- Periodic structure analysis with waveguide + hole geometry
- Band structure calculation
- Complex mode visualization
- References Notaros et al. (2015)

**Use Case:** Design of wavelength-selective Bragg filters and photonic crystal devices.

---

### 8. **metal_heater_phase_shifter.py**
**Category:** Thermo-Optic Devices (Steady-State)

**Description:** Simulates TiN (titanium nitride) metal heater-based thermal phase shifter, reproducing Jacques et al. (2019).

**Key Features:**
- Coupled thermal-optical simulation
- Current density sweep up to 7.4 mA
- Temperature distribution calculation
- Phase shift calculation over 320 μm length
- Silicon waveguide with TiN resistive heater

**Thermal Properties:**
- Core (Si): 90 W/m·K
- Heater (TiN): 28 W/m·K, conductivity 2.3×10⁶ S/m
- Box/Clad (SiO₂): 1.38 W/m·K

**Use Case:** Design of low-power thermal phase shifters for programmable photonics.

---

### 9. **metal_heater_phase_shifter_transient.py**
**Category:** Thermo-Optic Devices (Transient)

**Description:** Time-domain simulation of TiN TOPS heater dynamics.

**Key Features:**
- Transient thermal diffusion analysis
- Time-resolved temperature evolution
- Dynamic phase shift calculation
- Pulsed current excitation (10% and 50% duty cycle)
- Perturbation theory for fast neff approximation

**Simulation Parameters:**
- Time step: 0.1 μs
- Total steps: 100
- Thermal diffusivity included for all materials

**Use Case:** Analysis of switching speed and thermal time constants for reconfigurable photonics.

---

### 10. **si_heater_phase_shifter.py**
**Category:** Thermo-Optic Devices

**Description:** Simulates doped silicon heater-based thermal phase shifter from Jacques et al. (2019).

**Key Features:**
- Integrated doped silicon resistive heaters
- Lower thermal conductivity design (55 W/m·K for doped Si)
- Symmetric heater placement on both sides of waveguide
- Power dissipation: 25.2 mW

**Heater Configuration:**
- Heater width: 1 μm, thickness: 0.09 μm
- Buffer region: 0.8 μm
- Specific conductivity: 1×10⁵ S/m

**Use Case:** Compact, CMOS-compatible thermal phase shifters with simplified fabrication.

---

### 11. **coulomb.py**
**Category:** Electro-Optic Devices

**Description:** Simulates lithium niobate (LiNbO₃) electro-optic phase shifter using Coulomb/Poisson solver, reproducing Han et al. (2022).

**Key Features:**
- Electric field calculation via Coulomb solver
- Pockels effect simulation (electro-optic coefficient r₃₃ = 31 pm/V)
- Voltage-dependent effective refractive index
- Electrode configuration analysis

**Material Properties:**
- Core (x-cut LiNbO₃): n = 1.989, ε_dc = 7.5
- Slab (thin film LiNbO₃): n = 2.211, ε_dc = 28.4
- Electrode gap: optimized for efficient field overlap

**Use Case:** High-speed electro-optic modulators for telecommunications.

---

### 12. **microstrip_waveguide_vary_gap.py**
**Category:** RF/Microwave Structures

**Description:** Analyzes coupled microstrip transmission lines with varying gap spacing.

**Key Features:**
- Gap sweep from 0.02 to 2 mm
- Frequency sweep from 1 to 16 GHz
- Effective dielectric constant calculation
- Metallic boundary conditions
- Even and odd mode analysis

**Geometry:**
- Strip width: 0.6 mm
- Substrate thickness: 0.64 mm (εᵣ = 9.9)
- Conductor thickness: 0.005 mm

**Use Case:** Design of RF couplers and analysis of crosstalk in high-speed interconnects.

---

### 13. **microstrip_waveguide_vary_width.py**
**Category:** RF/Microwave Structures

**Description:** Calculates effective epsilon and characteristic impedance of microstrip lines vs width.

**Key Features:**
- Width sweep from 0.04 to 3 mm
- Frequency-dependent effective permittivity
- Characteristic impedance calculation using current integration
- Validation against Jansen et al. (1978)

**Use Case:** Impedance-controlled RF transmission line design and matching network optimization.

---

## Technical Details

### Common Dependencies
All examples use the following core libraries:
- **femwell**: Core FEM simulation engine for photonics
- **scikit-fem (skfem)**: Finite element mesh and basis functions
- **shapely**: Geometric operations and polygon definitions
- **numpy**: Numerical computations
- **matplotlib**: Visualization and plotting
- **scipy**: Scientific computing utilities
- **tqdm**: Progress bars for iterative simulations

### Simulation Workflow
1. **Geometry Definition:** Use shapely to define polygons and domains
2. **Mesh Generation:** Create finite element mesh with domain-specific resolution
3. **Material Assignment:** Set refractive indices, thermal conductivities, etc.
4. **Solver Execution:** Run Maxwell, thermal, or Coulomb solvers
5. **Post-Processing:** Calculate derived quantities and visualize results

### Resolution Guidelines
- Core waveguide regions: 0.01–0.05 μm
- Cladding regions: 0.1–0.6 μm
- Substrate/background: 0.2–10 μm
- Refine near interfaces and field hotspots

---

## References

Key papers reproduced or cited in these examples:
- Jacques et al., Opt. Express 27, 10456 (2019) - TiN and Si heaters
- Han et al., Opt. Express 30, (2022) - LiNbO₃ phase shifters
- Klenner et al., Opt. Express 24, (2016) - Si₃N₄ dispersion
- Notaros et al., IEEE J. Sel. Top. Quantum Electron. 21, (2015) - Gratings and Bragg filters
- Jansen et al., IEEE Trans. Microwave Theory Tech. 26, (1978) - Microstrip analysis

---

## Getting Started

To run any example:

```python
# Install dependencies
pip install femwell scikit-fem shapely numpy scipy matplotlib tqdm

# Run an example
python waveguide_modes.py
```

Most examples are formatted as Jupyter notebooks (using jupytext percent format) and can be opened directly in Jupyter or converted to .ipynb format.

---

## Device Categories

| **Category**                  | **Examples**                                                                 |
|-------------------------------|------------------------------------------------------------------------------|
| Basic Waveguide Analysis      | waveguide_modes.py                                                           |
| Dispersion Engineering        | vary_wavelength.py, calculate_GVD.py                                         |
| Coupling & Overlap            | fiber_overlap.py, coupled_mode_theory.py                                     |
| Periodic Structures           | grating_coupler.py, bragg_filter.py                                          |
| Thermo-Optic Devices          | metal_heater_phase_shifter.py, metal_heater_phase_shifter_transient.py, si_heater_phase_shifter.py |
| Electro-Optic Devices         | coulomb.py                                                                   |
| RF/Microwave Structures       | microstrip_waveguide_vary_gap.py, microstrip_waveguide_vary_width.py         |

---

## License & Attribution

These examples are part of the Femwell library. Please cite the original papers when using these examples in your research.

For more information, visit the [Femwell documentation](https://femwell.readthedocs.io/).
