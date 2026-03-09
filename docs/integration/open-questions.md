# Atlas-BioWorld Integration Open Questions

**Last Updated**: 2026-03-09  
**Status**: Active - Pending Resolution

---

## Blockers

Questions that prevent progress. Must resolve before next phase.

### B1: Runnability (Phase 3 Critical)

**Category**: runnable  
**Question**: Can all 5 sentinel conditions (baseline_full, no_L2, L3_off, L3_real_p001, L3_shuffled_p001) actually execute without error?

**Impact**: If any condition fails to run, we cannot perform falsification comparison.

**Owner**: Bio-World / Codex

**ETA**: 2026-03-12

**Status**: Open

**Resolution Criteria**:
- [ ] All 5 conditions run with exit code 0
- [ ] All produce CSV output
- [ ] Execution time < 5 minutes per condition (100-gen test)

---

### B2: CSV Field Semantics (Phase 3 Critical)

**Category**: semantic  
**Question**: Do the 7 required_now fields contain real computed values or placeholders?

**Impact**: Placeholder data makes falsification impossible.

**Owner**: Bio-World / Codex (implementation) + Atlas-HEC (verification)

**ETA**: 2026-03-12

**Status**: Open

**Resolution Criteria**:
- [ ] archive_sample_attempts > 0 after gen 100
- [ ] lineage_diversity varies (std > 0.1)
- [ ] top1_lineage_share in [0,1]
- [ ] No fields constant at 0

---

### B3: Shuffled Control Validity (Phase 3 Critical)

**Category**: evidence  
**Question**: Does L3_shuffled_p001 condition actually use shuffled archive content, or is it identical to L3_real_p001?

**Impact**: If not actually shuffled, falsification R1 is invalid.

**Owner**: Bio-World / Codex

**ETA**: 2026-03-13

**Status**: Open

**Resolution Criteria**:
- [ ] L3_shuffled code path exists
- [ ] Archive content randomized
- [ ] MD5 of archive different from L3_real

---

### B4: Anti-God-Mode Evidence Strength (Phase 3)

**Category**: evidence  
**Question**: Is the evidence for anti-god-mode preservation strong enough to proceed?

**Impact**: If boundaries violated, all results suspect.

**Owner**: Atlas-HEC (audit)

**ETA**: 2026-03-13

**Status**: Open

**Resolution Criteria**:
- [ ] hidden-oracle-auditor finds 0 violations
- [ ] No new Cell→Archive patterns
- [ ] Sampling rate = 0.01 ± 0.005

---

## Semantic Mismatch

Questions about interpretation differences between repos.

### S1: lineage_diversity Definition

**Atlas Interpretation**: Count of unique lineage_id values in current generation.

**Bio-World Interpretation**: May include historical lineages no longer present.

**Mismatch**: If Bio-World counts historical, trends will differ from Atlas calculations.

**Proposed Resolution**: 
- Use only currently alive cells
- Document clearly in contract
- Add `lineage_count` (historical) vs `lineage_diversity` (current) distinction

**Status**: Under Discussion

---

### S2: collapse_event_count Window Size

**Atlas Interpretation**: Rolling count over last 100 generations.

**Bio-World Interpretation**: Total count since simulation start.

**Mismatch**: If Bio-World uses total, we cannot detect recent trend changes.

**Proposed Resolution**: 
- Use rolling window of 100 generations
- Or provide both: `collapse_event_total` and `collapse_event_window`

**Status**: Under Discussion

---

### S3: strategy_entropy Granularity

**Atlas Interpretation**: Entropy over `preferred_strategy` enum values (cooperate/explore/balanced).

**Bio-World Interpretation**: May use continuous strategy space.

**Mismatch**: Different calculation methods yield incomparable results.

**Proposed Resolution**:
- Standardize on enum-based calculation
- Use 3 categories: cooperate, explore, balanced
- Document exact formula

**Status**: Under Discussion

---

## Next-Phase Proposals

Questions about future enhancements, not blocking current work.

### P1: JSONL Stream Export

**Proposal**: Add JSON Lines export option for real-time streaming.

**Value**: Lower latency, structured parsing, easier integration.

**Effort**: ~1 day implementation.

**Dependencies**: Phase 1 CSV fields must be stable first.

**Status**: Proposed for Phase 2

---

### P2: ContinuityProbe Real-time Alerts

**Proposal**: Add webhook/notification when Probe detects critical conditions.

**Value**: Immediate notification of convergence warnings.

**Effort**: ~2 days implementation.

**Dependencies**: ContinuityProbe MVP operational.

**Status**: Proposed for Phase 2

---

### P3: Cross-Seed Lineage Tracking

**Proposal**: Track lineage persistence across different random seeds.

**Value**: Distinguish robust strategies from seed-dependent luck.

**Effort**: ~3 days implementation.

**Dependencies**: Requires multiple completed runs.

**Status**: Proposed for Phase 3

---

### P4: Oracle Leak Score Computation

**Proposal**: Implement information-theoretic measurement of archive-to-cell leakage.

**Value**: Quantify anti-god-mode effectiveness.

**Effort**: ~5 days research + implementation.

**Dependencies**: Requires archive content analysis capabilities.

**Status**: Proposed for Phase 2/3

---

### P5: Drift Score for Population Divergence

**Proposal**: Measure population-level drift from baseline behavior.

**Value**: Early detection of anomalous evolution paths.

**Effort**: ~2 days implementation.

**Dependencies**: Baseline runs completed.

**Status**: Proposed for Phase 2

---

## Resolution Tracking

| ID | Category | Question | Status | Owner | Target Date |
|----|----------|----------|--------|-------|-------------|
| B1 | Blocker | Missing CSV fields | Open | Bio-World | 2026-03-12 |
| B2 | Blocker | Anti-God-Mode verification | Open | Atlas-HEC | 2026-03-13 |
| S1 | Semantic | lineage_diversity definition | Under Discussion | Both | 2026-03-14 |
| S2 | Semantic | collapse_event_count window | Under Discussion | Both | 2026-03-14 |
| S3 | Semantic | strategy_entropy granularity | Under Discussion | Both | 2026-03-14 |
| P1 | Proposal | JSONL export | Proposed | Bio-World | Phase 2 |
| P2 | Proposal | Real-time alerts | Proposed | Atlas-HEC | Phase 2 |
| P3 | Proposal | Cross-seed tracking | Proposed | Both | Phase 3 |
| P4 | Proposal | Oracle leak score | Proposed | Atlas-HEC | Phase 2/3 |
| P5 | Proposal | Drift score | Proposed | Atlas-HEC | Phase 2 |

---

## How to Update This File

1. Add new questions at the top of appropriate section
2. Use next available ID (B{N}, S{N}, or P{N})
3. Fill all fields
4. Update resolution tracking table
5. Update "Last Updated" date
6. Commit with `[atlas-sync]` or `[bioworld-sync]` tag

---

**Sync Protocol**: See `SYNC_PROTOCOL.md`
