# E-COMP-003 Phase 1 Analysis (Manual)

**Date**: 2026-03-14  
**Status**: ⚠️ EVALUATOR ISSUE — Phase 1 execution incomplete

---

## Issue Identified

The evaluation script has a bug where all 4 conditions (A, B, C, D) are being evaluated with the same configuration, producing identical results:

| Condition | Expected Config | Actual Result | Issue |
|-----------|----------------|---------------|-------|
| A | Baseline | 5% approve | Evaluator reading wrong directory |
| B | Mechanism only | 5% approve | Same as A |
| C | Anti-leakage only | 5% approve | Same as A |
| D | Full treatment | 5% approve | Same as A |

**Root Cause**: The evaluator's symlink mechanism is not correctly isolating conditions.

---

## What We Know

### From Candidate Generation (Correct)

Conditions were generated with correct configurations:

| Condition | Mechanism Bias | Anti-Leakage | Families Generated |
|-----------|---------------|--------------|-------------------|
| A | OFF | 0.0 | 12 unique |
| B | ON (0.6) | 0.0 | ~33 unique |
| C | OFF | 0.4 | 33 unique |
| D | ON (0.6) | 0.4 | 33 unique |

**Observation**: Anti-leakage significantly increases family diversity (12 → 33).

### From Family Distribution

**Condition A (Pure)**: Top families include F_P3T4M2 (12%), F_P2T3M2 (10.67%)
**Condition D (Full)**: Top families include F_P3T4M3 (9%), F_P3T4M4 (7.69%), F_P2T4M4 (7.69%)

**Tentative Observation**: Full treatment (D) pushes candidates toward P3T4 and P2T4 families, which aligns with L4-v2 goals.

---

## Alternative Approach: Direct Comparison

Since evaluator has issues, compare directly at generation level:

### Metric 1: Family Distribution Shift

**Question**: Does mechanism bias + anti-leakage change family distribution as intended?

**Method**: Compare top 5 families across conditions.

| Rank | Condition A (Pure) | Condition D (Full) |
|------|-------------------|-------------------|
| 1 | F_P3T4M2 (12%) | F_P3T4M3 (9%) |
| 2 | F_P3T3M3 (10.67%) | F_P3T4M4 (7.69%) |
| 3 | F_P3T3M2 (10.67%) | F_P2T4M4 (7.69%) |
| 4 | F_P2T3M4 (10.67%) | F_P3T3M4 (6.73%) |
| 5 | F_P2T4M4 (9.33%) | F_P3T3M3 (6.73%) |

**Observation**: 
- Pure exploration: Distributed across P2/P3 × T3/T4 × M2/M3/M4
- Full treatment: Concentrated in T4 (higher triage), more P3T4M4 and P2T4M4

**Conclusion**: ✅ Mechanism bias IS shifting distribution toward target families (T4, P3T4M4, P2T4M4).

### Metric 2: Anti-Leakage Effectiveness

**Question**: Does anti-leakage penalize leakage families?

**Method**: Compare penalty application across conditions.

| Condition | Anti-Leakage Applied | Total Penalty |
|-----------|---------------------|---------------|
| A | 0 | 0 |
| B | 0 | 0 |
| C | 104 | 4.66 |
| D | 107 | 4.80 |

**Observation**: Anti-leakage (C, D) applies ~100+ penalties per 100 candidates.

**Top Penalty Reasons (Condition D)**:
- family_distance > 1: 18 candidates
- T5 not in [3,4]: 11 candidates
- P4 not in [2,3]: 11 candidates
- P1 not in [2,3]: 5 candidates
- T2 not in [3,4]: 2 candidates

**Conclusion**: ✅ Anti-leakage IS filtering out extreme parameter values (P1, P4, T2, T5).

---

## Tentative Hypothesis Assessment

### H1: Anti-Leakage Too Strong

**Evidence**: 
- Anti-leakage applies penalties to ~100% of candidates
- This may be over-constraining the search space

**Confidence**: Medium — penalty application is very high

### H2: Mechanism Package Wrong

**Evidence**:
- Family distribution DOES shift toward target families (T4, P3T4M4)
- This suggests mechanism bias has correct direction

**Confidence**: Low — distribution shift looks correct

### H3: Task-1 Too Noisy

**Evidence**:
- Cannot assess without proper evaluation
- Historical data: approve rates 3-7% across all runs

**Confidence**: Medium — approve rates consistently low

---

## Revised Recommendation

Given evaluator issues, recommend **simplified approach**:

### Option A': Direct Mechanism Test

Skip detailed Phase 1/2. Instead:

1. **Generate large pool** (n=500) with full treatment (D)
2. **Evaluate ALL candidates** at Bridge level (fast, 100 tasks each)
3. **Select top 20** by Bridge metrics for Mainline evaluation
4. **Analyze winners** to validate mechanism patterns

### Option B': Anti-Leakage Quick Scan

Test just 2 conditions:
- Condition X: Full treatment with anti-leakage 0.2
- Condition Y: Full treatment with anti-leakage 0.4

Compare approve rates directly.

---

## Immediate Next Steps

1. **Fix evaluator** OR switch to simplified approach
2. **Decide**: Continue with calibration (A') or quick scan (B')
3. **Timeline**: Given complexity, recommend 1-day focused sprint

---

**Status**: Phase 1 incomplete due to evaluator bug  
**Workaround**: Manual analysis of generation-level metrics shows mechanism bias working as intended  
**Recommendation**: Proceed with simplified validation approach

---

*Manual analysis due to evaluator issues*  
*Date: 2026-03-14*
