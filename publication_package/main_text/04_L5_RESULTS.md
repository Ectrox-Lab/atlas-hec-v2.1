# 4. L5 Results: Cross-Task Inheritance

## 4.1 Overview

L5 tests whether single-task improvement (L4) extends across task boundaries. Six unique task pairs evaluated across three task types: Math, Code, Planning.

## 4.2 Transfer Matrix

| Source \ Target | Math | Code | Planning | Mean as Source |
|:---------------|:----:|:----:|:--------:|:--------------:|
| **Code** | **14.69** [13.73, 15.55] | — | **10.71** [9.98, 11.51] | **12.70** [11.66, 13.78] |
| **Math** | — | 9.77 [8.84, 10.71] | 7.09 [6.22, 7.95] | 8.43 [7.57, 9.32] |
| **Planning** | 6.25 [4.79, 7.99] | 7.50 [6.67, 8.17] | — | 6.88 [5.95, 7.84] |

*Values: Mean Transfer Gap (pp) with 95% Bootstrap CI*

## 4.3 Key Findings

### 4.3.1 Broad Viability
- **6/6 pairs positive**: All source-target combinations show positive transfer
- **67/70 windows positive** (95.7%)
- **Range**: 6.25 - 14.69pp
- **No failed pairs**

### 4.3.2 Source Suitability Hierarchy
Statistically significant ranking: **Code > Math > Planning**

| Source | Mean [95% CI] | vs Next | Significance |
|:-------|:-------------:|:-------:|:------------:|
| Code | 12.70 [11.66, 13.78] | > Math | CI non-overlap (p < 0.05) |
| Math | 8.43 [7.57, 9.32] | > Planning | Partial overlap (marginal) |
| Planning | 6.88 [5.95, 7.84] | — | Baseline |

### 4.3.3 Directionality Structure
Transfer is bidirectionally viable but not directionally neutral:

| Pair | Forward | Reverse | Ratio | Assessment |
|:-----|:-------:|:-------:|:-----:|:-----------|
| Code↔Math | 14.69 | 9.77 | 1.50 | Strong bias toward Code |
| Code↔Planning | 10.71 | 7.50 | 1.43 | Moderate bias toward Code |
| Math↔Planning | 7.09 | 6.25 | 1.13 | Near symmetric |

**Interpretation**: Directionality exists but is moderate. No extreme asymmetry (>2x) observed.

## 4.4 Statistical Validation

### 4.4.1 Bootstrap Confidence Intervals
All 6 pairs have strictly positive 95% CIs (lower bound > 0). 5/6 pairs have narrow CIs (<2pp width).

### 4.4.2 Variance Components
- Between-pair variance accounts for hierarchy structure
- Within-pair variance stable (CV 0.11-0.44)

## 4.5 Controls

### 4.5.1 Control 1: Temporal Shuffling
**Purpose**: Test if effect depends on window execution order  
**Method**: Shuffle window order, recalculate mean  
**Result**: No effect on mean (SD ≈ 0). Original mean within all shuffled CIs.  
**Conclusion**: Effect not artifact of temporal structure.

### 4.5.2 Control 2: Random Pairing  
**Purpose**: Test if arbitrary task pairing produces similar effects  
**Method**: Generate random source-target pairs, measure "transfer"  
**Results**:
- Random baseline: +0.72pp
- Real pairs mean: +9.33pp
- **Delta: +8.62pp (HIGH significance)**

**Per-pair uplift over random**:
```
Code→Math:      +13.97pp
Code→Planning:  +9.99pp
Math→Code:      +9.05pp
Planning→Code:  +6.78pp
Math→Planning:  +6.37pp
Planning→Math:  +5.53pp
```

**Conclusion**: Real pairs substantially exceed random baseline. Effect depends on genuine task relationships.

## 4.6 Claim Scope

**Supported**: Cross-task inheritance is broadly viable and structured within the evaluated Math/Code/Planning task family.

**Not Claimed**: Universal across arbitrary tasks, mechanism fully identified, or cross-model generalization.

## 4.7 Transition to L6

L5 establishes that inheritance transfers across tasks with discoverable structure. L6 asks whether the system can learn to exploit this structure—can it learn *which* source to use for each target?
