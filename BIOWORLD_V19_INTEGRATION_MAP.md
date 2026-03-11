# Bio-World v19 Integration Map

**Date**: 2026-03-09  
**Goal**: Module mapping → Interface definition → Gap closure

---

## Found Modules Inventory

| Metric | Source File | Input | Output | Status | Action |
|--------|-------------|-------|--------|--------|--------|
| **r** (sync) | `e1_critical_coupling/src/bin/e1_overnight_batch.rs` | `&[f64]` phases | `f64` | ✅ Ready | Wrap |
| **CI** | `e1_critical_coupling/src/bin/e1_overnight_batch.rs` | `&[f64]` phases | `f64` | ✅ Ready | Wrap |
| **P** (percolation) | `e1_critical_coupling/src/bin/e1_overnight_batch.rs` + `e3_percolation/src/main.rs` | `&[f64]` phases or network | `f64` | ✅ Ready | Wrap |
| **CDI** | `source/src/bio_superbrain_interface/lineage_adapter.rs` | `LineageMemory` | `f32` | ✅ Ready | Keep |
| **N** (population) | Stub only | - | - | ❌ Missing | Implement |
| **E** (energy) | `source/src/biomimetic/metabolism.rs` | single agent | `f32` | ⚠️ Partial | Extend |
| **h** (hazard) | Not found | - | - | ❌ Missing | Implement |

---

## Interface Definitions

### Tier 1: Metrics (Ready to Wrap)

```rust
// metrics_r.rs - Synchronization order parameter
pub fn compute_sync_order_parameter(phases: &[f64]) -> f64 {
    let (sum_cos, sum_sin) = phases.iter()
        .fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
    ((sum_cos / n).powi(2) + (sum_sin / n).powi(2)).sqrt()
}

// metrics_ci.rs - Condensation index  
pub fn compute_condensation_index(phases: &[f64]) -> f64 {
    // Phase clustering: max_bin / n
}

// metrics_p.rs - Percolation ratio
pub fn compute_percolation_ratio(network: &AgentNetwork) -> f64 {
    // largest_component / n
}
```

### Tier 2: Missing Core (Need Implementation)

```rust
// grid_world.rs - 50×50×16 multi-agent simulation
pub struct GridWorld {
    grid: [[[Option<Agent>; 16]; 50]; 50],  // x, y, z
    agents: Vec<Agent>,
    food_sources: Vec<Food>,
    tick: usize,
}

// population_dynamics.rs
pub struct PopulationDynamics {
    birth_rate: f32,
    death_rate: f32,
    carrying_capacity: usize,
}

// hazard_rate.rs
pub fn compute_hazard_rate(extinction_events: &[usize], dt: f32) -> f32 {
    // h(t) = d(extinctions)/dt
}
```

---

## Gap Analysis: 4 Missing Components

### 1. 50×50×16 Multi-Agent Grid Engine
**Required for**: Agent movement, spatial interaction, universe simulation
**Current state**: Only 16×16 GridWorld exists (`source/src/gridworld/mod.rs`)
**Gap**: Need 3D grid, 50×50×16, multiple parallel universes (128)

### 2. Birth/Death/Food/Reproduction Loop
**Required for**: Population dynamics (N), evolution pressure
**Current state**: LineageAdapter has genesis/inherit stubs
**Gap**: No actual reproduction with energy cost, no starvation death

### 3. Hazard Rate Tracking
**Required for**: Extinction prediction, early warning
**Current state**: death_count in LineageMemory
**Gap**: No `h(t) = d(extinctions)/dt` computation, no cascade detection

### 4. Dynamic Interaction Network
**Required for**: CI computation from actual agent interactions
**Current state**: E1/E3 use static/phase-based networks
**Gap**: Agent proximity → edge formation → dynamic rewiring

---

## Integration Target Architecture

```
bio_world_v19/
├── metrics/           # Wrap existing r/CI/P/CDI
│   ├── mod.rs
│   ├── sync.rs       # r from phases
│   ├── condensation.rs # CI from phases/network
│   └── percolation.rs  # P from network
│
├── core/              # NEW: Missing components
│   ├── grid.rs        # 50×50×16 world
│   ├── agent.rs       # Agent with position/energy
│   ├── population.rs  # Birth/death/food
│   └── network.rs     # Dynamic interaction graph
│
└── hazard/            # NEW: Extinction prediction
    └── rate.rs        # h(t) computation
```

---

## Immediate Next Steps

1. **Wrap Tier 1 metrics** → `bio_world_v19/metrics/`
2. **Implement 4 missing components** → `bio_world_v19/core/`
3. **Integrate with bio_superbrain_interface** → Replace stub simulation

---

## Decision Gate

If 4 missing components not found in next search → **Implement immediately**.
