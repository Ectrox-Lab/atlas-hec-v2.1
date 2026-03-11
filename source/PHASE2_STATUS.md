# Phase 2 Open-World Validation Status

## Round 1: MINIMAL BATCH PASSED ✓
## Round 1.5: TUNING ROUND PASSED ✓
## Round 2: IN PROGRESS

**Date:** 2026-03-12  
**Latest Config:** 3 seeds × 2000 ticks per environment

---

### Completed

#### Round 1 Results (3 seeds × 1200 ticks)
| Environment | Pass Rate | Status | Notes |
|------------|-----------|--------|-------|
| **HubFailureWorld** | 2/3 | ✓ **PASS** | Recovery logic functional, pop 299-359 |
| **RegimeShiftWorld** | 2/3 | ✓ **PASS** | Adaptation working, pop 282-310 |
| **MultiGameCycle** | 2/3 | ✓ **PASS** | Overflow fixed, pop 3012-3805 |
| **ResourceCompetition** | 1/3 | ⚠ **DEBT** | Scarcity too high, pop 155-193 |

#### Round 1.5: Tuning Round
**Changes:**
- Food spawn: 0.06 → 0.09 (+50%)
- Metabolism: 0.9 → 0.85 (-6%)
- Reproduction threshold: 40.0 → 38.0 (-5%)

**Results:**
| Environment | Pass Rate | Status |
|------------|-----------|--------|
| **ResourceCompetition** | 2/3 | ✓ **IMPROVED** (775-1045 pop) |
| **HubFailureWorld** | 2/3 | ✓ **NO REGRESSION** |

**All 4 environments now at 2/3+**

---

### Round 2: Current Status

**Target:** 5 seeds × 3000 ticks  
**Current:** 3 seeds × 2000 ticks (scaled due to timeout)  
**Method:** Independent environment runs + unified CSV

#### Performance Issue
- Single environment: ~0.07s ✓
- 4 env × 3 seeds batch: Timeout at 60s ✗
- Suspected: Trajectory collection overhead

#### Pass Criteria
| Environment | Target | Status |
|------------|--------|--------|
| HubFailureWorld | ≥ 2/3 | Pending |
| RegimeShiftWorld | ≥ 2/3 | Pending |
| ResourceCompetition | ≥ 2/3 | Pending |
| MultiGameCycle | No overflow + coord | Pending |
| Cross-env | No degradation | Pending |

---

### Files

- `phase2_batch_3x2k.rs`: Round 1/1.5 runner
- `phase2_round2.rs`: Round 2 runner (WIP)
- `phase2_resource_tuned.rs`: Tuning round
- `/tmp/phase2_*.csv`: Results
- `PHASE2_STATUS.md`: This document
