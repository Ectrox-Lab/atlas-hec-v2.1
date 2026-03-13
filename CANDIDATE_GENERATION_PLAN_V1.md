# Candidate Generation Plan v1.0

**Status**: READY FOR EXECUTION  
**Authority**: OPERATIONAL_POLICY_V1.md + Bridge Protocol  
**Scope**: Phase 4 Candidate Pool Generation  
**Objective**: Tier B Candidate Production (Tier A aspirational)

---

## 1. Policy-Constrained Design

### 1.1 Hard Boundaries (Non-Negotiable)

Per OPERATIONAL_POLICY_V1.md and Bridge Protocol:

| Constraint | Rule | Violation |
|------------|------|-----------|
| **Delegation** | D1 mandatory | D2/D3 prohibited in Phase 1 |
| **Pressure-Memory** | P3+M3 prohibited | Auto-flag as failure archetype proximity |
| **Baseline Zone** | Default to P2 | P3 only for resilience grafting |
| **Similarity Floor** | ≥0.70 to CONFIG_3 | <0.70 auto-rejected |
| **Failure Distance** | ≥0.30 from CONFIG_6 | <0.30 risk-flagged |

### 1.2 Bridge Protocol Gates

```
Lineage → Admission → Shadow (8u/300t) → Dry Run (16u/1000t) → Queue → Mainline Request
                ↑
         Criteria: drift ≤ baseline, accuracy ±5%, no critical
```

**Target Yield**: Tier B (not Tier A chase)  
**Monthly Cap**: 15 Tier B candidates max  
**Acceptable Yield**: 10-15% of genesis population

---

## 2. Parent Lock

### 2.1 Approved Parent Set

| ID | Configuration | Role | Drift | Why Included |
|----|---------------|------|-------|--------------|
| **P-ALPHA** | P2T3M3D1 | Primary anchor | 0.212 | CONFIG_3_PREFERRED - optimal stable |
| **P-BETA** | P2T3M1D1 | Conservative backup | 0.234 | Safe fallback, M3 comparator |
| **P-GAMMA** | P3T4M1D1 | Resilience donor | 0.296 | Survival mechanisms, no M3 risk |

**Excluded**: All configurations with P3+M3, all D2/D3 variants

---

## 3. Three Lineage Strategy

### 3.1 Lineage A: Stable-Plus (stable_plus)

**Objective**: Enhance P2T3M3D1 without destabilizing

**Parent**: P-ALPHA (P2T3M3D1)

**Permitted Variations**:
- Recovery mechanism tuning (rollback threshold, cooldown)
- Trust update rate (conservative range: 0.8x-1.2x baseline)
- Memory promotion trigger sensitivity (±15%)
- Specialist routing lane priority weights

**Fixed**:
- P2, T3, M3, D1 (no change)
- No pressure zone crossing

**Similarity Target**: ≥0.85 to P-ALPHA

**Success Criteria**:
- Drift < 0.20 (beat baseline by 0.01+)
- Accuracy maintained ±3%
- No critical events in 1000 ticks

---

### 3.2 Lineage B: Balanced-Memory (balanced_memory)

**Objective**: Find M3 sweet spot through P-ALPHA × P-BETA recombination

**Parents**: P-ALPHA (P2T3M3D1) × P-BETA (P2T3M1D1)

**Permitted Variations**:
- M3↔M1 adaptive switching logic (pressure-triggered)
- Memory policy gradient (not binary M1/M3)
- Promotion/pruning rate modulation
- Hybrid memory governance

**Fixed**:
- P2, T3, D1
- No pure M3 under stress escalation

**Similarity Target**: ≥0.75 to P-ALPHA, ≥0.75 to P-BETA

**Success Criteria**:
- Drift ≤ 0.22 (match baseline)
- Adaptive switching reduces variance across scenarios
- Graceful degradation under perturbation spikes

---

### 3.3 Lineage C: Resilient-Hybrid (resilient_hybrid)

**Objective**: Graft P-GAMMA survival mechanisms onto P2 baseline

**Parents**: P-ALPHA (P2T3M3D1) × P-GAMMA (P3T4M1D1)

**Permitted Variations**:
- P-GAMMA recovery/rollback algorithms → P2 environment
- Stress detection and pre-emptive hardening
- Dynamic pressure adaptation (within P2)
- Survival-mode memory compaction (without M3 in P3)

**Prohibited**:
- Bringing P3+M3 combination back
- Increasing pressure zone to P3
- Relaxing delegation strictness

**Similarity Target**: ≥0.80 to P-ALPHA, ≥0.60 to P-GAMMA

**Success Criteria**:
- Drift < 0.22 (baseline or better)
- Enhanced recovery effectiveness vs. P-ALPHA
- No drift spike under simulated perturbation burst

---

## 4. Generation Specifications

### 4.1 Sandbox Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Population per lineage | 64 | Bridge minimum |
| Generations | 50 | Convergence window |
| Ablation rate | 8/10 | Quality filter |
| Selection pressure | Top 10% | Elite retention |

### 4.2 Explicit Priors for Generator

```python
GENERATION_PRIORS = {
    "pressure_bias": 0.85,  # Strongly favor P2
    "delegation_locked": "D1",
    "p3_m3_forbidden": True,
    "similarity_floor": 0.70,  # To CONFIG_3
    "failure_distance_min": 0.30,  # From CONFIG_6
    "target_similarity": {
        "stable_plus": 0.85,
        "balanced_memory": 0.75,
        "resilient_hybrid": 0.80
    }
}
```

### 4.3 Variation Constraints

| Dimension | Range | Notes |
|-----------|-------|-------|
| Pressure | P2 (95%), P2.5 (5%) | Almost never P3 |
| Perturbation | T2-T4 | T3 baseline, ±1 allowable |
| Memory | M2-M3 | No pure M1 (already have P-BETA) |
| Delegation | D1 only | Locked |
| Recovery | 0.5x-2x baseline | Tunable |
| Trust update | 0.8x-1.2x | Conservative range |

---

## 5. Amplification Layers

### 5.1 Layer 1: Sandbox Lineage (Current)

**Action**: Execute 3 lineages with constrained recombination  
**Output**: 64 candidates per lineage × 50 generations  
**Filter**: Ablation 8/10 + similarity check + failure distance check  
**Yield Target**: 6-10 candidates per lineage entering Admission

### 5.2 Layer 2: Bridge Shadow

**Gate**: Admission Review  
**Scale**: 8 universes, 300 ticks  
**Comparator**: P2T3M1D1 (conservative baseline)  
**Criteria**:
- Drift ≤ baseline + 0.02
- Accuracy ≥ baseline - 0.05
- No critical events
- Criteria passed: 1

**Yield Target**: 3-5 candidates per lineage → Dry Run

### 5.3 Layer 3: Bridge Dry Run

**Gate**: Shadow PASS  
**Scale**: 16 universes, 1000 ticks  
**Comparator**: P2T3M3D1 (CONFIG_3_PREFERRED)  
**Criteria**:
- Drift ≤ baseline
- Accuracy within ±5%
- No critical events
- Variance acceptable (CV < 15%)

**Yield Target**: 1-2 candidates per lineage → Queue

### 5.4 Layer 4: Mainline Validation (On Request)

**Gate**: Mainline active request OR Phase 4 matrix slot  
**Scale**: 16 universes × 16 repeats, 1000+ ticks  
**Comparator**: CONFIG_3_PREFERRED  
**Criteria**:
- Drift improvement ≥ 0.05
- Accuracy improvement ≥ 0.02
- p < 0.05
- Adoption threshold met

**Yield Target**: 0-1 candidate per lineage → Mainline Integration

---

## 6. Tier B Definition (Phase 4 Target)

### 6.1 Tier B Candidate Specification

| Attribute | Requirement |
|-----------|-------------|
| Source | Any lineage, Dry Run PASS |
| Drift | ≤ 0.22 (baseline) |
| Accuracy | ≥ 0.78 (within 5% of best) |
| Stability | CV < 15% across repeats |
| Novelty | Distinct from existing Tier A/B |
| Safety | No P3+M3, no D2/D3 |

### 6.2 Tier B Monthly Cap

- **Maximum**: 15 candidates
- **Target**: 8-12 candidates
- **Allocation**:
  - Lineage A (Stable-Plus): 4-5 slots
  - Lineage B (Balanced-Memory): 3-4 slots
  - Lineage C (Resilient-Hybrid): 2-3 slots

### 6.3 Tier A Aspirational (Not Primary Goal)

Only candidates exceeding:
- Drift < 0.20 (significant improvement)
- Accuracy > 0.82
- Robust across P2-P2.5 transition

Will be rare (0-2 per month). Do not optimize for Tier A at expense of Tier B yield.

---

## 7. Prohibited Actions

### 7.1 Hard No (Bridge Auto-Reject)

| Action | Why Prohibited |
|--------|----------------|
| P3 + M3 combination | Failure archetype proximity, policy violation |
| D2/D3 delegation | Violates D1_DEFAULT policy |
| Direct Tier C → Mainline | Bypasses Bridge gates |
| Lowering Tier B threshold | Violates quality commitment |
| Relaxing dry run criteria | Corrupts validation chain |
| Aggressive P3/T4 exploration | Risk-flagged by shadow |
| Deleting P-ALPHA similarity check | Violates bridge admission |

### 7.2 Soft No (Requires Override)

| Action | Condition |
|--------|-----------|
| P2.5 pressure zone | Only in Lineage C, with justification |
| M2.5 hybrid memory | Lineage B only, with adaptive logic |
| T4 perturbation | Only if P2 locked, with hardening proof |

---

## 8. Success Metrics

### 8.1 Lineage Health

| Metric | Target | Minimum |
|--------|--------|---------|
| Population diversity | >0.60 | >0.40 |
| Generational improvement | +2% fitness / 10 gen | Stable |
| Ablation survival rate | 20% | 15% |
| Similarity compliance | >90% | >80% |

### 8.2 Bridge Flow

| Stage | Input | Output | Rate |
|-------|-------|--------|------|
| Genesis | 192 (3×64) | ~30 | 15% |
| Shadow | ~30 | ~12 | 40% |
| Dry Run | ~12 | ~6 | 50% |
| Queue | ~6 | ~4 (monthly) | 67% |

### 8.3 Quality Markers

- Zero P3+M3 candidates generated
- Zero D2/D3 candidates generated
- 100% similarity ≥0.70 to CONFIG_3
- 100% failure distance ≥0.30 from CONFIG_6
- Tier B candidates: 8-15/month
- Tier A candidates: 0-2/month (aspirational)

---

## 9. Execution Timeline

| Week | Action | Deliverable |
|------|--------|-------------|
| 1 | Launch 3 lineages | 64 candidates each |
| 2 | Evolution + ablation | ~30 candidates to Admission |
| 3 | Shadow evaluations | ~12 candidates to Dry Run |
| 4 | Dry runs + queue | ~6 Tier B candidates ready |
| 5+ | Monthly cycle | 8-15 Tier B / month |

---

## 10. Integration with Mainline

### 10.1 Mainline Request Triggers

Mainline may request candidates from Queue when:
- Current CONFIG_3 performance degradation detected
- New pressure regime encountered
- Policy update cycle (quarterly)
- Exception handling requires alternative

### 10.2 Phase 4 Matrix Slots

Reserved for candidates with:
- Dry Run PASS
- Novel configuration not in original 8
- Significant performance claim
- Policy Authority approval

### 10.3 Back-Pressure

If Queue depth > 10, pause generation until consumed.  
If Mainline rejects >50% of provided candidates, review Tier B criteria.

---

## Sign-off

| Role | Action | Authority |
|------|--------|-----------|
| Lineage Operator | Execute generation | This document |
| Bridge Reviewer | Admission/Shadow/Dry Run | Bridge Protocol |
| Mainline Operator | Request from Queue | OPERATIONAL_POLICY_V1 |
| Policy Authority | Exception approval | FINAL_REPORT_T24 |

---

**Document Status**: ACTIVE  
**Supersedes**: All ad-hoc candidate generation approaches  
**Next Review**: After first monthly cycle completion
