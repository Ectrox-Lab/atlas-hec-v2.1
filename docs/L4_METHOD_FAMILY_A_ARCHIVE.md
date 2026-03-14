# L4 Method Family A: Archive Report

**Status**: 🏁 CLOSED — Non-Convergent  
**Date**: 2026-03-14  
**Final Label**:
> L4 方法族 A：关闭。该方法族在扩大样本后不收敛，不能稳定把 inheritance 转化为复用提升。

**English**:
> L4 Method Family A: CLOSED — non-convergent under expanded sample regime.

---

## What Is Being Archived

### Method Family A Definition

The specific methodological approach consisting of:

1. **Inheritance package**: v1/v2/v3 family/mechanism-level knowledge encoding
2. **Generation bias**: Bias toward "stable families" or "route motifs"
3. **Anti-leakage**: Penalty for structural expansion
4. **Validation**: Task-1/Task-2 validators with reuse-rate targets

### Archive Scope

| Component | Status | Note |
|-----------|--------|------|
| L4-v1 | ✅ Archived | Family-level bias, 51.6% reuse |
| L4-v2 | ✅ Archived | Mechanism-level bias, 45% reuse (unstable) |
| L4-v3.0 | ✅ Archived | 45% → 30% on expansion |
| L4-v3.1 | ✅ Archived | Failed refinement, negative effect |
| L4-v3.0-Expanded | ✅ Archived | Falsification run, 30% ceiling |

---

## What Is NOT Being Archived

### L4 Main Goals (Preserved)

The research objectives remain valid and active:

- ✅ **Compositional reuse** — modules should compose, not just accumulate
- ✅ **Module routing** — stable paths through capability space
- ✅ **Self-improvement** — system should improve through experience
- ✅ **Core capability minimalization** — "true superbrain" capability set

**These goals are NOT failed. The specific engineering approach (Method Family A) failed to achieve them.**

---

## Evidence for Closure

### Convergent Pattern Across All Attempts

| Attempt | Small Sample | Large Sample | Conclusion |
|---------|--------------|--------------|------------|
| L4-v1 | 51.6% reuse | Not tested | Directional but ceiling unclear |
| L4-v2 | 45% reuse | Not tested | Improved anti-leakage |
| L4-v3.0 | 40% → 45% (+5pp) | **30% → 30% (0%)** | **Small-sample artifact** |
| L4-v3.1 | 36% → 32% (-4pp) | N/A | Refinement made it worse |
| L4-v3.0-Exp | N/A | 30% → 30% (0%) | **Ceiling confirmed ~30%** |

### Key Falsification

**The +5pp mechanism effect in L4-v3.0 disappeared at n=300.**

This is not "weak effect" — this is "no effect under proper statistical power."

### Stable Findings (Assets)

| Finding | Stability | Value |
|---------|-----------|-------|
| Anti-leakage works | ✅ Confirmed across all runs | Guardrail asset |
| Task-1 too difficult | ✅ Confirmed | Validator calibration |
| Task-2 better field | ✅ Confirmed | Methodology asset |
| Small-sample signals unreliable | ✅ Learned | Methodology asset |
| Current package semantics wrong | ✅ Falsified | Negative knowledge |

---

## Assets Preserved for Method Family B

### 1. Anti-Leakage as Guardrail

**Status**: Verified effective (0% leakage)

**Transfer**: Use in Method Family B as default safety boundary, not optimization target.

### 2. Task Difficulty Layering

**Status**: Task-1 (too hard) < Task-2 (appropriate) hierarchy established

**Transfer**: Method Family B should use appropriate difficulty validator from start.

### 3. Large-Sample Discipline

**Status**: Learned through painful experience

**Transfer**: Method Family B must validate at n≥300 before claiming convergence.

### 4. Mechanism/Task Separation

**Status**: Learned that validator difficulty masks mechanism signals

**Transfer**: Method Family B must explicitly separate mechanism quality from task difficulty.

---

## Methodological Lessons

### Lesson 1: Small-Sample Positive Signals Are Unreliable

**Evidence**: +5pp at n=20 became 0% at n=50.

**Practice**: No claims without n≥300 validation.

### Lesson 2: Refinement Without Validation Is Dangerous

**Evidence**: v3.1 made performance worse, not just unchanged.

**Practice**: Validate baseline before any refinement.

### Lesson 3: Leakage Control ≠ Reuse Achievement

**Evidence**: 0% leakage achieved, but reuse didn't improve.

**Practice**: Separate metrics for "preventing bad" vs "achieving good."

### Lesson 4: Family/Mechanism Abstraction May Be Wrong Level

**Evidence**: Biasing toward "stable families" didn't create actual stability.

**Practice**: Question whether current abstraction captures real reusable units.

---

## What Method Family B Needs

### Required Differences from Family A

| Aspect | Family A (Failed) | Family B (Requirements) |
|--------|-------------------|------------------------|
| Inheritance target | Families/mechanisms | **TBD — must be validated** |
| Generation bias | Toward "stable" configs | **TBD — must show effect at n=300** |
| Validation | Reuse rate | **TBD — must include mechanism inspection** |
| Sample size for claims | 20-100 | **Minimum 300** |
| Refinement approach | Aggressive | **Conservative, validated** |

### Family B Must Demonstrate

Before claiming success:
1. Effect at n=300 (not just n=20)
2. Reproducibility across seeds
3. Mechanism inspectability (can see *what* is being reused)
4. Transfer to new tasks

---

## Archive Documentation

### Files Archived

```
docs/
├── L4_V1_REPORT.md                    # Family A: v1
├── L4_V2_FINAL_REPORT.md              # Family A: v2
├── L4_V3_FINAL_REPORT.md              # Family A: v3.0
├── L4_V3_1_FAILED_REFINEMENT.md       # Family A: v3.1 (failed)
├── L4_V3_0_EXPANDED_VALIDATION.md     # Family A: falsification
└── L4_METHOD_FAMILY_A_ARCHIVE.md      # This summary

data/
├── /tmp/l4v1*/                        # L4-v1 results
├── /tmp/l4v2*/                        # L4-v2 results  
├── /tmp/l4v3*/                        # L4-v3.x results
├── /tmp/l4v3_0_expanded*/             # Falsification results
└── [preserved for analysis]
```

### Code Preserved

```
superbrain/fast_genesis/
├── generate_candidates.py             # v1 generator
├── generate_candidates_v2.py          # v2/v3 generator (with anti-leakage)

superbrain/task1_simulator/            # Task-1 validator
superbrain/task2_simulator/            # Task-2 validator
superbrain/module_routing/             # Mechanism extraction tools

[All code preserved as reference, not active development]
```

---

## Relationship to Other Research Lines

### Active Lines (Unaffected)

| Line | Relationship to L4-A Closure |
|------|------------------------------|
| Superbrain | Independent; may use L4-A assets (anti-leakage) |
| Continuity | Independent; L4-A lessons on sample size apply |
| Core Capability Minimization | Goal preserved; method to be determined |

### Future Lines (Method Family B)

| Potential Line | Connection |
|----------------|------------|
| L4-B: Gradient-based composition | Different approach to same goal |
| L4-B: Explicit module interfaces | Different abstraction level |
| L4-B: Verification-driven reuse | Different validation methodology |

---

## Final Assessment

### What Failed

- Family/mechanism-level inheritance as currently implemented
- Bias generation toward predefined "stable" configurations
- Reuse rate as sufficient validation metric
- Small-sample validation discipline

### What Succeeded

- Anti-leakage as structural guardrail
- Task difficulty layering methodology
- Large-sample falsification capability
- Clear negative knowledge about current approach

### What Remains

- Compositional reuse as valid goal
- Module routing as important problem
- Self-improvement as core requirement
- Need for Method Family B

---

**Archived**: 2026-03-14  
**Method Family A**: CLOSED — Non-convergent  
**L4 Main Goals**: PRESERVED — Awaiting Method Family B  
**Next Action**: Design Method Family B with lessons from A

---

*This archive preserves the failed approach while maintaining the research goals.*  
*Method Family B will build on assets, not repeat mistakes.*
