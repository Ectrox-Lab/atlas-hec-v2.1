# Project Status: Code-DNA Diffusion

**Last Updated**: 2026-03-11  
**Repository**: https://github.com/Ectrox-Lab/atlas-hec-v2.1

---

## Executive Summary

| Component | Status | Description |
|-----------|--------|-------------|
| **P0 Structural MVP** | ✅ **PASS** | Full architecture: diffusion, sampling, checkpoint, CLI |
| **Round 16 Gradient Proof** | ✅ **PASS** | Genuine gradient-based learning verified in isolation |
| **System-Wide Gradient Training** | ⏸️ **NOT YET INTEGRATED** | RealUNet still uses perturbation-based updates |
| **P0-4 Full-Model Effectiveness** | ⏳ **OPEN / NOT RE-RUN** | Awaiting gradient integration before revalidation |

**Key Principle**: 
> Round 16 verified that genuine gradient-based learning exists in isolation.  
> P0 remains a structural prototype until that mechanism is integrated into RealUNet and revalidated at system level.

---

## Verified Capabilities

### 1. P0 Structural MVP (PASS)

**Scope**: End-to-end architecture without claiming learning effectiveness

| Module | Status | Evidence |
|--------|--------|----------|
| `diffusion/` | ✅ | Forward/reverse diffusion, deterministic sampling |
| `models/` | ✅ | RealUNet with 33k real parameters |
| `sampling/` | ✅ | Seeded RNG, classifier-free guidance |
| `training/` | ⚠️ | Loop works, but updates are perturbation-based |
| `bin/` | ✅ | train, sample, p0_4_verify CLIs functional |

**Critical Limitation**: 
- Training uses `apply_noise()` (random walk), not gradient descent
- P0-4 v2 result: 0.88% divergence, 0% win rate vs untrained
- Parameters change, but do not learn task

**Correct Interpretation**: 
```
Structure:  VALIDATED ✅
Learning:   SIMULATED ⚠️ (not gradient-based)
Quality:    BASELINE ❌ (no improvement over random init)
```

### 2. Round 16 Gradient Learning Proof (PASS)

**Scope**: Minimal isolated experiment proving gradient mechanism works

**Experiment**: Single linear layer learns y = 2x

| Criterion | Result | Threshold | Status |
|-----------|--------|-----------|--------|
| Loss curve | 1.51 → 0.000069 | Monotonic decrease | ✅ PASS |
| Gradient evidence | dL/dW computed analytically | Non-zero, correct direction | ✅ PASS |
| Train > Untrained | 11,057x improvement | >10x gap | ✅ PASS |
| Reload determinism | Hash match | 100% consistent | ✅ PASS |

**Conclusion**: 
> Genuine gradient-based learning is possible in this codebase.  
> The mechanism exists and functions correctly in isolation.

**Key Separation**: 
- Round 16 ≠ "System can learn"
- Round 16 = "Learning mechanism verified, ready for integration"

---

## Completed Work

### Round 18: Gradient Integration Pilot ✅ COMPLETE

**Date**: 2026-03-11  
**Status**: Infrastructure ✅ PASS / Learning ❌ FAIL

**Verdict**: 
> Round 18 verified RealUNet integration infrastructure, but not full learning.

**Infrastructure Verified** (4/6):
- ✅ Gradient computation (non-zero, but simplified)
- ✅ Layer freezing (hidden/output unchanged)
- ✅ Trainable updates (input_proj changes)
- ✅ Reload determinism (identical re-runs)
- ❌ Loss decrease (1.4% reduction, not significant)
- ❌ Task improvement (no quality gain)

**Root Cause**: 
`backward()` used simplified gradient without full backprop chain. 
Missing: chain rule through frozen layers, ReLU derivatives, proper gradient flow.

**Evidence**: ROUND18_PILOT_REPORT.md

### Round 19: Backprop Implementation ✅ COMPLETE

**Date**: 2026-03-11  
**Status**: ✅ **PASS**

**Achievement**: Complete gradient-connected learning in minimal slice

| Check | Result | Evidence |
|-------|--------|----------|
| Loss reduction | ✅ PASS | 62.4% (0.169 → 0.063) |
| Gradient active | ✅ PASS | Avg norm 0.129 |
| Frozen unchanged | ✅ PASS | Hash identical |
| Trainable changed | ✅ PASS | Hash different |
| Reload deterministic | ✅ PASS | Bitwise identical |

**Implementation**: 
- Two-layer network: input → Linear → ReLU → Linear → output
- Complete chain rule through ReLU derivative
- Layer 1 (trainable): gradient via dL/dy @ w2.T * I(z1>0)
- Layer 2 (frozen): no update

**Evidence**: tests/round19_report.json

---

## Pending Work

### Round 20: RealUNet Full Integration (NOT STARTED)

**Goal**: Scale Round 19 mechanism to full RealUNet architecture

**Scope**:
- [ ] Replace RealUNetGradientPilot with full RealUNet backprop
- [ ] Handle 4-layer architecture (input → hidden1 → hidden2 → output)
- [ ] Integrate with diffusion timestep conditioning
- [ ] Verify: loss decreases on actual diffusion task

**Explicitly Out of Scope**:
- P0-4 revalidation (deferred until full integration proven)
- Multi-condition training
- Production-quality hyperparameters

**Success Criteria**:
```
1. RealUNet shows gradient-connected loss decrease
2. All layers respect freeze/trainable boundaries
3. Checkpoint/reload functionality preserved
4. Deterministic sampling maintained
```

### P0-4 Revalidation (BLOCKED → Round 20)

**Prerequisites**: 
1. Round 20 complete and successful (full RealUNet backprop)
2. Gradient learning verified on actual diffusion task

**When to Run**: Only after Round 20 proves full integration

**Expected Outcome** (if Round 20 succeeds):
- JS divergence > 5% (vs current 0.88%)
- Win rate > 50% (vs current 0%)
- Reload determinism maintained

---

## Evidence Standards

### Accepted as Learning Evidence

| Evidence | Required For |
|----------|--------------|
| Loss curve (monotonic decrease) | Round 16, Round 18, P0-4 |
| Gradient computation (non-zero, correct) | Round 16, Round 18 |
| Train vs Untrained (>10x improvement) | Round 16, P0-4 |
| Reload determinism (100% hash match) | All tiers |

### Rejected as Learning Evidence

| Evidence | Why Rejected |
|----------|--------------|
| "Parameter hash changed" | Perturbation also changes hash |
| "Checkpoint file exists" | Serialization ≠ learning |
| "Forward pass works" | Inference ≠ training |
| "Loss computed" | Without gradient, loss doesn't guide |

---

## Historical Context

### P0-4 v1 (2026-03-11)
- Determinism: ❌ FAIL (thread_rng in sampling)
- Divergence: 1.08%
- Win rate: 100% (false positive due to metric bug)
- Overall: FAIL

### P0-4 v2 (2026-03-11)
- Determinism: ✅ PASS (fixed seeded RNG chain)
- Divergence: 0.88%
- Win rate: 0%
- Overall: FAIL
- **Root Cause Identified**: Perturbation-based training

### Round 16 (2026-03-11)
- Gradient mechanism: ✅ VERIFIED in isolation
- Loss: 1.51 → 0.000069
- Accuracy: weight 0.069 → 1.998 (target 2.0)
- **Significance**: Learning mechanism exists

### Round 18 (2026-03-11)
- Infrastructure: ✅ PASS (layer freezing, updates, reload)
- Learning: ❌ FAIL (simplified gradient, no backprop chain)
- Loss: 0.402 → 0.397 (1.4% reduction)
- **Significance**: Integration infrastructure ready, needs full backprop

**Key Separation**:
```
Round 16: Mechanism exists (isolated)
Round 18: Infrastructure works (integrated)
Round 19: Full backprop needed (not started)
```

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-11 | Document P0 limitation | Prevent "hash change = learning" misinterpretation |
| 2026-03-11 | Run Round 16 isolation test | Verify gradient mechanism exists before integration |
| 2026-03-11 | **DO NOT** immediately integrate | Preserve clean separation between mechanism proof and system integration |
| 2026-03-11 | Plan Round 18 pilot | Gradual integration reduces debugging complexity |

---

## Quick Commands

```bash
# Test structural MVP
cargo test --release
cargo run --release --bin train -- --epochs 5
cargo run --release --bin p0_4_verify -- --trained checkpoints/model.pt

# Verify gradient mechanism (isolated)
cargo run --release --bin round16_gradient_verify

# Check status
cat STATUS.md
cat P0_STATUS.md
cat ROUND_16_OBJECTIVE.md
```

---

## Sign-off

**Current System Status**:

| Component | Status | Evidence |
|-----------|--------|----------|
| P0 Structural MVP | ✅ PASS | Full pipeline operational |
| Round 16 Gradient Proof | ✅ PASS | Isolated learning verified |
| Round 18 Infrastructure | ✅ PASS | Integration layer ready |
| **Round 19 Backprop** | ⏸️ **NOT STARTED** | Required for RealUNet learning |
| **P0-4 Revalidation** | ⏸️ **BLOCKED** | Requires Round 19 completion |

**Key Principle Maintained**:
> Round 16 proved mechanism exists.  
> Round 18 proved infrastructure works.  
> RealUNet full training remains blocked until complete backprop is implemented.

**Next Decision Point**:
- **Option A**: Implement Round 19 (full backprop) — when ready to commit 2-3 days
- **Option B**: Maintain current boundary — document as known limitation

**Do Not**:
- Claim RealUNet can learn (Round 18 failed at this)
- Extend perturbation-based training to claim learning
- Re-run P0-4 until Round 19 succeeds

---

*This document maintains strict separation between "structure exists", "mechanism works", "infrastructure ready", and "system learns". Do not conflate these tiers.*
