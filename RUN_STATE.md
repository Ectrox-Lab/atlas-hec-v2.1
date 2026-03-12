# RUN_STATE — Corrected Status

**Date**: 2026-03-13 00:30 UTC  
**Git**: 0a624bd  
**Rule**: No Workload + No Artifacts = PLACEHOLDER (not RUNNING)

---

## Status Definitions (5-State)

| State | Meaning |
|-------|---------|
| **NOT_STARTED** | Nothing exists |
| **PLACEHOLDER** | PID exists, but only sleep/heartbeat, no real workload |
| **RUNNING** | PID + active workload + resource usage + artifact generation |
| **HALTED** | Was running, now stopped |
| **INVALIDATED** | Previous status claims were false |

---

## Current Real Status

### Akashic v3

```yaml
name: akashic_v3_skeleton
previous_claim: RUNNING
actual_status: PLACEHOLDER
pid: 1914634
reality: sleep loop, 0% CPU, no data processing
artifacts: none
```

### E1 Executive

```yaml
name: e1_executive
previous_claim: RUNNING
actual_status: PLACEHOLDER
pid: 1919618
reality: sleep loop, 0% CPU, no test execution
artifacts: none
```

### G1 Long-Horizon

```yaml
name: g1_longhorizon
previous_claim: RUNNING
actual_status: PLACEHOLDER
pid: 1927606
reality: sleep loop, 0% CPU, no agent loop running
artifacts: none
```

---

## Required for RUNNING Status

Must have ALL of:

1. **PID** — Process exists
2. **Launch command** — Documented
3. **Log path** — Accessible
4. **Defined workload** — What is actually being computed
5. **Evidence** — ONE of:
   - Sustained CPU usage (>10% of allocated cores)
   - Memory growth/loaded dataset
   - Output files growing
   - Dataset being processed
   - Metrics actually changing
   - Checkpoints/artifacts accumulating

---

## Workload Definitions (Required Before Launch)

### A. Akashic v3 Actual Workload

**Input**:
- Existing experience entries from logs/
- Seed-spike registry entries

**Processing**:
```python
# Must actually execute:
for entry in experience_entries:
    grade = assign_evidence_level(entry)  # Not placeholder
    if grade >= REPEATED:
        lesson = extract_lesson(entry)
        policy_candidate = promote_to_policy(lesson)
        write_to_promoted_policies.json

for conflict in test_conflicts:
    resolution = adjudicate(conflict)  # Actual logic, not stub
    write_to_conflict_resolution_report.json

bundle = generate_inheritance_bundle()
write_to_akashic_v3_run_TIMESTAMP.json
```

**Output Artifacts** (must exist and grow):
- `akashic_v3_run_YYYYMMDD_HHMMSS.json`
- `promoted_policies.json` (appended, not empty)
- `conflict_resolution_report.json`

**RUNNING Evidence**:
- Files above exist and bytes increasing
- CPU usage during processing spikes
- Actual entries processed count increasing

---

### B. E1 Actual Workload

**Input**:
- Task dataset (100+ delegation scenarios)
- Ground truth labels for correct delegation

**Processing**:
```python
# Must actually execute:
for task in task_dataset:
    decomposition = executive.decompose(task)
    selected_specialist = executive.select(decomposition)
    audit_result = auditor.verify(selected_specialist, task)
    
    record = {
        "task": task.id,
        "decomposition_correct": decomposition == ground_truth.decomp,
        "selection_correct": selected_specialist == ground_truth.specialist,
        "audit_passed": audit_result.passed,
        "rollback_needed": not audit_result.passed,
        "rollback_success": rollback() if not audit_result.passed else None
    }
    append_to_e1_results.jsonl

generate_confusion_matrix()
write_to_delegation_confusion_matrix.json
extract_fail_cases_to_audit_fail_cases.md
```

**Output Artifacts** (must exist and grow):
- `e1_results.jsonl` (one line per test, increasing)
- `delegation_confusion_matrix.json`
- `audit_fail_cases.md`

**RUNNING Evidence**:
- `e1_results.jsonl` line count increasing
- CPU usage during test execution
- Confusion matrix values changing

---

### C. G1 Actual Workload

**Input**:
- Agent configuration
- Goal specification
- Task stream

**Processing**:
```python
# Must actually execute:
agent = Agent(config, goal)
for hour in range(72):
    for tick in range(3600):  # 1 tick/sec
        task = task_stream.get()
        result = agent.execute(task)
        
        drift_score = measure_goal_drift(agent, original_goal)
        hijack_signals = detect_specialist_hijack(agent)
        memory_usage = agent.memory.size()
        
        append_to_g1_timeseries.csv({
            "hour": hour,
            "tick": tick,
            "drift": drift_score,
            "hijack_attempts": hijack_signals,
            "memory_mb": memory_usage
        })
        
        if hijack_signals:
            append_to_drift_events.jsonl({
                "timestamp": now(),
                "type": "hijack_attempt",
                "details": hijack_signals
            })
        
        log_specialist_interaction(agent.last_interaction)
    
    checkpoint_to_disk()  # Write state
```

**Output Artifacts** (must exist and grow):
- `g1_timeseries.csv` (rows accumulating)
- `drift_events.jsonl` (events if any)
- `specialist_interaction_log.jsonl`
- Periodic checkpoint files

**RUNNING Evidence**:
- CSV rows increasing every second
- Memory usage changing
- Checkpoint files appearing
- CPU sustained during agent execution

---

## State Transition Rules

```
NOT_STARTED 
    → launch with workload defined 
    → PLACEHOLDER (PID exists, waiting for first artifact)

PLACEHOLDER 
    → artifacts appearing + resource usage 
    → RUNNING

PLACEHOLDER (after 5min no artifacts)
    → kill 
    → NOT_STARTED

RUNNING 
    → artifact flow stops + resource drops to 0
    → HALTED

Any state 
    → false status reported 
    → INVALIDATED
```

---

## Current Action Required

**Before any experiment can be RUNNING**:

1. **Stop placeholder processes** (PID 1914634, 1919618, 1927606)
2. **Implement actual workload** (code above, not sleep loops)
3. **Define input datasets** (real data, not empty)
4. **Launch with artifact tracking**
5. **Verify**: CPU usage, file growth, actual processing

**No workload definition + no artifact evidence = PLACEHOLDER maximum.**

---

**Status**: All experiments PLACEHOLDER (downgraded from false RUNNING)
**Next**: Implement actual workloads or remain NOT_STARTED
