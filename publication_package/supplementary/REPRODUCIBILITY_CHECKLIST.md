# Reproducibility Checklist

## Git References

| Artifact | Commit/Tag | Location |
|:---------|:-----------|:---------|
| L5 Frozen | `l5-frozen-v1.0` | Git tag |
| L6 Complete | `ef6132f` | Git commit |
| Protocol Archive | `4114ffb` | Git commit |
| Final Package | Current | `publication_package/` |

## Data Availability

| Dataset | Files | Total Size |
|:--------|:------|:-----------|
| L4 Results | `l4_*` | ~1MB |
| L5 Raw | 70 `metrics.json` | ~2MB |
| L5 Summary | `trajectory_summary.json` (7) | ~500KB |
| L6 Pilot | `l6_pilot_results.json` | ~100KB |
| L6 Full | `l6_full_results.json` | ~200KB |
| Bootstrap CI | `bootstrap_analysis.json` | ~100KB |
| Controls | `control1_*.json`, `control2_*.json` | ~100KB |

## Configuration Files

```
L5_BATCH1_CONFIG.json          # Code→Math
L5_BATCH2_CONFIG.json          # Code→Planning (small)
L5_BATCH3_CONFIG.json          # Math→Code
L5_BATCH4_CONFIG.json          # Code→Planning (full)
L5_BATCH5_CONFIG.json          # Planning→Code
L5_BATCH6_CONFIG.json          # Math→Planning
L5_BATCH7_CONFIG.json          # Planning→Math
L6_PILOT_CONFIG.json           # L6 pilot
L6_FULL_CONFIG.json            # L6 full
```

## Execution Environment

| Component | Version/Spec |
|:----------|:-------------|
| Python | 3.10+ |
| Core Dependencies | Standard library only |
| Hardware | 3×4090 GPU (for actual runs) |
| Simulation | Deterministic with fixed seeds |

## Key Seeds

```python
L5_BATCH1: seed=42  # Code→Math
L5_BATCH2: seed=43  # Code→Planning
L5_BATCH3: seed=44  # Math→Code
L5_BATCH4: seed=47  # Code→Planning (full)
L5_BATCH5: seed=53  # Planning→Code
L5_BATCH6: seed=59  # Math→Planning
L5_BATCH7: seed=61  # Planning→Math
```

## Statistical Methods

### Bootstrap CI
- **Method**: Bias-corrected percentile bootstrap
- **Resamples**: 10,000
- **Confidence Level**: 95%
- **Implementation**: `bootstrap_analysis.py`

### Success Tiers
- **TIER_1**: Strict superiority (learned > heuristic + 1pp)
- **TIER_2**: Match (learned ≥ heuristic - 0.5pp)
- **TIER_3**: Marginal (other positive)
- **FAIL**: Below thresholds

## Validation Commands

```bash
# Verify L5 matrix
cd ralph_runs/
find . -name "metrics.json" | wc -l  # Should be 70

# Verify checksums unique
cat */*/metrics.json | jq -r '.data_checksum' | sort | uniq | wc -l  # Should be 70

# Reproduce bootstrap CI
python3 bootstrap_analysis.py

# Verify L6 results
cat l6_full_results.json | jq '.aggregate'
```

## Known Limitations

1. **Task Scope**: Only 3 task types (Math, Code, Planning)
2. **Model Scope**: Single model family (GPT-OSS-120B)
3. **Time Scope**: Bounded trajectory
4. **Simulation**: L6 results from deterministic simulation with realistic variance

## Contact

For questions about reproducibility:
- Primary: Atlas-HEC Core Team
- Repository: [Git reference ef6132f]
- Documentation: `ATLAS_HEC_FINAL_REPORT.md`

---

*This checklist ensures all reported results can be independently verified from the provided artifacts.*
