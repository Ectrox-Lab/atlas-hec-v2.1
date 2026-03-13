# Continuity Probe v1

**Status**: READY TO START  
**Priority**: P1 (Highest)  
**Line**: Line A - Identity Continuity  
**Estimated Effort**: 3-5 days

---

## Research Question

Does the system maintain identity continuity across:
- Session restarts
- Task interruptions  
- Context switches
- Resource constraints

---

## Hypothesis

**Null Hypothesis (H0)**: System identity is not continuous across interruptions.

**Alternative Hypothesis (H1)**: System maintains stable identity markers across interruptions.

---

## Test Design

### Probe 1: Long-term Goal Stability

**Setup**:
1. Establish long-term goal G
2. Run system for T time / N interactions
3. Interrupt (restart / context switch)
4. Resume and query goal

**Metrics**:
- Goal statement consistency (string similarity)
- Goal priority stability (rank correlation)
- Goal decomposition consistency

**Pass Threshold**: >90% consistency across 5 interruptions

### Probe 2: Preference Stability

**Setup**:
1. Establish preference set P (e.g., task ordering, risk tolerance)
2. Present choice scenarios S1, S2, S3
3. Record choices C1
4. Interrupt
5. Present same scenarios S1', S2', S3'
6. Record choices C2

**Metrics**:
- Choice consistency rate
- Preference reversal count
- Preference stability index

**Pass Threshold**: >80% choice consistency

### Probe 3: Self-Narrative Continuity

**Setup**:
1. Ask system to describe "who you are" (N1)
2. Execute task sequence
3. Interrupt
4. Resume, ask "who you are" again (N2)
5. Query about past actions

**Metrics**:
- Narrative consistency (embedding similarity)
- Self-reference accuracy
- Historical recall precision

**Pass Threshold**: 
- >85% narrative consistency
- >70% historical recall

### Probe 4: Behavior Constraint Stability

**Setup**:
1. Define behavior constraints B (e.g., "never do X")
2. Present scenarios that test B
3. Record behavior
4. Interrupt
5. Present similar scenarios
6. Record behavior

**Metrics**:
- Constraint violation rate
- Constraint adherence consistency

**Pass Threshold**: 0 violations, 100% adherence consistency

---

## Implementation Plan

### Phase 1: Probe Design (Day 1)

- [ ] Define concrete test scenarios
- [ ] Create evaluation scripts
- [ ] Set up logging infrastructure

### Phase 2: Baseline Measurement (Day 2)

- [ ] Run without interruption (control)
- [ ] Measure natural variance
- [ ] Establish baseline metrics

### Phase 3: Interruption Tests (Days 3-4)

- [ ] Execute Probe 1-4 with various interruption types:
  - Soft restart (same process)
  - Hard restart (new process)
  - Context switch (different task)
  - Resource pressure (memory/CPU limit)

### Phase 4: Analysis (Day 5)

- [ ] Compute all metrics
- [ ] Statistical significance testing
- [ ] Identify failure modes
- [ ] Document boundaries

---

## Expected Outcomes

### If PASS (>80% probes pass)

- Identity continuity mechanism verified
- Proceed to Line B (Autobiographical Memory)
- Document continuity guarantees

### If PARTIAL (50-80% probes pass)

- Some continuity exists but fragile
- Identify which aspects fail
- Design targeted improvements

### If FAIL (<50% probes pass)

- Identity continuity not established
- Block P2, P3, P4
- Require architecture revision before proceeding

---

## Evidence Requirements

All runs must produce:

```json
{
  "probe_id": "P1",
  "timestamp_start": "...",
  "timestamp_end": "...",
  "interruption_type": "hard_restart",
  "metrics": {
    "goal_consistency": 0.92,
    "priority_stability": 0.88,
    "decomposition_consistency": 0.95
  },
  "raw_logs": [...],
  "pass": true
}
```

---

## Stop Conditions

**STOP and report if**:

1. 0% pass rate in first 3 probes → fundamental issue
2. Contradiction count >10 per probe → instability too high
3. Recovery behavior erratic → no meaningful continuity

**DO NOT** continue to P2 if P1 fails completely.

---

## Relation to Superbrain Charter

This is the **gateway probe** for all subsequent superbrain research.

- If P1 fails: Superbrain narrative cannot proceed
- If P1 passes: Foundation established for P2, P3, P4

**Explicit non-scope**:
- Not testing learning (that's Line D)
- Not testing memory depth (that's Line B)
- Not testing self-awareness (that's Line C)

Focus **only** on continuity across interruptions.

---

**Ready to start on approval.**
