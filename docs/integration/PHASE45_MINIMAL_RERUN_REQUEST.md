# Phase 4.5 Minimal Rerun Request

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Request Type**: Production run with complete field set  
**Estimated Cost**: ~72 runs × 2000 gen = 144k generations

---

## 1. Purpose

**Objective**: Generate missing data to complete Phase 4 triage and enable Phase 5 go/no-go decision.

**Current Blockers**:
1. B1-runnable: 2 of 5 conditions missing (L3_off, L3_shuffled)
2. B2-semantic: 5 of 7 required fields missing
3. B3-evidence: Cannot validate falsification rules R1, R2, R4, R5, R6, R7

---

## 2. Required Conditions

### 2.1 Missing Conditions

| Condition | Runs Needed | Seeds | Universes/Seed | Purpose |
|-----------|-------------|-------|---------------|---------|
| **L3_off** | 24 | 3 | 8 | Verify L3 necessity (R2, R4) |
| **L3_real_p001** | 24 | 3 | 8 | Valid L3 with real archive |
| **L3_shuffled_p001** | 24 | 3 | 8 | Falsification control (R1) |

**Total New Runs**: 72

### 2.2 Optional Conditions

| Condition | Runs | Purpose |
|-----------|------|---------|
| Additional ctrl seeds | +24 | Increase statistical power |

**Total Including Optional**: 96 runs

---

## 3. Required CSV Fields

### 3.1 Current CSV (8 fields)

```csv
tick,population,births,deaths,avg_energy,lineage_count,avg_stress_level,archive_record_count
```

### 3.2 Required CSV (15 fields)

```csv
tick,population,births,deaths,avg_energy,lineage_count,avg_stress_level,archive_record_count,
archive_sample_attempts,archive_sample_successes,archive_influenced_births,lineage_diversity,
top1_lineage_share,strategy_entropy,collapse_event_count
```

### 3.3 New Fields Specification

| Field | Type | Definition | Implementation |
|-------|------|------------|----------------|
| **archive_sample_attempts** | int | CDI attempts to read archive | Count of `read_archive()` calls |
| **archive_sample_successes** | int | Successful archive reads | Count of non-empty returns |
| **archive_influenced_births** | int | Births where strategy from archive | Count with `strategy_from_archive=True` |
| **lineage_diversity** | float | Effective number of lineages | 1/Σ(p_i²) where p_i = lineage_size/total |
| **top1_lineage_share** | float | Fraction of cells in largest lineage | max(lineage_sizes) / population |
| **strategy_entropy** | float | Shannon entropy of strategies | -Σ(p_s × log(p_s)) |
| **collapse_event_count** | int | Discrete collapse events detected | Count of population drops >50% |

---

## 4. Run Configuration

### 4.1 L3_off Condition

```python
{
    "L1_enabled": True,    # Intrinsic mortality ON
    "L2_enabled": True,    # Lineage tracking ON
    "L3_enabled": False,   # Archive/CDI OFF ← Key difference
    "boss_enabled": False,
    "generations": 2000,
    "population_cap": 3000
}
```

**Expected Output**:
- Lower lineage_diversity
- No archive_sample_attempts
- Higher top1_lineage_share
- Lower strategy_entropy

### 4.2 L3_real_p001 Condition

```python
{
    "L1_enabled": True,
    "L2_enabled": True,
    "L3_enabled": True,
    "archive_retrieval_prob": 0.001,  # 0.1% per tick
    "boss_enabled": False,
    "generations": 2000,
    "population_cap": 3000
}
```

**Expected Output**:
- Archive metrics populated
- Higher lineage_diversity than L3_off
- Positive archive_influenced_births

### 4.3 L3_shuffled_p001 Condition

```python
{
    "L1_enabled": True,
    "L2_enabled": True,
    "L3_enabled": True,
    "archive_retrieval_prob": 0.001,
    "archive_shuffle": True,  # ← Key: Shuffle archive entries
    "boss_enabled": False,
    "generations": 2000,
    "population_cap": 3000
}
```

**Expected Output**:
- Similar archive_sample_attempts to L3_real
- Similar archive_sample_successes to L3_real
- **Different** lineage outcomes (falsification test)

---

## 5. Implementation Notes

### 5.1 Bio-World Changes Required

**File**: `bioworld_mvp/core/experiment.py`

```python
# Add to export_csv()
def export_csv(self, path: str):
    # ... existing fields ...
    
    # NEW FIELDS - Required for Phase 4
    data['archive_sample_attempts'] = self.cdi.sample_attempts
    data['archive_sample_successes'] = self.cdi.sample_successes
    data['archive_influenced_births'] = self.count_archive_influenced_births()
    data['lineage_diversity'] = self.calculate_lineage_diversity()
    data['top1_lineage_share'] = self.calculate_top1_lineage_share()
    data['strategy_entropy'] = self.calculate_strategy_entropy()
    data['collapse_event_count'] = self.collapse_events_detected
```

### 5.2 CDI Instrumentation

**File**: `bioworld_mvp/core/cdi.py`

```python
class CDI:
    def __init__(self):
        self.sample_attempts = 0
        self.sample_successes = 0
        
    def read_archive(self, lineage_id: str) -> Optional[Strategy]:
        self.sample_attempts += 1
        result = self._do_read(lineage_id)
        if result is not None:
            self.sample_successes += 1
        return result
```

### 5.3 Lineage Metrics

```python
def calculate_lineage_diversity(self) -> float:
    """Effective number of lineages (inverse Simpson)."""
    counts = np.array([len(cells) for cells in self.lineages.values()])
    total = counts.sum()
    if total == 0:
        return 0.0
    proportions = counts / total
    return 1.0 / np.sum(proportions ** 2)

def calculate_top1_lineage_share(self) -> float:
    """Fraction of cells in largest lineage."""
    counts = [len(cells) for cells in self.lineages.values()]
    return max(counts) / sum(counts) if counts else 0.0
```

---

## 6. Run Execution Plan

### 6.1 Execution Order

```
Phase 1: Bio-World code update (add 7 fields)
    ↓
Phase 2: L3_off runs (24 runs, ~2 hours)
    ↓
Phase 3: L3_real_p001 runs (24 runs, ~2 hours)
    ↓
Phase 4: L3_shuffled_p001 runs (24 runs, ~2 hours)
    ↓
Phase 5: Data validation and CSV check
    ↓
Phase 6: Triage re-analysis
```

### 6.2 Validation Checkpoints

| Checkpoint | Test | Pass Criteria |
|------------|------|---------------|
| C1 | CSV fields | All 15 columns present |
| C2 | L3_off | archive_sample_attempts = 0 |
| C3 | L3_real | archive_sample_attempts > 0 |
| C4 | Data range | All values in reasonable bounds |
| C5 | Completeness | All 72 runs completed |

---

## 7. Success Criteria

### 7.1 Minimum Success

- [ ] All 72 runs complete without errors
- [ ] All 15 CSV fields present
- [ ] L3_shuffled data available (critical for R1)

### 7.2 Ideal Success

- [ ] Clear difference between L3_real and L3_shuffled
- [ ] L3_off shows measurable degradation
- [ ] Archive metrics correlate with lineage diversity

### 7.3 Failure Modes

| Mode | Detection | Response |
|------|-----------|----------|
| Code error | Runs crash | Debug and restart |
| Data missing | CSV incomplete | Re-run missing conditions |
| No effect | All conditions similar | Hypothesis may be invalid |

---

## 8. Post-Run Actions

### 8.1 Triage Re-Analysis

After rerun completes:
1. Fill `PHASE4_TRIAGE_REPORT_FILLED.md` with new data
2. Complete `PHASE4_COMPARISON_DECISION_TABLE_FILLED.md`
3. Re-evaluate falsification rules R1-R7

### 8.2 Phase 4.5 Completion

```
Phase 4.5 Checklist:
☐ Minimal rerun executed (72 runs)
☐ All 15 fields populated
☐ Triage report filled with actual data
☐ Comparison decision table completed
☐ Semantic alignment documented
☐ GO/HOLD/NO-GO decision made
```

---

## 9. Cost-Benefit Analysis

### 9.1 Cost

| Resource | Amount |
|----------|--------|
| Compute | ~72 runs × 2000 gen × ~100 cells/gen = ~14M cell-steps |
| Time | ~6 hours wall time (parallel execution) |
| Storage | ~10 MB CSV output |

### 9.2 Benefit

| Outcome | Value |
|---------|-------|
| Validate R1-R7 | Critical for hypothesis |
| Enable Phase 5 | Proceed to optimization |
| Scientific validity | Confirm archive mechanism works |

### 9.3 Risk

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| No effect found | 20% | High (hypothesis fails) | Design robust falsification tests |
| Code bug | 10% | Medium | Validation checkpoints |
| Takes too long | 5% | Low | Parallel execution |

---

## 10. Request Approval

### Request Details

| Field | Value |
|-------|-------|
| Requester | Atlas-HEC Phase 4.5 Lead |
| Priority | CRITICAL - Blocking Phase 5 |
| Deadline | 2026-03-12 (3 days) |
| Dependencies | Bio-World PR #6 (field expansion) |
| Estimated Effort | 6 hours compute + 2 hours dev |

### Approval Signature

```
Approved by: _________________________
Date: _________________________
Notes: _________________________
```

---

**Request Status**: PENDING_APPROVAL  
**Urgency**: HIGH - Blocking all downstream phases  
**Fallback**: If denied, cannot proceed to Phase 5
