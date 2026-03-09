# Three-Layer Memory Architecture - Complete
## Implementation-Ready Specification Suite

**Version**: 1.0  
**Date**: 2026-03-09  
**Status**: ✅ Specification Complete  
**Next**: Codex Implementation Phase

---

## Suite Overview

### 6 Documents, 1 Architecture

| # | Document | Purpose | Size |
|---|----------|---------|------|
| 1 | `THREE_LAYER_MEMORY_ARCHITECTURE_v1.md` | Core design principles | 13.7 KB |
| 2 | `MEMORY_FLOW_STATE_MACHINE_v1.md` | Event-driven transitions | 11.6 KB |
| 3 | `MEMORY_DATA_SCHEMA_v1.md` | Struct definitions | 15.1 KB |
| 4 | `BIOWORLD_V19_MEMORY_INTEGRATION_SPEC.md` | Interface contracts | 14.1 KB |
| 5 | `THREE_LAYER_MEMORY_VALIDATION_PROTOCOL.md` | Test experiments | 9.3 KB |
| 6 | `CODEX_IMPLEMENTATION_BRIEF_THREE_LAYER_MEMORY.md` | Implementation guide | 13.3 KB |

**Total**: 77.1 KB of specification

---

## Core Architecture

### Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: Causal Archive (Global, Third-Person)            │
│  • Historical record of significant events                 │
│  • Evidence-chain traceability                             │
│  • Weak sampling only (p=0.01)                             │
│  • Read: Random compressed prior                           │
│  • Write: Async, audited, significant events only          │
└─────────────────────────────────────────────────────────────┘
                              ↑ ↓ (weak sampling, p=0.01)
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: Lineage Memory (Heredity, Semi-Stable)           │
│  • Heritable traits and strategy bias                      │
│  • Transmitted at reproduction                             │
│  • Mutation rate: μ=0.05                                   │
│  • Max distilled lessons: 5 (from Archive)                 │
│  • Persist: 5+ generations or extinction                   │
└─────────────────────────────────────────────────────────────┘
                              ↑ ↓ (inheritance)
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Cell Memory (Local, First-Person)                │
│  • Individual agent experience                             │
│  • Rolling window (100 ticks)                              │
│  • Ephemeral (dies with cell)                              │
│  • Direct behavior driver                                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Constraint: No God Mode

```
❌ FORBIDDEN:
   Cell → Archive direct query
   Archive → Cell strategy injection
   Archive → "optimal answer" provision
   
✅ ALLOWED:
   Archive → Lineage (weak sampling, p=0.01)
   Lineage → Cell (birth initialization)
   Cell → Behavior (every tick)
```

---

## Hard Constants (Immutable)

```rust
// Mutation
pub const MUTATION_RATE: f32 = 0.05;

// Sampling
pub const ARCHIVE_SAMPLE_PROBABILITY: f32 = 0.01;
pub const SAMPLES_PER_LIFETIME: u32 = 1;

// Memory Limits
pub const MAX_CELL_MEMORY_WINDOW: usize = 100;
pub const MAX_DISTILLED_LESSONS: usize = 5;
pub const MAX_NEIGHBORS_TRACKED: usize = 20;

// Write Rates
pub const MAX_ARCHIVE_WRITE_RATE: u32 = 1; // per 100 generations
```

---

## Integration with Bio-World v19

### Existing Metrics (Unchanged)
```
CDI - Complexity-Degradation-Index
CI  - Condensation Index
r   - Synchronization order parameter
N   - Population
E   - Energy
```

### Memory Influence Path
```
Memory → Behavior → Network Structure → [CDI, CI, r]
```

**Direct impact**: None  
**Indirect impact**: Observable via behavior changes

---

## Validation Experiments (5 MVEs)

| ID | Name | Test | Expected |
|----|------|------|----------|
| EXP-1 | Cell Ablation | Local memory necessity | Faster collapse without |
| EXP-2 | Lineage Ablation | Heredity necessity | Slower adaptation without |
| EXP-3 | Archive Disconnect | Global memory role | Survives but limited learning |
| EXP-4 | Sampling Dose | Optimal rate | p=0.01 is sweet spot |
| EXP-5 | Overpowered | Constraint necessity | God mode destroys emergence |

**Pass Criteria**: 3/5 experiments show significant effect in predicted direction

---

## Implementation Phases (for Codex)

### Phase 1: Data Schema (Day 1 AM)
- `CellMemory` struct
- `LineageMemory` struct
- `CausalArchive` struct
- `MemoryAccessGuard` struct

### Phase 2: Access Guard (Day 1 PM)
- Permission validation
- Forbidden operation rejection
- Hard constraint enforcement

### Phase 3: Write Path (Day 2 AM)
- Cell Memory: Experience recording
- Lineage Memory: Mutation and inheritance
- Archive: Async write queue

### Phase 4: Weak Sampling (Day 2 PM)
- Archive random sampling (p=0.01)
- Newborn initialization
- Lesson compression

### Phase 5: Metrics (Day 3)
- Memory observables
- Extended CSV output
- Backward compatibility

---

## Success Criteria

### Compile-Time
- [ ] No Cell has Archive reference
- [ ] No Archive methods callable from Cell
- [ ] All constants defined as pub const

### Runtime
- [ ] Sampling rate exactly 0.01
- [ ] Mutation rate ~0.05
- [ ] Max lessons = 5 enforced
- [ ] Max window = 100 enforced

### Integration
- [ ] CDI/CI/r unchanged
- [ ] Extended metrics available
- [ ] v18 format compatible

### Validation
- [ ] EXP-1-5 executable
- [ ] 3/5 pass predicted direction

---

## GitHub Repository

**Location**: `Ectrox-Lab/atlas-hec-v2.1`

**Documents**:
```
THREE_LAYER_MEMORY_ARCHITECTURE_v1.md          # Design
MEMORY_FLOW_STATE_MACHINE_v1.md                # Transitions
MEMORY_DATA_SCHEMA_v1.md                       # Structs
BIOWORLD_V19_MEMORY_INTEGRATION_SPEC.md        # Interfaces
THREE_LAYER_MEMORY_VALIDATION_PROTOCOL.md      # Tests
CODEX_IMPLEMENTATION_BRIEF_THREE_LAYER_MEMORY.md  # Implementation
```

**Commit**: `75041ba`

---

## Scientific Context

### From v18 P0
```
CDI established as leading indicator
I_crit = 0.53 ± 0.01 (stable)
Hazard ratio > 10×
```

### To v19 Unified
```
[CDI, CI, r] unified state vector
Three-layer memory architecture
Complexity-Condensation dynamics
Causal state variable validation
```

### Research Trajectory
```
v18 P0 (observation) → v18 P1 (causal) → v19 (unified framework)
```

---

## Next Steps

### Immediate
1. Codex implements 5 phases
2. Unit tests for all components
3. Integration tests

### Short-term
1. Run EXP-1 through EXP-5
2. Validate 3/5 success criteria
3. Document results

### Medium-term
1. P1-v19 unified causal experiments
2. Compare v18 vs v19 prediction power
3. Publish complexity-stability framework

---

## Contact

**Repository**: https://github.com/Ectrox-Lab/atlas-hec-v2.1  
**Issues**: Create GitHub issue for questions  
**Documentation**: All specs in `/` root directory

---

*Specification Suite Version*: 1.0  
*Status*: ✅ Complete and Ready for Implementation  
*Estimated Implementation Time*: 2-3 days (Codex)  
*Estimated Validation Time*: 9 days (5 experiments)
