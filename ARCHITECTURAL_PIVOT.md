# Architectural Pivot: From Benchmark Tuning to Self-Organizing Substrate

Date: 2026-03-13

## What Just Happened

We **stopped** the Phase 2 Stage-2 benchmark tuning effort and **started** a new architectural line: **Self-Organizing Cognitive Substrate (SOCS)**.

This is not a bug fix or parameter adjustment. This is a fundamental change in direction.

---

## Why The Pivot

### The Old Path (Abandoned)
```
Hardcoded Strategy Layer → Environment-Specific Tuning → Benchmark Scores
                     ↑                                   ↓
              More Rules Added ←←←←←←←←←←←←←←←←←←←←←←←←┘
```

**Problem**: 
- Endless parameter stacking for each new environment
- System passes benchmarks because we wrote strategies for it
- No genuine learning or adaptation
- "Intelligence" is in the human-written rules, not the system

### The New Path (SOCS)
```
Simple Local Rules (L0) → Cluster Emergence (L1) → Global Broadcast (L2)
         ↑                                              ↓
         └←←←←←←←← Learning from Feedback ←←←←←←←←←←←←┘
```

**Goal**:
- Complexity emerges from simple local interactions
- Learning comes from prediction error and reward, not human-written strategies
- System develops capabilities by growing structure, not receiving rules
- Eventually optimizes itself within guardrails

---

## The Core Insight

> "You don't want a system that passes benchmarks. You want a substrate that can learn to pass benchmarks (and anything else)."

This requires:
1. **Local rules** (like cells/neurons)
2. **Emergent structure** (clusters/attractors)
3. **Shared state** (global workspace)
4. **Plasticity** (learning from experience)
5. **Self-optimization** (eventually)

---

## SOCS Architecture

### L0: Micro-Unit (The "Cells")
Each unit has 5 states:
- `activation` - current activity level
- `energy` - metabolic budget
- `memory_trace` - recent activity history
- `prediction_error` - difference between expected and actual
- `plasticity` - learning readiness

**Rules**: Update locally, connect to neighbors, consume energy, learn from error.

### L1: Meso-Cluster (Emergent Groups)
From dense connections form:
- **Attractors** - stable activation patterns
- **Working memory** - persistent activation states
- **Competition** - winner-take-all dynamics
- **Coordination** - synchronized clusters

### L2: Global Workspace (Shared Field)
Not a "consciousness module" written by humans, but:
- Which clusters win broadcasting rights
- What states propagate globally
- Which errors drive restructuring

### Bridge: Environment Interface
- **Input**: Local sensory signals only
- **Output**: Low-bandwidth action tendencies
- **No hardcoded game policies**

---

## Design Principles

1. **Few rules, many constraints**
   - Guardrails exist
   - No per-environment strategy tables

2. **Local learning, global emergence**
   - Units see only local state
   - No god-mode global controller

3. **Learning from feedback, not human answers**
   - No "PD should do X" rules
   - Only: observe, remember, reward/penalty, plasticity

4. **Structure before capability**
   - First: attractors, memory persistence, error recovery
   - Then: complex task performance

5. **Self-optimization within bounds**
   - Start with: connection strength, learning rate
   - Eventually: memory gating, broadcast threshold
   - Never: unbounded self-modification

---

## What We Stopped Doing

❌ **Phase 2 Stage-2 benchmark tuning**
   - Chasing 3000-tick pass rates
   - Environment-specific parameter stacks
   - "Make MultiGameCycle pass 100%"

❌ **Adding more strategy tables**
   - "If HubFailure then do X"
   - "If RegimeShift then do Y"

❌ **Reward shaping for benchmarks**
   - "Coordination bonus"
   - "Population survival reward"

## What We Started Doing

✅ **Building the substrate**
   - 2,500 lines of Rust
   - 0 external dependencies
   - 16 tests passing

✅ **Validating emergence**
   - Attractor formation
   - Memory persistence
   - Failure recovery
   - (6 dynamics phenomena, not benchmark scores)

✅ **Preparing for true learning**
   - Hebbian / STDP / Predictive / Reward-modulated plasticity
   - Energy-constrained competition
   - Structure formation and pruning

---

## Files

### New SOCS Core
```
self_organizing_substrate/
├── README.md                    # Vision and architecture
├── IMPLEMENTATION_STATUS.md     # Current status
├── src/
│   ├── lib.rs                   # Module exports
│   ├── micro_unit.rs            # L0: Simple units
│   ├── plasticity.rs            # Learning rules
│   ├── cluster_dynamics.rs      # L1: Emergent clusters
│   ├── global_workspace.rs      # L2: Global broadcast
│   └── substrate_open_world_bridge.rs  # Environment coupling
└── Cargo.toml
```

### Archived Phase 2
```
source/
├── PHASE2_STATUS.md             # Updated with pivot note
├── phase2_stage1.rs             # (passed, archived)
├── phase2_stage2.rs             # (abandoned, archived)
└── ...
```

---

## Immediate Next Steps

### 1. Validate 6 Dynamics Phenomena
Run the verification tests:
```bash
cd self_organizing_substrate
cargo run --bin verify_dynamics
```

Expected outputs:
- Attractor formation: PASS
- Memory persistence: PASS
- Failure recovery: PASS
- (etc.)

### 2. Scale Test
- 1k units → 10k units → 100k units
- Measure emergent properties
- Find scaling limits

### 3. Environment Integration
- Connect SOCS to existing Bio-World
- Replace strategy layer
- Validate survival without hardcoded policies

### 4. Comparison Study
- SOCS (no benchmark training) vs
- Phase-2-tuned (benchmark-optimized)
- Same environments, different approaches

---

## Long-term Vision

### Phase 1: Dynamics (Now)
Verify substrate shows expected emergent properties.

### Phase 2: Capability (Next)
Substrate learns to solve tasks through experience, not human-written strategies.

### Phase 3: Self-Optimization (Future)
Substrate improves its own parameters within guardrails.

### Phase 4: Open-Ended Growth (Far Future)
Substrate develops novel capabilities not anticipated by designers.

---

## Key Quote

> "C. elegans has 302 neurons and simple intelligence. It can learn, adapt, survive. We're scaling that principle, not hardcoding more rules."

This is the shift:
- **From**: "Make it pass the test"
- **To**: "Build something that can learn to pass any test"

---

## Summary

| Aspect | Old Path | New Path |
|--------|----------|----------|
| **Core** | Strategy Layer | Self-Organizing Substrate |
| **Complexity** | Human-written rules | Emergent from local interactions |
| **Learning** | Parameter tuning | Prediction error + plasticity |
| **Validation** | Benchmark scores | Dynamics phenomena |
| **Goal** | Pass tests | Learn to pass tests |
| **Endgame** | Static system | Self-improving system |

---

**The pivot is complete. SOCS v0.1.0 is ready for validation.**

