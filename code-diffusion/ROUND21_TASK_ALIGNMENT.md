# Round 21: Task-Aligned Diffusion Conditioning Pilot

**Status**: DEFINED (Not Started)  
**Goal**: Align training objective with generation quality  
**Predecessor**: Round 20 (mechanism proven, task effect not proven)

---

## Current Situation (Post-Round 20 / P0-4)

| Tier | Status | Evidence |
|------|--------|----------|
| Tier 1 Structure | ✅ PASS | Full pipeline operational |
| Tier 2 Mechanism | ✅ PASS | Gradient backprop working |
| Tier 3 Task Effect | ❌ NOT PROVEN | P0-4 divergence 0.34% < 5% |

**Key Finding**:
> Mechanism proven, task effectiveness not yet proven.

Gradient training works (13.8% loss reduction on regression), but does not translate to diffusion generation quality improvement.

---

## Root Cause Hypothesis

**Not**: "Need more training" (Option A - rejected)

**Likely**: "Task misalignment"

Current Round 20 training:
```
Task: Identity regression (input ≈ output)
Loss: MSE on direct reconstruction
Result: Model learns to copy, not to denoise
```

Real diffusion needs:
```
Task: Noise prediction (x_t → predict noise)
Loss: MSE on noise
Conditioning: timestep t, class c
Result: Model learns reverse process
```

---

## Round 21 Scope

### Option B1: Noise Prediction Training (Recommended)

Replace regression with actual diffusion objective:

```rust
// Forward diffusion
let x_t = sqrt(alpha_t) * x_0 + sqrt(1 - alpha_t) * noise;

// Predict noise (not reconstruct x)
let noise_pred = unet.forward(&x_t, t, class);

// Loss on noise
let loss = mse(&noise_pred, &noise);
```

**Expected outcome**:
- Training objective aligned with generation task
- P0-4 divergence should increase significantly

### Option B2: Conditional Generation Interface

Add explicit conditioning:
- Timestep embedding
- Class embedding  
- Cross-attention or simple concatenation

### Option B3: Curriculum Training

Progressive difficulty:
1. Start with few timesteps (simpler denoising)
2. Gradually increase to full 1000 steps
3. Mix conditioned and unconditioned

---

## Not in Scope (Explicitly Excluded)

❌ Option A: "Just train longer"
- 1000+ epochs on wrong task
- Low expected return
- Only if B proves insufficient

❌ Full P0-4 revalidation
- Until task alignment demonstrated
- Avoid premature testing

---

## Success Criteria

| Check | Target | Evidence |
|-------|--------|----------|
| Task alignment | Noise prediction loss | Loss decreases on actual diffusion |
| Quality proxy | Denoising step | Single-step denoising improves |
| Conditioning | t/c affects output | Different t/c → different outputs |

---

## Relationship to P0-4

**Current**: P0-4 divergence 0.34% (fail)

**After Round 21 success**: Re-run P0-4 with task-aligned model

**Target**: Divergence > 5%, Tier 3 PASS

---

## Decision Rationale

Why C + B, not A:

```
Evidence chain:
  R20: Gradient works ✓
  P0-4: Effect doesn't transfer ✗
  
Interpretation:
  Problem = task misalignment
  Solution = align task, not more training
```

A would optimize wrong objective more.
B fixes the objective.

---

**Next Action**: Implement B1 (noise prediction) when ready to proceed.

*All changes synced to: https://github.com/Ectrox-Lab/atlas-hec-v2.1*
