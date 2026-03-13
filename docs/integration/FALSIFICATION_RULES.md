# Falsification Rules

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Purpose**: Direct falsification conditions for three-layer memory hypothesis

---

## Core Hypothesis

> "Three-layer memory architecture (L1 Cell, L2 Lineage, L3 Archive) is a necessary condition for sustainable complexity and collapse resistance in digital organism populations."

**Falsification Strategy**: If any of the following conditions hold, the hypothesis is falsified.

---

## Rule 1: L3 Content Irrelevance

### Statement
If real L3 content produces statistically equivalent outcomes to shuffled L3 content, then L3 structure carries no meaningful information.

### Formal Condition
```
H0: μ(L3_real) = μ(L3_shuffled)
If p > 0.05 and |d| < 0.2:
  → FALSIFIED: L3 content irrelevant
```

### Metrics to Compare
- lineage_diversity (endpoint)
- strategy_entropy (endpoint)
- collapse_event_count
- avg population over last 100 generations

### Implementation
```python
from scipy import stats

real = load_endpoint_metrics('L3_real_p001')
shuffled = load_endpoint_metrics('L3_shuffled_p001')

t_stat, p_value = stats.ttest_ind(real['lineage_diversity'], shuffled['lineage_diversity'])
cohens_d = (real.mean() - shuffled.mean()) / pooled_std

if p_value > 0.05 and abs(cohens_d) < 0.2:
    verdict = "FALSIFIED: L3 content irrelevant"
```

---

## Rule 2: L2 Redundancy

### Statement
If disabling L2 (lineage memory) produces no significant change in population dynamics, then L2 is redundant.

### Formal Condition
```
H0: μ(no_L2) = μ(baseline)
If p > 0.05 and |d| < 0.3:
  → FALSIFIED: L2 redundant
```

### Expected Outcome (if hypothesis holds)
- `no_L2` should show REDUCED lineage_diversity
- `no_L2` should show INCREASED collapse_event_count
- `no_L2` should show REDUCED strategy_entropy

### Falsification Trigger
```python
if no_l2_lineage_diversity >= baseline_lineage_diversity:
    verdict = "FALSIFIED: L2 has no effect on lineage diversity"
    
if no_l2_collapse_count <= baseline_collapse_count:
    verdict = "FALSIFIED: L2 has no protective effect"
```

---

## Rule 3: L1 Redundancy

### Statement
If disabling L1 (cell memory) produces no significant change, then L1 is redundant.

### Formal Condition
```
H0: μ(no_L1) = μ(baseline)
If p > 0.05 and |d| < 0.3:
  → FALSIFIED: L1 redundant
```

### Expected Outcome (if hypothesis holds)
- `no_L1` should show REDUCED cooperation_density
- `no_L1` should show INCREASED death_rate

---

## Rule 4: L3 Overpowering

### Statement
If L3 with direct access (bypassing sampling constraints) leads to rapid diversity collapse, then L3 as designed is unsafe and current constraints are necessary.

### Formal Condition
```
Compare: L3_real_p001 vs L3_overpowered_direct

If L3_overpowered shows:
  - top1_lineage_share > 0.8 (monoculture)
  - strategy_entropy < 0.5 (convergence)
  - collapse_event_count > 2 (instability)
  
Then: Anti-God-Mode constraints are NECESSARY
(Not a falsification of hypothesis, but validation of design)
```

---

## Rule 5: Contract Field Nullity

### Statement
If contract-defined fields exist in CSV but show no meaningful variation across experimental conditions, then the fields are not actually computed from simulation state.

### Formal Condition
```
For each required field:
  variance = σ²(values across all conditions)
  
If variance < 0.001 for numeric fields:
  → FALSIFIED: Field is constant/fake
```

### Fields to Check
- archive_sample_attempts: should vary with p
- lineage_diversity: should vary with no_L2
- strategy_entropy: should vary with conditions
- collapse_event_count: should be 0 in baseline, >0 in stress

### Implementation
```python
def check_field_validity(df, field):
    variance = df[field].var()
    if variance < 0.001:
        return f"FALSIFIED: {field} has no variance ({variance})"
    
    # Check if field correlates with condition
    groups = df.groupby('condition')[field].mean()
    f_stat, p_value = stats.f_oneway(*[group for name, group in df.groupby('condition')[field]])
    
    if p_value > 0.1:
        return f"FALSIFIED: {field} does not respond to conditions"
    
    return "VALID"
```

---

## Rule 6: CDI Predictive Failure

### Statement
If CDI does not predict extinction better than random, then CDI is not a valid leading indicator.

### Formal Condition
```
Compute AUC of CDI-based hazard model
If AUC < 0.7:
  → FALSIFIED: CDI not predictive
```

### Implementation
```python
from sklearn.metrics import roc_auc_score

# CDI < 0.53 (I_crit) as predictor of collapse within 100 gens
predicted_risk = (cdi_values < 0.53).astype(int)
actual_collapse = (extinction_events > 0).astype(int)

auc = roc_auc_score(actual_collapse, predicted_risk)
if auc < 0.7:
    verdict = "FALSIFIED: CDI not predictive"
```

---

## Rule 7: Archive Sampling Rate Violation

### Statement
If actual archive sampling rate deviates significantly from p=0.01, then sampling mechanism is broken.

### Formal Condition
```
observed_rate = archive_sample_successes / archive_sample_attempts

If |observed_rate - 0.01| > 0.005 (50% relative error):
  → FALSIFIED: Sampling rate incorrect
```

### Check
```python
observed_p = df['archive_sample_successes'].sum() / df['archive_sample_attempts'].sum()
expected_p = 0.01

if abs(observed_p - expected_p) > 0.005:
    verdict = f"FALSIFIED: p={observed_p}, expected 0.01"
```

---

## Summary Table

| Rule | Condition | Falsified If |
|------|-----------|--------------|
| R1 | L3_real ≈ L3_shuffled | p > 0.05, d < 0.2 |
| R2 | no_L2 ≈ baseline | p > 0.05, d < 0.3 |
| R3 | no_L1 ≈ baseline | p > 0.05, d < 0.3 |
| R4 | L3_overpowered safe | Monoculture, collapse |
| R5 | Fields constant | σ² < 0.001 |
| R6 | CDI predictive | AUC < 0.7 |
| R7 | Sampling rate | \|p_obs - 0.01\| > 0.005 |

---

## Automated Falsification Script

```python
#!/usr/bin/env python3
# falsification_check.py

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

class FalsificationChecker:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.falsifications = []
    
    def load_condition(self, condition: str) -> pd.DataFrame:
        """Load all runs for a condition"""
        dfs = []
        for seed_dir in (self.output_dir / condition).glob('seed_*'):
            for u_dir in seed_dir.glob('u*'):
                df = pd.read_csv(u_dir / 'population.csv')
                df['condition'] = condition
                df['seed'] = seed_dir.name
                df['universe'] = u_dir.name
                dfs.append(df.iloc[-100:])  # Last 100 rows
        return pd.concat(dfs, ignore_index=True)
    
    def check_rule1_l3_irrelevance(self) -> dict:
        """L3_real vs L3_shuffled"""
        real = self.load_condition('L3_real_p001')
        shuffled = self.load_condition('L3_shuffled_p001')
        
        metric = 'lineage_diversity'
        t_stat, p_value = stats.ttest_ind(real[metric], shuffled[metric])
        
        # Cohen's d
        pooled_std = np.sqrt((real[metric].var() + shuffled[metric].var()) / 2)
        cohens_d = (real[metric].mean() - shuffled[metric].mean()) / pooled_std
        
        falsified = p_value > 0.05 and abs(cohens_d) < 0.2
        
        return {
            'rule': 'R1: L3 Content Irrelevance',
            'falsified': falsified,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'verdict': 'FALSIFIED' if falsified else 'NOT_FALSIFIED'
        }
    
    def check_rule2_l2_redundancy(self) -> dict:
        """no_L2 vs baseline"""
        baseline = self.load_condition('baseline')
        no_l2 = self.load_condition('no_L2')
        
        metric = 'lineage_diversity'
        t_stat, p_value = stats.ttest_ind(baseline[metric], no_l2[metric])
        
        # Direction check: no_L2 should have LOWER diversity
        direction_correct = no_l2[metric].mean() < baseline[metric].mean()
        
        falsified = p_value > 0.05 or not direction_correct
        
        return {
            'rule': 'R2: L2 Redundancy',
            'falsified': falsified,
            'p_value': p_value,
            'direction_correct': direction_correct,
            'verdict': 'FALSIFIED' if falsified else 'NOT_FALSIFIED'
        }
    
    def check_rule5_field_validity(self) -> dict:
        """Check fields have variance"""
        all_data = pd.concat([
            self.load_condition('baseline'),
            self.load_condition('no_L2'),
            self.load_condition('L3_real_p001')
        ])
        
        required_fields = [
            'archive_sample_attempts',
            'lineage_diversity',
            'strategy_entropy'
        ]
        
        results = {}
        for field in required_fields:
            variance = all_data[field].var()
            if variance < 0.001:
                results[field] = 'FALSIFIED: no variance'
            else:
                results[field] = 'VALID'
        
        return {
            'rule': 'R5: Field Validity',
            'falsified': any('FALSIFIED' in v for v in results.values()),
            'field_results': results,
            'verdict': 'FALSIFIED' if any('FALSIFIED' in v for v in results.values()) else 'NOT_FALSIFIED'
        }
    
    def run_all_checks(self) -> list:
        """Run all falsification checks"""
        self.falsifications = [
            self.check_rule1_l3_irrelevance(),
            self.check_rule2_l2_redundancy(),
            self.check_rule5_field_validity(),
            # Add more rules...
        ]
        return self.falsifications
    
    def report(self) -> str:
        """Generate falsification report"""
        lines = ["# Falsification Report", ""]
        
        any_falsified = False
        for check in self.falsifications:
            status = "❌ FALSIFIED" if check['falsified'] else "✓ NOT_FALSIFIED"
            lines.append(f"## {check['rule']}: {status}")
            lines.append(f"- p_value: {check.get('p_value', 'N/A')}")
            lines.append(f"- cohens_d: {check.get('cohens_d', 'N/A')}")
            lines.append("")
            if check['falsified']:
                any_falsified = True
        
        lines.append("# Final Verdict")
        if any_falsified:
            lines.append("❌ HYPOTHESIS FALSIFIED")
            lines.append("At least one falsification condition met.")
        else:
            lines.append("✓ HYPOTHESIS NOT FALSIFIED")
            lines.append("All checks passed. Proceed with confidence.")
        
        return '\n'.join(lines)

if __name__ == "__main__":
    import sys
    checker = FalsificationChecker(Path(sys.argv[1]))
    checker.run_all_checks()
    print(checker.report())
```

---

## Usage

```bash
# Run sentinel experiment
./sentinel_run.sh

# Check falsification
python3 falsification_check.py outputs/ > falsification_report.md

# If any rule shows FALSIFIED, hypothesis is rejected
```

---

**Next**: After falsification check passes, proceed to ContinuityProbe integration
