# Candidate 001 Status

**Date**: 2025-03-08

## Status: ✅ MECHANISM SUCCESS - FROZEN

### Success Criteria (Mechanism Layer)

| Criterion | Result | Status |
|-----------|--------|--------|
| Coherence gain vs OFF | +16.6% | ✅ PASS |
| Prediction gain vs OFF | +24.6% | ✅ PASS |
| 32-bit bandwidth | 4 bytes | ✅ PASS |
| 10x timescale | Enforced | ✅ PASS |
| Generic-only | No action IDs | ✅ PASS |
| No action leakage | Verified | ✅ PASS |
| p=0.01, α=0.5 | Locked | ✅ PASS |

### Frozen Configuration

```rust
// FROZEN - DO NOT MODIFY without Phase 8 validation
pub const CANDIDATE_001_FROZEN: bool = true;
pub const MARKER_SIZE_BYTES: usize = 4;        // 32 bits
pub const MARKER_UPDATE_INTERVAL: usize = 10;  // 10x
pub const PRIOR_SAMPLE_PROB: f64 = 0.01;
pub const PRIOR_STRENGTH: f64 = 0.5;
pub const POLICY_COUPLING_BIAS: f32 = 0.8;     // Validated
```

### Mainline Default

Candidate 001 is the **default prior carrier** for PriorChannel mainline.

```rust
use atlas_hec_v2::prior_channel::MainlinePriorChannel;
let pc = MainlinePriorChannel::new(); // Uses Candidate 001
```

---

## Layer Separation

### ✅ Mechanism Layer (THIS FILE) - FROZEN
- Provides: coherence, prediction signals
- Status: SUCCESS, validated, frozen
- Do not modify

### ⚠️ Strategy Layer (separate track) - ACTIVE
- Goal: Convert signals to task performance
- Location: `strategy_layer_v1/`
- Status: Continues as independent optimization

---

## Validation Results

### Mechanism Validation
```
Coherence:  0.584 (ON) vs 0.501 (OFF) = +16.6% ✅
Prediction: 0.618 (ON) vs 0.496 (OFF) = +24.6% ✅
```

### Task Performance (Strategy Layer Concern)
```
Chicken: ON (-9525) > OFF (-15454) ✅ Large improvement
Stag:    ON (5546)  > OFF (5497)   ✅ Modest improvement
PD:      ON (5270)  < OFF (5340)   ⚠️  Needs strategy work
```

---

## Conclusion

**Candidate 001 is mechanism-successful.**

It reliably provides:
- Higher behavioral coherence
- Better partner prediction
- Within all FROZEN_STATE_v1 constraints

**Task performance is a separate concern** handled by Strategy Layer v1.

---

*Candidate 001: Multi-Agent Consistency Markers - Mechanism Validated & Frozen*
