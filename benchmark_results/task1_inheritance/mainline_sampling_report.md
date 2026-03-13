# Mainline Phase 2 - Sampling Report

**Date**: 2026-03-14  
**Method**: Stratified sampling with control families  
**Target**: 30 candidates per round (total 91)

---

## Sampling Rules Applied

1. **Target family**: F_P3T4M4 (convergence family) - extra +1
2. **Round B gained**: P2/P3-T4 families (F_P2T4M3, F_P3T4M3, F_P4T4M3)
3. **Control families**: F_P3T3M2, F_P3T3M4, F_P2T3M4, F_P2T4M2
4. **Leakage test**: Suspicious new families (P1, P4, T5)
5. **Per family**: Top 2 by Shadow throughput (up to 3 for high-frequency)
6. **Per seed**: Minimum 8 representatives

---

## Sample Summary

| Round | Candidates | Seeds | Families | Selection Categories |
|-------|-----------|-------|----------|---------------------|
| **Round A** | 30 | 1000:14, 1001:8, 1002:8 | 12 | target:3, gained:4, control:7, fill:10, balance:6 |
| **Round B** | 31 | 1000:13, 1001:9, 1002:9 | 16 | target:3, gained:6, control:8, suspicious:2, fill:12 |
| **Ablation** | 30 | 1000:14, 1001:8, 1002:8 | 12 | target:3, gained:4, control:7, fill:12, balance:4 |

---

## Family Distribution (Samples)

| Family | Round A | Round B | Ablation | Notes |
|--------|---------|---------|----------|-------|
| F_P3T4M4 ★ | 4 | 3 | 3 | Target approved family |
| F_P2T4M3 | 2 | 2 | 2 | Round B gained |
| F_P3T4M3 | 2 | 2 | 4 | Round B gained |
| F_P4T4M3 ⚠ | 0 | 2 | 0 | Suspicious new (P4) |
| F_P1T3M3 ⚠ | 0 | 1 | 0 | Suspicious new (P1) |
| F_P3T5M5 ⚠ | 0 | 1 | 0 | Suspicious new (T5) |
| F_P3T3M2 | 3 | 2 | 2 | Control stable |
| F_P3T3M4 | 4 | 2 | 4 | Control stable |
| F_P2T4M4 | 2 | 3 | 3 | Control stable |
| F_P2T3M4 | 4 | 2 | 1 | Control stable |
| F_P2T3M2 | 2 | 2 | 3 | Fill |
| F_P2T3M3 | 2 | 2 | 2 | Fill |
| F_P3T3M3 | 2 | 2 | 2 | Fill |
| F_P3T4M2 | 2 | 1 | 2 | Fill |
| F_P2T4M2 | 1 | 2 | 2 | Fill |
| F_P2T2M3 | 0 | 2 | 0 | Fill (new in B) |

★ = Target approved family  
⚠ = Suspicious new families (leakage test)

---

## Validation Checklist

- ✅ Target family F_P3T4M4 included in all rounds
- ✅ Round B gained families (P2/P3-T4) included
- ✅ Control families (Round A stable) included
- ✅ Suspicious new families in Round B (leakage test)
- ✅ Minimum 8 per seed (all rounds)
- ✅ Sample size ~30 per round

---

## Key Observations

### Round B Family Shift (in samples)

| Shift Type | Families | Observation |
|------------|----------|-------------|
| **Gained** | F_P4T4M3, F_P2T2M3 | P4 and T2 families appear (new structure) |
| **Stable** | F_P3T4M4, F_P2T4M3, F_P3T4M3 | Core P2/P3-T4 families maintained |
| **Reduced** | F_P3T3M2, F_P3T3M4 | P3-T3 families less represented |

### Leakage Test

Round B includes suspicious new families:
- **F_P1T3M3**: P1 (unusual pressure)
- **F_P4T4M3**: P4 (high pressure, untested)
- **F_P3T5M5**: T5 (unusual triage)

If these families succeed in Mainline, it indicates "new module leakage" rather than "reuse of stable families".

---

## Output Files

```
benchmark_results/task1_inheritance/
├── mainline_input_a/
│   ├── mainline_sample.json
│   └── candidate_ids.txt
├── mainline_input_b/
│   ├── mainline_sample.json
│   └── candidate_ids.txt
└── mainline_input_ablation/
    ├── mainline_sample.json
    └── candidate_ids.txt
```

---

## Next Steps: Mainline Phase 2

Execute Mainline evaluation on sampled candidates:

```bash
# Round A (GPU 0)
python superbrain/mainline/run_mainline_phase2.py --round a --gpu 0

# Round B (GPU 1)  
python superbrain/mainline/run_mainline_phase2.py --round b --gpu 1

# Ablation (GPU 2)
python superbrain/mainline/run_mainline_phase2.py --round ablation --gpu 2
```

**Expected outputs** (per round):
- `mainline_effectiveness_report.json` (Table A)
- `mainline_compositionality_report.json` (Table B)
- `ab_comparison_summary.json` (cross-round comparison)

---

**Status**: Sampling complete → Ready for Mainline Phase 2
