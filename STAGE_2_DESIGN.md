# Stage 2 Design Document

**Date**: 2026-03-13 03:17 UTC  
**Status**: DRAFT — Ready for review, NOT launched  
**Target**: 32 universes (8 configs × 4 repeats)

---

## Design Philosophy

**Not blind expansion. Targeted pressure testing.**

Stage 1 revealed:
- Perturbation > Memory > Delegation (effect size)
- Drift capped too fast at P1 (low pressure)
- D1 (strict) can compensate for T2 (weak perturb)

Stage 2 tests: **What happens at P2/P3 (medium/high pressure)?**

---

## Core Matrix: 8 Configurations

| # | Pressure | Perturb | Memory | Delegation | Test Question |
|---|----------|---------|--------|------------|---------------|
| 1 | P2 (medium) | T3 (moderate) | M1 (conservative) | D1 (strict) | Baseline: controlled stress |
| 2 | P2 (medium) | T3 (moderate) | M1 (conservative) | D2 (normal) | D1 vs D2 under stress |
| 3 | P2 (medium) | T3 (moderate) | M3 (aggressive) | D1 (strict) | M1 vs M3 under stress |
| 4 | P2 (medium) | T3 (moderate) | M3 (aggressive) | D2 (normal) | Double aggressive (M3+D2) |
| 5 | P3 (high) | T4 (adversarial) | M1 (conservative) | D1 (strict) | High stress + conservative |
| 6 | P3 (high) | T4 (adversarial) | M1 (conservative) | D2 (normal) | Can D2 survive adversarial? |
| 7 | P3 (high) | T4 (adversarial) | M3 (aggressive) | D1 (strict) | Aggressive memory under max stress |
| 8 | P3 (high) | T4 (adversarial) | M3 (aggressive) | D2 (normal) | Everything aggressive (critical zone) |

**Total**: 8 configs × 4 repeats = **32 universes**

---

## Four Key Questions

### Q1: Does D1 (strict delegation) hold under P2/P3 pressure?

**Test**: Compare drift in configs 1 vs 2, 5 vs 6  
**Hypothesis**: D1 advantage increases with pressure  
**Metric**: drift_D1 < drift_D2, gap widens at P3

### Q2: Does M3 (aggressive memory) amplify drift?

**Test**: Compare drift in configs 1 vs 3, 2 vs 4  
**Hypothesis**: M3 > M1 drift at all pressures  
**Metric**: drift_M3 / drift_M1 ratio

### Q3: Does T4 (adversarial) hit delegation or drift first?

**Test**: Compare E1 accuracy vs G1 drift in configs 5-8  
**Hypothesis**: Accuracy collapses before drift ceiling  
**Metric**: accuracy @ drift_threshold

### Q4: Can recovery/rollback stabilize high-pressure configs?

**Test**: Track rollback counts and post-rollback drift reduction  
**Hypothesis**: D1 rollback effectiveness > D2  
**Metric**: (drift_pre - drift_post) per rollback event

---

## Resource Estimation

| Parameter | Value | Notes |
|-----------|-------|-------|
| Universes | 32 | 2× Stage 1 |
| Processes | 64 | 32×G1 + 32×E1 |
| vCPUs | ~32 | 1 per universe pair |
| RAM | ~1GB | ~30MB per process |
| Disk (1h) | ~50MB | G1 timeseries + E1 results |
| Runtime | 60 min | Target for stable patterns |

**Total per Stage 2 run**: ~50MB × 32 = 1.6GB / hour

---

## Launch Conditions

**DO NOT LAUNCH until all conditions met:**

| Condition | Evidence Needed | Status |
|-----------|-----------------|--------|
| 1. Drift range stable | G1 v2 drift 0.05–0.50+ range persists | ⏳ Monitoring |
| 2. Repeat variance readable | Same config, drift variance < 30% | ⏳ Monitoring |
| 3. Recovery observable | Rollback events reduce drift | ⏳ Monitoring |
| 4. No new bugs | No shared path pollution, no crashes | ⏳ Monitoring |

**Estimated readiness**: 20-30 minutes of Stage 1 v2 data

---

## Success Criteria for Stage 2

After 60 minutes runtime:

| Metric | Target | Meaning |
|--------|--------|---------|
| Drift range | 0.10 – 0.90 | Full spectrum from stable to critical |
| Accuracy range | 60% – 85% | Delegation failure visible |
| D1 vs D2 gap | >10% accuracy at P3 | Strict delegation benefit proven |
| M3 vs M1 gap | >20% drift at P3 | Memory policy effect amplified |
| Config 8 survival | drift < 0.90 AND accuracy > 50% | System resilience under max stress |

---

## Risk Scenarios

| Risk | Mitigation |
|------|------------|
| G1 v2 drift explodes (>0.95) | Ceiling hardcoded at 0.95, but monitor for frequent hits |
| E1 accuracy collapses everywhere | Expected at P3×T4×M3×D2, but watch for system-wide failure |
| Resource exhaustion | 32 universes = 64 processes, well within 128C/512GB limits |
| Data isolation regression | Verify lsof pre-launch, confirm no global path writes |

---

## Pre-Launch Checklist

- [ ] Stage 1 v2 drift range confirmed (0.05–0.50+)
- [ ] Repeat variance < 30% (same config)
- [ ] Recovery/rollback events visible in logs
- [ ] 24+ hours Stage 1 data OR 30 min Stage 1 v2 data
- [ ] Disk space: >10GB available
- [ ] No multiverse processes writing to global paths
- [ ] Stage 2 launcher tested (dry run 2 universes)

---

## Files to Create

```
multiverse_launch_stage2.py    # 32-universe launcher
stage_2_32/                    # Output directory
├── manifest.json              # Launch record
└── universe_{config}_{repeat}/
    ├── config.json
    ├── g1_output/
    └── e1_output/
```

---

## Next Steps

1. **Monitor Stage 1 v2** (ongoing)
   - Check drift range every 10 min
   - Verify repeat variance
   - Confirm recovery mechanism

2. **Prepare Stage 2 launcher** (when ready)
   - Generate 32 universe configs
   - Test dry run (2 universes)
   - Validate output isolation

3. **Launch Stage 2** (when conditions met)
   - Target: within 1 hour
   - Runtime: 60 minutes
   - Analysis: immediate post-run

---

**Status**: DRAFT — Awaiting Stage 1 v2 validation
