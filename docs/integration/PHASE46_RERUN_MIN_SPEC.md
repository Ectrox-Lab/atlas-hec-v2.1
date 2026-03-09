# Phase 4.6 Minimal Rerun Specification

**Role**: Missing-Data Closure Lead  
**Date**: 2026-03-09  
**Status**: SPECIFICATION_FINAL  
**Scope**: MINIMAL - Only blocking conditions

---

## 1. Executive Summary

### Purpose
Generate minimum data required to resolve HOLD status and enable Phase 5 GO decision.

### Scope Constraint
**ONLY blocking conditions. NO optional expansions.**

### Success Criteria
- Validate R1 (L3 content relevance)
- Validate R3 (L2 necessity)
- Enable complete triage decision

---

## 2. Required Conditions (Blocking)

### Priority 1: L3_shuffled_p001

**Purpose**: Validate falsification rule R1 (L3 content matters)

**Configuration**:
```yaml
name: L3_shuffled_p001
description: Archive with shuffled entries (control)
config:
  L1_enabled: true
  L2_enabled: true
  L3_enabled: true
  archive_retrieval_prob: 0.001
  archive_shuffle: true          # ← Key difference
  boss_enabled: false
  
execution:
  universes: 8
  ticks: 5000                    # ← Extended from 1000
  seeds: [101, 102, 103]
  
output:
  population.csv: required
  cdi.csv: required
  extinction.csv: required
```

**Expected Result**: L3_shuffled < L3_real (if content matters)

**Validation Rule**:
```python
if adaptation_gain(shuffled) < adaptation_gain(real):
    R1_status = "SUPPORTED - Content matters"
    decision = "GO"
elif adaptation_gain(shuffled) ≈ adaptation_gain(real):
    R1_status = "FALSIFIED - Content irrelevant"
    decision = "NO-GO"
```

**Resource Estimate**:
- Compute: 8 universes × 5000 ticks = 40k ticks
- Time: ~2-4 hours (parallel)
- Storage: ~2 MB

---

### Priority 2: no_L2

**Purpose**: Validate falsification rule R3 (L2 maintains diversity)

**Configuration**:
```yaml
name: no_L2
description: Lineage tracking disabled
config:
  L1_enabled: true
  L2_enabled: false              # ← Key difference
  L3_enabled: true
  archive_retrieval_prob: 0.001
  boss_enabled: false
  
execution:
  universes: 8
  ticks: 5000
  seeds: [101, 102, 103]
  
output:
  population.csv: required
  cdi.csv: required
  extinction.csv: required
```

**Expected Result**: no_L2 < baseline (lineage tracking helps)

**Validation Rule**:
```python
if lineage_diversity(no_L2) < lineage_diversity(baseline):
    R3_status = "VALIDATED - L2 maintains diversity"
elif lineage_diversity(no_L2) ≥ lineage_diversity(baseline):
    R3_status = "UNCLEAR - L2 effect not detected"
```

**Resource Estimate**:
- Compute: 8 universes × 5000 ticks = 40k ticks
- Time: ~2-4 hours (parallel)
- Storage: ~2 MB

---

## 3. Optional Conditions (Non-Blocking)

### Priority 3: no_L1

**Purpose**: Optional analysis of intrinsic mortality

**Configuration**:
```yaml
name: no_L1
config:
  L1_enabled: false              # Intrinsic mortality OFF
  L2_enabled: true
  L3_enabled: true
  archive_retrieval_prob: 0.001
execution:
  universes: 8
  ticks: 5000
priority: OPTIONAL
blocking: false
```

**Run only if**: Time permits after P1 and P2

---

### Priority 4: L3_overpowered_direct

**Purpose**: Stress test high archive bandwidth

**Configuration**:
```yaml
name: L3_overpowered_direct
config:
  L1_enabled: true
  L2_enabled: true
  L3_enabled: true
  archive_retrieval_prob: 0.1    # ← 100x higher
  boss_enabled: false
execution:
  universes: 8
  ticks: 5000
priority: OPTIONAL
blocking: false
```

**Run only if**: Want to validate low-bandwidth design

---

## 4. Minimal Configuration

### 4.1 Ticks Specification

| Condition | Previous | Minimal | Rationale |
|-----------|----------|---------|-----------|
| All | 1000 | **5000** | Better statistical power |

### 4.2 Universes Specification

| Condition | Universes | Seeds | Total Runs |
|-----------|-----------|-------|------------|
| L3_shuffled | 8 | 3 | 24 |
| no_L2 | 8 | 3 | 24 |
| **Total** | - | - | **48** |

### 4.3 Why 5000 Ticks?

```
Previous: 1000 ticks
Problem:  Low statistical power, high variance

Minimal:  5000 ticks
Benefit:  
  - 5x more data points
  - Lower standard error
  - Better effect detection
  - Can detect smaller differences

Trade-off: 5x compute time
Acceptable: Runs are parallelizable
```

---

## 5. CSV Output Requirements

### 5.1 Required Columns (15 total)

```csv
tick,generation,population,births,deaths,average_energy,dna_variance,
lineage_count,cooperation_rate,mean_cluster_size,multi_cell_boss_success_rate,
energy_transfer_count,signal_synchrony,mutation_count,nonzero_mutation_generations,
elite_lineage_survival,adaptation_gain,extinction_events,cdi,
archive_sample_attempts,archive_sample_successes,archive_influenced_births,
lineage_diversity,top1_lineage_share,strategy_entropy,collapse_event_count
```

### 5.2 New Fields (7 added)

| Field | Type | Source | Priority |
|-------|------|--------|----------|
| archive_sample_attempts | int | CDI counter | HIGH |
| archive_sample_successes | int | CDI counter | HIGH |
| archive_influenced_births | int | Birth tracking | HIGH |
| lineage_diversity | float | 1/Σ(p²) | HIGH |
| top1_lineage_share | float | max/size | MEDIUM |
| strategy_entropy | float | Shannon | LOW |
| collapse_event_count | int | Threshold | LOW |

### 5.3 Implementation Notes

**Bio-World changes required**:
```python
# In CDI class
self.sample_attempts = 0
self.sample_successes = 0

def read_archive(self, lineage_id):
    self.sample_attempts += 1
    result = self._read(lineage_id)
    if result is not None:
        self.sample_successes += 1
    return result

# In export_csv()
row['archive_sample_attempts'] = self.cdi.sample_attempts
row['archive_sample_successes'] = self.cdi.sample_successes
row['lineage_diversity'] = 1.0 / sum((count/total)**2 for count in lineage_counts)
row['top1_lineage_share'] = max(lineage_counts) / total
```

---

## 6. Execution Plan

### 6.1 Phase 1: Setup (Day 1)

```
Hour 0-2:
  [ ] Update Bio-World CSV export (add 7 fields)
  [ ] Implement archive_shuffle flag
  [ ] Test on 1 universe
  
Hour 2-4:
  [ ] Deploy to compute cluster
  [ ] Verify parallel execution setup
```

### 6.2 Phase 2: L3_shuffled Run (Day 1-2)

```
Hour 4-8:
  [ ] Run 8 universes × 5000 ticks
  [ ] Monitor for crashes
  [ ] Validate CSV outputs
  
Hour 8-12:
  [ ] Continue runs
  [ ] Generate summary statistics
```

### 6.3 Phase 3: no_L2 Run (Day 2)

```
Hour 12-16:
  [ ] Run 8 universes × 5000 ticks
  [ ] Monitor for crashes
  [ ] Validate CSV outputs
  
Hour 16-20:
  [ ] Continue runs
  [ ] Generate summary statistics
```

### 6.4 Phase 4: Validation (Day 3)

```
Hour 20-22:
  [ ] Compare L3_real vs L3_shuffled
  [ ] Compare baseline vs no_L2
  [ ] Validate falsification rules
  
Hour 22-24:
  [ ] Update triage documents
  [ ] Make GO/NO-GO decision
```

---

## 7. Resource Requirements

### 7.1 Compute

| Resource | Amount |
|----------|--------|
| Total ticks | 80,000 (2 conditions × 8 universes × 5000 ticks) |
| Parallel universes | 8 per condition |
| Estimated wall time | 6-8 hours per condition |
| Total wall time | 12-16 hours (sequential) or 6-8 hours (parallel) |

### 7.2 Storage

| Output | Size |
|--------|------|
| CSV files | ~4 MB per condition |
| Logs | ~1 MB per condition |
| Summary | ~100 KB |
| **Total** | **~10 MB** |

### 7.3 Personnel

| Role | Hours |
|------|-------|
| Bio-World dev | 4 hours (CSV update + shuffle) |
| Execution monitoring | 2 hours (intermittent) |
| Analysis | 2 hours |
| **Total** | **8 hours** |

---

## 8. Success Criteria

### 8.1 Required Outcomes

| Criterion | Measure | Threshold |
|-----------|---------|-----------|
| L3_shuffled completes | Runs finished | 8/8 universes |
| no_L2 completes | Runs finished | 8/8 universes |
| CSV fields present | Columns | 15/15 |
| R1 testable | Comparison possible | Yes |
| R3 testable | Comparison possible | Yes |

### 8.2 Decision Outcomes

| Scenario | L3_real vs shuffled | Decision |
|----------|---------------------|----------|
| A | L3_real > L3_shuffled | ✅ GO |
| B | L3_real ≈ L3_shuffled | ❌ NO-GO |
| C | L3_real < L3_shuffled | ❌ NO-GO |

| Scenario | baseline vs no_L2 | Decision Impact |
|----------|-------------------|-----------------|
| D | baseline > no_L2 | Strengthens evidence |
| E | baseline ≈ no_L2 | Weakens L2 claim |
| F | baseline < no_L2 | Contradicts hypothesis |

---

## 9. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Runs crash | Low | High | Test on 1 universe first |
| No effect detected | Medium | High | Extend to 10000 ticks |
| Shuffle implementation bug | Low | High | Code review + test |
| Compute unavailable | Low | Medium | Queue with priority |

---

## 10. Deliverables

### 10.1 From Bio-World

| Deliverable | Format | Due |
|-------------|--------|-----|
| L3_shuffled CSVs | 8 files | Day 2 |
| no_L2 CSVs | 8 files | Day 3 |
| Updated CSV schema | Documentation | Day 1 |

### 10.2 From Atlas-HEC

| Deliverable | Format | Due |
|-------------|--------|-----|
| Updated triage report | Markdown | Day 3 |
| Final decision | GO/NO-GO | Day 3 |

---

**Specification Status**: FINAL  
**Estimated Duration**: 2-3 days  
**Estimated Cost**: 8 person-hours + compute  
**Expected Outcome**: Resolution of HOLD status
