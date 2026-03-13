# Akashic Region Summary

**Generated**: 2026-03-12T14:13:18.963350
**Schema Version**: 1.0
**Source**: P2.6 Specialist Routing Lane

---

## Overview

- **Total Candidates**: 12
- **Regions Identified**: 2
- **Noise Points**: 0
- **Embedding Dimension**: 2

## Region Atlas

### HIGH_VARIANCE_REGION (Cluster 0)

**Size**: 7 candidates

**Members**:
- `SpikeCandidate-1` (risk: 0.48)
- `Experimental-B` (risk: 0.20)
- `OQS-v2` (risk: 0.22)
- `Experimental-A` (risk: 0.30)
- `SpikeCandidate-3` (risk: 0.29)
- `SpikeCandidate-2` (risk: 0.43)
- `OQS-Challenger` (risk: 0.24)

**Characteristics**: Inconsistent performance across seeds. May need architectural refinement.

---

### STABLE_REGION (Cluster 1)

**Size**: 5 candidates

**Members**:
- `OctopusLike-R4` (risk: 0.13)
- `StableVariant-B` (risk: 0.12)
- `StableVariant-A` (risk: 0.21)
- `OctopusLike-Mainline` (risk: 0.17)
- `StableVariant-C` (risk: 0.18)

**Characteristics**: High scale retention, low variance, consistent performance. Suitable for production deployment.

---

## Stress-Region Mapping

Based on candidate properties, regions show preferences for stress scenarios:

### high_variance_region

- **Average Risk Score**: 0.310
- **Recommended For**: 
Specific scenarios (see individual candidates)

### stable_region

- **Average Risk Score**: 0.166
- **Recommended For**: 
All scenarios (general purpose)

## Recommendations

### For Mainline (OctopusLike)

- **Current Status**: Located in `stable_region`

- **Assessment**: ✅ Stable

### For Surprise Lane

- **High-risk candidates**: 0 in seed-spike zone

- **Action**: Require additional seed testing before promotion

### For OQS Line

- **Location**: `high_variance_region`

- **Distance to Mainline**: (see embedding analysis)
