# Codex PR Review Template

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Purpose**: Structured review of Bio-World implementation PRs

---

## Evidence Labels

Every claim must be labeled:
- **[Verified]**: Directly observed in code/test/output
- **[Inference]**: Logical deduction from evidence
- **[Proposal]**: Suggestion, not yet validated

---

## PR Metadata

```yaml
pr_number: "#?"
branch: "?"
author: "Codex"
review_date: "2026-03-??"
reviewer: "Atlas-HEC Team"
```

---

## Review Items

### Item 1: CSV Column Additions

**Expected Behavior**:
- [Verified] All 7 required_now fields added to population.csv
- [Verified] Column names match contract exactly
- [Verified] Data types correct (u32/f32)

**Actual Behavior**:
- File changed: `bioworld_mvp/src/bio_world/output/csv_logger.rs`
- [ ] Header row contains: `archive_sample_attempts`
- [ ] Header row contains: `archive_sample_successes`
- [ ] Header row contains: `archive_influenced_births`
- [ ] Header row contains: `lineage_diversity`
- [ ] Header row contains: `top1_lineage_share`
- [ ] Header row contains: `strategy_entropy`
- [ ] Header row contains: `collapse_event_count`

**Contract Compliance**:
- [ ] Compliant - All fields present
- [ ] Partial - Some fields missing
- [ ] Non-compliant - Fields wrong or missing

**Blocker / Non-blocker**:
- [ ] BLOCKER - Cannot proceed without this
- [ ] Non-blocker - Can fix in follow-up

---

### Item 2: Data Computation Logic

**Expected Behavior**:
- [Verified] `archive_sample_attempts` increments on each sample attempt
- [Verified] `archive_sample_successes` increments only on successful retrieval
- [Verified] `lineage_diversity` = unique lineage_id count
- [Verified] `top1_lineage_share` = max lineage size / total pop
- [Verified] `strategy_entropy` = Shannon entropy over strategies
- [Verified] `collapse_event_count` = rolling window count

**Actual Behavior**:
- File changed: `bioworld_mvp/src/bio_world/engine/world.rs`
- [ ] Computation logic visible in diff
- [ ] No division by zero protection
- [ ] No negative values possible
- [ ] Values bounded correctly

**Code Review**:
```rust
// Expected pattern:
let lineage_diversity = lineage_counts.len() as u32;
let top1_lineage_share = max_count as f32 / pop.max(1) as f32;
```

**Contract Compliance**:
- [ ] Compliant - Logic correct
- [ ] Partial - Logic has issues
- [ ] Non-compliant - Wrong implementation

**Blocker / Non-blocker**:
- [ ] BLOCKER - Wrong computation
- [ ] Non-blocker - Minor optimization needed

---

### Item 3: Anti-God-Mode Preservation

**Expected Behavior**:
- [Verified] No Cell → Archive direct access added
- [Verified] No Archive → Cell policy override added
- [Verified] `ARCHIVE_SAMPLE_PROBABILITY` still 0.01
- [Verified] AccessGuard still forbids direct queries

**Actual Behavior**:
- Files changed: `*.rs`
- [ ] No new `cell.archive` direct access patterns
- [ ] No new `archive.inject(cell)` patterns
- [ ] Sampling probability not hardcoded elsewhere

**Verification Commands**:
```bash
grep -r "cell.*archive.*direct" src/ || echo "✓ No direct access"
grep -r "archive.*cell.*policy" src/ || echo "✓ No policy override"
grep -r "ARCHIVE_SAMPLE_PROBABILITY" src/ | grep -v "const"
```

**Contract Compliance**:
- [ ] Compliant - Boundaries intact
- [ ] Partial - Minor concerns
- [ ] Non-compliant - Boundaries violated

**Blocker / Non-blocker**:
- [ ] BLOCKER - God-mode introduced
- [ ] Non-blocker - Needs monitoring

---

### Item 4: Experimental Conditions

**Expected Behavior**:
- [Verified] `no_L2` condition runs (disables lineage memory)
- [Verified] `L3_off` condition runs (disables archive)
- [Verified] Each condition produces different outputs

**Actual Behavior**:
- File changed: `bioworld_mvp/src/bin/p1_experiment.rs`
- [ ] `--disable-lineage-memory` flag works
- [ ] `--disable-archive` flag works (if added)
- [ ] Outputs differ across conditions

**Test**:
```bash
# Run 2 conditions, 50 gens each
./p1_experiment --group CTRL --ticks 50 --output-dir test_ctrl
./p1_experiment --group P1A --ticks 50 --output-dir test_p1a
diff test_ctrl/seed_*/u0/population.csv test_p1a/seed_*/u0/population.csv
# Should show differences
```

**Contract Compliance**:
- [ ] Compliant - All conditions work
- [ ] Partial - Some conditions broken
- [ ] Non-compliant - No variation

**Blocker / Non-blocker**:
- [ ] BLOCKER - Cannot run experiments
- [ ] Non-blocker - Minor flag issues

---

### Item 5: status-sync.json Update

**Expected Behavior**:
- [Verified] `status-sync.json` updated with current state
- [Verified] `owned_modules` reflects Bio-World responsibilities
- [Verified] `blocking_issues` empty or documented

**Actual Behavior**:
- File changed: `docs/integration/status-sync.json`
- [ ] `repo` field = "bio-world"
- [ ] `interface_version` updated
- [ ] `owned_modules` includes new metrics

**Expected JSON**:
```json
{
  "repo": "bio-world",
  "interface_version": "v0.1.0",
  "owned_modules": [
    "l1_cell_memory",
    "l2_lineage_memory",
    "l3_causal_archive",
    "metrics_export",
    "contract_fields"
  ]
}
```

**Contract Compliance**:
- [ ] Compliant - File updated correctly
- [ ] Partial - Missing updates
- [ ] Non-compliant - Not updated

**Blocker / Non-blocker**:
- [ ] BLOCKER - Status unclear
- [ ] Non-blocker - Can update post-merge

---

### Item 6: open-questions.md Update

**Expected Behavior**:
- [Verified] Q1 (metrics format) marked resolved
- [Verified] Q3 (lineage diversity) marked resolved
- [Proposal] New questions added if discovered

**Actual Behavior**:
- File changed: `docs/integration/open-questions.md`
- [ ] Resolved questions marked
- [ ] Resolution dates added
- [ ] No unresolved blockers

**Contract Compliance**:
- [ ] Compliant - Questions tracked
- [ ] Partial - Some missing
- [ ] Non-compliant - No updates

**Blocker / Non-blocker**:
- [ ] BLOCKER - Critical questions open
- [ ] Non-blocker - Documentation issue

---

### Item 7: Performance Impact

**Expected Behavior**:
- [Verified] No >5% performance regression
- [Verified] New metrics computation overhead minimal

**Actual Behavior**:
- [ ] Benchmark before/after
- [ ] CPU overhead < 5%
- [ ] Memory overhead < 10%

**Benchmark**:
```bash
time ./p1_experiment --group CTRL --ticks 1000 --universes 8
# Compare wall-clock time
```

**Contract Compliance**:
- [ ] Compliant - Performance OK
- [ ] Partial - Minor regression
- [ ] Non-compliant - Major regression

**Blocker / Non-blocker**:
- [ ] BLOCKER - Too slow
- [ ] Non-blocker - Acceptable trade-off

---

## Summary

### Compliance Matrix

| Item | Status | Evidence | Blocker? |
|------|--------|----------|----------|
| CSV Columns | ☐ | | ☐ |
| Data Logic | ☐ | | ☐ |
| Anti-God-Mode | ☐ | | ☐ |
| Conditions | ☐ | | ☐ |
| status-sync.json | ☐ | | ☐ |
| open-questions.md | ☐ | | ☐ |
| Performance | ☐ | | ☐ |

### Final Verdict

- [ ] **APPROVE** - All critical items pass
- [ ] **CONDITIONAL** - Minor fixes needed
- [ ] **BLOCKED** - Major issues must resolve

### Required Follow-ups

1. 
2. 
3. 

### Direct Feedback for Codex

```
[Verdict]: APPROVE / CONDITIONAL / BLOCKED

[Critical Items]:
- 

[Non-critical Items]:
- 

[Next Steps]:
1. 
2. 
```

---

## Reviewer Sign-off

| Reviewer | Date | Verdict |
|----------|------|---------|
| | | |

**Atlas-HEC Team Use Only**:
- [ ] Review completed
- [ ] Blockers documented
- [ ] Follow-up tickets created
- [ ] Contract status updated
