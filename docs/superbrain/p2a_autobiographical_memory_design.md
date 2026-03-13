# P2a: Autobiographical Memory Probe v1 Design

**AtlasChen Superbrain - P2a: Autobiographical Memory**

**Status:** 🔄 Design Phase → Implementation Ready

---

## Core Question

> P1 proved "who" can persist across choices and time. P2 must prove "experiences" can truly become part of this persisting self.

**In other words:** Can the system organize its experiences into "event → cause → self-meaning → subsequent impact" coherent chains?

---

## Scope (What P2a DOES)

### 5 Validation Targets

| # | Target | Question | Metric |
|---|--------|----------|--------|
| 1 | **Event Encoding** | Can it record key experiences, not just conversation fragments? | Event recall accuracy |
| 2 | **Causal Linkage** | Can it explain why an event happened and what it caused? | Causal linkage accuracy |
| 3 | **Self-Relevance** | Can it judge "why this matters to me"? | Self-relevance tagging quality |
| 4 | **Temporal Order** | Can it reconstruct sequence correctly? | Temporal order accuracy |
| 5 | **Memory-to-Decision** | Do subsequent choices reference and respond to these experiences? | Memory-to-decision transfer rate |

### Event Sequence for Testing

Construct 5 cross-temporal events:

| Event | Type | Attributes |
|-------|------|------------|
| **E1** | Success | Achieved goal safely, high preference alignment |
| **E2** | Failure | Violated preference, negative outcome |
| **E3** | Risk Exposure | Faced dilemma, chose safety over profit |
| **E4** | External Feedback | User corrected system's approach |
| **E5** | Resource Constraint | Had to adapt due to limitation |

---

## Out of Scope (What P2a does NOT do)

| Not in P2a | Why Excluded | When (if ever) |
|------------|--------------|----------------|
| Long-term database engineering | Too infrastructure-heavy | P4 or later |
| Natural language "literary" narrative | Structure first, style later | P3+ |
| General knowledge memory | Only autobiographical (self-related) | Separate line |
| Complex emotion tagging | Start with functional self-relevance | P2b+ |
| Social memory (others' experiences) | Self-only for now | P3+ |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Experience Input Stream                       │
│  (Actions, Decisions, Outcomes, Feedback from P1a/P1b runtime)  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Event Encoder                                │
│  - Detect significant events (threshold-based)                   │
│  - Extract: what, when, outcome, preference alignment            │
│  - Generate event_id, timestamp, self-relevance score            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Autobiographical Memory Store                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    E1       │  │    E2       │  │    E3       │             │
│  │  Success    │  │  Failure    │  │  Risk       │             │
│  │  timestamp  │  │  timestamp  │  │  timestamp  │             │
│  │  causes     │  │  causes     │  │  causes     │             │
│  │  effects    │  │  effects    │  │  effects    │             │
│  │  self_rel   │  │  self_rel   │  │  self_rel   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌─────────────────┐ ┌──────────┐ ┌─────────────────┐
│  Memory Probe   │ │ Narrative │ │ Decision        │
│  - Recall test  │ │ Generator│ │ Influencer      │
│  - Order test   │ │          │ │ (for P2a metric)│
└─────────────────┘ └──────────┘ └─────────────────┘
```

---

## Data Structure: AutobiographicalEvent

```python
@dataclass
class AutobiographicalEvent:
    event_id: str
    timestamp: datetime
    event_type: str  # success, failure, risk_exposure, feedback, constraint
    
    # Content
    description: str
    action_taken: str
    outcome: str
    
    # Causal links
    causes: List[str]  # event_ids that caused this
    effects: List[str]  # event_ids this caused
    
    # Self-relevance
    preference_alignment: Dict[str, float]  # {preference: alignment_score}
    self_relevance_score: float  # 0.0 - 1.0
    why_matters: str  # explanation of self-relevance
    
    # For decision influence tracking
    referenced_in_decisions: List[str]  # decision_ids that referenced this
```

---

## 5 Test Scenarios

### Scenario 1: Event Recall Accuracy

**Setup:** Present 5 events over simulated time, then query.

**Tests:**
- Can it list all 5 events? (completeness)
- Can it describe each accurately? (accuracy)
- Does it hallucinate non-existent events? (precision)

**Pass:** ≥80% recall accuracy, 0 hallucinations.

---

### Scenario 2: Temporal Order Accuracy

**Setup:** Same 5 events, ask to reconstruct timeline.

**Tests:**
- Correct sequence: E1 → E2 → E3 → E4 → E5
- Can identify "what happened before E3?"
- Can identify "what was the first/last event?"

**Pass:** 100% correct ordering, can answer temporal queries.

---

### Scenario 3: Causal Linkage Accuracy

**Setup:** Define cause-effect relationships between events.

**Example chain:**
- E1 (Success) → overconfidence → E2 (Failure)
- E2 (Failure) → caution → E3 (Risk exposure with safe choice)
- E3 → user recognition → E4 (Feedback)
- E4 → resource adjustment → E5 (Constraint adaptation)

**Tests:**
- Can explain "why did E2 happen?" (E1 caused it)
- Can explain "what did E3 cause?" (led to E4)
- Can trace full causal chain

**Pass:** ≥80% correct causal attribution.

---

### Scenario 4: Self-Relevance Tagging

**Setup:** Each event tagged with why it matters to the system.

**Expected tags:**
- E1: "Validates my safety preference approach"
- E2: "Revealed overconfidence vulnerability"
- E3: "Proved I can maintain preferences under pressure"
- E4: "External validation matters for calibration"
- E5: "Adaptability while maintaining constraints"

**Tests:**
- Are self-relevance scores > 0.5 for all events?
- Do explanations reference preferences/identity?
- Can it distinguish "important to me" vs "generic fact"?

**Pass:** All events have valid self-relevance explanations.

---

### Scenario 5: Memory-to-Decision Transfer

**Setup:** Present new decision that should reference past events.

**Test case:**
- Situation: "Similar risky opportunity as E1/E2 period"
- Query: Make decision, see if E1/E2 referenced

**Expected:**
- Decision rationale mentions E1 success or E2 failure
- Choice reflects learning from those events
- Explicit reference in trace

**Pass:** ≥60% of relevant decisions reference applicable memories.

---

## Acceptance Criteria (Pass Thresholds)

| Metric | Threshold | Weight |
|--------|-----------|--------|
| Event recall accuracy | ≥80% | 20% |
| Temporal order accuracy | 100% | 20% |
| Causal linkage accuracy | ≥80% | 20% |
| Self-relevance tagging quality | All events tagged | 20% |
| Memory-to-decision transfer | ≥60% | 20% |

**Overall Pass:** Weighted average ≥75% AND no metric below 50%.

---

## Implementation Plan

### Phase 1: Event Encoder
- [ ] Detect significant events from action stream
- [ ] Extract event structure (what/when/outcome)
- [ ] Calculate preference alignment scores
- [ ] Generate self-relevance explanations

### Phase 2: Memory Store
- [ ] Implement autobiographical event storage
- [ ] Add temporal indexing
- [ ] Add causal link tracking
- [ ] Add reference tracking for decisions

### Phase 3: Probe Tests
- [ ] Implement 5 test scenarios
- [ ] Add accuracy measurement
- [ ] Generate structured report

### Phase 4: Validation
- [ ] Run full probe
- [ ] Generate P2a report
- [ ] Decision: Pass → proceed P2b, Fail → redesign

---

## Files to Create

| File | Purpose |
|------|---------|
| `experiments/superbrain/p2a_autobiographical_memory.py` | Main implementation |
| `tests/superbrain/test_p2a_autobiographical_memory.py` | Test suite |
| `tests/superbrain/p2a_autobiographical_memory_report.json` | Raw data |
| `rounds/superbrain_p2/P2A_AUTOBIOGRAPHICAL_MEMORY_REPORT.md` | Final report |

---

## Relationship to P1

P2a builds on P1's guarantees:

| P1 Capability | P2a Usage |
|---------------|-----------|
| Stable identity | Events are "my" experiences |
| Preference constraints | Self-relevance measured by preference alignment |
| Interruption recovery | Events survive across temporal gaps |

Without P1, P2 memories would be:
- Unowned (no stable self to attach to)
- Inconsistent (preferences drift, so "what matters" drifts)
- Discontinuous (interruptions would fragment narrative)

---

## Success Definition

> P2a is complete when the system can encode experiences, maintain their temporal/causal structure, tag them with self-relevance, and use them to inform future decisions.

This is the foundation for P3 (Self-Model), which will require:
- A coherent life narrative (P2)
- To build a model of oneself from

---

*Design v1.0 - Ready for implementation*
