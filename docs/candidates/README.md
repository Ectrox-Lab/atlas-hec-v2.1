# TINA Candidates - Terminology Compliance Phase

**Date**: 2026-03-10  
**Status**: COMPLIANCE REVIEW COMPLETE  
**Standard**: FROZEN_STATE_v1 (PriorChannel semantics)  

---

## Compliance Summary

| Candidate | Original Status | Compliance Review | Final Status |
|-----------|-----------------|-------------------|--------------|
| 002 Soft Robot | BUILD_NOW | ✅ PASS | **BUILD_NOW** |
| 001 Multi-Agent | BUILD_NOW | ⚠️ REVISED | **BUILD_NOW** (after revision) |
| 003 Reputation Ledger | - | ❌ REJECT | **ARCHIVED** |

**Result**: 2 candidates approved, 1 rejected  
**Standard**: All approved candidates use compliant PriorChannel terminology  

---

## Compliance Standard (FROZEN_STATE_v1)

### Hard Constraints

| Constraint | Rule | Rationale |
|------------|------|-----------|
| **Terminology** | "Archive" → "PriorChannel" | Research proven content-bearing false |
| **Bandwidth** | <= 32 bits per observation | PriorChannel hard limit |
| **Timescale** | >= 10x separation from L0 | Layer distinction requirement |
| **Mechanism** | Generic prior only | Phase 5-7 proven |
| **Content** | NONE | Content-bearing falsified |

### Banned Terms (Never Use)

| Banned | Replacement |
|--------|-------------|
| Archive | PriorChannel |
| Memory | Control / Channel |
| Content-bearing | Generic prior |
| Historical | Slow-varying |
| Inheritance | Prior injection |
| Wisdom | Regularization |
| Knowledge | Bias |

---

## Candidate 002: Soft Robot Proprioceptive Homeostasis

**Status**: ✅ **BUILD_NOW**  
**Compliance**: PASS  
**Risk**: Low  

### Why It Passes

- **No L3 interaction**: Body-level feedback, not population-level PriorChannel
- **Local mechanism**: Proprioception is agent-internal
- **No terminology violations**: Uses "body self-model" (local, not L3)
- **Compliant by absence**: Doesn't try to use PriorChannel incorrectly

### Next Step

Ready for immediate implementation.  
See: `candidate_002_intake.md`

---

## Candidate 001: Multi-Agent Consistency Markers

**Status**: ✅ **BUILD_NOW** (revised v0.2)  
**Compliance**: PASS (after revision)  
**Risk**: Medium  

### Revisions Made (v0.1 → v0.2)

| Aspect | v0.1 (Non-compliant) | v0.2 (Compliant) |
|--------|----------------------|------------------|
| Mechanism | "Identity token" with "history" | "Consistency marker" with slow coherence |
| Bandwidth | Unclear | **32 bits fixed** (8+8+16) |
| Timescale | Unclear | **10x separation** (marker updates every 10 ticks) |
| Content | "Action history summary" | **Generic coherence score** only |
| Terminology | "token", "memory", "fingerprint" | "marker", "prior", "bias" |

### Key Compliance Features

```yaml
Marker Structure (32 bits total):
  agent_id: 8 bits (fixed)
  coherence_score: 8 bits (slow update)
  behavioral_bias: 16 bits (generic prior)
  
Update Frequency: Every 10 ticks (10x slower than actions)
Mechanism: Generic prior for partner prediction (NOT specific content)
```

### Next Step

Ready for implementation.  
See: `candidate_001_intake.md` (updated v0.2)

---

## Candidate 003: Mixed-Reality Reputation Ledger

**Status**: ❌ **ARCHIVED**  
**Compliance**: FAIL  
**Reason**: Semantic drift, incompatible with PriorChannel  

### Critical Violations

| Violation | Evidence |
|-----------|----------|
| Content-bearing | "Reputation ledger" with specific scores per agent |
| Bandwidth | N agents × scores >> 32 bits |
| Timescale | "Real-time visibility" = no separation |
| Memory language | "reputation memory", "social self-model" |

### Why It Cannot Be Salvaged

1. **Core mechanism is content storage** - Proven false in Phase 5
2. **Bandwith violates hard limit** - Cannot implement as PriorChannel
3. **Describes standard reputation game** - Not novel research
4. **Converges to candidate_001 if made compliant** - Redundant

### Archive Location

See: `candidate_003_ARCHIVED.md`  
Purpose: Reference for semantic drift to avoid  

---

## Files

### Approved Candidates (BUILD_NOW)

- `candidate_002_intake.md` - Soft body proprioception
- `candidate_001_intake.md` - Multi-agent consistency markers (v0.2)

### Compliance Documentation

- `TERM_COMPLIANCE_CHECK.md` - Full compliance review for all 3 candidates
- `FROZEN_STATE_v1.md` - Frozen constraints and terminology

### Archived

- `candidate_003_ARCHIVED.md` - Rejected candidate (for reference)

---

## Next Steps

### Immediate

1. **candidate_002**: Begin implementation (Week 1-4)
2. **candidate_001**: Begin implementation (Week 1-4)
3. **Monitor**: Ensure implementation maintains compliance

### Ongoing

- All new candidates MUST pass `TERM_COMPLIANCE_CHECK` before formalization
- Creative line (TINA) outputs should be pre-filtered for banned terms
- Super Brain Group validates compliance before BUILD_NOW decision

---

## How to Check Compliance

### Quick Checklist

- [ ] No "archive", "memory", "content", "history" references
- [ ] Bandwidth explicitly stated as <= 32 bits
- [ ] Timescale separation explicitly stated as >= 10x
- [ ] Mechanism is generic prior, not specific content
- [ ] Uses "PriorChannel", "control", "generic", "prior" terminology

### Full Review

See: `TERM_COMPLIANCE_CHECK.md`

---

## Sign-off

| Role | Reviewer | Date | Status |
|------|----------|------|--------|
| Compliance Check | Super Brain Group | 2026-03-10 | Complete |
| candidate_002 | Approved | 2026-03-10 | BUILD_NOW |
| candidate_001 | Approved (revised) | 2026-03-10 | BUILD_NOW |
| candidate_003 | Rejected | 2026-03-10 | ARCHIVED |

---

**Research Phase**: COMPLETE (Phase 5-7)  
**Engineering Phase**: BEGIN  
**Approved Candidates**: 2  
**Standard**: FROZEN_STATE_v1 compliant terminology
