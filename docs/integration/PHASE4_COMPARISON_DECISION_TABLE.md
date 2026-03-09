# Phase 4 Comparison Decision Table

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Status**: WAITING_FOR_CODEX_OUTPUT

---

## Fixed Comparison Matrix

**Conditions** (5):
1. baseline_full
2. no_L2
3. L3_off
4. L3_real_p001
5. L3_shuffled_p001

**Metrics** (5):
1. survival_time
2. lineage_diversity
3. top1_lineage_share
4. strategy_entropy
5. collapse_event_count

---

## Metric 1: survival_time

| Condition A | Condition B | Observed Trend | Confidence | Interpretation | Decision Impact |
|-------------|-------------|----------------|------------|----------------|-----------------|
| baseline_full | no_L2 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| baseline_full | L3_off | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| L3_real_p001 | L3_shuffled_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | **CRITICAL** |
| baseline_full | L3_real_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |

**Key Question**: Does no_L2 show shorter survival?

**Expected**: no_L2 < baseline (lower is worse)

**Decision Relevance**: 
- If no_L2 ≈ baseline → R2 not validated → NO-GO risk
- If no_L2 clearly < baseline → R2 validated → supports hypothesis

---

## Metric 2: lineage_diversity

| Condition A | Condition B | Observed Trend | Confidence | Interpretation | Decision Impact |
|-------------|-------------|----------------|------------|----------------|-----------------|
| baseline_full | no_L2 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | **CRITICAL** |
| baseline_full | L3_off | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| L3_real_p001 | L3_shuffled_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | **CRITICAL** |
| baseline_full | L3_real_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |

**Key Question**: Does no_L2 show lower diversity?

**Expected**: no_L2 < baseline (lower means less diverse)

**Decision Relevance**:
- If no_L2 << baseline → Strong evidence L2 matters
- If no_L2 ≈ baseline → R2 potentially falsified → NO-GO
- If L3_real ≈ L3_shuffled → R1 potentially falsified → NO-GO

**Falsification Threshold**: Cohen's d < 0.3 AND p > 0.05

---

## Metric 3: top1_lineage_share

| Condition A | Condition B | Observed Trend | Confidence | Interpretation | Decision Impact |
|-------------|-------------|----------------|------------|----------------|-----------------|
| baseline_full | no_L2 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| baseline_full | L3_off | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| L3_real_p001 | L3_shuffled_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| baseline_full | L3_real_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |

**Key Question**: Does no_L2 show higher monopoly?

**Expected**: no_L2 > baseline (higher means more concentrated)

**Decision Relevance**:
- If no_L2 >> baseline → L2 prevents monopoly → supports hypothesis
- If top1 > 0.5 in no_L2 → Convergence warning → interesting finding

---

## Metric 4: strategy_entropy

| Condition A | Condition B | Observed Trend | Confidence | Interpretation | Decision Impact |
|-------------|-------------|----------------|------------|----------------|-----------------|
| baseline_full | no_L2 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| baseline_full | L3_off | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| L3_real_p001 | L3_shuffled_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| baseline_full | L3_real_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |

**Key Question**: Does no_L2 show lower entropy (convergence)?

**Expected**: no_L2 < baseline (lower means less exploration)

**Decision Relevance**:
- If no_L2 < baseline → L2 enables strategy diversity → supports hypothesis
- If strategy_entropy → 0 in no_L2 → Complete convergence → interesting

---

## Metric 5: collapse_event_count

| Condition A | Condition B | Observed Trend | Confidence | Interpretation | Decision Impact |
|-------------|-------------|----------------|------------|----------------|-----------------|
| baseline_full | no_L2 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| baseline_full | L3_off | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| L3_real_p001 | L3_shuffled_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |
| baseline_full | L3_real_p001 | [FILL] | ☐ High ☐ Med ☐ Low | [FILL] | [FILL] |

**Key Question**: Does no_L2 show more collapses?

**Expected**: no_L2 > baseline (higher means more unstable)

**Decision Relevance**:
- If no_L2 >> baseline → L2 prevents collapse → supports hypothesis
- If collapse count unexpectedly low → re-examine mechanism

---

## Critical Comparison Summary

### Comparison 1: baseline_full vs no_L2

**Hypothesis**: L2 (lineage memory) is necessary for diversity and stability

| Metric | Expected Direction | Observed | Match? | Cohen's d | p-value |
|--------|-------------------|----------|--------|-----------|---------|
| survival_time | no_L2 lower | [FILL] | ☐ | [FILL] | [FILL] |
| lineage_diversity | no_L2 lower | [FILL] | ☐ | [FILL] | [FILL] |
| top1_lineage_share | no_L2 higher | [FILL] | ☐ | [FILL] | [FILL] |
| strategy_entropy | no_L2 lower | [FILL] | ☐ | [FILL] | [FILL] |
| collapse_event_count | no_L2 higher | [FILL] | ☐ | [FILL] | [FILL] |

**Overall Match**: [FILL]/5 metrics

**Interpretation**:
- ☐ Strong support (4-5 matches, d > 0.5)
- ☐ Partial support (2-3 matches, d > 0.3)
- ☐ No support (0-1 matches or d < 0.2) → R2 falsified

---

### Comparison 2: L3_real_p001 vs L3_shuffled_p001

**Hypothesis**: L3 content (real vs shuffled) should NOT matter (or matter little)

| Metric | Expected | Observed | Match? | Cohen's d | p-value |
|--------|----------|----------|--------|-----------|---------|
| survival_time | Similar | [FILL] | ☐ | [FILL] | [FILL] |
| lineage_diversity | Similar | [FILL] | ☐ | [FILL] | [FILL] |
| top1_lineage_share | Similar | [FILL] | ☐ | [FILL] | [FILL] |
| strategy_entropy | Similar | [FILL] | ☐ | [FILL] | [FILL] |
| collapse_event_count | Similar | [FILL] | ☐ | [FILL] | [FILL] |

**Similarity Threshold**: |d| < 0.2 OR p > 0.1

**Interpretation**:
- ☐ Content irrelevant (all similar) → R1 not falsified
- ☐ Content matters (some different) → Interesting finding
- ☐ Strong difference (d > 0.5) → R1 potentially falsified

---

## Decision Matrix

### If baseline vs no_L2 shows CLEAR difference AND L3_real ≈ L3_shuffled

| Condition | Decision |
|-----------|----------|
| no_L2 < baseline (expected) | GO |
| no_L2 ≈ baseline | NO-GO (R2 falsified) |
| no_L2 > baseline (opposite) | NO-GO (unexpected) |

### If baseline vs no_L2 shows WEAK/AMBIGUOUS difference

**Check seed variance**: If within > 2× between → HOLD for more seeds

### If L3_real vs L3_shuffled shows STRONG difference

| Condition | Decision |
|-----------|----------|
| Effect in unexpected direction | Interesting, proceed with caution |
| Effect contradicts theory | HOLD for investigation |

---

## Quick Reference: How to Fill

### Step 1: Compute Means

```python
import pandas as pd

def get_mean(condition, metric):
    values = []
    for seed in [1001, 1002, 1003]:
        for u in range(8):
            df = pd.read_csv(f'outputs/{condition}/seed_{seed}/u{u}/population.csv')
            values.append(df[metric].iloc[-1])  # Endpoint
    return sum(values) / len(values)
```

### Step 2: Compute Effect Size

```python
from scipy import stats

def cohens_d(a, b):
    na, nb = len(a), len(b)
    pooled_std = (((na-1)*a.var() + (nb-1)*b.var()) / (na+nb-2)) ** 0.5
    return (a.mean() - b.mean()) / pooled_std
```

### Step 3: Statistical Test

```python
t_stat, p_value = stats.ttest_ind(a_values, b_values)
```

---

## Data Quality Flags

For each comparison, note:

| Issue | Present? | Severity | Action |
|-------|----------|----------|--------|
| Missing data points | ☐ | ☐ Low ☐ High | [FILL] |
| Outliers affecting mean | ☐ | ☐ Low ☐ High | [FILL] |
| High variance within condition | ☐ | ☐ Low ☐ High | [FILL] |
| Non-normal distribution | ☐ | ☐ Low ☐ High | [FILL] |

---

**Status**: AWAITING_DATA  
**Last Updated**: 2026-03-09
