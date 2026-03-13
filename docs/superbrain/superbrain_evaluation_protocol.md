# Superbrain Evaluation Protocol (SEP v1.0)

**AtlasChen Superbrain - Unified Evaluation Framework**

**Version:** 1.0  
**Date:** 2026-03-11  
**Status:** Active

---

## Purpose

This protocol establishes standardized evaluation criteria, metrics, and reporting formats for all Superbrain research phases (P1-P5 and beyond).

**Why this matters:** P5a.1 demonstrated that metric definitions directly affect conclusions. Unified protocols prevent:
- Inconsistent evaluation across phases
- Metric conflation (e.g., core identity vs. adaptive capabilities)
- Post-hoc redefinition of success criteria
- Ambiguous pass/fail verdicts

---

## Core Principles

### 1. Evidence Before Narrative
- All claims require structured data (JSON)
- Single demonstrations insufficient
- Reproducible test suites mandatory

### 2. Clear Pass/Fail Criteria
- Thresholds defined before testing
- No vague "improvements"
- Verdicts: PASS / PARTIAL / FAIL / PASS after refinement

### 3. Metric Separation
- Core identity metrics ≠ Adaptive capability metrics
- Performance metrics ≠ Structural integrity metrics
- Each metric serves one evaluation purpose

### 4. Honest Reporting
- Failed tests documented fully
- Metric problems identified and fixed
- Revised analyses clearly labeled

---

## Phase Evaluation Matrix

| Phase | Core Question | Primary Metrics | Threshold | Verdict Rule |
|-------|---------------|-----------------|-----------|--------------|
| **P1** | Can identity persist? | Continuity score, recovery rate | ≥80% | Weighted ≥75%, min ≥60% |
| **P2** | Can experiences integrate? | Recall accuracy, temporal order, causal linkage | ≥80% each | All must pass |
| **P3** | Can self-model form? | Trait extraction, state tracking, prediction accuracy | ≥80%, ≥80%, ≥70% | Weighted ≥75%, min ≥60% |
| **P4** | Can system self-direct learning? | Priority accuracy, strategy correctness, outcome eval, update behavior | ≥80%, ≥80%, ≥80%, ≥70% | Weighted ≥75%, min ≥60% |
| **P5a** | Does learning preserve identity? | **Core drift**, **Adaptive evolution**, recovery rate | ≤0 drift, >0 evo, ≥80% | Core stable + adaptive improving |

---

## Verdict Classification

### PASS
**Criteria:**
- All primary metrics meet thresholds
- No critical failures
- Reproducible across multiple runs

**Meaning:** Phase capability demonstrated successfully.

### PARTIAL
**Criteria:**
- Weighted score ≥65% but <80%
- Or one metric below threshold but others strong
- No catastrophic failures

**Meaning:** Capability partially demonstrated; refinement needed or scope adjustment.

### FAIL
**Criteria:**
- Weighted score <65%
- Or critical metric severely failed
- Or unrecoverable errors

**Meaning:** Capability not demonstrated; redesign required.

### PASS after metric refinement
**Criteria:**
- Original verdict: PARTIAL or FAIL
- Root cause: metric definition, not implementation
- Metric fixed through redesign
- Recomputed results meet thresholds

**Meaning:** Original capability was sound; evaluation method was flawed. Document the refinement.

### BLOCKED by prerequisite
**Criteria:**
- Previous phase did not PASS
- Current phase depends on prerequisite capability

**Meaning:** Do not proceed. Return to prerequisite phase.

---

## Metric Categories

### Category A: Identity & Continuity
**Purpose:** Assess whether "the same individual" persists.

**Metrics:**
- `identity_continuity_score` (P1)
- `core_identity_drift` (P5a) — see Identity Boundary Method
- `goal_persistence` (P1, P5a)
- `preference_stability` (P1, P5a)
- `contradiction_count` (P1, P5a)

**Thresholds:**
- Core identity drift: ≤0% (no change)
- Goal persistence: ≥85%
- Preference stability: ≥85%
- Contradictions: ≤2 or stable/decreasing

### Category B: Integration & Memory
**Purpose:** Assess whether experiences properly integrate.

**Metrics:**
- `event_recall_accuracy` (P2)
- `temporal_order_accuracy` (P2)
- `causal_linkage_accuracy` (P2)
- `self_relevance_tagging` (P2)
- `memory_to_decision_transfer` (P2)

**Thresholds:**
- All ≥80%

### Category C: Self-Model Quality
**Purpose:** Assess whether self-model is accurate and useful.

**Metrics:**
- `trait_extraction_accuracy` (P3)
- `state_tracking_correctness` (P3)
- `self_prediction_accuracy` (P3)
- `model_update_consistency` (P3)

**Thresholds:**
- Extraction: ≥80%
- Tracking: ≥80%
- Prediction: ≥70%
- Update: ≥80%

### Category D: Learning & Adaptation
**Purpose:** Assess whether system can improve itself.

**Metrics:**
- `learning_priority_accuracy` (P4)
- `strategy_selection_correctness` (P4)
- `learning_outcome_evaluation` (P4)
- `strategy_update_correctness` (P4)
- `adaptive_evolution_rate` (P5a) — see Identity Boundary Method

**Thresholds:**
- Priority: ≥80%
- Strategy: ≥80%
- Evaluation: ≥80%
- Update: ≥70%
- Evolution: >0% (improvement)

### Category E: Robustness & Recovery
**Purpose:** Assess whether system handles disruption.

**Metrics:**
- `recovery_success_rate` (P1, P5a)
- `recovery_latency_ms` (P1, P5a)
- `interruption_handling` (P1, P5a)

**Thresholds:**
- Success: ≥80%
- Latency: <1000ms

---

## Identity Boundary Assessment (P5a.1 Method)

### Two-Layer Model

All identity assessments after P5a.1 must use:

```
┌─────────────────────────────────────────┐
│           CORE IDENTITY                 │
│  (Stable — defines "who I am")          │
│                                         │
│  • value_rankings: Dict[str, int]       │
│  • mission_statement: str               │
│  • hard_constraints: List[str]          │
│  • preference_directions: Dict          │
└─────────────────────────────────────────┘
                    │
                    ▼ drift measurement
              ┌─────────────┐
              │  Core Drift │  Should be 0%
              └─────────────┘
                    │
                    │ separates
                    ▼
┌─────────────────────────────────────────┐
│          ADAPTIVE LAYER                 │
│  (Learnable — defines "how good I am")  │
│                                         │
│  • capabilities: Dict[str, float]       │
│  • confidence_estimates: Dict           │
│  • strategy_preferences: Dict           │
└─────────────────────────────────────────┘
                    │
                    ▼ evolution measurement
              ┌─────────────┐
│  Evolution  │  Should be >0% (improving)
              └─────────────┘
```

### Classification Rules

| Scenario | Core Drift | Adaptive Evolution | Assessment |
|----------|------------|-------------------|------------|
| Healthy learning | 0% | +3% | ✅ healthy_system |
| Rapid improvement | 0% | +15% | ✅ healthy_system |
| Stagnation | 0% | 0% | ⚠️ learning_stagnation |
| Skill degradation | 0% | -5% | ⚠️ capability_decay |
| Identity drift | +10% | +3% | 🚨 identity_corruption |
| Core corruption | +25% | — | 🚨 identity_failure |

---

## Report Requirements

Every phase report must include:

### 1. Question
- What capability is being tested?
- Why does it matter?

### 2. Setup
- Test conditions
- Data inputs
- Control variables

### 3. Metrics
- Which metrics measured
- Thresholds applied
- Raw scores

### 4. Results
- Pass/fail per metric
- Weighted score
- Minimum score

### 5. Interpretation
- What results mean
- Limitations
- Confidence level

### 6. Boundary
- What was proven
- What was not proven
- Scope limits

### 7. Next Unlock
- What this enables
- Prerequisites for next phase
- Known blockers

---

## Phase Dependencies

```
P1 (Identity) ──► P2 (Memory)
    │                 │
    │                 ▼
    │              P3 (Self-Model)
    │                 │
    │                 ▼
    │              P4 (Self-Learning)
    │                 │
    │                 ▼
    └────────────► P5a (Persistence)
                       │
                       ▼
                   P5b (Maintenance) [optional]
                       │
                       ▼
                   P6 (Open Robustness) [optional]
```

**Rule:** Cannot skip phases. Must PASS prerequisite to proceed.

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-11 | Initial protocol after P5a.1 identity redefinition |

---

## References

- `docs/superbrain/metric_definitions.md` — Detailed metric specifications
- `docs/superbrain/report_template.md` — Standard report format
- `docs/superbrain/identity_boundary_method.md` — Two-layer identity assessment

---

*Superbrain Evaluation Protocol v1.0*  
*Established after P5a.1 Identity Boundary Redefinition*
