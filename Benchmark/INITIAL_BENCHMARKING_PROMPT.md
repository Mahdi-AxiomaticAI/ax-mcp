# Initial Benchmarking Prompt: TiN Metal Heater Phase Shifter

---

## 🎯 Task Overview

**Objective:** Implement and validate a Femwell-based MCP tool for TiN metal heater thermo-optic phase shifters by benchmarking against validated Tidy3D results.

**Priority:** ⭐⭐⭐⭐⭐ HIGH (Phase 1)

**Reference:** Jacques et al., "Optimization of thermo-optic phase-shifter design and mitigation of thermal crosstalk on the SOI platform," *Opt. Express* 27, 10456-10471 (2019).

---

## 📋 Device Specification

### Device: Silicon Strip Waveguide with TiN Metal Heater

**Platform:** Silicon-on-insulator (SOI)

**Operating Wavelength:** λ = 1.55 μm

**Phase Shifter Length:** L = 320 μm

### Geometry Parameters

```
Waveguide (Silicon):
  - Width: 0.5 μm
  - Height: 0.22 μm
  - Material: Crystalline silicon

Heater (TiN):
  - Width: 2.0 μm
  - Height: 0.14 μm (Femwell) / 0.2 μm (Tidy3D)
  - Vertical offset: 2.0 μm above waveguide top surface
  - Material: Titanium nitride (TiN)

Cladding:
  - Material: Silicon dioxide (SiO₂)
  - Surrounding geometry: Box oxide + top cladding
  - Box thickness: 2.0 μm (typical SOI)
  - Top cladding: Sufficient thickness for thermal isolation

Substrate:
  - Material: Silicon
  - Thickness: Semi-infinite (or > 10 μm for simulation)
```

### Material Properties

| **Material** | **Thermal Conductivity κ (W/m·K)** | **Specific Heat c (J/kg·K)** | **Density ρ (kg/m³)** | **Thermo-Optic dn/dT (K⁻¹)** | **Refractive Index n** |
|--------------|-------------------------------------|-------------------------------|------------------------|-------------------------------|------------------------|
| Si (waveguide) | 90 | 711 | 2330 | 1.86×10⁻⁴ | 3.476 @ 1.55 μm |
| Si (substrate) | 148 | 711 | 2330 | - | - |
| TiN (heater) | 28 | 598 | 5240 | - | Metal (use PEC or impedance BC) |
| SiO₂ (cladding) | 1.38 | 709 | 2203 | 1.0×10⁻⁵ | 1.444 @ 1.55 μm |
| Air (if applicable) | 0.026 | 1006 | 1.177 | - | 1.0 |

**Notes:**
- All thermal conductivities in W/(m·K)
- Femwell uses SI units (convert to μm if needed)
- Tidy3D thermo-optic coefficients are linearized at reference temperature

---

## 🔧 Simulation Configuration

### Thermal Simulation (Steady-State)

**Boundary Conditions:**
1. **Bottom boundary (substrate-box interface):**
   - Type: Fixed temperature (Dirichlet BC)
   - Value: T = 300 K (reference temperature)

2. **Top boundary (cladding-air interface):**
   - Type: Convection (Robin BC)
   - Heat transfer coefficient: h = 10 W/(m²·K)
   - Ambient temperature: T_ambient = 300 K

3. **Side boundaries:**
   - Typically: Zero flux (Neumann BC) or far-field approximation

**Heat Source:**
- **Type:** Volumetric heat generation in TiN heater
- **Method 1 (Power-based):**
  - Input: Total electrical power P (mW)
  - Volumetric rate: q = P / V_heater (W/m³)
  - V_heater = width × height × length

- **Method 2 (Current-based):**
  - Input: Current I (mA)
  - Electrical power: P = I² × R
  - Resistance: R = ρ_elec × L / A_cross
  - ρ_elec for TiN: ~1/(2.3×10⁶ S/m) ≈ 4.35×10⁻⁷ Ω·m
  - A_cross = width × height

**Input Sweep:**
- **Power range:** 0 to 30 mW
- **Step size:** 3 mW (11 points) or 2 mW (16 points)
- **Alternatively:** Current 0 to 7.4 mA (if using current-based method)

**Mesh Resolution:**
- **Waveguide region:** < 0.05 μm (fine mesh)
- **Heater region:** < 0.05 μm (fine mesh)
- **Cladding:** 0.1–0.5 μm (coarse mesh away from active region)
- **Substrate:** > 0.5 μm (coarse mesh)

**Solver Settings:**
- Convergence tolerance: 1×10⁻⁶ (temperature residual)
- Solver: Direct or iterative (GMRES, CG)

---

### Optical Simulation (Mode Solving)

**Wavelength:** λ = 1.55 μm (frequency f = c/λ)

**Method:**
- 2D cross-section mode solver (FEM eigenmode analysis)
- Cross-section at center of waveguide (y = 0 or z = 0 depending on coordinate system)

**Perturbed Refractive Index:**
For each temperature field T(x, y):

```
n_perturbed(x, y) = n_0 + (dn/dT) × (T(x, y) - T_ref)
```

Where:
- n_0 = base refractive index at T_ref = 300 K
- dn/dT = thermo-optic coefficient
- T(x, y) = temperature field from thermal simulation

**Mode Solver Configuration:**
- **Number of modes:** 1 (fundamental TE-like mode)
- **Boundary:** PML or metallic boundaries at simulation edges
- **Mesh:** Inherit from thermal simulation or refine further
- **Solve for:** Complex effective index n_eff = n_eff_real + i·n_eff_imag

**Phase Shift Calculation:**
```
Δφ = (2π / λ) × Δn_eff × L
```

Where:
- λ = 1.55 μm
- Δn_eff = n_eff(T) - n_eff(T_ref)
- L = 320 μm (phase shifter length)

**Target:** π-shift (Δφ = π rad) at power P_π

---

## 📊 Expected Outputs

### From Thermal Simulation
For each power level P_i:

1. **Temperature field** T(x, y) [K]
   - 2D array or mesh data
   - Spatial resolution matching mesh

2. **Temperature at waveguide center** T_center [K]
   - Single scalar value at (x=0, y=y_wg_center)

3. **Temperature profile along x-axis** T(x) at y = y_wg_center
   - 1D array for plotting
   - x range: -10 μm to +10 μm (or larger for context)

### From Optical Simulation
For each temperature field (corresponding to power P_i):

1. **Effective refractive index** n_eff [dimensionless]
   - Real part: n_eff_real
   - Imaginary part: n_eff_imag (if material loss included)

2. **Change in effective index** Δn_eff = n_eff(T) - n_eff(T_ref)

3. **Phase shift** Δφ(P) [radians]
   - Calculated from Δn_eff
   - Should show linear relationship with power

4. **Mode profile** E_field or intensity |E|²
   - Optional: for visualization

### Summary Statistics

1. **Power for π-shift:** P_π [mW]
   - Interpolated from Δφ vs P curve where Δφ = π

2. **Thermal efficiency:** dT/dP [K/mW]
   - Slope of T_center vs P

3. **Electro-optic efficiency:** dΔφ/dP [rad/mW]
   - Slope of Δφ vs P

4. **Effective index sensitivity:** dΔn_eff/dP [1/mW]
   - Slope of Δn_eff vs P

---

## ✅ Validation Criteria

Compare Femwell MCP tool results against Tidy3D `TransientThermoOpticShifter.ipynb` (steady-state results):

| **Metric** | **Tidy3D Reference** | **Acceptable Range** | **Weight** |
|------------|----------------------|----------------------|------------|
| **P_π (mW)** | 23.9 mW | 20–27 mW (±15%) | ⭐⭐⭐ Critical |
| **ΔT at P_π (K)** | ~13-15 K | 10–18 K (±20%) | ⭐⭐ Important |
| **Phase shift linearity** | R² > 0.99 | R² > 0.95 | ⭐⭐ Important |
| **Δn_eff slope (per mW)** | ~1.5×10⁻⁵ | ±20% | ⭐ Moderate |
| **Temp profile shape** | Gaussian-like decay | Qualitative match | ⭐ Moderate |

**Pass Criteria:**
- All critical metrics (⭐⭐⭐) within acceptable range
- At least 3 out of 5 metrics pass

**Fail Criteria:**
- P_π outside ±30% range → Implementation error likely
- Non-linear phase shift (R² < 0.9) → Physical model error
- Temperature discontinuities → Meshing or BC error

---

## 📈 Deliverables

### 1. MCP Tool Implementation

**Tool Name:** `simulate_metal_heater_phase_shifter`

**Input Parameters:**
```json
{
  "waveguide_width": 0.5,        // μm
  "waveguide_height": 0.22,      // μm
  "heater_width": 2.0,           // μm
  "heater_height": 0.14,         // μm
  "heater_offset": 2.0,          // μm
  "phase_shifter_length": 320,   // μm
  "wavelength": 1.55,            // μm
  "power_range": [0, 30],        // mW [min, max]
  "num_points": 11,              // number of power steps
  "output_filename": "metal_heater_results.csv"
}
```

**Output File Format (CSV):**
```
power_mW, temp_center_K, delta_neff, phase_shift_rad
0.0, 300.0, 0.0, 0.0
3.0, 301.5, 2.3e-5, 0.29
6.0, 303.0, 4.6e-5, 0.58
...
30.0, 315.0, 2.3e-4, 3.68
```

**Output File Format (JSON):**
```json
{
  "device": {
    "waveguide": {"width": 0.5, "height": 0.22},
    "heater": {"width": 2.0, "height": 0.14, "offset": 2.0},
    "length": 320,
    "wavelength": 1.55
  },
  "results": {
    "power_mW": [0, 3, 6, ..., 30],
    "temp_center_K": [300.0, 301.5, ...],
    "delta_neff": [0.0, 2.3e-5, ...],
    "phase_shift_rad": [0.0, 0.29, ...],
    "P_pi_mW": 24.1,
    "temp_at_pi_K": 313.2
  },
  "temperature_field": {
    "x": [-10, -9.95, ..., 10],  // μm
    "y": [0, 0.05, ..., 5],       // μm
    "T": [[300.0, ...], [...]]     // K (2D array)
  }
}
```

### 2. Comparison Plots

Generate the following plots:

**Plot 1: Phase Shift vs Power**
- X-axis: Heater power (mW)
- Y-axis: Phase shift (rad or rad/π)
- Data: Femwell (solid line) vs Tidy3D (dashed line or markers)
- Annotations: P_π values for both

**Plot 2: Temperature Distribution (2D Heatmap)**
- Cross-section at P = P_π
- Colormap: Temperature (K)
- Show waveguide and heater outlines
- Side-by-side: Femwell vs Tidy3D (if Tidy3D data available)

**Plot 3: Temperature Profile (1D)**
- X-axis: Distance from waveguide center (μm)
- Y-axis: Temperature (K) or ΔT (K)
- Horizontal line at y = waveguide center
- Compare Femwell vs Tidy3D

**Plot 4: Effective Index Change vs Power**
- X-axis: Power (mW)
- Y-axis: Δn_eff
- Linear fit overlay
- R² value annotation

### 3. Quantitative Comparison Table

| **Metric** | **Femwell** | **Tidy3D** | **Relative Error** | **Pass?** |
|------------|-------------|------------|--------------------|-----------|
| P_π (mW) | [value] | 23.9 | [%] | ✅/❌ |
| ΔT at P_π (K) | [value] | ~14 | [%] | ✅/❌ |
| Phase linearity (R²) | [value] | > 0.99 | - | ✅/❌ |
| Δn_eff slope (per mW) | [value] | ~1.5e-5 | [%] | ✅/❌ |
| Overall | - | - | - | ✅/❌ |

### 4. Analysis Report (Markdown)

**Sections:**
1. **Summary:** Pass/fail status, key findings
2. **Methodology:** Brief description of Femwell implementation
3. **Results:** Quantitative metrics and plots
4. **Discussion:**
   - Sources of discrepancy (if any)
   - Sensitivity to geometric differences (heater thickness)
   - Mesh convergence check
5. **Conclusion:** Confidence level in MCP tool
6. **Recommendations:** Next steps or improvements

---

## 🛠️ Implementation Notes

### Femwell API Guidance

**Thermal Simulation (Femwell Heat Solver):**
```python
from femwell.heat import solve_heat_equation

# Define geometry, materials, BCs
thermal_result = solve_heat_equation(
    mesh=mesh,
    materials=materials,
    heat_sources=heat_sources,
    boundary_conditions=boundary_conditions
)

# Extract temperature field
T_field = thermal_result.temperature
```

**Optical Mode Solving (Femwell Mode Solver):**
```python
from femwell.maxwell.waveguide import compute_modes

# Apply temperature perturbation to refractive index
n_perturbed = n_base + dn_dT * (T_field - T_ref)

# Solve modes with perturbed index
modes = compute_modes(
    wavelength=1.55,
    mesh=mesh,
    epsilon=n_perturbed**2,
    num_modes=1
)

# Extract effective index
n_eff = modes[0].n_eff
```

### Common Pitfalls

1. **Unit Conversion:**
   - Ensure all lengths in μm consistently
   - Thermal conductivity: W/(m·K) → may need conversion if using μm-based system

2. **Coordinate Systems:**
   - Femwell may use (x, y) for cross-section
   - Tidy3D may use (x, z) or (y, z)
   - Check which axis is propagation direction

3. **Boundary Condition Application:**
   - Convection BC: Ensure correct heat transfer coefficient units
   - Fixed temperature: Apply at correct geometric boundary

4. **Mesh Quality:**
   - Check for element distortion near heater edges
   - Refine mesh if temperature gradients are steep

5. **Material Assignment:**
   - TiN heater: Metal (infinite conductivity for DC) or use resistivity
   - Ensure no overlapping material regions

### Debugging Checklist

- [ ] Temperature field converges (residual < tolerance)
- [ ] Temperature is physically reasonable (no negative values, < 1000 K)
- [ ] Phase shift increases monotonically with power
- [ ] P_π is in reasonable range (10-50 mW)
- [ ] Mode profile looks correct (confined to waveguide)
- [ ] CSV output format matches specification
- [ ] Plots render without errors

---

## 🚀 Execution Steps

### Step 1: Implement MCP Tool
1. Create Python module with Femwell simulation logic
2. Define MCP tool interface with input/output schema
3. Add parameter validation and error handling
4. Test with single power point (e.g., P = 10 mW)

### Step 2: Run Full Sweep
1. Execute MCP tool with power range 0-30 mW
2. Save outputs to CSV and JSON
3. Verify all data is populated correctly

### Step 3: Generate Comparison Plots
1. Load Tidy3D reference data (from notebook or CSV)
2. Create comparison plots (4 plots minimum)
3. Save plots as PNG or PDF

### Step 4: Calculate Metrics
1. Interpolate P_π from phase shift data
2. Compute slopes (temperature, phase, index)
3. Calculate R² for linear fits
4. Populate comparison table

### Step 5: Write Analysis Report
1. Generate markdown report with all sections
2. Include plots as embedded images
3. Add pass/fail assessment
4. Provide recommendations

### Step 6: Iterate if Needed
1. If validation fails, debug MCP tool
2. Check mesh convergence
3. Verify material properties
4. Re-run and compare

---

## 📚 References

1. **Primary Reference:**
   - Jacques, M., et al. "Optimization of thermo-optic phase-shifter design and mitigation of thermal crosstalk on the SOI platform." *Opt. Express* **27**, 10456-10471 (2019).
   - DOI: [10.1364/OE.27.010456](https://doi.org/10.1364/OE.27.010456)

2. **Femwell Documentation:**
   - [Femwell Heat Solver](https://femwell.readthedocs.io/en/latest/heat/)
   - [Femwell Mode Solver](https://femwell.readthedocs.io/en/latest/maxwell/waveguide/)

3. **Tidy3D Reference:**
   - Notebook: `TransientThermoOpticShifter.ipynb`
   - Location: `Tidy3D/example_library/TransientThermoOpticShifter.ipynb`

4. **Material Properties:**
   - Silicon thermal conductivity: Glassbrenner & Slack, Phys. Rev. 134, A1058 (1964)
   - Thermo-optic coefficients: Handbook of Optical Constants (Palik)

---

## ✉️ Contact & Support

For questions or issues during implementation:
- Consult Femwell documentation and examples
- Review Tidy3D notebook for implementation details
- Check material property databases for validation

---

**Status:** Ready for implementation
**Priority:** Phase 1, High Priority
**Estimated Time:** 2-4 hours (implementation) + 1-2 hours (validation)