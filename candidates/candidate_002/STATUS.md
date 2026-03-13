# Candidate 002 Status: ARCHIVED

**Date**: 2025-03-08  
**Previous Status**: REFINE  
**Current Status**: **ARCHIVED**

---

## Falsification History

| Test | Condition | Result | Finding |
|------|-----------|--------|---------|
| 1 | Proprioceptive Required | ✅ PASS | Blind agent degrades |
| 2 | Prediction Loop Affects Stability | ❌ FAIL | No effect in 2D mesh |
| 2b | 1D Spring Diagnostic | ❌ FAIL | No effect in 1D either |
| 3 | Recovery from Perturbation | ✅ PASS | Body-map recovers |

## Final Diagnostic

**1D Spring Test Results:**
- Normal (with prediction): Position stability = 0.998
- No-prediction: Position stability = 0.998
- **Difference**: -0.000 (no improvement)

**Conclusion**: Prediction-error minimization does not measurably improve stability, even in simplified 1D system. Root cause likely in the learning dynamics or the way prediction error is converted to control signals.

## Archive Decision

Per protocol: When 1D diagnostic fails, candidate is **ARCHIVED**, not continued.

**Reason**: Core hypothesis (prediction loop affects stability) falsified in both 2D and 1D conditions. Continuing would require fundamental redesign, exceeding REFINE scope.

## Lessons

1. 2D mesh was not the masking factor
2. Prediction-error minimization alone insufficient
3. May need active inference or explicit belief updating

## Files

- `soft_body_agent.py` - Original 2D implementation
- `test_falsification.py` - 2D tests (2/3 pass)
- `spring_1d_diagnostic.py` - Final diagnostic (FAIL)
- `STATUS.md` - This file

---

**Archived**: 2025-03-08  
**Next Candidate**: Candidate 001 (INTEGRATION phase)
