# Round 16 Objective: Minimal Real Gradient Learning Loop

**Status**: Draft  
**Goal**: Verify ONE module can learn via true gradient descent

---

## Scope (Minimal)

Target: Single linear layer  
Task: Learn y = 2x (synthetic regression)  
Metric: MSE loss < 0.01 after 100 steps

## Verification Standard (Strict)

| Evidence | Required | Current |
|----------|----------|---------|
| Loss curve (decreasing) | ✅ Mandatory | ❌ N/A |
| Gradient computation | ✅ Mandatory | ❌ perturbation |
| Train vs Untrained win | ✅ Mandatory | ❌ 0% win rate |
| Deterministic reload | ✅ Mandatory | ✅ fixed |
| Task metric improvement | ✅ Mandatory | ❌ N/A |

## Rejected Evidence

- ❌ "Parameter hash changed" 
- ❌ "Checkpoint file exists"
- ❌ "Forward pass works"

## Success Criteria

```
1. loss_0 > loss_50 > loss_100 (monotonic decrease)
2. trained_mse < 0.01 < untrained_mse (10x gap)
3. Reload + same seed = same output (determinism)
```

## Failure Mode

If gradient computation unstable or loss doesn't decrease:
- Document numerical issue
- Try simpler module (scalar instead of matrix)
- Do NOT claim partial success

---

**Reference**: P0_STATUS.md for why perturbation ≠ learning
