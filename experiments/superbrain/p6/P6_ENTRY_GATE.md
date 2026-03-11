# P6 Entry Gate

**Purpose:** Ensure P6 implementation starts from a solid, verified foundation  
**Principle:** Prevent 72h run from degenerating into "watch and hope"

---

## Gate Items (All Must Pass)

### Gate 1: P5b Artifacts Reproducible

**Check:** All P5b tests pass on clean environment

```bash
# Verification command
cd experiments/superbrain/p5b
python3 -m pytest test_p5b_core_protection.py test_p5b_core_protection_extended.py -v
python3 -m pytest test_p5b_week2_minimal_loop.py -v

# Expected: 25/25 tests passed
```

**Evidence:**
- [ ] Week 1: 18/18 passed
- [ ] Week 2: 7/7 passed
- [ ] Checkpoint 1 metrics match baseline
- [ ] Checkpoint 2 metrics match baseline

**Fail Action:** Fix P5b before proceeding

---

### Gate 2: 1-Hour Smoke Test Passes

**Check:** P6 runner completes 1-hour mode without errors

```python
# test_p6_entry_gate.py
def test_p6_1h_smoke():
    config = P6Config(duration_hours=1, epoch_minutes=5)
    runner = P6Runner(config)
    result = runner.run()
    
    assert result.state == RunnerState.COMPLETE
    assert len(result.epochs) == 12  # 60 min / 5 min
    assert all(e.core_hash == result.baseline_hash for e in result.epochs)
```

**Evidence:**
- [ ] 12 epochs completed
- [ ] 0 core drift
- [ ] All epochs have metrics
- [ ] State machine: INIT → RUN → COMPLETE

**Fail Action:** Debug runner before 24h/72h

---

### Gate 3: Stop Conditions Coded

**Check:** All 4 hard stops implemented and tested

```python
# test_p6_stop_conditions.py::test_all_stops
def test_all_stop_conditions():
    """Verify all 4 stop conditions trigger correctly"""
    checker = StopConditionChecker()
    
    # Test each condition
    assert checker._test_core_drift_trigger()
    assert checker._test_detector_degradation_trigger()
    assert checker._test_capability_exhaustion_trigger()
    assert checker._test_maintenance_overload_trigger()
```

**Required Stops:**
- [ ] Core drift detected → immediate halt
- [ ] 3 epochs recall < 0.6 → halt
- [ ] Capability diversity < 20% → halt
- [ ] Maintenance overhead > 30% → halt

**Evidence:** Unit tests for each condition

**Fail Action:** Complete stop condition implementation

---

### Gate 4: Critical Logging Wired

**Check:** All 4 critical metrics logged every epoch

```python
# Required log entries per epoch:
{
    "epoch": N,
    "timestamp": "...",
    "core_hash": "...",           # For drift detection
    "detector_recall_10ep": 0.85,  # For degradation
    "capability_diversity": 0.6,   # For exhaustion
    "maintenance_overhead": 0.05   # For overload
}
```

**Required Logs:**
- [ ] `p6_epoch_metrics.jsonl` - Per-epoch structured data
- [ ] `p6_core_hash.log` - One hash per line, timestamped
- [ ] `p6_stop_events.log` - Any stop condition triggers
- [ ] `p6_recovery_audit.log` - All repair operations

**Verification:**
```bash
# After 1h test
tail -n 12 p6_epoch_metrics.jsonl | jq '.core_hash' | sort | uniq -c
# Expected: 1 unique hash (no drift)
```

**Fail Action:** Complete logging infrastructure

---

## Entry Gate Verification Script

```bash
#!/bin/bash
# run_p6_entry_gate.sh

echo "P6 Entry Gate Verification"
echo "=========================="

# Gate 1: P5b reproducible
echo -n "Gate 1: P5b artifacts... "
cd ../p5b
python3 -m pytest --tb=no -q > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "✓ PASS"; else echo "✗ FAIL"; exit 1; fi

# Gate 2: 1h smoke test
echo -n "Gate 2: 1h smoke test... "
cd ../p6
python3 -m pytest test_p6_entry_gate.py::test_p6_1h_smoke --tb=no -q > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "✓ PASS"; else echo "✗ FAIL"; exit 1; fi

# Gate 3: Stop conditions
echo -n "Gate 3: Stop conditions... "
python3 -m pytest test_p6_stop_conditions.py::test_all_stop_conditions --tb=no -q > /dev/null 2>&1
if [ $? -eq 0 ]; then echo "✓ PASS"; else echo "✗ FAIL"; exit 1; fi

# Gate 4: Logging
echo -n "Gate 4: Critical logging... "
if [ -f "p6_epoch_metrics.jsonl" ] && [ $(wc -l < p6_epoch_metrics.jsonl) -ge 12 ]; then
    echo "✓ PASS"
else
    echo "✗ FAIL"; exit 1
fi

echo ""
echo "=========================="
echo "P6 ENTRY GATE: ALL PASSED"
echo "Ready for 24h smoke test"
echo "=========================="
```

---

## Gate Sign-Off

| Gate | Verified By | Date | Result |
|------|-------------|------|--------|
| 1. P5b reproducible | _________ | _________ | ☐ |
| 2. 1h smoke test | _________ | _________ | ☐ |
| 3. Stop conditions | _________ | _________ | ☐ |
| 4. Critical logging | _________ | _________ | ☐ |

**All gates passed:** ☐ YES → Proceed to 24h smoke  
**Any gate failed:** ☐ NO → Fix and re-verify

---

## Post-Gate Workflow

```
Entry Gate Pass
       ↓
24h Smoke Test (Stage 1)
       ↓
   ☐ PASS → 72h Primary Run (Stage 2)
   ☐ FAIL → Fix, return to Entry Gate
```

---

## Rationale

**Why these 4 gates?**

1. **P5b reproducible:** If P5b doesn't work, P6 has no foundation
2. **1h smoke:** Validates runner mechanics without long wait
3. **Stop conditions:** Safety system must work *before* long run
4. **Critical logging:** If you can't measure drift/degradation/exhaustion/overload, you can't validate P6

**What happens if we skip gates?**

- 72h run crashes at hour 48 → lost time, no data
- Core drift happens but not logged → false PASS
- Stop condition fails → run continues into undefined behavior
- P5b regression undetected → validating broken foundation

---

## Reference

- P5b artifacts: `experiments/superbrain/p5b/`
- P6 design: `P6_LONG_HORIZON_ROBUSTNESS.md`
- P6 implementation: `P6_IMPLEMENTATION_PLAN.md`

---

*Created: 2026-03-08*  
*Status: Active gate - all items must pass before 24h/72h runs*
