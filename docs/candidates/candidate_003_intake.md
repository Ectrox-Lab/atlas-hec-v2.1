# Candidate 003: Mixed-Reality Reputation Ledger

**Status**: REFINE_FIRST  
**Date**: 2026-03-10  
**Risk**: High  
**Readiness**: Low (mechanism unclear)  

---

## 1. Intake Memo (1 Page)

### Core Hypothesis
Agents develop social self-models when their "reputation" is:
- Observable by others (ledger)
- Tied to their own action history
- Persistent across interactions

The visibility of reputational state creates feedback loop where agents internalize their social identity.

### Minimal Mechanism
**CURRENT STATE: UNCLEAR**

Key ambiguity:
- Is this about external reputation tracking?
- Or about internal self-model formation?
- How is "mixed-reality" different from standard reputation?

### Required State Variables (TENTATIVE)
```python
{
  "reputation_ledger": Dict[agent_id, ReputationScore],
  "self_reputation": ReputationScore,  # Agent's view of own reputation
  "observed_reputation": Dict[agent_id, ReputationScore],  # What others show
  "social_self_model": {
    "predicted_reputation_trajectory": Vector,
    "identity_consistency": float  # Do my actions match my reputation?
  }
}
```

### Minimal Experimental Environment
**UNCLEAR**: Need to distinguish:
- Scenario A: Reputation visible to all (standard)
- Scenario B: Reputation visible only to self (internal)
- Scenario C: Reputation partially visible (mixed-reality?)

### Minimal Falsification Condition
- **Fail**: Ledger visibility only changes surface strategy, not internal self-model
- **Fail**: Removing visibility eliminates all "identity" effects immediately
- **Fail**: Effect is purely external monitoring (no internal representation)

### Most Likely Illusion
This candidate risks being:
- **External reputation game** with no self-model
- **Social pressure effect** rather than identity formation
- **Observability artifact** that disappears when monitoring stops

**Critical Question**: What is the "internal" representation that forms?

---

## 2. Minimal Mechanism Spec (DRAFT - NEEDS REFINEMENT)

### Agent Definition
```
Agent: ReputationAwareAgent
- State: (own_reputation, observed_others_reputation, history)
- Policy: π(action | reputation_state, social_self_model)

UNCLEAR: What is the mechanism of "social_self_model" formation?
```

### Environment Definition
```
Environment: ReputationArena
- Public ledger: visible to all
- Private ledger: visible only to self
- Mixed ledger: partially visible (what does this mean?)

UNCLEAR: What is "mixed-reality" aspect?
```

### Key Feedback Loop (UNCLEAR)
```
1. ACT: Choose action
2. UPDATE_LEDGER: Reputation scores updated
3. OBSERVE: See (some) reputations
4. UPDATE_SELF_MODEL: ???

CRITICAL GAP: How does observation → internal representation?
```

### Self-Model Variable (UNDEFINED)
```python
# What exactly represents "social self"?
# Is it:
# - predicted_reputation?
# - desired_reputation?
# - identity_consistency metric?
# - something else?

NEED: Concrete mathematical definition
```

### Refinement Questions
1. Is "mixed-reality" about physical+virtual interaction or information asymmetry?
2. What distinguishes this from standard reputation mechanisms?
3. What is the internal variable that constitutes "social self-model"?

---

## 3. Minimal Experiment Design (TENTATIVE)

### Experiment A: Visibility Effect

**Setup**:
- Multi-agent interaction
- Reputation ledger with varying visibility

**Conditions**:
- **Full visibility**: All see all reputations
- **Self-only**: Agents see only own reputation
- **None**: No reputation information

**Metrics**:
```python
{
  "strategy_consistency": entropy over time,
  "reputation_prediction_accuracy": P(r_t | r_{t-1}...),
  "social_coherence": correlation of own actions with reputation
}
```

**UNCLEAR**: What counts as "self-model" vs "reactive strategy"?

### Experiment B: Ledger Persistence

**Setup**:
- Temporarily remove ledger visibility
- Measure if behavior changes

**Question**: Does "identity" persist without external monitoring?

**Success**: Behavior remains consistent (internalized self-model)
**Fail**: Behavior reverts immediately (external pressure only)

### Experiment C: Reputation Manipulation

**Setup**:
- Manipulate agent's perceived reputation
- Measure action adaptation

**Question**: Does agent act to maintain consistent social identity?

**UNCLEAR**: How to measure "identity maintenance" vs "reputation optimization"?

---

## 4. Falsification Checklist (INCOMPLETE)

### Definite Fail Conditions (TO BE REFINED)

| # | Condition | If True |
|---|-----------|---------|
| F1 | Visibility removal eliminates all consistency | Pure external monitoring |
| F2 | Effect is just "behave well when watched" | No self-model formation |
| F3 | No internal variable predicts reputation changes | No internal representation |
| F4 | Agents don't show distress at reputation mismatch | No identity investment |

### Critical Unknowns
- What is the "self" in "social self-model"?
- How is this different from standard RL with state?
- What would "identity persistence" look like?

### Warning Signs
- Effect disappears when ledger is hidden (pure external)
- Requires complex social reasoning to show any effect
- Indistinguishable from standard reputation game theory

---

## 5. Priority Decision

**Decision**: REFINE_FIRST

**Rationale**:
- Core mechanism is ambiguous
- "Mixed-reality" concept not clearly defined
- Risk of being external reputation effect only
- Internal representation mechanism unclear

**Required Refinement**:
1. **Define "mixed-reality"**: Is this about information asymmetry, physical/virtual interaction, or something else?
2. **Specify internal mechanism**: What variable constitutes "social self-model"?
3. **Distinguish from standard reputation**: What new phenomenon does this capture?
4. **Concrete falsification**: What specific internal metric would disprove self-model formation?

**Refinement Path**:
- Week 1: Clarify mechanism with TINA
- Week 2: Define internal variables
- Week 3: Design minimal experiment
- Week 4: Decide BUILD_NOW vs REJECT

**Possible Outcomes**:
1. **Refine to BUILD**: Clarify mechanism, distinct from standard reputation
2. **Merge with 001**: If mechanism is essentially identity tokens in social context
3. **REJECT**: If cannot distinguish from external monitoring effect

---

## Refinement Questions for TINA

1. What does "mixed-reality" specifically mean in this context?
2. What is the internal representation that forms? (Mathematical definition)
3. How is this different from agent 001's identity tokens in multi-agent setting?
4. What would "social self-model persistence" look like experimentally?
5. Can you provide concrete example of behavior showing "social self" vs "reputation optimization"?

---

**Sign-off**: Needs mechanism clarification before implementation
