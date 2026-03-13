# Implementation Plan - BUILD_NOW Phase

**Date**: 2026-03-10  
**Status**: READY TO EXECUTE  
**Priority**: 002 first, 001 parallel  

---

## Execution Order

### Priority 1: candidate_002 (Soft Robot)

**Why First**: Cleanest mechanism, minimal PriorChannel interaction, direct falsification

**Week 1-2: Minimum Prototype**
- 2D deformable mesh (N=10-20 nodes)
- Pressure/strain sensors at each node
- Basic predictive model (linear or simple MLP)
- Homeostatic setpoint target

**Week 3-4: Core Experiments**
- Experiment A: Boundary discrimination
- Experiment B: Prediction error recovery
- Experiment C: Body map stability

**Success Criteria**:
- [ ] Self-boundary accuracy > 70% with feedback vs < 50% without
- [ ] Recovery time < 50 ticks with model vs > 100 ticks without
- [ ] Body map stability metric > 0.8

**Falsification Check**:
- [ ] FAIL if removing feedback doesn't degrade performance
- [ ] FAIL if prediction loop doesn't affect stability

---

### Priority 2: candidate_001 v0.2 (Consistency Markers)

**Why Second**: Good mechanism but more complex (multi-agent)

**Week 1-2: Minimum Prototype**
- 10 agents, repeated PD/Stag/Chicken
- Consistency markers (32 bits: 8 ID + 8 coherence + 16 bias)
- Marker update every 10 ticks (10x separation)
- Generic prior prediction (not specific action)

**Week 3-4: Core Experiments**
- Experiment A: Marker effect on coherence
- Experiment B: Bandwidth constraint test (8 vs 32 vs 128 bits)
- Experiment C: Timescale separation test (1x vs 10x vs 100x)

**Success Criteria**:
- [ ] Behavioral coherence +25% with markers
- [ ] Effect saturates at ~32 bits (bandwidth limit)
- [ ] Effect optimal at ~10x timescale
- [ ] NO specific action prediction (generic only)

**Falsification Check**:
- [ ] FAIL if removing markers doesn't affect coherence
- [ ] FAIL if high-bandwidth markers work better
- [ ] FAIL if markers improve coordination but not coherence

---

## Parallel Execution

Both can run in parallel (different team members):
- 002: Physics/simulation focused
- 001: Multi-agent/game theory focused

**Weekly Sync**: Share progress, blockers, early results

---

## Resource Requirements

| Candidate | Compute | Time | Skills |
|-----------|---------|------|--------|
| 002 Soft Robot | Medium (physics sim) | 4 weeks | Physics, ML, Rust |
| 001 Markers | Low (game theory) | 4 weeks | RL, Game Theory, Rust |

---

## Success Definition (BUILD_NOW complete)

### candidate_002
- ✅ Prototype runs
- ✅ At least 2/3 experiments show positive effect
- ✅ No falsification conditions triggered
- ✅ Report: `RESULTS_002.md`

### candidate_001 v0.2
- ✅ Prototype runs
- ✅ Coherence effect > 25%
- ✅ Bandwidth/timescale constraints validated
- ✅ No falsification conditions triggered
- ✅ Report: `RESULTS_001.md`

---

## If Fails

### candidate_002 fail
- Simplify to 1D spring system
- Try different prediction architectures
- Check if problem is embodiment vs learning

### candidate_001 fail
- Check if bandwidth limit is real constraint
- Test different timescale separations
- Verify generic vs specific prediction

---

## Deliverables

| Week | Deliverable |
|------|-------------|
| 1 | Prototype code (both) |
| 2 | Initial results (both) |
| 3 | Core experiments complete |
| 4 | Final reports + decision |

---

**Start Date**: Immediate  
**End Date**: 4 weeks  
**Decision Point**: BUILD / REFINE / REJECT per candidate
