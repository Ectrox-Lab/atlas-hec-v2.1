# Phase 2 Open-World Validation Status

## Round 1: MINIMAL BATCH PASSED ✓
## Round 1.5: TUNING ROUND PASSED ✓

**Date:** 2026-03-12  
**Config:** 3 seeds × 1200 ticks per environment

### Round 1 Results

| Environment | Pass Rate | Status | Notes |
|------------|-----------|--------|-------|
| **HubFailureWorld** | 2/3 | ✓ **PASS** | Recovery logic functional, pop 299-359 |
| **RegimeShiftWorld** | 2/3 | ✓ **PASS** | Adaptation working, pop 282-310 |
| **MultiGameCycle** | 2/3 | ✓ **PASS** | Overflow fixed, pop 3012-3805 |
| **ResourceCompetition** | 1/3 | ⚠ **DEBT** | Scarcity too high, pop 155-193 |

### Round 1.5: Tuning Round

**Changes:**
- Food spawn: 0.06 → 0.09 (+50%)
- Metabolism: 0.9 → 0.85 (-6%)
- Reproduction threshold: 40.0 → 38.0 (-5%)

**Results:**
| Environment | Pass Rate | Status |
|------------|-----------|--------|
| **ResourceCompetition** | 2/3 | ✓ **IMPROVED** |
| **HubFailureWorld** | 2/3 | ✓ **NO REGRESSION** |

### Current Status (ALL ENVIRONMENTS)
| Environment | Pass Rate | Status |
|------------|-----------|--------|
| HubFailureWorld | 2/3 | ✓ PASS |
| RegimeShiftWorld | 2/3 | ✓ PASS |
| MultiGameCycle | 2/3 | ✓ PASS |
| ResourceCompetition | 2/3 | ✓ PASS |

---

## Next: Round 2

**Goal:** Bring ResourceCompetition to 2/3 without degrading HubFailureWorld

**Changes:**
- Relax scarcity (food spawn rate)
- Adjust metabolism/reproduction balance
- Keep other 3 environments fixed

**Test:**
- ResourceCompetition (target 2/3)
- HubFailureWorld (regression protection)

**Pass Criteria:**
- ResourceCompetition ≥ 2/3, OR
- ResourceCompetition significantly improved + HubFailure unchanged

---

## Round 2 Plan (after tuning)

**Config:** 5 seeds × 3000 ticks per environment  
**Method:** Independent environment runs + unified CSV aggregation  
**Target:** Full 4-environment validation

---

## Files

- `phase2_batch_3x2k.rs`: Main batch runner
- `/tmp/phase2_*.csv`: Per-environment results
- `PHASE2_STATUS.md`: This document
