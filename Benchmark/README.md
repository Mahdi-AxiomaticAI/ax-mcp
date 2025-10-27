# Benchmark Folder

This folder contains all documentation for benchmarking Femwell MCP tools against Tidy3D validation results.

---

## 📁 Contents

### 1. **BENCHMARKING_SUMMARY.md**
**Quick reference guide**
- Overview of benchmarkable example pairs
- Priority rankings
- Key validation metrics
- Recommended workflow

**Use this for:** Quick lookup of which examples can be benchmarked

---

### 2. **BENCHMARKING_ANALYSIS.md**
**Comprehensive analysis document**
- Detailed comparison tables for all example pairs
- Compatibility assessments (Excellent/Moderate/Poor)
- Material properties comparison
- Implementation approach and strategies
- Expected outcomes and success criteria
- Phase-by-phase execution plan

**Use this for:** Understanding the full scope of benchmarking possibilities

---

### 3. **INITIAL_BENCHMARKING_PROMPT.md**
**Ready-to-use prompt for TiN heater benchmark** (Phase 1, Priority ⭐⭐⭐⭐⭐)
- Complete device specifications
- Geometry parameters with diagrams
- Material properties (thermal, optical, thermo-optic)
- Simulation configuration (thermal + optical)
- Boundary conditions and mesh settings
- Expected outputs (CSV, JSON, plots)
- Validation criteria with pass/fail thresholds
- Implementation notes and debugging checklist
- Step-by-step execution guide

**Use this for:** Implementing the first MCP tool benchmark

---

## 🎯 Quick Start

### For First-Time Benchmarking:
1. Read `BENCHMARKING_SUMMARY.md` (5 min)
2. Review `INITIAL_BENCHMARKING_PROMPT.md` (15 min)
3. Implement Femwell MCP tool for TiN heater
4. Run benchmark and generate validation report

### For Understanding Full Scope:
1. Read `BENCHMARKING_ANALYSIS.md` thoroughly
2. Identify additional benchmark candidates
3. Adapt prompt template for other devices

---

## 🏆 Priority Order

### Phase 1: High-Confidence Validation (Do This First)
1. **TiN Metal Heater** - `INITIAL_BENCHMARKING_PROMPT.md` has full details
2. **Doped Silicon Heater** - Use similar approach as TiN heater

### Phase 2: Quick Validation (EASIEST)
3. **Waveguide Dispersion** - Both Femwell and Tidy3D MCP tools exist!

### Phase 3: Multi-Physics Validation (Optional)
4. **Carrier Injection Modulator** - Both MCP tools exist, but multi-physics complexity

---

## 📊 Success Criteria

For a benchmark to pass:
- **P_π within ±15%** of Tidy3D reference (critical)
- **Phase shift linearity R² > 0.95** (important)
- **Temperature distribution qualitatively matches** (important)

---

## 🔗 Related Files

- **Femwell Examples:** `../Femwell/example_library/`
- **Tidy3D Examples:** `../Tidy3D/example_library/`
- **Femwell Summary:** `../Femwell/CATEGORIZED_SUMMARY.md`
- **Tidy3D Summary:** `../Tidy3D/CATEGORIZED_SUMMARY.md`

---

## 📝 Notes

- All benchmarking focuses on **thermo-optic phase shifters** because:
  - Both Femwell and Tidy3D have validated examples
  - Same reference paper (Jacques et al., 2019) for validation
  - Clear quantitative metrics (P_π, phase shift, temperature)
  - High confidence in cross-validation

- **Why not other devices?**
  - RF structures: Different transmission line types (microstrip vs CPW)
  - Gratings: Different applications or solver approaches
  - Electro-optic: No Tidy3D equivalent for Femwell's LiNbO₃ example
  - Charge transport: Femwell lacks charge solver

---

## 🚀 Next Steps

1. ✅ Documentation complete
2. ⏭️ Implement `simulate_metal_heater_phase_shifter` MCP tool
3. ⏭️ Extract Tidy3D reference data from `TransientThermoOpticShifter.ipynb`
4. ⏭️ Run comparison and generate plots
5. ⏭️ Create validation report
6. ⏭️ Iterate on doped silicon heater if TiN benchmark passes

---

**Last Updated:** 2025-10-23
**Status:** Ready for MCP tool implementation