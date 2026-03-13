# P1 Causal Experiment Protocol v1.0
## Proving CDI as Causal State Variable

**Date**: 2026-03-09  
**Version**: 1.0  
**Objective**: Move CDI from "leading indicator" to "causal state variable"

---

## 1. Core Causal Question

**Primary Proposition**:
```
do(X) → ΔCDI → Δh(t) → Δextinction
```

Where:
- **X**: External intervention on system structural components
- **CDI**: Complexity/structural quality state variable  
- **h(t)**: Extinction hazard rate
- **extinction**: Extinction timing / probability / cascade strength

---

## 2. Causal Identification Strategy

P1 must answer three things:

### 2.1 Does intervention change CDI first?
```
Intervention → CDI shift ✓
```

### 2.2 Does CDI change alter hazard rate?
```
CDI shift → hazard shift ✓
```

### 2.3 Is this not caused by third variables?
- Control seed randomization
- Lock initial conditions
- Single-variable intervention

---

## 3. Experimental Structure

### 3.1 Four Groups

| Group | Intervention | Target |
|-------|-------------|--------|
| **CTRL** | None (baseline) | Reference |
| **P1-A** | Memory KO | CDI component causality |
| **P1-B** | Cooperation suppression | CDI component causality |
| **P1-C** | Boss pressure ↑ | Threshold vs stress separation |

### 3.2 Seed Randomization

**CRITICAL**: All groups use **identical seed set**

```python
seeds = [1, 2, 3, 4, 5]  # Phase 1
# or [1, 2, 3, 4, 5, 6, 7, 8] for Phase 2
```

This enables **paired comparison** across groups.

### 3.3 Initial Conditions Lock

Must be identical across all groups:
- Initial population: 120
- Initial DNA distribution
- Initial resource allocation
- Initial boss layout (except P1-C)
- Initial Akashic state

### 3.4 Single-Variable Intervention

**PROHIBITED**: Multiple simultaneous changes

| Group | Change | Fixed |
|-------|--------|-------|
| P1-A | memory_capacity = 0 | cooperation, boss |
| P1-B | cooperation_willingness × 0.3 | memory, boss |
| P1-C | boss_strength × 1.5 | memory, cooperation |

---

## 4. Dose-Response Design (Phase 2)

### 4.1 Memory Dose

| Level | Memory Capacity |
|-------|----------------|
| CTRL | 100% (baseline) |
| Low | 50% |
| High | 0% (KO) |

### 4.2 Cooperation Dose

| Level | Cooperation Willingness |
|-------|------------------------|
| CTRL | 1.0× |
| Medium | 0.6× |
| Low | 0.3× |

### 4.3 Boss Pressure Dose

| Level | Boss Strength |
|-------|--------------|
| CTRL | 1.0× |
| Medium | 1.25× |
| High | 1.5× |

**Dose-Response Evidence**: Stronger intervention → Earlier CDI decline → Higher hazard → Earlier extinction

---

## 5. Sample Size Design

### Phase 1: Directional Screening
- **n = 3 seeds/group**
- Total: 12 runs
- Purpose: Determine effect direction

### Phase 2: Formal Validation  
- **n = 5-8 seeds/group** (for confirmed effects)
- Total: 20-32 runs
- Purpose: Establish statistical significance

### Why Not 20 Seeds Initially?

P1 is **mechanism validation**, not final universal law statistics.
Use 5-8 seeds to establish clear effects, then decide on expansion.

---

## 6. Primary & Secondary Endpoints

### 6.1 Primary Endpoints (Pre-registered)

Must report:
1. **CDI decline onset** (generation)
2. **Time to population decline** (generation)
3. **Time to first extinction** (generation)
4. **Hazard ratio** (below vs above I_crit)
5. **Estimated I_crit** (fitted value)

### 6.2 Secondary Endpoints

Additional metrics:
- CDI slope
- Extinction cascade size
- Alive universes over time
- Cooperation density
- Memory utilization
- Boss success/failure profile

---

## 7. Statistical Framework

### 7.1 Primary Tests

**Paired comparison** (same seed across groups):

For P1-A / P1-B:
- Δ(CDI decline onset)
- Δ(Time to extinction)
- Δ(Hazard ratio)

For P1-C:
- Δ(I_crit) ≈ 0? (threshold stability)
- Δ(Hazard level) > 0? (stress effect)
- Δ(Extinction timing) earlier? (consequence)

### 7.2 Statistical Methods

**Time-to-event**:
- Kaplan-Meier survival curves
- Cox proportional hazards model

**Threshold stability**:
- Mean ± std
- Coefficient of variation (CV)
- Bootstrap CI

**Group comparison**:
- Permutation test (small sample)
- Bootstrap effect size
- Paired Wilcoxon / paired t-test (distribution-dependent)

### 7.3 Multiple Comparison Correction

3 main experiments → must correct.

**Recommended**: Holm-Bonferroni

Report both:
- Raw p-values
- Corrected p-values

---

## 8. Minimum Standards for Causality

### 8.1 Required Evidence (2 of 3)

1. **Intervention changes CDI**
   - Earlier decline OR steeper slope

2. **CDI change alters hazard**
   - Higher hazard ratio in low-CDI zone
   - Worse survival curve

3. **Extinction dynamics change**
   - Earlier first extinction
   - Faster extinction cascade
   - Steeper alive-universe decline

### 8.2 Dose-Response Evidence

Strongest causal support:
```
Intervention strength ↑ → CDI decline earlier → Hazard ↑ → Extinction earlier
```

---

## 9. Temporal Precedence Proof

### Required Metrics

For each run, extract:
- t_peak_CDI
- t_decline_CDI (start)
- t_decline_population
- t_first_extinction

### Calculate Leads

```
lead_1 = t_decline_population - t_decline_CDI
lead_2 = t_first_extinction - t_decline_CDI
```

### Report

- Per-seed leads
- Group mean and distribution
- Cross-group comparison

---

## 10. Confounding Control

### 10.1 Seed Pairing

**Mandatory**: Same seed across all groups.

Reduces: Random initial trajectory effects

### 10.2 Initial Akashic Fixation

Akashic initial library must be identical snapshot.

Reduces: Different prior knowledge effects

### 10.3 Boss Randomness Fixation

Except P1-C, boss configuration identical.

Reduces: Environmental stochasticity

### 10.4 Analysis Blinding

Analysis scripts should only read:
- run_id
- metrics
- group_label

**Avoid**: Manual cherry-picking during visualization

---

## 11. Adaptive Stopping Rules

### Early Stop (Success)

At n=5 seeds, if ALL criteria met:
- Effect direction consistent
- Effect size ≥ threshold
- Bootstrap CI excludes 0
- Corrected p-value significant

→ **Stop**, mark as "Causality Supported"

### Early Stop (Failure)

At n=5 seeds, if ANY:
- Direction inconsistent across seeds
- Effect size negligible
- Opposite to theory prediction
- No hazard/extinction change

→ **Stop**, mark as "No Support for Causal Effect"

---

## 12. Failure Mode Interpretation

| Scenario | Interpretation |
|----------|---------------|
| CDI changes, extinction doesn't | CDI insufficient for system-level stability |
| Extinction changes, CDI doesn't | Intervention bypasses CDI; CDI incomplete |
| P1-C changes I_crit | Threshold is environment-dependent, not pure structure |
| All directions chaotic | Intervention too weak; CDI definition unstable; seed variance too high |

---

## 13. Pass Criteria

### Weak Pass
At least 1 intervention group shows:
- CDI earlier decline
- Hazard increase
- Extinction earlier

### Medium Pass
At least 2 intervention groups show consistent direction with dose-response evidence.

### Strong Pass
ALL of:
- P1-A/P1-B: Change CDI and extinction dynamics
- P1-C: I_crit stable, hazard curve shifts up
- Multi-group consistency
- Stable effect sizes
- Survives multiple comparison correction

---

## 14. Acceptable Causal Conclusions

### Strong Pass Wording
> "Intervening on memory or cooperation causally alters CDI trajectories and extinction dynamics, supporting CDI as a causal state variable rather than merely a leading indicator."

### Medium Pass Wording
> "Environmental stress modulates extinction hazard without materially shifting the estimated CDI threshold, supporting a distinction between structural criticality and stress modulation."

### Weak/No Pass Wording
> "Current intervention designs do not provide conclusive evidence for CDI as causal state variable. Further refinement of intervention targets or CDI definition may be required."

---

## 15. Required Outputs

| File | Content |
|------|---------|
| `P1_CAUSAL_EXPERIMENT_PROTOCOL.md` | This document |
| `P1_RESULTS_SUMMARY.md` | Executive summary |
| `P1_EFFECT_SIZES.json` | Quantified effects |
| `P1_SURVIVAL_CURVES.png` | KM curves by group |
| `P1_HAZARD_ANALYSIS.json` | Hazard model fits |
| `P1_DOSE_RESPONSE.png` | Dose-response plots |

---

## 16. Recommended Execution Order

### Phase 1: Quick Screen (n=3/group)
1. CTRL vs P1-C (easiest: threshold vs stress)
2. CTRL vs P1-A (clear component manipulation)
3. CTRL vs P1-B (if time permits)

### Phase 2: Full Validation (n=5-8/group)
Expand only groups showing correct direction in Phase 1.

Add dose-response for confirmed effects.

---

## 17. Core Philosophy

**Shortest path from correlation to causality**:

1. Prove CDI can be manipulated
2. Prove CDI manipulation changes extinction

That's it.

Don't overcomplicate. Don't collect unnecessary data.

Focus on the causal chain.

---

*Protocol Version*: 1.0  
*Date*: 2026-03-09  
*Next Step*: Implement `run_p1_experiments.sh`
