# Task-2: Multi-Stage Pipeline Scheduling

**Status**: 🟢 SPEC DEFINED — Ready for L4-v3  
**Date**: 2026-03-14  
**Rationale**: Closest to existing "coordination-delegation-recovery" semantics

---

## Why Task-2 (Over Task-3/Task-4)

### 1. Semantic Proximity to Existing Mechanisms

**From Stage 3 Analysis (Documented)**:
- D1 strict delegation: stable under pressure, drift ↓ ~33%
- M3 conditional: beneficial at P2, harmful at P3
- P2T3M3D1 / Config 3: current stable sweet spot

**Task-2 directly reuses these patterns**:
- Stage handoff = delegation (D1)
- Stage recovery = memory-based recovery (M3)
- Pressure handling = P2 vs P3 tuning
- Pipeline stability = long-horizon drift control

### 2. Clearer Validator Than Task-1

**Task-1 Problem**: Validator too harsh (14-20% pass rate even for stable families)

**Task-2 Solution**: Borrow from OctopusLike operational envelope:

| Metric | Definition | Source |
|--------|-----------|--------|
| Stage throughput | Tasks completed per stage per unit time | OctopusLike throughput |
| Handoff latency | Time between stage completion and next stage start | Operational metric |
| Failover success | % of stage failures successfully recovered | Failover procedure |
| Degradation containment | Impact radius when one stage degrades | Envelope monitoring |
| Unnecessary rerouting | Reroutes not improving pipeline completion | Alert rules |
| Pipeline completion rate | End-to-end task completion % | Primary success metric |

### 3. Lower Risk Than Task-4, More Mechanism-Focused Than Task-3

| Task | Risk | Focus | Verdict |
|------|------|-------|---------|
| Task-4 (Distributed consensus) | High coordination overhead, seed-sensitive | Consensus algorithms | Too noisy |
| Task-3 (Dynamic resource allocation) | Resource layer focus | Load balancing | Off-topic |
| **Task-2 (Pipeline scheduling)** | **Medium, controllable** | **Stage routing, recovery** | **Optimal** |

---

## Task-2 Definition

### Core Problem

Multi-stage pipeline scheduling with failure recovery under perturbation.

**Input**: Stream of tasks requiring processing through N stages (e.g., ingest → transform → validate → output)

**System Must Decide**:
- Stage assignment (which executor handles which stage)
- Handoff timing (when to pass to next stage)
- Priority ordering (which task first when congested)
- Failure recovery (retry, reroute, rollback)

**Under Constraints**:
- Stage capacity limits
- Dependency ordering (stage N requires stage N-1 complete)
- Perturbation (stage failures, capacity changes)

### Success Metrics (L4-v3 Validator)

```python
TASK2_VALIDATOR = {
    "pipeline_completion_rate": {
        "target": "> 70%",
        "weight": 0.30,
        "rationale": "Primary success metric"
    },
    "stage_throughput": {
        "target": "> baseline",
        "weight": 0.25,
        "rationale": "Efficiency metric"
    },
    "handoff_latency": {
        "target": "< 2x baseline",
        "weight": 0.20,
        "rationale": "Coordination overhead"
    },
    "failover_success": {
        "target": "> 80%",
        "weight": 0.15,
        "rationale": "Recovery capability"
    },
    "degradation_containment": {
        "target": "< 20% cascade",
        "weight": 0.10,
        "rationale": "Stability under stress"
    }
}
```

### Perturbation Model

Based on Task-1 patterns, adapted for pipeline:

| Parameter | Task-1 Equivalent | Pipeline Interpretation |
|-----------|------------------|------------------------|
| Pressure | Arrival rate | Task injection rate |
| Triage | Deadline urgency | Stage priority weights |
| Memory | Recovery state | Pipeline state tracking |
| Delegation | D1/D2 | Stage assignment strictness |

---

## L4-v3 Application

### Mechanism Mapping

| L4-v2 Mechanism | Task-2 Equivalent |
|-----------------|-------------------|
| Trust-based routing | Stage assignment based on executor reliability |
| Adaptive migration | Dynamic stage handoff when executor degrades |
| Recovery sequences | Pipeline rollback / retry sequences |
| Trust update priors | Executor reliability tracking per stage |

### Expected Behavior

**If L4-v3 succeeds**:
- Mechanism bias pushes candidates toward stable stage-coordination patterns
- High-triage (T4) candidates show better handoff latency
- Low-leakage candidates avoid erratic stage rerouting
- Reuse manifests as shared recovery sequences across stages

**Validation**:
- Round B (mechanism bias) > Round A (pure) on pipeline completion
- Winners show consistent stage-handoff patterns
- Anti-leakage prevents "novel but unstable" coordination schemes

---

## Implementation Plan

### Simulator Design

```python
class PipelineSimulator:
    def __init__(self, num_stages=4, stage_capacity=10):
        self.stages = [Stage(i, capacity) for i in range(num_stages)]
        self.tasks = []
        self.metrics = PipelineMetrics()
    
    def run(self, scheduler_config, num_tasks=1000, seed=None):
        # Generate task arrival stream
        # For each task, decide stage assignment
        # Handle handoffs, failures, recovery
        # Track pipeline completion, latency, reroutes
        return self.metrics
```

### Baseline

Simple FIFO stage assignment with fixed retry.

### Adaptive Scheduler

Trust-based stage assignment + adaptive handoff + recovery sequences.

### Parameters (P/T/M/D Mapping)

| Parameter | Pipeline Interpretation | Range |
|-----------|------------------------|-------|
| P (pressure) | Task injection rate multiplier | 1.0 - 3.0 |
| T (triage) | Stage priority weight granularity | 1 - 5 |
| M (memory) | Pipeline state history length | 1 - 5 |
| D (delegation) | Stage assignment strictness | 1 (strict) - 2 (flexible) |

---

## Relationship to Existing Assets

### Reuses from Task-1

- Trust update dynamics (decay/recovery rates)
- Perturbation model (pressure/capacity changes)
- Evaluation methodology (A/B/Ablation)

### Extends Beyond Task-1

- Multi-stage coordination (not single-stage)
- Explicit handoff mechanism
- Pipeline-wide recovery (not single-node)

### Aligns with OctopusLike

- Operational envelope concepts
- Degradation monitoring
- Failover procedures

---

## Validation Criteria

### Hard Targets (L4-v3 Success)

| Metric | Target |
|--------|--------|
| Round B approve rate | > Round A + 15% |
| Reuse rate | > 60% |
| Leakage | < 10% |
| Control purity | Round A = Ablation (±5%) |

### Soft Targets

| Metric | Target |
|--------|--------|
| T4 share in winners | > 50% |
| Pipeline completion | > 70% for winners |
| Failover success | > 80% for winners |

---

## Next Steps

1. [ ] Build Task-2 simulator (adapt from Task-1)
2. [ ] Define baseline scheduler
3. [ ] Design L4-v3 mechanism-first package
4. [ ] Execute L4-v3 (Round A/B/Ablation)
5. [ ] Validate against targets

---

**Status**: SPEC COMPLETE  
**Ready for**: Simulator implementation  
**Blocked by**: None

---

*Task-2 Specification*  
*Selected for L4-v3: Multi-stage pipeline scheduling*
