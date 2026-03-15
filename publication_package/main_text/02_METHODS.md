# 2. Methods

## 2.1 Core Concepts

### 2.1.1 Trajectory
A trajectory is the fundamental unit of progress: **antecedent → state transition → artifact → consequence**.

- **Antecedent**: Seeds, inheritance packages, selection pressure
- **State Transition**: Computation with verifiable checksum change
- **Artifact**: Model weights, decision logs, metrics
- **Consequence**: Changed initial conditions for next generation

### 2.1.2 Execution Window
The primary experimental unit. Each window:
- Executes with fixed resource budget
- Produces auditable outputs (metrics.json, checksums)
- Yields pass/fail/marginal verdict
- Must complete within wall-clock limits (enforced by external gate)

### 2.1.3 Inheritance Package
Structured carryover from prior trajectories containing:
- Lineage identifiers
- Compressed failure patterns
- Successful route records
- Consumption metadata

## 2.2 Experimental Protocol

### 2.2.1 L4 Protocol (Single-Task)
```
Baseline: No inheritance
Treatment: Inheritance package consumption
Metric: Control Gap (improvement over baseline)
Validation: Lineage traceability
```

### 2.2.2 L5 Protocol (Multi-Task)
```
Design: 3 tasks × 3 tasks = 9 pairs (minus 3 self-pairs = 6 unique)
Windows: 10 per pair
Metrics: Transfer Gap (target improvement with source inheritance)
Controls: Bootstrap CI, temporal shuffling, random pairing
```

### 2.2.3 L6 Protocol (Meta-Learning)
```
Policies Compared:
  - RANDOM: Uniform source selection
  - CODE_FIRST: Hand-coded priority [Code, Math, Planning]
  - LEARNED: Lightweight model trained on L5 history

Features: Source prior, pair history, confidence, variance
Evaluation: 3-run reproducibility with tier assignment
```

## 2.3 Circuit Breaker System

### 2.3.1 Purpose
Automatic safety mechanism to halt experiments when:
- Real execution has ceased
- No new auditable artifacts produced
- Trajectory evidence becomes inconsistent
- Hard failure conditions triggered

### 2.3.2 v2.0 Specification (Post-Incident)
```python
CB1: learned_mean < random_mean - 2.0pp    # Much worse than random
CB2: learned_positive_rate < 0.90          # Reliability too low
CB3: learned_regret > baseline_regret + 0.5 # Robustness degraded
CB4: worst_pair < 6.0pp                    # Worst case unacceptable
```

**Key Property**: All thresholds are absolute, not relative to baseline performance.

### 2.3.3 Protocol Evolution Case
Documented in Section 6: v1.0 → v2.0 transition following a rule-design failure at perfect-performance boundary.

## 2.4 Statistical Methods

### 2.4.1 Bootstrap Confidence Intervals
- 10,000 resamples per estimate
- 95% confidence level
- Bias-corrected percentile method

### 2.4.2 Success Tiers
**TIER_1 (Complete)**: Learned > Heuristic + 1pp, regret better, 3/3 reproducible
**TIER_2 (Match)**: Learned ≥ Heuristic - 0.5pp, regret comparable, 2/3 reproducible
**TIER_3 (Marginal)**: Other positive results
**FAIL**: Below acceptable thresholds

### 2.4.3 Claim Discipline
Claims are staged:
- **Pilot**: "Feasibility" or "marginal" only
- **Full**: "Match" or "robust" only
- **Publication**: "Validated" or "demonstrated" only

## 2.5 Reproducibility

### 2.5.1 Git History
- 28+ commits documenting full arc
- Frozen tags for major milestones
- Complete lineage from L4 → L5 → L6

### 2.5.2 Artifact Inventory
- 190+ unique execution windows
- 190+ checksum-verified outputs
- 7 batch trajectory summaries
- 3 control experiment reports

### 2.5.3 Configuration Archive
All hyperparameters, random seeds, and execution configs versioned and referenced.
