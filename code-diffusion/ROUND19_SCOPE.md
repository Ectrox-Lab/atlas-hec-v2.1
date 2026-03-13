# Round 19: RealUNet Backprop Implementation (Minimal)

**Status**: ACTIVE  
**Goal**: Complete gradient-connected learning in narrow RealUNet slice  
**Strict Constraint**: Single trainable path only, no scope creep

---

## Scope (Hard Limits)

### In Scope ✅

1. **Architecture**: Two-layer network maximum
   - Layer 1: input_proj (trainable)
   - Layer 2: hidden (frozen) OR output (frozen)
   - No deeper chains

2. **Task**: Direct regression (not full diffusion)
   - Input → Linear → ReLU → Linear → Output
   - Target: identity or simple transformation
   - Loss: MSE only

3. **Gradient**: Complete chain rule
   - dL/dW1 computed through activation derivatives
   - dL/db1 included
   - No simplification, no approximation

4. **Verification**: Strict 4-point check
   - Loss decreases 50%+ from baseline
   - Gradient norm > 0 (directional)
   - Frozen layers unchanged (hash check)
   - Reload deterministic (seeded re-run)

### Out of Scope ❌

- Full RealUNet (4+ layers)
- Diffusion timesteps
- Classifier-free guidance
- P0-4 matrix re-run
- Adam/optimizer variants
- Multi-batch training loops

---

## Implementation Plan

### Phase 1: Forward Cache (30 min)
```rust
struct MinimalBackpropNet {
    w1: Array2<f64>, b1: Array1<f64>,  // trainable
    w2: Array2<f64>, b2: Array1<f64>,  // frozen
    
    // Cache for backward
    x: Option<Array2<f64>>,      // input
    z1: Option<Array2<f64>>,     // pre-activation
    a1: Option<Array2<f64>>,     // post-ReLU
}
```

### Phase 2: Backward Pass (1 hour)
```rust
fn backward(&mut self, grad_output: &Array2<f64>) -> Gradient {
    // Layer 2 (frozen): just pass gradient back
    let grad_a1 = grad_output.dot(&self.w2.t());
    
    // ReLU derivative
    let grad_z1 = &grad_a1 * self.a1.as_ref().unwrap().mapv(|v| if v > 0.0 { 1.0 } else { 0.0 });
    
    // Layer 1 (trainable): compute gradients
    let x = self.x.as_ref().unwrap();
    let grad_w1 = x.t().dot(&grad_z1);
    let grad_b1 = grad_z1.sum_axis(Axis(0));
    
    Gradient { d_w1: grad_w1, d_b1: grad_b1 }
}
```

### Phase 3: Training Loop (30 min)
```rust
for epoch in 0..epochs {
    let y_pred = model.forward(&x);
    let loss = mse(&y_pred, &y_target);
    
    let grad_output = 2.0 * (&y_pred - &y_target) / n;
    let grad = model.backward(&grad_output);
    
    model.update(&grad, lr);  // SGD on w1, b1 only
}
```

### Phase 4: Verification (30 min)
- [ ] loss[0] > loss[mid] > loss[end]
- [ ] |grad| > 0 consistently
- [ ] frozen_hash unchanged
- [ ] reload_hash identical

---

## Success Criteria

```
Before:
  loss = 0.40
  
After 100 epochs:
  loss < 0.20          (50% reduction)
  |grad_w1| > 0.01     (active learning)
  w2, b2 unchanged     (frozen respected)
```

## Failure Mode

If loss doesn't decrease:
1. Check gradient flow (print intermediate norms)
2. Verify ReLU derivative
3. Try lower learning rate
4. Document specific failure, do NOT expand scope

---

## Evidence Output

```
tests/round19_report.json
{
  "status": "PASS|FAIL",
  "loss_initial": 0.40,
  "loss_final": 0.18,
  "loss_reduction_pct": 55.0,
  "gradient_norm_avg": 0.15,
  "frozen_unchanged": true,
  "reload_deterministic": true
}
```

---

## Time Budget

- Implementation: 2 hours max
- Debugging: 1 hour max
- If exceeds: document blocker, do NOT scope creep

---

## Completion Definition

Round 19 is complete when:
1. Minimal two-layer net shows gradient-connected loss decrease
2. Frozen layers truly frozen (verified by hash)
3. Determinism preserved
4. Report saved to tests/round19_report.json

Round 19 is NOT complete when:
- Full RealUNet works (that's later)
- P0-4 passes (requires full integration)
- Multi-layer chain works (requires scope expansion)

---

*This is implementation work, not just validation. Scope is deliberately narrow to prove mechanism before scaling.*
