# Week 1 Sprint - Immediate Execution

**Date**: 2026-03-10  
**Status**: EXECUTE NOW  
**Resource Split**: 002 (70%) / 001 (30%)  
**Gate**: Kill/Continue at Week 1 end  

---

## Resource Allocation

| Track | Priority | Resources | Goal |
|-------|----------|-----------|------|
| **002 Soft Robot** | PRIMARY | 70% | Full prototype + early signal |
| **001 Markers** | SECONDARY | 30% | Skeleton + mechanism validation |

---

## Track 1: 002 Soft Robot (Primary)

### Week 1 Deliverables

#### Day 1-2: Environment Setup
```
[ ] Create 2D deformable mesh (N=16 nodes, 4x4 grid)
[ ] Implement pressure physics (springs + damping)
[ ] Add boundary conditions (container walls)
[ ] Visualization: mesh deformation render
```

#### Day 3-4: Sensor + Feedback
```
[ ] Add pressure/strain sensors at each node
[ ] Implement proprioceptive feedback channel
[ ] Create baseline controller (reactive, no prediction)
[ ] Test: mesh stability under perturbation
```

#### Day 5-7: Predictive Model
```
[ ] Implement simple predictive model (linear: P̂(t+1) = W·P(t) + b)
[ ] Add prediction error computation
[ ] Implement homeostatic controller (minimize ||P - P_setpoint||)
[ ] Test: prediction accuracy over time
```

### Week 1 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mesh stability | No crashes | 1000 ticks without failure |
| Feedback effect | Visible | Prediction error < reactive error |
| Recovery | Measurable | Return to setpoint < 100 ticks |

### Week 1 Kill/Continue Gate

**CONTINUE if ANY:**
- [ ] With-feedback shows lower prediction error than without
- [ ] System recovers from perturbations (visibly)
- [ ] Self-boundary discrimination > 60% accuracy

**KILL if ALL false:**
- [ ] No difference with/without feedback
- [ ] No recovery behavior observed
- [ ] System unstable regardless of feedback

**Kill Action**: Simplify to 1D spring, or pivot to different mechanism

---

## Track 2: 001 Consistency Markers (Secondary)

### Week 1 Deliverables (Skeleton Only)

#### Day 1-3: Marker Structure
```
[ ] Define 32-bit marker format:
    - bits 0-7: agent_id (8 bits)
    - bits 8-15: coherence_score (8 bits, 0-255)
    - bits 16-31: behavioral_bias (16 bits, encoded strategy)
[ ] Implement marker encoding/decoding
[ ] Add marker visibility (observable by other agents)
```

#### Day 4-5: Update Mechanism
```
[ ] Implement 10x timescale separation:
    - Agent acts every tick
    - Marker updates every 10 ticks
[ ] Coherence score computation:
    - variance(action_history) over window
    - higher consistency = lower variance = higher score
[ ] Test: marker updates correctly, not every tick
```

#### Day 6-7: Minimal Environment
```
[ ] Create 4-agent repeated PD environment
[ ] Basic agents: random, tit-for-tat, defector
[ ] Add marker-observing agents
[ ] Test: agents can see each other's markers
```

### Week 1 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Marker format | Frozen | 32-bit structure implemented |
| Timescale | Correct | Updates every 10 ticks only |
| Coherence | Computable | Score changes based on behavior variance |
| Environment | Runs | 4-agent PD completes without crash |

### Week 1 Kill/Continue Gate

**CONTINUE if ANY:**
- [ ] Marker coherence score correlates with behavior consistency
- [ ] 10x timescale separation working (not updating every tick)
- [ ] Agents can use markers to predict partner behavior (generic, not specific)

**KILL if ALL false:**
- [ ] Coherence score random / unrelated to behavior
- [ ] Marker updates violate timescale constraint
- [ ] No prediction improvement from markers

**Kill Action**: Revisit mechanism design, or merge with 002 if body-based self is primary

---

## Daily Sync (5 minutes)

### 002 Track
- Mesh stable?
- Feedback working?
- Any blockers?

### 001 Track
- Marker encoding done?
- Timescale working?
- Environment running?

### Cross-Track
- Shared learnings
- Resource reallocation if needed

---

## Week 1 End Review (Friday)

### 002 Review Questions
1. Does feedback improve prediction? (Yes/No)
2. Does system recover from perturbations? (Yes/No)
3. Is self-boundary measurable? (Yes/No)

**Decision**: Continue (if ≥2 Yes) / Kill (if ≤1 Yes)

### 001 Review Questions
1. Does coherence score correlate with behavior? (Yes/No)
2. Is 10x timescale working? (Yes/No)
3. Do markers improve partner prediction? (Yes/No)

**Decision**: Continue (if ≥2 Yes) / Kill (if ≤1 Yes)

---

## Risk Mitigation

### 002 Risks
| Risk | Mitigation |
|------|------------|
| Physics unstable | Reduce mesh size, increase damping |
| Prediction doesn't help | Try simpler linear model first |
| No self-boundary signal | Check sensor placement |

### 001 Risks
| Risk | Mitigation |
|------|------------|
| Coherence score not meaningful | Try different variance windows |
| Marker not used by agents | Ensure agents can observe it |
| Too complex for Week 1 | Reduce to 2 agents |

---

## Success Scenario (Week 1)

### 002
- Mesh physics working
- Feedback shows visible effect
- Ready for formal experiments Week 2

### 001
- Marker structure frozen
- Timescale constraint validated
- Ready for multi-agent experiments Week 2

### Decision
Both CONTINUE to Week 2 full experiments

---

## Failure Scenario (Week 1)

### 002
- No feedback effect observed
- System unstable

**Action**: Kill 002, move 001 to primary (100% resources)

### 001
- Marker irrelevant to behavior
- Timescale constraint violated

**Action**: Kill 001, focus 002 as sole candidate

### Both Fail
**Action**: Re-evaluate PriorChannel assumptions, consider alternative mechanisms

---

## Sign-off

| Track | Lead | Status | Week 1 Goal |
|-------|------|--------|-------------|
| 002 Soft Robot | TBD | READY | Feedback effect visible |
| 001 Markers | TBD | READY | Marker mechanism working |

**Start**: Immediate  
**Week 1 Review**: 2026-03-17  
**Decision**: Continue / Kill per gates above

---

**Sprint Version**: 1.0  
**Resource Model**: 70/30 split  
**Risk Model**: Early kill/continue gates  
**Next**: Execute Day 1 tasks immediately
