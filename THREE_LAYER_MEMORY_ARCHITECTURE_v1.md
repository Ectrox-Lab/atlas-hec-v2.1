# Three-Layer Memory Architecture v1.0
## Bio-World / Atlas Unified Research Stack

**Version**: 1.0  
**Date**: 2026-03-09  
**Status**: Design Specification  

---

## 1. Design Goals

1.1 **Explicit Separation**
- Unambiguously partition memory into three distinct layers with non-overlapping responsibilities
- Prevent conceptual collapse between local experience, heritable traits, and global history

1.2 **Emergence Preservation**
- Ensure global archive cannot short-circuit local decision-making
- Maintain distributed autonomy of cellular agents

1.3 **Causal Traceability**
- Every significant event must be auditable to its source layer
- Prevent "god mode" interventions from archive to cell

1.4 **Minimal Integration**
- Add memory layers without disrupting existing [CDI, CI, r] metrics
- Backward compatible with Bio-World v18 experimental framework

---

## 2. Non-Goals

2.1 **Not a Universal Memory System**
- Do not attempt to unify all memory types into single abstraction
- Do not create a "one size fits all" memory interface

2.2 **Not a Perfect Knowledge Base**
- Archive is not a ground truth oracle
- Archive contains historical traces, not optimal solutions

2.3 **Not a Direct Control Channel**
- Archive must not override cellular autonomy
- No direct archive → behavior mapping

2.4 **Not Implemented in This Document**
- No code, no algorithms, no data structures beyond field definitions
- Implementation deferred to subsequent specifications

---

## 3. Layer 1: Cell Memory

### 3.1 Definition
First-person, short-term, experiential state of individual cellular agent.

### 3.2 Data Structure
```
CellMemory {
    // Temporal traces (rolling window, last N ticks)
    recent_energy_history: Vec<Float>,      // [t-10, t-9, ..., t]
    recent_threat_history: Vec<Threat>,     // encounters with boss/danger
    
    // Spatial context
    last_food_location: Option<Coord>,
    last_threat_location: Option<Coord>,
    home_territory: Option<Region>,
    
    // Social context
    neighbor_trust: Map<AgentID, Float>,    // [-1.0, 1.0]
    last_collaboration_outcome: Option<Outcome>,
    
    // Action outcomes
    recent_action_success: Map<Action, Float>, // success rate per action
    
    // State
    current_mood: Enum{Explore, Flee, Cooperate, Rest},
    accumulated_stress: Float,
}
```

### 3.3 Lifecycle
- **Birth**: Initialized empty or with minimal priors
- **Living**: Updated every tick based on experience
- **Reproduction**: NOT directly inherited (see Layer 2)
- **Death**: Discarded (trace may enter Layer 3 via audit)

### 3.4 Write Conditions
- Updated continuously during agent lifetime
- Write triggered by: energy change, threat detection, successful collaboration, failed action

### 3.5 Read Conditions
- Read every tick by cell decision logic
- Read scope: self only
- NO read access to other cells' Layer 1 memory

### 3.6 Decay/Forget Mechanism
- Rolling window: keep only last N ticks (N=100 default)
- Exponential decay: older events weighted lower
- Reset on major state change (near-death, reproduction)

### 3.7 Impact on Behavior
- Primary driver of cell's action selection
- Direct input to: movement, signal emission, collaboration acceptance
- Modulates: exploration rate, risk tolerance

---

## 4. Layer 2: Lineage Memory

### 4.1 Definition
Semi-stable, heritable strategy patterns transmitted through reproduction.

### 4.2 Data Structure
```
LineageMemory {
    // Heritable traits (encoded in DNA or epigenetic markers)
    preferred_strategy: Enum{Aggressive, Cooperative, Exploratory, Conservative},
    
    // Population-level patterns
    average_lifespan: Float,
    common_death_causes: Vec<DeathCause>,
    
    // Successful adaptations
    successful_traits: Map<Trait, SuccessRate>,
    
    // Lineage identity
    lineage_id: UUID,
    generation_count: Int,
    
    // Compressed experience (not raw events)
    distilled_lessons: Vec<Lesson>,  // max 5 lessons, oldest dropped
}
```

### 4.3 Lifecycle
- **Birth**: Inherited from parent(s) with mutation
- **Living**: Slowly updated based on population performance
- **Reproduction**: Transmitted to offspring with probability p (p=0.8 default)
- **Extinction**: Lost when last lineage member dies

### 4.4 Write Conditions
- Updated periodically (every 100 generations)
- Write triggered by: significant population event, strategy success/failure, extinction of related lineage

### 4.5 Read Conditions
- Read by newborn during initialization
- Read scope: own lineage only
- Read frequency: once at birth, not during lifetime

### 4.6 Decay/Mutation Mechanism
- Mutation rate: μ per generation (μ=0.05 default)
- Drift: traits slowly shift based on selection pressure
- Loss: forgotten if unsuccessful for N generations

### 4.7 Impact on Behavior
- Sets initial bias for newborn cells
- Influences: initial strategy, risk profile, collaboration tendency
- Does NOT override Layer 1 during lifetime

---

## 5. Layer 3: Causal Archive

### 5.1 Definition
Global, long-term, auditable record of significant system events with evidence chains.

### 5.2 Data Structure
```
CausalArchiveRecord {
    // Event identification
    event_id: UUID,
    timestamp: Generation,
    event_type: Enum{Extinction, Innovation, Collapse, Adaptation},
    
    // Causal context
    preconditions: Vec<SystemState>,
    triggers: Vec<Event>,
    consequences: Vec<Outcome>,
    
    // Evidence chain
    evidence: Vec<Evidence>,
    source_agents: Vec<AgentID>,
    audit_trail: Vec<AuditPoint>,
    
    // Metrics snapshot
    cdi_at_event: Float,
    ci_at_event: Float,
    population_at_event: Int,
    
    // Compressed narrative
    causal_summary: String,  // max 256 chars
}

CausalArchive {
    records: Vec<CausalArchiveRecord>,
    index: Map<EventType, Vec<RecordID>>,
    query_interface: RestrictedQueryInterface,
}
```

### 5.3 Lifecycle
- **Creation**: Written when significant event detected
- **Storage**: Persistent, append-only
- **Query**: Available for weak sampling only
- **Expiration**: Old records archived (not deleted) after N generations

### 5.4 Write Conditions
- Write triggered by: extinction event, major adaptation, system collapse, significant innovation
- Write rate: max 1 record per 100 generations per universe
- Audit requirement: every write must have evidence chain

### 5.5 Read Conditions (CRITICAL CONSTRAINTS)
- **Frequency**: Max once per cell lifetime
- **Scope**: Global, but sampling is WEAK and PROBABILISTIC
- **Method**: Query returns compressed prior, not direct answer
- **NO DIRECT READ**: Cell cannot directly query archive
- **SAMPLING ONLY**: Newborn may sample one record with probability p=0.01

### 5.6 Decay/Compression Mechanism
- Old records compressed: full detail → summary → statistical aggregate
- After 1000 generations: individual records → cohort statistics
- No deletion, but granularity decreases

### 5.7 Impact on Behavior (CONSTRAINED)
- Indirect only: via Layer 2 (if sampled during reproduction)
- Archive → Lineage (weak bias) → Cell (initial state)
- NO direct archive → cell path

---

## 6. Information Flow Constraints

### 6.1 Allowed Flows

```
[Cell Memory] ←→ [Cell Behavior]  (continuous, every tick)
       ↑
       | (birth initialization only)
       ↓
[Lineage Memory] ←→ [Heredity]  (reproduction events)
       ↑
       | (weak sampling, p=0.01)
       ↓
[Causal Archive] ←→ [Audit/Query]  (rare, constrained)
```

### 6.2 Forbidden Flows

- ❌ Cell Memory ←→ Causal Archive (direct query)
- ❌ Causal Archive → Cell Behavior (god mode)
- ❌ Causal Archive → Lineage Memory (forced injection)
- ❌ Lineage Memory → Cell Memory (runtime override)

### 6.3 Flow Frequency Limits

| Path | Max Frequency | Trigger |
|------|--------------|---------|
| Cell ↔ Behavior | 1/tick | Continuous |
| Lineage → Cell | 1/birth | Reproduction |
| Archive → Lineage | 1/birth × 0.01 | Probabilistic sample |
| Cell → Archive | 1/death | Significant event only |

---

## 7. Read/Write Policies

### 7.1 Layer 1 (Cell) Policies

| Operation | Policy |
|-----------|--------|
| Read | Unlimited, self-only |
| Write | Continuous, auto-update |
| Share | None (private) |
| Persist | No (ephemeral) |

### 7.2 Layer 2 (Lineage) Policies

| Operation | Policy |
|-----------|--------|
| Read | Once at birth |
| Write | Periodic (every 100 gen) |
| Share | Vertical (parent→child) |
| Persist | Yes (heritable) |
| Mutation | μ=0.05 per generation |

### 7.3 Layer 3 (Archive) Policies

| Operation | Policy |
|-----------|--------|
| Read | Sampled, p=0.01, weak prior only |
| Write | Event-triggered, audited |
| Share | Global, read-only |
| Persist | Permanent (compressed) |
| Query | Restricted interface only |

---

## 8. Anti-Cheating / Anti-God-Mode Rules

### 8.1 Hard Constraints (Must Be Enforced)

**Rule 1: No Perfect Information**
- Archive cannot contain optimal strategies
- Archive cannot contain "correct" actions
- Archive contains only: what happened, not what should happen

**Rule 2: No Direct Control**
- Archive query cannot return: "go left", "cooperate with agent 5"
- Archive query can return: "in similar situations, cooperation had 0.3 success rate"

**Rule 3: Sampling Imperfection**
- Newborn does not always get archive access (p=0.01)
- When accessed, gets random record, not "best" record
- Record is compressed summary, not full detail

**Rule 4: Lineage Is Not Archive**
- Lineage memory is traits, not experiences
- Lineage cannot "upload" to archive
- Lineage cannot "download" from archive

**Rule 5: Cell Is Isolated**
- Cell cannot know other cells' Layer 1 memory
- Cell cannot know global state beyond local perception
- Cell must act on partial information

### 8.2 Enforcement Mechanisms

- **Audit Layer**: Every archive read/write logged
- **Sandbox**: Cell decision logic has no archive reference
- **Mutation Gate**: Lineage mutations applied before inheritance
- **Query Limiter**: Archive queries counted and rate-limited

---

## 9. Minimal Integration Points with Bio-World v19

### 9.1 Existing Metrics Unaffected

[CDI, CI, r, N, E] continue to be computed as in v18.

Memory layers are internal to agents, not direct inputs to metrics.

### 9.2 New Observables

Optional metrics for validation:
- `avg_cell_memory_size`: average Layer 1 utilization
- `lineage_diversity`: number of distinct LineageMemory IDs
- `archive_query_rate`: frequency of Layer 3 sampling

### 9.3 Integration Hooks

**Hook 1: Cell Tick**
```
cell.tick() {
    local_state = read_cell_memory()
    action = decide(local_state, current_perception)
    update_cell_memory(action, outcome)
}
```

**Hook 2: Reproduction**
```
reproduce() {
    child_lineage = sample_lineage_memory(p=0.8) + mutate(μ=0.05)
    if random() < 0.01 {
        archive_hint = sample_causal_archive()
        child_lineage.distilled_lessons.push(archive_hint)
    }
    child = Agent(cell_memory=empty, lineage=child_lineage)
}
```

**Hook 3: Death**
```
die() {
    if is_significant_event() {
        write_causal_archive(
            preconditions=system_state,
            triggers=death_cause,
            evidence=collect_evidence()
        )
    }
}
```

### 9.4 No Changes to External Interface

- Input: same parameters as v18
- Output: same metrics as v18 (plus optional memory observables)
- Evolution.csv format: extended but backward compatible

---

## 10. Validation Criteria

### 10.1 Architecture Validation

| Criterion | Test | Pass Threshold |
|-----------|------|----------------|
| Separation | Cell cannot access archive directly | Code inspection |
| Isolation | Archive query rate < 0.01 per cell | Metric check |
| Heredity | Lineage traits persist > 5 generations | Observation |
| Decay | Cell memory window ≤ 100 ticks | Metric check |

### 10.2 Behavioral Validation

| Criterion | Test | Pass Threshold |
|-----------|------|----------------|
| Autonomy | Cells function without archive | Experiment |
| Emergence | Global patterns from local rules | Observation |
| No God Mode | Archive disabled → system still runs | Experiment |
| Traceability | Significant events auditable | Code inspection |

### 10.3 Integration Validation

| Criterion | Test | Pass Threshold |
|-----------|------|----------------|
| CDI Stability | Memory layers don't break CDI computation | Regression test |
| CI Accuracy | Network metrics still valid | Regression test |
| Performance | Overhead < 10% | Benchmark |

---

## Appendix A: Layer Comparison Summary

| Aspect | Cell Memory | Lineage Memory | Causal Archive |
|--------|-------------|----------------|----------------|
| **Timescale** | 10-100 ticks | 10-1000 generations | Permanent |
| **Scope** | Individual cell | Family/clade | Global system |
| **Perspective** | First-person | Inherited | Third-person |
| **Content** | Raw experience | Strategy bias | Event history |
| **Access** | Self only | Offspring only | Weak sampling |
| **Mutability** | High | Medium | Append-only |
| **Purpose** | Immediate action | Heritable tendency | Audit/Learning |

---

## Appendix B: Decision Flowchart

```
Agent needs to make decision:
    ↓
Query Cell Memory? → YES → Use local experience → Act
    ↓ NO
Query Lineage Memory? → Only at birth → Set initial bias
    ↓
Query Causal Archive? → NO (forbidden direct query)
    ↓
Archive accessible only via:
    - Death event write
    - Birth sampling (p=0.01)
    - External audit (outside agent)
```

---

*Specification Version*: 1.0  
*Next Step*: Memory Flow State Machine (Instruction 2)  
*Implementation Status*: Not started - awaiting downstream specifications
