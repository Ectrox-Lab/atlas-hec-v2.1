# P2.6 Workstream 1: Scale-Aware Schema v1.0

**Status**: 🟢 IN PROGRESS (Accelerated)  
**Start**: 2026-03-12 20:30 UTC  
**Target**: 2026-03-13 06:00 UTC (9 hours, accelerated from Week 1)

---

## Core Problem Solved

Current SR1 fingerprint conflates **scale effects** with **structural differences**.

Example from R6:
- Observation: CWCI drops at 6x
- Misclassified: "Specialist routing ineffective"
- Actually: Normal 6x boundary behavior (12.5% degradation expected)

## Schema v1.0 Definition

```yaml
# DIMENSION 1: Scale-Normalized Metrics
metrics:
  raw_cwci: "Direct measurement"
  
  scale_normalized_cwci:
    formula: "(cwci - baseline_4x) / expected_6x_variance"
    interpretation:
      "> 0": "Better than 6x expected"
      "= 0": "Matches 6x expected"
      "< 0": "Worse than 6x expected (potential SR effect)"
    
  degradation_attribution:
    scale_component: "From 4x→6x envelope model"
    sr_component: "Residual = true SR effect"

# DIMENSION 2: Seed-Stratified Analysis
seed_classification:
  stable: "7/8 seeds, CWCI ~0.64"
  degradable: "1/8 seeds, CWCI dips to ~0.57"
  
analysis_requirement: "Report SR effects separately for each class"

# DIMENSION 3: Time-Resolved Comparison
windows:
  pre_degradation: "ticks 0-500"
  during_degradation: "seed-specific dynamic window"
  post_failover: "post-failover recovery comparison"
  
comparison: "SR vs baseline at each phase"

# DIMENSION 4: Cross-Scale Baseline
required_samples:
  OctopusLike_4x: ">= 10 samples"
  OctopusLike_6x: ">= 10 samples"
  per_seed: "All 8 seeds represented"
```

---

## Immediate Actions (Tonight)

1. **Baseline Sampling Started**: 22:00 UTC
2. **Seed Scan Initiated**: 22:30 UTC
3. **Schema Spec Finalization**: 06:00 UTC tomorrow

---

**Status**: Schema framework DEFINED, implementation in progress
