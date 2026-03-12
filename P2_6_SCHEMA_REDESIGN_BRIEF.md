# P2.6 Schema Redesign Brief

**Status:** ⏸️ PAUSED - Redesign Required Before Restart  
**Date:** 2026-03-12  
**Original Goal:** Specialist Routing validation

---

## 1. Why SR1 Failed Twice

### Root Cause: Fingerprint Misclassification

Current SR1 fingerprint treats **scale effects** as **structural differences**:

| Observation | Misclassified As | Actually Is |
|-------------|------------------|-------------|
| CWCI drops at 6x | "Specialist routing ineffective" | Normal 6x boundary behavior |
| Seed 44 degrades | "SR failure" | Expected 12.5% degradation |
| Failover triggers | "Instability" | Designed monitoring response |

**Problem:** SR1 schema lacks scale-aware dimensions, conflating P0 envelope behavior with SR effectiveness.

### Evidence from R6 Validation

- P0 6x without SR: 12.5% degradation, CWCI 0.638
- SR1 attempted at 6x: Similar degradation observed
- **Conclusion:** Degradation is scale effect, not SR failure

**Current schema cannot distinguish:**
- Scale-induced degradation vs SR-induced improvement
- Normal 6x variance vs SR signal

---

## 2. Required Scale-Aware Dimensions

New schema must include:

### 2.1 Scale-Normalized Metrics

```yaml
metrics:
  absolute_cwci: "raw measurement"
  
  scale_normalized_cwci:
    formula: "(cwci - baseline_4x) / (expected_6x_variance)"
    # Removes expected 6x degradation, isolates SR effect
    
  degradation_attribution:
    scale_component: "from 4x→6x envelope model"
    sr_component: "residual after scale removal"
```

### 2.2 Seed-Stratified Analysis

| Seed Type | Expected Behavior | SR Success Criteria |
|-----------|-------------------|---------------------|
| Stable (7/8) | CWCI ~0.64 | Maintain or improve |
| Degradable (1/8) | CWCI dips to ~0.57 | Faster recovery vs baseline |

**Current mistake:** Averaging all seeds masks SR effect on degradable seeds.

### 2.3 Time-Resolved Comparison

```yaml
comparison_windows:
  pre_degradation: "ticks 0-500, all seeds"
  during_degradation: "seed-specific, dynamic window"
  post_failover: "ticks post-failover, compare SR vs baseline"
```

**Required:** SR must show benefit **during** degradation event, not just overall.

---

## 3. Restart Conditions

### Before Restarting SR1

**Must Have:**

1. [ ] Scale-aware fingerprint schema (sections 2.1-2.3 above)
2. [ ] Baseline dataset: P0 6x without SR, per-seed, per-tick
3. [ ] Challenger data: Valid seed-spike candidates from P2.5
4. [ ] Clear hypothesis: "SR improves [specific metric] for [specific seed type] at [specific phase]"

**Must Validate:**

1. [ ] Can distinguish scale effect from SR effect
2. [ ] Baseline 6x variance is repeatable
3. [ ] SR mechanism is compatible with 6x envelope

### Explicitly Forbidden Until Conditions Met

- ❌ Third SR1 attempt with current schema
- ❌ SR2/SR3 any work
- ❌ Any SR production deployment claim

---

## 4. Current Blockers

| Blocker | Status | Unblocks When |
|---------|--------|---------------|
| Schema lacks scale-awareness | 🔴 Active | Section 2.1-2.3 implemented |
| No validated 6x baseline | 🔴 Active | Weekly ops dataset 4+ weeks |
| Seed-spike registry incomplete | 🟡 Partial | P2.5 accumulates more data |
| SR-hypothesis too vague | 🔴 Active | Specific mechanism proposed |

---

## 5. Recommended Path Forward

### Option A: Minimal Redesign (Recommended)

1. Add scale-normalized metrics to fingerprint
2. Wait 4 weeks of P0 weekly ops data
3. Re-run SR1 with new schema only
4. Decision: continue / modify / terminate

**Effort:** 2 weeks  
**Risk:** Low  
**Value:** Answers "does SR matter at scale?"

### Option B: Full Redesign

1. Rebuild entire SR architecture with scale-awareness
2. Integrate with Tier 2 monitoring infrastructure
3. Run extended validation (8+ weeks)
4. Decision: production candidate or not

**Effort:** 2 months  
**Risk:** Medium  
**Value:** Potential production feature

### Option C: Terminate

1. Accept that SR may not add value at 6x
2. Focus P2.6 resources elsewhere
3. Maintain 8x research for future architecture

**Effort:** Immediate  
**Risk:** None  
**Value:** Resource reallocation

---

## 6. Decision Checkpoint

**Current Recommendation:** Option A (Minimal Redesign)

**Rationale:**
- Low cost to validate core question
- Uses existing P0 operational data
- Prevents premature termination
- Does not over-invest if negative

**Decision Required By:** 2026-03-26  
**Decision Owner:** Research Lead (Dr. Sarah Williams)  
**P0 Impact:** None (P2.6 remains paused regardless)

---

## One-Line Summary

> **P2.6 paused for schema redesign. Current fingerprint conflates scale effects with SR effectiveness. Restart requires scale-aware dimensions, 4+ weeks baseline data, and specific hypothesis.**

---

**Do not restart SR1 until restart conditions are met.**
