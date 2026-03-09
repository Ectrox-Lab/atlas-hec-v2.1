# Phase 7 Generic Channel Sweep Specification

**Objective**: Find optimal operating region for L3 as generic stabilization channel  
**Date**: 2026-03-10  
**Scope**: MINIMAL - p × α sweep only, no new theory  
**Status**: READY_FOR_EXECUTION  

---

## 1. Core Question

What is the **optimal operating region** for L3 as a generic prior/weak regularizer?

**Not asking**:
- ❌ Does content matter? (Phase 5-6 answered: NO)
- ❌ Is there any effect? (Phase 6 confirmed: YES)
- ❌ New mechanisms or layers

**Asking**:
- ✅ At what sampling probability p is effect strongest?
- ✅ At what signal strength α is effect optimal?
- ✅ Where does channel become ineffective or harmful?

---

## 2. Sweep Matrix

### 2.1 Dimensions

| Dimension | Levels | Values | Rationale |
|-----------|--------|--------|-----------|
| **p (sampling probability)** | 5 | 0, 0.001, 0.01, 0.05, 0.1 | From none to frequent |
| **α (signal strength)** | 3 | weak, medium, strong | Generic prior intensity |

**Total conditions**: 5 × 3 = 15  
**Universes per condition**: 8  
**Total runs**: 120  
**Ticks per run**: 5000  

### 2.2 Configuration Matrix

```yaml
# p values
probabilities:
  - 0.0      # Baseline: no channel
  - 0.001    # Phase 5-6 tested
  - 0.01     # 10x higher
  - 0.05     # 50x higher
  - 0.1      # 100x higher

# α values (implemented as signal intensity)
strengths:
  weak:    {prior_weight: 0.1, mutation_dampening: 0.9}
  medium:  {prior_weight: 0.5, mutation_dampening: 0.5}
  strong:  {prior_weight: 0.9, mutation_dampening: 0.1}
```

---

## 3. Implementation

### 3.1 New Sentinel Modes

```rust
// L3_generic_weak
archive_mode: generic_prior
sample_probability: {p}
prior_weight: 0.1

// L3_generic_medium
archive_mode: generic_prior
sample_probability: {p}
prior_weight: 0.5

// L3_generic_strong
archive_mode: generic_prior
sample_probability: {p}
prior_weight: 0.9
```

### 3.2 Mode Naming

```
L3_generic_p{p}_{strength}

Examples:
- L3_generic_p0_weak      (baseline: no channel)
- L3_generic_p0.001_weak  (Phase 6 equivalent)
- L3_generic_p0.1_strong  (high freq, strong signal)
```

---

## 4. Metrics (4 Only)

| Metric | Purpose | Target Direction |
|--------|---------|------------------|
| **lineage_diversity** | Core stability indicator | Higher is better |
| **top1_lineage_share** | Dominance control | Moderate (0.3-0.7) |
| **strategy_entropy** | Behavioral diversity | Higher is better |
| **extinction_event_count** | System resilience | Lower is better |

**Not measuring**:
- ❌ adaptation_gain (narrative-heavy)
- ❌ archive-specific metrics (content irrelevant)
- ❌ Complex derived indices

---

## 5. Success Criteria

### 5.1 Optimal Region Definition

```
A condition is "OPTIMAL" if:
  1. lineage_diversity > baseline (p=0) by >10%
  2. extinction_event_count = 0
  3. top1_lineage_share ∈ [0.3, 0.7] (not too dominant, not too fragmented)
  4. Cohen's d vs baseline > 0.5

A condition is "EFFECTIVE" if:
  1. lineage_diversity > baseline by >5%
  2. extinction_event_count acceptable
  3. Cohen's d > 0.3

A condition is "INEFFECTIVE" if:
  1. No significant difference vs baseline
  2. Cohen's d < 0.2

A condition is "HARMFUL" if:
  1. lineage_diversity < baseline by >10%
  2. OR extinction events increase
  3. Cohen's d < -0.3
```

### 5.2 Decision Output

```
SWEEP_RESULT:
  optimal_region:
    p_range: [p_min, p_max]
    α_range: [α_min, α_max]
    best_single_point: (p_best, α_best)
  
  trade_off_analysis:
    diversity_vs_stability: "higher p increases diversity but may fragment"
    signal_strength_effect: "strong α may over-constrain"
  
  recommendation:
    default_config: (p_recommended, α_recommended)
    rationale: "balancing diversity and stability"
```

---

## 6. Execution Plan

### 6.1 Batch Execution

```bash
# Execute all 15 conditions
for p in 0.0 0.001 0.01 0.05 0.1; do
  for strength in weak medium strong; do
    mode="L3_generic_p${p}_${strength}"
    ./bioworld_mvp \
      --ticks 5000 \
      --universes 8 \
      --sentinel-mode "$mode" \
      --output-dir "runs/sentinel/$mode"
  done
done
```

**Parallelization**: Up to 15 simultaneous (if CPU permits)  
**Estimated time**: 15-30 minutes (parallel) or 2-4 hours (sequential)

### 6.2 Execution Order (if sequential)

```
Priority 1: p=0.001 (baseline from Phase 6)
Priority 2: p=0.0 (true baseline)
Priority 3: p=0.01 (10x test)
Priority 4: p=0.05, p=0.1 (high freq test)

Within each p: weak → medium → strong
```

---

## 7. Analysis

### 7.1 Visualization

```python
# Heatmap: lineage_diversity vs (p, α)
# Heatmap: extinction_rate vs (p, α)
# Scatter: diversity vs dominance (colored by p)
# Line plots: metric vs p (for each α)
```

### 7.2 Statistical Tests

```python
for each (p, α) condition:
    compare vs baseline (p=0):
        - t-test for lineage_diversity
        - effect size (Cohen's d)
        - classification: optimal/effective/ineffective/harmful

find peak regions:
    - local maxima in diversity
    - acceptable extinction rate
    - balanced dominance
```

### 7.3 Output

```
PHASE7_SWEEP_REPORT:
  sweep_parameters:
    p_values: [0, 0.001, 0.01, 0.05, 0.1]
    α_values: [weak, medium, strong]
  
  results_matrix:
    [15 cells with classification and metrics]
  
  optimal_region:
    p_range: "0.01 to 0.05"
    α_range: "medium"
    best_point: "p=0.01, α=medium"
  
  engineering_recommendation:
    default_p: 0.01
    default_α: medium
    rationale: "best diversity gain without fragmentation"
  
  architectural_implications:
    - "Channel should be low-frequency (p<0.1)"
    - "Signal strength should be moderate"
    - "High-frequency strong signals are harmful"
```

---

## 8. Terminology Compliance

### 8.1 Required Terms

| Term | Context |
|------|---------|
| "generic channel" | L3 mechanism description |
| "prior weight" | α parameter |
| "sampling probability" | p parameter |
| "stabilization" | Effect characterization |
| "regularization" | Mechanism description |

### 8.2 Prohibited Terms

| Term | Status | Why |
|------|--------|-----|
| "content" | ❌ BANNED | Irrelevant per Phase 5-6 |
| "memory" | ❌ BANNED | Wrong abstraction |
| "inheritance" | ❌ BANNED | Not what's happening |
| "archive" | ⚠️ DEPRECATED | Use "channel" instead |
| "historical" | ❌ BANNED | No history involved |

---

## 9. Constraints (Do Not Violate)

| Constraint | Rationale |
|------------|-----------|
| **No new theory** | H1 sufficient, just optimize |
| **No H2/H3/H4** | Defer to Phase 8+ |
| **No new layers** | L3 is the channel, that's it |
| **No content tests** | Already settled |
| **No timing experiments** | Out of scope |
| **No receiver capacity** | Out of scope |

---

## 10. Success Definition

### 10.1 Minimum Success

```
Identify at least one (p, α) region where:
- lineage_diversity improves >10% vs baseline
- No extinction events
- Effect statistically significant (d > 0.5)
```

### 10.2 Full Success

```
Characterize complete response surface:
- Clear optimal region identified
- Trade-offs documented
- Engineering defaults recommended
- Architectural constraints defined
```

### 10.3 Failure (Unexpected)

```
If all (p, α) conditions show:
- No improvement vs baseline, OR
- Only harmful effects

Then:
- L3 as generic channel may be implementation-dependent
- Re-examine channel design
- Consider removing L3 entirely
```

---

## 11. Post-Phase 7 Actions

### If Successful

1. **Lock L3 configuration** to optimal (p, α)
2. **Simplify implementation**:
   - Remove content storage
   - Remove compression logic
   - Keep only: sampler + prior injector
3. **Rename in codebase**: "Archive" → "PriorChannel" or "Stabilizer"
4. **Documentation**: Update all docs to "three-layer control"

### If Ambiguous

1. Extend p range (e.g., p=0.0001, p=0.5)
2. Refine α granularity
3. Add intermediate points

### If Harmful

1. Consider L3 removal
2. Test L2-only system
3. Evaluate alternative stabilization mechanisms

---

## Sign-off

| Item | Status |
|------|--------|
| Scope minimal | ✅ p × α only |
| No new theory | ✅ Just optimization |
| Metrics defined | ✅ 4 metrics |
| Success criteria | ✅ Clear thresholds |
| Terminology clean | ✅ No content/memory |
| Engineering focus | ✅ Channel tuning |

---

**Spec Version**: 1.0-FINAL  
**Estimated Duration**: 15-30 min (parallel) / 2-4 hours (sequential)  
**Decision Type**: Engineering optimization, not hypothesis test
