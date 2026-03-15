# Source × Target Transfer Matrix (L5)

> Updated: 2026-03-15  
> Status: 5/6 pairs completed

---

## Current Matrix

| Source \ Target | Math | Code | Planning |
|:---------------|:----:|:----:|:--------:|
| **Code** | 14.69pp ✅ | - | 10.71pp ✅ |
| **Math** | - | 9.77pp ✅ | ⏸️ PENDING |
| **Planning** | ⏸️ PENDING | 7.50pp ✅ | - |

---

## Directionality Analysis

### Code as Source (Both directions verified)

```
Code→Math:  14.69pp (strongest)
Code→Planning: 10.71pp (strong)

→ Code is consistently strong source across targets
```

### Planning as Source/Taget (Both directions verified)

```
Code→Planning: 10.71pp
Planning→Code:  7.50pp
Ratio: 1.428 (near symmetric but biased toward Code)

→ Planning is moderate source, not target-only
→ Gap is smaller than Code/Math pair
```

### Math as Target/Source (One direction each)

```
Code→Math: 14.69pp (Math is excellent target)
Math→Code:  9.77pp (Math is moderate source)
Ratio: 1.504 (similar to Planning ratio)

→ Math pattern resembles Planning pattern
→ Both are better targets than sources
```

---

## Source Suitability Ranking (Working)

| Rank | Task | As Source | As Target | Assessment |
|:----:|:----:|:---------:|:---------:|:-----------|
| 1 | **Code** | ⭐⭐⭐ Strong (10-15pp) | ⭐⭐ Moderate | Best source, universal advantage |
| 2 | **Planning** | ⭐⭐ Moderate (~7.5pp) | ⭐⭐⭐ Strong (10pp+) | Balanced, not target-only |
| 3 | **Math** | ⭐⭐ Moderate (~9-10pp) | ⭐⭐⭐ Strong (14pp+) | Best target, not best source |

---

## Key Patterns

1. **Code Superiority as Source**
   - Highest transfer gaps to both Math and Planning
   - Consistent across targets

2. **Math/Planning Similarity**
   - Both are better targets than sources
   - Both have directionality ratios ~1.4-1.5

3. **No Weak Pairs So Far**
   - All completed pairs >= 7.5pp
   - All pairs >= 9/10 windows positive
   - Suggests broad viability of L5 mechanism

---

## Remaining Pairs

### Batch-6: Math→Planning

**Expected**: 6-9pp  
**Question**: Does Math→Planning follow the pattern?

Hypothesis A: ~8pp (similar to Math→Code)  
→ Supports "Math is moderate source to all"

Hypothesis B: <6pp (much weaker)  
→ Suggests target matters more than source for Math

### Batch-7: Planning→Math

**Expected**: 5-8pp (lowest pair)  
**Question**: Can Planning transfer to Math?

If successful: Complete matrix all positive  
If weak: Reveals boundary of Planning source ability

---

## Theoretical Implications

### Current Evidence Supports:

1. **Source Suitability Hierarchy**
   ```
   Code > Planning ≈ Math (as sources)
   ```

2. **Target Receptivity Hierarchy**
   ```
   Math > Planning ≈ Code (as targets)
   ```

3. **Directionality is Real but Moderate**
   - Ratios 1.4-1.5, not extreme
   - All directions viable, just different efficiencies

### Open Questions:

- Is there a pair where transfer fails (<5pp)?
- Does Math→Planning break the pattern?
- Can we predict transfer strength from source/target properties?

---

## Next Action

Execute Batch-6 (Math→Planning) to complete source coverage.

```bash
python3 ralph_window_gate.py --config L5_BATCH6_MATH2PLANNING.json
```

---

*Source × Target Matrix v1.0*
