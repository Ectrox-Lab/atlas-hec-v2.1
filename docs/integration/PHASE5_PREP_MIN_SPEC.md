# Phase 5 Prep - Minimal Scale-Up Specification

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Status**: CONDITIONAL_TEMPLATE - Only if Phase 4 = GO

---

## Activation Condition

**This document is ONLY valid if Phase 4 Triage = GO**

If Phase 4 = HOLD or NO-GO, ignore this document.

---

## Minimal Scale-Up Parameters

### Seeds Increase

| Current | Target | Increase |
|---------|--------|----------|
| 3 seeds | 5 seeds | +2 seeds |

**Rationale**: Reduces seed variance, enables better statistics  
**Cost**: +67% compute  
**Risk**: Low

### Generations Increase

| Current | Target | Increase |
|---------|--------|----------|
| 1500 | 5000 | +233% |

**Rationale**: Capture long-term dynamics, more extinction events  
**Cost**: +233% compute  
**Risk**: Medium (longer time to results)

### Grid & Population

| Parameter | Current | Target | Change |
|-----------|---------|--------|--------|
| Grid | 25×25×8 | Keep same | None |
| Max population | 3000 | Keep same | None |
| Initial population | 300 | Keep same | None |

**Rationale**: Focus on temporal extension before spatial

---

## Conditions to Retain

| Condition | Retain? | Reason |
|-----------|---------|--------|
| baseline_full | ✓ YES | Reference |
| no_L2 | ✓ YES | Critical for R2 |
| L3_off | ✓ YES | Control |
| L3_real_p001 | ✓ YES | Reference |
| L3_shuffled_p001 | ✓ YES | Critical for R1 |

**All 5 conditions retained** - No removal

---

## Conditions to Drop

**NONE**

Do not drop any conditions in Phase 5. Keep full comparison set.

---

## Priority Charts (Still First)

### Chart 1: Lineage Diversity Trajectory (MUST HAVE)

**X**: generation (0-5000)  
**Y**: lineage_diversity  
**Lines**: 5 conditions  
**Window**: Rolling 100-generation mean

**What to see**:
- baseline: stable or slowly declining
- no_L2: clearly lower by generation 1000
- L3_off: different pattern
- L3_real ≈ L3_shuffled

### Chart 2: Archive Activity Over Time (MUST HAVE)

**X**: generation  
**Y**: archive_sample_attempts (cumulative)  

**What to see**:
- Slope ~0.01 × births
- No saturation

### Chart 3: Strategy Entropy Distribution (MUST HAVE)

**X**: condition  
**Y**: strategy_entropy (endpoint at 5000)  
**Type**: Box plot with 5 seeds × 8 universes = 40 points per condition

**What to see**:
- no_L2 lower than baseline
- Clear separation

---

## Secondary Charts (If Time Permits)

### Chart 4: Survival Curves

**X**: generation  
**Y**: survival probability  
**Lines**: 5 conditions

### Chart 5: Top1 Lineage Share Over Time

**X**: generation  
**Y**: top1_lineage_share  
**Lines**: 5 conditions

### Chart 6: Collapse Event Timeline

**X**: generation  
**Y**: cumulative collapse_event_count  
**Lines**: 5 conditions

---

## Total Compute Budget

| Phase | Runs | Gens/Run | Total Gen-Runs |
|-------|------|----------|----------------|
| Phase 4 | 120 | 1500 | 180,000 |
| Phase 5 | 200 | 5000 | 1,000,000 |

**Increase**: 5.6× total compute

**Time Estimate**:
- Phase 4: ~4 hours
- Phase 5: ~24 hours

---

## Success Criteria for Phase 5

### Statistical Power

- [ ] Cohen's d > 0.5 for baseline vs no_L2
- [ ] p < 0.01 for primary comparisons
- [ ] At least 10 extinction events observed

### Falsification Checks

- [ ] R1: L3_real vs L3_shuffled |d| < 0.2
- [ ] R2: baseline vs no_L2 d > 0.5
- [ ] R5: All fields show variance σ² > 0.001

### Data Quality

- [ ] 95%+ completion rate
- [ ] No fields with >10% missing
- [ ] All values in valid ranges

---

## Execution Commands

### Full Phase 5 Run

```bash
#!/bin/bash
# phase5_run.sh

CONDITIONS=("baseline_full" "no_L2" "L3_off" "L3_real_p001" "L3_shuffled_p001")
SEEDS=(1001 1002 1003 1004 1005)
TICKS=5000
UNIVERSES=8

for condition in "${CONDITIONS[@]}"; do
  for seed in "${SEEDS[@]}"; do
    echo "Running $condition seed=$seed..."
    ./p1_experiment \
      --group "$condition" \
      --seed "$seed" \
      --ticks "$TICKS" \
      --universes "$UNIVERSES" \
      --output-dir "phase5_outputs/${condition}/seed_${seed}"
  done
done
```

### Validation

```bash
# Check completion
find phase5_outputs -name "population.csv" | wc -l
# Expected: 200

# Run falsification checks
python3 falsification_check.py phase5_outputs/
```

---

## What NOT to Add in Phase 5

- ☐ New experimental conditions
- ☐ New metrics (keep the 7 required_now only)
- ☐ Grid size changes
- ☐ Population size changes
- ☐ Mutation rate changes
- ☐ Boss difficulty changes

**Stay minimal. Validate core hypothesis first.**

---

## Transition to Phase 6

Phase 6 (if Phase 5 succeeds):
- Add new conditions (e.g., different p values)
- Add reserved_next metrics
- Integrate ContinuityProbe
- Long runs (10000+ gens)

**Only after Phase 5 confirms hypothesis.**

---

**Status**: CONDITIONAL - Activate only if Phase 4 = GO  
**Last Updated**: 2026-03-09
