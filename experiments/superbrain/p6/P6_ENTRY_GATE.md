# P6 Entry Gate

**Purpose:** Ensure P6 implementation starts from a solid, verified foundation  
**Principle:** Prevent 72h run from degenerating into "watch and hope"

---

## Gate Items (All Must Pass)

### Gate 1: P5b Artifacts Reproducible ✅

**Check:** All P5b tests pass on clean environment

```bash
# Verification command
cd experiments/superbrain/p5b
python3 -m pytest test_p5b_core_protection.py test_p5b_core_protection_extended.py test_p5b_week2_minimal_loop.py --tb=no -q

# Expected: 25/25 tests passed
```

**Evidence:**
- ☑ Week 1: 18/18 passed
- ☑ Week 2: 7/7 passed
- ☑ Total: 25/25 tests passing

**Status:** ✅ PASSED (P5b verified)

**Next:** Gate 2 (1h smoke test)

---

### Gate 2: 1-Hour Smoke Test Passes ✅

**Check:** P6 runner completes 1-hour mode without errors

```bash
# Verification
cd experiments/superbrain/p6
python3 -m pytest test_p6_runner.py::test_gate2_1h_smoke_explicit -v
```

**Evidence:**
- ☑ 12 epochs completed
- ☑ 0 core drift
- ☑ All epochs have metrics
- ☑ State machine: INIT → RUN → COMPLETE
- ☑ 13/13 tests passing

**Status:** ✅ PASSED (commit 94808ae)

**Next:** Gate 3 (stop conditions unit tests)

---

### Gate 3: Stop Conditions Coded ✅

**Check:** All 4 hard stops implemented and tested

```bash
# Verification
python3 -m pytest test_p6_stop_conditions.py -v
```

**Required Stops (All Implemented):**
- ☑ Core drift detected → immediate halt
- ☑ 3 epochs recall < 0.6 → halt  
- ☑ Capability diversity < 20% → halt
- ☑ Maintenance overhead > 30% → halt

**Evidence:**
- 10/10 tests passing
- Individual condition tests (8 tests)
- Integration test verifying all 4

**Status:** ✅ PASSED (commit TBD)

**Next:** Gate 4 (critical logging)

---

### Gate 4: Critical Logging Wired ✅

**Check:** All 4 critical metrics logged every epoch

```bash
# Verification
python3 -m pytest test_p6_logging.py -v
```

**Logged Metrics (per epoch):**
- ☑ `core_hash` - Drift detection
- ☑ `detector_recall` - Degradation monitoring
- ☑ `capability_diversity` - Exhaustion monitoring
- ☑ `maintenance_overhead` - Overload monitoring

**Evidence:**
- 10/10 tests passing
- Results saved to `results/P6_final_results.json`
- Checkpoints created at intervals
- All metrics in valid ranges

**Status:** ✅ PASSED (commit TBD)

**Next:** All gates passed → Ready for 24h smoke test

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

## Gate Sign-Off ✅

| Gate | Verified By | Date | Result |
|------|-------------|------|--------|
| 1. P5b reproducible | automated | 2026-03-08 | ✅ PASS |
| 2. 1h smoke test | automated | 2026-03-08 | ✅ PASS |
| 3. Stop conditions | automated | 2026-03-08 | ✅ PASS |
| 4. Critical logging | automated | 2026-03-08 | ✅ PASS |

**All gates passed:** ✅ YES → Proceed to 24h smoke  
**Verification script:** `./run_p6_entry_gate.sh`

### Sign-Off Command

```bash
./run_p6_entry_gate.sh
# Expected: ✅ P6 ENTRY GATE: ALL PASSED
```

---

## Post-Gate Status

```
P6 Entry Gate: ✅ PASSED
       ↓
24h Smoke Test (Stage 1)
       ↓
   ☐ PASS → 72h Primary Run (Stage 2)
   ☐ FAIL → Fix, return to Entry Gate
```

**Next Action:** Execute 24h smoke test

**Command:**
```bash
python3 p6_runner.py  # Configured for 24h mode
```

---

## Archive Note

This Entry Gate was passed on 2026-03-08 with:
- P5b: 25/25 tests passing
- P6 Phase 1-3: 33/33 tests passing
- Total: 58/58 tests passing

P6 implementation ready for long-horizon validation.

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
