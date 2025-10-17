## Axiomatic Femwell MCP Server

This MCP server exposes Femwell-based calculations for depletion waveguide modulators with PN junctions. It computes effective index and absorption as a function of applied voltage, enabling phase and amplitude modulation analysis. Results are saved to `mcp_output/` in the current working directory.

### Tool: `simulate_depletion_modulator`
Compute effective index change and absorption vs voltage for a silicon photonic depletion modulator using Femwell's finite element mode solver with carrier-induced index perturbations.

- **Outputs**:
  - **CSV**: `depletion_modulator_results.csv` (columns: `voltage_V, neff_real, neff_imag, neff_change, absorption_dB_per_cm`)
  - **PNG**: `depletion_modulator_modulation.png` (phase modulation and absorption plots)
  - **PNG**: `depletion_modulator_epsilon_V{voltage}.png` (epsilon distribution at specified voltage, if enabled)
  - **Python**: `depletion_modulator_simulation.py` (reproducible simulation code)

### Arguments
- **Voltage sweep**
  - `voltages` (list[float]): List of voltages to sweep (V). Default: `[-3, -2, -1, 0, 1, 2, 3]`
- **PN junction parameters**
  - `xpn` (float): PN junction position in µm. Default: `0.0`
  - `NA` (float): Acceptor doping concentration (cm⁻³). Default: `1e18`
  - `ND` (float): Donor doping concentration (cm⁻³). Default: `1e18`
- **Operating wavelength**
  - `wavelength` (float): Wavelength in micrometers. Default: `1.55`
- **Geometry (µm)**
  - `wg_width`: Waveguide core width. Default: `0.5`
  - `wg_thickness`: Waveguide core thickness. Default: `0.22`
  - `slab_width`: Slab region width. Default: `3.0`
  - `slab_thickness`: Slab region thickness. Default: `0.09`
  - `clad_thickness`: Cladding thickness. Default: `2.0`
- **Material indices**
  - `core_index` (float): Refractive index of core (e.g., silicon). Default: `3.45`
  - `slab_index` (float): Refractive index of slab. Default: `3.45`
  - `clad_index` (float): Refractive index of cladding (e.g., SiO₂). Default: `1.444`
- **Mode solver parameters**
  - `num_modes` (int): Number of modes to compute. Default: `1`
  - `mode_order` (int): FEM mode solver order. Default: `2`
- **Plotting options**
  - `enable_epsilon_plot` (bool): Save epsilon distribution plot. Default: `false`
  - `epsilon_plot_voltage` (float): Voltage for epsilon plot (V). Default: `0.0`
- **Outputs**
  - `output_prefix` (str): Prefix for saved CSV/PNG files under `mcp_output/`. Default: `"depletion_modulator"`

### Physics Model
The tool uses Femwell's analytical PN junction model to compute carrier-induced refractive index changes:

- **Phase modulation**: Δn_eff = Re(n_eff(V)) - Re(n_eff(0))
- **Absorption**: α(V) = 4π·Im(n_eff(V))/λ [converted to dB/cm]

The PN junction creates a voltage-dependent depletion region that modulates the local refractive index and introduces free-carrier absorption. The mode solver computes the effective index of the fundamental mode including these perturbations.

### Usage
#### Register the server
Ensure your client registers the server (example `mcp.json` entry):

```json
{
  "mcpServers": {
    "axiomatic-femwell": {
      "command": "python",
      "args": ["-m", "axiomatic_mcp.servers.femwell"],
      "env": {}
    }
  }
}
```

#### Call the tool
From an MCP-enabled client, invoke `simulate_depletion_modulator` with desired arguments. Example:

```json
{
  "name": "simulate_depletion_modulator",
  "arguments": {
    "voltages": [-3, -2, -1, 0, 1, 2, 3],
    "xpn": 0.0,
    "NA": 1e18,
    "ND": 1e18,
    "wavelength": 1.55,
    "wg_width": 0.5,
    "wg_thickness": 0.22,
    "slab_width": 3.0,
    "slab_thickness": 0.09,
    "clad_thickness": 2.0,
    "core_index": 3.45,
    "slab_index": 3.45,
    "clad_index": 1.444,
    "num_modes": 1,
    "mode_order": 2,
    "enable_epsilon_plot": true,
    "epsilon_plot_voltage": -2.0,
    "output_prefix": "my_modulator"
  }
}
```

### Dependencies
- **Python**: 3.10+
- **Packages**: `femwell`, `shapely`, `scikit-fem`, `numpy`, `matplotlib`, `meshio`

Install (example):
```bash
pip install femwell shapely scikit-fem numpy matplotlib meshio
```

Note: This repository does not pin `femwell` as a hard dependency to allow server registration without it; imports happen lazily inside tool functions.

### Typical Performance Metrics
For a standard lateral PN junction depletion modulator:
- **Phase efficiency**: ~0.5-2 × 10⁻⁵ Δn_eff per volt
- **Absorption**: 10-50 dB/cm at reverse bias
- **V_π·L**: ~2-5 V·mm (for π phase shift)

These values depend strongly on doping profiles, junction position, and waveguide geometry.

### Notes
- **PN Junction Position** (`xpn`): Controls where the junction intersects the waveguide. For lateral junctions, `xpn = 0` centers it in the waveguide.
- **Doping Concentrations**: Higher doping (NA, ND) increases phase efficiency but also increases absorption.
- **Mesh Resolution**: The default mesh parameters balance accuracy and computation time. For high-accuracy studies, consider reducing `core_resolution` in the mesh generation.
- **Outputs** are created in `mcp_output/` with the chosen `output_prefix`.
- **Epsilon Plots** show the real and imaginary parts of the permittivity distribution, useful for visualizing the depletion region and carrier distribution.

### References
- Femwell documentation: https://helgegehring.github.io/femwell/
- PN junction modulator theory: Soref & Bennett, IEEE J. Quantum Electron. 23, 123 (1987)
