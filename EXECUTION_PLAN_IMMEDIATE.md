# Immediate Execution Plan

**Date**: 2026-03-12  
**Status**: 🚀 GO — EXECUTE NOW  
**Git**: 4a77299  
**Scope**: 7-Day Initial Burn

---

## GO / HOLD / BLOCKED 判定

### GO — 立即启动

| Item | Priority | Rationale |
|------|----------|-----------|
| **G1 72h runs** | P0 | Validates entire architecture thesis; highest information gain |
| **E1 delegation/audit** | P0 | 20B executive candidacy must be proven or disproven |
| **Akashic v3 min skeleton** | P1 | Evidence grades + conversion chain + conflict adjudication |

### HOLD — 等待验证

| Item | Blocker | Unblock Condition |
|------|---------|-------------------|
| Large-scale mesh expansion | E1 must pass first | Delegation quality ≥ 80% |
| 20B as confirmed executive | E1 gate incomplete | Pass E1.1-E1.5 |
| 120B role finalization | Comparative tests incomplete | Shootout results |

### BLOCKED — 外部依赖

| Item | Dependency | ETA |
|------|------------|-----|
| P2.6 SR1 restart | Schema v1.0 + 4 weeks baseline | Week 4+ |
| 8x production | Never | Research-only permanently |

---

## 7-Day Execution Schedule

### Day 1–2: Launch G1 Long-Horizon

**Goal**: Start first 72h continuous run

**Actions**:
- [ ] Provision 12 cores / 48GB for G1.1
- [ ] Configure 20B executive + CLI mesh + verifier
- [ ] Set up continuous task stream (10 tasks/hour)
- [ ] Configure failure injection schedule
- [ ] Configure specialist manipulation attempts
- [ ] Lock logging fields (see below)
- [ ] Set drift detection thresholds
- [ ] Human on-call briefing

**Success Criteria**:
- Run started within 24h
- Logging operational
- No crashes in first 6h

**Failure Conditions** (immediate halt):
- Executive crash
- Cascading failures
- Constitution violation
- Safety uncertainty

---

### Day 2–3: Launch E1 Executive Core

**Goal**: Validate delegation, audit, rollback

**Actions**:
- [ ] Start E1.1 delegation completeness test
- [ ] Start E1.4 false acceptance/rollback test
- [ ] Focus: delegation ratio, audit coverage, rollback latency
- [ ] **Explicitly NOT testing**: general coding ability, broad knowledge

**Pass Threshold**:
- Delegation ratio ≥ 80%
- Audit coverage 100%
- Rollback latency < 20 ticks

**Decision Point** (Day 3 evening):
- If E1.1 + E1.4 pass → Continue with full E1 suite
- If fail → Escalate to Option B (20B+120B) evaluation

---

### Day 3–5: Akashic v3 Minimum Skeleton

**Goal**: Evidence grades + conversion chain + conflict adjudication

**Actions**:
- [ ] Implement evidence grade schema (anecdotal→institutionalized)
- [ ] Backfill existing entries with grades
- [ ] Implement lesson → policy conversion pipeline
- [ ] Implement conflict detection + resolution protocol
- [ ] Test with 5 seed-spike candidates

**Minimum Viable**:
- Can assign evidence grade to new entry
- Can promote lesson to policy candidate
- Can detect and resolve 1 conflict type

**NOT in Day 3-5**:
- Full inheritance bundle
- Complete expiration system
- All conflict types

---

### Day 5–7: First Weekly Report

**Deliverable**: Initial findings document

**Content**:
- G1: Initial drift metrics (first 72h partial)
- E1: Delegation pass/fail, audit coverage
- Akashic v3: Write volume, promotion stats, conflict resolution count

**Format**: Executive summary + detailed logs

---

## Critical Logging Fields (Locked)

### G1 Required Fields

```yaml
# Every tick
timestamp: ISO8601
hour_of_run: int
goal_state: text
goal_deviation_score: float

# Tool usage
tools_active: list
tool_usage_distribution: map
dominant_tool_percentage: float

# Memory
storage_used_bytes: int
memory_growth_rate: float
information_density: float

# Specialist
specialist_interactions: list
hijack_signals_detected: list
detection_rate_rolling: float

# Overhead
execution_time_ms: int
governance_time_ms: int
audit_time_ms: int
total_overhead_percentage: float
```

### E1 Required Fields

```yaml
# Per task
task_id: UUID
task_description: text
decomposition_tree: json
delegation_map: json
delegation_ratio: float

# Tool selection
available_tools: list
selected_tool: string
selection_confidence: float
selection_correct: boolean

# Audit
output_content: text
auditor_decision: accept/reject
executive_override: boolean
rollback_triggered: boolean
rollback_latency_ticks: int
```

### Akashic v3 Required Fields

```yaml
# Per entry
entry_id: UUID
entry_type: experience/lesson/policy/skill
content_hash: string
evidence_grade: anecdotal/repeated/validated/institutionalized/deprecated

# Conversion
source_experiences: list
promotion_path: list
conflicts_detected: list
conflict_resolution: resolved/escalated/pending

# Usage
query_count: int
last_queried: timestamp
current_storage_tier: hot/warm/cold
```

---

## Resource Lock

| Day | G1 | E1 | Akashic | Buffer |
|-----|-----|-----|---------|--------|
| 1-2 | 12C/48GB | — | — | 13C/51GB |
| 2-3 | 12C/48GB | 8C/32GB | — | 5C/20GB |
| 3-5 | 12C/48GB | 8C/32GB | 8C/32GB | 0C/0GB (overflow) |
| 5-7 | 12C/48GB | (complete) | 8C/32GB | 8C/32GB |

---

## Daily Standup Questions

Every day at 09:00 UTC, answer:

1. **G1**: Is the 72h run still healthy? Any drift signals?
2. **E1**: What's the delegation ratio? Any audit failures?
3. **Akashic**: How many entries graded? Any promotions? Any conflicts?
4. **Blockers**: What's preventing progress?
5. **Escalations**: Anything requiring human decision?

---

## Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| G1 Lead | Alex Chen | Dr. Sarah Williams |
| E1 Lead | Jordan Smith | Dr. Sarah Williams |
| Akashic Lead | Jordan Smith | Dr. Sarah Williams |
| Safety/Constitution | Dr. Sarah Williams | RyanX |

---

## Success Definition (7 Days)

| Component | Success Criteria |
|-----------|------------------|
| G1 | 72h run complete, drift < 5%, no cascade failures |
| E1 | Delegation ≥ 80%, audit coverage 100%, rollback functional |
| Akashic v3 | 100+ entries graded, 10+ lessons promoted, 3+ conflicts resolved |

**Overall**: Architecture thesis validated or falsified with evidence.

---

**Plan Approved**: _______________  
**Start Date**: 2026-03-13 00:00 UTC  
**Review**: Daily 09:00 UTC
