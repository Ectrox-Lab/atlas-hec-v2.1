# Implementation Plan — Workload First, Launch Later

**Date**: 2026-03-13  
**Git**: fa2a20b  
**Mode**: IMPLEMENTATION FIRST  
**Current Status**: All experiments NOT_STARTED

---

## Rule

> **No dry run, no RUNNING.**
>
> Each line must deliver: code + input + output schema + dry run result.

---

## Implementation Sequence

### Phase 1: Akashic v3 (First — Easiest to Verify)

**Deliverables Required**:
1. [ ] Executable script: `implementations/akashic_v3/workload.py`
2. [ ] Input data: Path to existing experience entries
3. [ ] Output files:
   - `promoted_policies.json` (appending)
   - `conflict_resolution_report.json`
   - `evidence_graded_entries.json`
4. [ ] Dry run result: Processing completes on sample data
5. [ ] RUNNING criteria: CPU usage + file growth visible

**Minimum Workload**:
```python
# implementations/akashic_v3/workload.py
# Input: logs/*.json (experience entries)
# Output: promoted_policies.json, conflict_resolution_report.json

for entry in load_experience_entries():
    grade = assign_evidence_level(entry)  # Real logic
    if grade >= VALIDATED:
        lesson = extract_lesson(entry)
        policy = generate_policy_candidate(lesson)
        append_to_promoted_policies(policy)

for conflict in load_test_conflicts():
    resolution = adjudicate_conflict(conflict)  # Real logic
    append_to_conflict_report(resolution)
```

**Start Condition**: Dry run passes on 100 sample entries

---

### Phase 2: E1 Executive (Second — Medium Complexity)

**Deliverables Required**:
1. [ ] Executable script: `implementations/e1/workload.py`
2. [ ] Input data: 100+ delegation test scenarios
3. [ ] Output files:
   - `e1_results.jsonl` (one line per test)
   - `delegation_confusion_matrix.json`
   - `audit_fail_cases.md`
4. [ ] Dry run result: 100 tests complete
5. [ ] RUNNING criteria: Results file growing, confusion matrix populated

**Minimum Workload**:
```python
# implementations/e1/workload.py
# Input: test_scenarios/delegation_tests.jsonl
# Output: e1_results.jsonl, confusion_matrix.json

for test in load_delegation_tests():
    decomposition = executive.decompose(test.task)
    specialist = executive.select(decomposition)
    audit_pass = auditor.verify(specialist, test.task)
    rollback_success = rollback_if_failed(audit_pass)
    
    append_to_results({
        "task_id": test.id,
        "decomposition_correct": decomposition == test.expected_decomp,
        "specialist_correct": specialist == test.expected_specialist,
        "audit_passed": audit_pass,
        "rollback_success": rollback_success
    })

generate_confusion_matrix()
extract_fail_cases()
```

**Start Condition**: Dry run passes on all 100 tests

---

### Phase 3: G1 Long-Horizon (Last — Highest Risk of Fake Running)

**Deliverables Required**:
1. [ ] Executable script: `implementations/g1/workload.py`
2. [ ] Input data: Agent config + goal spec + task stream
3. [ ] Output files:
   - `g1_timeseries.csv` (appending every tick)
   - `drift_events.jsonl`
   - `specialist_interaction_log.jsonl`
   - `checkpoints/` directory
4. [ ] Dry run result: 1-hour test completes with CSV output
5. [ ] RUNNING criteria: CSV rows increasing every minute

**Minimum Workload**:
```python
# implementations/g1/workload.py
# Input: configs/agent_config.yaml, goals/goal_spec.yaml
# Output: timeseries.csv (1 row per tick), drift_events.jsonl

agent = Agent(config, goal)
for hour in range(72):
    for tick in range(3600):  # 1 tick/sec
        task = task_stream.get()
        result = agent.execute(task)
        
        drift = measure_goal_drift(agent, original_goal)
        hijack = detect_hijack_signals(agent)
        mem = agent.memory.size()
        
        append_to_timeseries({
            "timestamp": now(),
            "hour": hour,
            "tick": tick,
            "drift": drift,
            "hijack_signals": hijack,
            "memory_mb": mem
        })
        
        if hijack:
            append_to_drift_events({"timestamp": now(), "type": "hijack", "details": hijack})
    
    write_checkpoint(agent, f"checkpoints/hour_{hour}.pkl")
```

**Start Condition**: 1-hour dry run completes with consistent CSV output

---

## Implementation Discipline

### For Each Line

```
Step 1: Write workload.py (actual code, not sleep)
Step 2: Prepare input data (real files, not empty)
Step 3: Define output schema (document expected fields)
Step 4: Dry run on sample data (verify completes)
Step 5: Check output files exist and grow
Step 6: Only then mark READY_TO_LAUNCH
Step 7: Launch and verify RUNNING criteria
```

### Forbidden Until Dry Run Passes

- ❌ Nohup launch
- ❌ Status = RUNNING
- ❌ Resource claims ("using 128C")
- ❌ Progress reports ("iteration X")

### Allowed During Implementation

- ✅ Code commits
- ✅ Unit tests
- ✅ Dry run logs
- ✅ Status = IMPLEMENTING

---

## Current Action

**Now**: Start Phase 1 — Implement Akashic v3 workload

**Next**: Deliver dry run result before claiming RUNNING

---

**Mode**: IMPLEMENTATION FIRST  
**Status**: NOT_STARTED → IMPLEMENTING (Akashic v3)
