## Axiomatic Tidy3D MCP Server

This MCP server exposes compact Tidy3D-based calculations for waveguide couplers (two parallel rectangular dielectric waveguides). It computes coupling vs wavelength, coupling vs length, and can export mode field plots. Results are saved to `mcp_output/` in the current working directory.

### Tool: `simulate_waveguide_coupler`
Compute evanescent coupling using Tidy3D's rectangular dielectric waveguide mode solver and save results.

- **Outputs**:
  - **CSV**: `wg_coupler_coupling_vs_wavelength.csv` (columns: `wavelength_um, power_coupling`)
  - **CSV**: `wg_coupler_coupling_vs_length.csv` (columns: `length_um, power_coupling`)
  - **PNG**: `wg_coupler_coupling_vs_wavelength.png` and `wg_coupler_coupling_vs_length.png`
  - **PNG**: `wg_coupler_modes_Ey.png` (when mode plots are enabled)

### Arguments
- **Materials**
  - `core_material_family` (str): e.g., `"cSi"` or `"Si3N4"`
  - `core_material_model` (str): e.g., `"Palik_Lossless"`
  - `clad_material_family` (str): e.g., `"SiO2"`
  - `clad_material_model` (str): e.g., `"Palik_Lossless"`
- **Geometry (µm)**
  - `wg_width1_um`, `wg_width2_um`: core widths
  - `wg_height_um`: core thickness
  - `wg_gap_um`: center gap between the cores
  - `coupler_length_um`: coupling interaction length
  - `sidewall_angle_deg`: sidewall angle (0 = vertical)
  - `polarization`: `"te"` or `"tm"` (mode filter)
- **Wavelength sweep (µm)**
  - `enable_coupling_vs_wavelength` (bool)
  - `lam_start_um`, `lam_stop_um`, `num_wavelength_points`
- **Length sweep (µm)**
  - `enable_coupling_vs_length` (bool)
  - `length_start_um`, `length_stop_um`, `num_length_points`
  - `length_wavelength_um`: wavelength used for the length sweep
- **Mode plots**
  - `enable_mode_plots` (bool)
  - `mode_plot_wavelength_um` (µm)
- **Outputs**
  - `output_prefix` (str): prefix for saved CSV/PNG files under `mcp_output/`

### Model
For wavelength-dependent coupling, the power coupling is computed from the two lowest effective indices `n_eff[:, 0]` and `n_eff[:, 1]` returned by Tidy3D, using:

- \( P_\text{coupling}(\lambda) = \sin^2\left(\pi \, L \, \frac{n_1 - n_2}{\lambda} \right) \)

For coupling vs length, `n_1` and `n_2` are evaluated at `length_wavelength_um`.

### Usage
#### Register the server
Ensure your client registers the server (example `mcp.json` entry):

```json
{
  "mcpServers": {
    "axiomatic-tidy3d": {
      "command": "python",
      "args": ["-m", "axiomatic_mcp.servers.tidy3d"],
      "env": {}
    }
  }
}
```

#### Call the tool
From an MCP-enabled client, invoke `simulate_waveguide_coupler` with desired arguments. Example (defaults mimic cSi core in SiO2 cladding, TE):

```json
{
  "name": "simulate_waveguide_coupler",
  "arguments": {
    "core_material_family": "cSi",
    "core_material_model": "Palik_Lossless",
    "clad_material_family": "SiO2",
    "clad_material_model": "Palik_Lossless",
    "wg_width1_um": 0.5,
    "wg_width2_um": 0.5,
    "wg_height_um": 0.22,
    "wg_gap_um": 0.2,
    "coupler_length_um": 50.0,
    "polarization": "te",
    "enable_coupling_vs_wavelength": true,
    "lam_start_um": 1.27,
    "lam_stop_um": 1.31,
    "num_wavelength_points": 101,
    "enable_coupling_vs_length": true,
    "length_start_um": 0.0,
    "length_stop_um": 100.0,
    "num_length_points": 21,
    "length_wavelength_um": 1.31,
    "enable_mode_plots": true,
    "mode_plot_wavelength_um": 1.55,
    "output_prefix": "wg_coupler"
  }
}
```

### Dependencies
- **Python**: 3.10+
- **Packages**: `tidy3d` (Ansys Tidy3D; requires a valid license/account), `numpy`, `matplotlib`

Install (example):
```bash
pip install numpy matplotlib tidy3d
```

Note: This repository does not pin `tidy3d` as a hard dependency to allow server registration without it; imports happen lazily inside tool functions.

### Notes
- **Materials** must exist in the Tidy3D material library. Examples: `cSi/Palik_Lossless`, `SiO2/Palik_Lossless`, `Si3N4/Luke2015Sellmeier`.
- **Outputs** are created in `mcp_output/` with the chosen `output_prefix`.
- **Mode plots** export the Ey field for the two lowest-order modes using the specified polarization filter.
