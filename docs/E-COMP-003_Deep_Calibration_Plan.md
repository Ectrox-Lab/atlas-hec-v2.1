# E-COMP-003 Deep Calibration Plan

**Status**: 🟢 APPROVED — Variable Isolation & Anti-Leakage Strength Scan  
**Date**: 2026-03-14  
**Decision**: Option A (Deep Calibration)

---

## Goal

**Primary Question**: Why does mechanism bias + anti-leakage underperform pure exploration?

**Sub-questions**:
1. Is anti-leakage too aggressive, filtering viable candidates?
2. Is mechanism package semantic incorrect?
3. Is Task-1 validator noise too high?

**Approach**: Systematic variable isolation + strength scanning

---

## Phase 1: Variable Isolation Matrix

### 4 Test Conditions

| Condition | Mechanism Bias | Anti-Leakage | Purpose |
|-----------|---------------|--------------|---------|
| **A** | OFF | OFF | Baseline (pure exploration) |
| **B** | ON | OFF | Isolated mechanism bias effect |
| **C** | OFF | ON (0.4) | Isolated anti-leakage effect |
| **D** | ON | ON (0.4) | Full L4-v2 treatment |

**Hypothesis Priority**:
1. H1: Anti-leakage too strong (C < A, D < B)
2. H2: Mechanism package wrong (B < A)
3. H3: Task-1 too noisy (A ≈ B ≈ C ≈ D)

### Sample Size

- Per condition: n=100 candidates
- Total generated: 400 candidates
- Stratified sample to Mainline: n=20 per condition

---

## Phase 2: Anti-Leakage Strength Scan

### Test Conditions (if H1 confirmed in Phase 1)

| Condition | Anti-Leakage Strength | Purpose |
|-----------|---------------------|---------|
| **C1** | 0.0 | Baseline (no penalty) |
| **C2** | 0.2 | Light penalty |
| **C3** | 0.3 | Medium penalty |
| **C4** | 0.4 | Original L4-v2 strength |

**Metrics to Track**:
- Approve rate
- Reuse rate (stable families)
- Leakage rate
- **Sweet spot**: Low leakage + Reasonable approve rate

### Sample Size

- Per strength: n=100 candidates
- Stratified to Mainline: n=20 per strength

---

## Phase 3: Bridge-First Screening (Optional Optimization)

To save Mainline compute, use Bridge-level screening:

1. **Bridge evaluation** (fast, 100 tasks): All 400 candidates
2. **Select top performers** by Bridge metrics
3. **Mainline evaluation** (slow, 500 tasks): Only top 20 per condition

**Trade-off**: Bridge may not perfectly correlate with Mainline, but saves ~80% compute.

---

## Decision Gates

### Gate A1: Variable Isolation Results

**Decision based on Phase 1**:

| Result Pattern | Conclusion | Next Action |
|---------------|------------|-------------|
| C < A and D < B | **H1 confirmed**: Anti-leakage too strong | → Phase 2 (strength scan) |
| B < A and C ≈ A | **H2 confirmed**: Mechanism package wrong | → Option C (redesign package) |
| A ≈ B ≈ C ≈ D | **H3 confirmed**: Task-1 too noisy | → Option B (switch to Task-2) |
| B > A, C ≈ A, D > B | Mechanism good, anti-leakage neutral | Tune mechanism only |

### Gate A2: Strength Scan Results

**Decision based on Phase 2**:

| Finding | Action |
|---------|--------|
| Sweet spot at 0.2-0.3 | Update route_constraints with optimal penalty |
| No sweet spot (all bad) | Anti-leakage fundamentally incompatible with Task-1 |
| 0.0 best (no penalty) | Remove anti-leakage, keep mechanism bias only |

---

## Execution Script

```bash
# Phase 1: Variable Isolation
./run_ecomp003_calib_p1_var_isolation.sh

# Phase 2: Strength Scan (if H1 confirmed)
./run_ecomp003_calib_p2_strength_scan.sh

# Analysis
python3 superbrain/module_routing/calibration_analyzer.py \
    --results /tmp/ecomp003_calibration_results \
    --output-dir docs/research/E-COMP-003/calibration
```

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 2 hours | Variable isolation results |
| Decision | 15 min | H1/H2/H3 determination |
| Phase 2 (if needed) | 2 hours | Optimal anti-leakage strength |
| Analysis | 30 min | Final calibration report |
| **Total** | **~5 hours** | Calibrated mechanism map |

---

## Expected Outcomes

### Best Case (H1 confirmed)
- Anti-leakage was too strong at 0.4
- Sweet spot at 0.2-0.3
- Update v2 package with optimal settings
- Proceed to L4-v3 with confidence

### Medium Case (H2 confirmed)
- Mechanism package semantic wrong
- Need to rebuild from winners (n=9 total from all rounds)
- One more iteration of package design

### Worst Case (H3 confirmed)
- Task-1 validator too noisy for any signal
- Pivot to Task-2 for cleaner validation
- Archive Task-1 learnings

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Still insufficient winners | Use Bridge-level evaluation for larger effective sample |
| Phase 1 inconclusive | Add intermediate conditions (mechanism 0.5, anti-leakage 0.2) |
| Compute too slow | Reduce Mainline to 300 tasks, increase seeds to 5 |

---

## Documentation

All results archived in:
```
docs/research/E-COMP-003/calibration/
├── phase1_var_isolation/
│   ├── condition_A_results.json
│   ├── condition_B_results.json
│   ├── condition_C_results.json
│   ├── condition_D_results.json
│   └── phase1_analysis.md
├── phase2_strength_scan/ (if executed)
│   ├── strength_0.0_results.json
│   ├── strength_0.2_results.json
│   ├── strength_0.3_results.json
│   ├── strength_0.4_results.json
│   └── phase2_analysis.md
└── final_calibration_report.md
```

---

**Approved**: Deep Calibration — Variable Isolation + Strength Scan  
**Primary Goal**: Determine if anti-leakage too strong, package wrong, or Task-1 too noisy  
**Decision Point**: After Phase 1 (variable isolation)

---

*E-COMP-003 Deep Calibration*  
*Date: 2026-03-14*
