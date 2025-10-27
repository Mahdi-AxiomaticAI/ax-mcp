# Femwell vs Tidy3D Benchmarking Analysis

This document identifies cross-compatible examples between Femwell (FEM-based) and Tidy3D (FDTD-based) simulation libraries that can be benchmarked against each other.

---

## 🎯 Objective

Create MCP tools from Femwell examples and validate their results against equivalent Tidy3D simulations to:
1. Verify accuracy of MCP tool implementations
2. Compare FEM vs FDTD solver performance
3. Establish confidence in automated simulation workflows
4. Identify strengths/limitations of each approach

---

## 📊 Benchmarkable Example Pairs

### 1. **Thermo-Optic Phase Shifters (TiN Metal Heater)** ⭐⭐⭐⭐⭐ HIGH PRIORITY

| **Attribute** | **Femwell** | **Tidy3D** |
|---------------|-------------|------------|
| **Example** | `metal_heater_phase_shifter.py` | `TransientThermoOpticShifter.ipynb` |
| **Category** | Thermo-Optic Devices | Thermo-Optic Devices |
| **Waveguide** | 0.5 μm × 0.22 μm Si | 0.5 μm × 0.22 μm Si |
| **Heater** | 2 μm × 0.14 μm TiN, 2 μm offset | 2 μm × 0.2 μm TiN, 2 μm offset |
| **Length** | 320 μm | 320 μm |
| **Wavelength** | 1.55 μm | 1.55 μm |
| **Materials** | Si (κ=90), TiN (κ=28), SiO₂ (κ=1.38) W/(m·K) | Si (κ=90), TiN (κ=28), SiO₂ (κ=1.38) W/(m·K) |
| **Thermo-optic** | Si: dn/dT = 1.86×10⁻⁴ K⁻¹ | Si: dn/dT = 1.8×10⁻⁴ K⁻¹ |
| **Input** | Current: 0–7.4 mA | Power: 0–30 mW (→ Pπ = 23.9 mW) |
| **Physics** | Thermal + Optical (steady-state) | Thermal + Optical (steady + transient) |
| **Solver** | FEM (Femwell) | FEM Heat + Mode (Tidy3D) |
| **Reference** | Jacques et al., Opt. Express 27, 10456 (2019) | Jacques et al., Opt. Express 27, 10456 (2019) |

**Comparable Outputs:**
- ✅ Temperature distribution T(x, y)
- ✅ Effective refractive index neff vs power
- ✅ Phase shift Δφ vs power
- ✅ Power for π-shift (Pπ)
- ✅ Temperature profile along x-axis

**Validation Metrics:**
- Temperature at waveguide center
- neff change per mW
- Pπ value (should be ~23-24 mW)
- Spatial temperature distribution

**Compatibility:** ✅ **EXCELLENT** - Same reference paper, nearly identical geometry

---

### 2. **Thermo-Optic Phase Shifters (Doped Silicon Heater)** ⭐⭐⭐⭐ HIGH PRIORITY

| **Attribute** | **Femwell** | **Tidy3D** |
|---------------|-------------|------------|
| **Example** | `si_heater_phase_shifter.py` | `TransientThermoOpticShifter.ipynb` (rib variant) |
| **Category** | Thermo-Optic Devices | Thermo-Optic Devices |
| **Waveguide** | 0.5 μm × 0.22 μm Si core | 0.5 μm × 0.22 μm Si core + 0.09 μm slab |
| **Heater** | 1 μm × 0.09 μm doped Si (symmetric) | 1 μm × 0.09 μm N++ Si (symmetric) |
| **Buffer** | 0.8 μm from core | 0.8 μm from core |
| **Power** | 25.2 mW | Pπ = 25.2 mW |
| **Materials** | Si (κ=90), Doped Si (κ=55), SiO₂ (κ=1.38) | Si (κ=90), N++ Si (κ=25), SiO₂ (κ=1.38) |
| **Physics** | Thermal + Optical | Thermal + Optical (steady + transient) |
| **Reference** | Jacques et al., Opt. Express 27, 10456 (2019) | Jacques et al., Opt. Express 27, 10456 (2019) |

**Comparable Outputs:**
- ✅ Temperature distribution T(x, y)
- ✅ Phase shift vs power
- ✅ Pπ value (should be ~25 mW)
- ✅ Attenuation due to doping

**Validation Metrics:**
- Pπ agreement
- Temperature distribution shape
- Optical loss comparison
- Thermal time constant (Tidy3D transient only)

**Compatibility:** ✅ **EXCELLENT** - Same reference paper, nearly identical design

**Note:** Femwell uses κ=55 W/(m·K) for doped Si, Tidy3D uses κ=25 W/(m·K) for N++ Si (higher doping)

---

### 3. **Bragg Gratings / Periodic Structures** ⭐⭐⭐ MEDIUM PRIORITY

| **Attribute** | **Femwell** | **Tidy3D** |
|---------------|-------------|------------|
| **Example** | `bragg_filter.py` | `BraggGratings.ipynb` |
| **Category** | Periodic Structures | Photonic Waveguides & Gratings |
| **Method** | Periodic mode solver (Bloch) | FDTD with periodic boundaries |
| **Physics** | Eigenmode analysis | Full-wave time-domain |
| **Outputs** | Band structure, photonic bandgaps | Transmission/reflection spectra |

**Comparable Outputs:**
- ⚠️ Band structure → Transmission spectrum (indirect comparison)
- ⚠️ Bandgap location and width
- ⚠️ Mode profiles

**Validation Metrics:**
- Bandgap center wavelength
- Bandgap width
- Stopband rejection ratio (Tidy3D)

**Compatibility:** ⚠️ **MODERATE** - Different solver approaches, indirect comparison

**Challenge:** FEM periodic mode solver vs FDTD spectral analysis require different interpretation

---

### 4. **RF/Microwave Transmission Lines** ⭐⭐ LOW-MEDIUM PRIORITY

| **Attribute** | **Femwell** | **Tidy3D** |
|---------------|-------------|------------|
| **Example** | `microstrip_waveguide_vary_gap.py`, `microstrip_waveguide_vary_width.py` | `CPWRFPhotonics1.ipynb` |
| **Category** | RF/Microwave Structures | RF & Microwave Devices |
| **Device** | Microstrip (single/coupled) | Co-planar waveguide (CPW) |
| **Method** | 2D FEM mode solver | 2D Mode + 3D FDTD |
| **Frequency** | 1–16 GHz | 1–65 GHz |

**Comparable Outputs:**
- ⚠️ Effective permittivity εeff vs frequency (different structures)
- ⚠️ Characteristic impedance Z₀ (microstrip vs CPW)

**Compatibility:** ❌ **POOR** - Different transmission line types (microstrip vs CPW)

**Not Recommended:** Structures are fundamentally different

---

## ❌ Non-Benchmarkable Examples

### Reason: Different Physics or Applications

1. **Grating Couplers**
   - Femwell: `grating_coupler.py` (vertical coupling with PML)
   - Tidy3D: `BiosensorGrating.ipynb` (sensing application)
   - **Issue:** Different applications and design goals

2. **Electro-Optic Devices**
   - Femwell: `coulomb.py` (LiNbO₃ Pockels effect)
   - Tidy3D: No equivalent
   - **Issue:** No Tidy3D example for electro-optic modulators

3. **Basic Waveguide Modes**
   - Femwell: `waveguide_modes.py` (Si₃N₄, 2.5×0.3 μm)
   - Tidy3D: No direct equivalent
   - **Issue:** Different materials, but could create custom benchmark

4. **Charge Transport**
   - Femwell: No charge solver
   - Tidy3D: `ThermoOpticDopedModulator.ipynb` (includes charge simulation)
   - **Issue:** Femwell doesn't have charge transport solver

5. **MZI Modulators**
   - Femwell: `coupled_mode_theory.py` (directional coupler component)
   - Tidy3D: `MachZehnderModulator.ipynb` (full MZI device)
   - **Issue:** Component vs full device simulation

---

## 🎯 Recommended Benchmarking Strategy

### **Phase 1: High-Confidence Validation** (Priority 1)
**Focus:** Thermo-optic phase shifters with identical reference paper

1. ✅ **TiN Metal Heater (Steady-State)**
   - Implement Femwell `metal_heater_phase_shifter.py` as MCP tool
   - Compare against Tidy3D `TransientThermoOpticShifter.ipynb` (steady-state results)
   - **Expected Agreement:** Within 5-10% for Pπ, temperature, phase shift

2. ✅ **Doped Silicon Heater**
   - Implement Femwell `si_heater_phase_shifter.py` as MCP tool
   - Compare against Tidy3D rib waveguide variant
   - **Expected Agreement:** Within 10-15% (different doping conductivities)

**Success Criteria:**
- Pπ values match within 15%
- Temperature profiles show similar spatial distribution
- Phase shift vs power shows linear relationship with similar slope

---

### **Phase 2: Exploratory Validation** (Priority 2)
**Focus:** Bragg gratings and periodic structures

3. ⚠️ **Bragg Gratings**
   - Implement Femwell `bragg_filter.py` as MCP tool
   - Compare bandgap predictions with Tidy3D transmission spectra
   - **Expected Agreement:** Qualitative comparison of stopband location/width

**Success Criteria:**
- Bandgap center wavelength within 5%
- Bandgap width within 20%
- Qualitative agreement on mode structure

---

### **Phase 3: Method Comparison** (Priority 3 - Optional)
**Focus:** Understanding solver differences

4. ⚠️ **Create Custom Benchmark**
   - Design identical Si or Si₃N₄ waveguide for both solvers
   - Compare: neff, ng, mode profiles, dispersion
   - **Goal:** Understand FEM vs FDTD mode solver differences

---

## 📝 Initial Prompt Template for Benchmarking

```markdown
# Thermo-Optic Phase Shifter Benchmarking Request

## Objective
Compare the Femwell FEM-based thermo-optic phase shifter simulation against the validated Tidy3D FDTD results from Jacques et al. (2019).

## Device Configuration: TiN Metal Heater

### Geometry
- **Waveguide:** 0.5 μm (width) × 0.22 μm (height) silicon
- **Heater:** 2 μm (width) × 0.14-0.2 μm (height) TiN
- **Heater offset:** 2 μm above waveguide top surface
- **Phase shifter length:** 320 μm
- **Wavelength:** 1.55 μm

### Material Properties
| Material | Thermal Conductivity (W/m·K) | Thermo-Optic Coeff (K⁻¹) |
|----------|------------------------------|---------------------------|
| Si (waveguide) | 90 | 1.86×10⁻⁴ |
| TiN (heater) | 28 | - |
| SiO₂ (cladding) | 1.38 | 1.0×10⁻⁵ |

### Boundary Conditions
- **Bottom (substrate interface):** Fixed temperature 300 K
- **Top (SiO₂/air interface):** Convection with h = 10 W/(m²·K), T_ambient = 300 K

### Input Parameters to Sweep
- **Heater power:** 0 to 30 mW (10 steps)
- Alternatively: Current 0 to 7.4 mA (convert to power: P = I²R)

### Expected Outputs
1. **Temperature distribution** T(x, y) at steady state for each power level
2. **Temperature at waveguide center** vs power
3. **Effective refractive index change** Δneff vs power
4. **Phase shift** Δφ = (2π/λ) × Δneff × L vs power
5. **Power for π-shift (Pπ):** Should be approximately 23-24 mW

### Validation Criteria
Compare Femwell MCP tool results against Tidy3D `TransientThermoOpticShifter.ipynb`:

| Metric | Target Value (Tidy3D) | Acceptable Range |
|--------|------------------------|------------------|
| Pπ (mW) | 23.9 | 20–27 mW (±15%) |
| ΔT at center (K) for Pπ | ~13-15 K | ±20% |
| Δneff slope (per mW) | ~1.5×10⁻⁵ per mW | ±20% |
| Phase shift linearity | R² > 0.99 | R² > 0.95 |

### Reference Benchmark Data
- **Paper:** Jacques et al., Opt. Express 27, 10456-10471 (2019)
- **Tidy3D notebook:** `TransientThermoOpticShifter.ipynb`
- **Femwell example:** `metal_heater_phase_shifter.py`

### Deliverables
1. Femwell MCP tool implementation
2. Comparison plots:
   - Temperature distribution (2D heatmap)
   - Phase shift vs power (Femwell vs Tidy3D)
   - Temperature profile along x-axis at y=0
3. Quantitative comparison table
4. Analysis of discrepancies (if any)

### Notes
- Both simulations reference the same Jacques et al. (2019) paper
- Tidy3D includes both steady-state and transient analysis; compare only steady-state
- Small geometry differences (heater thickness: 0.14 μm vs 0.2 μm) may cause minor variations
```

---

## 🔧 Implementation Approach

### Step 1: MCP Tool Creation
For each Femwell example:
1. Extract core simulation logic from Python script
2. Define MCP tool interface with parameters:
   - Geometry (waveguide dimensions, heater dimensions, offset)
   - Materials (thermal conductivity, thermo-optic coefficients)
   - Boundary conditions (temperature, convection)
   - Input sweep (power or current range)
3. Return structured outputs:
   - Temperature field data
   - Effective index data
   - Phase shift calculations
   - Summary statistics

### Step 2: Automated Benchmarking
1. Run Femwell MCP tool with same parameters as Tidy3D
2. Extract Tidy3D results from notebook outputs
3. Generate comparison plots automatically
4. Calculate quantitative metrics:
   - Relative error for Pπ
   - RMSE for temperature profiles
   - Correlation coefficient for phase shift linearity

### Step 3: Validation Report
Generate markdown report with:
- Parameter summary
- Side-by-side comparison plots
- Quantitative error metrics
- Pass/fail assessment based on validation criteria
- Discussion of discrepancies

---

## 📈 Expected Outcomes

### Success Scenarios
1. **Excellent Agreement (< 10% error):**
   - Validates MCP tool implementation
   - Confirms FEM solver accuracy
   - Provides confidence for automated workflows

2. **Good Agreement (10-20% error):**
   - Identifies minor geometric or material differences
   - Highlights solver-specific approximations
   - Still useful for design exploration

3. **Moderate Agreement (20-30% error):**
   - Requires investigation of discrepancies
   - May reveal bugs in MCP implementation
   - Could indicate fundamental solver differences

### Failure Scenarios
1. **Poor Agreement (> 30% error):**
   - Likely implementation error in MCP tool
   - Possible misinterpretation of Femwell API
   - Requires debugging and code review

2. **Qualitative Mismatch:**
   - Different trends (non-linear vs linear)
   - Indicates fundamental issue
   - May require expert consultation

---

## 🚀 Next Steps

1. **Prioritize TiN heater benchmark** (highest confidence, same reference paper)
2. **Implement Femwell MCP tool** for `metal_heater_phase_shifter.py`
3. **Extract Tidy3D reference data** from `TransientThermoOpticShifter.ipynb`
4. **Run automated comparison** with validation criteria
5. **Generate report** and assess results
6. **Iterate** on doped silicon heater (second benchmark)
7. **Document findings** for future MCP tool development

---

## 📚 References

1. Jacques, M., et al. "Optimization of thermo-optic phase-shifter design and mitigation of thermal crosstalk on the SOI platform." *Opt. Express* 27, 10456-10471 (2019).
   - Used by both Femwell and Tidy3D examples
   - Provides experimental validation data

2. Femwell Documentation: https://femwell.readthedocs.io/
3. Tidy3D Documentation: https://docs.flexcompute.com/projects/tidy3d/