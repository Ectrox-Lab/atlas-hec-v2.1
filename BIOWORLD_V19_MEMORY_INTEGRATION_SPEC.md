# Bio-World v19 Memory Integration Specification
## Minimal Interface for Three-Layer Memory Architecture

**Version**: 1.0  
**Date**: 2026-03-09  
**Depends on**: All previous specifications  
**Constraint**: Interface design only. No implementation code.

---

## 1. Integration Goals

### 1.1 Primary Goal
Integrate Three-Layer Memory into Bio-World v19 without disrupting existing [CDI, CI, r] metrics pipeline.

### 1.2 Secondary Goals
- Enable memory layers to influence agent behavior
- Allow memory metrics to be observable
- Maintain backward compatibility with v18 experiments

### 1.3 Non-Goals
- Change existing CDI/CI/r computation logic
- Add memory as direct inputs to metrics formulas
- Create new experimental conditions (P1 continues unchanged)

---

## 2. Interface Overview

### 2.1 Integration Points

```
Bio-World v19 Core
├── cell_tick()           ← Reads Cell Memory
├── reproduction()        ← Handles Lineage inheritance
├── death_event()         ← Triggers Archive write
├── newborn_init()        ← Weak sampling from Lineage/Archive
└── metrics_layer()       ← Observes memory effects

Three-Layer Memory
├── CellMemory            → cell_tick()
├── LineageMemory         → reproduction(), newborn_init()
├── CausalArchive         → death_event(), metrics_layer()
└── AccessGuard           → All interfaces
```

### 2.2 Call Direction

| Caller | Callee | Frequency | Sync/Async |
|--------|--------|-----------|------------|
| cell_tick() | CellMemory::read() | 1/tick | Sync |
| cell_tick() | CellMemory::write() | On event | Sync |
| reproduction() | LineageMemory::inherit() | On birth | Sync |
| reproduction() | LineageMemory::mutate() | On birth | Sync |
| newborn_init() | Archive::sample() | On birth × 0.01 | Sync |
| death_event() | Archive::write() | On death (rare) | Async (queue) |
| metrics_layer() | Memory::observe() | 1/generation | Async |

---

## 3. Cell Tick Interface

### 3.1 Function Signature

```rust
fn cell_tick(
    cell_id: AgentID,
    current_state: Perception,
    cell_memory: &mut CellMemory,          // Layer 1
) -> Action;
```

### 3.2 Read Operations

**What cell_tick reads from CellMemory**:
```rust
// Decision context
let context = DecisionContext {
    recent_energy_trend: cell_memory.energy_trend(),
    threat_nearby: cell_memory.recent_threats().any(),
    trusted_neighbors: cell_memory.neighbor_trust.above_threshold(0.5),
    last_successful_action: cell_memory.recent_action_success.max(),
    current_mood: cell_memory.current_mood,
};
```

**Constraints**:
- Read scope: Own CellMemory only
- Read frequency: Every tick
- No access to: Other cells, Lineage, Archive

### 3.3 Write Operations

**What cell_tick writes to CellMemory**:
```rust
// After action execution
if energy_changed {
    cell_memory.recent_energy_history.push(current_energy);
    cell_memory.recent_energy_history.truncate(MAX_WINDOW);
}

if threat_detected {
    cell_memory.recent_threat_timestamps.push(current_generation);
}

if collaboration_completed {
    cell_memory.update_trust(partner_id, outcome);
}

cell_memory.update_action_success(action_taken, outcome);
cell_memory.update_mood();
cell_memory.decay_old_entries();
```

**Constraints**:
- Write scope: Own CellMemory only
- Write triggers: Event-driven
- Decay: Automatic on every write

### 3.4 No Archive Access

**Hard constraint**: `cell_tick` has no reference to Archive.
```rust
// FORBIDDEN
// let hint = archive.query("what should I do?");  // NOT ALLOWED
// let strategy = global_optimal_strategy();        // NOT ALLOWED
```

---

## 4. Reproduction Interface

### 4.1 Function Signature

```rust
fn reproduction(
    parent_id: AgentID,
    parent_cell_memory: &CellMemory,
    parent_lineage: &LineageMemory,         // Layer 2
    archive: &CausalArchive,                // Layer 3
) -> (AgentID, CellMemory, LineageMemory);
```

### 4.2 Lineage Inheritance

**Synchronous operation**:
```rust
// Copy parent lineage
let child_lineage = parent_lineage.clone();

// Increment generation
child_lineage.generation_count += 1;
child_lineage.parent_lineage = Some(parent_lineage.lineage_id);
```

### 4.3 Mutation Application

**Synchronous, probabilistic**:
```rust
// Apply mutation with probability μ=0.05
if random() < MUTATION_RATE {
    let mutation = generate_mutation(&child_lineage);
    child_lineage.apply_mutation(mutation);
    child_lineage.mutation_count += 1;
    child_lineage.last_mutation_generation = current_generation;
}
```

### 4.4 Archive Weak Sampling

**Synchronous, low probability**:
```rust
// Weak sampling with p=0.01
if random() < ARCHIVE_SAMPLE_PROBABILITY {
    let record = archive.random_sample();
    let lesson = compress_to_lesson(record);
    
    // Add to distilled lessons (max 5, oldest dropped)
    child_lineage.distilled_lessons.push(lesson);
    if child_lineage.distilled_lessons.len() > MAX_DISTILLED_LESSONS {
        child_lineage.distilled_lessons.remove(0);  // Drop oldest
    }
}
```

**Constraints**:
- Sampling probability: p ≤ 0.01
- Sample selection: Random, not "best"
- Data returned: Compressed lesson only, not full record
- No direct query: Cannot request specific information

### 4.5 Child Initialization

**Result**:
```rust
let child = Agent {
    id: generate_agent_id(),
    cell_memory: CellMemory::empty(),      // Fresh Layer 1
    lineage: child_lineage,                 // Inherited Layer 2 (possibly with Archive hint)
};
```

---

## 5. Death Event Interface

### 5.1 Function Signature

```rust
fn death_event(
    cell_id: AgentID,
    death_cause: DeathCause,
    final_cell_memory: &CellMemory,
    final_state: SystemState,
    archive: &mut CausalArchive,            // Layer 3
) -> Option<EventID>;                      // Returns EventID if archived
```

### 5.2 Significance Check

**Synchronous**:
```rust
fn is_significant_event(
    death_cause: &DeathCause,
    final_state: &SystemState,
) -> bool {
    match death_cause {
        DeathCause::BossKill if is_first_in_cluster => true,
        DeathCause::Starvation if population_drop > 0.20 => true,
        DeathCause::CascadeTrigger => true,
        _ if death_impact_score > SIGNIFICANCE_THRESHOLD => true,
        _ => false,
    }
}
```

### 5.3 Archive Write (Conditional)

**Asynchronous queue**:
```rust
if is_significant_event(death_cause, final_state) {
    let record = CausalArchiveRecord {
        event_id: generate_event_id(),
        timestamp: current_generation,
        event_type: EventType::from(death_cause),
        // ... collect evidence from final_cell_memory and final_state
    };
    
    // Queue for async write (don't block death process)
    archive.write_queue.push(record);
    
    return Some(record.event_id);
} else {
    return None;  // Not significant, no archive entry
}
```

**Constraints**:
- Write trigger: Significant events only
- Write rate: Max 1/100 generations
- Evidence required: Yes
- Async: Death process not blocked

### 5.4 Lineage Update

**Synchronous**:
```rust
// Update lineage statistics
lineage.record_death(death_cause);
lineage.current_members -= 1;

if lineage.current_members == 0 {
    lineage.is_extinct = true;
    // Final lineage summary may be archived
    archive.write_lineage_summary(lineage);
}
```

---

## 6. Newborn Initialization Interface

### 6.1 Function Signature

```rust
fn newborn_init(
    child_id: AgentID,
    parent_lineage: &LineageMemory,
    archive: &CausalArchive,
) -> (CellMemory, LineageMemory);
```

### 6.2 Cell Memory Creation

**Fresh start**:
```rust
let cell_memory = CellMemory {
    recent_energy_history: Vec::new(),
    recent_threat_timestamps: Vec::new(),
    neighbor_trust: HashMap::new(),
    // ... all fields initialized empty or default
    created_at: current_generation,
};
```

### 6.3 Lineage Inheritance

See Section 4.2-4.4.

### 6.4 No Direct Archive Access

**Hard constraint**: Newborn cannot directly query Archive.
```rust
// FORBIDDEN
// let answer = archive.query("how do I survive?");  // NOT ALLOWED
```

Archive influence is only via:
- Lineage inheritance (Section 4.2)
- Weak sampling (Section 4.4)

---

## 7. Metrics Layer Interface

### 7.1 Observability Functions

**Read-only access for metrics collection**:
```rust
fn observe_cell_memory_stats(
    cells: &[Agent],
) -> CellMemoryMetrics {
    CellMemoryMetrics {
        avg_memory_size: cells.iter().map(|c| c.cell_memory.size()).mean(),
        avg_stress_level: cells.iter().map(|c| c.cell_memory.accumulated_stress).mean(),
        mood_distribution: cells.iter().map(|c| c.cell_memory.current_mood).histogram(),
    }
}

fn observe_lineage_stats(
    lineages: &[LineageMemory],
) -> LineageMetrics {
    LineageMetrics {
        lineage_count: lineages.len(),
        avg_generation_count: lineages.iter().map(|l| l.generation_count).mean(),
        extinction_rate: lineages.iter().filter(|l| l.is_extinct).count() / lineages.len(),
        strategy_distribution: lineages.iter().map(|l| l.preferred_strategy).histogram(),
    }
}

fn observe_archive_stats(
    archive: &CausalArchive,
) -> ArchiveMetrics {
    ArchiveMetrics {
        record_count: archive.records.len(),
        write_rate: archive.records.len() as f32 / current_generation as f32,
        event_type_distribution: archive.records.iter().map(|r| r.event_type).histogram(),
        avg_severity: archive.records.iter().map(|r| r.severity).mean(),
    }
}
```

### 7.2 Impact on [CDI, CI, r]

**No direct impact**:
- Memory layers do not directly modify CDI formula
- Memory layers do not directly modify CI formula
- Memory layers do not directly modify r formula

**Indirect impact observable**:
- Memory influences cell behavior
- Cell behavior influences network structure
- Network structure influences CDI/CI/r
- Metrics capture the result, not the cause

### 7.3 Extended Output Format

**Backward compatible**:
```csv
// v18 format (still works)
generation,population,avg_cdi,extinct_count,alive_universes
```

**v19 extended**:
```csv
// v19 format (additional columns, optional)
generation,population,avg_cdi,avg_ci,avg_sync_r,extinct_count,alive_universes,
avg_cell_memory_size,avg_stress_level,lineage_count,archive_record_count
```

---

## 8. Synchronization and Timing

### 8.1 Synchronous Operations

| Operation | Latency Requirement | Blocking? |
|-----------|-------------------|-----------|
| CellMemory read | < 1 microsecond | Yes |
| CellMemory write | < 1 microsecond | Yes |
| Lineage inheritance | < 10 microseconds | Yes |
| Lineage mutation | < 10 microseconds | Yes |
| Archive sampling | < 100 microseconds | Yes (rare) |

### 8.2 Asynchronous Operations

| Operation | Latency Tolerance | Queue? |
|-----------|------------------|--------|
| Archive write | < 1 second | Yes |
| Metrics observation | < 1 generation | Yes |
| Archive compression | Background | Yes |

### 8.3 Audit Trail

**All write operations logged**:
```rust
struct AuditLog {
    timestamp: Generation,
    operation: OperationType,
    actor: AgentID or System,
    target: TargetID,
    success: bool,
    hash: Hash,
}
```

---

## 9. Access Control Summary

### 9.1 Permission Matrix

| Operation | Cell | Lineage | Archive | Notes |
|-----------|------|---------|---------|-------|
| **CellMemory::read** | Self only | N/A | N/A | Every tick |
| **CellMemory::write** | Self only | N/A | N/A | Event-driven |
| **LineageMemory::read** | At birth | Self | N/A | Inherited |
| **LineageMemory::write** | N/A | System | N/A | Mutation only |
| **Archive::read** | N/A | At birth (0.01) | Audit only | Weak sampling |
| **Archive::write** | N/A | N/A | Death event | Async, audited |

### 9.2 Forbidden Operations (Enforced)

```rust
// These operations MUST be rejected at compile time or runtime

// Forbidden 1: Cell direct Archive query
let answer = archive.query(...);  // ERROR: Cell has no Archive reference

// Forbidden 2: Archive direct Cell overwrite
archive.inject_strategy(cell_id, strategy);  // ERROR: No such interface

// Forbidden 3: Lineage direct Archive upload
lineage.upload_to_archive();  // ERROR: Lineage cannot write Archive

// Forbidden 4: Cell read other Cell
let other_memory = other_cell.cell_memory;  // ERROR: Private field
```

---

## 10. Integration Validation

### 10.1 Compile-Time Checks

- [ ] Cell struct has no Archive field
- [ ] Archive methods not callable from Cell scope
- [ ] Lineage mutation rate constant enforced
- [ ] Sampling probability constant enforced

### 10.2 Runtime Checks

- [ ] Archive query from Cell triggers panic/error
- [ ] Sampling probability verified at each sample
- [ ] Memory size limits enforced
- [ ] Write rate limits enforced

### 10.3 Experimental Validation

- [ ] CDI/CI/r metrics stable with memory integration
- [ ] Memory-enabled runs comparable to v18 baselines
- [ ] P1 experiments function correctly
- [ ] No God-mode behavior observed

---

## Appendix A: Interface Dependency Graph

```
cell_tick()
├── CellMemory::read() [Sync, every tick]
└── CellMemory::write() [Sync, on event]

reproduction()
├── LineageMemory::inherit() [Sync, on birth]
├── LineageMemory::mutate() [Sync, on birth]
└── Archive::sample() [Sync, p=0.01 on birth]

death_event()
├── Archive::write() [Async, if significant]
└── LineageMemory::update() [Sync]

metrics_layer()
├── CellMemory::observe() [Async, read-only]
├── LineageMemory::observe() [Async, read-only]
└── Archive::observe() [Async, read-only]
```

---

## Appendix B: Error Handling Strategy

| Error | Response | Log |
|-------|----------|-----|
| Memory overflow | Truncate oldest | Warning |
| Archive write fail | Retry queue | Error |
| Unauthorized access | Reject + audit | Critical |
| Mutation rate exceed | Clamp to μ | Info |
| Sampling rate exceed | Reject sample | Warning |

---

*Specification Version*: 1.0  
*Next Step*: Validation Protocol (Instruction 5) or Codex Implementation Brief (Instruction 6)  
*Dependencies*: MEMORY_DATA_SCHEMA_v1.md
