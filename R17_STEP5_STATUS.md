# R17.4 Step 5 Validation - Ready for Execution

**Date**: 2026-03-09  
**Status**: ✅ Infrastructure Ready - Awaiting Patch A Shadow Data

---

## What Was Prepared

### 1. 50-Sample Test Set

**File**: `r17_validation/data/step5_samples.json`

**Distribution**:
| Bucket | Count | Percentage |
|--------|-------|------------|
| live_auto | 25 | 50% |
| live_manual | 15 | 30% |
| replay_real | 10 | 20% |

**Coverage**: 50 samples with varied complexity (simple/medium/complex)

### 2. Validation Configuration

**Global Thresholds**:
- deliberation = 70
- review = 80

**Targets**:
- overall FB ≤ 15%
- live_auto FB ≤ 20%
- alignment ≥ 75%

**Redlines** (trigger rollback):
- alignment < 75%
- live_manual FB > 25%
- overall FB > 18%

### 3. Automated Validation Script

**File**: `r17_validation/step5/validator.py`

**Outputs**:
```json
{
  "summary": {
    "overall_fb": 0.15,
    "live_auto_fb": 0.18,
    "live_manual_fb": 0.12,
    "alignment": 0.78,
    "targets_met": {...},
    "redlines_triggered": [...],
    "should_rollback": false
  },
  "bucket_stats": {...},
  "checkpoints": [...]
}
```

### 4. Checkpoint Schedule

Checkpoints at fixed intervals:
- 10 samples
- 20 samples
- 30 samples
- 40 samples
- 50 samples

Each checkpoint shows:
- Current metrics
- Redline status
- Go/No-Go recommendation

---

## Test Run Results (Mock Data)

**Note**: Test used mock data with ~12% error rate

| Checkpoint | Overall FB | Live Auto FB | Alignment | Redlines | Action |
|------------|------------|--------------|-----------|----------|--------|
| 10 | 30% | 43% | 70% | 2 triggered | 🚨 ROLLBACK |
| 20 | 30% | 27% | 70% | 2 triggered | 🚨 ROLLBACK |
| 30 | 30% | 33% | 70% | 2 triggered | 🚨 ROLLBACK |
| 40 | 25% | 26% | 75% | 1 triggered | 🚨 ROLLBACK |
| 50 | 22% | 24% | 78% | 1 triggered | 🚨 ROLLBACK |

**Result**: Validation framework correctly identified redline violations.

---

## Next Steps

### To Run Actual Validation:

1. **Prepare Patch A outputs** for all 50 samples
   ```python
   # Format for each sample:
   {
     "sample_id": "S5-001",
     "action": "approve|reject|request_changes|escalate",
     "deliberation_score": 75.5,
     "review_score": 82.0,
     "processing_time_ms": 120.5
   }
   ```

2. **Run validation**:
   ```bash
   cd r17_validation/step5
   python3 validator.py --samples data/step5_samples.json \
                        --patch-a-outputs data/patch_a_outputs.json \
                        --output results/final_validation.json
   ```

3. **Check results** at each checkpoint

4. **Final Go/No-Go** at 50 samples

---

## Files

```
r17_validation/
├── data/
│   └── step5_samples.json          # 50 sample test set
├── results/
│   ├── step5_report.json           # Summary report
│   └── step5_report_full.json      # Full report with all samples
└── step5/
    ├── validation_config.py        # Configuration
    ├── sample_generator.py         # Test set generator
    └── validator.py                # Main validation script
```

---

## Decision Criteria

| Condition | Threshold | Action |
|-----------|-----------|--------|
| alignment ≥ 75% | target met | ✅ continue |
| overall FB ≤ 15% | target met | ✅ continue |
| live_auto FB ≤ 20% | target met | ✅ continue |
| alignment < 75% | **redline** | 🚨 **rollback** |
| live_manual FB > 25% | **redline** | 🚨 **rollback** |
| overall FB > 18% | **redline** | 🚨 **rollback** |

---

## Status

- [x] 50-sample test set prepared
- [x] Buckets: live_auto/live_manual/replay_real
- [x] Automated validation script
- [x] Checkpoint mechanism (10/20/30/40/50)
- [x] Redline detection
- [x] JSON/Markdown output
- [ ] Patch A shadow data (awaiting)
- [ ] Live validation run

**Ready for Step 5 execution upon receipt of Patch A outputs.**
