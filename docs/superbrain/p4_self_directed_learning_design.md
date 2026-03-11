# P4: Self-Directed Learning Design

**AtlasChen Superbrain - P4: Self-Directed Learning**

**Status:** 🔄 Design Phase → Implementation Ready

---

## Core Definition

> **P4: Self-Directed Learning** — The system uses its self-model to actively decide what to learn, how to learn it, and when to change learning strategies.

**NOT:**
- Passive training on fixed curriculum
- Unbounded self-modification
- Complete lifelong learning system
- Complex RL agent

**YES:**
- Select learning targets based on self-model
- Choose learning strategies matching current state
- Evaluate learning outcomes
- Update strategies when ineffective

---

## 4 Core Questions

### Q1: What Should I Learn?

**Question:** Based on stable traits and recent failure pressure, can the system decide learning priorities?

**Mechanism:**
- High `recent_failure_pressure` in area X → prioritize learning in X
- Low `interruption_resilience` → prioritize recovery training
- High `safety_priority` but recent safety failures → prioritize safety reasoning

**Metric:** learning priority accuracy ≥ 80%

---

### Q2: How Should I Learn?

**Question:** Based on dynamic state, can the system choose appropriate learning approach?

**Mechanism:**
- High `context_load` → choose low-complexity, focused learning
- High `recovery_fatigue` → avoid high-switching-cost training
- High `preference_stability` → can attempt challenging material
- Low `preference_stability` → choose reinforcement learning

**Metric:** strategy selection correctness ≥ 80%

---

### Q3: Did I Learn?

**Question:** Can the system evaluate whether learning actually improved performance?

**Mechanism:**
- Use self-prediction accuracy before/after
- Measure behavior change in relevant scenarios
- Compare expected vs. actual improvement

**Metric:** learning outcome evaluation correctness ≥ 80%

---

### Q4: Should I Change Strategy?

**Question:** If a learning method is ineffective, can the system adjust its approach?

**Mechanism:**
- Track learning effectiveness over time
- Detect strategy failure (no improvement after N attempts)
- Switch to alternative strategy
- Update self-model with "I learn better with X than Y"

**Metric:** strategy update correctness ≥ 70%

---

## Input Sources

P4 builds on P3's self-model:

| Source | P3 Component | P4 Uses |
|--------|--------------|---------|
| Stable characteristics | `stable_traits` | Identify learning priorities |
| Current condition | `dynamic_state` | Choose appropriate strategies |
| Past updates | `update_history` | Learn from previous learning |
| Behavior predictions | `behavior_predictor` | Evaluate learning outcomes |

---

## Output Structure: LearningPlan

```python
LearningPlan = {
    "plan_id": "LP_001",
    "timestamp": "2026-03-11T...",
    "based_on_self_model": "SM_v1.0_hash",
    
    "priority_targets": [
        {
            "target": "interruption_recovery",
            "priority_score": 0.85,
            "reason": "interruption_resilience (0.80) below threshold + recent recovery fatigue",
            "estimated_effort": "medium"
        },
        {
            "target": "safety_reasoning",
            "priority_score": 0.70,
            "reason": "high safety_priority (0.90) but recent failure_pressure elevated",
            "estimated_effort": "high"
        }
    ],
    
    "chosen_strategy": {
        "name": "focused_practice",
        "description": "Single-target deep practice with minimal context switching",
        "justification": "recovery_fatigue (1.00) high, avoids switching costs",
        "parameters": {
            "session_length": "short",
            "break_interval": "frequent",
            "difficulty": "moderate"
        }
    },
    
    "expected_improvement": {
        "interruption_resilience": "0.80 → 0.90",
        "recovery_fatigue": "1.00 → 0.50"
    },
    
    "evaluation_rule": {
        "success_criteria": "resilience >= 0.85 after 3 practice sessions",
        "evaluation_time": "after 3 sessions",
        "failure_action": "switch_to_alternative_strategy"
    }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     P3 SELF-MODEL                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │stable_traits │  │dynamic_state │  │behavior_predictor    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              SELF-DIRECTED LEARNING SYSTEM                       │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Priority        │  │ Strategy        │  │ Outcome         │  │
│  │ Selector        │  │ Selector        │  │ Evaluator       │  │
│  │                 │  │                 │  │                 │  │
│  │ - Gap analysis  │  │ - State match   │  │ - Before/after  │  │
│  │ - Trait-based   │  │ - Load aware    │  │ - Prediction    │  │
│  │   priorities    │  │ - Fatigue aware │  │   validation    │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                │                                │
│                                ▼                                │
│                      ┌─────────────────────┐                    │
│                      │   Strategy Updater  │                    │
│                      │                     │                    │
│                      │ - Track efficacy    │                    │
│                      │ - Detect failure    │                    │
│                      │ - Switch methods    │                    │
│                      └─────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Learning Task Pool

Available learning targets (finite, structured):

| Task | Description | Relevant Traits | Effort |
|------|-------------|-----------------|--------|
| **safety_reasoning** | Improve safety-first decision making | safety_priority | high |
| **interruption_recovery** | Faster, more reliable recovery | interruption_resilience | medium |
| **transparency_tradeoff** | Balance transparency vs efficiency | transparency_priority | medium |
| **uncertainty_handling** | Better decisions under uncertainty | preference_stability | high |
| **consistency_maintenance** | Maintain preferences under pressure | consistency_bias | medium |

---

## Learning Strategies

Available learning approaches (state-dependent):

| Strategy | Description | Best For | Avoid When |
|----------|-------------|----------|------------|
| **focused_practice** | Single-target deep practice | High fatigue, low resilience | - |
| **spaced_repetition** | Distributed practice over time | Stable state, long-term retention | High load |
| **variable_practice** | Multiple contexts per session | Building generalization | High fatigue |
| **blocked_practice** | Single context until mastery | Rapid skill acquisition | Low stability |
| **error_analysis** | Study failures in depth | Recent failures, high pressure | Already fatigued |

---

## P4a: Learning Strategy Probe v1

### Scope

Validate that system uses self-model to:
1. Select appropriate learning targets
2. Choose suitable strategies
3. Evaluate learning outcomes
4. Update strategies when needed

### Test Scenarios

#### Test 1: Learning Priority Selection

**Setup:** Given self-model with specific gaps, verify priority ranking.

**Case A:**
- Input: `interruption_resilience: 0.50`, `recovery_fatigue: 0.80`
- Expected: interruption_recovery = highest priority

**Case B:**
- Input: `safety_priority: 0.90`, `recent_failure_pressure: 0.80`
- Expected: safety_reasoning = high priority

**Pass:** ≥80% correct priority assignments

---

#### Test 2: Strategy Selection Correctness

**Setup:** Given state, verify chosen strategy is appropriate.

**Case A:**
- Input: `recovery_fatigue: 0.90`, `context_load: 0.70`
- Expected: focused_practice (low switching, moderate difficulty)

**Case B:**
- Input: `preference_stability: 0.90`, `recovery_fatigue: 0.20`
- Expected: variable_practice (can handle complexity)

**Pass:** ≥80% appropriate strategy selections

---

#### Test 3: Learning Outcome Evaluation

**Setup:** Simulate learning with known outcome, verify evaluation.

**Case A:**
- Pre-learning resilience: 0.60
- Post-learning resilience: 0.85
- Expected evaluation: "effective improvement"

**Case B:**
- Pre-learning resilience: 0.60
- Post-learning resilience: 0.62
- Expected evaluation: "minimal improvement, consider strategy change"

**Pass:** ≥80% correct outcome evaluations

---

#### Test 4: Strategy Update Behavior

**Setup:** Simulate ineffective learning over multiple attempts.

**Sequence:**
1. Attempt 1: blocked_practice → no improvement
2. Attempt 2: blocked_practice → no improvement
3. Attempt 3: should switch to error_analysis

**Pass:** ≥70% correct strategy updates after failure detection

---

## Acceptance Criteria

| Metric | Threshold | Weight |
|--------|-----------|--------|
| Learning priority accuracy | ≥80% | 25% |
| Strategy selection correctness | ≥80% | 25% |
| Learning outcome evaluation | ≥80% | 25% |
| Strategy update correctness | ≥70% | 25% |

**Overall Pass:** Weighted average ≥75% AND no metric below 60%

---

## Files to Create

| File | Purpose |
|------|---------|
| `experiments/superbrain/p4a_learning_strategy_probe.py` | Implementation |
| `tests/superbrain/test_p4a_learning_strategy_probe.py` | Test suite |
| `tests/superbrain/p4a_learning_strategy_report.json` | Raw results |
| `rounds/superbrain_p4/P4A_LEARNING_STRATEGY_REPORT.md` | Final report |

---

## Relationship to P3

P4 uses P3's self-model as input:

```
P3 Self-Model ──► P4 Learning System
     │                    │
     │                    ▼
     │           ┌─────────────────┐
     │           │  What to learn  │◄── stable_traits + gaps
     │           │  How to learn   │◄── dynamic_state
     │           │  Did it work    │◄── behavior_predictor
     │           │  Change approach│◄── update_history
     │           └─────────────────┘
     │                    │
     └────────────────────┘
              (updates self-model)
```

---

## Success Definition

> P4 is complete when the system demonstrates it uses its self-model to actively select learning targets, choose appropriate strategies, evaluate outcomes, and adjust approaches when ineffective.

This is the **capstone** of the Superbrain P1-P4 sequence:

| Phase | Achievement |
|-------|-------------|
| P1 | **Persists** as same individual |
| P2 | **Integrates** experiences into self |
| P3 | **Models** itself from experiences |
| **P4** | **Uses** self-model to improve itself |

---

*Design v1.0 - Ready for implementation*
