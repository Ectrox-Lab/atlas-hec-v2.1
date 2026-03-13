# Phase 4 Comparison Decision Table - ACTUAL DATA FILL

**Version**: v0.1.0-ACTUAL  
**Date**: 2026-03-09  
**Status**: INCOMPLETE - Missing Critical Conditions

---

## 1. Condition Availability Matrix

| Condition | Runs Found | Status | Available for Analysis |
|-----------|-----------|--------|---------------------|
| **baseline_full** | 40 | [Verified] | ☑ Yes |
| **no_L2** | 24 | [Verified] | ☑ Yes |
| **L3_off** | 0 | [Verified] | ☗ No |
| **L3_real_p001** | 0 | [Verified] | ☗ No |
| **L3_shuffled_p001** | 0 | [Verified] | ☗ No |

**Legend**: ☑ Available | ☗ Missing | ⚠ Partial

---

## 2. Metrics Availability by Condition

### 2.1 Available Metrics (from CSV)

| Metric | baseline_full | no_L2 | L3_off | L3_real | L3_shuffled |
|--------|--------------|-------|--------|---------|-------------|
| population | ☑ [Verified] | ☑ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| lineage_count | ☑ [Verified] | ☑ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| archive_record_count | ☑ [Verified] | ☑ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |

### 2.2 Missing Metrics (from CSV)

| Metric | baseline_full | no_L2 | L3_off | L3_real | L3_shuffled |
|--------|--------------|-------|--------|---------|-------------|
| archive_sample_attempts | ☗ [Verified] | ☗ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| archive_sample_successes | ☗ [Verified] | ☗ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| archive_influenced_births | ☗ [Verified] | ☗ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| lineage_diversity | ☗ [Verified] | ☗ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| top1_lineage_share | ☗ [Verified] | ☗ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| strategy_entropy | ☗ [Verified] | ☗ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |
| collapse_event_count | ☗ [Verified] | ☗ [Verified] | ☗ N/A | ☗ N/A | ☗ N/A |

---

## 3. Comparison Matrix - Partially Filled

### 3.1 baseline_full vs no_L2

**Status**: ☑ PARTIAL COMPARISON POSSIBLE

| Metric | baseline_full (mean ± std) | no_L2 (mean ± std) | Delta % | Expected | Actual | Confidence |
|--------|---------------------------|-------------------|---------|----------|--------|------------|
| **survival_time** (generations) | 2100 ± 0 | 1500 ± 0 | -28.6% | Similar | Lower | [Inference] |
| **lineage_count** | 13.2 ± 4.2 | 13.2 ± 3.4 | +0.2% | Lower | Similar | [Verified] |
| **archive_record_count** | 24.7 ± ? | 23.8 ± ? | -3.6% | ? | Similar | [Inference] |
| **lineage_diversity** | N/A | N/A | N/A | Lower | N/A | ☗ CANNOT |
| **top1_lineage_share** | N/A | N/A | N/A | Higher | N/A | ☗ CANNOT |
| **strategy_entropy** | N/A | N/A | N/A | Lower | N/A | ☗ CANNOT |
| **collapse_event_count** | N/A | N/A | N/A | Higher | N/A | ☗ CANNOT |

**Interpretation**: 
- [Inference] Only 1 of 7 metrics comparable (lineage_count)
- [Verified] lineage_count shows NO significant difference (+0.2%)
- [Ambiguous] May indicate field mismatch or weak L2 effect

**Decision Impact**: ☐ Accept degradation evidence  
☐ Reject degradation evidence  
☑ **INSUFFICIENT DATA TO DECIDE**

---

### 3.2 baseline_full vs L3_off

**Status**: ☗ COMPARISON IMPOSSIBLE - L3_off data missing

| Metric | Expected | Actual | Pass/Fail/Ambiguous |
|--------|----------|--------|---------------------|
| All | L3_off lower | N/A | ☗ CANNOT VERIFY |

---

### 3.3 L3_real_p001 vs L3_shuffled_p001

**Status**: ☗ COMPARISON IMPOSSIBLE - Both conditions missing

| Metric | Expected | Actual | Pass/Fail/Ambiguous |
|--------|----------|--------|---------------------|
| All | Real > Shuffled | N/A | ☗ CANNOT VERIFY |

**Critical Falsification Rule**: R1 (L3 content irrelevance) **CANNOT BE VALIDATED**

---

## 4. Falsification Rule Validation Status

| Rule | Description | Test | Status | Evidence |
|------|-------------|------|--------|----------|
| R1 | L3 content irrelevant | Real vs Shuffled | ☗ BLOCKED | No data for either condition |
| R2 | L3 should improve over off | Real vs Off | ☗ BLOCKED | No L3_off data |
| R3 | L2 degeneration | No L2 vs Baseline | ⚠ UNCLEAR | lineage_count similar, not lower |
| R4 | Birth rate tied to L3 | Real > Off | ☗ BLOCKED | No L3_off data |
| R5 | Archive diversity vs collapse | Correlation | ☗ BLOCKED | Missing fields |
| R6 | Lineage diversity decline | Trend | ☗ BLOCKED | Missing fields |
| R7 | Top lineage share increase | Trend | ☗ BLOCKED | Missing fields |

**Legend**: ☑ Validated | ⚠ Partial | ☗ Blocked

---

## 5. Actual Data Summary

### 5.1 Quantitative Summary

```
Total Runs Analyzed: 88 (baseline: 40, no_L2: 24, P1B: 24, P1C: 24)
Total Generations: ~173,000 (88 runs × avg 1500-2100 gen)
Data Points: ~2.2M (ticks across all runs)

Completeness Score: 2/7 fields × 2/5 conditions = 11% complete
```

### 5.2 Key Observations

**Observation 1**: Lineage counts stable across conditions
```
CTRL:  13.2 ± 4.2 lineages
P1A:   13.2 ± 3.4 lineages (no significant change)
P1B:   11.8 ± 3.1 lineages (slightly lower)
P1C:   26.6 ± 15.1 lineages (much higher - boss pressure effect)
```

**Observation 2**: Boss pressure (P1C) shows clearest effect
- Lineage count: +102% vs baseline
- Highest variance (15.1 std)
- Suggests pressure increases diversity

**Observation 3**: Missing archive behavior metrics
- Cannot evaluate CDI effectiveness
- Cannot validate probe behavior

---

## 6. Decision Framework

### 6.1 Available Evidence

| Evidence Type | Available? | Finding |
|--------------|------------|---------|
| Population dynamics | Yes | Stable at ~3000 |
| Lineage count trends | Partial | No clear degradation pattern |
| Archive engagement | No | Missing required fields |
| L3 effect | No | Missing L3 conditions |
| Shuffled control | No | Missing entirely |

### 6.2 Missing Evidence

**Critical for GO decision**:
1. L3_off runs (24 needed)
2. L3_real_p001 runs (24 needed)
3. L3_shuffled_p001 runs (24 needed)
4. 5 archive-related fields

**Nice to have**:
1. More seeds per condition (currently 3)
2. More universes per seed (currently 8)

---

## 7. Comparison Decision Summary

### Matrix Summary

| Comparison | Evidence Quality | Conclusion | Decision Impact |
|------------|-----------------|------------|-----------------|
| baseline vs no_L2 | LOW | Unclear | No impact |
| baseline vs L3_off | NONE | Cannot compare | Blocking |
| L3_real vs L3_shuffled | NONE | Cannot compare | Blocking |

### Overall Status

**TRIAGE CLASSIFICATION**: ☐ GO ☐ NO-GO ☑ HOLD

**Reason**: 
- 0 of 3 critical comparisons possible
- Only 2 of 7 metrics available
- 2 of 5 conditions completely missing

**Recommended Action**: Execute minimal rerun with complete field set.

---

## 8. Appendix: Raw Statistics

### 8.1 Sample Data (baseline, seed_101, u0)

```
Generations: 2100
Final population: 3000
Lineage count: 10
Archive records: 21
```

### 8.2 Sample Data (no_L2, seed_101, u0)

```
Generations: 1500
Final population: 3000
Lineage count: 14
Archive records: 24
```

### 8.3 Statistical Test (lineage_count)

```
CTRL:  n=40, mean=13.2, std=4.2
P1A:   n=24, mean=13.2, std=3.4

t-test: p = 0.98 (not significant)
Cohen's d = 0.01 (negligible effect)
```

**Conclusion**: No statistically significant difference in lineage_count.

---

**Report Status**: COMPLETE based on actual available data  
**Data Completeness**: 11% (2/7 fields × 2/5 conditions)  
**Recommended Status**: HOLD
