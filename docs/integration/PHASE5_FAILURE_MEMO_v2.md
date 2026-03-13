# Phase 5 Failure Memorandum v2

**Date**: 2026-03-09  
**Status**: HYPOTHESIS FAILED - NO-GO  
**Classification**: Internal Alignment Document  

---

## Executive Summary

**Verdict**: ❌ NO_GO_HYPOTHESIS_FAIL  
**Failed Hypothesis**: Archive content relevance ("content-bearing memory inheritance")  
**Preserved Finding**: Archive presence effect (channel/presence/generic prior)  
**Data Quality**: Valid, sufficient, properly analyzed  

This is **not** a system failure. This is **hypothesis refinement**.

---

## Part 1: Failed Propositions (Stop Using These)

### F1: Content-Bearing Archive Hypothesis [TERMINATED]

**Original Claim**: 
> "Archive records specific historical strategies and passes them to descendants, enabling content-relevant adaptation."

**Evidence Against**:
| Metric | L3_real | L3_shuffled | δ | Cohen's d | p-value |
|--------|---------|-------------|---|-----------|---------|
| lineage_diversity | 0.007667 | 0.007803 | -1.7% | -0.129 | 0.7174 |
| top1_lineage_share | 0.616764 | 0.644962 | -4.4% | -0.147 | 0.6803 |
| strategy_entropy | 0.742670 | 0.730580 | +1.7% | +0.110 | 0.7585 |

**Threshold Violation**:
- Required: δ > +20% for GO
- Observed: δ = -1.7% (within equivalence zone -10% ≤ δ ≤ +10%)
- Conclusion: Content **irrelevant**

**Action**: 
- ❌ Stop using "content-bearing archive"
- ❌ Stop claiming "historical strategy inheritance"
- ❌ Stop narrative about "ancestral wisdom"

---

### F2: Compressed Content Utility Hypothesis [TERMINATED]

**Original Claim**:
> "Even compressed/abstracted content from archive provides lineage-relevant guidance."

**Evidence Against**:
- Shuffled archive (random content) ≈ Real archive (historical content)
- No detectable difference in any metric
- Compression does not preserve useful content semantics

**Action**:
- ❌ Stop claiming "compressed memory"
- ❌ Stop assuming "abstracted strategy patterns"

---

## Part 2: Preserved Propositions (Keep These)

### P1: Archive Presence Effect [CONFIRMED]

**Finding**:
```
L3_off < L3_real ≈ L3_shuffled

L3_off:  lineage_diversity = baseline
L3_real: lineage_diversity = +4.6% vs off
L3_shuffled: lineage_diversity = +6.4% vs off
```

**Interpretation**:
- Archive **existence** matters
- Archive **content** does not matter
- Effect is architectural, not informational

**Valid Descriptions**:
- ✅ "Low-bandwidth stabilization channel"
- ✅ "Architectural regularizer"
- ✅ "Generic prior injection mechanism"
- ✅ "Presence effect / channel effect"

**Invalid Descriptions**:
- ❌ "Memory inheritance"
- ❌ "Content transmission"
- ❌ "Historical strategy reuse"

---

### P2: L2 Lineage Tracking Necessity [CONFIRMED]

**Finding**:
| Comparison | Metric | δ | Cohen's d | p-value |
|------------|--------|---|-----------|---------|
| baseline vs no_L2 | top1_lineage_share | +28.0% | 0.992 | 0.0087 |
| baseline vs no_L2 | lineage_diversity | +5.4% | 0.473 | 0.1914 |

**Interpretation**:
- L2 maintains lineage structure
- Disabling L2 reduces dominance control
- Mechanism remains valid

**Status**: ✅ **PRESERVED** for Phase 6

---

### P3: Three-Layer Architecture Viability [PARTIALLY CONFIRMED]

**Status**:
- L1 (Intrinsic mortality): Presumed working
- L2 (Lineage tracking): ✅ Confirmed working
- L3 (Archive): ⚠️ Working as **channel**, not as **memory**

**Revision**:
```
Original: "Three-layer memory system"
Revised:  "Three-layer control system with weak archival channel"
```

---

## Part 3: Phase 6 Minimal New Hypotheses

### H1: Archive-as-Generic-Prior [PRIMARY]

**Question**: Does the archive act as a weak generic prior / regularizer, independent of specific content?

**Testable Predictions**:
1. Any low-frequency external signal (not just archive) provides similar stabilization
2. Archive effect scales with sampling probability p, not with content quality
3. Random strategies from archive ≈ Historical strategies from archive

**Already Supported**: ✅ Prediction 3 confirmed in Phase 5

**Phase 6 Test**:
- Compare L3_real vs L3_constant (archive always returns fixed strategy)
- If constant ≈ real, confirms generic prior effect

**Acceptance**: δ < 10% difference between real and constant

---

### H2: Content-Threshold Hypothesis [SECONDARY]

**Question**: Is there a content richness threshold below which content becomes irrelevant?

**Rationale**: 
- Current archive may compress too aggressively
- Content may be present but below detection/expression threshold

**Phase 6 Test**:
- Run L3_high_resolution (less compression, more bits)
- Run L3_direct (no compression, raw strategy)
- Compare to L3_real

**Acceptance**: High-res or direct shows δ > 20% vs shuffled

**Risk**: May discover that no compression level makes content matter

---

### H3: Receiver-Capacity Hypothesis [TERTIARY]

**Question**: Do newborn cells have sufficient capacity to utilize archive content?

**Rationale**:
- Current design: newborns get archive sample at birth
- Newborns may not have enough state/memory to use complex content
- Content may be there but unreadable by receiver

**Phase 6 Test**:
- Add "maturity period" before archive access allowed
- Compare mature-access vs birth-access

**Acceptance**: Mature-access shows stronger effect than birth-access

---

### H4: Sampling-Timing Hypothesis [OPTIONAL]

**Question**: Does sampling timing (not just probability) affect content utility?

**Phase 6 Test**:
- L3_stressed (sample only during stress events)
- L3_periodic (sample every N ticks vs random)

**Acceptance**: Timing-sensitive effects detected

---

## Prohibited Actions (Do Not Do These)

| Prohibition | Reason |
|-------------|--------|
| ❌ Larger-scale rerun of real vs shuffled | Already falsified, more data won't help |
| ❌ Longer duration hoping for reversal | Effect is structural, not temporal |
| ❌ More complex content encoding | Content irrelevant at any encoding |
| ❌ Narrative reframing as "partial success" | Hard falsification accepted |
| ❌ Phase 6 with original hypothesis intact | Must revise hypothesis first |

---

## Terminology Changes (Mandatory)

| Old Term | New Term | Rationale |
|----------|----------|-----------|
| "Three-layer memory" | "Three-layer control" | L3 is not memory |
| "Content-bearing archive" | "Weak channel" | No content transmission |
| "Historical inheritance" | "Stabilization effect" | No inheritance mechanism |
| "Compressed memory" | "Low-bandwidth signal" | No memory semantics |
| "Ancestral wisdom" | [TERMINATED] | Narrative contamination |

---

## Scientific Value Assessment

### What We Proved

1. **Falsification works**: The system can reject its own hypotheses
2. **Presence ≠ Content**: Architectural effects distinct from informational effects
3. **L2 validated**: Lineage tracking mechanism remains sound

### What We Learned

1. **Channel effects are real**: Low-bandwidth external coupling helps
2. **Content is not the mechanism**: Specific historical information not utilized
3. **Design constraint**: Current archive implementation too weak for content transmission

### What We Avoided

1. **Confirmation bias**: Did not force positive interpretation
2. **Scope creep**: Did not expand to rescue failed hypothesis
3. **Narrative drift**: Accepted hard result without reframing

---

## Next Steps

### Immediate (This Week)

1. ✅ **Accept verdict**: NO_GO formally recorded
2. ✅ **Update terminology**: Remove content-bearing language
3. ✅ **Archive data**: Preserve for future meta-analysis

### Phase 6 Planning (Next 2 Weeks)

1. **Design H1 test**: Archive-as-generic-prior
2. **Evaluate H2**: Content-threshold (decide if worth testing)
3. **Write new spec**: Phase 6 with revised hypotheses

### Long-term (Next Month)

1. **Architecture decision**: Keep L3 as channel, redesign as memory, or remove?
2. **Alternative designs**: Consider non-archive stabilization mechanisms
3. **Publication strategy**: Report falsification as positive methodological outcome

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Execution Lead | Kimi/Local | 2026-03-09 | ✅ Data valid |
| Analysis Lead | Codex | 2026-03-09 | ✅ Analysis confirmed |
| Decision | Atlas-HEC | 2026-03-09 | ✅ NO_GO accepted |

---

**Document Status**: FINAL  
**Distribution**: Internal only  
**Next Review**: Phase 6 planning meeting
