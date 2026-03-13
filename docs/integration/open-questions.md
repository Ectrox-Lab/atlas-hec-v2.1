# Atlas-BioWorld Integration Open Questions

**Last Updated**: 2026-03-09 (Phase 4.6 Update)  
**Status**: Phase 4.6 Complete - HOLD_FOR_MINIMAL_RERUN

---

## Phase 4.6 Summary

**Decision**: ☑ **HOLD_FOR_MINIMAL_RERUN**  
**Primary Blocker**: L3_shuffled missing (R1 validation)  
**Secondary Blocker**: no_L2 missing (R3 validation)  
**Strongest Evidence**: L3 effect validated (+405% adaptation gain) [Verified]

---

## Critical Blockers (Phase 4.6)

### B1: L3_shuffled Missing (CRITICAL)

**Category**: blocker  
**Question**: Is there a L3_shuffled condition to validate R1 (content relevance)?

**Status**: ❌ **MISSING** - Blocking falsification validation

**Impact**: Cannot test if archive content matters or just existence

**Owner**: Bio-World

**Resolution**:
- [ ] Run 8 universes × 5000 ticks with archive_shuffle=true
- [ ] Compare adaptation: L3_real vs L3_shuffled
- [ ] If L3_real > L3_shuffled: ✅ GO
- [ ] If L3_real ≈ L3_shuffled: ❌ NO-GO

**ETA**: 2026-03-12

---

### B2: no_L2 Missing (HIGH)

**Category**: blocker  
**Question**: Is there a no_L2 condition to validate R3 (lineage necessity)?

**Status**: ❌ **MISSING** - Weakens lineage mechanism evidence

**Impact**: Cannot prove L2 maintains diversity

**Owner**: Bio-World

**Resolution**:
- [ ] Run 8 universes × 5000 ticks with L2_enabled=false
- [ ] Compare lineage_diversity: baseline vs no_L2
- [ ] If baseline > no_L2: R3 validated

**ETA**: 2026-03-12

---

### B3: Archive Instrumentation Missing

**Category**: blocker  
**Question**: Can we measure actual archive engagement (attempts, successes)?

**Status**: ⚠️ **MISSING** - Non-blocking but limits analysis depth

**Impact**: Cannot quantify CDI engagement rates

**Owner**: Bio-World

**Resolution**:
- [ ] Add archive_sample_attempts counter to CDI
- [ ] Add archive_sample_successes counter
- [ ] Re-export CSV or regenerate

**ETA**: 2026-03-13 (lower priority)

---

## Resolved Questions (Phase 4.6)

### ✅ R1: Data Source Reconciliation

**Status**: **RESOLVED**

**Decision**: Use GitHub data exclusively, do not merge with Local

**Rationale**:
- GitHub has 19 columns vs Local 8 columns
- GitHub has critical L3_off and L3_real
- GitHub has adaptation_gain metric
- Local data incompatible (different schema, metrics)

**Document**: `PHASE46_DATA_SOURCE_RECONCILIATION.md`

---

### ✅ R2: L3 Effect Validation

**Status**: **RESOLVED - POSITIVE**

**Finding**: L3 system provides substantial benefit

**Evidence**:
- Adaptation gain: +405.5% (12.77 → 64.56) [Verified]
- Lineage count: +18.5% (38.4 → 45.5) [Verified]
- CDI: +16.3% (0.842 → 0.979) [Verified]

**Conclusion**: L3 mechanism works as hypothesized

**Document**: `PHASE46_ANALYSIS_WITH_GAPS.md`

---

### ✅ R3: Strongest Conclusions Identified

**Status**: **RESOLVED**

**Conclusion 1**: L3 system works (+405% adaptation) [Verified]  
**Conclusion 2**: System is stable (56 runs, no crashes) [Verified]

**Remaining gaps**: R1, R3 validation blocked by missing conditions

**Document**: `PHASE4_TRIAGE_REPORT.md`

---

## Remaining Open Questions

### S1: lineage_diversity Definition

**Atlas Interpretation**: 1/Σ(p²) effective number of lineages  
**Bio-World Current**: lineage_count (unique IDs only)

**Status**: Under Discussion

**Proposed Resolution**:
- Calculate lineage_diversity from existing data
- lineage_count remains as raw count
- Add both to CSV export

---

### S2: CSV Schema Finalization

**Current (GitHub)**: 19 columns  
**Required**: 15 columns minimum (Atlas contract)

**Missing from Atlas contract**:
- generation (redundant with tick)
- dna_variance
- cooperation_rate
- mean_cluster_size
- multi_cell_boss_success_rate
- energy_transfer_count
- signal_synchrony
- mutation_count
- nonzero_mutation_generations
- elite_lineage_survival
- cdi

**Status**: GitHub schema richer than required

**Decision**: ✅ Use GitHub V2 schema (19 columns)

---

### S3: Ticks Extension

**Current**: 1000 ticks  
**Minimal Rerun Spec**: 5000 ticks

**Rationale**: Better statistical power

**Status**: Approved for minimal rerun

---

## Phase 5 Preparation

### P1: Minimal Rerun Execution

**Tasks**:
1. Generate L3_shuffled (8 universes, 5000 ticks)
2. Generate no_L2 (8 universes, 5000 ticks)
3. Add archive instrumentation
4. Re-triage with complete data

**Expected Outcome**: GO decision (if L3_real > L3_shuffled)

**Timeline**: 2-3 days

**Document**: `PHASE46_RERUN_MIN_SPEC.md`

---

### P2: Phase 5 Readiness

**Current Blockers**: 2 (L3_shuffled, no_L2)  
**After Rerun**: Expected 0 blockers  
**Decision**: GO_TO_PHASE5_MINI_SCALEUP

---

## Resolution Tracking

| ID | Category | Question | Status | Owner | Target Date |
|----|----------|----------|--------|-------|-------------|
| B1 | Blocker | L3_shuffled missing | 🔴 Open | Bio-World | 2026-03-12 |
| B2 | Blocker | no_L2 missing | 🟡 Open | Bio-World | 2026-03-12 |
| B3 | Blocker | Archive instrumentation | 🟡 Open | Bio-World | 2026-03-13 |
| R1 | Resolved | Data source reconciliation | ✅ Resolved | Atlas-HEC | 2026-03-09 |
| R2 | Resolved | L3 effect validation | ✅ Resolved | Atlas-HEC | 2026-03-09 |
| R3 | Resolved | Strongest conclusions | ✅ Resolved | Atlas-HEC | 2026-03-09 |
| S1 | Semantic | lineage_diversity calc | 🟡 Discussion | Both | 2026-03-14 |
| S2 | Semantic | CSV schema | ✅ Resolved | Both | 2026-03-09 |
| S3 | Semantic | Ticks extension | ✅ Resolved | Both | 2026-03-09 |
| P1 | Phase 5 | Minimal rerun | 🟡 Planned | Bio-World | 2026-03-12 |
| P2 | Phase 5 | Phase 5 readiness | 🟡 Pending | Atlas-HEC | 2026-03-14 |

---

## Phase 4.6 Deliverables

| Document | Status | Purpose |
|----------|--------|---------|
| PHASE46_MISSING_DATA_LEDGER.md | ✅ Complete | List all missing data with blocking status |
| PHASE46_ANALYSIS_WITH_GAPS.md | ✅ Complete | What can/cannot be concluded |
| PHASE4_TRIAGE_REPORT.md | ✅ Final | Complete triage with actual data |
| PHASE4_COMPARISON_DECISION_TABLE.md | ✅ Final | Comparison matrix filled |
| PHASE46_RERUN_MIN_SPEC.md | ✅ Complete | Minimal rerun specification |
| PHASE46_DATA_SOURCE_RECONCILIATION.md | ✅ Complete | GitHub vs Local resolution |
| status-sync.json | ✅ Updated | Current status with blockers |

---

## How to Update This File

1. Add new questions at the top of appropriate section
2. Use next available ID (B{N}, S{N}, or P{N})
3. Fill all fields
4. Update resolution tracking table
5. Update "Last Updated" date
6. Commit with `[atlas-sync]` or `[bioworld-sync]` tag

---

**Current Phase**: 4.6  
**Next Phase**: 5 (pending minimal rerun)  
**Decision**: HOLD_FOR_MINIMAL_RERUN  
**Sync Protocol**: See `SYNC_PROTOCOL.md`
