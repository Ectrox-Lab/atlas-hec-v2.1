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

### Real-vs-Shuffled Threshold Formalization

**Primary Metric**: `adaptation_gain` (mean across universes)

**Decision Thresholds**:
| Comparison | Threshold | Decision | Rationale |
|------------|-----------|----------|-----------|
| `real > shuffled + 20%` | δ > 0.20 | ✅ **GO** | Content clearly matters |
| `shuffled - 10% ≤ real ≤ shuffled + 10%` | -0.10 ≤ δ ≤ 0.10 | ❌ **NO-GO** | Content irrelevant (falsified) |
| `real < shuffled - 20%` | δ < -0.20 | ❌ **NO-GO** | Shuffled better (design flaw) |
| `10% < δ < 20%` or `-20% < δ < -10%` | Ambiguous | 🟡 **EXTEND** | Insufficient power, run more universes |

**Effect Size Calculation**:
```
δ = (adaptation_gain(real) - adaptation_gain(shuffled)) / adaptation_gain(shuffled)

Statistical validation:
- Required: p < 0.05 (t-test)
- Required: n ≥ 8 universes per condition
- Required: Cohen's d > 0.5 (medium effect)
```

**Secondary Metrics** (supporting evidence):
| Metric | Expected Direction | Weight |
|--------|-------------------|--------|
| lineage_diversity | real > shuffled | 0.3 |
| CDI | real > shuffled | 0.3 |
| adaptation_gain | real > shuffled | 1.0 (primary) |

**Composite Score**:
```
If primary metric is AMBIGUOUS, use weighted composite:
score = 1.0×δ(adaptation) + 0.3×δ(lineage) + 0.3×δ(cdi)

Decision on composite:
- score > 0.15: GO
- score < -0.05: NO-GO
- else: EXTEND
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


---

## 11. Phase 5 Comparison Matrix & Effect-Size Standards

### 11.1 Phase 5 Comparison Matrix (Minimal Set)

| Comparison | Metric | Effect Size Threshold | p-value | Decision |
|------------|--------|----------------------|---------|----------|
| **L3_real vs L3_shuffled** | adaptation_gain | Cohen's d > 0.5 | < 0.05 | GO if d > 0.5 |
| **baseline vs no_L2** | lineage_diversity | Cohen's d > 0.3 | < 0.05 | Strengthens if d > 0.3 |
| **L3_real vs L3_off** | adaptation_gain | Cohen's d > 2.0 | < 0.001 | Already validated |
| **baseline vs C_HIGH** | adaptation_gain | Cohen's d > 3.0 | < 0.001 | Pressure effect |

### 11.2 Effect-Size Standards

| Effect Size | Cohen's d | Interpretation | Required For |
|-------------|-----------|----------------|--------------|
| Negligible | < 0.2 | Not meaningful | Reject claim |
| Small | 0.2 - 0.5 | Weak evidence | Not sufficient |
| **Medium** | **0.5 - 0.8** | **Clear effect** | **Minimum for GO** |
| Large | 0.8 - 1.2 | Strong evidence | Strong support |
| **Very Large** | **> 2.0** | **Overwhelming** | **Hypothesis proven** |

**Phase 5 Decision Criteria**:
```
Primary comparison (L3_real vs L3_shuffled):
  d > 0.8 + p < 0.01 → STRONG GO
  d > 0.5 + p < 0.05 → GO
  d > 0.3 + p < 0.10 → WEAK GO (with caveats)
  d < 0.2 or p > 0.10 → NO-GO (hypothesis fails)

Secondary comparisons (supporting):
  baseline vs no_L2: d > 0.3 required
  L3_real vs L3_off: d > 2.0 already observed
```

### 11.3 Statistical Power Requirements

| Parameter | Minimum | Target | Notes |
|-----------|---------|--------|-------|
| Universes per condition | 8 | 12 | Current: 8, Extend if ambiguous |
| Ticks per universe | 5000 | 10000 | Current: 5000 |
| Alpha (significance) | 0.05 | 0.01 | Primary comparison |
| Power (1-β) | 0.80 | 0.90 | 80% chance detect medium effect |

---

## 12. Shuffled Equivalence Invariant-Test Spec

### 12.1 Purpose
Test that shuffling archive entries produces a valid control condition without breaking system invariants.

### 12.2 Invariant Tests (Must Pass Before Comparison)

| Invariant | Test | Expected | If Failed |
|-----------|------|----------|-----------|
| **Population Stability** | Final population ∈ [500, 700] | Stable | Discard run, check config |
| **No Crash** | Exit code 0, no exceptions | Clean exit | Debug implementation |
| **Archive Accessibility** | archive_sample_attempts > 0 | CDI functional | Check L3 enabled |
| **Birth Rate Normal** | births/tick ∈ [0.5, 2.0] | Healthy | Check parameters |
| **Mutation Present** | mutation_count > 0 | Evolution active | Check mutation rate |

### 12.3 Equivalence Test (Shuffled vs Real Structure)

**Structural Invariants** (should be identical):
```python
# Archive structure
assert len(archive_shuffled) == len(archive_real)
assert set(archive_shuffled.keys()) == set(archive_real.keys())

# Retrieval rate
assert abs(retrieval_rate_shuffled - retrieval_rate_real) < 0.001

# Cell lifecycle
assert abs(birth_rate_shuffled - birth_rate_real) < 0.1
assert abs(death_rate_shuffled - death_rate_real) < 0.1
```

**Content Difference** (should differ):
```python
# Strategy values shuffled
assert hash(archive_shuffled) != hash(archive_real)
assert correlation(ordered_strategies, shuffled_strategies) < 0.1
```

### 12.4 Acceptance Criteria for Shuffled Condition

| Criterion | Threshold | Action if Failed |
|-----------|-----------|------------------|
| Passes all invariants | 100% | Re-run with fixed config |
| Structural equivalence | δ < 0.05 | Validate implementation |
| Content difference | corr < 0.1 | Verify shuffle algorithm |
| Valid for comparison | All above | Include in analysis |

### 12.5 Invariant Violation Response

| Violation Type | Response | Retry? |
|----------------|----------|--------|
| Population crash | Check boss pressure, L1 settings | Yes |
| No archive access | Check L3_enabled, retrieval_prob | Yes |
| Exit code error | Debug traceback | Yes |
| Structural divergence | Check shuffle implementation | Yes |
| Content not shuffled | Fix shuffle algorithm | Yes |

---

## 13. Final Decision Matrix (Post-Rerun)

```
After L3_shuffled and no_L2 complete:

Step 1: Validate invariants
  └─ All pass? → Continue
  └─ Any fail? → Re-run failed universes

Step 2: Calculate effect sizes
  └─ L3_real vs L3_shuffled: Cohen's d = ?
  └─ baseline vs no_L2: Cohen's d = ?

Step 3: Apply thresholds
  ├─ d > 0.5, p < 0.05 → GO_TO_PHASE5
  ├─ d > 0.3, p < 0.10 → GO_WITH_CAVEATS
  ├─ d < 0.2 or p > 0.10 → NO_GO
  └─ Ambiguous → EXTEND (more universes)

Step 4: Final classification
  ├─ STRONG GO: d > 0.8 + supporting evidence
  ├─ GO: d > 0.5 + R3 validated
  ├─ WEAK GO: d > 0.3 + partial R3
  └─ NO_GO: d < 0.2 or equivalence demonstrated
```

---

**Specification Version**: 1.1-FINAL  
**Includes**: Threshold formalization, Phase 5 standards, Invariant tests  
**Updated**: 2026-03-09
