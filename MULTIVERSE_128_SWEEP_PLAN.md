# MULTIVERSE 128 SWEEP PLAN

**Version**: 1.0  
**Date**: 2026-03-13  
**Status**: STAGE 1 PREP  
**Scope**: Upgrade single-instance to 128-parallel universe sweep

---

## Current State vs Target

| Aspect | Current | Target |
|--------|---------|--------|
| Instances | 3 (single each) | 128 (parallel universes) |
| Resource use | <1% CPU, ~50MB RAM | 128 vCPU, 128-256GB RAM |
| Data diversity | Single path | 128 different configurations |
| Akashic input | Sequential batches | Bulk multiverse ingest |
| Goal | Mechanism validation | Structure differentiation |

---

## 128 Universe Experiment Matrix

### 4 Dimensions × 4 Levels × 2 Repeats = 128

**Dimension 1: Environmental Pressure**
| Level | Description | Resource Pressure |
|-------|-------------|-------------------|
| 1. Low | Steady light load | 10 tasks/min |
| 2. Medium | Normal operational | 30 tasks/min |
| 3. High | Saturated input | 100 tasks/min |
| 4. Bursty | Spike-and-recover | 0→200→0 tasks/min |

**Dimension 2: Specialist Perturbation**
| Level | Description | Error Injection |
|-------|-------------|-----------------|
| 1. None | Clean execution | 0% error |
| 2. Weak mismatch | Occasional wrong specialist | 10% error |
| 3. Moderate mismatch | Frequent misassignment | 25% error |
| 4. Adversarial bias | Systematic wrong selection | 40% error |

**Dimension 3: Memory Policy**
| Level | Promotion Threshold | Pruning Strategy |
|-------|---------------------|------------------|
| 1. Conservative | Only institutionalized | Rare pruning |
| 2. Balanced | Validated+ | Moderate pruning |
| 3. Aggressive promotion | Repeated+ | Aggressive pruning |
| 4. Aggressive pruning | High bar | Constant compaction |

**Dimension 4: Delegation Regime**
| Level | Audit Strictness | Escalation Threshold |
|-------|------------------|----------------------|
| 1. Strict | 95% confidence required | Low (frequent escalation) |
| 2. Normal | 80% confidence | Medium |
| 3. Permissive | 60% confidence | High |
| 4. Escalation-heavy | Always double-check | Very low |

### Universe ID Format
```
universe_{pressure}{perturb}{memory}{delegation}_{repeat}

Example:
- universe_3112_1: High pressure, weak mismatch, aggressive promo, strict, repeat 1
- universe_1243_2: Low pressure, adversarial, conservative, escalation-heavy, repeat 2
```

---

## Three-Line Upgrade

### G1 → Multiverse Long-Horizon Stress Test

**Per Universe**:
```python
# universe_<id>/g1_agent.py
agent = Agent(
    pressure=config.pressure_level,  # 1-4
    perturbation=config.perturb_level,  # 1-4
    goal="Build reliable governance",
    runtime=72h  # or accelerated
)

for hour in range(72):
    for tick in range(tasks_per_minute):
        task = generate_task(pressure_profile)
        result = agent.execute(task, perturbation=config.perturb)
        
        drift = measure_goal_drift(agent)
        hijack = detect_hijack(agent, config.perturb)
        memory = agent.memory.size()
        rollback = agent.rollback_count
        
        write_to(f"g1_universe_{id}.csv", {
            hour, tick, drift, hijack, memory, rollback
        })

write_summary(f"summary_{id}.json")
```

**Output per universe**:
- `g1_universe_<id>.csv` — Timeseries
- `drift_events_<id>.jsonl` — Drift incidents
- `summary_<id>.json` — Aggregated metrics

### E1 → Multiverse Delegation Benchmark

**Per Universe**:
```python
# universe_<id>/e1_delegation.py
executive = Executive(
    perturbation=config.perturb_level,
    delegation_regime=config.delegation_level
)

for batch in range(batches):
    tests = generate_tests(perturbation=config.perturb)
    
    for test in tests:
        decomposition = executive.decompose(test)
        specialist = executive.select(decomposition, regime=config.delegation)
        audit = auditor.verify(specialist, strictness=config.delegation)
        rollback = rollback_if_needed(audit)
        
        record_result(f"e1_results_{id}.jsonl", {
            test_id, correct, audit_passed, rollback_success
        })

generate_matrix(f"confusion_matrix_{id}.json")
analyze_failures(f"failure_modes_{id}.md")
```

**Output per universe**:
- `e1_results_<id>.jsonl` — Per-test results
- `confusion_matrix_<id>.json` — Performance matrix
- `failure_modes_<id>.md` — Failure analysis

### Akashic → Unified Aggregation Layer

**Ingest Pattern** (not direct write):
```python
# akashic/multiverse_ingest.py

# Stage 1: Collect from all universes
for universe_id in range(128):
    ingest_g1(f"universe_{universe_id}/summary.json")
    ingest_e1(f"universe_{universe_id}/confusion_matrix.json")

# Stage 2: Cross-universe analysis
aggregate_evidence_levels()
promote_multiverse_policies()  # Policies that work across universes
adjudicate_cross_universe_conflicts()
extract_failure_archetypes()
compute_routing_priors()

# Stage 3: Write unified outputs
write("multiverse_digest.json")
write("promoted_policies.json")  # Universe-robust policies
write("failure_atlas.json")  # Failure mode taxonomy
write("routing_priors.json")  # Context-dependent routing
```

**Unified Outputs**:
- `multiverse_digest.json` — Cross-universe summary
- `promoted_policies.json` — Robust policies (work in >80% universes)
- `failure_atlas.json` — Failure archetypes by condition
- `routing_priors.json` — Optimal routing by context

---

## Resource Budget

### Per Universe (Conservative)
```
CPU: 1 vCPU (lightweight Python)
RAM: 1-2 GB (limited memory growth)
Storage: ~100 MB per universe (logs + outputs)

128 universes:
- CPU: 128 vCPU (fits in 128C)
- RAM: 128-256 GB (fits in 512GB)
- Storage: ~12.8 GB total
```

### Resource Distribution
```
G1 universes: 64 instances (drift monitoring focus)
E1 universes: 48 instances (delegation testing focus)
Akashic aggregation: 16 instances (bulk processing)

Total: 128 instances
```

---

## Three-Stage Deployment

### Stage 1: 16 Universes (Validation)
**Goal**: Verify orchestration, file structure, Akashic ingest

**Selection**:
- 2 pressure × 2 perturb × 2 memory × 2 delegation = 16
- Include extremes (1111, 4444) and balanced (2222, 3333)

**Validation Checklist**:
- [ ] All 16 instances start without error
- [ ] File structure correct per universe
- [ ] No cross-universe interference
- [ ] Akashic can read all 16 summaries
- [ ] Resource usage within budget

**Duration**: 1-2 hours or 72h accelerated

### Stage 2: 32 Universes (Pattern Detection)
**Goal**: Verify metrics differentiate, structure emerges

**Selection**:
- Add 16 more configurations
- Include edge cases (1444, 4111, etc.)

**Validation Checklist**:
- [ ] Drift patterns diverge by pressure level
- [ ] Delegation accuracy correlates with perturbation
- [ ] Memory policy affects promotion rate
- [ ] Akashic identifies cross-universe patterns

**Duration**: Full 72h run

### Stage 3: 128 Universes (Full Sweep)
**Goal**: Complete multiverse coverage

**Selection**:
- All 4×4×4×4 combinations
- 2 repeats for statistical validity

**Success Criteria**:
- [ ] 128 universes complete
- [ ] Multiverse digest generated
- [ ] Robust policies identified
- [ ] Failure archetypes cataloged
- [ ] Routing priors computed

**Duration**: Full 72h run

---

## Risk Mitigation

### Risk 1: Akashic Write Bottleneck
**Mitigation**: 
- Universes write to local files first
- Akashic batch-ingests (not real-time)
- Staggered ingest schedule

### Risk 2: Log Explosion
**Mitigation**:
- Per-universe: Summary + compact timeseries only
- Full logs: Optional, compressed, rotated
- Retention: 7 days then archive

### Risk 3: Orchestration Failure
**Mitigation**:
- Stage 1 validates orchestration
- Auto-restart on failure (max 3 retries)
- Checkpoint every hour

### Risk 4: Resource Exhaustion
**Mitigation**:
- Monitor CPU/RAM per universe
- Kill + restart heavy consumers
- Graceful degradation (reduce to 64 universes)

---

## Output Structure

```
multiverse_sweep/
├── stage_1_16/
│   ├── universe_1111_1/
│   │   ├── g1_universe_1111_1.csv
│   │   ├── drift_events_1111_1.jsonl
│   │   ├── summary_1111_1.json
│   │   ├── e1_results_1111_1.jsonl
│   │   ├── confusion_matrix_1111_1.json
│   │   └── failure_modes_1111_1.md
│   ├── universe_1111_2/
│   │   └── ...
│   └── ... (16 total)
├── stage_2_32/
│   └── ... (32 total)
├── stage_3_128/
│   └── ... (128 total)
└── akashic_aggregated/
    ├── multiverse_digest.json
    ├── promoted_policies.json
    ├── failure_atlas.json
    └── routing_priors.json
```

---

## Immediate Next Action

**Start Stage 1**: Deploy 16 universes

**Command**:
```bash
./multiverse_launch.py --stage 1 --count 16 --matrix 2x2x2x2
```

**First Validation** (30 minutes):
- All 16 PIDs running
- 16 output directories created
- Files growing
- No errors in logs

---

**Target**: True multiverse — 128 parallel experiments, structured differentiation, unified Akashic learning.
