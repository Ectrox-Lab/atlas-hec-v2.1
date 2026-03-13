# Ambiguity Handling Guide

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Purpose**: Define when results are ambiguous and how to proceed

---

## Principle

> **Ambiguity is not a conclusion. It is a signal to gather more data or refine the question.**

Do not use narrative to resolve ambiguity. Use explicit criteria.

---

## Ambiguity Type 1: High Seed Variance

### Scenario
baseline and no_L2 show different means, but within-seed variance is larger than between-condition difference.

### Detection
```python
def check_seed_variance():
    baseline_by_seed = [values_for_seed(s) for s in [1001, 1002, 1003]]
    no_l2_by_seed = [values_for_seed(s) for s in [1001, 1002, 1003]]
    
    within_variance = np.mean([np.var(s) for s in baseline_by_seed + no_l2_by_seed])
    between_variance = np.var([np.mean(s) for s in baseline_by_seed + no_l2_by_seed])
    
    return within_variance > between_variance  # Ambiguous if True
```

### Criteria
| Situation | Action |
|-----------|--------|
| Within > 2× Between | AMBIGUOUS |
| Within ≈ Between | WEAK SIGNAL (proceed with caution) |
| Within < 0.5× Between | CLEAR SIGNAL |

### Resolution
1. **Do not conclude** no_L2 has no effect
2. **Do conclude** more replicates needed
3. **Next step**: Run 5 seeds instead of 3

---

## Ambiguity Type 2: Weak Effect Size

### Scenario
L3_real and L3_shuffled differ, but Cohen's d < 0.3 (small effect).

### Detection
```python
effect_size = cohens_d(l3_real_values, l3_shuffled_values)
```

### Criteria
| d | Interpretation | Action |
|---|----------------|--------|
| < 0.2 | Negligible | May be noise, extend runs |
| 0.2-0.5 | Small | Real but weak, acceptable |
| 0.5-0.8 | Medium | Clear signal |
| > 0.8 | Large | Strong signal |

### Special Case: L3_real vs L3_shuffled
For this comparison specifically:
- **Expected**: d < 0.2 (no difference)
- **If d > 0.3**: Content matters (interesting!)
- **If 0.2 < d < 0.3**: AMBIGUOUS - need more data

---

## Ambiguity Type 3: Direction Inversion

### Scenario
diversity decreases but survival increases (or vice versa).

### Example
no_L2 shows:
- lineage_diversity: ↓ (lower than baseline)
- survival_time: ↑ (higher than baseline)

### Interpretation
| Diversity | Survival | Interpretation |
|-----------|----------|----------------|
| ↓ | ↓ | Clear: no_L2 harmful |
| ↓ | ↑ | AMBIGUOUS: trade-off? |
| ↑ | ↓ | AMBIGUOUS: different harm? |
| ↑ | ↑ | Clear: no_L2 beneficial |

### Resolution
1. **Do not average across metrics**
2. **Report separately**: "no_L2 reduces diversity but increases survival"
3. **Check**: Are we measuring the right things?
4. **Next step**: Add more metrics (cooperation rate, energy efficiency)

---

## Ambiguity Type 4: Semantic Mismatch

### Scenario
Field exists and varies, but meaning differs from contract.

### Examples

**Example 1: lineage_diversity**
- Contract: Count of currently alive unique lineages
- Implementation: Count of all lineages ever existed
- Result: Higher values, trends differ

**Example 2: collapse_event_count**
- Contract: Rolling window (last 100 gens)
- Implementation: Cumulative total
- Result: Always increasing vs. variable

### Detection
```python
def check_semantic_match(df, field):
    # lineage_diversity should be <= population
    if field == 'lineage_diversity':
        if (df[field] > df['population'] * 1.5).any():
            return "SEMANTIC_MISMATCH: diversity >> population"
    
    # collapse_event_count should not always increase if rolling
    if field == 'collapse_event_count':
        decreases = (df[field].diff() < 0).sum()
        if decreases == 0 and len(df) > 200:
            return "SEMANTIC_MISMATCH: always increasing (cumulative?)"
    
    return "OK"
```

### Resolution
1. **Do not use field until clarified**
2. **Report mismatch** in open-questions.md (semantic section)
3. **Request clarification** from implementation team
4. **Use alternative metric** if available

---

## Ambiguity Type 5: Partial Data

### Scenario
Some runs completed, others failed or missing.

### Criteria
| Completion Rate | Action |
|-----------------|--------|
| 100% (120/120) | Proceed normally |
| 90-99% (108-119) | Proceed with note |
| 75-89% (90-107) | AMBIGUOUS - analyze completed only |
| < 75% (<90) | NO-GO - insufficient data |

### Resolution for 75-89%
```python
completed_conditions = count_completed_per_condition()
if any(c < 20 for c in completed_conditions):  # Need at least 20 per condition
    return "NO-GO: insufficient data for condition"
```

---

## Ambiguity Type 6: Outlier Sensitivity

### Scenario
Results depend heavily on single outlier run.

### Detection
```python
def check_outlier_sensitivity(values):
    mean_with = np.mean(values)
    mean_without_max = np.mean(values[values != values.max()])
    
    return abs(mean_with - mean_without_max) / mean_with > 0.2  # 20% change
```

### Resolution
1. **Report with and without outlier**
2. **Investigate outlier**: Did it actually collapse?
3. **If real collapse**: Include it (that's the signal!)
4. **If data error**: Exclude and note

---

## Ambiguity Decision Matrix

| Type | Detection | Default Action | Resolution |
|------|-----------|----------------|------------|
| High seed variance | Within > Between | Extend to 5 seeds | More replicates |
| Weak effect size | d < 0.2 | Extend runs | Longer generations |
| Direction inversion | Opposite trends | Report separately | Add metrics |
| Semantic mismatch | Implausible values | Stop using field | Clarify definition |
| Partial data | <90% complete | Analyze partial | Note limitations |
| Outlier sensitivity | 20% change without | Report both ways | Investigate outlier |

---

## Reporting Ambiguity

### In FIRST_COMPARISON_MATRIX.md

```markdown
| Condition A | Condition B | Expected | Actual | Status | Notes |
|-------------|-------------|----------|--------|--------|-------|
| baseline | no_L2 | Lower | Lower? | **AMBIGUOUS** | High seed variance (within=2.3×between) |
```

### In Status Report

```yaml
ambiguities_detected:
  - type: "high_seed_variance"
    metric: "lineage_diversity"
    comparison: "baseline_vs_no_L2"
    action: "extend_to_5_seeds"
    blocker: false
```

### In open-questions.md

Add to "Semantic Mismatch" section if definition issue, or create new ambiguity tracker.

---

## Go/Hold/No-Go with Ambiguity

### GO Criteria (despite ambiguity)
- Main falsification condition clear (L3_real vs L3_shuffled)
- No_L2 shows expected direction even if noisy
- Ambiguity is in secondary metrics only

### HOLD Criteria
- Primary comparison (no_L2 vs baseline) ambiguous
- Multiple types of ambiguity present
- Semantic mismatch detected

### NO-GO Criteria
- Ambiguity plus missing data (<75%)
- Semantic mismatch in primary metric
- Direction inversion in falsification critical comparison

---

## Quick Reference: Is It Ambiguous?

```
Is there a clear difference between conditions?
├── YES → Is the direction as expected?
│         ├── YES → GO
│         └── NO  → Check if falsification (might be OK)
└── NO  → Is variance high?
          ├── YES → AMBIGUOUS (extend runs/seeds)
          └── NO  → NO EFFECT (falsification candidate)
```

---

**Remember**: When in doubt, run more data. Do not paper over ambiguity with narrative.
