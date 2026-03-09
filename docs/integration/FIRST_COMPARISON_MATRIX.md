# First Comparison Matrix

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Status**: Template - Fill in after Codex Phase 3 output

---

## Scope

**Conditions**: 5 only (minimal falsification set)
- baseline_full
- no_L2
- L3_off
- L3_real_p001
- L3_shuffled_p001

**Metrics**: 5 only (key indicators)
- survival_time
- lineage_diversity
- top1_lineage_share
- strategy_entropy
- collapse_event_count

**Goal**: Quick directional check, not definitive statistics.

---

## Comparison Matrix

### Metric 1: survival_time

| Condition A | Condition B | Expected Direction | Actual Direction | Pass/Fail/Ambiguous | Notes |
|-------------|-------------|-------------------|------------------|---------------------|-------|
| baseline_full | no_L2 | no_L2 shorter or similar | [FILL] | ☐ | |
| baseline_full | L3_off | L3_off shorter | [FILL] | ☐ | |
| L3_real_p001 | L3_shuffled_p001 | Similar (±15%) | [FILL] | ☐ | Critical for falsification |

**Verdict**: ☐ PASS ☐ FAIL ☐ AMBIGUOUS

---

### Metric 2: lineage_diversity

| Condition A | Condition B | Expected Direction | Actual Direction | Pass/Fail/Ambiguous | Notes |
|-------------|-------------|-------------------|------------------|---------------------|-------|
| baseline_full | no_L2 | no_L2 lower | [FILL] | ☐ | Key falsification test |
| baseline_full | L3_off | Different | [FILL] | ☐ | |
| L3_real_p001 | L3_shuffled_p001 | Similar (±10%) | [FILL] | ☐ | If different, L3 matters |

**Verdict**: ☐ PASS ☐ FAIL ☐ AMBIGUOUS

---

### Metric 3: top1_lineage_share

| Condition A | Condition B | Expected Direction | Actual Direction | Pass/Fail/Ambiguous | Notes |
|-------------|-------------|-------------------|------------------|---------------------|-------|
| baseline_full | no_L2 | no_L2 higher | [FILL] | ☐ | Monopoly indicator |
| baseline_full | L3_off | Different | [FILL] | ☐ | |
| L3_real_p001 | L3_shuffled_p001 | Similar | [FILL] | ☐ | |

**Verdict**: ☐ PASS ☐ FAIL ☐ AMBIGUOUS

---

### Metric 4: strategy_entropy

| Condition A | Condition B | Expected Direction | Actual Direction | Pass/Fail/Ambiguous | Notes |
|-------------|-------------|-------------------|------------------|---------------------|-------|
| baseline_full | no_L2 | no_L2 lower | [FILL] | ☐ | Convergence indicator |
| baseline_full | L3_off | Different | [FILL] | ☐ | |
| L3_real_p001 | L3_shuffled_p001 | Similar | [FILL] | ☐ | |

**Verdict**: ☐ PASS ☐ FAIL ☐ AMBIGUOUS

---

### Metric 5: collapse_event_count

| Condition A | Condition B | Expected Direction | Actual Direction | Pass/Fail/Ambiguous | Notes |
|-------------|-------------|-------------------|------------------|---------------------|-------|
| baseline_full | no_L2 | no_L2 higher | [FILL] | ☐ | Stress indicator |
| baseline_full | L3_off | Higher or similar | [FILL] | ☐ | |
| L3_real_p001 | L3_shuffled_p001 | Similar | [FILL] | ☐ | |

**Verdict**: ☐ PASS ☐ FAIL ☐ AMBIGUOUS

---

## Summary Verdicts

### By Condition Pair

| Pair | Overall Verdict | Key Metric | Notes |
|------|-----------------|------------|-------|
| baseline vs no_L2 | ☐ | lineage_diversity | Most important |
| baseline vs L3_off | ☐ | survival_time | |
| L3_real vs L3_shuffled | ☐ | lineage_diversity | Falsification critical |

### Overall Assessment

**Total Comparisons**: 15  
**Clear Pass**: [FILL]/15  
**Clear Fail**: [FILL]/15  
**Ambiguous**: [FILL]/15

**Final Verdict**: ☐ GO ☐ HOLD ☐ NO-GO

---

## Falsification Check

### Rule Checks

| Rule | Condition | Expected | Actual | Status |
|------|-----------|----------|--------|--------|
| R1: L3 content irrelevant | L3_real ≈ L3_shuffled? | No | [FILL] | ☐ |
| R2: L2 redundant | no_L2 ≈ baseline? | No | [FILL] | ☐ |
| R5: Fields constant | Any field σ² < 0.001? | No | [FILL] | ☐ |

**Falsification Status**: ☐ NONE ☐ PARTIAL ☐ FULL

---

## Data Quality Notes

| Issue | Present? | Severity | Action |
|-------|----------|----------|--------|
| Seed variance too high | ☐ | | |
| Some runs incomplete | ☐ | | |
| CSV parsing errors | ☐ | | |
| Values out of range | ☐ | | |

---

## Next Steps

### If GO
- Proceed to longer runs (5000 generations)
- Add more replicates (5 seeds)
- Begin ContinuityProbe integration

### If HOLD
- Identify specific ambiguity source
- Run additional quick checks (200 gens)
- Re-examine semantic definitions

### If NO-GO
- Report specific failure mode
- Request Codex fix before continuing
- Do not proceed to longer runs

---

**Filled by**: [Name]  
**Date**: [Date]  
**Reviewed by**: [Name]
