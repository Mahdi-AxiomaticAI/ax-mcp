# Axiomatic Digital Twin Server

An MCP server for simulating photonic integrated circuit (PIC) models using JAX-based digital twin implementations.

The Digital Twin server enables AI assistants to simulate multimode ring resonators and MZI filter devices, returning transmission spectra as CSV files.

## Tools Available

### `simulate_multimode_ring`

Simulates a multimode ring resonator with up to 3 modes and various optical effects.

**Arguments:**

- `lam_start_nm`: Starting wavelength in nm (default: 1540.0)
- `lam_stop_nm`: Ending wavelength in nm (default: 1560.0)
- `num_points`: Number of wavelength points (default: 2001)
- `ring_radius_um`: Ring radius in micrometers (default: 10000.0)
- `enable_mode2`: Enable second mode (default: false)
- `enable_mode3`: Enable third mode (default: false)
- `mode1_neff`: Mode 1 effective index (default: 2.40)
- `mode1_alpha_dB_per_cm`: Mode 1 loss in dB/cm (default: 3.0)
- `mode1_kappa`: Mode 1 coupling coefficient (default: 0.20)
- `mode1_weight`: Mode 1 weight (default: 1.0)
- `mode2_neff`: Mode 2 effective index (default: 2.45)
- `mode2_alpha_dB_per_cm`: Mode 2 loss in dB/cm (default: 3.0)
- `mode2_kappa`: Mode 2 coupling coefficient (default: 0.15)
- `mode2_weight`: Mode 2 weight (default: 0.6)
- `mode3_neff`: Mode 3 effective index (default: 2.50)
- `mode3_alpha_dB_per_cm`: Mode 3 loss in dB/cm (default: 3.0)
- `mode3_kappa`: Mode 3 coupling coefficient (default: 0.10)
- `mode3_weight`: Mode 3 weight (default: 0.4)
- `inter_mode_coherence`: Coherence between modes (0-1, default: 1.0)
- `enable_grating`: Enable grating envelope (default: false)
- `grating_center_nm`: Grating center wavelength (default: 1550.0)
- `grating_fwhm_nm`: Grating FWHM in nm (default: 20.0)
- `grating_peak_loss_dB`: Grating peak loss in dB (default: 3.0)
- `insertion_loss_dB`: Insertion loss in dB (default: 0.0)
- `output_filename`: Output CSV filename (default: "ring_transmission.csv")

**Returns:**

- CSV file with wavelength (nm), linear transmission, and dB transmission columns
- Summary statistics

### `simulate_mzi_filter`

Simulates an 8-channel MZI-based CWDM filter.

**Arguments:**

- `lam_start_nm`: Starting wavelength in nm (default: 1270.0)
- `lam_stop_nm`: Ending wavelength in nm (default: 1310.0)
- `num_points`: Number of wavelength points (default: 4001)
- `lambda0`: Central wavelength in meters (default: 1290e-9)
- `delta_lambda`: Channel spacing in meters (default: 4.4e-9)
- `n0_1`, `n1_1`, `n2_1`: Stage 1 dispersion coefficients
- `n0_2`, `n1_2`, `n2_2`: Stage 2 dispersion coefficients
- `n0_3`, `n1_3`, `n2_3`: Stage 3 dispersion coefficients
- `kappa_05`: 50% coupling coefficient (default: 0.5)
- `kappa_029`: 29% coupling coefficient (default: 0.29)
- `kappa_008`: 8% coupling coefficient (default: 0.08)
- `kappa_02`: 20% coupling coefficient (default: 0.2)
- `kappa_004`: 4% coupling coefficient (default: 0.04)
- `output_filename`: Output CSV filename (default: "mzi_transmission.csv")

**Returns:**

- CSV file with wavelength (nm) and transmission for 8 channels (λ1-λ8)
- Channel performance metrics

### `list_available_models`

Lists all available digital twin models and their descriptions.

**Returns:**

- List of available models with descriptions and parameter counts

## Installation

### Quick Install (via PyPI)

Add to your MCP client configuration:

```json
{
  "axiomatic-dts": {
    "command": "uvx",
    "args": ["--from", "axiomatic-dts", "axiomatic-dts-server"]
  }
}
```

### Development Install

For development or local modifications:

```json
{
  "axiomatic-dts": {
    "command": "python",
    "args": ["-m", "axiomatic_dts.Server"]
  }
}
```

## Output Format

All simulations save results as CSV files with the following formats:

### Ring Resonator Output
```csv
wavelength_nm,transmission_linear,transmission_dB
1540.0,0.95,-0.22
1540.1,0.93,-0.31
...
```

### MZI Filter Output
```csv
wavelength_nm,λ1,λ2,λ3,λ4,λ5,λ6,λ7,λ8
1270.0,0.001,0.002,0.001,0.003,0.001,0.002,0.001,0.002
1270.1,0.002,0.003,0.002,0.004,0.002,0.003,0.002,0.003
...
```

## Example Usage

Via an LLM client such as Claude Desktop:

> Simulate a dual-mode ring resonator from 1550 to 1570 nm with mode effective indices of 2.40 and 2.45, and save the results.

> Generate an 8-channel CWDM filter response from 1270 to 1310 nm with 4.4 nm channel spacing.

## Physical Models

### Multimode Ring Resonator
- All-pass ring configuration with up to 3 modes
- Wavelength-dependent coupling and loss
- Inter-mode coherence control
- Optional grating envelope and external reflections
- Background field interference effects

### MZI Filter
- 3-stage cascaded MZI architecture
- 8-channel CWDM demultiplexer
- Wavelength-dependent coupling coefficients
- Material dispersion modeling
- Full transfer matrix calculation

## Support

For issues or questions:

- GitHub Issues: [https://github.com/Axiomatic-AI/axiomatic-dts/issues](https://github.com/Axiomatic-AI/axiomatic-dts/issues)
- Email: [support@axiomatic-ai.com](mailto:support@axiomatic-ai.com)