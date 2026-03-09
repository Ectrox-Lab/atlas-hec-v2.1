# Candidate 001: Multi-Agent Meta-Game Identity Tokens

**Status**: BUILD_NOW  
**Date**: 2026-03-10  
**Risk**: Medium  
**Readiness**: High (minor refinement needed)  

---

## 1. Intake Memo (1 Page)

### Core Hypothesis
Multi-agent systems develop persistent self-models when individual agents carry "identity tokens" that:
- Track their own action history
- Are observable by other agents
- Create selection pressure for consistent (identifiable) behavior

The token serves as an anchor for self-representation and other-model formation.

### Minimal Mechanism
- **Agents**: N identical agents in repeated game
- **Identity Token**: Observable but non-transferable agent ID + action history summary
- **Game**: Mixture of cooperation and deception scenarios
- **Learning**: Policy that depends on own token state and observed other tokens

### Required State Variables
```python
{
  "self_token": {
    "agent_id": int,
    "action_history": List[Action],
    "strategy_fingerprint": Vector[traits]
  },
  "other_tokens": Dict[agent_id, Observation],
  "self_model": {
    "predicted_own_actions": Distribution[Action],
    "consistency_score": float  # How predictable am I?
  },
  "other_models": Dict[agent_id, PredictedStrategy],
  "reputation_state": Dict[agent_id, TrustScore]
}
```

### Minimal Experimental Environment
- **Game**: Repeated social dilemmas (Prisoner's Dilemma, Stag Hunt, Chicken)
- **Episodes**: 100-1000 rounds with same partners
- **Observations**: Actions + tokens of all agents
- **Metrics**:
  - Self-model stability (consistency of self-prediction)
  - Strategy persistence (action distribution stability)
  - Other-model accuracy (prediction of others)

### Minimal Falsification Condition
- **Fail**: Removing tokens doesn't degrade self-model stability
- **Fail**: Tokens only improve cooperation rate without forming self-representation
- **Fail**: Agents don't show consistent strategy when tokens are visible

### Most Likely Illusion
Treating token as "identity" when it's actually:
- Just a coordination device (no self-model formation)
- External reputation tracker (no internal representation)
- Memory aid (no emergent identity)

---

## 2. Minimal Mechanism Spec

### Agent Definition
```
Agent: TokenAwareAgent
- State: (own_token, observed_other_tokens, memory)
- Policy: π(action | own_token, history, other_models)
- Learning: RL update based on game rewards + consistency bonus
```

### Environment Definition
```
Environment: MetaGameArena
- Population: N agents, repeated pairing
- Games: {Prisoner's Dilemma, Stag Hunt, Chicken} sampled each episode
- Token visibility: All agents observe all tokens (or subset)
- Reward: Game payoff + consistency bonus (optional)
```

### Key Feedback Loop
```
1. OBSERVE: See other agents' tokens and last actions
2. PREDICT: Use other_models to predict their actions
3. ACT: Choose action based on own_token + predictions
4. UPDATE_TOKEN: Append action to own_token.history
5. UPDATE_MODELS: 
   - self_model ← consistency(own_token.history)
   - other_models[partner] ← observed behavior
6. LEARN: Policy gradient on (game_reward + λ*consistency)
```

### Self-Model Variable
```python
# self_model.consistency_score = coherence of own action history
# self_model.predicted_own_actions = policy(own_token) distribution
# Identity emerges when consistency_score > threshold AND stable
```

### Emergence Criteria
- **Appears**: 
  - Self-prediction accuracy > baseline (random/no-token)
  - Strategy consistent across episodes with same partner
  - Other-model accuracy improves over time
- **Absent**: 
  - Actions independent of token
  - No other-model formation
  - Purely reactive (no history dependence)

---

## 3. Minimal Experiment Design

### Experiment A: Token Effect on Self-Model Stability

**Setup**:
- Population of 10 agents
- 500 rounds, random pairing
- Mixed games (PD, Stag, Chicken)

**Conditions**:
- **With tokens**: Full mechanism
- **Without tokens**: Agents see only current actions, no IDs

**Metrics**:
```python
{
  "self_prediction_accuracy": P(a_t | history, own_token),
  "strategy_entropy": -Σ p(a) log p(a) over episode,
  "partner_prediction_accuracy": P(partner_a | other_model),
  "cooperation_rate": fraction of cooperate actions
}
```

**Success**: With-tokens shows higher self-prediction + strategy consistency

### Experiment B: Token Deception Resistance

**Setup**:
- Introduce "deceiver" agents who randomize strategy
- Measure if honest agents maintain self-model

**Metrics**:
- Self-model stability under deception pressure
- Identification of deceivers (model accuracy drop)

**Success**: Self-model persists despite deception attempts

### Experiment C: Transfer to New Partners

**Setup**:
- Train with partner set A
- Test with partner set B

**Metrics**:
- Strategy consistency across partner change
- Speed of new other-model formation

**Success**: Positive transfer (uses learned self-strategy)

---

## 4. Falsification Checklist

### Definite Fail Conditions

| # | Condition | If True |
|---|-----------|---------|
| F1 | Removing tokens doesn't affect self-model metrics | Token is not identity anchor |
| F2 | Tokens improve cooperation but not self-prediction | External coordination only |
| F3 | Strategy consistency doesn't correlate with token visibility | Token irrelevant to identity |
| F4 | Other-model accuracy doesn't improve over time | No learning of others |
| F5 | Agents with tokens are equally exploitable as without | No self-model benefit for protection |

### Warning Signs
- Self-model converges to "always cooperate" or "always defect" (trivial)
- Requires hand-crafted consistency bonus to show any effect
- Performance improvement is purely coordination (no prediction)

### Success Criteria
- [ ] Δ self-prediction accuracy > 25% with tokens
- [ ] Strategy entropy lower (more consistent) with tokens
- [ ] Other-model accuracy improves > 20% over episodes
- [ ] Performance advantage persists against novel partners

---

## 5. Priority Decision

**Decision**: BUILD_NOW

**Rationale**:
- Clear game-theoretic mechanism
- Extensible from simple to complex
- Well-defined metrics
- Falsifiable through token removal

**Refinement Needed**:
- Define exact "consistency score" computation
- Specify token information structure (what history is included)
- Choose RL algorithm (Q-learning, policy gradient, or evolutionary)

**Implementation Path**:
1. Week 1: Basic multi-agent PD with tokens
2. Week 2: Add token history + learning
3. Week 3: Extend to game mixtures
4. Week 4: Measure self-model metrics

**Fallback if Fails**:
- Simplify to 2-agent repeated game
- Try different token structures
- Test if issue is credit assignment vs identity

---

**Sign-off**: Ready with minor refinement on token structure
