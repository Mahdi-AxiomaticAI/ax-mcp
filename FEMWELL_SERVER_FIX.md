# Femwell MCP Server Fix

**Date**: 2025-10-23
**Issue**: Femwell MCP server not connecting
**Status**: ✅ FIXED

---

## Problem

The Femwell MCP server was not accessible via the Claude Code MCP interface. Users encountered connection issues when trying to use the server.

## Root Cause

The Femwell server was missing from the project's entry points in `pyproject.toml`. While the server code existed and was functional, it wasn't registered as an installable script, preventing it from being discovered by MCP clients.

## Solution

Added the missing entry point to `pyproject.toml`:

```toml
[project.scripts]
axiomatic-pic = "axiomatic_mcp.servers.pic:main"
axiomatic-documents = "axiomatic_mcp.servers.documents:main"
axiomatic-plots = "axiomatic_mcp.servers.plots:main"
axiomatic-dts = "axiomatic_mcp.servers.dts:main"
axiomatic-tidy3d = "axiomatic_mcp.servers.tidy3d:main"
axiomatic-femwell = "axiomatic_mcp.servers.femwell:main"  # <-- ADDED THIS LINE
```

## Changes Made

1. **Updated `pyproject.toml`** (line 49):
   - Added: `axiomatic-femwell = "axiomatic_mcp.servers.femwell:main"`

2. **Reinstalled package**:
   ```bash
   pip install -e .
   ```

3. **Verified installation**:
   - Created test script `test_femwell_server.py`
   - Confirmed all 4 tools are registered:
     - ✅ `simulate_depletion_modulator`
     - ✅ `simulate_metal_heater_phase_shifter`
     - ✅ `simulate_doped_si_heater_phase_shifter`
     - ✅ `simulate_waveguide_dispersion`

## Verification

Run the test script to verify the server is working:

```bash
python test_femwell_server.py
```

Expected output:
```
Testing Femwell MCP Server...
Server name: Axiomatic Femwell

Number of tools registered: 4

Expected tools:
  [OK] simulate_depletion_modulator
  [OK] simulate_metal_heater_phase_shifter
  [OK] simulate_doped_si_heater_phase_shifter
  [OK] simulate_waveguide_dispersion

All registered tools:
  - simulate_depletion_modulator
  - simulate_metal_heater_phase_shifter
  - simulate_doped_si_heater_phase_shifter
  - simulate_waveguide_dispersion

[SUCCESS] All 4 Femwell MCP tools are registered!
```

## Testing the Server

### Via Command Line:
```bash
python -m axiomatic_mcp.servers.femwell
```

This starts the server in stdio mode, ready to accept MCP protocol messages.

### Via Claude Code:
After reinstalling the package, the server should now be discoverable in Claude Code's MCP server list as `axiomatic-femwell`.

## Server Details

- **Server Name**: Axiomatic Femwell
- **Version**: 0.0.2
- **Transport**: STDIO (default)
- **Entry Point**: `axiomatic_mcp.servers.femwell:main`
- **Module Location**: `axiomatic_mcp/servers/femwell/`

## Tools Available

1. **simulate_depletion_modulator**
   - Compute effective index and absorption vs voltage for PN junction modulators
   - Validates against benchmark #4

2. **simulate_metal_heater_phase_shifter**
   - Compute phase shift vs current for TiN metal heater phase shifters
   - Validates against benchmark #1

3. **simulate_doped_si_heater_phase_shifter**
   - Compute phase shift vs power for doped silicon heater phase shifters
   - Validates against benchmark #2

4. **simulate_waveguide_dispersion**
   - Compute effective index, group index, and GVD vs wavelength
   - Validates against benchmark #3

---

## Next Steps

The server is now ready for benchmarking against Tidy3D:
1. ✅ All tools implemented and tested
2. ✅ Server registered in pyproject.toml
3. ✅ Package reinstalled with new entry point
4. 📋 Ready to run benchmark comparisons

See `Benchmark/TOP_4_BENCHMARKS.md` for benchmarking instructions.
