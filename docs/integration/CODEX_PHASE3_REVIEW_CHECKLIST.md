# Codex Phase 3 Review Checklist

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Purpose**: Structured review of Codex Phase 3 deliverables

---

## Pre-Review Requirements

Before starting review, verify:
- [ ] Git commit hash provided by Codex
- [ ] `status-sync.json` updated by Codex
- [ ] `open-questions.md` updated by Codex

---

## Section A: Changed Files

### A.1 Source Code Changes

| File | Expected Change | Actual | Verified? |
|------|-----------------|--------|-----------|
| `src/output/csv_logger.rs` | Add 7 required_now fields | [ ] | ☐ |
| `src/engine/world.rs` | Compute field values | [ ] | ☐ |
| `src/bin/p1_experiment.rs` | Add L3_shuffled condition | [ ] | ☐ |
| `src/memory/*.rs` | Ensure archive sampling tracked | [ ] | ☐ |

**Check**:
```bash
git diff --name-only HEAD~1
# Should show: src/output/csv_logger.rs, src/engine/world.rs, etc.
```

### A.2 Integration Files Updated

| File | Required Update | Verified? |
|------|-----------------|-----------|
| `docs/integration/status-sync.json` | Commit hash, deliverables | ☐ |
| `docs/integration/open-questions.md` | B1, B2 status | ☐ |

---

## Section B: Runnable Commands

### B.1 Build Command

```bash
cd bioworld_mvp
cargo build --release
```

- [ ] Builds without errors
- [ ] Builds without warnings (or warnings documented)

### B.2 Quick Test Command

```bash
./target/release/p1_experiment \
  --group CTRL \
  --seed 999 \
  --ticks 100 \
  --universes 1 \
  --output-dir quick_test
```

- [ ] Runs without panic
- [ ] Completes in < 30 seconds
- [ ] Exit code 0

### B.3 Column Verification Command

```bash
head -1 quick_test/seed_999/u0/population.csv | tr ',' '\n'
```

**Expected output contains**:
- [ ] archive_sample_attempts
- [ ] archive_sample_successes
- [ ] archive_influenced_births
- [ ] lineage_diversity
- [ ] top1_lineage_share
- [ ] strategy_entropy
- [ ] collapse_event_count

### B.4 Sentinel Conditions Commands

For each condition:

| Condition | Command | Runs? | Output Different? |
|-----------|---------|-------|-------------------|
| baseline_full | `./p1_experiment --group CTRL ...` | ☐ | ☐ |
| no_L2 | `./p1_experiment --group P1A ...` | ☐ | ☐ |
| L3_off | `--disable-archive` or similar | ☐ | ☐ |
| L3_real_p001 | Same as baseline | ☐ | Reference |
| L3_shuffled_p001 | `--archive-shuffled` or similar | ☐ | ☐ |

---

## Section C: Generated CSV Files

### C.1 File Count

Expected: 120 CSV files (5 conditions × 3 seeds × 8 universes)

```bash
find outputs -name "population.csv" | wc -l
```

- [ ] Count = 120
- [ ] Count >= 108 (90% completion)
- [ ] Count < 108 → NO-GO

### C.2 Per-File Validation

Run on sample of files:

```bash
python3 validate_csv_fields.py outputs/baseline_full/seed_1001/u0/population.csv
```

| File | Errors | Warnings | Status |
|------|--------|----------|--------|
| baseline_full/seed_1001/u0 | 0 | [ ] | ☐ PASS ☐ FAIL |
| no_L2/seed_1001/u0 | 0 | [ ] | ☐ PASS ☐ FAIL |
| L3_shuffled/seed_1001/u0 | 0 | [ ] | ☐ PASS ☐ FAIL |

**Status Key**:
- PASS: No errors
- FAIL: Any error

---

## Section D: Sentinel Conditions Evidence

### D.1 Condition Runnability

| Condition | Exit Code 0? | Output Generated? | Duration Reasonable? |
|-----------|--------------|-------------------|---------------------|
| baseline_full | ☐ | ☐ | ☐ |
| no_L2 | ☐ | ☐ | ☐ |
| L3_off | ☐ | ☐ | ☐ |
| L3_real_p001 | ☐ | ☐ | ☐ |
| L3_shuffled_p001 | ☐ | ☐ | ☐ |

### D.2 Output Differentiation

Check that conditions produce different outputs:

```bash
# Compare endpoint populations
for condition in baseline_full no_L2 L3_off L3_shuffled_p001; do
  tail -1 outputs/${condition}/seed_1001/u0/population.csv | cut -d',' -f2
done
```

- [ ] Values differ across conditions
- [ ] baseline ≠ no_L2 (critical)
- [ ] L3_real ≈ L3_shuffled (expected)

### D.3 Archive Activity Check

Verify archive fields have activity:

```bash
awk -F',' 'NR>100 && NR<200 {sum+=$9} END {print sum}' \
  outputs/baseline_full/seed_1001/u0/population.csv
```

- [ ] Sum > 0 (archive_sample_attempts increasing)

---

## Section E: Anti-God-Mode Evidence

### E.1 Direct Access Check

```bash
grep -r "cell.*archive.*direct" src/ || echo "OK: No direct access"
grep -r "archive.*inject" src/ || echo "OK: No injection"
grep -r "global.*teacher" src/ || echo "OK: No global teacher"
```

- [ ] No forbidden patterns found
- [ ] Any findings documented and justified

### E.2 Sampling Rate Check

Verify p=0.01 enforced:

```python
df = pd.read_csv('outputs/baseline_full/seed_1001/u0/population.csv')
late = df[df['tick'] > 100]
rate = late['archive_sample_successes'].sum() / late['archive_sample_attempts'].sum()
# Should be ~0.01
```

- [ ] 0.005 < rate < 0.02

### E.3 AccessGuard Verification

Check code still has:

```rust
// In access_guard.rs
(Accessor::Cell(_), Target::Archive, _) => Err(AccessError::Forbidden)
```

- [ ] Forbidden pattern present

---

## Section F: Unresolved Blockers

### F.1 Blocker Status

From Codex's `open-questions.md`:

| Blocker ID | Description | Status | Resolved? |
|------------|-------------|--------|-----------|
| B1 | Missing CSV fields | [Status] | ☐ |
| B2 | Anti-God-Mode verification | [Status] | ☐ |

### F.2 New Blockers Identified

During review, if new blockers found:

| Blocker | Description | Severity | Action |
|---------|-------------|----------|--------|
| | | ☐ Critical ☐ Minor | |

---

## Section G: GO/NO-GO Assessment

### G.1 Rule Checks

| Rule | Status | Notes |
|------|--------|-------|
| G1: All conditions runnable | ☐ GO ☐ HOLD ☐ NO-GO | |
| G2: All fields present | ☐ GO ☐ HOLD ☐ NO-GO | |
| G3: Fields have real values | ☐ GO ☐ HOLD ☐ NO-GO | |
| G4: L3 effect detectable | ☐ GO ☐ HOLD ☐ NO-GO | |
| G5: no_L2 direction correct | ☐ GO ☐ HOLD ☐ NO-GO | |

### G.2 Critical Issues

| Issue | Present? | Blocks Progress? |
|-------|----------|------------------|
| Missing required fields | ☐ Yes ☐ No | ☐ Yes ☐ No |
| All fields zero | ☐ Yes ☐ No | ☐ Yes ☐ No |
| Conditions not runnable | ☐ Yes ☐ No | ☐ Yes ☐ No |
| L3_real ≈ L3_shuffled AND no_L2 ≈ baseline | ☐ Yes ☐ No | ☐ Yes ☐ No |

### G.3 Final Verdict

**Overall Assessment**: ☐ GO ☐ HOLD ☐ NO-GO

**If GO**:
- Proceed to longer runs (5000 generations)
- Begin FIRST_COMPARISON_MATRIX fill

**If HOLD**:
- Ambiguities to resolve: [List]
- Additional data needed: [Describe]

**If NO-GO**:
- Critical issue: [Describe]
- Required fix: [Describe]
- Do not proceed until resolved

---

## Review Sign-off

| Reviewer | Date | Verdict |
|----------|------|---------|
| | | ☐ GO ☐ HOLD ☐ NO-GO |

**Comments**:

---

## Appendix: Quick Commands

```bash
# Full validation
./validate_phase3.sh outputs/

# Single file check
python3 validate_csv_fields.py outputs/CONDITION/seed_SEED/uUNIVERSE/population.csv

# Compare conditions
python3 compare_conditions.py outputs/ baseline_full no_L2 lineage_diversity

# Check anti-god-mode
grep -r "archive" src/ | grep -v "test" | grep -v "comment"
```

---

**Execute this checklist immediately upon receiving Codex Phase 3 outputs.**
