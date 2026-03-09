# Atlas-BioWorld Integration Contract

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Status**: Draft - Pending Bio-World Implementation

---

## 1. Purpose

This contract defines the minimal integration interface between:
- **Atlas-HEC v2.1** (Research control plane, audit authority)
- **Bio-World v19** (Simulation engine, three-layer memory implementation)

The contract enforces:
- Read-only observation from Atlas to Bio-World
- No direct control of cellular agents
- Anti-god-mode boundary preservation
- Falsification-first validation

---

## 2. Shared Metrics Schema

### 2.1 Required Now (Phase 1)

**Status**: Must be implemented in current sprint  
**Deadline**: 2026-03-16  
**Owner**: Bio-World

| Field | Type | Source | Description | Verification |
|-------|------|--------|-------------|--------------|
| `archive_sample_attempts` | u32 | Bio-World | Count of archive sampling attempts per generation | `grep -c "archive_sample_attempts" population.csv` |
| `archive_sample_successes` | u32 | Bio-World | Count of successful archive retrievals | Sum of actual samples taken |
| `archive_influenced_births` | u32 | Bio-World | Newborns with archive-derived lessons | Count births with lesson injection |
| `lineage_diversity` | u32 | Bio-World | Count of distinct lineage_id values | `HashSet::len()` of lineage_ids |
| `top1_lineage_share` | f32 | Bio-World | Proportion of population from largest lineage | `max(lineage_counts) / total_pop` |
| `strategy_entropy` | f32 | Bio-World | Shannon entropy of strategy distribution | `-Σ p_i * ln(p_i)` over strategies |
| `collapse_event_count` | u32 | Bio-World | Number of extinction events in window | Rolling count over 100 gens |

**Acceptance Criteria**:
- [ ] All 7 fields present in CSV header
- [ ] All fields have non-zero variance across conditions
- [ ] Values respond appropriately to experimental conditions
- [ ] No missing values in any row

### 2.2 Reserved Next (Phase 2)

**Status**: Design complete, implementation deferred  
**Deadline**: 2026-03-30  
**Owner**: Atlas-HEC (computation), Bio-World (data export)

| Field | Type | Source | Description | Dependency |
|-------|------|--------|-------------|------------|
| `continuity_signature` | String | Atlas-HEC | Lineage continuity hash | Requires Phase 1 metrics stable |
| `oracle_leak_score` | f32 | Atlas-HEC | Computed from information flow analysis | Requires ContinuityProbe |
| `archive_exposure_gain` | f32 | Atlas-HEC | Per-generation info gain from archive | Requires archive content analysis |
| `drift_score` | f32 | Atlas-HEC | Population-level drift measurement | Requires multi-seed analysis |
| `collapse_risk` | f32 | Atlas-HEC | Computed extinction probability | Requires ML model training |

**Unblock Conditions**:
1. Phase 1 fields validated
2. Sentinel run passes falsification
3. ContinuityProbe operational
4. Cross-repo data pipeline stable

### 2.3 CDI/CI/r State Vector

```rust
struct SystemState {
    generation: u32,
    cdi: f32,           // Complexity Decline Index
    ci: f32,            // Condensation Index
    r: f32,             // Synchronization order parameter
    n: u32,             // Population
    
    // Memory layer health
    l1_health: f32,     // Cell memory utilization
    l2_health: f32,     // Lineage memory diversity
    l3_health: f32,     // Archive write rate / capacity
}
```

---

## 3. CollectiveContinuityProbe (Minimal Super-Brain)

### 3.1 Core Responsibility

Monitor cross-lineage continuity and detect early warning signals of:
- Strategy convergence (reduced entropy)
- Lineage monopoly (increased top1 share)
- Archive over-reliance (increased exposure gain)
- Memory layer degradation

### 3.2 Minimal Data Structure

```rust
struct ContinuityProbe {
    // Temporal window (last 100 generations)
    history: RingBuffer<SystemState>,
    
    // Derived metrics
    lineage_diversity_trend: Trend,
    strategy_entropy_trend: Trend,
    archive_influence_rate: f32,
    
    // Alerts
    convergence_warning: bool,
    collapse_warning: bool,
    oracle_leak_detected: bool,
}

struct Trend {
    slope: f32,
    r_squared: f32,
    p_value: f32,
}
```

### 3.3 Update Frequency

- **Per-generation**: Update state buffer
- **Per-100-generations**: Compute trends
- **Per-500-generations**: Generate report

### 3.4 Input/Output

**Input**:
- SystemState from Bio-World
- Archive read access (audit only)

**Output**:
- ContinuityScore [0.0, 1.0]
- Warning flags
- Falsification conditions met

### 3.5 Relationship to L1/L2/L3

| Layer | Relationship |
|-------|--------------|
| L1 Cell | Observer only, no influence |
| L2 Lineage | Monitor diversity, detect convergence |
| L3 Archive | Read for audit, compute exposure gain |

### 3.6 Anti-Cheat Boundaries

- Cannot influence cell decisions
- Cannot modify archive contents
- Cannot inject signals into simulation
- Read-only observation role

### 3.7 Falsification Conditions

The probe is falsified if:
1. Lineage diversity increases while collapse occurs
2. Archive exposure gain correlates with survival
3. Strategy entropy predicts extinction worse than CDI
4. Convergence warning false positive rate > 20%

---

## 4. Anti-God-Mode Boundaries

### 4.1 Enforced Constraints

| Constraint | Bio-World | Atlas-HEC |
|------------|-----------|-----------|
| Cell → Archive direct query | Forbidden | N/A |
| Archive → Cell policy override | Forbidden | N/A |
| Perfect answer injection | Forbidden | N/A |
| Global state mutation | N/A | Forbidden |
| Central controller | N/A | Forbidden |

---

## 5. Implementation Status

| Component | Bio-World | Atlas-HEC | Status |
|-----------|-----------|-----------|--------|
| L1 Cell Memory | ✓ | N/A | [Verified] Implemented |
| L2 Lineage Memory | ✓ | N/A | [Verified] Implemented |
| L3 Causal Archive | ✓ | N/A | [Verified] Implemented |
| Metrics Export | Partial | N/A | [Inference] CSV only |
| JSONL Stream | ✗ | N/A | [Proposal] Needed |
| Atlas Bridge | N/A | ✗ | [Proposal] Not started |
| ContinuityProbe | N/A | ✗ | [Proposal] Design only |

---

## 6. Next Actions

1. **Bio-World**: Implement JSONL metrics stream
2. **Bio-World**: Add contract-specified metrics to CSV output
3. **Atlas-HEC**: Implement read-only bridge
4. **Atlas-HEC**: Implement ContinuityProbe
5. **Both**: Run integration tests
6. **Both**: Execute falsification experiments

---

**Contract Owners**:
- Atlas-HEC: ZeroClaw Lab
- Bio-World: Ectrox Lab

**Review Cycle**: Weekly until v1.0 stable
