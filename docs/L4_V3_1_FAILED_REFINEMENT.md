# L4-v3.1: Failed Refinement Report

**Status**: ❌ FAILED REFINEMENT  
**Date**: 2026-03-14  
**Conclusion**: Route-motif-level refinement introduced negative effect under Task-2

---

## Executive Summary

L4-v3.1 attempted to amplify reuse by refining mechanism semantics from family-level to route-motif-level. **Result: negative effect**.

| Metric | L4-v3.0 | L4-v3.1 | Change |
|--------|---------|---------|--------|
| Round A reuse | 40% | **36%** | -4pp |
| Round B reuse | **45%** | **32%** | **-13pp** |
| Mechanism effect | **+5pp** | **-4pp** | **-9pp reversal** |
| Leakage | 0% | 0% | maintained |

**Critical Finding**: Refined semantics not only failed to improve reuse — they actively degraded performance.

---

## What Failed

### Route-Motif Refinement

**Hypothesis**: Finer-grained semantics (route motifs vs families) would enable stronger mechanism bias and higher reuse.

**Reality**: 
- Motif definitions may not match Task-2's actual stable patterns
- Weights may have been set incorrectly
- Over-constraint from finer granularity filtered good candidates

### Key Evidence

```
L4-v3.0:  40% → 45%  (+5pp mechanism effect)
L4-v3.1:  36% → 32%  (-4pp mechanism effect) ← NEGATIVE
```

The reversal is clear and significant.

---

## What Did NOT Fail

### Core Architecture
- Task-2 as experimental field: still valid (100% approve)
- Anti-leakage guardrail: still effective (0% leakage)
- Mechanism-first direction: still valid (L4-v3.0 showed +5pp)
- A/B/Ablation methodology: still sound

### L4-v3.0 Foundation
- Family-level semantics worked (+5pp)
- 45% reuse achieved
- Clean signal established

---

## Root Cause Analysis

### Primary: Motif-Task Mismatch

The refined route motifs in v3.1 were designed based on:
- L4-v3.0 observations (limited sample)
- Theoretical decomposition of families
- Not validated against actual Task-2 behavior

**Result**: Motifs that looked good in theory did not translate to better candidates.

### Secondary: Over-Constraint

**v3.0**: Bias toward stable families (coarse but flexible)
**v3.1**: Bias toward specific motif signatures (fine but rigid)

The finer granularity may have:
- Excluded viable candidates that didn't match exact motif patterns
- Created false negatives (good candidates rejected)
- Overfitted to L4-v3.0's small sample

---

## Lessons Learned

### 1. Validation Before Refinement

**Mistake**: Refined semantics without validating motif definitions on larger sample.

**Lesson**: Always validate decomposition (family → motif) before using it for generation bias.

### 2. Granularity Has Cost

**Insight**: Finer is not always better. Coarse but correct > fine but wrong.

**Implication**: Family-level (v3.0) captured real patterns; motif-level (v3.1) introduced artificial constraints.

### 3. Negative Results Are Information

**Value**: We now know route-motif approach (as implemented) doesn't work for Task-2.

**Action**: Next motif redesign must be validated differently.

---

## Immediate Response: L4-v3.0-Expanded

### Decision

**Revert to L4-v3.0 configuration, expand sample only**.

### What Stays

| Component | Configuration | Rationale |
|-----------|--------------|-----------|
| Task | Task-2 | Clean field proven |
| Package | v3.0 family-level | Worked (+5pp) |
| Anti-leakage | 0.2 | Verified guardrail |
| Methodology | A/B/Ablation | Sound |

### What Changes

| Component | L4-v3.0 | L4-v3.0-Expanded |
|-----------|---------|------------------|
| Sample size | 100/round | **300/round** |
| Eval sample | 20/round | **50/round** |

### Single Question to Answer

> Is L4-v3.0's 45% reuse a stable phenomenon, or was it small-sample noise?

### Success Criteria

| Scenario | Round A | Round B | Effect | Interpretation |
|----------|---------|---------|--------|----------------|
| **Stable** | ~40% | ~45%+ | +5pp | 45% is real baseline; v3.1 was wrong turn |
| **Unstable** | ~35% | ~38% | +3pp | 45% was noise; current architecture has lower ceiling |

### Decision Gates

**If Stable** (A~40%, B~45%, effect +5pp):
- ✅ Confirm v3.0 is solid foundation
- ✅ v3.1 failure was motif definition, not direction
- → Can attempt v3.2 with corrected motifs

**If Unstable** (A~35%, B~38%, effect weak):
- ⚠️ Reassess architecture ceiling
- ⚠️ 60% target may be unrealistic
- → Discuss target adjustment or fundamental redesign

---

## Documentation

### Failed Branch

```
L4-v3.0 (baseline, +5pp) ─┬─► L4-v3.1 (refined, -4pp) ❌ FAILED
                           │
                           └─► L4-v3.0-Expanded (validation) 🔄 CURRENT
```

### Key Files

```
docs/
├── L4_V3_1_FAILED_REFINEMENT.md (this file)
└── L4_V3_0_EXPANDED_PLAN.md (next step)

data/
├── /tmp/l4v3_1_task2_results/ (failed run, archived)
└── /tmp/l4v3_0_expanded/ (validation run, pending)
```

---

## Relationship to Main Research

### Not a Line Failure

L4-v3.1 is a **failed refinement attempt**, not a failure of the compositional reuse line.

**Foundation still solid**:
- Task-2 is clean field
- Mechanism-first direction confirmed (v3.0)
- Anti-leakage works
- Methodology sound

### Local Error, Global Direction Preserved

The negative result localizes the problem:
- ❌ Route-motif implementation (v3.1)
- ✅ Family-level mechanism bias (v3.0)
- ✅ Task-2 as validator

---

## Conclusion

L4-v3.1 attempted refinement too aggressively without validation. The negative effect (-4pp vs +5pp) clearly indicates the motif decomposition was incorrect for Task-2.

**Correct response**: Step back to v3.0, validate stability with larger sample, then attempt corrected refinement.

**Research discipline**: Failed refinements are data. We now know one path that doesn't work, which narrows the search space for what does.

---

**Status**: FAILED REFINEMENT — Archived  
**Next**: L4-v3.0-Expanded validation  
**Confidence in line**: Maintained (v3.0 foundation still valid)

---

*Failed refinement logged for future motif design reference*  
*Date: 2026-03-14*
