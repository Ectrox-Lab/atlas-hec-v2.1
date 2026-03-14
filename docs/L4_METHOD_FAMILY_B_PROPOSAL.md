# L4 Method Family B: Proposal

**Status**: 🟡 PROPOSED  
**Date**: 2026-03-14  
**Parent**: L4 Method Family A (CLOSED — Non-Convergent)  
**Goal**: Same as Family A (compositional reuse), different approach

---

## Problem Statement

### From Family A Failure

**What we learned**:
1. Family/mechanism-level abstraction doesn't capture real reusable units
2. Biasing generation toward "stable configurations" doesn't create stability
3. Small samples (n=20-100) produce unreliable positive signals
4. Anti-leakage works (0% leakage) but doesn't drive reuse improvement

**What we need**:
- Different abstraction for "reusable module"
- Different generation/bias approach
- Different validation (must work at n=300)
- Different refinement discipline

---

## Core Hypothesis: Family B

### Hypothesis: Explicit Interface Contracts

**Problem with Family A**: Implicit "family" or "mechanism" identity.

**Family B approach**: Explicit interface contracts that can be:
- Verified (does implementation satisfy contract?)
- Composed (do contracts align for composition?)
- Inherited (can new candidate reuse verified contract?)

### Key Difference

| Aspect | Family A (Failed) | Family B (Proposed) |
|--------|-------------------|---------------------|
| **Unit of reuse** | Family/mechanism label | **Interface contract** |
| **Verification** | Performance correlation | **Contract satisfaction** |
| **Generation** | Bias toward stable families | **Compose from verified contracts** |
| **Validation** | Reuse rate | **Contract coverage + composition success** |

---

## Technical Approach

### 1. Interface Contract Definition

Instead of:
```python
# Family A: Implicit
"F_P3T4M4 is stable"
```

Use:
```python
# Family B: Explicit
Contract {
  "name": "StageHandoff",
  "requires": {"triage": 4, "delegation": 1},
  "guarantees": {"handoff_latency": "< 2x baseline"},
  "verified_on": [task1, task2],
  "composes_with": ["FailureRecovery", "LoadBalancing"]
}
```

### 2. Generation by Contract Composition

Instead of:
```python
# Family A: Bias toward family
if candidate.family in stable_families:
    boost_score()
```

Use:
```python
# Family B: Compose contracts
candidate = Compose([
    ContractDB.Get("StageHandoff"),
    ContractDB.Get("FailureRecovery")
])
if candidate.SatisfiesAllContracts():
    approve()
```

### 3. Validation by Contract Verification

Instead of:
```python
# Family A: Reuse rate
if approve_rate > threshold:
    success()
```

Use:
```python
# Family B: Contract coverage
for contract in candidate.contracts:
    assert Verify(contract, on=validation_tasks)
coverage = len(verified_contracts) / len(candidate.contracts)
if coverage > 0.9:
    success()
```

---

## Minimal Viable Experiment (MVE)

### Goal

Test if "explicit contract composition" produces better results than "family bias" in same Task-2 environment.

### Setup

**Contracts to define** (3-5 minimal set):
1. `StrictHandoff` — D1 delegation, low trust decay
2. `AdaptiveRecovery` — M3+ memory, recovery sequence
3. `PressureThrottle` — P2, controlled injection
4. `HighTriage` — T4, priority scheduling

**Generation**:
- Randomly compose 2-3 contracts per candidate
- Verify contract satisfaction on Task-2
- Only evaluate candidates with 100% contract coverage

**Validation**:
- n=300 candidates
- Measure: contract coverage, composition success, task performance
- Compare to Family A baseline (30% reuse ceiling)

### Success Criteria

| Metric | Family A (Failed) | Family B Target |
|--------|-------------------|-----------------|
| Reuse (via contracts) | 30% | **>50%** |
| Contract coverage | N/A | **>90%** |
| Composition success | N/A | **>80%** |
| Effect at n=300 | 0% | **>+10pp** |

### Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Contract design | 2 days | 3-5 verified contracts |
| Generator build | 2 days | Contract composition generator |
| MVE execution | 2 days | n=300 evaluation |
| Analysis | 1 day | Go/No-Go decision |
| **Total** | **7 days** | **Family B validation** |

---

## Risk Mitigation

### Risk 1: Contracts Also Don't Capture Reuse

**Mitigation**: Start with 3 simple contracts based on Family A's observed patterns. If even simple contracts fail, abandon approach.

### Risk 2: Contract Verification Too Expensive

**Mitigation**: Use fast simulation (Bridge-level) for contract verification, only full Mainline for final candidates.

### Risk 3: Same Small-Sample Trap

**Mitigation**: Hard rule: No claims without n=300. Build infrastructure for large-sample validation from day 1.

---

## Comparison: Family A vs Family B

| Dimension | Family A (CLOSED) | Family B (PROPOSED) |
|-----------|-------------------|---------------------|
| **Core abstraction** | Implicit family identity | **Explicit interface contracts** |
| **Reuse mechanism** | Statistical correlation | **Verified composition** |
| **Validation** | Reuse rate | **Contract coverage + composition** |
| **Sample requirement** | 20-100 (insufficient) | **300 minimum (hard rule)** |
| **Refinement** | Aggressive (v3.1 failed) | **Conservative (validate first)** |

---

## Open Questions

1. **What contracts actually matter?** — Need empirical identification
2. **How to verify composition?** — Static analysis vs runtime testing
3. **Contract granularity?** — Fine-grained (many small) vs coarse-grained (few large)
4. **Transfer across tasks?** — Core requirement, needs explicit design

---

## Decision Required

### Approve Family B Proposal?

**Yes means**:
- Archive Family A completely (done)
- Allocate 7 days for Family B MVE
- Accept risk of second failure

**No means**:
- Abandon compositional reuse line entirely
- Pivot to different research direction
- Document L4 goals as "not achievable with current techniques"

### Recommended: YES

**Rationale**:
- Family A's failure was specific (family/mechanism abstraction)
- Core goals (compositional reuse) remain valid
- Family B addresses root cause (explicit vs implicit)
- 7-day MVE is acceptable cost for potential breakthrough
- If Family B also fails, then abandon line with stronger evidence

---

**Proposed**: Approve Family B MVE  
**Timeline**: 7 days  
**Decision deadline**: 2026-03-15

---

*L4 Method Family B Proposal*  
*Building on lessons from Family A*
