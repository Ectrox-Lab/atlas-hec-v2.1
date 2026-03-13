# Codex Implementation Brief: Three-Layer Memory
## For Bio-World v19 Integration

**Version**: 1.0  
**Date**: 2026-03-09  
**Target**: Codex (implementation agent)  
**Complexity**: High  
**Estimated Effort**: 2-3 days  

---

## Executive Summary

Implement Three-Layer Memory Architecture into Bio-World v19.

**Architecture Documents** (read first):
1. `THREE_LAYER_MEMORY_ARCHITECTURE_v1.md` - Design principles
2. `MEMORY_FLOW_STATE_MACHINE_v1.md` - Event transitions
3. `MEMORY_DATA_SCHEMA_v1.md` - Struct definitions
4. `BIOWORLD_V19_MEMORY_INTEGRATION_SPEC.md` - Interface contracts
5. `THREE_LAYER_MEMORY_VALIDATION_PROTOCOL.md` - Test requirements

---

## Implementation Order

### Phase 1: Data Schema (Day 1 Morning)
**Files to modify/create**:
- `src/memory/cell_memory.rs` - NEW
- `src/memory/lineage_memory.rs` - NEW
- `src/memory/causal_archive.rs` - NEW
- `src/memory/mod.rs` - NEW (module exports)

**Tasks**:
1. Implement `CellMemory` struct with all fields from SCHEMA §2
2. Implement `LineageMemory` struct with all fields from SCHEMA §3
3. Implement `CausalArchiveRecord` and `CausalArchive` structs from SCHEMA §4
4. Implement `ArchiveSamplingPolicy` from SCHEMA §5
5. Implement `MemoryAccessGuard` from SCHEMA §6

**Acceptance Criteria**:
- [ ] All structs compile without errors
- [ ] All constants defined with correct values
- [ ] No impl blocks yet (just data definitions)

---

### Phase 2: Access Guard (Day 1 Afternoon)
**Files to modify**:
- `src/memory/access_guard.rs` - NEW
- `src/memory/mod.rs` - Add Guard exports

**Tasks**:
1. Implement `MemoryAccessGuard` validation logic
2. Implement permission matrix from INTEGRATION_SPEC §9
3. Implement hard constraints:
   - Cell cannot access Archive directly
   - Archive cannot overwrite Cell
   - Sampling probability enforced (p ≤ 0.01)

**Acceptance Criteria**:
- [ ] All forbidden operations return compile-time or runtime error
- [ ] Access logging functional
- [ ] Unit tests for all guard conditions

**Unit Tests Required**:
```rust
#[test]
fn test_cell_cannot_access_archive() {
    let cell = Cell::new();
    let archive = Archive::new();
    // This should fail to compile or panic at runtime
    // cell.query_archive(&archive); // MUST NOT WORK
}

#[test]
fn test_sampling_probability_enforced() {
    let policy = ArchiveSamplingPolicy::default();
    assert!(policy.sample_probability <= 0.01);
}
```

---

### Phase 3: Write Path (Day 2 Morning)
**Files to modify**:
- `src/memory/cell_memory.rs` - Add write methods
- `src/memory/lineage_memory.rs` - Add mutation methods
- `src/memory/causal_archive.rs` - Add write queue

**Tasks**:
1. Cell Memory write:
   - `record_experience(event)` - Write to rolling window
   - `update_trust(agent, outcome)` - Update neighbor trust
   - `decay()` - Apply decay rules

2. Lineage Memory write:
   - `mutate()` - Apply mutation with rate μ=0.05
   - `record_death(cause)` - Update statistics
   - `inherit_from(parent)` - Copy with mutation

3. Archive write:
   - `queue_record(event)` - Async queue for writes
   - `process_queue()` - Background processing
   - `compress_old_records()` - Background compression

**Acceptance Criteria**:
- [ ] Cell Memory updates on events
- [ ] Lineage mutations at correct rate
- [ ] Archive queue processes without blocking
- [ ] Write rate limits enforced (max 1/100 gen)

**Integration Point**:
```rust
// In cell.rs, death_event()
if is_significant {
    archive.queue_record(death_event);
}
```

---

### Phase 4: Weak Sampling (Day 2 Afternoon)
**Files to modify**:
- `src/memory/causal_archive.rs` - Add sampling
- `src/agent.rs` - Add newborn initialization

**Tasks**:
1. Archive sampling:
   - `random_sample()` - Random record selection (not "best")
   - `compress_to_lesson(record)` - Compress full record to Lesson
   - Enforce p=0.01 probability

2. Newborn initialization:
   - `inherit_lineage(parent)` - Copy lineage
   - `maybe_sample_archive(archive)` - With p=0.01, sample one record
   - `init_cell_memory()` - Empty Cell Memory

**Hard Constraint**:
```rust
// Must enforce this
const ARCHIVE_SAMPLE_PROBABILITY: f32 = 0.01;
const SAMPLES_PER_LIFETIME: u32 = 1;

fn newborn_init(archive: &Archive) -> LineageMemory {
    let mut lineage = inherit_from_parent();
    
    if random() < ARCHIVE_SAMPLE_PROBABILITY {
        if let Some(record) = archive.random_sample() {
            let lesson = compress_to_lesson(record);
            lineage.distilled_lessons.push(lesson);
            // Max 5 lessons, oldest dropped
            if lineage.distilled_lessons.len() > 5 {
                lineage.distilled_lessons.remove(0);
            }
        }
    }
    
    lineage
}
```

**Acceptance Criteria**:
- [ ] Sampling rate exactly 0.01
- [ ] Random selection (not optimized)
- [ ] Lesson compression applied
- [ ] Max 5 lessons enforced

---

### Phase 5: Metrics Integration (Day 3)
**Files to modify**:
- `src/metrics.rs` - Add memory observables
- `src/evolution_logger.rs` - Extend CSV output

**Tasks**:
1. Memory metrics:
   - `avg_cell_memory_size()` - Average utilization
   - `avg_stress_level()` - From CellMemory
   - `lineage_count()` - Distinct lineages
   - `lineage_diversity()` - Strategy distribution
   - `archive_record_count()` - Total records
   - `archive_write_rate()` - Writes per generation

2. Extended output:
   - Add columns to evolution.csv (optional, backward compatible)
   - Maintain v18 format as default
   - v19 extended format with flag

**Integration Point**:
```rust
// In evolution_logger.rs
fn log_generation(&self, world: &World) {
    let base_record = BaseRecord {
        generation: world.generation,
        population: world.population_count(),
        avg_cdi: world.cdi(),
        // ... v18 fields
    };
    
    // Optional v19 extension
    if self.v19_mode {
        let memory_metrics = MemoryMetrics {
            avg_cell_memory_size: world.avg_cell_memory_size(),
            lineage_count: world.lineage_count(),
            archive_record_count: world.archive.record_count(),
        };
        self.write_extended(base_record, memory_metrics);
    } else {
        self.write_base(base_record);  // v18 compatible
    }
}
```

**Acceptance Criteria**:
- [ ] All memory metrics computable
- [ ] CSV output backward compatible
- [ ] Extended format contains new fields
- [ ] No impact on CDI/CI/r computation

---

## File Structure

```
src/
├── memory/
│   ├── mod.rs                    # Module exports
│   ├── cell_memory.rs            # CellMemory struct + methods
│   ├── lineage_memory.rs         # LineageMemory struct + methods
│   ├── causal_archive.rs         # Archive + Record structs
│   ├── access_guard.rs           # Permission validation
│   └── constants.rs              # All constants (μ, p, MAX_*)
├── agent.rs                      # Modified: newborn init
├── cell.rs                       # Modified: tick, death
├── world.rs                      # Modified: metrics
└── evolution_logger.rs           # Modified: extended output
```

---

## Critical Implementation Constraints

### Forbidden (Will Cause Rejection)

1. **No God Mode Archive**
   ```rust
   // REJECT: Archive providing answers
   let answer = archive.query("what should I do?");
   ```

2. **No Direct Archive Access from Cell**
   ```rust
   // REJECT: Cell has Archive reference
   struct Cell {
       archive: &Archive,  // NOT ALLOWED
   }
   ```

3. **No Perfect Strategy Injection**
   ```rust
   // REJECT: Archive providing optimal strategy
   archive.inject_optimal_strategy(cell_id, strategy);
   ```

4. **No Unlimited Sampling**
   ```rust
   // REJECT: Sampling > 0.01
   const SAMPLE_PROB: f32 = 0.1;  // NOT ALLOWED (must be ≤ 0.01)
   ```

5. **No Breaking CDI/CI/r**
   ```rust
   // REJECT: Memory affecting metrics directly
   cdi += cell_memory.hint;  // NOT ALLOWED
   ```

### Required (Must Implement)

1. **Hard Constraint Constants**
   ```rust
   pub const MUTATION_RATE: f32 = 0.05;
   pub const ARCHIVE_SAMPLE_PROBABILITY: f32 = 0.01;
   pub const MAX_DISTILLED_LESSONS: usize = 5;
   pub const MAX_CELL_MEMORY_WINDOW: usize = 100;
   pub const MAX_ARCHIVE_WRITE_RATE: u32 = 1; // per 100 generations
   ```

2. **Access Control Enforcement**
   ```rust
   impl AccessGuard {
       fn validate(&self, request: AccessRequest) -> Result<(), Rejection> {
           match (requestor, target) {
               (Cell, Archive) => Err(Rejection::Forbidden),
               (Cell, OtherCellMemory) => Err(Rejection::Forbidden),
               // ... etc
           }
       }
   }
   ```

3. **Async Archive Writes**
   ```rust
   impl Archive {
       fn write(&mut self, record: Record) {
           self.queue.push(record);  // Queue, don't block
       }
       
       fn process_queue(&mut self) {
           // Background thread/process
       }
   }
   ```

---

## Testing Requirements

### Unit Tests (Each File)

**cell_memory.rs**:
```rust
#[test]
fn test_rolling_window() {
    let mut mem = CellMemory::new();
    for i in 0..150 {
        mem.record_energy(i as f32);
    }
    assert_eq!(mem.recent_energy_history.len(), 100); // Max window
}

#[test]
fn test_trust_decay() {
    let mut mem = CellMemory::new();
    mem.update_trust(AgentID(1), 0.8);
    mem.decay();
    assert!(mem.neighbor_trust[&AgentID(1)] < 0.8);
}
```

**lineage_memory.rs**:
```rust
#[test]
fn test_mutation_rate() {
    let mut lineage = LineageMemory::new();
    let original = lineage.preferred_strategy.clone();
    
    let mut mutation_count = 0;
    for _ in 0..1000 {
        let child = lineage.reproduce();
        if child.preferred_strategy != original {
            mutation_count += 1;
        }
    }
    
    // Should be ~50 mutations (1000 × 0.05)
    assert!(mutation_count > 30 && mutation_count < 70);
}
```

**access_guard.rs**:
```rust
#[test]
#[should_panic(expected = "Forbidden")]
fn test_cell_cannot_access_archive() {
    let cell = Cell::new();
    let archive = Archive::new();
    
    // This must panic or fail
    AccessGuard::validate(
        Accessor::Cell(cell.id),
        Target::Archive,
    ).unwrap();
}
```

### Integration Tests

**test_memory_layers.rs**:
```rust
#[test]
fn test_full_lifecycle() {
    let mut world = World::new();
    
    // Run 100 generations
    for _ in 0..100 {
        world.tick();
    }
    
    // Verify: Cell memories exist
    assert!(world.avg_cell_memory_size() > 0.0);
    
    // Verify: Lineages propagated
    assert!(world.lineage_count() > 0);
    
    // Verify: Archive has records (if deaths occurred)
    if world.total_deaths > 0 {
        assert!(world.archive.record_count() > 0);
    }
}

#[test]
fn test_no_god_mode() {
    let mut world = World::new();
    
    // Verify Cell has no Archive reference
    for cell in &world.cells {
        assert!(!cell.has_archive_reference());
    }
}
```

---

## Acceptance Checklist

### Compile-Time Checks
- [ ] No cell has Archive field
- [ ] No archive methods callable from cell scope
- [ ] All constants defined as pub const
- [ ] No impl of `GodMode` trait (if exists, remove)

### Runtime Checks
- [ ] Sampling rate exactly 0.01 verified
- [ ] Mutation rate ~0.05 verified
- [ ] Max lessons = 5 enforced
- [ ] Max memory window = 100 enforced
- [ ] Archive write rate ≤ 1/100 gen enforced

### Integration Checks
- [ ] CDI computation unchanged
- [ ] CI computation unchanged
- [ ] r computation unchanged
- [ ] Extended metrics available
- [ ] Backward compatible output

### Validation Ready
- [ ] EXP-1 (Cell ablation) can be run
- [ ] EXP-2 (Lineage ablation) can be run
- [ ] EXP-3 (Archive disconnect) can be run
- [ ] EXP-4 (Sampling dose) can be run
- [ ] EXP-5 (Overpowered) can be run

---

## Common Pitfalls (Avoid)

### Pitfall 1: Making Archive Too Powerful
**Wrong**: Archive provides optimal strategies  
**Right**: Archive provides historical observations only

### Pitfall 2: Breaking Cell Isolation
**Wrong**: Cell can query global state  
**Right**: Cell only knows local perception + own memory

### Pitfall 3: Synchronous Archive Writes
**Wrong**: `archive.write(record)` blocks until disk flush  
**Right**: `archive.queue(record)` returns immediately, background processing

### Pitfall 4: Breaking Metrics
**Wrong**: CDI formula includes memory terms  
**Right**: CDI formula unchanged, memory influences behavior which influences CDI indirectly

### Pitfall 5: Unlimited Memory Growth
**Wrong**: Cell Memory grows without bound  
**Right**: Rolling window (100 entries) enforced

---

## Reference Documents

Read in order:
1. `THREE_LAYER_MEMORY_ARCHITECTURE_v1.md` - Understand why
2. `MEMORY_DATA_SCHEMA_v1.md` - Know what structs
3. `BIOWORLD_V19_MEMORY_INTEGRATION_SPEC.md` - Learn interfaces
4. This brief - Implement

---

## Questions?

If unclear on:
- **Design intent**: Read ARCHITECTURE document
- **State transitions**: Read STATE_MACHINE document  
- **Field definitions**: Read SCHEMA document
- **Interface contracts**: Read INTEGRATION_SPEC document
- **Test requirements**: Read VALIDATION_PROTOCOL document

**Do not guess. Read the spec.**

---

*Implementation Brief Version*: 1.0  
*Target Completion*: 2-3 days  
*Success Criteria*: All acceptance checklist items pass
