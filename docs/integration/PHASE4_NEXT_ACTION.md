# Phase 4 Next Action

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Status**: PENDING_TRIAGE_DECISION

---

## Decision Tree

```
After Phase 4 Triage:
  |
  v
All 4 core questions answered clearly?
  |                    |
  YES                   NO
  |                     v
  |          Any blocker critical?
  |            |            |
  |           YES           NO
  |            |            |
  v            v            v
GO_TO_    NO_GO_      HOLD_FOR_
PHASE5    HYPOTHESIS  FIELD_FIX
```

---

## Option 1: GO_TO_PHASE5_MINI_SCALEUP

### Trigger Conditions (ALL must be met)

- [ ] All 5 conditions runnable (B1 resolved)
- [ ] All 7 fields have real values (B2 resolved)
- [ ] L3_shuffled actually shuffled (B3 resolved)
- [ ] Anti-god-mode preserved (B4 resolved)
- [ ] no_L2 shows expected degeneration (d > 0.3, p < 0.05)
- [ ] L3_real ≈ L3_shuffled OR clear interpretable difference
- [ ] No values out of valid range

### Immediate Actions

1. **Extend runs to 5000 generations**
   ```bash
   ./p1_experiment --ticks 5000 ...
   ```

2. **Increase to 5 seeds**
   ```bash
   for seed in 1001 1002 1003 1004 1005; do ...
   ```

3. **Generate priority charts**
   - Lineage diversity trajectory
   - Archive activity over time
   - Strategy entropy distribution

4. **Run falsification checks**
   ```bash
   python3 falsification_check.py outputs/
   ```

5. **Fill FIRST_COMPARISON_MATRIX with full data**

### What NOT to Do

- ☐ Do NOT add new conditions
- ☐ Do NOT add new metrics yet
- ☐ Do NOT change experimental design
- ☐ Do NOT proceed to 10000+ generations yet

### Success Criteria for Phase 5

- [ ] 120 runs × 5 seeds = 600 total runs
- [ ] All falsification rules checked with high confidence
- [ ] ContinuityProbe integrated
- [ ] Ready for long-term experiments

---

## Option 2: HOLD_FOR_FIELD_FIX

### Trigger Conditions (ANY)

- [ ] Some fields present but constant/suspicious
- [ ] Effect size ambiguous (0.2 < d < 0.5)
- [ ] High seed variance obscures signal
- [ ] L3_shuffled implementation uncertain
- [ ] Minor anti-god-mode concerns

### Immediate Actions

1. **Document specific issues**
   ```markdown
   ## Required Fixes
   - Field X: Currently constant, should vary
   - Condition Y: Exit code non-zero
   ```

2. **File FIELD_FIX_REQUEST with Codex**
   - Use PHASE4_FIELD_FIX_REQUEST.md template
   - Specify exact fields/conditions
   - Set 48-hour deadline

3. **Run extended test (200 generations)** on fixed version
   ```bash
   ./p1_experiment --ticks 200 ...
   ```

4. **Re-run validation**
   ```bash
   python3 validate_csv_fields.py ...
   ```

### What NOT to Do

- ☐ Do NOT proceed to 5000 generations
- ☐ Do NOT add more seeds
- ☐ Do NOT ignore the issues
- ☐ Do NOT proceed with placeholder data

### Resolution Criteria

Hold lifted when:
- [ ] All specified fields fixed
- [ ] Validation passes
- [ ] Quick test (200 gens) shows improvement

---

## Option 3: NO_GO_HYPOTHESIS_FAIL

### Trigger Conditions (ANY)

- [ ] no_L2 ≈ baseline (R2 falsified)
- [ ] L3_real ≈ L3_shuffled AND no_L2 ≈ baseline (full falsification)
- [ ] Values out of range (data integrity failure)
- [ ] Anti-god-mode boundaries violated
- [ ] Conditions fail to execute

### Immediate Actions

1. **Write FAILURE_MEMO**
   - Use PHASE4_FAILURE_MEMO.md template
   - Document exact falsification trigger

2. **Stop all scale-up activities**
   - No longer runs
   - No more seeds
   - No integration work

3. **Preserve what works**
   - Document any salvageable sub-hypotheses
   - Identify alternative directions

4. **Report to stakeholders**
   - Present falsification evidence
   - Recommend next steps (pivot/abort/redesign)

### What NOT to Do

- ☐ Do NOT continue with current design
- ☐ Do NOT ignore falsification
- ☐ Do NOT add complexity to salvage
- ☐ Do NOT blame without evidence

### Post-Decision Options

If NO-GO:
- [ ] Redesign three-layer architecture
- [ ] Test alternative hypotheses
- [ ] Archive current results for post-mortem
- [ ] Define new minimal experiment

---

## Decision Matrix

| Scenario | Q1 Runnability | Q2 Fields Real | Q3 L3 Shuffled | Q4 no_L2 Degeneration | Decision |
|----------|----------------|----------------|----------------|----------------------|----------|
| All Good | ✓ | ✓ | ✓ | ✓ (d>0.3) | GO |
| Minor Issues | ✓ | ⚠ | ✓ | ✓ (d>0.2) | HOLD |
| Major Issues | ✓ | ✗ | ✓ | ✓ | HOLD |
| Hypothesis Fail | ✓ | ✓ | ✓ | ✗ (d<0.2) | NO-GO |
| Full Falsification | ✓ | ✓ | ✗ | ✗ | NO-GO |
| System Failure | ✗ | - | - | - | NO-GO |

Legend: ✓ Pass, ⚠ Marginal, ✗ Fail

---

## Current Status

**Awaiting**: Codex Phase 3 outputs

**Once received**:
1. Run PHASE4_TRIAGE_REPORT
2. Check 4 core questions
3. Apply decision matrix
4. Execute selected option

**No decision can be made without data.**

---

## Quick Reference

### If data looks GOOD
```bash
# GO path
git checkout -b phase5-scaleup
# Extend runs, add seeds
```

### If data looks AMBIGUOUS
```bash
# HOLD path
vim PHASE4_FIELD_FIX_REQUEST.md
# Request specific fixes from Codex
```

### If data shows FAILURE
```bash
# NO-GO path
vim PHASE4_FAILURE_MEMO.md
# Document and report
```

---

**Status**: PENDING_TRIAGE  
**Last Updated**: 2026-03-09
