# Phase 2 Stage-2: Scale-Up Validation Plan

**Status:** READY TO EXECUTE  
**Goal:** Prove conclusions hold at larger scale  
**Previous:** Stage-1 complete (3×1200 ticks, all envs ≥ 2/3 pass)

---

## Objective

Validate that Stage-1 results (survival, adaptation, coordination) remain stable at increased scale:
- **Duration:** 3000+ ticks (vs 1200 in Stage-1)
- **Seeds:** 5 (vs 3 in Stage-1)
- **Target:** Maintain ≥ 2/3 pass rate across all 4 environments

---

## Configuration

| Parameter | Stage-1 | Stage-2 | Change |
|-----------|---------|---------|--------|
| Seeds | 3 | 5 | +67% |
| Ticks | 1200 | 3000 | +150% |
| Total runs | 12 | 20 | +67% |

---

## Pass Criteria

### Per-Environment
| Environment | Min Pass Rate | Critical? |
|------------|---------------|-----------|
| HubFailureWorld | ≥ 3/5 (60%) | ✓ Yes |
| RegimeShiftWorld | ≥ 3/5 (60%) | ✓ Yes |
| ResourceCompetition | ≥ 3/5 (60%) | No |
| MultiGameCycle | ≥ 3/5 (60%) + no overflow | No |

### Cross-Environment
- **No degradation:** Pass rates should not drop >10% vs Stage-1
- **Stability:** Population trajectories should not show divergence
- **Consistency:** Coordination scores stable across seeds

---

## Execution Plan

### Step 1: Optimize Runner
**Problem:** Stage-2 batch (5×3000) estimated 2-3× Stage-1 runtime
**Solutions to try:**
1. Sequential execution with progress logging
2. Reduce telemetry frequency (100 → 200 ticks)
3. Profile and optimize hot paths if needed

### Step 2: Execute Batch
```
5 seeds × 3000 ticks × 4 environments = 60k ticks total
```

### Step 3: Aggregate Results
- Per-environment pass rates
- Population trajectory comparison vs Stage-1
- Coordination stability metrics
- Recovery time distributions (HubFailure)
- Adaptation event counts (RegimeShift, MultiGameCycle)

### Step 4: Verify Pass/Fail
- Critical gates (HubFailure, RegimeShift): Must ≥ 3/5
- All environments: Must ≥ 3/5
- No degradation vs Stage-1

---

## Output

### Files
| File | Content |
|------|---------|
| `/tmp/phase2_s2_*.csv` | Per-environment trajectories |
| `/tmp/phase2_s2_summary.json` | Aggregate statistics |
| `PHASE2_STAGE2_REPORT.md` | Final report |

### Metrics
- pass_rate per environment
- avg_final_pop vs Stage-1
- avg_coordination vs Stage-1
- stability_score (variance across seeds)
- degradation_flag (true if >10% drop)

---

## Success Criteria

### Must Have (Blocker)
- [ ] HubFailureWorld ≥ 3/5 pass
- [ ] RegimeShiftWorld ≥ 3/5 pass
- [ ] All environments ≥ 3/5 pass

### Should Have (Quality)
- [ ] No degradation >10% vs Stage-1
- [ ] Stable coordination scores
- [ ] No overflow in MultiGameCycle

### Nice to Have (Insight)
- [ ] Recovery time distributions
- [ ] Adaptation event patterns
- [ ] Early-warning indicators

---

## Failure Modes

### If HubFailure < 3/5
→ Recovery logic unstable at scale → Investigate hub knockout handling

### If RegimeShift < 3/5
→ Adaptation breaks down over longer horizon → Check regime detector

### If MultiGameCycle overflow
→ Reproduction control insufficient → Revisit tuning parameters

### If systematic degradation
→ Stage-1 results not scalable → Major architecture review needed

---

## Timeline

| Step | Duration | Blocker? |
|------|----------|----------|
| Runner optimization | 1 session | Yes |
| Batch execution | 1-2 sessions | Yes |
| Result analysis | 0.5 session | Yes |
| Report generation | 0.5 session | No |

---

## Post-Stage-2

If Stage-2 passes:
→ Proceed to **Phase 3: Long-Horizon Stress**
- 10k+ ticks
- Multiple regime shifts
- Population shocks
- Hub cascade failures

If Stage-2 fails:
→ Diagnose degradation source
→ Decide: Fix and retry, or accept Stage-1 as max validated scale

---

*Phase 2 Stage-2: Scale-Up Validation - Ready to execute*
