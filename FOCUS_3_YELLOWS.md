# Focus: 3 Yellows → Green

**Date**: 2026-03-12  
**Git**: da1f916  
**Mode**: Surgical Optimization — No Expansion

---

## Current Readout

| Grid | Status | Meaning |
|------|--------|---------|
| G1 Drift | 🟡 | Light signal, watch for accumulation |
| G1 Hijack | 🟢 | No specialist capture signs |
| G1 Mem | 🟢 | Governance stable |
| E1 Del | 🟡 | **Weakest point — delegation 75%** |
| E1 Audit | 🟢 | Mechanism solid |
| E1 Roll | 🟢 | Recovery working |
| Akashic Evi | 🟡 | Writing, not yet stable |
| Akashic Pro | 🟢 | 12 lessons promoted — real output |
| Akashic Con | 🟡 | **Pending conflicts need resolution** |

---

## Priority 1: E1 Delegation 75% → 80%+

### Diagnosis Required

**Question**: Where does the 25% delegation failure come from?

**Three Hypotheses**:

| Hypothesis | Test | Fix |
|------------|------|-----|
| **H1: Task typing error** | Misclassification of task complexity | Better decomposition rules |
| **H2: Specialist selection error** | Wrong tool picked for task | Enhanced matching logic |
| **H3: Escalation threshold wrong** | Premature escalation or missed escalation | Tune threshold parameters |

### Immediate Actions (Next 6h)

```yaml
focus_scope:
  - ONLY delegation (don't touch audit/rollback)
  - Log every delegation decision
  - Categorize failure mode

data_collection:
  - task_type: simple/medium/complex
  - decomposition_attempt: success/fail
  - specialist_selected: which
  - actual_best_specialist: ground_truth
  - escalation_triggered: yes/no
  - should_have_escalated: ground_truth

analysis:
  - failure_by_type: % failures per task category
  - selection_accuracy: correct / total
  - escalation_precision: true_pos / (true_pos + false_pos)
  - escalation_recall: true_pos / (true_pos + false_neg)
```

### Success Criteria

| Metric | Current | Target | In 6h |
|--------|---------|--------|-------|
| Delegation ratio | 75% | ≥ 80% | ↑ or diagnosed why not |

---

## Priority 2: G1 Drift — Watch, Don't Judge

### Current State
- **Drift**: ~2-3% (🟡)
- **Not yet**: 🔴 (would be >5%)
- **Critical**: Watch trajectory, not snapshot

### Monitoring Focus (Next 6h)

```yaml
drift_analysis:
  trend: increasing / stable / decreasing
  rate: % per hour
  
correlation_check:
  with_memory_growth: correlated?
  with_specialist_interaction: correlated?
  with_task_type: specific patterns?
  
early_warning:
  if_drift_rate_accelerates: flag immediately
  if_exceeds_4%: escalate to human
  if_exceeds_5%: halt for diagnosis
```

### Key Question

> Is drift **accumulating** or **fluctuating around stable**?

- Accumulating → Problem, need intervention
- Fluctuating → Acceptable, continue monitoring

### Success Criteria

| Metric | Current | Watch | Action if |
|--------|---------|-------|-----------|
| Drift | 2-3% | Trend | >4% escalate, >5% halt |

---

## Priority 3: Akashic Conflict — Clear Pending

### Current State
- **Resolved**: 2 conflicts
- **Pending**: 1 conflict
- **Risk**: If adjudication unstable, Akashic becomes "record layer" not "inheritance layer"

### Immediate Actions (Next 6h)

```yaml
conflict_resolution:
  target: clear the 1 pending conflict
  method: automatic adjudication
  fallback: escalate to governance core

validation:
  resolution_correct: verify against ground truth
  no_new_conflicts_introduced: check

stress_test:
  inject_3_new_conflicts: can system resolve?
  resolution_time: < 1 hour target
```

### Success Criteria

| Metric | Current | Target | In 6h |
|--------|---------|--------|-------|
| Pending conflicts | 1 | 0 | ✅ resolved |
| Resolution quality | 2/2 good | 3/3 good | verified |
| New conflicts handled | N/A | 3 injected, 3 resolved | tested |

---

## What We DO NOT Do

| Forbidden | Rationale |
|-----------|-----------|
| ❌ Expand mesh | Delegation not yet solid |
| ❌ Touch 20B mainline | External, not our block |
| ❌ Change red lines | Working, don't break |
| ❌ Treat yellow as stop | Optimize, don't halt |
| ❌ Optimize audit/rollback | Already green, focus on yellow |
| ❌ Full Akashic build | Skeleton first, conflict resolution critical |

---

## Next 6h Targets

| Line | Metric | Current | Target | Verify |
|------|--------|---------|--------|--------|
| E1 | Delegation | 75% | ↑ trend or root cause | Log analysis |
| G1 | Drift | 2-3% | Stable or ↓ | Trajectory check |
| Akashic | Conflicts pending | 1 | 0 | Resolution confirmed |

---

## Warboard Update (Expected in 6h)

```
E1 Del: 🟡 → 🟢 (if ≥80%) or 🟡 with diagnosis
G1 Drift: 🟡 (watch trajectory)
Akashic Con: 🟡 → 🟢 (if 0 pending)
```

---

**One Line**: Optimize 3 yellows. Don't expand. Don't change greens. Push to green in 6h.
