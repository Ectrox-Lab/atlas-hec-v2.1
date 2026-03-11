# Phase 2 Stage-2: Scale-Up Validation - Execution Plan

## Status
- **Stage-1:** ✅ COMPLETE (all 4 envs ≥ 2/3 pass)
- **Stage-2:** 🚀 READY TO EXECUTE

---

## Configuration

| Parameter | Value |
|-----------|-------|
| Seeds | 5 |
| Ticks | 3000 |
| Environments | 4 |
| Total runs | 20 |
| Method | Independent environment execution |

---

## Pass Criteria

### Required (Blockers)
| Environment | Min Pass Rate | Notes |
|------------|---------------|-------|
| HubFailureWorld | ≥ 3/5 (60%) | Critical gate |
| RegimeShiftWorld | ≥ 3/5 (60%) | Critical gate |
| ResourceCompetition | ≥ 3/5 (60%) | Overflow risk monitored |
| MultiGameCycle | ≥ 3/5 (60%) | Coordination gate |

### Quality Gates
- **No degradation:** Pass rates should not drop >10% vs Stage-1 baseline (67%)
- **Stability:** Population trajectories consistent across seeds
- **Overflow check:** ResourceCompetition population < 5000

---

## Execution Steps

### Step 1: Pre-flight Check
```bash
cargo build --release --bin phase2_stage2
```

### Step 2: Execute Batch
```bash
cargo run --release --bin phase2_stage2 --no-default-features
```
Expected runtime: ~5-10 seconds

### Step 3: Verify Results
Check output for:
- All environments ≥ 3/5 pass
- Critical gates (HubFailure, RegimeShift) passing
- No degradation alerts

### Step 4: Export
Results saved to: `/tmp/phase2_stage2_results.csv`

---

## Success Criteria Checklist

- [ ] HubFailureWorld ≥ 3/5 pass
- [ ] RegimeShiftWorld ≥ 3/5 pass
- [ ] ResourceCompetition ≥ 3/5 pass
- [ ] MultiGameCycle ≥ 3/5 pass
- [ ] No degradation >10% vs Stage-1
- [ ] ResourceCompetition population controlled

---

## Post-Stage-2 Decision Tree

### If All Pass ✅
→ Proceed to **Phase 3: Long-Horizon Stress**
- 10k+ ticks
- Rapid regime shifts
- Population shocks
- Cascade failure tests

### If Critical Gates Fail ❌
→ Diagnose and potentially retune
- HubFailureWorld: Check recovery logic
- RegimeShiftWorld: Check adaptation triggers

### If ResourceCompetition Overflow ❌
→ Emergency fix required
- Reduce food spawn
- Increase metabolism
- Lower reproduction rate

---

## Files

| File | Purpose |
|------|---------|
| `phase2_stage2.rs` | Main runner |
| `PHASE2_STAGE2_EXECUTION.md` | This document |
| `/tmp/phase2_stage2_results.csv` | Output data |

---

*Ready to execute. Run: `cargo run --release --bin phase2_stage2`*
