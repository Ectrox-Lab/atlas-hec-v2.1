# Terminology Compliance Check - L3/PriorChannel

**Date**: 2026-03-10  
**Status**: COMPLIANCE REVIEW  
**Scope**: All 3 TINA candidates  
**Standard**: FROZEN_STATE_v1  

---

## Compliance Rules (Hard Constraints)

### Rule 1: L3 Semantics

| Violation | Correct |
|-----------|---------|
| "Archive" | "PriorChannel" |
| "Memory layer" | "Control layer" / "Channel" |
| "Content-bearing" | "Generic prior" |
| "Historical inheritance" | "Weak regularization" |
| "Ancestral wisdom" | "Stabilization mechanism" |

### Rule 2: Bandwidth Constraint

```
L3 information flow <= 32 bits per timestep
- This is HARD LIMIT
- No exceptions for "rich content" or "compressed wisdom"
```

### Rule 3: Timescale Separation

```
L3/L0 >= 10x timescale separation
- L0: Fast (per-tick decisions)
- L3: Slow (every 10+ ticks)
- No "continuous monitoring" by L3
```

### Rule 4: Modulation Only

```
L3 can only MODULATE, not CONTROL
- Correct: "influences", "biases", "nudges"
- Wrong: "directs", "commands", "determines"
```

### Rule 5: Generic Prior Only

```
L3 provides generic prior, NOT specific content
- Correct: "weak bias", "stabilization signal"
- Wrong: "strategy", "knowledge", "lesson", "wisdom"
```

---

## Candidate 002: Soft Robot Proprioceptive Homeostasis

### Review Status: ✅ PASS (with minor notes)

| Check | Status | Notes |
|-------|--------|-------|
| Archive references | ✅ None | Uses "proprioceptive", not L3 |
| Memory language | ✅ None | "Body self-model" is local, not L3 |
| Content-bearing | ✅ None | Prediction error, not content transfer |
| Bandwidth | ✅ Compliant | Local sensors, no L3 involved |
| Timescale | ✅ N/A | Not using L3 architecture |

### Assessment

**Mechanism**: Local proprioceptive feedback loop  
**L3 Usage**: None (this is body-level, not population-level)  
**Risk**: Low - doesn't interact with L3 semantics

### Minor Note

Document mentions "self-model" but this is:
- Local to agent (body state prediction)
- Not using population-level L3/PriorChannel
- Acceptable - different level of abstraction

### Verdict

✅ **COMPLIANT** - No L3/PriorChannel references to check  
**Action**: Ready for BUILD_NOW (after general review)

---

## Candidate 001: Multi-Agent Meta-Game Identity Tokens

### Review Status: ⚠️ NEEDS REVISION

| Check | Status | Notes |
|-------|--------|-------|
| Archive references | ⚠️ Found | "token" may imply content storage |
| Memory language | ⚠️ Found | "identity memory", "token history" |
| Content-bearing | ⚠️ Risk | "fingerprint" implies content |
| Bandwidth | ⚠️ Unclear | Token information content? |
| Timescale | ⚠️ Unclear | How often is token updated? |

### Problematic Language Found

```markdown
# CURRENT (problematic):
- "identity token" carries "action history summary"
- "token history" as state variable
- "strategy fingerprint" as content
- "memory" in "cell_memory"

# ISSUE: 
Implies content-bearing, history storage, specific information transfer
```

### Required Revision

```markdown
# REVISED (compliant):
- "identity marker" (not content-bearing)
- "consistency signal" (not history)
- "behavioral bias" (not fingerprint)
- NO storage of specific actions
- NO transfer of historical content

# COMPLIANT MECHANISM:
Each agent has observable marker that:
- Is fixed or slowly changing
- Creates selection pressure for consistent behavior
- Does NOT carry specific strategy content
- Acts as generic prior for partner predictions
```

### Bandwidth Check Required

```
Token information content must be <= 32 bits:
- Allowed: ID (8 bits), consistency score (8 bits), 2-3 traits (16 bits)
- NOT allowed: Full action history, compressed strategies, "wisdom"
```

### Timescale Check Required

```
Token update frequency:
- Must be <= 1/10 of decision frequency
- If agents act every tick, token updates every 10+ ticks
- NOT allowed: Continuous token monitoring
```

### Revision Instructions

1. Replace "token" with "marker" or "signal"
2. Remove "action history" - use "consistency metric" instead
3. Remove "fingerprint" - use "bias profile" instead
4. Clarify token is NOT content storage
5. Specify bandwidth <= 32 bits
6. Specify update frequency (slow)

### Verdict

⚠️ **NEEDS REVISION** - Language implies content-bearing  
**Action**: Rewrite to emphasize generic prior mechanism, not content storage

---

## Candidate 003: Mixed-Reality Reputation Ledger

### Review Status: ❌ REJECT (semantic drift)

| Check | Status | Notes |
|-------|--------|-------|
| Archive references | ❌ Found | "ledger" implies storage |
| Memory language | ❌ Found | "reputation memory", "social self-model" |
| Content-bearing | ❌ Violation | Explicit content (reputation scores) |
| Bandwidth | ❌ Violation | Ledger content likely > 32 bits |
| Timescale | ❌ Unclear | Real-time visibility implies fast updates |

### Critical Violations

```markdown
# VIOLATION 1: Content-bearing
"reputation_ledger: Dict[agent_id, ReputationScore]"
- Explicit content storage
- Specific information transfer
- NOT generic prior

# VIOLATION 2: Real-time visibility
"Mixed-reality" implies continuous visibility
- Violates 10x timescale separation
- L3 would be monitoring continuously

# VIOLATION 3: Bandwidth
Reputation scores for N agents:
- N * score_bits >> 32 bits per timestep
- Violates hard bandwidth constraint

# VIOLATION 4: Memory language
"social self-model", "reputation memory"
- Explicit "memory" terminology
- FROZEN_STATE_v1 banned term
```

### Fundamental Problem

This candidate describes:
- **External reputation system** (what others think of you)
- **NOT internal self-model** (what you think of yourself)
- **Content transfer** (specific scores)
- **NOT generic prior** (weak bias)

The mechanism is essentially:
- Standard reputation game theory
- With visibility manipulation
- NOT PriorChannel architecture

### Why It Cannot Be Salvaged

1. Core mechanism violates "generic prior only" constraint
2. "Reputation ledger" is inherently content-bearing
3. "Mixed-reality" implies real-time monitoring (no timescale separation)
4. Social pressure ≠ internal self-model

### Recommendation

❌ **REJECT** - Cannot be made compliant with PriorChannel semantics

**Alternative paths**:
1. Merge with candidate_001 (if about identity markers)
2. Redesign as "social consistency signal" (generic, not content)
3. Abandon and focus on 001 and 002

---

## Summary

| Candidate | Status | Action |
|-----------|--------|--------|
| 002 Soft Robot | ✅ PASS | Ready for BUILD_NOW |
| 001 Multi-Agent | ⚠️ REVISE | Remove content language, specify constraints |
| 003 Reputation | ❌ REJECT | Semantic drift, cannot comply |

---

## Revised Candidate List

### BUILD_NOW (1 candidate)

1. **candidate_002** - Soft Robot Proprioceptive Homeostasis
   - No L3 interaction
   - Local feedback mechanism
   - Ready for implementation

### REVISE_FIRST (1 candidate)

2. **candidate_001** - Multi-Agent Identity Markers (revised)
   - Must remove: token history, content-bearing language
   - Must add: bandwidth limit, timescale separation
   - After revision: re-evaluate for BUILD_NOW

### REJECTED (1 candidate)

3. **candidate_003** - Mixed-Reality Reputation Ledger
   - Mechanism incompatible with PriorChannel
   - Content-bearing by design
   - Recommend: abandon or merge with 001

---

## Next Steps

1. **candidate_002**: Proceed to implementation
2. **candidate_001**: Revise per compliance rules, resubmit
3. **candidate_003**: Archive or merge with 001
4. **Update documentation**: All candidates use compliant terminology

---

**Reviewer**: Super Brain Group  
**Date**: 2026-03-10  
**Standard**: FROZEN_STATE_v1
