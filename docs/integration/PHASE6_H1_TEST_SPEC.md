# Phase 6 H1 Test Specification

**Hypothesis**: Archive-as-Generic-Prior  
**Date**: 2026-03-09  
**Scope**: MINIMAL - H1 only, no H2/H3/H4  
**Status**: READY_FOR_EXECUTION  

---

## 1. Core Question

Does the archive act as a **generic stabilization channel**, independent of specific content?

**Not asking**:
- ❌ Does content matter? (Phase 5 answered: NO)
- ❌ Does compression level matter? (H2 - deferred)
- ❌ Does receiver capacity matter? (H3 - deferred)

**Asking**:
- ✅ Does ANY low-bandwidth signal provide stabilization?
- ✅ Is content shape irrelevant to effect?
- ✅ Is the effect purely architectural/presence-based?

---

## 2. Minimal Test Design

### 2.1 Conditions (4 total)

| Condition | Description | Expected | Test |
|-----------|-------------|----------|------|
| **baseline_full** | L1+L2+L3 with real archive | Strong stabilization | Control |
| **L3_constant** | Archive returns **fixed constant** strategy | Similar to baseline | **KEY TEST** |
| **L3_random_each_tick** | Archive returns **fresh random** each tick | Similar to baseline | **KEY TEST** |
| **L3_off** | No archive | Weak stabilization | Baseline comparison |

**Total**: 4 conditions × 8 universes = 32 runs  
**Duration**: 5000 ticks (reduced from 10000 for speed)  

### 2.2 Why These 4?

```
Logic chain:

IF archive effect comes from SPECIFIC CONTENT:
   constant ≠ real, random ≠ real
   → H1 fails

IF archive effect comes from GENERIC CHANNEL:
   constant ≈ real ≈ random ≠ off
   → H1 supported
   
The question is NOT "which content is best"
The question is "does ANY content work"
```

---

## 3. Configuration Details

### 3.1 L3_constant

```yaml
name: L3_constant
archive_mode: constant
archive_value: 
  strategy: "cooperate"  # Fixed single strategy
  strength: 0.5
archive_retrieval_prob: 0.001

# Implementation:
# Every archive read returns the SAME strategy
# No historical content used
```

### 3.2 L3_random_each_tick

```yaml
name: L3_random_each_tick
archive_mode: random_fresh
archive_generator: uniform_random
archive_retrieval_prob: 0.001
archive_value_range: [0.0, 1.0]  # SAME as real archive output range
archive_update_frequency: per_read  # NOT per tick

# Implementation:
# Every archive read returns NEW random strategy
# CRITICAL CONSTRAINTS:
#   1. Same bandwidth as real: p=0.001
#   2. Same amplitude range as real: [0.0, 1.0]
#   3. Same injection points: only when archive accessed
#   4. NO additional noise outside archive mechanism
# 
# This tests: "unstructured generic prior" 
# NOT: "high-frequency noise injection"
#
# If random shows harm vs constant/real:
#   → Likely bandwidth/amplitude mismatch, not H1 falsification
#   → Check implementation before concluding
```

### 3.3 baseline_full (Control)

```yaml
name: baseline_full
archive_mode: historical_real
archive_retrieval_prob: 0.001

# Standard operation as in Phase 5
```

### 3.4 L3_off (Control)

```yaml
name: L3_off
archive_enabled: false

# No archive access
```

---

## 4. Metrics (Minimal Set)

### 4.1 Primary Metric

| Metric | Why | Measurement |
|--------|-----|-------------|
| **lineage_diversity** | Core stabilization indicator | Mean across final 1000 ticks |

### 4.2 Secondary Metrics

| Metric | Purpose |
|--------|---------|
| population_variance | Stability over time |
| extinction_event_count | System resilience |

### 4.3 Not Measuring (Deliberate)

- ❌ adaptation_gain (narrative-heavy, skip)
- ❌ strategy_entropy (content-focused, irrelevant)
- ❌ archive_sample_successes (engagement not the question)

---

## 5. Decision Thresholds

### 5.1 Success Criteria (H1 Supported)

```
IF:
  (constant ≈ real) AND (random ≈ real) AND (constant/random ≠ off)
  
  WHERE "≈" means:
    δ < 10% difference
    Cohen's d < 0.3 (small/negligible effect)
    
  AND "≠" means:
    δ > 20% difference vs off
    Cohen's d > 0.5
    p < 0.05

THEN:
  ✅ H1 SUPPORTED - Archive acts as generic channel
  → Proceed to Phase 7 (architecture optimization)
```

### 5.2 Failure Criteria (H1 Falsified)

```
IF:
  (constant ≠ real) OR (random ≠ real)
  
  WHERE "≠" means:
    δ > 20% difference
    Cohen's d > 0.5
    p < 0.05

THEN:
  ❌ H1 FALSIFIED - Content DOES matter (unexpected)
  → Re-examine Phase 5 methodology
  → Consider Phase 5 false negative
```

### 5.3 Ambiguous Zone

```
IF:
  10% ≤ δ ≤ 20%
  OR
  0.3 ≤ Cohen's d ≤ 0.5

THEN:
  🟡 EXTEND - Run more universes (16 → 24)
```

---

## 6. Execution Plan

### 6.1 Pre-flight Check

```bash
# Verify PR #12 merged
git log --oneline | grep -i "constant\|random\|generic"

# Verify new modes implemented
./bioworld_mvp --help | grep -E "archive_mode|constant|random"
```

### 6.2 Execution Order

```
Hour 0:
  [ ] L3_constant (8 universes, 5000 ticks)
  [ ] L3_random_each_tick (8 universes, 5000 ticks)
  
Hour 1-2:
  [ ] baseline_full (8 universes, 5000 ticks) - if not reused from Phase 5
  [ ] L3_off (8 universes, 5000 ticks) - if not reused from Phase 5
  
Hour 2-3:
  [ ] Analysis
  [ ] Decision
```

**Total time**: 2-3 hours  
**Parallelizable**: Yes (4 conditions simultaneously if CPU permits)

---

## 7. Analysis Script

```python
# phase6_h1_analysis.py
import pandas as pd
import numpy as np
from scipy import stats

def analyze_h1():
    """H1: Archive-as-Generic-Prior analysis"""
    
    # Load data
    real = load_condition('baseline_full')
    constant = load_condition('L3_constant')
    random_fresh = load_condition('L3_random_each_tick')
    off = load_condition('L3_off')
    
    results = {}
    
    # Test 1: constant ≈ real?
    results['constant_vs_real'] = compare(
        constant, real, 
        threshold_equivalence=0.10,
        threshold_difference=0.20
    )
    
    # Test 2: random ≈ real?
    results['random_vs_real'] = compare(
        random_fresh, real,
        threshold_equivalence=0.10,
        threshold_difference=0.20
    )
    
    # Test 3: real/constant/random ≠ off?
    for name, data in [('real', real), ('constant', constant), ('random', random_fresh)]:
        results[f'{name}_vs_off'] = compare(
            data, off,
            threshold_difference=0.20
        )
    
    # Verdict
    h1_supported = (
        results['constant_vs_real']['equivalent'] and
        results['random_vs_real']['equivalent'] and
        all(results[f'{n}_vs_off']['different'] for n in ['real', 'constant', 'random'])
    )
    
    return {
        'h1_supported': h1_supported,
        'details': results,
        'recommendation': 'PROCEED_TO_PHASE7' if h1_supported else 'REEXAMINE'
    }

def compare(a, b, threshold_equivalence=0.10, threshold_difference=0.20):
    """Compare two conditions"""
    delta = (a.mean() - b.mean()) / b.mean()
    d = cohens_d(a, b)
    
    return {
        'delta': delta,
        'cohens_d': d,
        'p_value': stats.ttest_ind(a, b).pvalue,
        'equivalent': abs(delta) < threshold_equivalence and abs(d) < 0.3,
        'different': abs(delta) > threshold_difference and abs(d) > 0.5
    }
```

---

## 8. Terminology Compliance

### 8.1 Required Terms (Use These)

| Term | Context |
|------|---------|
| "generic prior" | Hypothesis name and description |
| "stabilization channel" | Archive mechanism description |
| "weak regularizer" | Effect characterization |
| "architectural effect" | Distinction from content effect |

### 8.2 Prohibited Terms (Do Not Use)

| Term | Status | Replacement |
|------|--------|-------------|
| "content-bearing" | ❌ TERMINATED | "signal-carrying" (if must) |
| "memory inheritance" | ❌ TERMINATED | "channel effect" |
| "ancestral wisdom" | ❌ TERMINATED | [do not use] |
| "historical strategy" | ❌ TERMINATED | "generic signal" |

---

## 9. Success Definition

### 9.1 H1 Supported

```
✅ CONSTANT ≈ REAL ≈ RANDOM ≠ OFF

Interpretation:
- Archive provides stabilization through presence, not content
- Any low-bandwidth signal works
- System uses archive as generic regularizer
- Content shape irrelevant
```

### 9.2 H1 Falsified

```
❌ CONSTANT ≠ REAL or RANDOM ≠ REAL

Interpretation:
- Phase 5 may have been false negative
- Content DOES matter
- Need to re-examine methodology
- Consider longer runs or different metrics
```

---

## 10. Next Steps After H1

### If H1 Supported

1. **Phase 7**: Optimize generic channel
   - Test different sampling probabilities
   - Test different signal strengths
   - Remove content storage entirely (simplify)

2. **Architecture decision**
   - Archive → Simplified stabilizer
   - Remove compression/decoding logic
   - Pure weak coupling mechanism

### If H1 Falsified

1. **Re-examine Phase 5**
   - Check for measurement errors
   - Consider effect size vs duration tradeoff
   - Review statistical power

2. **H2 resurrection**
   - Content-threshold may be relevant after all
   - Test high-resolution archive

---

## Sign-off

| Item | Status |
|------|--------|
| Hypothesis clarity | ✅ Single question, no scope creep |
| Test minimalism | ✅ 4 conditions, 1 primary metric |
| Terminology compliance | ✅ New terms only |
| No H2/H3/H4 | ✅ Deferred |
| Execution ready | ✅ Awaiting implementation |

---

**Spec Version**: 1.0-FINAL  
**Scope**: H1 only  
**Estimated Duration**: 2-3 hours  
**Decision Type**: Binary (support/falsify)
