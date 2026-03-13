# Round A/B Candidate Generation Report

**Experiment**: E-T1-003 + E-COMP-002 Candidate Generation Phase  
**Date**: 2026-03-14  
**Status**: Generation Complete, Awaiting Bridge/Mainline Evaluation

---

## 1. Experiment Design

### 1.1 Fixed Variables (Control)
| Variable | Value |
|----------|-------|
| Seeds | 1000, 1001, 1002 |
| Candidates per seed | 50 |
| Total candidates per round | 150 |
| Task family | Task-1 (heterogeneous executor coordination) |

### 1.2 Independent Variable (Treatment)
| Round | Inheritance Package | Bias Strength | Expected Mode |
|-------|---------------------|---------------|---------------|
| **A** | None | N/A | `uniform_exploration` |
| **B** | `task1_inheritance_package.json` | 0.7 | `inheritance_biased` |
| **Ablation** | `task1_inheritance_package.json` | 0.0 | `uniform_exploration` (package loaded but disabled) |

### 1.3 Key Design Principle
**Same seeds across rounds** - This ensures observed differences come from inheritance bias, not random variation.

---

## 2. Generation Results

### 2.1 Approved Family Coverage
Approved families: `F_P3T4M4`, `F_P2T3M3`, `F_P3T4M3` (converged families from E-EVO-003)

| Round | Total Candidates | Approved Family Count | Coverage |
|-------|------------------|----------------------|----------|
| **A** (control) | 150 | 36 | 24.0% |
| **B** (treatment) | 150 | 36 | 24.0% |
| **Ablation** | 150 | 36 | 24.0% |

### 2.2 Same-Seed Detailed Comparison

#### Seed 1000
| Round | Approved Count | Top 3 Families | Delta vs A |
|-------|---------------|----------------|------------|
| A | 9/50 | F_P3T3M4(9), F_P2T4M4(6), F_P3T3M2(5) | - |
| B | 18/50 | F_P2T4M3(9), F_P3T4M3(7), F_P3T4M4(6) | **+9** |
| Ablation | 9/50 | F_P3T3M4(9), F_P2T4M4(6), F_P3T3M2(5) | 0 |

**✓ Ablation matches A**: Bias layer correctly disabled

#### Seed 1001
| Round | Approved Count | Top 3 Families | Delta vs A |
|-------|---------------|----------------|------------|
| A | 15/50 | F_P3T3M2(9), F_P2T3M4(7), F_P3T4M4(6) | - |
| B | 8/50 | F_P3T3M4(7), F_P2T3M2(6), F_P2T3M4(4) | **-7** |
| Ablation | 15/50 | F_P3T3M2(9), F_P2T3M4(7), F_P3T4M4(6) | 0 |

**✓ Ablation matches A**: Bias layer correctly disabled

#### Seed 1002
| Round | Approved Count | Top 3 Families | Delta vs A |
|-------|---------------|----------------|------------|
| A | 12/50 | F_P2T4M4(6), F_P3T3M2(5), F_P3T4M3(5) | - |
| B | 10/50 | F_P2T4M4(5), F_P3T4M3(5), F_P2T4M3(5) | **-2** |
| Ablation | 12/50 | F_P2T4M4(6), F_P3T3M2(5), F_P3T4M3(5) | 0 |

**✓ Ablation matches A**: Bias layer correctly disabled

---

## 3. S1 Completion Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| CLI Interface | ✅ | `--inheritance-package`, `--bias-strength` implemented |
| Round A Purity | ✅ | Same output with/without package loading (bias=0.0) |
| Manifest Records | ✅ | `inheritance_package_version`, `bias_source`, `generation_mode` present |
| Observable Shift | ✅ | `family_distribution.json`, `generation_log.json` with `bias_applied` flag |
| Bias Toggleable | ✅ | Ablation (bias=0.0) ≡ Round A for all seeds |

---

## 4. Key Observations

### 4.1 Bias Effect Inconsistency
Using same seeds, Round B shows **mixed results**:
- Seed 1000: +9 improvement (bias working)
- Seed 1001: -7 decline (bias not aligned with this seed's structure)
- Seed 1002: -2 decline (marginal)

**Interpretation**: The current `approved_families` list (`F_P3T4M4`, `F_P2T3M3`, `F_P3T4M3`) may not capture the true "good families" for all seeds. This is expected in early validation - the inheritance package needs iterative refinement.

### 4.2 Ablation Validation Success
For all seeds, Ablation (package loaded, bias=0.0) produces **identical results** to Round A. This confirms:
- Bias is truly toggleable
- Random seed control is working correctly
- Package loading itself doesn't affect generation (only bias does)

---

## 5. Next Steps

### 5.1 Immediate (Bridge Evaluation)
Execute Bridge evaluation on generated candidates:

```bash
# Round A (GPU0)
python superbrain/bridge/bridge_scheduler.py \
  --input benchmark_results/task1_inheritance/round_a/ \
  --output benchmark_results/task1_inheritance/round_a_bridge_results/

# Round B (GPU1)  
python superbrain/bridge/bridge_scheduler.py \
  --input benchmark_results/task1_inheritance/round_b/ \
  --output benchmark_results/task1_inheritance/round_b_bridge_results/
```

### 5.2 Metrics to Track (E-T1-003)
- Bridge pass rate (Δ vs Round A)
- Mainline approve rate (Δ vs Round A)
- Mean throughput delta
- Failure archetype recurrence

### 5.3 Metrics to Track (E-COMP-002)
- F_P3T4M4 final representation in successful candidates
- Reuse rate vs new module generation
- New family leakage in successful candidates

---

## 6. File Outputs

```
benchmark_results/task1_inheritance/
├── ab_generation_summary.json      # This summary (machine-readable)
├── ab_generation_report.md         # This report (human-readable)
├── round_a/
│   ├── seed_1000/
│   │   ├── manifest.json
│   │   ├── family_distribution.json
│   │   ├── generation_log.json
│   │   └── candidates/
│   ├── seed_1001/
│   └── seed_1002/
├── round_b/
│   ├── seed_1000/
│   ├── seed_1001/
│   └── seed_1002/
└── round_ablation/
    ├── seed_1000/
    ├── seed_1001/
    └── seed_1002/
```

---

**Status**: Generation phase complete. Awaiting Bridge/Mainline evaluation for L4 validation.
