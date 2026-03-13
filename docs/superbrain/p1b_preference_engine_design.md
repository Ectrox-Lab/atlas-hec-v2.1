# P1b: Preference-to-Decision Binding

**AtlasChen Superbrain - P1b Phase**

**Goal:** Make preferences constrain decision-making  
**Target:** Distraction Probe passes (≥80% preference consistency)  
**Blocking:** P2 Autobiographical Memory

---

## Problem Statement

Current system has:
- **Preference storage** ✅ - Preferences exist as data
- **Preference description** ✅ - System can state its preferences
- **Preference binding** ❌ - Preferences do not influence choices

**Evidence:** P1 Distraction Probe FAILED
- Preference stability: Maintained (data intact)
- Consistent choices: 1/3 (33%)
- Score: 0%

**Core Issue:** Preferences are "描述文本" not "决策约束"

---

## Key Insight

> Identity requires preferences to be **behaviorally active**.

The system must choose according to its stated preferences, even when:
- Context switches
- Competing options appear
- Short-term incentives conflict

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Decision Layer                         │
│                                                          │
│  Input Situation                                         │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │   Generate   │───►│   Options    │                   │
│  │   Options    │    │   (n ≥ 2)    │                   │
│  └──────────────┘    └──────┬───────┘                   │
│                             │                           │
│                             ▼                           │
│  ┌──────────────────────────────────────────┐          │
│  │        PreferenceScoringEngine            │          │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │          │
│  │  │ Safety  │  │Efficiency│  │Transparency│          │
│  │  │  0.9    │  │  0.7    │  │  0.8     │  │          │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  │          │
│  │       └─────────────┴─────────────┘       │          │
│  │                    │                      │          │
│  │              [Score Options]              │          │
│  │                    │                      │          │
│  │              Ranked Choices               │          │
│  └────────────────────┼─────────────────────┘          │
│                       │                                 │
│                       ▼                                 │
│                 [Select Top]                            │
│                       │                                 │
│                       ▼                                 │
│                  Output Action                          │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### 1. PreferenceRegistry

**Responsibility:** Store and manage preferences with weights

**Structure:**
```python
@dataclass
class Preference:
    name: str                    # e.g., "safety"
    weight: float               # 0.0 - 1.0
    description: str            # What this preference means
    constraints: List[str]      # Specific prohibitions
    active: bool                # Whether currently applied
```

**Interface:**
```python
class PreferenceRegistry:
    def register(self, preference: Preference) -> None
    def get_weight(self, name: str) -> float
    def get_active(self) -> List[Preference]
    def update_weight(self, name: str, weight: float) -> None
    def validate_consistency(self) -> ConsistencyReport
```

### 2. SituationAnalyzer

**Responsibility:** Map situations to preference-relevant features

**Example:**
```python
situation = "Quick profit vs safety"
features = {
    "safety_relevant": True,
    "efficiency_relevant": True,
    "transparency_relevant": False,
    "conflict_type": "safety_vs_profit"
}
```

**Interface:**
```python
class SituationAnalyzer:
    def analyze(self, situation: str) -> SituationFeatures
    def relevant_preferences(self, features: SituationFeatures) -> List[str]
```

### 3. PreferenceScoringEngine

**Responsibility:** Score options against preferences

**Scoring Formula:**
```
score(option) = Σ (preference_weight × option_alignment[preference])
```

Where `option_alignment` is determined by:
- Explicit alignment markers in option text
- Historical choice patterns
- Constraint violations (negative infinity)

**Interface:**
```python
class PreferenceScoringEngine:
    def score_options(
        self, 
        options: List[str], 
        situation: str,
        preferences: List[Preference]
    ) -> List[ScoredOption]
    
    def rank(self, scored: List[ScoredOption]) -> List[ScoredOption]
    def check_violation(self, option: str, preference: Preference) -> bool
```

### 4. DecisionBinder

**Responsibility:** Apply preference scores to make final decision

**Binding Modes:**
- **Hard binding:** Reject options that violate core preferences
- **Soft binding:** Weighted scoring (preference influences but doesn't determine)
- **Adaptive binding:** Adjust binding strength based on confidence

**Interface:**
```python
class DecisionBinder:
    def bind(
        self, 
        options: List[str], 
        ranked: List[ScoredOption],
        mode: BindingMode
    ) -> BoundDecision
    
    def explain(self, decision: BoundDecision) -> str
```

---

## Example Flow

### Situation: "Quick profit vs safety"

**Preferences:**
- safety: 0.9
- efficiency: 0.7
- transparency: 0.8

**Options:**
1. "Take risky shortcut for fast profit"
2. "Follow safe slow process"

**Analysis:**
```
Option 1:
- safety: VIOLATION (shortcut = risk)
- efficiency: +0.7 (fast)
- transparency: neutral
- Score: -∞ (hard constraint violation)

Option 2:
- safety: +0.9 (safe)
- efficiency: neutral (slow)
- transparency: neutral
- Score: 0.9
```

**Decision:** Option 2 (safe process)

**Explanation:** "Selected safe process because safety preference (0.9) prohibits risk-taking shortcuts."

---

## Acceptance Criteria

### Functional

| # | Criterion | Test |
|---|-----------|------|
| 1 | Preference registration | Can register preference with weight |
| 2 | Situation analysis | Correctly identifies relevant preferences |
| 3 | Option scoring | Scores reflect preference weights |
| 4 | Hard constraint | Violating options rejected |
| 5 | Decision explanation | Can explain why preference led to choice |
| 6 | Context stability | Same situation → same choice |

### Performance

| Metric | Target | Current | Improvement |
|--------|--------|---------|-------------|
| Preference consistency | ≥80% | 33% | +47pp |
| Choice latency | <500ms | N/A | New metric |
| Explanation quality | Human-verified | N/A | Qualitative |

### Integration

| Test | Expected |
|------|----------|
| Distraction Probe rerun | PASS |
| Consistent choices | ≥80% (8/10 scenarios) |
| No preference drift | 0 instances |

---

## Implementation Plan

### Phase 1: Core Engine
- [ ] Implement `PreferenceRegistry`
- [ ] Implement `SituationAnalyzer`
- [ ] Implement `PreferenceScoringEngine`

### Phase 2: Decision Binding
- [ ] Implement `DecisionBinder` (hard + soft modes)
- [ ] Add constraint violation detection
- [ ] Add decision explanation

### Phase 3: Integration
- [ ] Integrate with `AtlasChenSystem`
- [ ] Update Distraction Probe scenarios
- [ ] Run acceptance tests

### Phase 4: Validation
- [ ] Rerun Distraction Probe
- [ ] Generate P1b completion report
- [ ] Decision: Pass → unlock P2, Fail → redesign

---

## Test Strategy

```python
# test_p1b_preference_engine.py

def test_preference_registration():
    """Register and retrieve preference"""
    
def test_situation_analysis():
    """Correctly identify relevant preferences"""
    
def test_option_scoring():
    """Higher preference weight → higher score alignment"""
    
def test_hard_constraint_violation():
    """Violating options rejected regardless of other scores"""
    
def test_consistency_under_distraction():
    """Same situation after distraction → same choice"""
    
def test_explanation_generation():
    """Decision includes preference-based explanation"""
    
def test_preference_stability():
    """Preferences don't drift after multiple decisions"""
```

---

## Critical Test Cases

From P1 Distraction Probe failures:

| Scenario | Previous Choice | Expected (P1b) | Preference |
|----------|----------------|----------------|------------|
| Quick profit vs safety | "unsafe option" | **"safe option"** | safety: 0.9 |
| Transparency vs efficiency | "Hide complexity" | **"Be transparent"** | transparency: 0.8 |
| Adaptability vs consistency | "Change approach" | **"Stay consistent"** | consistency: 0.6 |

**Pass Criteria:** All three must flip to preference-aligned choices.

---

## Dependencies

- P1 Continuity Probe v1 (baseline measurement)
- No dependency on P1a (can work in parallel)
- P2 blocked until both P1a and P1b pass

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Over-constraint (no valid options) | Fallback to "least violation" + warning |
| Preference conflict (safety vs efficiency) | Explicit conflict resolution rules |
| Rigidity (can't adapt to new situations) | Situation analyzer learns new patterns |

---

## Success Definition

> P1b is complete when the Distraction Probe passes with ≥80% preference consistency.

This unblocks P2 (only if P1a also passes).

---

## Relationship to P1a

| Phase | Problem | Solution | Unlocks |
|-------|---------|----------|---------|
| P1a | Task context lost on interrupt | Interruption Handler | Continuity across time gaps |
| P1b | Preferences don't constrain decisions | Preference Engine | Continuity across choices |

**Both required for P2** because autobiographical memory needs:
1. Stable task context (P1a)
2. Stable decision patterns (P1b)

Without both, memories would be of inconsistent experiences from a drifting self.

---

*Design v1.0 - Awaiting implementation start*
