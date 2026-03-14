# L4-v3 Design Specification

**Status**: 🟡 DESIGN PHASE  
**Date**: 2026-03-14  
**Parent**: L4-v2 (PARTIAL SUCCESS) + E-COMP-003 (CLOSED)  
**Goal**: Mechanism-resolvable inheritance in new task environment

---

## Lessons from E-COMP-003 (Carry Forward)

### ✅ Confirmed Effective
1. **Mechanism/routing bias** — direction correct, family distribution shifts as intended
2. **Anti-leakage** — leakage suppression works (0% achieved)

### ✅ Confirmed Not Bottleneck
3. **Anti-leakage strength** — 0.2 ≈ 0.4, tuning not useful

### ❌ Task-1 Not Suitable
4. **Task-1 for fine-tuning** — too difficult/noisy, approve rates 3-7% regardless of configuration

---

## Core Design Decisions

### Decision 1: New Task Family

**Rationale**: Task-1 difficulty masks mechanism differences. Need clearer signal.

**Requirements for new task**:
- [ ] Real-world semantics (not toy problem)
- [ ] Clearer mechanism-signal relationship than Task-1
- [ ] Approve rate 20-40% achievable (not 3-7%)
- [ ] Inherits Task-1's heterogeneous executor coordination theme

**Candidates**:
- Task-2: Multi-stage pipeline scheduling
- Task-3: Dynamic resource allocation with changing constraints
- Task-4: Distributed consensus under churn

### Decision 2: Mechanism-First Inheritance

**Rationale**: Family-level bias too coarse (L4-v1 lesson).

**L4-v3 Package Structure**:
```json
{
  "package_version": "3.0-mechanism-first",
  "stable_mechanisms": {
    "delegation_patterns": [...],
    "recovery_sequences": [...],
    "trust_priors": {...}
  },
  "routing_geometry": {
    "high_value_regions": [...],
    "avoid_regions": [...]
  },
  "anti_leakage": {
    "enabled": true,
    "strength": 0.2,  // Fixed, not tuned
    "max_family_distance": 1
  }
}
```

### Decision 3: T4 / High Triage Prior

**From E-COMP-003**: T4 consistently appeared in high-performing configurations.

**Implementation**: Bias generation toward high triage (T4), but not absolute rule.

### Decision 4: Approve Rate Target Adjustment

**Task-1 experience**: 60% unrealistic.

**L4-v3 targets**:
- Approve rate: >25% (achievable, not 60%)
- Reuse rate: >60% (mechanism-level)
- Leakage: <10%

---

## L4-v3 Experiment Design

### Rounds

| Round | Purpose | Config |
|-------|---------|--------|
| **Round A-v3** | Baseline | Pure exploration |
| **Round B-v3** | Mechanism-first inheritance | v3 package with T4 prior |
| **Ablation-v3** | Control purity | Package loaded, bias=0 |

### Sample Size

- Generation: n=100 per round
- Mainline evaluation: n=30 per round (stratified)
- Target: ≥10 winners total for pattern validation

### Success Criteria

| Metric | Target | Hard/Soft |
|--------|--------|-----------|
| Approve rate (B vs A) | B > A +10% | Hard |
| Reuse rate | >60% | Hard |
| Leakage | <10% | Hard |
| T4 share in winners | >50% | Soft |
| Control purity | A = Ablation | Hard |

---

## Implementation Plan

### Phase 1: Task Selection (1 day)

- Evaluate Task-2, Task-3, Task-4 candidates
- Select based on: real semantics, clearer signal, 20-40% achievable approve rate
- Build minimal validator

### Phase 2: Package Design (1 day)

- Design v3 mechanism-first package
- Define stable mechanisms from L4-v2 winners (if transferable)
- Set T4 prior and anti-leakage 0.2

### Phase 3: Execution (2 days)

- Generate candidates
- Evaluate
- Extract patterns

### Phase 4: Judgment (0.5 day)

- Compare B vs A
- Validate targets
- Go/No-Go decision

**Total**: ~4.5 days

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| New task also too difficult | Pre-validate with quick Bridge test |
| Mechanisms not transferable | Design new mechanisms from scratch if needed |
| Still low approve rates | Lower targets further or accept partial success |

---

## Relationship to Other Lines

| Line | Relationship |
|------|--------------|
| L4-v2 | Parent — lessons absorbed, flaws addressed |
| E-COMP-003 | Direct predecessor — critical lessons (strength not bottleneck) |
| Superbrain | Potential integration point if L4-v3 succeeds |

---

## Open Questions

1. **Which task family?** — Need to evaluate candidates
2. **Mechanism transfer?** — Can Task-1 mechanisms transfer or need redesign?
3. **T4 prior generalizable?** — Will high triage be valuable in new task?

---

## Next Steps

1. [ ] Task family selection
2. [ ] Minimal validator build
3. [ ] v3 package design
4. [ ] Execution

---

**Design Status**: Initial spec complete  
**Ready for**: Task selection decision  
**Blocked by**: None

---

*L4-v3 Design Specification*  
*Date: 2026-03-14*
