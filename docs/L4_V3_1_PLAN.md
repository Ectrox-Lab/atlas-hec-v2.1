# L4-v3.1 Plan: Reuse Amplification

**Status**: 🟢 PLANNED  
**Parent**: L4-v3 (PARTIAL SUCCESS — Higher Quality)  
**Date**: 2026-03-14  
**Goal**: Push compositional reuse from 45% toward 55-60%

---

## Problem Statement

L4-v3 achieved:
- ✅ Clean experimental field (Task-2, 100% approve)
- ✅ Mechanism bias confirmed (+5pp reuse improvement)
- ✅ Leakage fully suppressed (0%)
- ⚠️ **Reuse rate at 45%, short of 60% target**

**Question**: How to amplify reuse signal from 45% to 55-60%?

---

## Root Cause Analysis

### Two Contributing Factors

**A. Sample Size Insufficient**
- Current: n=100 generated, n=20 evaluated
- Signal: +5pp (40% → 45%)
- May need larger sample to see amplification

**B. Package Semantics Too Coarse**
- Current: Family-level mechanism mapping
- Stable paths defined at family granularity
- May need finer-grained route motif definitions

**Assessment**: Both likely contribute. Address simultaneously.

---

## L4-v3.1 Design

### Core Principles (Keep)

| Component | Decision | Rationale |
|-----------|----------|-----------|
| Task | Task-2 | Clean field proven |
| Anti-leakage | 0.2 fixed | Verified guardrail |
| Mechanism-first | Yes | Direction confirmed |
| Control purity | A/B/Ablation | Experimental discipline |

### Key Changes (Evolve)

| Component | L4-v3 | L4-v3.1 | Rationale |
|-----------|-------|---------|-----------|
| Sample size | 100/round | **300/round** | Amplify signal |
| Eval sample | 20/round | **50/round** | Better statistics |
| Package version | 3.0 | **3.1** | Refined semantics |
| Mechanism map | Family-level | **Route motif-level** | Finer granularity |

---

## Refined Package Semantics (v3.1)

### From Family-Level to Route Motif-Level

**Current (v3.0)**:
```json
{
  "stable_families": ["F_P3T4M4", "F_P2T4M3"],
  "family_mechanism_map": {
    "F_P3T4M4": ["adaptive_migration", "trust_based_routing"]
  }
}
```

**Proposed (v3.1)**:
```json
{
  "stable_route_motifs": [
    {
      "motif_id": "high_triage_trust_handoff",
      "signature": {"triage": 4, "trust_decay": [0.05, 0.10], "delegation": 1},
      "success_rate": 0.92,
      "context": "stage_coordination"
    },
    {
      "motif_id": "adaptive_stage_recovery",
      "signature": {"memory": [3, 4], "recovery_sequence": ["detect", "isolate", "reroute"]},
      "success_rate": 0.88,
      "context": "failure_recovery"
    }
  ],
  "route_geometry": {
    "high_value_subspaces": [
      {"dimensions": ["triage", "memory"], "optimal": [4, 3], "confidence": 0.85}
    ]
  }
}
```

### Generation Bias Strategy

**Instead of**: "Pick from stable families"

**Use**: "Match candidate signature to stable route motifs"

**Implementation**:
1. Score candidate by motif match (not family membership)
2. Prefer candidates with multiple motif matches
3. Penalize candidates with no motif matches (anti-leakage)

---

## Experiment Design

### Rounds

| Round | Purpose | Sample |
|-------|---------|--------|
| **A-v3.1** | Baseline | Generate 300, evaluate 50 |
| **B-v3.1** | Refined mechanism bias | Generate 300, evaluate 50 |
| **Ablation-v3.1** | Control purity | Generate 300, evaluate 50 |

### Success Criteria

| Metric | L4-v3 Result | L4-v3.1 Target | Hard/Soft |
|--------|--------------|----------------|-----------|
| Approve rate | 100% | >90% | Soft (maintain) |
| Reuse rate | 45% | **>55%** | **Hard** |
| Leakage | 0% | <5% | Hard |
| Mechanism effect | +5pp | **+10pp** | **Hard** |

**Decision Gate**:
- **PASS**: Reuse ≥55% AND Mechanism effect ≥+10pp
- **PARTIAL**: Reuse 50-55% OR Mechanism effect +7-10pp
- **NEED REDESIGN**: Reuse <50% AND Mechanism effect <+7pp

---

## Implementation Plan

### Phase 1: Package Refinement (1 day)

**Tasks**:
1. Analyze L4-v3 winners (n=60 total) for route motifs
2. Define stable route motifs at sub-family granularity
3. Build v3.1 mechanism package
4. Update generator to use motif-level scoring

**Deliverable**: `task2_inheritance_package_v3_1.json`

### Phase 2: Large Sample Generation (1 day)

**Tasks**:
1. Generate 300 candidates per round
2. Ensure stratification by motif match score
3. Validate generation distribution

**Deliverable**: 900 candidates (300 × 3 rounds)

### Phase 3: Evaluation (2 days)

**Tasks**:
1. Evaluate 50 candidates per round on Task-2
2. Track motif-level metrics (not just family)
3. Calculate reuse by motif match, not family membership

**Deliverable**: Evaluation results with motif-level analysis

### Phase 4: Analysis & Decision (0.5 day)

**Tasks**:
1. Compare B vs A (mechanism effect magnitude)
2. Validate control purity (A vs Ablation)
3. Assess target achievement
4. Make go/no-go decision

**Deliverable**: L4-v3.1 final report

**Total Timeline**: ~4.5 days

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Motif definition wrong | Cross-validate with L4-v3 winners; keep family as fallback |
| Sample still insufficient | Can expand to n=500 if 300 shows promising but inconclusive results |
| Task-2 degradation | Monitor baseline; if completion drops below 80%, investigate |

---

## Success Scenarios

### Scenario 1: Strong Pass (60% probability)

**Results**:
- Reuse rate: 58%
- Mechanism effect: +12pp
- Approve rate: 95%

**Decision**: L4-v3.1 SUCCESS → Proceed to L4-v4 or integration with Superbrain

### Scenario 2: Partial Pass (30% probability)

**Results**:
- Reuse rate: 52%
- Mechanism effect: +8pp

**Decision**: Need one more iteration (L4-v3.2) with further refinement

### Scenario 3: Need Redesign (10% probability)

**Results**:
- Reuse rate: 47% (no improvement)
- Mechanism effect: +5pp (same as L4-v3)

**Decision**: Fundamental reassessment — perhaps 60% target is unrealistic, or mechanism inheritance needs different approach

---

## Relationship to Main Research

### Enables (If Successful)

| Downstream Line | How L4-v3.1 Helps |
|-----------------|-------------------|
| L4-v4 | Final tuning before production |
| Superbrain Integration | Proven mechanism inheritance for continuity |
| Task Generalization | Pattern for validating on new tasks |

### Depends On

| Upstream | Contribution |
|----------|--------------|
| L4-v3 | Clean field established, direction confirmed |
| E-COMP-003 | Calibration methodology |

---

## Key Metrics to Track

### Primary (Hard Targets)

| Metric | Definition | Target |
|--------|-----------|--------|
| Reuse rate | % approved candidates matching stable motifs | >55% |
| Mechanism effect | Round B reuse - Round A reuse | >+10pp |

### Secondary (Diagnostic)

| Metric | Purpose |
|--------|---------|
| Motif match score distribution | Is generator successfully biased? |
| Per-motif success rate | Which motifs are truly stable? |
| Anti-leakage penalty rate | Is filtering still appropriate? |

---

## Open Questions

1. **Motif granularity**: How fine-grained should route motifs be?
2. **Scoring function**: How to combine multiple motif matches?
3. **Target realism**: Is 60% reuse achievable, or should target be 55%?

---

## Next Steps

1. [ ] Refine v3.1 package with route motifs
2. [ ] Implement motif-level generator scoring
3. [ ] Execute large sample experiment
4. [ ] Evaluate and decide

---

**Status**: PLANNED  
**Ready to start**: Yes  
**Blocked by**: None  
**Priority**: High (continuation of active line)

---

*L4-v3.1 Plan: Reuse Amplification*  
*Building on L4-v3's cleaner signal*
