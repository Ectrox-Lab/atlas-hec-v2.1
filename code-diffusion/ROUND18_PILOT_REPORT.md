# Round 18 Pilot Report: RealUNet Single-Layer Gradient Integration

**Date**: 2026-03-11  
**Status**: ❌ **FAIL**  
**Scope**: Gradient-based update on input_proj layer with frozen hidden/output layers

---

## Executive Summary

Attempted to integrate real gradient learning into ONE layer of RealUNet while keeping others frozen. Mechanism partially worked but **loss did not decrease**, indicating gradient computation is incomplete.

**Key Finding**: Freezing mechanism and layer isolation work correctly, but full backpropagation chain requires more implementation effort than pilot scope allowed.

---

## Test Configuration

```json
{
  "trainable_layer": "input_proj",
  "frozen_layers": ["hidden_w", "hidden_b", "output_proj", "output_bias"],
  "epochs": 50,
  "learning_rate": 0.01,
  "batch_size": 16,
  "input_dim": 64,
  "hidden_dim": 128
}
```

---

## Results

### ✅ PASS: Infrastructure (4/6)

| Check | Result | Evidence |
|-------|--------|----------|
| Gradient non-zero | ✅ | Avg \|grad_W\| = 0.202 |
| Frozen layers unchanged | ✅ | Hash match with baseline |
| Trainable layer updated | ✅ | Hash changed during training |
| Reload deterministic | ✅ | Bitwise identical after re-run |
| Structure preserved | ✅ | Forward pass works post-training |

### ❌ FAIL: Learning Effectiveness (2/6)

| Check | Result | Evidence |
|-------|--------|----------|
| Loss decreasing | ❌ | 0.402 → 0.397 (1.4% reduction, not monotonic) |
| Task improvement | ❌ | No significant quality gain |

**Overall**: ❌ **PILOT FAIL**

---

## Root Cause Analysis

### Implementation Limitation

The `backward()` function in `RealUNetGradientPilot` uses a **simplified gradient**:

```rust
// Simplified: treats as direct regression on z1
let grad_z1 = grad_output.slice(...);
let grad_w = x.t().dot(&grad_z1_expanded);
```

**What's Missing**: 
1. Full backpropagation chain: output → hidden → input_proj
2. ReLU derivative (chain rule through activations)
3. Proper gradient flow through frozen layers

### Why This Happened

Round 18 scope was intentionally limited to "pilot" level:
- ❌ No full autograd system
- ❌ No manual chain rule through all layers
- ✅ Only infrastructure for single-layer updates

The pilot succeeded at its infrastructure goals but failed at learning because **gradient computation was incomplete**, not because the concept is invalid.

---

## Comparison: Round 16 vs Round 18

| Aspect | Round 16 (Isolation) | Round 18 (Integration) |
|--------|----------------------|------------------------|
| **Result** | ✅ PASS | ❌ FAIL |
| **Gradient** | Complete analytical | Simplified/approximate |
| **Architecture** | Single linear layer | RealUNet slice |
| **Chain Rule** | Direct (y = Wx) | Multi-layer (not implemented) |
| **Lesson** | Gradient mechanism works | Infrastructure works, needs full backprop |

---

## Implications

### What We Learned

1. **Layer freezing works**: Can isolate trainable parameters
2. **Update mechanism works**: SGD updates apply correctly
3. **Determinism preserved**: Checkpoint/reload is solid
4. **Gradient needs work**: Full backprop chain required for learning

### What This Means for Future Work

**Option A: Full Gradient Implementation**
- Implement complete backpropagation through all layers
- Handle ReLU derivatives, chain rule properly
- Estimated effort: 1-2 days

**Option B: Accept Current Limitation**
- Document that RealUNet training requires autograd framework
- Keep pilot as infrastructure validation only
- Future work: integrate with candle/tch for automatic differentiation

**Option C: Hybrid Approach**
- Use Round 16 proof as evidence that gradient learning is possible
- Keep P0 as structural MVP with perturbation training
- Defer full RealUNet training to milestone with proper autograd

---

## Recommendations

### Immediate

- ✅ Document Round 18 as "infrastructure pilot passed, learning mechanism needs full backprop"
- ❌ Do NOT claim RealUNet can learn yet
- ❌ Do NOT extend to second layer until gradient chain is fixed

### Next Steps (Choose One)

| Path | Action | Effort |
|------|--------|--------|
| Deep | Implement full manual backpropagation | 1-2 days |
| Wide | Integrate with candle/tch autograd | 2-3 days |
| Document | Accept limitation, update STATUS.md | 30 min |

---

## Evidence Files

```
experiments/realunet_gradient_pilot.py     # Python wrapper
tests/realunet_gradient_pilot_report.json  # Structured results
src/bin/round18_gradient_pilot.rs          # Main experiment code
src/models/realunet_gradient.rs            # Gradient-enabled model
```

---

## Sign-off

**Round 18 Verdict**: Infrastructure validated, learning mechanism incomplete.

**Impact on Project Status**:
- P0 Structural MVP: ✅ Unchanged (still PASS)
- Round 16 Gradient Proof: ✅ Still valid (isolated case)
- RealUNet Gradient Training: ⏸️ BLOCKED pending full backprop implementation

**Key Principle Maintained**: 
> Do not claim capabilities beyond what is verified. Round 18 failed at learning, so RealUNet gradient training remains unproven.

---

*This report documents a failed pilot. The failure is valuable data: we now know the exact gap between "infrastructure works" and "learning works" — it's the backpropagation chain.*
