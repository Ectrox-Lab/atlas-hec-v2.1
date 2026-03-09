# Week 1 Gate Review Template

**Date**: 2026-03-17 (Friday)  
**Reviewers**: TBD  
**Decision**: CONTINUE / REFINE / KILL per track  

---

## Track 1: 001 Consistency Markers

### Current Status: 🟡 UNDER REVIEW

### Executive Summary
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Consistency (with markers) | ___ | > 0.6 | ⬜ |
| Consistency (without markers) | ___ | < 0.6 | ⬜ |
| Effect size | ___ | > 10% | ⬜ |
| Timescale validation | ___ | Must pass | ⬜ |

### Question 1: Marker Effect Stability
**Test**: Run 10 trials each of with/without markers

| Trial | With | Without | Delta |
|-------|------|---------|-------|
| 1 | | | |
| 2 | | | |
| ... | | | |
| 10 | | | |
| **Mean** | | | |
| **Std** | | | |

**Decision**: ⬜ Stable (>70% trials show same direction)  
**Decision**: ⬜ Unstable

### Question 2: Timescale Sensitivity
**Test**: Compare 1x / 5x / 10x / 20x update rates

| Timescale | Consistency Score | Notes |
|-----------|-------------------|-------|
| 1x (every tick) | | Should be lower |
| 5x | | |
| **10x** | | **Target: optimal** |
| 20x | | May be too slow |

**Decision**: ⬜ 10x is optimal  
**Decision**: ⬜ Other scale better  
**Decision**: ⬜ No clear pattern

### Question 3: Ablation Test
**Test**: Same environment, agents simply cannot see markers

| Condition | Cooperation Rate | Consistency | Source of Difference |
|-----------|------------------|-------------|---------------------|
| Full (marker visible) | | | |
| Ablated (marker invisible) | | | |
| Delta | | | |

**Key Check**: Is difference from marker itself, or just environment randomness?

**Decision**: ⬜ Marker causes difference  
**Decision**: ⬜ Environment/noise causes difference  
**Decision**: ⬜ Inconclusive

### Question 4: Mechanism vs Coordination
**Critical Distinction**: Is this self-model or just coordination aid?

| Evidence for Self-Model | Evidence for Coordination Only |
|-------------------------|-------------------------------|
| | |
| | |

**Decision**: ⬜ Self-model signal  
**Decision**: ⬜ Coordination only  
**Decision**: ⬜ Cannot distinguish yet

### 001 Final Decision
```
[ ] CONTINUE to Week 2 (≥2 of 4 questions positive)
[ ] REFINE (1 of 4 positive, need more validation)
[ ] KILL (0 of 4 positive, mechanism not working)
```

**If CONTINUE**: Week 2 plan: _________________  
**If REFINE**: Focus area: _________________  
**If KILL**: Reason: _________________  

---

## Track 2: 002 Soft Robot

### Current Status: 🔴 CONDITION RESET

### Executive Summary
| Condition | Stability | Recovery Time | Prediction Error |
|-----------|-----------|---------------|------------------|
| Predictive Feedback | ___ | ___ | ___ |
| Reactive Only | ___ | ___ | N/A |
| No Control | ___ | ___ | N/A |

### Question 1: Perturbation Sensitivity
**Test**: Strong perturbation (boundary displacement, local compression)

| Perturbation Type | Predictive Recovery | Reactive Recovery | Delta |
|-------------------|---------------------|-------------------|-------|
| Boundary displacement | ___s | ___s | ___ |
| Local compression | ___s | ___s | ___ |
| Random noise injection | ___s | ___s | ___ |

**Decision**: ⬜ Feedback shows advantage  
**Decision**: ⬜ No difference  
**Decision**: ⬜ Reactive better (unexpected)

### Question 2: Task Difficulty Gradient
**Test**: Easy → Medium → Hard tasks

| Difficulty | Task Description | Feedback Advantage |
|------------|------------------|-------------------|
| Easy | Maintain shape | ___ |
| Medium | Recovery from perturbation | ___ |
| Hard | Dynamic shape tracking | ___ |

**Decision**: ⬜ Advantage emerges at higher difficulty  
**Decision**: ⬜ Advantage constant across difficulty  
**Decision**: ⬜ No advantage at any difficulty

### Question 3: Feedback Dropout
**Test**: Randomly disable feedback during run

| Metric | Feedback ON | Feedback OFF | Dropout Impact |
|--------|-------------|--------------|----------------|
| Stability | | | |
| Recovery | | | |
| Energy efficiency | | | |

**Decision**: ⬜ Clear on/off difference  
**Decision**: ⬜ Gradual degradation  
**Decision**: ⬜ No impact (feedback not used)

### Question 4: Mechanism Diagnosis
If no difference observed, root cause:

```
[ ] Task too easy (no need for prediction)
[ ] Perturbation too weak (reactive sufficient)
[ ] Sensor information insufficient
[ ] Controller gain mis-tuned
[ ] Prediction horizon too short
[ ] Mechanism fundamentally weak
```

### 002 Final Decision
```
[ ] CONTINUE to Week 2 (clear advantage demonstrated)
[ ] REFINE_ENVIRONMENT (adjust conditions, retest)
[ ] PIVOT_MECHANISM (major controller redesign)
[ ] KILL (mechanism not viable)
```

**If CONTINUE**: Week 2 focus: _________________  
**If REFINE**: Specific changes: _________________  
**If PIVOT**: New approach: _________________  
**If KILL**: Learning: _________________  

---

## Cross-Track Comparison

### Resource Reallocation Recommendation

| Scenario | 001 Allocation | 002 Allocation | Rationale |
|----------|---------------|----------------|-----------|
| 001✓ 002✓ | 50% | 50% | Both viable, parallel development |
| 001✓ 002✗ | 80% | 20% | Focus on proven mechanism |
| 001✗ 002✓ | 20% | 80% | Focus on proven mechanism |
| 001✗ 002✗ | 0% | 0% | Both failed, re-evaluate approach |
| 001? 002? | 50% | 50% | Both unclear, need more data |

**Current Recommendation**: _________________  
**Next Review**: _________________  

---

## Strategic Implications

### For PriorChannel Architecture
```
If 001 succeeds: Multi-agent self-model is viable path
If 002 succeeds: Embodied self-model is viable path
If both succeed: Two independent validation routes
If both fail: PriorChannel may need redesign
```

### For TINA Integration
```
Winning candidate will be integrated into:
- Bio-world simulation
- PriorChannel parameter sweep
- Creative tree experiments
```

---

## Action Items

| ID | Action | Owner | Due |
|----|--------|-------|-----|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

**Review Completed**: _________________  
**Next Steps Approved**: _________________  
