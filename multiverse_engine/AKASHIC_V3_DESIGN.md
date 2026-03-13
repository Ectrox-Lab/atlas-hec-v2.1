# Akashic Memory System v3 Design

**Version**: 3.0  
**Date**: 2026-03-12  
**Scope**: From Strong Memory Layer to Civilization Inheritance Layer

---

## One-Line Positioning

> **Akashic is not a memory warehouse. Akashic is the conversion layer: Experience → Policy → Institution → Inheritance.**

---

## V2 Foundation (Preserved)

Akashic v2 established:

| Component | Function |
|-----------|----------|
| **Hall of Fame** | Successful patterns, validated winners |
| **Graveyard** | Failed patterns, anti-patterns |
| **Statistics Layer** | Frequency, success rates, correlations |
| **Failure Modes** | Taxonomy of how things break |
| **Cross-Generation Bias** | Inheritance of validated priors |
| **Negative Knowledge** | What NOT to do |
| **Seed-Spike Risk Query** | Fragile combination detection |

**Core Principle Preserved**:
> "Akashic does not give answers. Akashic records under what conditions structures were effective."

---

## V3: Five New Core Mechanisms

### Mechanism 1: Evidence Grade System

**Problem**: All experiences treated equally → noise dominates signal

**Solution**: Every Akashic entry carries evidence grade

```yaml
evidence_grades:
  anecdotal:
    description: "Single observation, unverified"
    weight: 0.1
    promotion_requirement: "Replication x3"
    
  repeated:
    description: "Observed multiple times"
    weight: 0.3
    promotion_requirement: "Controlled test"
    
  validated:
    description: "Passed controlled validation"
    weight: 0.7
    promotion_requirement: "Institutional adoption"
    
  institutionalized:
    description: "Adopted as policy/constitution"
    weight: 0.95
    promotion_requirement: "Multi-generation survival"
    
  deprecated:
    description: "Once valid, now superseded"
    weight: 0.0
    action: "Archive to cold storage"
```

**Promotion Rules**:
- Anecdotal → Repeated: 3+ independent observations
- Repeated → Validated: Controlled experiment passes
- Validated → Institutionalized: Adopted in constitution
- Any → Deprecated: Contradicting evidence + conflict resolution

**Query Behavior**:
- Default query excludes < repeated
- Critical decisions require ≥ validated
- Constitution amendments require institutionalized

---

### Mechanism 2: Lesson → Policy → Skill → Constitution Conversion Chain

**Problem**: Experiences accumulate but don't become enforceable

**Solution**: Structured conversion pipeline

```
Experience
    │
    ▼ (extraction)
Lesson ("X caused Y in condition Z")
    │
    ▼ (abstraction + validation)
Routing Prior ("In Z-like conditions, prefer not-X")
    │
    ▼ (formalization)
Policy ("IF condition_Z THEN avoid_X")
    │
    ▼ (institutionalization)
Skill ("Implementation pattern for avoid_X")
    │
    ▼ (constitution amendment)
Constitution Rule ("Invariant: X prohibited in Z")
```

**Conversion Criteria**:

| Stage | Input | Output | Validation |
|-------|-------|--------|------------|
| Experience → Lesson | Logs, outcomes | Causal claim | Falsifiable |
| Lesson → Routing Prior | Causal claim | Preference | Predictive test |
| Prior → Policy | Preference | Rule | Compliance check |
| Policy → Skill | Rule | Implementation | Functional test |
| Skill → Constitution | Implementation | Invariant | Multi-gen survival |

**Rejection Points**:
- Cannot falsify → Remains lesson (anecdotal)
- Fails predictive test → Rejected
- Violates higher policy → Escalate
- Functional test fails → Back to policy

---

### Mechanism 3: Conflict Resolution Mechanism

**Problem**: Experiences contradict; new evidence challenges old rules

**Solution**: Explicit conflict resolution protocol

```yaml
conflict_types:
  success_vs_failure:
    description: "Same action, different outcomes"
    resolution: "Condition decomposition"
    example: "X works in A but fails in B"
    
  new_vs_old:
    description: "New evidence contradicts established rule"
    resolution: "Evidence weight comparison"
    example: "Validated finding contradicts institutional rule"
    
  local_vs_global:
    description: "Works here but not there"
    resolution: "Scope restriction"
    example: "Policy valid only for domain X"

resolution_process:
  1_detect:
    condition: "Contradiction identified"
    action: "Flag both entries, suspend policy"
    
  2_characterize:
    action: "Determine conflict type"
    output: "Classification + scope"
    
  3_evidence_weigh:
    action: "Compare evidence grades"
    rule: "Higher grade wins; equal → escalate"
    
  4_condition_decompose:
    action: "Find contextual differences"
    output: "Refined conditions distinguishing cases"
    
  5_policy_update:
    action: "Update or split policy"
    validation: "Predictive test new formulation"
    
  6_escalation:
    condition: "Cannot resolve automatically"
    action: "Escalate to governance core"
```

**Escalation Triggers**:
- Equal evidence grades, opposite conclusions
- Constitution-level conflict
- Value/goal implication
- Repeated resolution failure

---

### Mechanism 4: Generational Inheritance Bundle

**Problem**: Each generation starts from scratch

**Solution**: Exportable inheritance package

```yaml
inheritance_bundle:
  version: "v3.YYYYMMDD"
  parent_generation: "hash_of_parent"
  
  canonical_lessons:
    format: "lesson_id, lesson_statement, evidence_grade, conditions"
    count: "top N by grade and relevance"
    
  anti_patterns:
    format: "pattern_id, description, failure_modes, detection_rules"
    count: "all validated failures"
    
  routing_priors:
    format: "condition_pattern, preference_ranking, confidence"
    count: "active priors"
    
  failure_archetypes:
    format: "archetype_id, signature, root_cause, mitigation"
    count: "taxonomized failures"
    
  constitution_deltas:
    format: "amendment_id, rule_text, rationale, adoption_date"
    count: "since parent generation"
    
  negative_knowledge:
    format: "what_not_to_do, why, detection_method"
    count: "seed-spike registry + deprecated patterns"
    
  validation_manifest:
    format: "test_suite, pass_rate, coverage"
    purpose: "Verify inheritance integrity"
```

**Bundle Generation**:
- Trigger: Periodic (monthly) + Event-driven (major milestone)
- Compression: Remove ephemeral, retain institutionalized
- Validation: Self-test bundle completeness

**Bundle Consumption**:
- New generation loads bundle as initial state
- Validates against manifest
- Extends, does not replace, built-in priors

---

### Mechanism 5: Expiration / Decay / Anti-Corruption

**Problem**: Akashic becomes log graveyard, oracle of stale wisdom, or historical baggage

**Solution**: Active lifecycle management

```yaml
lifecycle_policies:
  ttl_decay:
    anecdotal: 30_days
    repeated: 90_days_without_promotion
    validated: 365_days_without_institutionalization
    institutionalized: indefinite (constitution review)
    deprecated: immediate_archive
    
  staleness_detection:
    trigger: "Policy success rate drops"
    threshold: "< 70% over 20 samples"
    action: "Flag for review, lower confidence"
    
  conflict_audit:
    frequency: weekly
    scope: "All active policies"
    action: "Detect contradictions, queue resolution"
    
  archive_compaction:
    frequency: monthly
    criteria: "Deprecated + TTL-expired + superseded"
    action: "Move to cold storage, remove from hot query"
    retention: "7 years (configurable)"
    
  corruption_prevention:
    checks:
      - "Evidence grade inflation audit"
      - "Conflict resolution bypass detection"
      - "Inheritance bundle tampering verification"
      - "Query result manipulation detection"
    frequency: continuous
    action: "Alert + escalate + audit trail"
```

**Anti-Patterns Prevented**:

| Risk | Prevention |
|------|------------|
| Log graveyard | TTL + compaction |
| Oracle of stale wisdom | Staleness detection + deprecation |
| Historical baggage | Archive + cold storage |
| Grade inflation | Audit + verification required |
| Conflict avoidance | Mandatory resolution protocol |
| Bundle corruption | Hash verification + tamper detection |

---

## Query Interface (V3)

```yaml
query_types:
  experience_lookup:
    input: "Condition description"
    output: "Relevant experiences with grades"
    filter: "Minimum grade threshold"
    sort: "Grade desc, recency desc"
    
  policy_advice:
    input: "Decision context"
    output: "Applicable policies with confidence"
    warning: "Include conflicting policies if any"
    
  failure_prediction:
    input: "Proposed action + context"
    output: "Similar failures from graveyard"
    grade_filter: "≥ validated only"
    
  inheritance_request:
    input: "Generation ID"
    output: "Complete inheritance bundle"
    validation: "Manifest verification"
    
  conflict_check:
    input: "New observation/policy"
    output: "Existing conflicts if any"
    action: "Queue resolution if found"
```

---

## Implementation Notes

### Storage Architecture

```
Hot Tier (SSD):
  - Active policies
  - Institutionalized rules
  - Recent validated findings
  - Query cache
  
Warm Tier (SSD, compressed):
  - Repeated observations
  - Archived lessons
  - Historical queries
  
Cold Tier (Object storage):
  - Deprecated entries
  - Expired anecdotes
  - Full logs
  - Old inheritance bundles
```

### Performance Targets

| Operation | Latency Target |
|-----------|----------------|
| Experience query | < 100ms |
| Policy lookup | < 50ms |
| Conflict detection | < 200ms |
| Bundle generation | < 5s |
| Bundle validation | < 1s |

---

## Success Metrics (V3)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Experience → Lesson conversion | ≥ 30% | Of significant experiences |
| Lesson → Policy conversion | ≥ 20% | Of extracted lessons |
| Policy → Constitution rate | ≥ 10% | Of validated policies |
| Conflict resolution time | < 24h | From detection to resolution |
| Stale policy detection | ≥ 90% | Of policies with degraded performance |
| Inheritance bundle integrity | 100% | Hash verification pass rate |
| Query result usefulness | ≥ 80% | User-rated relevance |

---

## Migration from V2

1. **Grade all existing entries**: Default to anecdotal, promote based on evidence
2. **Identify conflicts**: Run conflict audit on existing policies
3. **Generate first bundle**: Export current state as v2→v3 inheritance
4. **Enable mechanisms gradually**: TTL → Conflict resolution → Bundle generation
5. **Validate**: Ensure no regression in query quality

---

## Summary

Akashic v3 transforms from passive memory to active institutionalization engine:

| Aspect | V2 | V3 |
|--------|-----|-----|
| Core function | Record | Convert |
| Evidence | Undifferentiated | Graded |
| Experience | Accumulates | Institutionalizes |
| Conflict | Ignored | Resolved |
| Inheritance | None | Bundled |
| Lifecycle | Infinite | Managed |

**One Line**: Akashic v3 is the Experience → Policy → Institution → Inheritance conversion layer.

---

**Design Approved**: _______________  
**Implementation Lead**: _______________  
**Target Completion**: _______________
