# E-COMP-003 Gate-1 Validation Report

**Date**: 2026-03-14  
**Status**: ⚠️ INCONCLUSIVE — High variance, mechanism bias not consistently outperforming baseline

---

## Executive Summary

Gate-1 evaluation completed with n=90 candidates (30 per round). Results show **high variance** and **inconsistent performance** of mechanism bias:

| Round | Approve Rate | Reuse Rate | F_P3T4M4 | Winners |
|-------|-------------|-----------|----------|---------|
| Round A-v3 (pure) | 6.67% | 50.0% | 0.0% | 2/30 |
| **Round B-v3 (mechanism bias)** | **3.33%** | **0.0%** | **0.0%** | **1/30** |
| Ablation-v3 (control) | 6.67% | 50.0% | 0.0% | 2/30 |

**Critical Finding**: Round B (with mechanism bias) performed **worse** than pure exploration and ablation.

---

## Gate-1 Target Assessment

### Target 1: T4M4 Stability Foundation

**Status**: ❌ NOT VALIDATED

**Evidence**:
- Winners distributed across families, no clear T4M4 dominance
- Sample too small (n=5 winners total) to confirm pattern

**Required**: n=20+ winners to validate T4M4 foundation

### Target 2: F_P3T4M4 as Mechanism Bundle

**Status**: ❌ NOT VALIDATED

**Evidence**:
- No F_P3T4M4 winners in Gate-1
- F_P3T4M4 appeared in original L4-v2 (n=1), but not replicating

**Concern**: May have been statistical fluke in original sample

### Target 3: P2 vs P3 as Risk-Preference Tuning

**Status**: ❌ NOT VALIDATED

**Evidence**:
- Winners: 3 from Round A/Ablation, 1 from Round B
- No clear P2 vs P3 pattern
- Variance too high to draw conclusions

### Target 4: Pattern Table Predictive Power

**Status**: ⚠️ PARTIAL

**Evidence**:
- Control purity maintained ✅ (Round A = Ablation)
- Reuse rate signal inconsistent (50% in A/Ablation, 0% in B)
- Leakage consistently 0% ✅

---

## Critical Issue: Mechanism Bias Underperforming

### Observation

Round B (mechanism bias + anti-leakage) had **lowest** approval rate:
- Round A: 6.67%
- Round B: 3.33% ← **Worst**
- Ablation: 6.67%

### Possible Explanations

1. **Over-constraint**: Anti-leakage too aggressive, filtering out viable candidates
2. **Wrong priors**: v2 mechanism package may encode incorrect assumptions
3. **High variance**: Task-1 stochasticity dominates any signal
4. **Sample size**: n=30 per round still too small for stable estimates

### Comparison with Original L4-v2

| Metric | Original L4-v2 | Gate-1 | Difference |
|--------|---------------|--------|------------|
| Round B approve | 6.67% | 3.33% | -50% |
| Round B reuse | 50% | 0% | -100% |
| F_P3T4M4 in winners | Yes (1) | No | Disappeared |

---

## Root Cause Analysis

### Hypothesis 1: Task-1 Difficulty Masks All Signals

**Evidence**:
- All approve rates 3-7% (very low)
- High variance between runs
- Even "stable families" from calibration only 14-20% pass

**Implication**: No mechanism can achieve high approval on this validator

### Hypothesis 2: Mechanism Bias Over-Constrained

**Evidence**:
- Round B worse than pure exploration
- Anti-leakage may be too aggressive
- Route constraints too restrictive

**Implication**: v2 package needs tuning, not just scaling

### Hypothesis 3: Statistical Fluke in Original L4-v2

**Evidence**:
- F_P3T4M4 appeared once (n=1), never replicated
- Patterns not stable across runs
- Small samples unreliable for mechanism inference

**Implication**: Need much larger samples (n=500+) or different approach

---

## Decision Gate Assessment

| Gate | Criteria | Status | Reason |
|------|----------|--------|--------|
| **Gate-1A** | All 4 targets met | ❌ FAIL | Mechanism bias not consistently outperforming |
| **Gate-1B** | ≥2 targets fail | ✅ TRIGGER | Pattern table not predictive |
| **Gate-1C** | Map stable, test generalization | ❌ FAIL | Map not stable |

**Verdict**: Gate-1B triggered — **REVISION REQUIRED**

---

## Recommendations

### Option A: Deep Calibration (Recommended)

**Goal**: Understand why mechanism bias underperforms

**Actions**:
1. **Relax anti-leakage**: Test 0.2, 0.3, 0.4 strengths
2. **Ablation study**: Mechanism-only (no anti-leakage) vs anti-leakage-only
3. **Larger sample**: n=500 candidates, evaluate all (not just stratified 30)

**Timeline**: 1-2 days

### Option B: Switch to Task-2

**Rationale**: Task-1 difficulty may be too high to see mechanism signals

**Risk**: May repeat same problem if Task-2 also difficult

### Option C: Redesign Inheritance Package

**Rationale**: Current v2 package may have wrong priors

**Approach**: Learn from winners (n=5 total across all rounds), rebuild package

---

## Updated Confidence Assessment

| Claim | Original Confidence | Gate-1 Confidence | Change |
|-------|-------------------|------------------|--------|
| T4M4 is foundation | High | Low | ❌ Downgraded |
| F_P3T4M4 is mechanism bundle | Medium | Very Low | ❌ Downgraded |
| Anti-leakage works | High | Medium | ⚠️ Downgraded |
| Control purity | High | High | ✅ Maintained |

---

## Next Steps

### Immediate (Today)

1. **Decision**: Choose Option A, B, or C
2. **Documentation**: Update E-COMP-003 status
3. **Archive**: Gate-1 results preserved for comparison

### Short-term (This Week)

If Option A:
- Run anti-leakage ablation study
- Test multiple penalty strengths
- Build proper learning curve (n=50, 100, 200, 500)

If Option B:
- Design Task-2 validator
- Port mechanism bias to new task
- Compare cross-task patterns

If Option C:
- Analyze all winners (n=5) for common patterns
- Rebuild v3 package from actual data
- Test new package in quick iteration

---

## Conclusion

Gate-1 did **not** validate the mechanism map. Instead, it revealed:

1. **High variance**: Task-1 results inconsistent across runs
2. **Underperforming bias**: Mechanism bias + anti-leakage worse than pure exploration
3. **Unstable patterns**: F_P3T4M4 disappeared in larger sample

**Recommendation**: Before scaling to L4-v3, must understand why mechanism bias underperforms. Suggest **Option A (Deep Calibration)** to isolate variables.

---

**Status**: ⚠️ GATE-1B TRIGGERED — Revision Required  
**Next Decision**: Choose Option A, B, or C  
**Confidence in Current Map**: LOW

---

*Generated: 2026-03-14*  
*E-COMP-003 Gate-1 Validation*
