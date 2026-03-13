# L4-v1 Final Judgment

**Date**: 2026-03-14  
**Experiment**: E-T1-003 + E-COMP-002  
**Status**: FAILED under strict compositional criterion

---

## One-Sentence Conclusion

> Current inheritance drives **exploratory expansion**, not **compositional reuse-based self-improvement**.

---

## What Worked (Established)

| Observation | Evidence |
|-------------|----------|
| **Inheritance consumed** | Round B shows different family distribution vs Round A |
| **Distribution shifted** | F_P2T4M3, F_P4T4M3 gained; F_P3T3M2, F_P2T4M2 reduced |
| **Raw throughput improved** | Round B: +5.13% vs Round A: +1.51% |
| **Ablation validated** | bias=0.0 reproduces Round A behavior |

**Interpretation**: The inheritance mechanism functions. The package is being read and biasing candidate generation.

---

## What Failed (Blockers for L4)

| Criterion | Target | Round B | Status |
|-----------|--------|---------|--------|
| **Approve rate** | > Round A +5pp | 51.6% vs 40.0% | ✅ PASS |
| **Throughput delta** | > Round A | +5.13% vs +1.51% | ✅ PASS |
| **F_P3T4M4 share** | > 25% | 9.7% | ❌ FAIL |
| **Reuse rate** | > 60% | 51.6% | ❌ FAIL |
| **New family leakage** | < 15% | 12.9% | ✅ PASS |
| **Winners from stable paths** | > 50% | 22.6% | ❌ FAIL |

**Interpretation**: Improvement came from **novel family exploration** (P1, P4, T5 families), not **reuse of stable families**.

---

## Root Cause Analysis

### Current Inheritance Package Semantics (v1)

```json
{
  "approved_families": ["F_P3T4M4", "F_P2T3M3"],
  "generator_priors": {
    "trust_decay_range": [0.05, 0.15]
  }
}
```

**Problem**: Family-level bias is too coarse-grained.

- Encourages "family-hopping" to nearby variants
- Allows structural expansion into untested regions (P4, T5)
- Does not encode *mechanism-level* reusable patterns

### Required Inheritance Package Semantics (v2)

```json
{
  "stable_mechanisms": {
    "delegation_patterns": ["adaptive_migration", "trust_based_routing"],
    "recovery_sequences": [["detect", "isolate", "redistribute"]],
    "trust_update_priors": {"decay": 0.10, "recovery": 0.05}
  },
  "blocked_motifs": ["rapid_switching", "migration_thrashing"],
  "routing_constraints": {
    "pressure_range": [2, 3],
    "triage_range": [3, 4]
  }
}
```

**Target**: Mechanism-level bias, not family-level.

---

## Two-Knife Fix (No Architecture Diffusion)

### Knife 1: Akashic Package Schema

**From**: Family-level prior (`approved_family`, `blocked_family`)  
**To**: Mechanism/routing prior (`stable_patterns`, `blocked_motifs`, `route_constraints`)

**Implementation**:
- `Task1KnowledgeArchive` extracts delegation/recovery patterns, not just family IDs
- `generate_task1_inheritance_package()` outputs mechanism-level priors
- Schema version bump to v2.1

### Knife 2: Fast Genesis Anti-Leakage Bias

**Current**: `bias_toward_known_good` (family-level)  
**Add**: `anti_structural_expansion_penalty`

**Implementation**:
```python
def generation_score(candidate):
    base = similarity_to_known_good(candidate)
    penalty = 0
    
    # Penalize unjustified expansion
    if candidate.family not in KNOWN_FAMILIES:
        penalty += 0.3
    if candidate.pressure not in [2, 3]:
        penalty += 0.2
    if has_novel_motif(candidate, HISTORY):
        penalty += 0.4
    
    return base - penalty
```

**Constraint**: No new families beyond ±1 neighbor of known-good clusters.

---

## Next Steps: L4-v2

### Immediate (No Diffusion)
1. Update `Task1KnowledgeArchive` to extract mechanism patterns
2. Update `generate_task1_inheritance_package()` to output v2 schema
3. Add `anti_leakage_bias` to `generate_candidates.py`

### Experiment (A/B Structure Preserved)
- Round A-v2: No inheritance (same as v1)
- Round B-v2: Inheritance package v2 + anti-leakage
- Success criteria unchanged

### Success Definition (L4-v2)
| Metric | Threshold |
|--------|-----------|
| Approve rate B > A | +5pp |
| Reuse rate | > 60% |
| Leakage | < 10% |
| F_P3T4M4 share | > 25% |
| Winners from stable paths | > 50% |

---

## State Update

**L4-v1**: FAILED under strict compositional criterion  
**Signal**: Inheritance mechanism works, drives exploration  
**Gap**: Does not drive compositional reuse  
**Next**: L4-v2 with mechanism-level inheritance + anti-leakage

---

*Atlas-HEC Research Committee*  
*2026-03-14*
