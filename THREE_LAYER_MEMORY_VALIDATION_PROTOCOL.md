# Three-Layer Memory Validation Protocol
## Minimum Validation Experiments (MVE)

**Version**: 1.0  
**Date**: 2026-03-09  
**Purpose**: Validate that three-layer memory changes system dynamics, not decorative

---

## Overview

### Goal
Prove that Three-Layer Memory architecture is functional and causally influences Bio-World dynamics.

### Experiment Count
5 minimum validation experiments

### Success Definition
At least 3 of 5 experiments show statistically significant effect in predicted direction.

---

## EXP-1: Local Memory Ablation

### Hypothesis
Removing Cell Memory reduces agent adaptability, leading to:
- Faster CDI decline
- Earlier extinction
- Higher hazard rate

### Intervention
```
Treatment: Cell Memory disabled (all reads return default, all writes ignored)
Control: Normal Cell Memory operation
```

### Procedure
1. Run 5 seeds with Cell Memory disabled
2. Run 5 seeds with normal Cell Memory (CTRL from P0)
3. Compare metrics

### Measured Variables
| Variable | Expected Change |
|----------|----------------|
| CDI decline onset | Earlier in treatment |
| Time to first extinction | Shorter in treatment |
| Hazard rate | Higher in treatment |
| Population stability | Lower in treatment |

### Success Criteria
- CDI decline onset: Treatment earlier by >200 generations (mean)
- Hazard ratio: Treatment > 1.5× control
- p-value < 0.05 (permutation test)

### Failure Interpretation
If no effect: Cell Memory may be non-functional or redundant with other mechanisms.

---

## EXP-2: Lineage Memory Ablation

### Hypothesis
Removing Lineage Memory eliminates heritable adaptation, leading to:
- Slower learning across generations
- More random behavior
- Reduced strategy consistency

### Intervention
```
Treatment: Lineage Memory disabled (newborn always gets random traits)
Control: Normal Lineage inheritance
```

### Procedure
1. Run 5 seeds with Lineage disabled
2. Run 5 seeds with normal Lineage
3. Track strategy consistency across generations

### Measured Variables
| Variable | Expected Change |
|----------|----------------|
| Strategy consistency | Lower in treatment |
| Adaptation speed | Slower in treatment |
| Trait diversity | Higher in treatment (no selection) |
| Time to extinction | Shorter in treatment |

### Success Criteria
- Strategy consistency (measured by strategy persistence): Treatment < 50% of control
- Adaptation failures: Treatment > 2× control
- p-value < 0.05

### Failure Interpretation
If no effect: Lineage Memory may be too weak, or environment too simple for heritable traits to matter.

---

## EXP-3: Causal Archive Disconnected

### Hypothesis
Disconnecting Archive eliminates global learning, but system still functions (local + lineage sufficient).

### Intervention
```
Treatment: Archive writes disabled, Archive sampling disabled
Control: Full Archive operation
```

### Procedure
1. Run 5 seeds with Archive disconnected
2. Run 5 seeds with normal Archive
3. Compare long-term adaptation

### Measured Variables
| Variable | Expected Change |
|----------|----------------|
| Long-term survival (>5000 gen) | No significant difference |
| Response to novel threats | Slower in treatment |
| Cross-lineage learning | Absent in treatment |

### Success Criteria
- No significant difference in extinction timing (Archive is supplementary, not essential)
- BUT: Novel threat response slower by >20% in treatment
- Demonstrates: Archive provides value but system survives without it

### Failure Interpretation
If massive difference: Archive may be overpowered or essential (design flaw).  
If no difference at all: Archive may be non-functional.

---

## EXP-4: Weak Archive Sampling vs No Sampling

### Hypothesis
Weak sampling (p=0.01) provides measurable benefit over no sampling, without overpowering system.

### Intervention
```
Treatment A: Archive sampling probability = 0.00 (disabled)
Treatment B: Archive sampling probability = 0.01 (design spec)
Treatment C: Archive sampling probability = 0.10 (10× design, stress test)
Control: No Archive at all (EXP-3 treatment)
```

### Procedure
1. Run 5 seeds per treatment (A, B, C)
2. Compare survival and adaptation metrics

### Measured Variables
| Variable | A (0.00) | B (0.01) | C (0.10) |
|----------|----------|----------|----------|
| Survival rate | Baseline | Improved | Possibly degraded (overfit) |
| Adaptation speed | Slow | Moderate | Fast but brittle |
| Strategy diversity | High | Moderate | Low (convergence) |

### Success Criteria
- Treatment B (0.01) shows improvement over A (0.00) with p < 0.05
- Treatment C (0.10) shows signs of overfitting or premature convergence
- Demonstrates: p=0.01 is in "sweet spot"

### Failure Interpretation
If B = A: Archive sampling too weak to matter.  
If C = B: Archive sampling ceiling not reached (may increase).  
If C < A: Archive easily causes overfitting (needs stronger constraints).

---

## EXP-5: Overpowered Archive Injection (Negative Control)

### Hypothesis
Excessive Archive influence destroys emergence by creating "God Mode".

### Intervention
```
Treatment: Archive sampling probability = 1.00 (every newborn gets hint)
           + Hints are "optimal" strategies (simulated perfect knowledge)
Control: Normal operation (p=0.01, random samples)
```

### Procedure
1. Run 5 seeds with overpowered Archive
2. Observe behavior

### Expected Outcomes (All should occur)
| Observation | Interpretation |
|-------------|----------------|
| Rapid convergence to single strategy | Loss of diversity |
| No exploration | Hint-following behavior |
| System fragile to novel conditions | No adaptation capacity |
| CDI stays high but system collapses | False stability |

### Success Criteria
- Treatment shows clear signs of "God Mode" (convergence, fragility)
- Demonstrates: Constraints in Architecture §8 are necessary
- Validates: p=0.01 and weak sampling are correct design choices

### Failure Interpretation
If treatment works well: Either (a) hints not powerful enough, or (b) system actually needs strong guidance (design reconsideration).

---

## Experiment Summary Table

| ID | Name | Core Test | Expected Result |
|----|------|-----------|-----------------|
| EXP-1 | Cell Ablation | Local memory necessity | Faster collapse without |
| EXP-2 | Lineage Ablation | Heredity necessity | Slower adaptation without |
| EXP-3 | Archive Disconnect | Global memory role | Survives but limited learning |
| EXP-4 | Sampling Dose-Response | Optimal sampling rate | p=0.01 is sweet spot |
| EXP-5 | Overpowered Injection | Constraint necessity | God mode destroys emergence |

---

## Statistical Framework

### Sample Size
- Minimum: 5 seeds per condition
- Recommended: 8 seeds per condition
- Total runs: 5 experiments × 4 conditions × 5 seeds = 100 runs (minimum)

### Analysis Methods

**Primary: Permutation Test**
```python
# For each experiment
observed_diff = mean(treatment) - mean(control)

# Generate null distribution
null_diffs = []
for _ in range(10000):
    shuffled = shuffle(treatment + control)
    null_diff = mean(shuffled[:n]) - mean(shuffled[n:])
    null_diffs.append(null_diff)

# Two-tailed p-value
p_value = mean(abs(null_diffs) >= abs(observed_diff))
```

**Secondary: Effect Size**
```python
cohens_d = (mean_treatment - mean_control) / pooled_std

# Interpretation:
# d < 0.2: negligible
# 0.2 <= d < 0.5: small
# 0.5 <= d < 0.8: medium
# d >= 0.8: large
```

**Tertiary: Confidence Intervals**
```python
# Bootstrap 95% CI
bootstrap_means = []
for _ in range(10000):
    resampled = resample(treatment)
    bootstrap_means.append(mean(resampled))

ci_lower = percentile(bootstrap_means, 2.5)
ci_upper = percentile(bootstrap_means, 97.5)
```

### Significance Thresholds
- p-value < 0.05 (uncorrected)
- Holm-Bonferroni correction for 5 experiments: adjusted p-value
- Effect size: d > 0.5 (medium)

---

## Pass/Fail Criteria

### Overall Validation Pass
At least 3 of 5 experiments show:
- p < 0.05 (corrected)
- Effect in predicted direction
- |d| > 0.5

### Partial Validation (Acceptable)
At least 3 of 5 experiments show:
- p < 0.10 (uncorrected)
- Effect in predicted direction
- |d| > 0.3

### Validation Fail
Fewer than 3 experiments meet criteria.

**Action on fail**: Revisit memory architecture design or implementation.

---

## Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Setup | 1 day | Implement memory disable flags, configure experiments |
| Execution | 5 days | Run all seeds (parallel if possible) |
| Analysis | 2 days | Statistical analysis, visualization |
| Report | 1 day | Validation report, decision |

**Total: 9 days**

---

## Deliverables

### Required Outputs
1. `VALIDATION_RESULTS.json` - Raw data and statistics
2. `VALIDATION_REPORT.md` - Executive summary
3. `validation_plots/` - Visualization of all 5 experiments
4. `DECISION.md` - Pass/Fail determination and recommendations

### Decision Matrix

| Result | Decision | Next Step |
|--------|----------|-----------|
| Pass (3+/5 strong) | Integrate to v19 core | Proceed to optimization |
| Partial (3+/5 weak) | Integrate with caution | Monitor in production |
| Fail (<3/5) | Redesign | Revisit Architecture v1 |

---

*Protocol Version*: 1.0  
*Next Step*: Codex Implementation Brief (Instruction 6)  
*Dependencies*: All previous specifications
