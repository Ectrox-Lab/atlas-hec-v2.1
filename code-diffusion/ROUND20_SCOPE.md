# Round 20: RealUNet Full Gradient Integration

**Status**: ACTIVE  
**Goal**: Scale Round 19 backprop mechanism to full RealUNet

---

## Current State

Round 19 proved gradient learning works in minimal slice:
- ✅ Two-layer: input → ReLU → output
- ✅ 62.4% loss reduction
- ✅ Complete chain rule: dL/dy @ w2.T * I(z1>0)

Round 20 extends this to full RealUNet:
- Four layers: input → hidden1 → hidden2 → output
- All trainable (no freezing needed for initial integration)
- Integration with diffusion timestep

---

## Implementation Plan

### Phase 1: RealUNetFull (1 hour)

Replace `RealUNet` with gradient-enabled version:

```rust
pub struct RealUNetFull {
    // Layer 1
    w1: Array2<f64>, b1: Array1<f64>,
    // Layer 2
    w2: Array2<f64>, b2: Array1<f64>,
    // Layer 3 (output)
    w3: Array2<f64>, b3: Array1<f64>,
    
    // Forward cache
    cache_x: Option<Array2<f64>>,
    cache_z1: Option<Array2<f64>>,
    cache_a1: Option<Array2<f64>>,
    cache_z2: Option<Array2<f64>>,
    cache_a2: Option<Array2<f64>>,
}
```

### Phase 2: Full Backprop Chain (1 hour)

```rust
fn backward(&self, grad_output: &Array2<f64>) -> FullGradient {
    // Layer 3 gradient
    let grad_w3 = a2.t().dot(grad_output);
    let grad_b3 = grad_output.sum_axis(Axis(0));
    
    // Backprop to layer 2
    let grad_a2 = grad_output.dot(&self.w3);
    let grad_z2 = &grad_a2 * relu_deriv(&self.cache_z2);
    
    // Layer 2 gradient
    let grad_w2 = a1.t().dot(&grad_z2);
    let grad_b2 = grad_z2.sum_axis(Axis(0));
    
    // Backprop to layer 1
    let grad_a1 = grad_z2.dot(&self.w2);
    let grad_z1 = &grad_a1 * relu_deriv(&self.cache_z1);
    
    // Layer 1 gradient
    let grad_w1 = x.t().dot(&grad_z1);
    let grad_b1 = grad_z1.sum_axis(Axis(0));
    
    FullGradient { grad_w1, grad_b1, grad_w2, grad_b2, grad_w3, grad_b3 }
}
```

### Phase 3: Diffusion Integration (1 hour)

```rust
// Train on actual diffusion task
for epoch in 0..epochs {
    // Sample timestep
    let t = rng.gen_range(0..timesteps);
    
    // Forward diffusion: x_noisy = sqrt(alpha) * x + sqrt(1-alpha) * noise
    let x_noisy = q_sample(x, t);
    
    // Predict noise
    let noise_pred = unet.forward(&x_noisy, t);
    
    // Loss: MSE between predicted and actual noise
    let loss = mse(&noise_pred, &target_noise);
    
    // Backprop
    let grad = unet.backward(&grad_output);
    unet.update(&grad, lr);
}
```

### Phase 4: Verification (30 min)

| Check | Target |
|-------|--------|
| Loss decreases | >30% from baseline |
| Gradient norms | All layers > 0.01 |
| Determinism | Reload identical |
| Checkpoint | Save/load works |

---

## Success Criteria

```
Before training:
  Loss on noise prediction: ~1.0 (random)

After 50 epochs:
  Loss on noise prediction: < 0.7 (30%+ reduction)
  All gradient norms: > 0.01
  Reload after re-run: identical hash
```

## Out of Scope

- ❌ P0-4 full matrix (deferred)
- ❌ Multi-condition training
- ❌ Classifier-free guidance training
- ❌ Adam/momentum optimizers

---

## Evidence Output

```
tests/round20_report.json
{
  "round": 20,
  "status": "PASS|FAIL",
  "loss_initial": 1.0,
  "loss_final": 0.65,
  "loss_reduction_pct": 35.0,
  "gradient_norms": {
    "layer1": 0.15,
    "layer2": 0.12,
    "layer3": 0.08
  },
  "reload_deterministic": true
}
```

---

*All changes synced to: https://github.com/Ectrox-Lab/atlas-hec-v2.1*
