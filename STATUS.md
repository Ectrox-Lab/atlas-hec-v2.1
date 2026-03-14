# Atlas-HEC Project Status

**Date**: 2026-03-11  
**Repository**: https://github.com/Ectrox-Lab/atlas-hec-v2.1

---

## Executive Summary

### Research Line 0: L4 Compositional Reuse 🏁 CLOSED — PARTIAL SUCCESS

**Status**: L4-v2 archived and absorbed — lessons extracted, mainline continues  
**Final Conclusion**:
> Compositional direction corrected (reuse 0%→50%), structural leakage suppressed (0%), stable core recovered (F_P3T4M4 0%→50%); but Task-1 validator difficulty prevents full target achievement.

**Three Lessons Absorbed**:
1. Inheritance cannot be just family bias — needs mechanism/routing level
2. Mechanism bias is the right direction — reuse ↑, leakage ↓
3. Validator difficulty can mask mechanism progress — need early calibration

**Outcome**: CLOSED — PARTIAL SUCCESS. Lessons absorbed, freeze L4-v2, continue mainline.

See: `L4_V2_FINAL_REPORT.md` for detailed archive

---

### Research Line 1: Code-DNA Diffusion 🏁 CLOSED

**Status**: Phase complete - mechanism verified, task effect inconclusive  
**Final Conclusion**: 
> Gradient-based learning verified, but task-level effectiveness remains unproven under current diffusion architecture.

**Outcome**: Quality negative result - eliminated "training insufficiency" hypothesis

See: `code-diffusion/STATUS.md` for detailed archive

---

### Research Line 1.5: E-COMP-003 Core Module & Routing Map 🏁 CLOSED

**Status**: Archived — informative but non-convergent  
**Final Label**: 
> E-COMP-003：归档。提供了有效的机制层信息，但未在 Task-1 上收敛成稳定的通过率提升。

**Key Finding from B'**: Anti-leakage 0.2 ≈ 0.4 — strength is not the bottleneck  
**Four Lessons**: Mechanism bias direction ✓, Anti-leakage effective ✓, Strength not bottleneck ✓, Task-1 not for fine-tuning ✓  

**Archive**: `docs/research/E-COMP-003/E-COMP-003_FINAL_ARCHIVE.md`  

### Research Line 1.6: L4-v3 Mechanism-First Inheritance 🟡 CLOSED — PARTIAL SUCCESS

**Status**: Higher-quality partial success than L4-v2  
**Key Results**:
- Task-2 validated as clean experimental field (100% approve vs 5% on Task-1)
- Mechanism bias confirmed: reuse 40% → 45% (+5pp)
- Leakage fully suppressed: 0% across all rounds
- Control purity verified

**Achievement**: Found readable mechanism signal environment  
**Gap**: Strong reuse (45% vs 60% target) not yet established

**Final Report**: `docs/L4_V3_FINAL_REPORT.md`

### Research Line 1.A: L4 Method Family A 🏁 CLOSED — Non-Convergent

**Status**: **CLOSED** — Method family archived, goals preserved  
**Final Label**:
> L4 方法族 A：关闭。该方法族在扩大样本后不收敛，不能稳定把 inheritance 转化为复用提升。

**Archive**: `docs/L4_METHOD_FAMILY_A_ARCHIVE.md`

**What Failed**:
- Family/mechanism-level inheritance approach
- Generation bias toward "stable" configurations
- Small-sample validation (20-100 candidates)

**What Preserved (Assets for Family B)**:
- ✅ Anti-leakage as guardrail (0% leakage verified)
- ✅ Task-2 as better validation field than Task-1
- ✅ Large-sample discipline (n≥300 required)
- ✅ Small-sample signals unreliable (hard-won lesson)

**What NOT Failed (Goals Remain)**:
- Compositional reuse as objective
- Module routing as research direction  
- Self-improvement as core requirement

---

### Research Line 1.B: L4 Method Family B 🟡 **MVE EXECUTED** — Technical Issues

**Status**: **MVE COMPLETED** with partial success, verification bug encountered  
**Duration**: 7 days (completed early due to technical issues)

**What Worked**:
- ✅ 3 executable contracts defined (StrictHandoff, AdaptiveRecovery, PressureThrottle)
- ✅ Contract composition generator functional
- ✅ Generated 300 candidates/round (n=900 total)
- ✅ Task-2 integration: 100% approve rate, 94-95% completion

**What Didn't Work**:
- ⚠️ Contract verification logic has bug (shows 0% coverage despite contracts assigned)
- ⚠️ Cannot measure "reuse via contracts" metric
- ⚠️ Cannot determine if Family B > Family A

**Results** (with caveat):
| Round | Approve | Completion | Contract Usage |
|-------|---------|------------|----------------|
| A (mixed) | 100% | 94.6% | 84-94% contract assignment |
| B (full) | 100% | ~95% | 100% full stack |

**MVE Report**: `docs/FAMILY_B_MVE_REPORT.md`

**Decision Required**: 
- **Option 1**: Extend 2 days to fix verification and get actual metrics
- **Option 2**: Proceed to B.1 acknowledging partial success
- **Option 3**: Halt and fix methodology before continuing

### Research Line 2: AtlasChen Superbrain 🟢 ACTIVE

**Status**: New independent line, decoupled from Code-DNA  
**Current Phase**: Engineering validation of core mechanisms  
**Next**: Continuity Probe v1 (pending E-COMP-003 completion)

**Charter**: `docs/atlaschen_superbrain_charter.md`

---

## Research Line 2: AtlasChen Superbrain

### Phase: Core Mechanism Engineering Validation

**Allowed Conclusions**:
- ✅ Verified mechanism
- ⚠️ Unverified capability  
- ❌ Explicit boundary / blocker

**Forbidden**:
- ❌ Claiming "complete superbrain achieved"
- ❌ Local success → system-level completion

---

### Research Priorities (In Order)

| Priority | Line | Objective | Status |
|----------|------|-----------|--------|
| P1 | Line A | Identity Continuity | 🟢 Ready |
| P2 | Line B | Autobiographical Memory | ⏸️ Blocked on P1 |
| P3 | Line C | Self-Model | ⏸️ Blocked on P1 |
| P4 | Line D | System-Level Learning | ⏸️ Blocked on P1-3 |

---

### Immediate Next Step

**Continuity Probe v1**

**Research Question**: Does system maintain identity continuity across interruptions?

**Tests**:
1. Long-term goal stability
2. Preference stability
3. Self-narrative continuity
4. Behavior constraint stability

**Definition**: `docs/continuity_probe_v1.md`

**Success Threshold**: >80% probes pass

**Failure Mode**: If <50%, block all P2-P4

---

## Evidence Standards (Both Lines)

### Required
- Reproducible experiments
- Structured logs
- Pass/fail criteria
- Control/baseline
- Failed results preserved

### Forbidden as Strong Evidence
- Subjective impressions
- Single demo success
- Parameter changes alone
- Unchecked "feels smarter"
- Unlogged memory claims

---

## Decoupling Statement

**Code-DNA Diffusion** and **AtlasChen Superbrain** are **independent research lines**.

- Code-DNA conclusions **do not** transfer to Superbrain
- Superbrain **does not** inherit Code-DNA assumptions
- Each line has independent:
  - Problem definition
  - Success criteria
  - Evidence standards
  - Evaluation metrics

**Exception**: Explicit interface research only

---

## Git Index

| Path | Content |
|------|---------|
| `L4_V2_FINAL_REPORT.md` | L4-v2 archive (PARTIAL SUCCESS) |
| `superbrain/fast_genesis/generate_candidates_v2.py` | L4-v2 generator with anti-leakage |
| `superbrain/fast_genesis/task1_l4v2_evaluate.py` | Task-1 L4-v2 evaluator |
| `superbrain/fast_genesis/task1_validator_calibration.py` | Validator calibration tool |
| `code-diffusion/` | Closed research line (archive) |
| `docs/atlaschen_superbrain_charter.md` | Superbrain charter (active) |
| `docs/continuity_probe_v1.md` | Next research definition |
| `experiments/superbrain/` | Future: Continuity Probe experiments |

---

## Current Commit

L4-v2 archived: PARTIAL SUCCESS — mechanism verified, task difficulty constrained effectiveness

---

*Next update: After Continuity Probe v1 completion*
