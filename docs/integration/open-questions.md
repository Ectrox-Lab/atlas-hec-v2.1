# Atlas-BioWorld Integration Open Questions

**Last Updated**: 2026-03-09  
**Status**: Active - Pending Resolution

---

## Q1: Metrics Export Format

**Question**: Should Bio-World export metrics as:
- A) CSV append (current, simple)
- B) JSONL stream (structured, easier parsing)
- C) Both (flexibility, more maintenance)

**Context**: Current CSV format requires parsing and type inference. JSONL would enable direct structured consumption.

**Proposed Answer**: Start with CSV enhancement, migrate to JSONL in v0.2.0

**Owner**: Bio-World team
**Priority**: High
**Status**: Awaiting decision

---

## Q2: Archive Exposure Measurement

**Question**: How to measure `archive_exposure_gain` without violating anti-god-mode?

**Options**:
1. Track archive read frequency per lineage
2. Compare lineage behavior with/without archive access
3. Analyze information-theoretic content of sampled lessons

**Concern**: Measurement itself might create observer effect

**Owner**: Atlas-HEC team  
**Priority**: High
**Status**: Needs experiment design

---

## Q3: Lineage Diversity Metric

**Question**: How to define `lineage_diversity` robustly?

**Options**:
- Count unique lineage_id values
- Shannon entropy of lineage size distribution
- Effective number of lineages (Hill number)

**Concern**: Simple count may not capture structural diversity

**Proposed Answer**: Use effective number with q=1 (Shannon-equivalent)

**Owner**: Both teams
**Priority**: Medium
**Status**: Pending implementation

---

## Q4: ContinuityProbe Access Level

**Question**: What level of archive access should ContinuityProbe have?

**Options**:
1. Full read access (complete audit capability)
2. Sampled read (p=0.01, same as cells)
3. Summary statistics only (aggregated data)

**Concern**: Full access might create information asymmetry

**Proposed Answer**: Start with summary statistics, escalate to sampled read if needed

**Owner**: Atlas-HEC team
**Priority**: Medium
**Status**: Design phase

---

## Q5: Falsification Experiment Priorities

**Question**: Which falsification experiment should run first?

**Options**:
1. P1-C Boss Pressure (environmental stress → structural response)
2. Archive Over-Reliance (increased sampling → reduced adaptation)
3. Memory KO (no inheritance → survival impact)

**Context**: P1-C already shows promising results in Phase 1

**Proposed Answer**: Complete P1-C Phase 2 first, then archive over-reliance

**Owner**: Both teams
**Priority**: High
**Status**: Awaiting resource allocation

---

## Resolution Tracking

| ID | Question | Status | Owner | Target Date |
|----|----------|--------|-------|-------------|
| Q1 | Metrics Export Format | Open | Bio-World | 2026-03-12 |
| Q2 | Archive Exposure Measurement | Open | Atlas-HEC | 2026-03-16 |
| Q3 | Lineage Diversity Metric | Open | Both | 2026-03-14 |
| Q4 | ContinuityProbe Access | Open | Atlas-HEC | 2026-03-13 |
| Q5 | Falsification Priorities | Open | Both | 2026-03-11 |

---

## How to Add New Questions

1. Use Q{N} format for ID
2. Include: Question, Context, Options, Concern, Proposed Answer
3. Assign Owner and Priority
4. Update resolution tracking table

---

## Question Resolution Process

1. **Open**: Question identified, no consensus
2. **Under Discussion**: Active conversation
3. **Decision Made**: Consensus reached
4. **Implemented**: Code/docs updated
5. **Closed**: Verified in production

---

**Next Review**: 2026-03-12
