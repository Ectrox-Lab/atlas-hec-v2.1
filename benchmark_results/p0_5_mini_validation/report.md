# P0-5 Mini Validation Report

**Timestamp:** 2026-03-14T02:24:49.423979694+08:00

**Overall Status:** ❌ FAIL

## Failures

- Only 2/3 seeds showed positive improvement
- Mean improvement 0.23% below threshold 5.00%

## Configuration

- Seeds: [42, 123, 999]
- Warmup Steps: 100
- Train Steps: 500
- Batch Size: 8
- Learning Rate: 0.001
- Sequence Length: 128
- Hidden Dim: 64
- Channels: 16
- Timesteps: 1000

## Per-Seed Results

| Seed | Initial Loss | Final Loss | Improvement % | Reload Δ | Status |
|------|--------------|------------|---------------|----------|--------|
| 42 | 1.016385 | 1.010705 | 0.56% | 0.00020610 | ⚠️ |
| 123 | 1.026010 | 1.022961 | 0.30% | 0.00024389 | ⚠️ |
| 999 | 1.030832 | 1.032531 | -0.16% | 0.00025543 | ❌ |

## Trained vs Untrained Comparison

| Seed | Untrained Loss | Trained Loss | Improvement % | Noise Error (U) | Noise Error (T) |
|------|----------------|--------------|---------------|-----------------|-----------------|
| 42 | 1.016385 | 1.010705 | 0.56% | 0.804583 | 0.802359 |
| 123 | 1.026010 | 1.022961 | 0.30% | 0.808290 | 0.807075 |
| 999 | 1.030832 | 1.032531 | -0.16% | 0.810289 | 0.811005 |

## Aggregate Metrics

- Mean Improvement: 0.23%
- Std Improvement: 0.30%
- Min Improvement: -0.16%
- Seeds with Positive Improvement: 2/3
- Mean Reload Δ: 0.00023514
- Max Reload Δ: 0.00025543
- Trained vs Untrained Mean Improvement: 0.00%

## Validation Criteria

- ✅ 3/3 seeds positive improvement: FAIL
- ✅ Mean improvement > 5%: FAIL (0.23%)
- ✅ Reload consistency (mean Δ < 0.01): PASS
