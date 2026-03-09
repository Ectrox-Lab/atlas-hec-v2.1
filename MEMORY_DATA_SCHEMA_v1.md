# Memory Data Schema v1.0
## Minimum Struct Definitions for Three-Layer Memory

**Version**: 1.0  
**Date**: 2026-03-09  
**Depends on**: THREE_LAYER_MEMORY_ARCHITECTURE_v1.md, MEMORY_FLOW_STATE_MACHINE_v1.md  
**Constraint**: Schema only. No impl, no functions, no methods.

---

## 1. Primitive Types

```rust
// Type aliases for clarity
type Generation = u64;
type AgentID = UUID;
type LineageID = UUID;
type EventID = UUID;
type Coord = (i32, i32);
type Region = Vec<Coord>;
```

---

## 2. CellMemory

### 2.1 Struct Definition

```rust
struct CellMemory {
    // Section: Temporal Traces (rolling window)
    recent_energy_history: Vec<f32>,           // Length: MAX_WINDOW = 100
    recent_threat_timestamps: Vec<Generation>, // When threats encountered
    
    // Section: Spatial Context
    last_food_location: Option<Coord>,
    last_threat_location: Option<Coord>,
    home_territory: Option<Region>,            // Explored safe zone
    
    // Section: Social Context
    neighbor_trust: HashMap<AgentID, f32>,     // Range: [-1.0, 1.0]
    last_collaboration_partner: Option<AgentID>,
    last_collaboration_outcome: Option<CollaborationOutcome>,
    
    // Section: Action History
    recent_action_success: HashMap<ActionType, SuccessRate>,
    action_attempts: HashMap<ActionType, u32>,
    
    // Section: State
    current_mood: Mood,
    accumulated_stress: f32,                   // Range: [0.0, 1.0]
    
    // Section: Metadata
    created_at: Generation,
    last_updated: Generation,
    entry_count: usize,                        // For size tracking
}
```

### 2.2 Field Specifications

| Field | Type | Range/Constraints | Decay? | Persist? | Notes |
|-------|------|-------------------|--------|----------|-------|
| recent_energy_history | Vec<f32> | Length ≤ 100, values ≥ 0 | Yes | No | Rolling window |
| recent_threat_timestamps | Vec<Gen> | Length ≤ 20 | Yes | No | Time-decay priority |
| last_food_location | Option<Coord> | Valid coordinates | Yes | No | TTL = 50 ticks |
| last_threat_location | Option<Coord> | Valid coordinates | Yes | No | TTL = 100 ticks |
| home_territory | Option<Region> | Max 100 cells | No | Yes | Stable safe zone |
| neighbor_trust | HashMap<ID, f32> | Max 20 entries, value ∈ [-1,1] | Yes | No | Exponential decay 0.99/tick |
| last_collaboration_partner | Option<ID> | Valid AgentID | Yes | No | Single partner |
| last_collaboration_outcome | Option<Enum> | {Success, Failure, Betrayed} | Yes | No | One-shot |
| recent_action_success | HashMap<Action, f32> | Success rate ∈ [0,1] | Yes | Yes | Weighted by recency |
| action_attempts | HashMap<Action, u32> | Count | No | No | Diagnostic only |
| current_mood | Enum | {Explore, Flee, Cooperate, Rest} | Yes | No | Derived from state |
| accumulated_stress | f32 | [0.0, 1.0] | Yes | No | Decays 0.01/tick |
| created_at | Generation | Valid timestamp | No | Yes | Immutable |
| last_updated | Generation | Valid timestamp | N/A | N/A | Auto-updated |
| entry_count | usize | ≥ 0 | N/A | N/A | For memory pressure |

### 2.3 Constants

```rust
const MAX_CELL_MEMORY_WINDOW: usize = 100;
const MAX_NEIGHBOR_TRACKED: usize = 20;
const MAX_ACTION_TYPES: usize = 10;
const FOOD_LOCATION_TTL: Generation = 50;
const THREAT_LOCATION_TTL: Generation = 100;
const TRUST_DECAY_RATE: f32 = 0.99;
const STRESS_DECAY_RATE: f32 = 0.01;
```

---

## 3. LineageMemory

### 3.1 Struct Definition

```rust
struct LineageMemory {
    // Section: Identity
    lineage_id: LineageID,
    parent_lineage: Option<LineageID>,
    generation_count: u32,
    
    // Section: Heritable Traits
    preferred_strategy: Strategy,
    risk_tolerance: f32,                       // [0.0, 1.0]
    exploration_bias: f32,                     // [0.0, 1.0]
    cooperation_threshold: f32,                // [0.0, 1.0]
    
    // Section: Performance Statistics
    average_lifespan: f32,
    total_members: u32,
    current_members: u32,
    extinction_risk_score: f32,                // [0.0, 1.0]
    
    // Section: Death Analysis
    common_death_causes: Vec<DeathCause>,      // Top 3 causes
    death_cause_frequency: HashMap<DeathCause, f32>,
    
    // Section: Successful Adaptations
    successful_traits: Vec<(Trait, SuccessRate)>,
    failed_traits: Vec<(Trait, FailureRate)>,
    
    // Section: Distilled Lessons (from Archive sampling)
    distilled_lessons: Vec<Lesson>,            // Max 5, oldest dropped
    
    // Section: Mutation State
    mutation_count: u32,
    last_mutation_generation: Generation,
    
    // Section: Metadata
    created_at: Generation,
    last_updated: Generation,
    is_extinct: bool,
}
```

### 3.2 Field Specifications

| Field | Type | Range/Constraints | Decay? | Persist? | Notes |
|-------|------|-------------------|--------|----------|-------|
| lineage_id | UUID | Unique | No | Yes | Immutable |
| parent_lineage | Option<UUID> | Valid or None | No | Yes | Ancestry |
| generation_count | u32 | ≥ 1 | No | Yes | Increments |
| preferred_strategy | Enum | {Aggressive, Cooperative, Exploratory, Conservative} | Yes | Yes | Mutable via selection |
| risk_tolerance | f32 | [0.0, 1.0] | Yes | Yes | Heritable, mutable |
| exploration_bias | f32 | [0.0, 1.0] | Yes | Yes | Heritable, mutable |
| cooperation_threshold | f32 | [0.0, 1.0] | Yes | Yes | Heritable, mutable |
| average_lifespan | f32 | ≥ 0 | Yes | Yes | Rolling average |
| total_members | u32 | ≥ current_members | No | Yes | Cumulative |
| current_members | u32 | ≥ 0 | N/A | N/A | Runtime only |
| extinction_risk_score | f32 | [0.0, 1.0] | Yes | No | Computed |
| common_death_causes | Vec<Cause> | Length ≤ 3 | Yes | Yes | Top causes |
| death_cause_frequency | HashMap | Sum = 1.0 | Yes | Yes | Distribution |
| successful_traits | Vec | Max 10 entries | Yes | Yes | Selection memory |
| failed_traits | Vec | Max 10 entries | Yes | Yes | Negative learning |
| distilled_lessons | Vec<Lesson> | Max 5 | No | Yes | From Archive |
| mutation_count | u32 | ≥ 0 | No | Yes | Cumulative |
| last_mutation_generation | Gen | Valid | No | Yes | Timestamp |
| created_at | Gen | Valid | No | Yes | Immutable |
| last_updated | Gen | Valid | N/A | N/A | Auto-updated |
| is_extinct | bool | Boolean | No | Yes | Set on last death |

### 3.3 Constants

```rust
const MAX_DISTILLED_LESSONS: usize = 5;
const MAX_TRACKED_TRAITS: usize = 10;
const MUTATION_RATE: f32 = 0.05;
const TRAIT_DRIFT_RATE: f32 = 0.01;
const LINEAGE_SELECTION_PRESSURE: f32 = 0.1;
```

### 3.4 Mutation Specification

```rust
struct Mutation {
    trait_affected: Trait,
    original_value: f32,
    mutated_value: f32,
    mutation_type: MutationType,  // {Point, Shift, Drift}
    generation: Generation,
}

enum MutationType {
    Point,      // Single value change
    Shift,      // Distribution shift
    Drift,      // Gradual random walk
}
```

---

## 4. CausalArchiveRecord

### 4.1 Struct Definition

```rust
struct CausalArchiveRecord {
    // Section: Identification
    event_id: EventID,
    timestamp: Generation,
    event_type: EventType,
    severity: Severity,
    
    // Section: System State
    preconditions: SystemStateSnapshot,
    triggers: Vec<TriggerEvent>,
    consequences: Vec<OutcomeEvent>,
    
    // Section: Evidence Chain
    evidence: Vec<Evidence>,
    source_agents: Vec<AgentID>,
    witness_agents: Vec<AgentID>,
    
    // Section: Metrics
    cdi_at_event: f32,
    ci_at_event: f32,
    sync_r_at_event: f32,
    population_at_event: u32,
    extinction_count_at_event: u32,
    
    // Section: Causal Analysis
    causal_summary: String,                    // Max 256 chars
    key_factors: Vec<Factor>,
    counterfactual_notes: Option<String>,
    
    // Section: Audit
    created_by: AgentID,                       // Recording agent
    audit_trail: Vec<AuditPoint>,
    verification_hash: Hash,
    
    // Section: Compression Status
    compression_level: CompressionLevel,       // {Full, Summary, Aggregate}
    original_size_bytes: usize,
}
```

### 4.2 Field Specifications

| Field | Type | Range/Constraints | Decay? | Persist? | Notes |
|-------|------|-------------------|--------|----------|-------|
| event_id | UUID | Unique | No | Yes | Immutable |
| timestamp | Gen | Valid | No | Yes | Immutable |
| event_type | Enum | {Extinction, Innovation, Collapse, Adaptation, Cascade} | No | Yes | Classification |
| severity | Enum | {Low, Medium, High, Critical} | No | Yes | Impact |
| preconditions | Snapshot | Valid state | No | Yes | Before event |
| triggers | Vec<Event> | Non-empty | No | Yes | Immediate causes |
| consequences | Vec<Event> | May be empty | No | Yes | Effects |
| evidence | Vec<Evidence> | Min 1, Max 10 | No | Yes | Proof chain |
| source_agents | Vec<ID> | Non-empty | No | Yes | Primary actors |
| witness_agents | Vec<ID> | May be empty | No | Yes | Observers |
| cdi_at_event | f32 | [0.0, 1.0] | No | Yes | Metric snapshot |
| ci_at_event | f32 | [0.0, 1.0] | No | Yes | Metric snapshot |
| sync_r_at_event | f32 | [0.0, 1.0] | No | Yes | Metric snapshot |
| population_at_event | u32 | ≥ 0 | No | Yes | Metric snapshot |
| extinction_count_at_event | u32 | ≥ 0 | No | Yes | Metric snapshot |
| causal_summary | String | Len ≤ 256 | No | Yes | Human-readable |
| key_factors | Vec<Factor> | Max 5 | No | Yes | Causal decomposition |
| counterfactual_notes | Option<String> | Len ≤ 512 | No | Yes | What if? |
| created_by | ID | Valid | No | Yes | Recording agent |
| audit_trail | Vec<AuditPoint> | Non-empty | No | Yes | Verification chain |
| verification_hash | Hash | Valid hash | No | Yes | Integrity check |
| compression_level | Enum | {Full, Summary, Aggregate} | N/A | Yes | Evolves over time |
| original_size_bytes | usize | > 0 | No | Yes | For compression ratio |

### 4.3 Supporting Types

```rust
struct SystemStateSnapshot {
    generation: Generation,
    global_cdi: f32,
    global_ci: f32,
    global_sync_r: f32,
    population_count: u32,
    universe_count: u32,
    boss_positions: Vec<Coord>,
    resource_distribution: ResourceMap,
}

struct Evidence {
    evidence_type: EvidenceType,
    data: Vec<u8>,
    timestamp: Generation,
    source: AgentID,
    confidence: f32,                           // [0.0, 1.0]
}

enum EvidenceType {
    Observation,       // Direct witness
    Measurement,       // Metric reading
    Inference,         // Derived conclusion
    Testimony,         // Reported by agent
}

struct AuditPoint {
    timestamp: Generation,
    auditor: AgentID,
    action: AuditAction,
    hash_before: Hash,
    hash_after: Hash,
}

enum AuditAction {
    Create,
    Verify,
    Compress,
    Archive,
}

enum CompressionLevel {
    Full,        // Complete record
    Summary,     // Key fields only
    Aggregate,   // Statistical summary only
}
```

### 4.4 Constants

```rust
const MAX_EVIDENCE_PER_RECORD: usize = 10;
const MAX_CAUSAL_SUMMARY_LEN: usize = 256;
const MAX_COUNTERFACTUAL_LEN: usize = 512;
const MAX_KEY_FACTORS: usize = 5;
const ARCHIVE_RETENTION_GENERATIONS: Generation = 10_000;
const COMPRESSION_THRESHOLD_GEN: Generation = 1_000;
```

---

## 5. ArchiveSamplingPolicy

### 5.1 Struct Definition

```rust
struct ArchiveSamplingPolicy {
    // Section: Sampling Parameters
    sample_probability: f32,                   // p = 0.01 default
    max_samples_per_lifetime: u32,             // 1
    
    // Section: Selection Bias
    recency_bias: f32,                         // [0.0, 1.0]
    relevance_bias: f32,                       // [0.0, 1.0]
    severity_bias: f32,                        // [0.0, 1.0]
    
    // Section: Compression Policy
    compression_threshold: Generation,         // When to compress
    compression_ratio: f32,                    // Target size reduction
    
    // Section: Access Control
    allow_direct_query: bool,                  // MUST BE FALSE
    allow_audit_access: bool,                  // TRUE for system only
    allow_weak_sampling: bool,                 // TRUE with probability
}
```

### 5.2 Hard Constraints

```rust
// These are INVARIANTS, not defaults
const SAMPLING_PROBABILITY_MAX: f32 = 0.01;
const SAMPLES_PER_LIFETIME_MAX: u32 = 1;
const DIRECT_QUERY_ALLOWED: bool = false;
```

---

## 6. MemoryAccessGuard

### 6.1 Struct Definition

```rust
struct MemoryAccessGuard {
    // Section: Access Context
    accessor_id: AgentID,
    accessor_type: AccessorType,               // {Cell, System, Audit}
    access_timestamp: Generation,
    
    // Section: Requested Access
    target_layer: MemoryLayer,                 // {Cell, Lineage, Archive}
    target_id: ID,                             // AgentID or LineageID
    access_type: AccessType,                   // {Read, Write, Sample}
    
    // Section: Policy Check
    policy_compliant: bool,
    rejection_reason: Option<RejectionReason>,
    
    // Section: Audit Log
    access_granted: bool,
    data_accessed: Option<DataFingerprint>,
}

enum AccessorType {
    Cell,        // Agent accessing own memory
    Parent,      // Parent accessing child (limited)
    System,      // System-level access
    Audit,       // External audit
}

enum MemoryLayer {
    Cell,
    Lineage,
    Archive,
}

enum AccessType {
    Read,
    Write,
    Sample,      // Archive only
    Audit,       // Read with full evidence
}
```

### 6.2 Validation Matrix

| Accessor | Target | Read | Write | Notes |
|----------|--------|------|-------|-------|
| Cell | Own Cell Memory | ✅ | ✅ | Self only |
| Cell | Other Cell | ❌ | ❌ | Isolation enforced |
| Cell | Own Lineage | ✅ (birth only) | ❌ | Inherited at birth |
| Cell | Archive | ❌ | ❌ | Direct query forbidden |
| Parent | Child Lineage | ❌ | ❌ | Mutation, not write |
| System | Any (audit) | ✅ | ❌ | Read-only access |
| Audit | Archive | ✅ (full) | ❌ | Complete evidence |

---

## 7. Cross-References

### 7.1 References to Architecture

- Section 3 (CellMemory) → Architecture §3
- Section 4 (LineageMemory) → Architecture §4
- Section 5 (CausalArchiveRecord) → Architecture §5
- Section 6 (ArchiveSamplingPolicy) → Architecture §5.5, §7.3

### 7.2 References to State Machine

- CellMemory lifecycle → StateMachine §3.1
- LineageMemory transitions → StateMachine §3.2
- ArchiveRecord creation → StateMachine §3.3
- AccessGuard validation → StateMachine §5 (Forbidden Flows)

---

## 8. Schema Validation Checklist

- [ ] All struct fields have specified types
- [ ] All fields have range/constraints documented
- [ ] All fields have decay/persist flags
- [ ] No complex methods or impl blocks included
- [ ] All constants defined with values
- [ ] All enums have variant definitions
- [ ] Cross-references to Architecture and State Machine correct
- [ ] Access control matrix complete
- [ ] Hard constraints (SAMPLING_PROBABILITY_MAX, etc.) defined
- [ ] No God-mode access paths in AccessGuard

---

*Specification Version*: 1.0  
*Next Step*: Bio-World v19 Integration Spec (Instruction 4)  
*Dependencies*: MEMORY_FLOW_STATE_MACHINE_v1.md
