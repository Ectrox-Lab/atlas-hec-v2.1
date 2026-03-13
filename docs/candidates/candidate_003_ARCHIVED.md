# Candidate 003: Mixed-Reality Reputation Ledger (ARCHIVED)

**Status**: ❌ REJECTED - Terminology Compliance Failure  
**Date**: 2026-03-10  
**Reason**: Semantic drift, incompatible with PriorChannel constraints  
**Archived by**: Super Brain Group  

---

## Rejection Summary

### Critical Violations

| Constraint | Violation | Evidence |
|------------|-----------|----------|
| Content-bearing | ❌ VIOLATION | "Reputation ledger" stores specific scores per agent |
| Bandwidth <= 32 bits | ❌ VIOLATION | Ledger content >> 32 bits (N agents × score) |
| Timescale separation | ❌ VIOLATION | "Real-time visibility" implies no separation |
| Generic prior only | ❌ VIOLATION | Specific reputation scores, not generic bias |
| Memory terminology | ❌ VIOLATION | "reputation memory", "social self-model" |

### Core Problem

This candidate describes:
- **External reputation system** (what others think)
- **Content transfer mechanism** (specific reputation scores)
- **Real-time monitoring** (no timescale separation)
- **NOT PriorChannel architecture**

The mechanism is essentially **standard reputation game theory**, not generic prior injection.

---

## Detailed Violation Analysis

### Violation 1: Content-Bearing Mechanism

```markdown
# ORIGINAL CLAIM:
"reputation_ledger: Dict[agent_id, ReputationScore]"

# PROBLEM:
- Explicit content storage per agent
- Specific numerical scores (not generic prior)
- Information content scales with N agents
- Violates "generic prior only" constraint
```

**Why It Matters**:  
Phase 5-7 proved content-bearing mechanisms don't work. This candidate assumes content transfer as core mechanism.

### Violation 2: Bandwidth Limit

```markdown
# CALCULATION:
N agents × ReputationScore bits >> 32 bits per timestep

# EXAMPLE:
10 agents × 32-bit scores = 320 bits per observation
320 bits >> 32 bit limit

# PROBLEM:
- Violates hard bandwidth constraint
- Cannot be implemented as PriorChannel
```

**Why It Matters**:  
PriorChannel bandwidth limit (32 bits) is architectural constraint, not arbitrary limit.

### Violation 3: Timescale Separation

```markdown
# ORIGINAL CLAIM:
"Mixed-reality" with "visible reputational state"

# INTERPRETATION:
- Real-time visibility of reputation changes
- No delay between action and reputation update
- Continuous monitoring by other agents

# PROBLEM:
- Violates 10x timescale separation
- L3 would need to update every tick
- Blurs L0/L3 distinction
```

**Why It Matters**:  
Timescale separation is core to three-layer control architecture. Real-time monitoring collapses layers.

### Violation 4: Memory Terminology

```markdown
# BANNED TERMS USED:
- "reputation memory"
- "social self-model"  
- "ledger" (implies storage)
- "mixed-reality" (ambiguous, implies continuous)

# VIOLATION:
FROZEN_STATE_v1 explicitly banned "memory" terminology for L3.
```

**Why It Matters**:  
Terminology shapes implementation. Using banned terms leads to wrong architecture.

---

## Why It Cannot Be Salvaged

### Option 1: Make It Generic Prior

**Attempt**: Replace reputation scores with generic consistency signal  
**Result**: Essentially becomes candidate_001 (consistency markers)  
**Verdict**: Redundant, don't need two similar candidates

### Option 2: Keep Content, Remove L3

**Attempt**: Implement as standard reputation game without PriorChannel  
**Result**: Standard game theory, not Atlas research  
**Verdict**: Out of scope

### Option 3: Reduce Bandwidth

**Attempt**: Compress reputation to 32 bits  
**Result**: Loses information, becomes generic signal anyway  
**Verdict**: Converges to candidate_001

---

## Recommendation

### Primary: REJECT

Do not pursue this candidate further. It:
- Violates core PriorChannel constraints
- Reverts to falsified content-bearing model
- Describes standard game theory, not novel mechanism

### Secondary: Merge with 001

If "social consistency" is important:
- Extend candidate_001 (consistency markers) with social dimension
- Add "observed coherence of others" to marker
- Keep within bandwidth/timescale constraints

### Tertiary: Archive for Reference

Keep this document as:
- Example of semantic drift to avoid
- Reference for what violates compliance
- Teaching material for new team members

---

## Lessons Learned

### For TINA Creative Line

1. **Watch for content-bearing language**
   - "ledger", "storage", "memory", "history"
   - These imply mechanisms we know don't work

2. **Check bandwidth implications**
   - Any "rich information" violates 32-bit limit
   - If it scales with N agents, it's not PriorChannel

3. **Verify timescale separation**
   - "Real-time", "continuous", "immediate" are red flags
   - PriorChannel must be slow (10x separation)

### For Super Brain Validation

1. **Compliance check BEFORE formalization**
   - Catches semantic drift early
   - Prevents wasted effort on wrong mechanisms

2. **Hard constraints are hard**
   - 32 bits is limit, not suggestion
   - Content-bearing is banned, not discouraged

3. **Some ideas must be rejected**
   - Not all creative outputs can be made compliant
   - Better to reject early than compromise constraints

---

## Related Documents

- `TERM_COMPLIANCE_CHECK.md` - Full compliance review
- `FROZEN_STATE_v1.md` - Constraints this violated
- `candidate_001_intake.md` - Alternative that is compliant
- `PRIOR_CHANNEL_REFACTOR_SPEC.md` - Correct architecture

---

**Status**: ARCHIVED (not deleted, for reference)  
**Archived Date**: 2026-03-10  
**Reason**: Terminology compliance failure  
**Recommended Action**: Focus on candidates 001 and 002
