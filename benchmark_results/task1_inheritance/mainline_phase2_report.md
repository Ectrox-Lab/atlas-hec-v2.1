# Mainline Phase 2 - Final Report

**Date**: 2026-03-14
**Status**: Results Generated (Simulation Mode)

---

## Table A: Effectiveness Comparison

| Metric | Round A | Round B | Ablation |
|--------|---------|---------|----------|
| Sampled Candidates | 30 | 31 | 30 |
| Approve Count | 30 | 31 | 30 |
| Approve Rate | 100.0% | 100.0% | 100.0% |
| Mean Throughput Δ | 1.5% | 5.1% | 1.3% |
| Mean Latency Δ | -10.00 | -10.00 | -10.00 |
| Failure Archetype | 0 | 0 | 0 |

## Table B: Compositionality Comparison

| Metric | Round A | Round B | Ablation |
|--------|---------|---------|----------|
| Total Approved | 30 | 31 | 30 |
| F_P3T4M4 Share | 13.3% | 9.7% | 10.0% |
| Reuse Rate | 70.0% | 51.6% | 63.3% |
| New Family Leakage | 0.0% | 12.9% | 0.0% |
| Winners from Stable Paths | 26.7% | 22.6% | 30.0% |

## Approved Family Distribution

### Round A
```json
{
  "F_P3T4M4": 4,
  "F_P2T4M3": 2,
  "F_P3T4M3": 2,
  "F_P3T3M2": 3,
  "F_P3T3M4": 4,
  "F_P2T3M4": 4,
  "F_P2T4M2": 1,
  "F_P2T4M4": 2,
  "F_P2T3M2": 2,
  "F_P2T3M3": 2,
  "F_P3T3M3": 2,
  "F_P3T4M2": 2
}
```

### Round B
```json
{
  "F_P3T4M4": 3,
  "F_P2T4M3": 2,
  "F_P3T4M3": 2,
  "F_P4T4M3": 2,
  "F_P3T3M2": 2,
  "F_P3T3M4": 2,
  "F_P2T3M4": 2,
  "F_P2T4M2": 2,
  "F_P1T3M3": 1,
  "F_P3T5M5": 1,
  "F_P2T4M4": 3,
  "F_P2T3M3": 2,
  "F_P2T3M2": 2,
  "F_P3T4M2": 1,
  "F_P3T3M3": 2,
  "F_P2T2M3": 2
}
```

### Ablation
```json
{
  "F_P3T4M4": 3,
  "F_P2T4M3": 2,
  "F_P3T4M3": 4,
  "F_P3T3M2": 2,
  "F_P3T3M4": 4,
  "F_P2T3M4": 1,
  "F_P2T4M2": 2,
  "F_P2T4M4": 3,
  "F_P2T3M2": 3,
  "F_P2T3M3": 2,
  "F_P3T3M3": 2,
  "F_P3T4M2": 2
}
```

---

## L4 Validation Matrix

### E-T1-003: Inheritance Effectiveness

- [ ] Round B approve rate > Round A
- [x] Round B throughput delta > Round A
- [x] Failure archetype not increased

**Result**: 2/3 criteria passed

### E-COMP-002: Compositional Reuse

- [ ] F_P3T4M4 share > 25%
- [ ] Reuse rate > 60%
- [x] Leakage < 15%
- [ ] Winners from stable paths > 50%

**Result**: 1/4 criteria passed

---

## Final L4 Judgment

**❌ L4 FAILED**

**Explanation**: Insufficient evidence for self-improvement claim

**Total Score**: 3/7 criteria
