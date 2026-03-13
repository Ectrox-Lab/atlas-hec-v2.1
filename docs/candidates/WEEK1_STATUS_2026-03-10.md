# Week 1 Status - 2026-03-10 (Tuesday)

**Resource Split**: 002 (50%) / 001 (50%) - Adjusted from 70/30  
**Next Review**: Friday 2026-03-17  
**Commits**: `3f1c0fa` (launch) → `007e7dc` (refinement)

---

## Track 1: 001 Consistency Markers

### Status: 🟡 REFINE (Early signal detected, tightening validation)

### Progress
| Component | Status | Notes |
|-----------|--------|-------|
| 32-bit marker encoding | ✅ Frozen | agent_id + coherence + bias |
| 10x timescale | ✅ Fixed | Validation now passes |
| Coherence score | ✅ Working | CV-based computation |
| 4-agent PD env | ✅ Running | Marker-based vs TitForTat |

### Early Signals (Preliminary)
| Metric | With Markers | Without | Delta |
|--------|--------------|---------|-------|
| Consistency | 0.751 | 0.502 | **+49.6%** |
| Cooperation | 0.65 | 1.00 | -35% |
| Timescale valid | true | N/A | ✅ |

### Timescale Comparison
| Interval | Consistency | Cooperation |
|----------|-------------|-------------|
| 1x | 0.625 | 0.60 |
| 5x | 0.606 | 0.60 |
| **10x** | **0.500** | **0.68** |
| 20x | 0.502 | 0.75 |

**Issue**: 1x (every tick) shows highest consistency - contradicts 10x hypothesis

### Ablation Test
| Condition | Consistency | Cooperation |
|-----------|-------------|-------------|
| Full (markers visible) | 0.500 | 0.68 |
| Ablated (invisible) | 0.502 | 1.00 |
| **Delta** | **-0.002** | **-0.32** |

**Issue**: Ablation delta near zero - effect may be environmental noise

### Critical Questions for Friday
1. ✅ Timescale validation fixed
2. ❓ Is 10x actually optimal? (Data suggests 1x better)
3. ❓ Is marker effect real? (Ablation inconclusive)
4. ❓ Self-model or coordination? (Cannot distinguish yet)

### Next Actions (Wed-Thu)
- [ ] Run 10-trial stability test
- [ ] Debug why 1x > 10x for consistency
- [ ] Try different agent strategy mixes
- [ ] Check if cooperation rate inversion is stable

---

## Track 2: 002 Soft Robot

### Status: 🔴 CONDITION RESET (Mechanism alive, conditions need tuning)

### Progress
| Component | Status | Notes |
|-----------|--------|-------|
| 2D mesh physics | ✅ Stable | Pressure + spring system |
| Multiple perturbations | ✅ Added | 5 types implemented |
| Micro-perturbations | ✅ Active | Every 10 ticks |
| Predictor | ✅ Running | Linear model learning |

### Current Results
| Condition | Stability | Recovery | Notes |
|-----------|-----------|----------|-------|
| Predictive | 0.368 | -0.0s | No recovery detected |
| Reactive | N/A | N/A | Baseline |
| No control | 0.368 | -0.0s | Same as predictive |

**Key Change**: Stability dropped from 0.964 → 0.368 (stronger challenge activated)

### Implemented Perturbations
| Type | Description | Status |
|------|-------------|--------|
| VelocityImpulse | Strong push + noise | ✅ |
| BoundaryDisplacement | Side compression | ✅ |
| LocalCompression | Single-side push | ✅ |
| RandomNoise | Random forces all nodes | ✅ |
| SustainedWind | Continuous force + micro | ✅ |

### Critical Issues
1. **No recovery detection**: Drift threshold may be wrong
2. **No condition separation**: All conditions same stability
3. **Feedback not helping**: Either too weak or task wrong

### Next Actions (Wed-Thu)
- [ ] Test each perturbation type individually
- [ ] Fix recovery detection (centroid drift calculation)
- [ ] Increase predictor learning rate
- [ ] Add feedback dropout test
- [ ] Try boundary recovery task (return to specific shape)

---

## Cross-Track Analysis

### Resource Adjustment Rationale
| Factor | 001 | 002 |
|--------|-----|-----|
| Early signal | ✅ Consistency diff | ❌ No diff yet |
| Mechanism clarity | Moderate | High |
| Validation complexity | High (ablation needed) | Medium (condition tuning) |
| Risk level | Lower | Higher |

**Decision**: 50/50 split until Friday

### Friday Gate Decision Matrix

| Scenario | 001 Decision | 002 Decision | Resource Shift |
|----------|--------------|--------------|----------------|
| 001✓ 002✓ | CONTINUE | CONTINUE | Stay 50/50 |
| 001✓ 002✗ | CONTINUE | REFINE/PIVOT | 70/30 → 001 |
| 001✗ 002✓ | REFINE/KILL | CONTINUE | 30/70 → 002 |
| 001✗ 002✗ | KILL | KILL | Re-evaluate PriorChannel |

---

## Risk Assessment

### 001 Risks
| Risk | Probability | Mitigation |
|------|-------------|------------|
| Effect is coordination-only | Medium | Add more self-model proxy metrics |
| 10x timescale wrong | High | Test 1x/5x/20x thoroughly |
| Ablation fails Friday | Medium | Prepare fallback mechanisms |

### 002 Risks
| Risk | Probability | Mitigation |
|------|-------------|------------|
| Task fundamentally too easy | Medium | Add shape maintenance objective |
| Prediction not useful | Low | Try nonlinear predictor |
| Feedback delay issue | Medium | Check sensor-controller loop |
| Mechanism weak | Low | Simplify to 1D spring if needed |

---

## Deliverables for Friday

### Required
- [ ] 001: 10-trial stability data
- [ ] 001: Timescale comparison (all 4)
- [ ] 001: Ablation results
- [ ] 002: Perturbation sweep results
- [ ] 002: Recovery curve data
- [ ] Both: Gate Review Template filled

### Optional
- [ ] 001: Alternative agent strategies
- [ ] 002: Shape maintenance task
- [ ] Both: Visualization of dynamics

---

## Key Metrics to Watch

### 001
```
Target: consistency_delta > 0.1 (stable across trials)
Target: ablation_delta > 0.05 (marker causes effect)
Target: 10x_optimal = true (timescale validated)
```

### 002
```
Target: predictive_recovery < reactive_recovery * 0.8
Target: predictive_stability > no_control * 1.2
Target: feedback_dropout shows degradation
```

---

## Conclusion

**001**: Early signal exists but needs tightening. Risk is false positive from coordination effects.

**002**: Not dead, just challenged. Physics working, need right task to show feedback value.

**Overall**: Both tracks alive but need focused Wed-Thu experimentation to reach Friday decision threshold.

**Next Update**: Wednesday EOD checkpoint
