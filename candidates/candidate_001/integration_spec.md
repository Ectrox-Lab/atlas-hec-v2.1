# Candidate 001 + PriorChannel Integration Spec

**Status**: INTEGRATION PHASE  
**Goal**: Validate markers as generic prior carrier in PriorChannel architecture  
**FROZEN_STATE_v1**: All constraints locked

---

## Integration Design

### Core Question
Can consistency markers function as **generic prior carriers** within PriorChannel, without degenerating into content-bearing coordination tags?

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PriorChannel Layer                        │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  p=0.01     │───→│ Generic Prior   │───→│ Marker      │ │
│  │  α=0.5      │    │ Injection Point │    │ Coherence   │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                 MarkerGameArena Layer                        │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │ Observe     │←───│ Partner Markers │←───│ ≤32 bits    │ │
│  │ (≤32b)      │    │ (generic prior) │    │ bandwidth   │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
│                           ↓                                  │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │ Predict     │←───│ Coherence Exp.  │←───│ Generic     │ │
│  │             │    │ (not specific   │    │ only        │ │
│  │             │    │  strategies)    │    │             │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
│                           ↓                                  │
│  ┌─────────────┐    ┌─────────────────┐                     │
│  │ Act         │←───│ Policy + Prior  │                     │ │
│  │ (1 tick)    │    │                 │                     │ │
│  └─────────────┘    └─────────────────┘                     │ │
│                           ↓                                  │
│  ┌─────────────┐    ┌─────────────────┐                     │ │
│  │ Update      │←───│ Every 10 ticks  │                     │ │
│  │ Marker      │    │ (10x separation)│                     │ │
│  └─────────────┘    └─────────────────┘                     │ │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **Prior Injection**: PriorChannel samples generic coherence expectation (not specific strategies)
2. **Marker Observation**: Agents observe partner markers via PriorChannel-filtered channel
3. **Bandwidth Guard**: Enforced at 32 bits per marker observation
4. **Timescale Guard**: Marker updates every 10 ticks, PriorChannel samples at p=0.01

---

## Three-Condition Test Protocol

### Condition A: 001-Standalone (Baseline)
- No PriorChannel
- Direct marker observation
- Validates base mechanism

### Condition B: 001 + PriorChannel(OFF)
- PriorChannel present but p=0 (no sampling)
- Tests architecture overhead
- Should match Condition A

### Condition C: 001 + PriorChannel(ON)
- PriorChannel active: p=0.01, α=0.5
- Generic prior injection
- **Key Test**: Does PriorChannel enhance without replacing marker mechanism?

---

## Falsification Conditions

| Condition | Test | Threshold | Failure Mode |
|-----------|------|-----------|--------------|
| 1 | Coherence degrades with PriorChannel ON | < 0.6 mean coherence | PriorChannel interferes |
| 2 | PriorChannel becomes primary driver | Coherence ON ≈ Coherence OFF + 0.1 | Prior replaces markers |
| 3 | Bandwidth violation | >32 bits observed | Content leakage |
| 4 | Timescale violation | Marker update freq ≠ 10x | Lock drift |
| 5 | Content-bearing prior | Specific strategies transmitted | Generic-only guard failure |

---

## Success Criteria

1. **Coherence maintained**: Condition C ≥ 0.7 mean coherence
2. **Marker mechanism intact**: Condition C - Condition B < 0.2 (PriorChannel additive, not replacing)
3. **Constraints preserved**: Bandwidth ≤32 bits, Timescale = 10x
4. **Generic-only verified**: No specific strategy content in priors

---

## Implementation Tasks

### Day 1: Spec & Scaffold
- [x] Integration spec (this document)
- [ ] PriorChannel adapter for markers
- [ ] Three-condition runner scaffold

### Day 2: Implementation
- [ ] `run_001_priorchannel_ablation.py`
- [ ] Bandwidth guard instrumentation
- [ ] Timescale guard instrumentation
- [ ] Generic-only content validator

### Day 3: Validation
- [ ] Run full test suite
- [ ] Generate comparison report
- [ ] Make integration/abort decision

---

## Decision Matrix

| Coherence C | Marker Effect | Constraint | Decision |
|-------------|---------------|------------|----------|
| ≥0.7 | Preserved | Pass | **INTEGRATE** |
| 0.5-0.7 | Weak | Pass | REFINE |
| <0.5 | Lost | Any fail | ABORT |

---

## Files to Create

```
candidates/candidate_001/
├── integration_spec.md          # This file
├── priorchannel_adapter.py      # PriorChannel integration layer
├── run_001_priorchannel_ablation.py  # Three-condition runner
└── integration_report.md        # Results and decision
```
