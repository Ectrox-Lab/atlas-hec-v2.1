# Phase 4 Field Fix Request

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Status**: CONDITIONAL_TEMPLATE - Only if Phase 4 = HOLD

---

## Activation Condition

**This document is ONLY valid if Phase 4 Triage = HOLD**

If Phase 4 = GO or NO-GO, ignore this document.

---

## Request to Codex

**From**: Atlas-HEC Result Triage Lead  
**To**: Codex (Bio-World maintainer)  
**Priority**: HIGH  
**Deadline**: 48 hours from request

**Context**: Phase 4 triage identified specific issues that prevent GO classification. This request specifies minimal fixes needed.

---

## Issues Identified (TO BE FILLED)

### Issue 1: [FIELD_NAME]

**Problem**: [FILL - e.g., "Field is constant at 0 after generation 100"]

**Evidence**:
```
From outputs/baseline_full/seed_1001/u0/population.csv:
Generation 100-150: archive_sample_attempts = 0
Expected: Should increase as cells attempt archive access
```

**Required Fix**: [FILL - specific implementation guidance]

**Acceptance Criteria**:
- [ ] Field shows variation (std > 0.1)
- [ ] Values in valid range
- [ ] Non-zero after generation 100

---

### Issue 2: [CONDITION_NAME]

**Problem**: [FILL - e.g., "no_L2 condition fails with exit code 1"]

**Evidence**:
```
$ ./p1_experiment --group no_L2 --ticks 100
Exit code: 1
Error: [FILL]
```

**Required Fix**: [FILL]

**Acceptance Criteria**:
- [ ] Condition runs with exit code 0
- [ ] Produces CSV output
- [ ] Output different from baseline

---

### Issue 3: [OTHER_ISSUE]

**Problem**: [FILL]

**Evidence**: [FILL]

**Required Fix**: [FILL]

**Acceptance Criteria**: [FILL]

---

## Minimal Fix List

### Required Fixes (Must Have)

| # | Item | Severity | ETA |
|---|------|----------|-----|
| 1 | [FILL] | ☐ Critical ☐ High | [FILL] |
| 2 | [FILL] | ☐ Critical ☐ High | [FILL] |
| 3 | [FILL] | ☐ Critical ☐ High | [FILL] |

### Optional Fixes (Nice to Have)

| # | Item | Severity |
|---|------|----------|
| 1 | [FILL] | ☐ Medium ☐ Low |

---

## Verification Commands

After fixes, Codex must verify:

```bash
# 1. Build
 cargo build --release

# 2. Quick test (100 generations)
 ./target/release/p1_experiment \
   --group CTRL \
   --seed 999 \
   --ticks 100 \
   --universes 2 \
   --output-dir fix_test

# 3. Check fields
 head -1 fix_test/seed_999/u0/population.csv | grep [FIELD]

# 4. Validate values
 python3 validate_csv_fields.py fix_test/seed_999/u0/population.csv
```

All checks must pass before submitting to Atlas-HEC.

---

## Evidence Gap (TO BE FILLED)

**What We Cannot Validate Without Fix**:

| Gap | Impact | Unblocks |
|-----|--------|----------|
| [FILL] | [FILL] | [FILL] |

---

## Hold Lift Conditions

Hold will be lifted when:

- [ ] All required fixes implemented
- [ ] Verification commands pass
- [ ] Quick test (200 gens) shows improvement
- [ ] Atlas-HEC reviews and approves

---

## What Happens If Not Fixed

If fixes not received within 48 hours:
1. HOLD continues
2. Cannot proceed to Phase 5
3. May escalate to NO-GO if blockers critical

---

## Contact

Questions about this request: [Atlas-HEC contact]

---

**Status**: CONDITIONAL - Activate only if Phase 4 = HOLD  
**Last Updated**: 2026-03-09
