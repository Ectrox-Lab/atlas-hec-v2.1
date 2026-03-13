# Candidate 001: Multi-Agent Consistency Markers

**Status**: REVISE_FIRST → BUILD_NOW (after compliance update)  
**Date**: 2026-03-10  
**Risk**: Medium  
**Readiness**: High (terminology updated)  

---

## 1. Intake Memo (1 Page)

### Core Hypothesis
Multi-agent systems develop persistent behavioral patterns when individual agents carry **consistency markers** that:
- Are observable by other agents (public signal)
- Change slowly (low bandwidth)
- Create selection pressure for coherent (identifiable) behavior

The marker acts as a **generic prior** for partner predictions, not as content storage.

### Minimal Mechanism
- **Agents**: N agents in repeated game
- **Consistency Marker**: Observable agent ID + slow-varying consistency score (<= 32 bits total)
- **Game**: Mixture of cooperation and deception scenarios
- **Learning**: Policy influenced by marker visibility and partner predictions

### Required State Variables (COMPLIANT)
```python
{
  "consistency_marker": {
    "agent_id": 8 bits,              # Fixed identifier
    "coherence_score": 8 bits,       # How consistent is behavior? (slow update)
    "behavioral_bias": 16 bits       # Generic prior direction (not specific content)
  },
  "observed_markers": Dict[agent_id, ConsistencyScore],  # Partner coherence only
  "prior_prediction": {
    "expected_partner_coherence": float,  # Generic expectation, not specific strategy
    "consistency_pressure": float         # Selection pressure for coherence
  }
}
```

**Bandwidth Check**: <= 32 bits per observation ✅  
**Timescale**: Marker updates every 10+ ticks (10x separation from actions) ✅

### Minimal Experimental Environment
- **Game**: Repeated social dilemmas (Prisoner's Dilemma, Stag Hunt, Chicken)
- **Episodes**: 100-1000 rounds with same partners
- **Observations**: Current actions + slow markers (not history)
- **Metrics**:
  - Behavioral coherence (entropy of action distribution)
  - Partner prediction accuracy (generic, not specific)
  - Marker consistency stability

### Minimal Falsification Condition
- **Fail**: Removing markers doesn't degrade coherence metrics
- **Fail**: Markers only improve cooperation rate without creating consistency pressure
- **Fail**: Agents don't show behavioral coherence when markers are visible

### Most Likely Illusion
Treating marker as "identity" when it's actually:
- Just a coordination device (no consistency pressure)
- External pressure only (no internal prior)
- Pure reputation tracking (not generic bias)

---

## 2. Minimal Mechanism Spec (COMPLIANT)

### Agent Definition
```
Agent: ConsistencyMarkerAgent
- State: (own_marker, observed_partner_coherence, prior_bias)
- Policy: π(action | own_marker, prior_prediction, game_state)
- Learning: RL with consistency bonus (slow signal, not history)
```

### Environment Definition
```
Environment: MarkerGameArena
- Population: N agents, repeated pairing
- Games: {Prisoner's Dilemma, Stag Hunt, Chicken} sampled each episode
- Marker visibility: All agents observe all markers (bandwidth-limited)
- Marker update: Every 10 ticks (10x slower than actions)
- Reward: Game payoff + λ*consistency_bonus (slow feedback)
```

### Key Feedback Loop (COMPLIANT)
```
1. OBSERVE: See partner markers (<= 32 bits each)
   - agent_id (fixed)
   - coherence_score (slow update)
   - NO action history
   - NO specific strategy content

2. PREDICT: Use generic prior from marker
   - High coherence → expect consistent behavior
   - Low coherence → expect variable behavior
   - NOT predicting specific actions

3. ACT: Choose action based on game + prior

4. UPDATE_MARKER (every 10 ticks):
   - coherence_score ← variance(recent_actions)
   - Slow update maintains 10x timescale separation

5. LEARN: Policy gradient on (game_reward + λ*consistency)
   - Consistency bonus from slow marker feedback
   - NOT from specific action rewards
```

### Generic Prior Variable (COMPLIANT)
```python
# prior_prediction.coherence_expectation = f(observed_marker.coherence_score)
# This is a GENERIC prior about partner consistency, NOT specific content

# Consistency emerges when:
# - Agents maintain stable coherence scores
# - Partners use these as priors for predictions
# - Selection pressure favors coherent agents
```

### Emergence Criteria
- **Appears**: 
  - Behavioral coherence (low action entropy) > baseline
  - Partner prediction accuracy (generic) > random
  - Coherence scores stabilize over time
- **Absent**: 
  - Actions independent of marker visibility
  - No coherence pressure
  - Purely reactive (no prior formation)

---

## 3. Minimal Experiment Design

### Experiment A: Marker Effect on Coherence

**Setup**:
- Population of 10 agents
- 500 rounds, random pairing
- Mixed games (PD, Stag, Chicken)

**Conditions**:
- **With markers**: Full mechanism (<= 32 bits, 10x timescale)
- **Without markers**: Agents see only current actions

**Metrics**:
```python
{
  "behavioral_coherence": 1 / entropy(action_distribution),
  "partner_prediction_accuracy": P(coherence | marker),
  "coherence_stability": variance(coherence_score) over time,
  "cooperation_rate": fraction of cooperate actions
}
```

**Success**: With-markers shows higher coherence + better generic prediction

### Experiment B: Bandwidth Constraint Test

**Setup**:
- Vary marker information content: 8 bits vs 32 bits vs 128 bits

**Prediction**: 
- 8-32 bits: Effective (within PriorChannel constraint)
- 128 bits: Violates bandwidth, should NOT show additional benefit

**Verification**: PriorChannel bandwidth limit is meaningful constraint

### Experiment C: Timescale Separation Test

**Setup**:
- Vary marker update frequency: every tick vs every 10 ticks vs every 100 ticks

**Prediction**:
- Every tick (1x): No separation, may not work
- Every 10 ticks (10x): Optimal (default)
- Every 100 ticks (100x): Too slow, reduced effect

**Verification**: 10x timescale separation is optimal

---

## 4. Falsification Checklist (COMPLIANT)

### Definite Fail Conditions

| # | Condition | If True |
|---|-----------|---------|
| F1 | Removing markers doesn't affect coherence metrics | Marker is not consistency anchor |
| F2 | Markers improve cooperation but not coherence | External pressure only |
| F3 | Coherence doesn't correlate with marker visibility | Marker irrelevant |
| F4 | High-bandwidth markers (>32 bits) work better | Violates PriorChannel constraint |
| F5 | Fast-updating markers (every tick) work better | Violates timescale separation |

### PriorChannel Compliance Tests

| Test | Expected | Violation |
|------|----------|-----------|
| Bandwidth <= 32 bits | Effect saturates at 32 bits | Continues improving beyond 32 bits |
| Timescale >= 10x | Effect optimal at 10x | Best at 1x (no separation) |
| Generic prior | Predicts coherence, not actions | Predicts specific strategies |

### Success Criteria
- [ ] Δ behavioral coherence > 25% with markers
- [ ] Partner coherence prediction > baseline
- [ ] Effect saturates at ~32 bits (bandwidth limit)
- [ ] Effect optimal at ~10x timescale separation
- [ ] NO specific action prediction (generic only)

---

## 5. Priority Decision

**Decision**: BUILD_NOW (after terminology compliance update)

**Rationale**:
- Mechanism uses generic prior (not content storage) ✅
- Complies with bandwidth constraint (<= 32 bits) ✅
- Complies with timescale separation (10x) ✅
- Clear falsification conditions ✅

**Implementation Path**:
1. Week 1: Basic multi-agent PD with markers (32-bit, 10x update)
2. Week 2: Add consistency learning
3. Week 3: Test bandwidth and timescale constraints
4. Week 4: Measure coherence and generic prediction

**Fallback if Fails**:
- Check if bandwidth limit is real constraint
- Test different timescale separations
- Verify generic vs specific prediction

---

## Terminology Compliance Notes

### Changes Made (from v0.1 to v0.2)

| Old (Non-compliant) | New (Compliant) | Rationale |
|---------------------|-----------------|-----------|
| "identity token" | "consistency marker" | Avoids "identity" baggage |
| "action history" | "coherence score" | Removes content storage implication |
| "token history" | "slow coherence update" | Emphasizes timescale separation |
| "strategy fingerprint" | "behavioral bias" | Generic, not specific content |
| "self_model" | "prior_prediction" | Mechanism, not entity |
| "memory" | "slow signal" | Removes storage implication |

### Bandwidth Verification

```
Marker structure:
- agent_id: 8 bits (fixed)
- coherence_score: 8 bits (0-255)
- behavioral_bias: 16 bits (generic direction)
Total: 32 bits ✅
```

### Timescale Verification

```
Agent actions: Every tick (fast)
Marker updates: Every 10 ticks (slow)
Separation: 10x ✅
```

### Generic Prior Verification

```
Marker provides:
- Coherence expectation (generic)
- NOT specific action predictions
- NOT historical content
- NOT strategy transfer
```

---

**Sign-off**: Compliant with FROZEN_STATE_v1  
**Reviewer**: Super Brain Group  
**Date**: 2026-03-10
