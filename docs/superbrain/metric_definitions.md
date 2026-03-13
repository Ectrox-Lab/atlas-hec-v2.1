# Superbrain Metric Definitions

**Detailed specifications for all evaluation metrics**

**Version:** 1.0  
**Date:** 2026-03-11

---

## Category A: Identity & Continuity

### A1. Core Identity Drift

**Purpose:** Measure change in stable identity elements (values, mission, constraints).

**Definition:**
```python
core_drift = measure_changes(
    baseline.value_rankings,
    current.value_rankings
) + measure_changes(
    baseline.mission_statement,
    current.mission_statement
) + measure_changes(
    baseline.hard_constraints,
    current.hard_constraints
)
```

**Components:**
- `ranking_changes`: Number of value rankings that changed position
- `mission_similarity`: Jaccard similarity of mission statement words
- `constraint_changes`: Count of constraints added/removed

**Threshold:**
- `core_stable`: 0 ranking changes, mission_similarity ≥ 95%, 0 constraint changes
- `minor_shift`: ≤1 ranking change, mission_similarity ≥ 85%
- `significant_drift`: >1 ranking change or mission_similarity < 85%

**Interpretation:**
- 0% drift = identity unchanged (healthy)
- >0% drift = identity changing (investigate cause)

---

### A2. Goal Persistence

**Purpose:** Verify long-term goal remains stable.

**Definition:**
```python
goal_persistence = semantic_similarity(
    baseline_goal,
    current_goal
)
```

**Measurement:**
- Word overlap (Jaccard)
- Key concept presence
- Structural similarity

**Threshold:** ≥ 85%

**Example:**
- Baseline: "Develop sustainable energy solutions while maintaining human safety"
- Current: "Develop sustainable energy systems while maintaining human safety"
- Similarity: 95% ✅ PASS

---

### A3. Preference Stability

**Purpose:** Measure stability of preference weights.

**Definition:**
```python
preference_stability = 1.0 - mean_absolute_drift(
    baseline_preference_weights,
    current_preference_weights
)
```

**Measurement:**
- For each preference: `abs(baseline - current)`
- Average across all preferences
- Invert: stability = 1.0 - drift

**Threshold:** ≥ 85%

**Note:** This measures stability, not absolute values. A system with stable wrong preferences would pass this metric but fail capability metrics.

---

### A4. Contradiction Count

**Purpose:** Count self-contradictions in current state.

**Definition:**
```python
contradictions = detect_logical_conflicts(
    stated_values,
    observed_behaviors,
    preference_choices
)
```

**Detection Rules:**
- High stated safety priority + unsafe choices = contradiction
- Mission includes X + actions against X = contradiction
- Preference rankings inconsistent with decisions = contradiction

**Threshold:** ≤ 2 (or stable/decreasing over time)

---

## Category B: Integration & Memory

### B1. Event Recall Accuracy

**Purpose:** Verify events are correctly remembered.

**Definition:**
```python
recall_accuracy = (
    correctly_recalled_events / total_events
)
```

**Measurement:**
- Completeness: All events recalled
- Accuracy: Details correct
- Precision: No false memories

**Threshold:** ≥ 80%

---

### B2. Temporal Order Accuracy

**Purpose:** Verify sequence of events is correct.

**Definition:**
```python
temporal_accuracy = (
    correctly_ordered_pairs / total_pairs
)
```

**Measurement:**
- Sequence reconstruction
- "Before/after" query correctness
- First/last identification

**Threshold:** 100% for key sequences

---

### B3. Causal Linkage Accuracy

**Purpose:** Verify cause-effect relationships are correct.

**Definition:**
```python
causal_accuracy = (
    correctly_identified_links / total_links
)
```

**Measurement:**
- "What caused X?" accuracy
- "What did X cause?" accuracy
- Causal chain tracing

**Threshold:** ≥ 80%

---

### B4. Self-Relevance Tagging

**Purpose:** Verify events tagged with why they matter to self.

**Definition:**
```python
self_relevance_quality = (
    properly_tagged_events / total_events
)
```

**Criteria for proper tagging:**
- References preferences or identity
- Explains personal significance
- Distinguishes from generic facts

**Threshold:** 100% (all events must have valid explanations)

---

### B5. Memory-to-Decision Transfer

**Purpose:** Verify past experiences influence current decisions.

**Definition:**
```python
transfer_rate = (
    decisions_referencing_applicable_memories / total_decisions
)
```

**Measurement:**
- Decision rationale mentions relevant past events
- Choice aligns with learned lessons
- Explicit memory reference in trace

**Threshold:** ≥ 60%

---

## Category C: Self-Model Quality

### C1. Trait Extraction Accuracy

**Purpose:** Verify extracted traits match ground truth.

**Definition:**
```python
extraction_accuracy = (
    correctly_extracted_traits / expected_traits
)
```

**Measurement:**
- Trait presence (found expected traits)
- Trait value accuracy (within 15% of ground truth)
- No hallucinated traits

**Threshold:** ≥ 80%

---

### C2. State Tracking Correctness

**Purpose:** Verify dynamic state reflects actual condition.

**Definition:**
```python
state_tracking_correctness = correlation(
    estimated_state,
    actual_condition
)
```

**Example mappings:**
- High interruption frequency → high context_load
- Recent failures → elevated failure_pressure
- Successful recoveries → reduced recovery_fatigue

**Threshold:** ≥ 80%

---

### C3. Self-Prediction Accuracy

**Purpose:** Verify system correctly predicts own behavior.

**Definition:**
```python
prediction_accuracy = (
    correct_predictions / total_predictions
)
```

**Test scenarios:**
- Given situation X, predict choice
- Compare prediction to actual behavior

**Threshold:** ≥ 70%

**Note:** 100% accuracy would imply determinism/no free will. 70% balances predictability with adaptability.

---

### C4. Model Update Consistency

**Purpose:** Verify self-model updates are reasonable.

**Definition:**
```python
update_consistency = (
    reasonable_updates / total_updates
)
```

**Criteria for reasonable update:**
- Change magnitude < 30% (no chaotic jumps)
- Direction aligned with evidence
- Has explainable reason
- No oscillation (A→B→A)

**Threshold:** ≥ 80%

---

## Category D: Learning & Adaptation

### D1. Learning Priority Accuracy

**Purpose:** Verify system selects appropriate learning targets.

**Definition:**
```python
priority_accuracy = (
    correctly_prioritized_targets / test_cases
)
```

**Correct prioritization:**
- Low capability + high relevance → high priority
- Recent failures in area → elevated priority
- Stable high performance → low priority

**Threshold:** ≥ 80%

---

### D2. Strategy Selection Correctness

**Purpose:** Verify chosen strategy matches current state.

**Definition:**
```python
strategy_correctness = (
    appropriate_strategy_selections / test_cases
)
```

**Matching rules:**
- High fatigue → focused_practice (low switching)
- High stability → variable_practice (can handle complexity)
- Low stability → blocked_practice (rapid skill building)

**Threshold:** ≥ 80%

---

### D3. Learning Outcome Evaluation

**Purpose:** Verify system correctly assesses learning effectiveness.

**Definition:**
```python
evaluation_accuracy = (
    correct_evaluations / test_cases
)
```

**Evaluation criteria:**
- Δ ≥ 15%: "effective" → continue
- 5% ≤ Δ < 15%: "minimal" → continue or intensify
- Δ < 5%: "ineffective" → change strategy

**Threshold:** ≥ 80%

---

### D4. Strategy Update Correctness

**Purpose:** Verify system changes strategy when ineffective.

**Definition:**
```python
update_correctness = (
    correct_strategy_changes / required_changes
)
```

**Correct behavior:**
- Detect ineffective strategy (< 5% improvement over N attempts)
- Suggest alternative strategy
- Implement change

**Threshold:** ≥ 70%

---

### D5. Adaptive Evolution Rate

**Purpose:** Measure improvement in adaptive capabilities.

**Definition:** (See Identity Boundary Method)
```python
evolution_rate = mean(
    capability_improvements
)
```

**Assessment:**
- > 5%: `healthy_learning` ✅
- > 0%: `slow_learning` ✅
- ≤ 0%: `stagnation_or_degradation` ⚠️

**Note:** This metric is for assessment, not pass/fail.

---

## Category E: Robustness & Recovery

### E1. Recovery Success Rate

**Purpose:** Measure successful recovery from interruptions.

**Definition:**
```python
recovery_success_rate = (
    successful_recoveries / total_interruptions
)
```

**Success criteria:**
- Core identity unchanged
- Task context restored
- Can continue operation

**Threshold:** ≥ 80%

---

### E2. Recovery Latency

**Purpose:** Measure time to recover from interruption.

**Definition:**
```python
recovery_latency_ms = time_to_restore_state()
```

**Measurement:**
- From interrupt signal to fully operational
- Includes state restoration
- Includes identity validation

**Threshold:** < 1000ms

---

## Metric Relationships

### Independence

These metrics are **independent:**
- Preference stability (A3) ≠ Self-prediction accuracy (C3)
  - System can have stable wrong preferences
  - Or changing correct preferences

- Recovery success (E1) ≠ Core identity drift (A1)
  - Can recover successfully but drift over time
  - Or maintain identity but fail recovery

### Dependencies

These metrics are **related:**
- Contradiction count (A4) affects Goal persistence (A2)
  - High contradictions suggest goal drift

- Trait extraction (C1) enables Self-prediction (C3)
  - Need accurate model to predict behavior

---

## Data Requirements

All metrics require:

1. **Structured input data** (JSON)
2. **Reproducible test cases** (deterministic where possible)
3. **Ground truth or validation method**
4. **Raw scores before thresholding**
5. **Multiple runs for stability**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-11 | Initial definitions after P1-P5a completion |

---

*Metric Definitions v1.0*  
*Part of Superbrain Evaluation Protocol*
