# P2.6 Restart Readiness Scorecard

**Status**: ⏳ Restart Preparation (Execution Still Paused)  
**Last Updated**: 2026-03-12 23:30 UTC  
**Campaign**: Restart Readiness (Accelerated)

---

## Four Critical Conditions - Progress Tracker

| # | Condition | Required | Current | Progress | Status | ETA |
|---|-----------|----------|---------|----------|--------|-----|
| 1 | **Scale-aware schema v1.0** | Complete spec | Framework defined, 80% drafted | ████████░░ 80% | 🟡 Near Complete | 6h |
| 2 | **Baseline weeks** | 4+ weeks data | Night 1: 3/8 samples | ██░░░░░░░░ 20% | 🟡 In Progress | 3 weeks |
| 3 | **Spike/rejected history** | ≥5 candidates | 5 found (Batch 1) | ██████░░░░ 60% | 🟢 Target Met (buffer for 8-10) | 12h |
| 4 | **Challenger family/OQS** | ≥3 candidates | 0 identified | ░░░░░░░░░░ 0% | 🔴 Not Started | Week 2-3 |

---

## Detailed Status

### 1. Scale-Aware Schema v1.0 (80%)

**Completed**:
- [x] Problem statement (scale vs structure conflation)
- [x] Dimension 1: Scale-normalized CWCI metric
- [x] Dimension 2: Seed-stratified analysis
- [x] Dimension 3: Time-resolved comparison
- [x] Dimension 4: Cross-scale baseline requirement

**Remaining**:
- [ ] Formal specification document
- [ ] Implementation guide
- [ ] Validation protocol

**Blockers**: None  
**Action**: Complete spec by 06:00 UTC

---

### 2. Baseline Weeks (20%)

**Accumulated**:
| Scale | Required | Current | Gap |
|-------|----------|---------|-----|
| 4x | 10 samples | 3 complete | 7 |
| 6x | 10 samples | 3 complete | 7 |

**Schedule**:
- Night 1 (tonight): 8 samples per scale
- Night 2 (tomorrow): +1 per scale
- Night 3 (day after): +1 per scale
- **Total by Night 3**: 10 per scale ✅

**Blockers**: None  
**Action**: Continue Night 1 sampling

---

### 3. Spike/Rejected History (60% → 100%)

**Found (Batch 1: seeds 100-150)**:
| ID | Seed | Pattern | Classification |
|----|------|---------|----------------|
| SSP_001 | 103 | oscillating_decay | fragile_combination |
| SSP_002 | 117 | steady_collapse | coordination_overload |
| SSP_003 | 128 | sustained_low | broadcast_saturation |
| SSP_004 | 134 | unstable_recovery | population_volatility |
| SSP_005 | 142 | gradual_decline | fragile_combination |

**In Progress**:
- Batch 2 (seeds 151-200): Expected +3-5 candidates

**Target**: 5-8 total  
**Status**: ✅ **MINIMUM MET** (continuing for buffer)

---

### 4. Challenger Family/OQS (0%)

**Required**: ≥3 real OQS candidates  
**Current**: 0 identified  
**Status**: 🔴 **CRITICAL GAP**

**Sources to Explore**:
| Source | Expected Count | Priority |
|--------|----------------|----------|
| P2.5 rejected history | 2-3 | P0 |
| OctopusLike variants | 1-2 | P1 |
| External benchmarks | 1 | P2 |

**Blockers**: Awaiting schema completion  
**Action**: Start identification 06:00 UTC

---

## Restart Readiness Assessment

### Current State: NOT READY

| Condition | Met? |
|-----------|------|
| Schema v1.0 | ❌ (80%, 6h remaining) |
| Baseline weeks | ❌ (20%, 3 weeks remaining) |
| Spike history | ✅ (60%, target met with buffer) |
| Challenger family | ❌ (0%, Week 2-3) |

**Overall**: 1/4 conditions met, 1 near-complete, 2 in progress

### Path to Restart

**Scenario A: Fast Track (Optimistic)**
- Schema: Complete in 6h
- Baseline: Compress to 1 week (intensive sampling)
- Challenger: Parallel identification
- **ETA**: 1 week (aggressive)

**Scenario B: Standard Pace (Realistic)**
- Schema: Complete in 6h
- Baseline: Full 3 weeks
- Challenger: Week 2-3
- **ETA**: 3 weeks (original plan)

**Scenario C: Extended (Pessimistic)**
- Challenger identification fails
- Baseline insufficient variance
- **ETA**: 4+ weeks or NO-GO

---

## Recommended Decision Framework

| Checkpoint | Date | Decision Criteria |
|------------|------|-------------------|
| Schema Complete | 2026-03-13 06:00 | If schema ready, continue; else delay |
| Week 1 Review | 2026-03-20 | If baseline ≥6 samples + challenger ≥1, continue |
| Week 2 Review | 2026-03-27 | If baseline ≥8 samples + challenger ≥2, continue |
| Final Decision | 2026-04-03 | GO if all 4 conditions met, else NO-GO |

---

## One-Line Summary

> **P2.6 remains paused, but restart conditions are being manufactured: 1/4 met, 1 at 80%, baseline 20% and growing, challenger 0% and starting.**

---

**Scorecard Owner**: Jordan Smith  
**Review Frequency**: Daily during campaign  
**Next Update**: 2026-03-13 06:00 UTC
