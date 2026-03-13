# Phase 3 Result Review Protocol

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Role**: Execution Auditor + Falsification Analyst

---

## Overview

This protocol defines how to review Codex Phase 3 outputs. Focus on:
1. **Runnable check**: Do the 7 sentinel conditions actually run?
2. **Data reality check**: Are the required_now fields real values or placeholders?
3. **First comparison**: Can we see differences between conditions?

**Not in scope**: Long runs, high statistics, definitive conclusions.

---

## 1. Per-Run CSV Review Checklist

For each of the 120 runs (5 conditions × 3 seeds × 8 universes):

### 1.1 File Existence

```bash
for condition in baseline_full no_L2 L3_off L3_real_p001 L3_shuffled_p001; do
  for seed in 1001 1002 1003; do
    for u in 0 1 2 3 4 5 6 7; do
      test -f "outputs/${condition}/seed_${seed}/u${u}/population.csv" || echo "MISSING"
    done
  done
done
```

**Pass**: All 120 files exist  
**Fail**: Any missing file is a NO-GO

### 1.2 Required Columns Check

```bash
head -1 outputs/baseline_full/seed_1001/u0/population.csv | tr ',' '\n' | grep -E '^(archive_sample_attempts|archive_sample_successes|archive_influenced_births|lineage_diversity|top1_lineage_share|strategy_entropy|collapse_event_count)$'
```

**Pass**: All 7 columns present  
**Fail**: Any missing column is a NO-GO

### 1.3 Data Non-Zero Check

```bash
awk -F',' 'NR>1 {
  if($9==0 && $10==0 && $11==0) print "Row " NR ": All archive fields zero"
}' outputs/baseline_full/seed_1001/u0/population.csv
```

**Caution**: Archive fields may be zero initially, but should increase  
**Fail**: All rows have zero archive fields → placeholder data

---

## 2. Required_Now Field Reality Check

### 2.1 Field-by-Field Validation

| Field | Check | Real Data Indicator | Placeholder Indicator |
|-------|-------|---------------------|----------------------|
| archive_sample_attempts | `max > 0` | Increases over time | Always 0 or constant |
| archive_sample_successes | `max > 0` | ~1% of attempts | Always 0 |
| archive_influenced_births | `max > 0` | Small positive values | Always 0 |
| lineage_diversity | `std > 0` | Fluctuates 10-50 | Constant or NaN |
| top1_lineage_share | `range > 0` | Varies 0.1-0.8 | Constant or >1 |
| strategy_entropy | `std > 0` | Varies 0.5-2.0 | Constant or negative |
| collapse_event_count | `max > 0` or all 0 | Some runs have collapses | Random large values |

### 2.2 Automated Reality Check Script

```python
#!/usr/bin/env python3
# check_field_reality.py

import pandas as pd
import sys

def check_field_reality(csv_path):
    df = pd.read_csv(csv_path)
    
    checks = {
        'archive_sample_attempts': lambda x: x.max() > 0,
        'archive_sample_successes': lambda x: x.max() > 0,
        'archive_influenced_births': lambda x: x.max() >= 0,
        'lineage_diversity': lambda x: x.std() > 0.1,
        'top1_lineage_share': lambda x: 0 <= x.min() and x.max() <= 1,
        'strategy_entropy': lambda x: x.std() > 0.01,
        'collapse_event_count': lambda x: x.max() >= 0,
    }
    
    results = {}
    for field, check_fn in checks.items():
        if field not in df.columns:
            results[field] = 'MISSING'
        elif check_fn(df[field]):
            results[field] = 'REAL'
        else:
            results[field] = 'SUSPECT'
    
    return results

if __name__ == '__main__':
    results = check_field_reality(sys.argv[1])
    for field, status in results.items():
        print(f"{field}: {status}")
```

**Pass**: All fields REAL or SUSPECT (acceptable for some)  
**Fail**: Any field MISSING  
**NO-GO**: More than 2 fields SUSPECT

---

## 3. Sentinel Conditions Execution Check

### 3.1 Condition Runnable Verification

| Condition | Verification Command | Expected Output |
|-----------|---------------------|-----------------|
| baseline_full | `./p1_experiment --group CTRL --ticks 100` | Runs without error |
| no_L2 | `./p1_experiment --group P1A --ticks 100` | Runs, produces different output |
| L3_off | `./p1_experiment --group P1C_LOW --ticks 100` | Runs, archive fields = 0 |
| L3_real_p001 | `./p1_experiment --group CTRL --ticks 100` | Baseline (reference) |
| L3_shuffled_p001 | Need new flag | Must exist in code |

### 3.2 Output Differentiation Check

```bash
# Generate MD5 of final population values
for condition in baseline_full no_L2 L3_off L3_real_p001 L3_shuffled_p001; do
  tail -1 outputs/${condition}/seed_1001/u0/population.csv | md5sum
 done | sort | uniq -c
```

**Pass**: At least 3 different hashes (baseline, no_L2, L3_off different)  
**HOLD**: Only 2 different hashes  
**NO-GO**: All same hash

---

## 4. Minimum Falsification Requirements

### 4.1 Must Show Direction

| Comparison | Expected Direction | Pass Threshold |
|------------|-------------------|----------------|
| no_L2 vs baseline | no_L2 lower diversity | Δ > 10% |
| L3_off vs baseline | L3_off different | Δ > 5% |
| L3_shuffled vs L3_real | Similar (±10%) | \|Δ\| < 15% |

### 4.2 Quick Direction Check

```python
import pandas as pd

def quick_direction_check(condition_a, condition_b, metric='lineage_diversity'):
    # Load last generation data
    a_vals = []
    b_vals = []
    
    for seed in [1001, 1002, 1003]:
        for u in range(8):
            a_df = pd.read_csv(f'outputs/{condition_a}/seed_{seed}/u{u}/population.csv')
            b_df = pd.read_csv(f'outputs/{condition_b}/seed_{seed}/u{u}/population.csv')
            a_vals.append(a_df[metric].iloc[-1])
            b_vals.append(b_df[metric].iloc[-1])
    
    a_mean = sum(a_vals) / len(a_vals)
    b_mean = sum(b_vals) / len(b_vals)
    
    return {
        'a_mean': a_mean,
        'b_mean': b_mean,
        'delta_pct': (b_mean - a_mean) / a_mean * 100,
        'direction': 'higher' if b_mean > a_mean else 'lower'
    }
```

---

## 5. Priority Charts (Look First)

### 5.1 Chart 1: Lineage Diversity Trajectory

**File**: `population.csv`  
**X**: generation  
**Y**: lineage_diversity  
**Lines**: 5 conditions overlaid  

**What to see**:
- baseline: stable 20-50
- no_L2: declining or lower
- L3_off: different pattern
- L3_real ≈ L3_shuffled

**Decision**:
- no_L2 clearly lower → GO
- no_L2 ≈ baseline → NO-GO
- Ambiguous → HOLD

### 5.2 Chart 2: Archive Activity Over Time

**File**: `population.csv`  
**X**: generation  
**Y**: archive_sample_attempts  

**What to see**:
- Should increase over time
- Not flat at 0

**Decision**:
- Clear increasing trend → GO
- Flat at 0 → NO-GO
- Sporadic → HOLD

### 5.3 Chart 3: Strategy Entropy Distribution

**File**: `population.csv`  
**Type**: Box plot or violin  
**X**: condition  
**Y**: strategy_entropy (endpoint)  

**What to see**:
- Variation across conditions
- Not all identical

**Decision**:
- Clear differences → GO
- All identical → NO-GO
- Overlapping distributions → HOLD

---

## 6. Review Flowchart

```
Start
  |
  v
All 120 CSVs exist? ----No----> NO-GO
  | Yes
  v
All 7 columns present? ----No----> NO-GO
  | Yes
  v
Fields pass reality check? ----No----> NO-GO
  | Yes
  v
5 conditions runnable? ----No----> NO-GO
  | Yes
  v
Outputs differentiated? ----No----> NO-GO
  | Yes
  v
Direction matches expected? 
  | Yes          | No          | Ambiguous
  v              v             v
 GO          NO-GO          HOLD
```

---

## 7. Documentation Requirements

After review, update:

### 7.1 FIRST_COMPARISON_MATRIX.md
Fill in actual directions observed.

### 7.2 status-sync.json
```json
{
  "phase3_results": {
    "csv_files_generated": 120,
    "conditions_runnable": 5,
    "fields_real": "Y/N",
    "overall_verdict": "GO/HOLD/NO-GO"
  }
}
```

### 7.3 open-questions.md
- Move resolved blockers to closed
- Add new ambiguities discovered

---

## 8. Time Budget

| Task | Max Time |
|------|----------|
| File existence check | 5 min |
| Column check | 5 min |
| Reality check | 15 min |
| Condition runnable | 10 min |
| Chart generation | 20 min |
| Matrix fill | 10 min |
| Verdict | 5 min |
| **Total** | **70 min** |

**If any check fails early**: Stop and report NO-GO immediately.

---

**Next**: Run protocol on Codex outputs, fill FIRST_COMPARISON_MATRIX
