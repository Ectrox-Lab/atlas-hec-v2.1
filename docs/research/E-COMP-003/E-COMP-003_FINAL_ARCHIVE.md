# E-COMP-003 Final Archive

**Status**: 🏁 CLOSED — Informative but Non-Convergent  
**Date**: 2026-03-14  
**Final Label**: 
> E-COMP-003：归档。提供了有效的机制层信息，但未在 Task-1 上收敛成稳定的通过率提升。

---

## Executive Summary

E-COMP-003 completed its mission: **identify why L4-v2 underperforms**.

**Answer**: Not anti-leakage strength. The bottleneck is elsewhere (likely Task-1 difficulty or mechanism package semantics).

**Decision**: Archive E-COMP-003, absorb lessons, proceed to L4-v3 design.

---

## Key Findings from B' Quick Scan

### Anti-Leakage Strength Test (0.2 vs 0.4)

| Metric | Strength 0.2 | Strength 0.4 | Conclusion |
|--------|-------------|--------------|------------|
| Approve rate | 5% | 5% | No improvement |
| Reuse rate | 0% | 0% | No improvement |
| Leakage | 0% | 0% | Both effective |
| F_P3T4M4 share | 0% | 0% | No difference |

**Critical Finding**: **0.2 ≈ 0.4**

Anti-leakage strength is **not** the bottleneck.

---

## Four Lessons to Carry Forward

### Lesson 1: Mechanism Bias Direction is Correct ✅

Family distribution shifts toward target regions (T4, P3T4M4, P2T4M4) when mechanism bias is applied.

**For L4-v3**: Keep mechanism/routing-level bias. Do not revert to family-level bias.

### Lesson 2: Anti-Leakage is Effective ✅

Leakage can be suppressed to 0%.

**For L4-v3**: Keep anti-leakage as guardrail, not as primary optimization knob. Use moderate strength (0.2-0.4).

### Lesson 3: Anti-Leakage Strength is Not the Bottleneck ✅

0.2 and 0.4 perform identically.

**For L4-v3**: Stop tuning anti-leakage strength. Focus on other variables.

### Lesson 4: Task-1 is Not Suitable for Fine-Grained Mechanism Optimization ⚠️

Approve rates consistently low (3-7%) regardless of configuration.

**For L4-v3**: Task-1 better serves as high-difficulty stress validator, not as fine-tuning environment. Design L4-v3 for new task family.

---

## What Did NOT Work

| Approach | Result | Reason |
|----------|--------|--------|
| Gate-1 large sample (n=150/round) | Inconclusive | Evaluator issues + high variance |
| Phase 1 variable isolation | Incomplete | Evaluator bugs prevented clean comparison |
| B' strength scan | No signal | 0.2 ≈ 0.4, both ~5% approve |

**Root Cause**: Task-1 difficulty masks mechanism differences.

---

## Assets Preserved

### Code
```
superbrain/module_routing/mechanism_extractor.py
superbrain/module_routing/calibration_analyzer.py
run_ecomp003_*.sh (archive only)
```

### Data
```
docs/research/E-COMP-003/
├── gate1/                     # Gate-1 attempt results
├── calibration/               # Phase 1 + B' results
├── family_mechanism_map_v1.json
├── route_constraints_v1.json
├── stable_vs_leakage_pattern_table.md
└── E-COMP-003_FINAL_ARCHIVE.md (this file)
```

### Lessons
- Mechanism bias direction: ✅ validated
- Anti-leakage effectiveness: ✅ validated  
- Anti-leakage strength tuning: ❌ not useful
- Task-1 for fine-tuning: ❌ not suitable

---

## Why Archive Now (Not Earlier)

| Stage | Decision | Rationale |
|-------|----------|-----------|
| After Gate-1 | Continue | Had not tested anti-leakage strength |
| After B' | **Archive** | Answered critical question: not strength issue |
| Hypothetical Phase 2 | Skip | Would likely show same pattern (Task-1 difficulty) |

**Correct timing**: Now. Further investment in Task-1 has diminishing returns.

---

## L4-v3 Design Guidelines (From E-COMP-003)

### Carry Forward

1. **T4 / high triage preference** — as prior, not absolute rule
2. **Mechanism/routing bias** — not family-level bias
3. **Anti-leakage as guardrail** — moderate strength, not optimization target

### Abandon

1. **Task-1 as primary optimization environment** — too difficult/noisy
2. **Fine-grained anti-leakage tuning** — 0.2-0.4 sufficient
3. **Approve rate >60% target on Task-1** — unrealistic

### New Direction

Design L4-v3 for:
- **New task family** (Task-2 or Task-3)
- **Mechanism-resolvable environment** (clearer signal than Task-1)
- **Retain real-world semantics** (not toy environment)

---

## Research Line Status

| Line | Status | Relationship to E-COMP-003 |
|------|--------|---------------------------|
| L4-v2 | 🏁 CLOSED — PARTIAL SUCCESS | Parent line |
| **E-COMP-003** | 🏁 **CLOSED** — Informative but Non-Convergent | This archive |
| L4-v3 | 🟡 PENDING | Next line, uses E-COMP-003 lessons |

---

## Final Statement

> E-COMP-003 provided critical information: the bottleneck is not anti-leakage strength. This justifies pivoting to L4-v3 design with new task family. The investment was worthwhile; the decision to archive is correct.

---

**Archived**: 2026-03-14T09:17:34+08:00  
**Next**: L4-v3 Design  
**Status**: CLOSED — Lessons Absorbed
