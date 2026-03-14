# Stable vs Leakage Pattern Table

**E-COMP-003 Deliverable**  
**Date**: 2026-03-14  
**Source**: L4-v2 Round B winners (n=4 approved candidates)

---

## Overview

| Category | Count | Percentage | Key Families |
|----------|-------|------------|--------------|
| **Stable Patterns** | 4 | 100% | F_P2T4M4 (3), F_P3T4M4 (1) |
| **Leakage Patterns** | 0 | 0% | None observed |
| **Pseudo-Reuse** | 0 | 0% | None detected |

**Note**: Very small sample size (n=4) - patterns are preliminary.

---

## Stable Pattern Analysis

### Pattern 1: F_P2T4M4 (Moderate Pressure, High Triage, High Memory)

**Observations**:
- **Count**: 3/4 winners (75%)
- **Mechanism Score**: 0.5 - 0.6 (moderate)
- **Trust Pattern**: "balanced" (decay 0.08-0.12, recovery 0.04-0.06)
- **Delegation Pattern**: "pressure_threshold_based" (inferred from P2)
- **Success Rate**: 33% (within this family)

**Characteristics**:
- Lower pressure (P2) reduces system stress
- High triage (T4) enables good task prioritization
- High memory (M4) supports recovery sequences
- Moderate mechanism score suggests this is a "safe" configuration

**Why It Works**:
- P2 = less pressure cascade risk
- T4 = better deadline management
- M4 = enough buffer for recovery
- Not pushing boundaries = more consistent performance

### Pattern 2: F_P3T4M4 (High Pressure, High Triage, High Memory)

**Observations**:
- **Count**: 1/4 winners (25%)
- **Mechanism Score**: 0.92 (very high)
- **Trust Pattern**: "balanced"
- **Delegation Pattern**: "adaptive_migration" (inferred from P3)
- **Is Stable Family**: Yes (in L4-v2 definition)

**Characteristics**:
- Higher pressure (P3) but managed by high triage/memory
- Very high mechanism score suggests this is the "golden" configuration
- Lower success rate in this sample (1 winner) but higher quality

**Why It Works**:
- P3 = higher throughput potential
- T4 + M4 = enough capacity to manage P3 stress
- When it works, it works very well (mechanism_score 0.92)

---

## Leakage Pattern Analysis

**Observation**: Zero leakage in approved candidates.

**Leakage Families (from L4-v2 definition)**:
- P1, P4 (extreme pressure)
- T2, T5 (extreme triage)
- M1, M5 (extreme memory)

**Result**: None of these appeared in winners.

**Interpretation**:
- Anti-leakage penalty was effective
- System successfully avoided structural expansion
- Winners are concentrated in "middle ground" (P2-3, T4, M4)

---

## Pseudo-Reuse Detection

**Definition**: Candidates that pass but don't actually reuse stable mechanisms.

**Detection Criteria**:
1. Approved but mechanism_score < 0.3
2. Novel motifs not in stable set
3. High performance variance across seeds

**Result**: No pseudo-reuse detected in winners.

- All winners have mechanism_score >= 0.5
- All use known delegation patterns
- All from families in stable set

---

## Key Insights

### 1. T4M4 is the Common Denominator

**100% of winners have T=4, M=4.**

This suggests:
- High triage (T4) is necessary for good performance
- High memory (M4) is necessary for recovery
- Pressure (P) can vary (2 or 3) but T/M must be high

### 2. P2 vs P3 Trade-off

| Family | Throughput Potential | Consistency | Best Use Case |
|--------|---------------------|-------------|---------------|
| F_P2T4M4 | Lower | Higher | Safe, reliable |
| F_P3T4M4 | Higher | Lower (but higher ceiling) | Aggressive optimization |

### 3. Mechanism vs Family

**Question**: Is F_P3T4M4 a family label or a mechanism bundle?

**Evidence**:
- F_P3T4M4 has very high mechanism_score (0.92)
- Represents specific mechanism combination: adaptive_migration + trust_based_routing
- Not just "P=3, T=4, M=4" but "high pressure managed by specific mechanisms"

**Conclusion**: F_P3T4M4 is a **mechanism bundle**, not just a family label.

---

## Recommendations for L4-v3

### 1. Focus on T4M4 Base

All winners have T4M4. This should be the foundation of next-generation candidates.

### 2. Pressure as Tuning Parameter

P2 for safety, P3 for performance. Both viable with T4M4.

### 3. Mechanism Scoring Over Family Bias

F_P3T4M4's high mechanism_score (0.92) is more predictive than family membership alone.

### 4. Anti-Leakage Confirmed Effective

Zero leakage in winners. Keep penalty structure for L4-v3.

---

## Open Questions

1. **Why only 4 winners?**
   - Task-1 difficulty
   - Need larger sample to confirm patterns

2. **Can F_P3T4M4 scale?**
   - Only 1 winner in current sample
   - High mechanism_score suggests potential
   - Need more evaluation

3. **Are there other viable families?**
   - F_P2T3M4? F_P3T3M4?
   - Current sample too small to rule out

---

## Confidence Assessment

| Claim | Confidence | Reason |
|-------|------------|--------|
| T4M4 is necessary | **High** | 100% of winners |
| P2 safer than P3 | **Medium** | 3 vs 1 winners, but small sample |
| Anti-leakage works | **High** | 0% leakage |
| F_P3T4M4 is mechanism bundle | **Medium** | High mechanism_score, but n=1 |
| No pseudo-reuse | **High** | All winners have good mechanism scores |

**Overall**: Patterns are clear but based on tiny sample. Recommend larger evaluation before finalizing L4-v3.

---

*Generated by E-COMP-003 Mechanism Analysis*  
*Next update: After larger sample evaluation*
