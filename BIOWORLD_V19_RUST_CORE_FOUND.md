# Bio-World v19 Rust Core Modules - FOUND

**Date**: 2026-03-09  
**Status**: ✅ Core Modules Located in `src/candidates/`

---

## Found Core Modules

### 1. E1 Critical Coupling (`src/candidates/e1_critical_coupling/`)

**Contains v19 State Vector Components: r, CI, P**

File: `src/bin/e1_overnight_batch.rs`
```rust
/// Metrics: r, CI, P, CDI, N, E, h (v19 unified state vector)

#[derive(Debug, Serialize)]
struct Result {
    // v19 unified metrics
    r_final: f64,      // synchronization order parameter
    ci_final: f64,     // condensation index
    p_final: f64,      // percolation ratio
    stability: f64,    // variance of r
    convergence_time: Option<usize>,
    ...
}
```

**Implemented Functions:**
- `estimate_ci(phases: &[f64]) -> f64` - Phase clustering measure
- `estimate_percolation(phases: &[f64], n: usize) -> f64` - Giant component proxy
- Kuramoto dynamics with mean-field coupling

**Simulation Scale:**
- N: 50,000 oscillators
- Generations: 10,000
- 3 K-groups (CTRL, CRIT, HIGH)
- 3 σ-levels

---

### 2. E3 Percolation (`src/candidates/e3_percolation/`)

**Contains: P (percolation) and r (synchronization) causality test**

File: `src/main.rs`
```rust
/// E3 Phase A: Percolation-Synchronization Causality
/// Test if P (percolation ratio) precedes r (synchronization order parameter)

struct Result {
    p_final: f64,      // Percolation metrics
    r_final: f64,      // Sync metrics
    p_precedes_r: bool,
    time_lag: Option<isize>,
}
```

**Features:**
- 2D grid with occupancy probability p
- Oscillators at occupied sites
- Kuramoto coupling on network
- DFS for connected components

**Simulation Scale:**
- Grid: 100×100 = 10,000 sites
- Parameters: 20p × 3K × 3σ = 180 configs

---

### 3. CDI Implementation (`source/src/bio_superbrain_interface/`)

**File: `lineage_adapter.rs`**
```rust
/// Get CDI for universe (Bio-World state vector component)
pub fn universe_cdi(&self) -> f32 {
    let total: f32 = self.active_lineages.iter()
        .map(|l| l.cdi_contribution())
        .sum();
    total / self.active_lineages.len() as f32
}

pub fn cdi_contribution(&self) -> f32 {
    let generation_factor = (self.generation as f32 / 100.0).min(1.0);
    let stability_factor = 1.0 - (self.death_count as f32 / 10.0).min(1.0);
    (generation_factor * 0.5 + stability_factor * 0.5) * self.coherence_baseline
}
```

---

## Module Integration Status

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| **r** (sync order parameter) | `e1_critical_coupling/`, `e3_percolation/` | ✅ Implemented | Kuramoto model |
| **CI** (condensation index) | `e1_critical_coupling/src/bin/e1_overnight_batch.rs` | ✅ Implemented | Phase clustering proxy |
| **P** (percolation) | `e1_critical_coupling/`, `e3_percolation/` | ✅ Implemented | Giant component ratio |
| **CDI** | `bio_superbrain_interface/lineage_adapter.rs` | ✅ Implemented | Simplified lineage-based |
| **N** (population) | Stub only | ⚠️ MVP | No real population dynamics |
| **E** (energy) | `biomimetic/metabolism.rs` | ⚠️ Partial | Single agent only |
| **h** (hazard rate) | Not found | ❌ Missing | Needs implementation |

---

## What's Missing for Full v19

### 1. Grid-Based Multi-Agent Simulation
- 50×50×16 3D grid
- Agent positions, movement
- Food/resource distribution
- Birth/death mechanics

### 2. Population Dynamics
- Energy metabolism per agent
- Reproduction with inheritance
- Starvation/predation death
- Carrying capacity

### 3. Network Formation
- Agent-agent interaction network
- Dynamic edge formation
- Scale-free hub emergence
- Network rewiring

### 4. Full CDI/CI/r/P Integration
- Real-time state vector computation
- CDI from agent behavior complexity
- CI from network structure
- Correlation analysis

### 5. Hazard Rate Model
- `h(t) = d(extinctions)/dt`
- Extinction prediction
- Early warning system
- Cascade dynamics

---

## File Locations Summary

```
src/candidates/
├── e1_critical_coupling/
│   ├── src/main.rs                    # Basic Kuramoto r computation
│   └── src/bin/e1_overnight_batch.rs  # v19 state vector: r, CI, P
│   └── src/bin/e1_phase_b.rs          # Critical coupling analysis
│
├── e3_percolation/
│   └── src/main.rs                    # P and r causality test
│
├── 001_markers/
│   ├── src/environment.rs             # Multi-agent environment
│   └── src/marker.rs                  # Consistency markers
│
└── 002_soft_robot/
    └── src/                           # Proprioceptive homeostasis

source/src/
├── bio_superbrain_interface/
│   ├── lineage_adapter.rs             # CDI computation
│   ├── cell_adapter.rs                # Cell mapping
│   └── experiment_runner.rs           # A-E matrix
│
└── biomimetic/
    └── metabolism.rs                  # Single-agent metabolism
```

---

## Next Steps

### Option 1: Extend Existing Modules
- Integrate E1/E3 into Bio-Superbrain interface
- Add population dynamics to lineage_adapter
- Connect metabolism to multi-agent system

### Option 2: New v19 Core Implementation
- Create `bioworld_v19/` module
- Implement 50×50×16 grid
- Add birth/death/food mechanics
- Integrate CDI/CI/r/P computation

---

## Verification

**Confirmed:** v19 state vector components (r, CI, P) exist in:
- `src/candidates/e1_critical_coupling/src/bin/e1_overnight_batch.rs`

**Confirmed:** CDI computation exists in:
- `source/src/bio_superbrain_interface/lineage_adapter.rs`

**Missing:** Full multi-agent Bio-World simulation with:
- Grid-based movement
- Population dynamics
- Network condensation
- Hazard rate modeling
