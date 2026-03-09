# GO / NO-GO / HOLD Rules - Phase 3

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Purpose**: Minimal decision rules for Phase 3 execution

---

## Decision Categories

| Category | Meaning | Next Action |
|----------|---------|-------------|
| **GO** | Continue to next phase | Proceed to longer runs / integration |
| **HOLD** | Need more data or clarification | Extend runs / resolve ambiguity |
| **NO-GO** | Critical issue found | Stop and fix before continuing |

---

## GO Rules

### G1: All Conditions Runnable

**Rule**: All 5 sentinel conditions execute without error.

**Check**:
```bash
for condition in baseline_full no_L2 L3_off L3_real_p001 L3_shuffled_p001; do
  timeout 60 ./p1_experiment --group "$condition" --ticks 100 --output-dir test_${condition}
  if [ $? -ne 0 ]; then echo "NO-GO: $condition failed"; exit 1; fi
done
echo "GO: All conditions runnable"
```

### G2: Required Fields Present

**Rule**: All 7 required_now fields exist in CSV.

**Check**:
```bash
head -1 population.csv | grep -q "archive_sample_attempts" || exit 1
head -1 population.csv | grep -q "lineage_diversity" || exit 1
# ... (all 7 fields)
echo "GO: All fields present"
```

### G3: Fields Have Real Values

**Rule**: No field is placeholder (all zeros or constant).

**Check**:
```python
def check_real_values(df):
    for field in REQUIRED_FIELDS:
        if df[field].max() == 0:
            return "NO-GO: {field} all zeros"
        if df[field].std() < 0.001:
            return "HOLD: {field} constant"
    return "GO: All fields have variation"
```

### G4: L3 Content Effect Detectable

**Rule**: L3_real_p001 and L3_shuffled_p001 show measurable differences OR clear similarity.

**Check**:
```python
real = load_data('L3_real_p001')
shuffled = load_data('L3_shuffled_p001')

d = cohens_d(real['lineage_diversity'], shuffled['lineage_diversity'])

if abs(d) < 0.2:
    return "GO: L3 content effect negligible (as expected)"
elif abs(d) > 0.5:
    return "GO: L3 content has significant effect (interesting!)"
else:
    return "HOLD: Effect size ambiguous"
```

### G5: no_L2 Shows Direction

**Rule**: no_L2 differs from baseline in expected direction (even if weak).

**Check**:
```python
baseline = load_data('baseline_full')
no_l2 = load_data('no_L2')

baseline_div = baseline['lineage_diversity'].mean()
no_l2_div = no_l2['lineage_diversity'].mean()

if no_l2_div < baseline_div * 0.9:  # At least 10% lower
    return "GO: no_L2 shows expected lower diversity"
elif no_l2_div > baseline_div * 1.1:  # Opposite direction
    return "NO-GO: no_L2 opposite to expected"
else:
    return "HOLD: Difference too small"
```

---

## NO-GO Rules

### N1: Conditions Not Runnable

**Rule**: Any sentinel condition fails to execute.

**Trigger**: Exit code != 0, timeout, or crash.

**Action**: Report to Codex immediately. Do not proceed.

---

### N2: Missing Required Fields

**Rule**: Any of the 7 required_now fields missing from CSV.

**Check**:
```bash
for field in archive_sample_attempts archive_sample_successes archive_influenced_births lineage_diversity top1_lineage_share strategy_entropy collapse_event_count; do
  if ! head -1 population.csv | grep -q "$field"; then
    echo "NO-GO: Missing field $field"
    exit 1
  fi
done
```

**Action**: Stop. Request Codex add missing fields.

---

### N3: Placeholder Data

**Rule**: Any critical field is all zeros or constant after generation 100.

**Critical Fields**:
- archive_sample_attempts
- archive_sample_successes
- lineage_diversity

**Check**:
```python
late_game = df[df['tick'] > 100]
if late_game['archive_sample_attempts'].max() == 0:
    return "NO-GO: Archive sampling not working"
```

**Action**: Stop. Archive system broken or not connected.

---

### N4: L3_real ≈ L3_shuffled (Falsification R1)

**Rule**: If L3_real and L3_shuffled are statistically equivalent AND no_L2 ≈ baseline.

**Interpretation**: Both L2 and L3 are irrelevant → Hypothesis falsified.

**Check**:
```python
r1 = cohens_d(L3_real, L3_shuffled) < 0.2
r2 = cohens_d(no_L2, baseline) < 0.2

if r1 and r2:
    return "NO-GO: R1 and R2 both indicate redundancy"
```

**Action**: Report falsification. Do not proceed with current architecture.

---

### N5: Values Out of Range

**Rule**: Any field has impossible values.

**Checks**:
- lineage_diversity < 1
- top1_lineage_share < 0 or > 1
- strategy_entropy < 0

**Action**: Stop. Data corrupted or semantic mismatch.

---

## HOLD Rules

### H1: Ambiguous Effect Size

**Rule**: Effect size between 0.2 and 0.5 for critical comparisons.

**Critical Comparisons**:
- no_L2 vs baseline
- L3_off vs baseline

**Action**: Extend to 5 seeds or longer runs (5000 gens).

---

### H2: High Seed Variance

**Rule**: Within-seed variance > 2× between-seed variance.

**Action**: Add more seeds (5 instead of 3).

---

### H3: Semantic Uncertainty

**Rule**: Field varies but meaning unclear.

**Example**: lineage_diversity >> population (implies historical counting).

**Action**: Clarify definition with Codex before using field.

---

### H4: Partial Completion

**Rule**: 75-89% of runs completed.

**Action**: Analyze completed runs, note limitations.

---

### H5: Direction Inversion

**Rule**: no_L2 shows opposite effect for different metrics.

**Example**: diversity ↓ but survival ↑

**Action**: Report both directions. Do not average. Add more metrics.

---

## Decision Flowchart

```
Start
  |
  v
All 5 conditions runnable? ----No----> NO-GO (N1)
  | Yes
  v
All 7 fields present? ---------No----> NO-GO (N2)
  | Yes
  v
Fields have real values? -----No----> NO-GO (N3)
  | Yes
  v
Values in valid range? -------No----> NO-GO (N5)
  | Yes
  v
L3_real ≈ L3_shuffled AND
no_L2 ≈ baseline? ------------Yes---> NO-GO (N4)
  | No
  v
Effect size clear (|d|>0.5
or |d|<0.2)? -----------------No----> HOLD (H1)
  | Yes
  v
Seed variance acceptable? -----No----> HOLD (H2)
  | Yes
  v
Semantics clear? --------------No----> HOLD (H3)
  | Yes
  v
Completion > 90%? -------------No----> HOLD (H4)
  | Yes
  v
Consistent direction? ---------No----> HOLD (H5)
  | Yes
  v
 GO
```

---

## Quick Reference Card

| Check | Pass | Hold | No-Go |
|-------|------|------|-------|
| Runnable | All 5 work | - | Any fails |
| Fields present | All 7 present | - | Any missing |
| Real values | All vary | Some constant | All zeros |
| Valid range | All in range | - | Any out |
| L3 content | Clear diff/similar | Ambiguous | Both redundant |
| no_L2 effect | Clear direction | Weak signal | Opposite/worse |
| Seed variance | Low | High | - |
| Completion | >90% | 75-89% | <75% |

---

## Reporting Template

```markdown
## Phase 3 GO/NO-GO Assessment

**Date**: [Date]
**Reviewer**: [Name]

### Checks

| Rule | Status | Notes |
|------|--------|-------|
| G1: Runnable | ☐ GO ☐ HOLD ☐ NO-GO | |
| G2: Fields present | ☐ GO ☐ HOLD ☐ NO-GO | |
| G3: Real values | ☐ GO ☐ HOLD ☐ NO-GO | |
| G4: L3 effect | ☐ GO ☐ HOLD ☐ NO-GO | |
| G5: no_L2 direction | ☐ GO ☐ HOLD ☐ NO-GO | |

### Verdict

**Overall**: ☐ GO ☐ HOLD ☐ NO-GO

### If HOLD
- Ambiguity: [Describe]
- Resolution: [Action]

### If NO-GO
- Reason: [Rule N1-N5]
- Required fix: [Describe]
```

---

**Execute this protocol immediately upon receiving Codex outputs.**
