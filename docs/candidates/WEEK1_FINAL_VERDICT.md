# Week 1 Final Verdict

**Date**: 2026-03-17 (Friday)  
**Commit**: `abf2ee1`  
**Status**: EXPERIMENTS COMPLETE

---

## Executive Summary

| Track | Verdict | Confidence | Key Finding |
|-------|---------|------------|-------------|
| **001 Markers** | 🟡 **REFRAME** | Medium | Fixed-marker semantics wrong; dynamic update OK |
| **002 Soft Robot** | 🔴 **KILL** | High | No feedback advantage in any task condition |

---

## Track 1: 001 Consistency Markers

### Final Experiment: Site-of-Action Dissection

| Condition | Consistency | Interpretation |
|-----------|-------------|----------------|
| Baseline (no marker) | 1.000 | Reference |
| **WriteOnly** | **1.000** | ✅ Write mechanism harmless |
| **ReadOnly** (fixed) | **0.502** | ❌ Fixed marker harms performance |
| **Full** (dynamic) | **1.000** | ✅ Dynamic update works |

### Diagnostic Logic

```
If WriteOnly ≈ Baseline: Write mechanism OK ✓
If ReadOnly < Baseline: Marker semantics wrong ✗
If Full ≈ Baseline: Dynamic coupling OK ✓
```

### Root Cause Analysis

**Problem**: Fixed coherence value (128) doesn't provide useful signal
- Agents reading frozen marker make suboptimal decisions
- Dynamic marker with actual coherence computation works fine

**Not a failure of**: Timescale separation, update mechanism, general concept
**Actually a failure of**: Static marker initialization in ReadOnly mode

### Recommended Verdict: REFRAME

**Rationale**:
- Mechanism isn't fundamentally broken
- But "fixed marker" assumption in ablation was misleading
- Need to redesign: marker must carry useful dynamics

**Next Steps**:
1. Retire "fixed marker" concept
2. Test if dynamic marker helps in more complex environments
3. If still no benefit after 1 more week → ARCHIVE

---

## Track 2: 002 Soft Robot

### Final Experiment: Single-Shot Recovery

**Task**: Single strong perturbation (40 velocity impulse), clean recovery

| Metric | Predictive | Reactive | No Control |
|--------|------------|----------|------------|
| Peak drift | 0.160 | 0.160 | 0.160 |
| Time to 50% | 0.03s | 0.03s | 0.03s |
| Time to 90% | None | None | None |
| Residual drift | 0.044 | 0.044 | 0.044 |
| **Recovery rate** | **0%** | **0%** | **0%** |

### Previous Experiments Summary

| Experiment | Result |
|------------|--------|
| Standard stability | All conditions = 0.964 |
| With micro-perturbations | All conditions = 0.368 |
| Recovery detection | All conditions = 0.6s |
| Single-shot recovery | All conditions identical |

### Diagnostic Conclusion

**Consistent pattern**: Feedback controller never outperforms open-loop or reactive

**Not due to**:
- NaN/numerical issues (fixed)
- Recovery detection bugs (fixed)
- Task too easy (tried harder conditions)

**Actual cause**: 
- Current feedback mechanism doesn't leverage predictive model effectively
- Simple reactive control is sufficient for this physics

### Recommended Verdict: KILL

**Rationale**:
- Exhaustive testing across multiple task types
- No condition separation in any metric
- Feedback mechanism not producing value

**Resource reallocation**: Move effort to 001 or new candidates

---

## Resource Reallocation

### Immediate (Next Week)

| Allocation | Target | Rationale |
|------------|--------|-----------|
| 70% | **Superbrain/超脑主线** | Core project priority |
| 20% | 001 REFRAME | One last test of dynamic marker |
| 10% | New candidate exploration | If 001 fails, need backup |
| 0% | 002 | Terminated |

### If 001 REFRAME Fails

| Allocation | Target |
|------------|--------|
| 85% | Superbrain主线 |
| 15% | New candidate search |

---

## Key Learnings

### 001 Lessons

1. **Ablation design matters**: Fixed-marker vs no-marker is different from dynamic-marker vs no-marker
2. **Metric coupling was real**: Decision-level vs tick-level coherence gave different patterns
3. **Timescale not the issue**: 5x performed as well as 1x after metric fix

### 002 Lessons

1. **Task design is critical**: Must expose control value, not just stability
2. **Multiple task types needed**: Single task insufficient for validation
3. **Kill criteria work**: When no condition separates after exhaustive testing, mechanism likely invalid

### Process Lessons

1. **Early gates valuable**: Caught 002 issues before major investment
2. **Diagnostic experiments > parameter sweeps**: Site dissection told us more than 20x timescale sweep
3. **Parallel tracks reduce risk**: If only ran 002, would have wasted full 4 weeks

---

## Action Items

| ID | Action | Owner | Due |
|----|--------|-------|-----|
| 1 | Document 002 termination | - | Today |
| 2 | 001 REFRAME experiment design | - | Monday |
| 3 | Archive 002 code with notes | - | This week |
| 4 | Review TINA candidate pool | - | This week |

---

## Sign-off

**001 Decision**: REFRAME  
**002 Decision**: KILL  
**Next Review**: Monday 2026-03-20 (001 REFRAME checkpoint)

---

**Experiment Code**: `abf2ee1` FINAL EXPERIMENTS: Week 1 verdict experiments
