# Sentinel Run Specification

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Purpose**: Minimal verification protocol for Bio-World validation

---

## Executive Summary

This spec defines the **minimum viable experiment** to validate:
1. Three-layer memory implementation correctness
2. Anti-God-Mode boundary enforcement
3. Metrics export functionality
4. Falsification condition sensitivity

**Total Compute**: ~4 hours (32 parallel universes × 1500 generations)

---

## 1. Experimental Design

### 1.1 Agents (Conditions)

| Agent ID | Condition | Description |
|----------|-----------|-------------|
| A1 | `baseline` | Normal operation, all layers active |
| A2 | `no_L2` | Lineage memory disabled (P1-A) |
| A3 | `L3_real_p001` | Real archive, p=0.01 sampling |
| A4 | `L3_shuffled_p001` | Shuffled archive content, p=0.01 |
| A5 | `L3_off` | Archive completely disabled |

### 1.2 Grid Configuration

```yaml
grid:
  x: 25
  y: 25
  z: 8
  max_population: 3000
  initial_population: 300
```

### 1.3 Generations

```yaml
generations: 1500
burn_in: 100        # Discard first 100 for analysis
analysis_window: 100  # Last 100 for endpoint metrics
```

### 1.4 Seeds

```yaml
seeds:
  - 1001
  - 1002
  - 1003
replicates_per_seed: 1
```

### 1.5 Universes per Condition

```yaml
parallel_universes: 8
total_runs: 5 agents × 3 seeds × 8 universes = 120 runs
```

---

## 2. Required Output Files

Each run must produce:

### 2.1 Primary Outputs

| File | Columns | Frequency |
|------|---------|-----------|
| `population.csv` | 15 columns (see below) | per-tick |
| `cdi.csv` | 6 columns | per-tick |
| `extinction.csv` | 6 columns | per-tick |
| `summary.json` | aggregated | per-seed |

### 2.2 Directory Structure

```
outputs/
├── baseline/
│   ├── seed_1001/
│   │   ├── u0/
│   │   │   ├── population.csv
│   │   │   ├── cdi.csv
│   │   │   └── extinction.csv
│   │   ├── u1/...
│   │   └── summary.json
│   ├── seed_1002/...
│   └── seed_1003/...
├── no_L2/
├── L3_real_p001/
├── L3_shuffled_p001/
└── L3_off/
```

---

## 3. Required CSV Columns

### 3.1 population.csv (15 columns)

```csv
tick,population,births,deaths,avg_energy,lineage_count,avg_stress_level,archive_record_count,archive_sample_attempts,archive_sample_successes,archive_influenced_births,lineage_diversity,top1_lineage_share,strategy_entropy,collapse_event_count
```

**Endpoint Metrics** (last row per run):
- `population`: Final population
- `lineage_diversity`: Count of unique lineages
- `top1_lineage_share`: Proportion of largest lineage
- `strategy_entropy`: Shannon entropy of strategies

### 3.2 cdi.csv (6 columns)

```csv
tick,signal_diversity,cooperation_density,memory_usage,exploration_rate,cdi
```

### 3.3 extinction.csv (6 columns)

```csv
tick,death_rate,cdi,hazard_rate,extinction_probability,extinction_events
```

---

## 4. Pass/Fail Interpretation

### 4.1 Baseline Checks

| Check | Threshold | Fail If |
|-------|-----------|---------|
| Population stability | > 100 at generation 1500 | Population < 100 |
| CDI range | [0.4, 0.8] | CDI < 0.2 or CDI > 1.0 |
| Lineage diversity | > 10 | Diversity < 5 |
| Archive samples | > 0 in 1500 gens | Samples = 0 |

### 4.2 Falsification Checks

| Comparison | Expected | Fail If |
|------------|----------|---------|
| `no_L2` vs `baseline` | Significant difference (p<0.05) | No difference |
| `L3_off` vs `baseline` | Significant difference | No difference |
| `L3_shuffled` vs `L3_real` | No significant difference | Significant difference |
| `L3_real` vs `baseline` | Small or no difference | Large difference |

### 4.3 Metric Sanity Checks

| Metric | Sanity Check | Fail If |
|--------|--------------|---------|
| `archive_sample_attempts` | > 0 | All zeros |
| `lineage_diversity` | >= 1 | Any zero |
| `top1_lineage_share` | [0, 1] | Outside range |
| `strategy_entropy` | >= 0 | Negative values |
| `collapse_event_count` | Integer >= 0 | Negative or non-integer |

---

## 5. Execution Commands

### 5.1 Full Sentinel Run

```bash
#!/bin/bash
# sentinel_run.sh

AGENTS=("baseline" "no_L2" "L3_real_p001" "L3_shuffled_p001" "L3_off")
SEEDS=(1001 1002 1003)
TICKS=1500
UNIVERSES=8

for agent in "${AGENTS[@]}"; do
  for seed in "${SEEDS[@]}"; do
    echo "Running $agent seed=$seed..."
    ./p1_experiment \
      --group "$agent" \
      --seed "$seed" \
      --ticks "$TICKS" \
      --universes "$UNIVERSES" \
      --output-dir "outputs/${agent}/seed_${seed}"
  done
done
```

### 5.2 Validation Script

```python
#!/usr/bin/env python3
# validate_sentinel.py

import pandas as pd
import json
from pathlib import Path

def validate_run(output_dir: Path) -> dict:
    results = {"pass": True, "errors": []}
    
    # Check files exist
    pop_file = output_dir / "u0" / "population.csv"
    if not pop_file.exists():
        results["pass"] = False
        results["errors"].append("Missing population.csv")
        return results
    
    # Check columns
    df = pd.read_csv(pop_file)
    required_cols = [
        "archive_sample_attempts", "archive_sample_successes",
        "archive_influenced_births", "lineage_diversity",
        "top1_lineage_share", "strategy_entropy", "collapse_event_count"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        results["pass"] = False
        results["errors"].append(f"Missing columns: {missing}")
    
    # Check data sanity
    if df["lineage_diversity"].min() < 1:
        results["errors"].append("lineage_diversity < 1")
    
    if df["top1_lineage_share"].min() < 0 or df["top1_lineage_share"].max() > 1:
        results["errors"].append("top1_lineage_share out of range")
    
    return results

if __name__ == "__main__":
    import sys
    output_dir = Path(sys.argv[1])
    result = validate_run(output_dir)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["pass"] else 1)
```

---

## 6. Analysis Pipeline

### 6.1 Post-Processing

```bash
# 1. Validate all runs
find outputs -name "seed_*" -type d | while read dir; do
  python3 validate_sentinel.py "$dir" || echo "FAIL: $dir"
done

# 2. Compare conditions
python3 -c "
import pandas as pd
from pathlib import Path

def load_endpoints(agent):
    dfs = []
    for seed_dir in Path(f'outputs/{agent}').glob('seed_*'):
        for u_dir in seed_dir.glob('u*'):
            df = pd.read_csv(u_dir / 'population.csv')
            dfs.append(df.iloc[-1])  # Last row
    return pd.DataFrame(dfs)

baseline = load_endpoints('baseline')
no_l2 = load_endpoints('no_L2')

print('Baseline lineage_diversity:', baseline['lineage_diversity'].mean())
print('no_L2 lineage_diversity:', no_l2['lineage_diversity'].mean())
"

# 3. Generate report
python3 generate_sentinel_report.py outputs/ > sentinel_report.md
```

### 6.2 Success Criteria

```yaml
success_criteria:
  baseline:
    - population_final > 100
    - lineage_diversity > 10
    - archive_sample_attempts > 0
    
  falsification:
    - no_L2 ≠ baseline (p < 0.05)
    - L3_off ≠ baseline (p < 0.05)
    - L3_shuffled ≈ L3_real (p > 0.05)
    
  data_quality:
    - all_csv_files_present: true
    - all_columns_present: true
    - no_missing_values: true
    - numeric_ranges_valid: true
```

---

## 7. Timeline

| Phase | Duration | Output |
|-------|----------|--------|
| Setup | 10 min | Environment ready |
| Execution | 4 hours | 120 run directories |
| Validation | 30 min | Pass/fail per run |
| Analysis | 30 min | Comparison results |
| Report | 20 min | sentinel_report.md |
| **Total** | **5.5 hours** | Complete validation |

---

## 8. Rollback Conditions

Stop and fix if:
1. > 10% runs fail validation
2. Baseline population collapses (< 50)
3. All archive_sample_attempts = 0
4. Missing required columns detected

---

**Next**: After Sentinel Run passes, proceed to full falsification experiments
