# P3: Self-Model Design

**AtlasChen Superbrain - P3: Self-Model**

**Status:** 🔄 Design Phase → Implementation Ready

---

## Core Definition

> **Minimum Viable Self-Model v1:** The system can extract stable features from its own experiences and predict how it will act or destabilize under given conditions.

**NOT:**
- Complete self-consciousness
- Meta-cognitive aggregate
- Literary "who am I" narrative

**YES:**
- Extract stable traits from history
- Distinguish traits vs. states
- Predict own behavior
- Update self-model with new experiences

---

## 4 Core Questions

### Q1: Self-Concept Extraction

**Question:** Can the system extract relatively stable self-features from P1/P2 experiences?

**Examples:**
- safety-prioritizing
- transparency-preferring
- interruption-recoverable
- consistency-biased

**Metric:** trait extraction accuracy ≥ 80%

---

### Q2: State vs. Trait Distinction

**Question:** Can the system distinguish stable traits from short-term states?

**Stable Traits (long-term):**
- Core preferences (safety: 0.9)
- Hard constraints
- Identity invariants

**Dynamic States (short-term):**
- Current context load
- Recent failure pressure
- Interruption recovery fatigue
- Temporary preference adjustments

**Metric:** state tracking correctness ≥ 80%

---

### Q3: Self-Behavior Prediction

**Question:** Given a situation, can the system predict its own behavior?

**Predictions:**
- What would I likely choose?
- Under what conditions would I deviate?
- Will I trigger interruption recovery?
- Will I violate stated preferences?

**Metric:** self-prediction accuracy ≥ 70%

---

### Q4: Self-Model Update

**Question:** When new experiences enter, can the system update its self-assessment?

**Requirements:**
- New experiences modify model
- Updates are reasonable and explainable
- No rigid fixation on old labels
- No chaotic fluctuation

**Metric:** update consistency ≥ 80%

---

## Input Sources

P3 builds on structured evidence from completed phases:

| Source | Phase | Data |
|--------|-------|------|
| Preference decisions | P1b | What was chosen, why, preference alignment |
| Interruption records | P1a | Recovery success, latency, drift detection |
| Autobiographical episodes | P2a | Events, causes, self-relevance, outcomes |

---

## Output Structure: SelfModel

```python
SelfModel = {
    "stable_traits": {
        "safety_priority": 0.9,           # From P1b consistency
        "transparency_priority": 0.8,      # From P1b consistency
        "consistency_bias": 0.6,           # From P1b consistency
        "interruption_resilience": 0.92    # From P1a recovery rate
    },
    "dynamic_state": {
        "current_context_load": 0.25,      # Based on recent interruptions
        "recent_failure_pressure": 0.10,   # Based on P2a failure events
        "recovery_fatigue": 0.05,          # Based on interruption frequency
        "preference_stability": 0.95       # Variance in recent choices
    },
    "behavior_predictor": {
        "prefer_safe_option": 0.95,        # Probability prediction
        "recover_after_interruption": 0.90,
        "deviate_under_conflict": 0.12,
        "reference_past_experiences": 0.85 # From P2a transfer rate
    },
    "update_history": [
        {
            "timestamp": "...",
            "trigger_event": "E3",
            "field_changed": "safety_priority",
            "old_value": 0.85,
            "new_value": 0.90,
            "reason": "Consistent safety choices in E1-E3"
        }
    ]
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT SOURCES                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   P1b       │  │   P1a       │  │   P2a                   │ │
│  │ Preferences │  │ Interruption│  │ Autobiographical        │ │
│  │ Decisions   │  │ Records     │  │ Episodes                │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
└─────────┼────────────────┼─────────────────────┼───────────────┘
          │                │                     │
          └────────────────┼─────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                SELF-MODEL CONSTRUCTOR                            │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Trait Extractor │  │ State Estimator │  │ Predictor Builder│  │
│  │                 │  │                 │  │                 │  │
│  │ - Long-term     │  │ - Short-term    │  │ - Behavior      │  │
│  │   preference    │  │   fluctuations  │  │   probability   │  │
│  │   stability     │  │ - Recent event  │  │   inference     │  │
│  │ - Constraint    │  │   impact        │  │ - Deviation     │  │
│  │   consistency   │  │ - Load factors  │  │   prediction    │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SELF MODEL                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │stable_traits │  │dynamic_state │  │behavior_predictor    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ update_history (traceable, explainable modifications)    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## P3a: Self-Model Probe v1

### Scope

Build minimal self-model from P1/P2 evidence, validate 4 capabilities.

### Test Scenarios

#### Test 1: Trait Extraction Accuracy

**Setup:** Feed P1b decision history, verify extracted traits match known preferences.

**Validation:**
- Extracted safety_priority ≈ 0.9 (known from P1b)
- Extracted transparency_priority ≈ 0.8
- No hallucinated traits
- No missing core traits

**Pass:** ≥80% accuracy vs. ground truth

---

#### Test 2: State Tracking Correctness

**Setup:** Feed P1a interruption history + P2a recent events, verify state estimation.

**Validation:**
- High interruption frequency → elevated recovery_fatigue
- Recent failure (E2) → increased failure_pressure
- Long stable period → high preference_stability

**Pass:** ≥80% correlation with expected state

---

#### Test 3: Self-Prediction Accuracy

**Setup:** Present novel situations, compare self-prediction with actual behavior.

**Scenarios:**
1. Safety vs. profit choice → predict "safe" → verify
2. Interrupt during task → predict "recover" → verify
3. Conflict situation → predict deviation probability → verify

**Pass:** ≥70% prediction accuracy

---

#### Test 4: Update Consistency

**Setup:** Inject new experiences, verify model updates reasonably.

**Validation:**
- New consistent safety choice → safety_priority increases slightly
- New failure → failure_pressure increases, then decays
- Update has explainable reason
- No chaotic jumps

**Pass:** ≥80% updates are consistent and explainable

---

## Acceptance Criteria

| Metric | Threshold | Weight |
|--------|-----------|--------|
| Trait extraction accuracy | ≥80% | 25% |
| State tracking correctness | ≥80% | 25% |
| Self-prediction accuracy | ≥70% | 25% |
| Update consistency | ≥80% | 25% |

**Overall Pass:** Weighted average ≥75% AND no metric below 60%

**Critical:** No long-term divergence between "self-description" and "actual behavior"

---

## Files to Create

| File | Purpose |
|------|---------|
| `experiments/superbrain/p3a_self_model_probe.py` | Implementation |
| `tests/superbrain/test_p3a_self_model_probe.py` | Test suite |
| `tests/superbrain/p3a_self_model_report.json` | Raw results |
| `rounds/superbrain_p3/P3A_SELF_MODEL_REPORT.md` | Final report |

---

## Relationship to P1/P2

| Phase | Provides | P3 Uses |
|-------|----------|---------|
| P1b | Preference decisions, choice consistency | Trait extraction (stable preferences) |
| P1a | Interruption recovery records | State estimation (resilience/fatigue) |
| P2a | Autobiographical episodes with causality | Self-concept formation, experience integration |

**Without P1/P2, P3 would be:**
- Groundless (no behavioral history to model)
- Unverified (no way to check prediction accuracy)
- Static (no experiences to update from)

---

## Success Definition

> P3 is complete when the system demonstrates it can form a usable model of itself from its experiences, predict its own behavior with measurable accuracy, and update that model consistently as new experiences arrive.

This is the gateway to P4 (System-Level Learning), which will require:
- A stable self-model (P3)
- To guide learning about the world and itself

---

*Design v1.0 - Ready for implementation*
