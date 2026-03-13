# Bridge Ultra-Fast Evaluation Report

**Phase**: 1 (Shadow-only screening)  
**Date**: 2026-03-14  
**Mode**: Ultra-fast (Shadow only, 50 tasks per candidate)

---

## Executive Summary

| Round | Total | Passed | Pass Rate | Avg Throughput Δ |
|-------|-------|--------|-----------|------------------|
| **Round A** (Control) | 150 | 150 | **100.0%** | +21.5% |
| **Round B** (Treatment) | 150 | 150 | **100.0%** | +21.5% |
| **Ablation** (bias=0.0) | 150 | 150 | **100.0%** | +21.5% |

**Key Finding**: Shadow stage alone cannot discriminate between rounds. All candidates pass the -0.5% tolerance threshold.

---

## Detailed Results

### Pass Rate by Seed

| Seed | Round A | Round B | Ablation |
|------|---------|---------|----------|
| 1000 | 50/50 (100%) | 50/50 (100%) | 50/50 (100%) |
| 1001 | 50/50 (100%) | 50/50 (100%) | 50/50 (100%) |
| 1002 | 50/50 (100%) | 50/50 (100%) | 50/50 (100%) |

### Top Families by Pass Rate

All families show 100% pass rate in Shadow stage. Top 5 by candidate count:

| Family | Round A | Round B | Ablation |
|--------|---------|---------|----------|
| F_P3T3M2 | 15 | - | 15 |
| F_P2T4M4 | 14 | - | 14 |
| F_P3T4M4 | 12 | 12 | 12 |
| F_P2T3M4 | 12 | - | 12 |
| F_P3T3M4 | 12 | - | 12 |

*Note: Round B shows different family distribution due to inheritance bias*

---

## Analysis

### 1. Shadow Threshold Too Permissive

Current Shadow criteria:
```python
status = "PASS" if throughput_delta > -0.005 else "FAIL"  # -0.5% tolerance
```

All generated candidates show +15% to +30% throughput vs baseline (2.14%), far exceeding the -0.5% threshold.

### 2. Discrimination Requires Dry Run or Mainline

The Shadow stage (100 tasks) is designed for coarse filtering, not fine discrimination. To see differences between rounds:

- **Dry Run**: 1000 tasks, 3 seeds, variance analysis (CV < 0.15 for Tier B)
- **Mainline**: 10k tasks, strict resource constraints, fault injection

### 3. Family Distribution Shift Observable

While pass rates are identical, family distributions differ:

| Family | Round A | Round B | Δ |
|--------|---------|---------|---|
| F_P3T4M4 | 12 (8%) | 12 (8%) | 0 |
| F_P2T4M3 | 8 (5%) | 16 (11%) | +8 |
| F_P3T4M3 | 7 (5%) | 11 (7%) | +4 |

*Round B shows shift toward P2/P3-T4 families*

---

## Next Steps: Phase 2 Mainline

Since all 450 candidates passed Bridge Shadow, Phase 2 Mainline should evaluate:

**Sampling Strategy** (due to computational cost):
1. **Tier B candidates** from Dry Run (if available)
2. **Top 20% by Shadow throughput** from each round
3. **Stratified sample** by family

**Metrics to Collect** (E-T1-003):
- Mainline approve rate
- Mean throughput delta
- Failure archetype recurrence

**Metrics to Collect** (E-COMP-002):
- Final successful family distribution
- Reuse rate of approved families
- New family leakage

---

## Output Files

```
benchmark_results/task1_inheritance/
├── bridge_uf_a/
│   ├── bridge_uf_summary.json
│   ├── bridge_uf_by_seed.json
│   ├── bridge_uf_by_family.json
│   └── bridge_uf_passed_candidates.json
├── bridge_uf_b/
│   └── ...
└── bridge_uf_ablation/
    └── ...
```

---

**Status**: Phase 1 Complete → Ready for Phase 2 Mainline (sampled)
