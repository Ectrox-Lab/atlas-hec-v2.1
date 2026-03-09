# CSV Field Validation Rules

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Purpose**: Define validation rules for required_now fields

---

## Field Specifications

### Field 1: archive_sample_attempts

| Attribute | Specification |
|-----------|---------------|
| **Type** | u32 (unsigned 32-bit integer) |
| **Source** | Counter in Cell::update() or Reproduction logic |
| **Unit** | Count per generation |
| **Valid Range** | [0, population_size] |
| **All Zero Allowed?** | First ~100 generations, then NO |
| **All Zero = Blocker?** | YES (after gen 100) |

**Validation**:
```python
def validate_archive_sample_attempts(df):
    # Check monotonic increasing
    late_game = df[df['tick'] > 100]['archive_sample_attempts']
    if late_game.max() == 0:
        return 'BLOCKER: No sampling after generation 100'
    
    # Check <= population
    if (df['archive_sample_attempts'] > df['population']).any():
        return 'ERROR: Attempts > population'
    
    return 'VALID'
```

**Semantics**:
- Increments every time a cell attempts to sample archive
- Should be ~1% of births × p=0.01 attempts
- If constant at 0, archive system not working

---

### Field 2: archive_sample_successes

| Attribute | Specification |
|-----------|---------------|
| **Type** | u32 |
| **Source** | Counter when archive.sample() returns Some |
| **Unit** | Count per generation |
| **Valid Range** | [0, archive_sample_attempts] |
| **All Zero Allowed?** | First ~100 generations, then NO |
| **All Zero = Blocker?** | YES (after gen 100) |

**Validation**:
```python
def validate_archive_sample_successes(df):
    # Cannot exceed attempts
    if (df['archive_sample_successes'] > df['archive_sample_attempts']).any():
        return 'ERROR: Successes > attempts'
    
    # Check rate ~1%
    late_game = df[df['tick'] > 100]
    if late_game.empty:
        return 'SKIP: Not enough data'
    
    success_rate = late_game['archive_sample_successes'].sum() / late_game['archive_sample_attempts'].sum()
    if success_rate > 0.05:  # >5% seems wrong
        return 'WARNING: Success rate too high (>5%)'
    
    if success_rate == 0:
        return 'BLOCKER: No successful samples'
    
    return 'VALID'
```

**Semantics**:
- Should be ~1% of attempts (p=0.01)
- If always 0, archive empty or sampling broken
- If >>1%, sampling probability wrong

---

### Field 3: archive_influenced_births

| Attribute | Specification |
|-----------|---------------|
| **Type** | u32 |
| **Source** | Counter when newborn has lesson from archive |
| **Unit** | Count per generation |
| **Valid Range** | [0, births] |
| **All Zero Allowed?** | Rare but possible |
| **All Zero = Blocker?** | NO (if successes > 0 but not used) |

**Validation**:
```python
def validate_archive_influenced_births(df):
    # Cannot exceed births
    if (df['archive_influenced_births'] > df['births']).any():
        return 'ERROR: Influenced > total births'
    
    # Cannot exceed successes
    if (df['archive_influenced_births'] > df['archive_sample_successes']).any():
        return 'ERROR: Influenced > successes'
    
    return 'VALID'
```

**Semantics**:
- Tracks actual use of archive in reproduction
- May be < successes if lessons not passed
- Zero OK if archive lessons rejected

---

### Field 4: lineage_diversity

| Attribute | Specification |
|-----------|---------------|
| **Type** | u32 |
| **Source** | HashSet::len() of active lineage_ids |
| **Unit** | Count of distinct lineages |
| **Valid Range** | [1, population] |
| **All Zero Allowed?** | NEVER |
| **All Zero = Blocker?** | YES (impossible state) |

**Validation**:
```python
def validate_lineage_diversity(df):
    # Must be >= 1
    if (df['lineage_diversity'] < 1).any():
        return 'BLOCKER: Diversity < 1 (impossible)'
    
    # Should be <= population
    if (df['lineage_diversity'] > df['population']).any():
        return 'ERROR: Diversity > population'
    
    # Check variation (not constant)
    if df['lineage_diversity'].std() < 0.1:
        return 'WARNING: Diversity nearly constant'
    
    # Reasonable range check
    if df['lineage_diversity'].max() > 1000:
        return 'WARNING: Diversity suspiciously high'
    
    return 'VALID'
```

**Semantics**:
- Count of unique lineage_id among alive cells
- Key falsification metric for no_L2 condition
- Should fluctuate with population dynamics

---

### Field 5: top1_lineage_share

| Attribute | Specification |
|-----------|---------------|
| **Type** | f32 |
| **Source** | max(lineage_counts) / population |
| **Unit** | Proportion [0.0, 1.0] |
| **Valid Range** | [0.0, 1.0] |
| **All Zero Allowed?** | NEVER |
| **All Zero = Blocker?** | YES |

**Validation**:
```python
def validate_top1_lineage_share(df):
    # Must be in [0, 1]
    if (df['top1_lineage_share'] < 0).any() or (df['top1_lineage_share'] > 1).any():
        return 'BLOCKER: Share out of range [0,1]'
    
    # Should be >= 1/population (if diversity >= 1)
    min_expected = 1.0 / df['population'].max()
    if (df['top1_lineage_share'] < min_expected).any():
        return 'WARNING: Share < 1/population'
    
    # Check variation
    if df['top1_lineage_share'].std() < 0.001:
        return 'WARNING: Share nearly constant'
    
    return 'VALID'
```

**Semantics**:
- Proportion of population from largest lineage
- >0.5 indicates monopoly forming
- Key convergence indicator

---

### Field 6: strategy_entropy

| Attribute | Specification |
|-----------|---------------|
| **Type** | f32 |
| **Source** | -Σ p_i × ln(p_i) over strategies |
| **Unit** | Bits (Shannon entropy) |
| **Valid Range** | [0.0, ln(3)] ≈ [0.0, 1.1] for 3 strategies |
| **All Zero Allowed?** | Theoretically yes (all same strategy) |
| **All Zero = Blocker?** | NO (but suspicious) |

**Validation**:
```python
import numpy as np

def validate_strategy_entropy(df):
    # Must be >= 0
    if (df['strategy_entropy'] < 0).any():
        return 'BLOCKER: Entropy negative (impossible)'
    
    # Max for 3 strategies is ln(3) ≈ 1.098
    max_entropy = np.log(3)
    if (df['strategy_entropy'] > max_entropy * 1.1).any():
        return 'ERROR: Entropy > max for 3 strategies'
    
    # Check variation
    if df['strategy_entropy'].std() < 0.001:
        return 'WARNING: Entropy nearly constant'
    
    return 'VALID'
```

**Semantics**:
- Shannon entropy of strategy distribution
- 0 = all same strategy (convergence)
- ~1.1 = uniform distribution (max diversity)
- Key indicator of strategy exploration

---

### Field 7: collapse_event_count

| Attribute | Specification |
|-----------|---------------|
| **Type** | u32 |
| **Source** | Rolling count of extinctions in window |
| **Unit** | Count per 100-generation window |
| **Valid Range** | [0, N] |
| **All Zero Allowed?** | YES (common in stable runs) |
| **All Zero = Blocker?** | NO |

**Validation**:
```python
def validate_collapse_event_count(df):
    # Must be >= 0
    if (df['collapse_event_count'] < 0).any():
        return 'BLOCKER: Negative count (impossible)'
    
    # Should not decrease (rolling window or cumulative)
    # If rolling window, can decrease
    # If cumulative, must be monotonic
    
    # Check for reasonable values
    if df['collapse_event_count'].max() > 100:
        return 'WARNING: Very high collapse count'
    
    return 'VALID'
```

**Semantics**:
- Count of extinction events
- May be rolling window (last 100 gens) or cumulative
- High values indicate unstable conditions

---

## Blocker Summary

| Field | All Zero = Blocker? | After Gen 100? |
|-------|---------------------|----------------|
| archive_sample_attempts | YES | YES |
| archive_sample_successes | YES | YES |
| archive_influenced_births | NO | NO |
| lineage_diversity | YES | ALWAYS |
| top1_lineage_share | YES | ALWAYS |
| strategy_entropy | NO | NO |
| collapse_event_count | NO | NO |

**Critical Blockers** (must fix immediately):
- archive_sample_attempts = 0 after gen 100
- archive_sample_successes = 0 after gen 100
- lineage_diversity < 1
- top1_lineage_share out of [0,1]

---

## Automated Validation Script

```python
#!/usr/bin/env python3
# validate_csv_fields.py

import pandas as pd
import sys
from pathlib import Path

VALIDATION_RULES = {
    'archive_sample_attempts': {
        'min': 0,
        'max_col': 'population',
        'check_zero_after': 100,
        'blocker_if_zero': True,
    },
    'archive_sample_successes': {
        'min': 0,
        'max_col': 'archive_sample_attempts',
        'check_zero_after': 100,
        'blocker_if_zero': True,
    },
    'archive_influenced_births': {
        'min': 0,
        'max_col': 'births',
        'blocker_if_zero': False,
    },
    'lineage_diversity': {
        'min': 1,
        'max_col': 'population',
        'blocker_if_zero': True,
    },
    'top1_lineage_share': {
        'min': 0.0,
        'max': 1.0,
        'blocker_if_zero': True,
    },
    'strategy_entropy': {
        'min': 0.0,
        'max': 1.2,
        'blocker_if_zero': False,
    },
    'collapse_event_count': {
        'min': 0,
        'blocker_if_zero': False,
    },
}

def validate_csv(csv_path):
    df = pd.read_csv(csv_path)
    errors = []
    warnings = []
    
    for field, rules in VALIDATION_RULES.items():
        if field not in df.columns:
            errors.append(f"MISSING: {field}")
            continue
        
        # Check range
        if 'min' in rules and (df[field] < rules['min']).any():
            errors.append(f"RANGE: {field} < {rules['min']}")
        
        if 'max' in rules and (df[field] > rules['max']).any():
            errors.append(f"RANGE: {field} > {rules['max']}")
        
        if 'max_col' in rules and (df[field] > df[rules['max_col']]).any():
            errors.append(f"RANGE: {field} > {rules['max_col']}")
        
        # Check zero blocker
        if rules.get('blocker_if_zero'):
            if 'check_zero_after' in rules:
                late = df[df['tick'] > rules['check_zero_after']][field]
                if late.max() == 0:
                    errors.append(f"ZERO: {field} = 0 after gen {rules['check_zero_after']}")
            else:
                if df[field].max() == 0:
                    errors.append(f"ZERO: {field} always 0")
        
        # Check variation
        if df[field].std() < 0.001:
            warnings.append(f"CONSTANT: {field} nearly constant")
    
    return {'errors': errors, 'warnings': warnings}

if __name__ == '__main__':
    results = validate_csv(sys.argv[1])
    print(f"Errors: {len(results['errors'])}")
    for e in results['errors']:
        print(f"  ❌ {e}")
    print(f"Warnings: {len(results['warnings'])}")
    for w in results['warnings']:
        print(f"  ⚠️  {w}")
    
    sys.exit(1 if results['errors'] else 0)
```

---

**Usage**: Run on every generated CSV before accepting Phase 3 output.
