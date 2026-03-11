# Strategy Layer v1

**Status**: Independent optimization track (NOT part of Candidate 001 validation)

**Goal**: Convert Candidate 001's coherence/prediction signals into task score advantages.

---

## Layer Separation

| Layer | Status | Responsibility |
|-------|--------|----------------|
| **Candidate 001** | ✅ FROZEN | Provide coherence/prediction signals |
| **Strategy v1** | ⚠️ ACTIVE | Convert signals to task performance |

---

## Current State

### Mechanism (Candidate 001) - FROZEN
- Coherence gain: +16.6%
- Prediction gain: +24.6%
- Constraints: All satisfied ✅

### Strategy v1 - ACTIVE
- Chicken: Large improvement ✅
- Stag: Modest improvement ✅
- PD: Needs work ⚠️

---

## v1 Success Gate

| Criterion | Threshold |
|-----------|-----------|
| ON score > OFF | Required |
| ON score > Baseline | Required |
| Prediction preserved | > 0 |
| Coherence preserved | >= 90% |
| Constraints | 32-bit, 10x, generic-only |

---

## Roadmap

1. **Opponent-Model-Conditioned Policy**
2. **Game-Aware Reward Shaping**
3. **Score-First Validation**

---

*Strategy Layer v1 - Active optimization on frozen Candidate 001 substrate*
