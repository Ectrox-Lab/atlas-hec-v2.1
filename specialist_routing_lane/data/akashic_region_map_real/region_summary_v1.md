# Akashic Region Summary

**Generated**: 2026-03-12T19:06:18.901083
**Schema Version**: 1.0
**Source**: P2.6 Specialist Routing Lane

---

## Overview

- **Total Candidates**: 22
- **Regions Identified**: 4
- **Noise Points**: 0
- **Embedding Dimension**: 2

## Region Atlas

### REGION_0 (Cluster 0)

**Size**: 6 candidates

**Members**:
- `Octopus Like (seed 23)` (risk: 0.17)
- `Octopus Like (seed 37) (experimental 11)` (risk: 0.18)
- `Octopus Like (seed 37) (experimental 5)` (risk: 0.17)
- `Octopus Like (seed 11)` (risk: 0.17)
- `Octopus Like (seed 11) (experimental 8)` (risk: 0.28)
- `Octopus Like (seed 37)` (risk: 0.12)

**Characteristics**: Standard region with mixed properties.

---

### STABLE_REGION (Cluster 1)

**Size**: 6 candidates

**Members**:
- `OctopusLike R5 (scale=8.0x)` (risk: 0.13)
- `OctopusLike R4 (scale=4.0x) (experimental 2)` (risk: 0.20)
- `OctopusLike R5 (scale=8.0x) (stable variant 10)` (risk: 0.17)
- `OctopusLike R4 (scale=4.0x) (stable variant 1)` (risk: 0.09)
- `OctopusLike R6 (scale=6.0x)` (risk: 0.26)
- `OctopusLike R4 (scale=4.0x)` (risk: 0.10)

**Characteristics**: High scale retention, low variance, consistent performance. Suitable for production deployment.

---

### REGION_2 (Cluster 2)

**Size**: 5 candidates

**Members**:
- `Pulse Central (seed 11) (stable variant 4)` (risk: 0.15)
- `Pulse Central (seed 23)` (risk: 0.17)
- `Pulse Central (seed 37)` (risk: 0.17)
- `Pulse Central (seed 11)` (risk: 0.17)
- `Pulse Central (seed 11) (stable variant 7)` (risk: 0.16)

**Characteristics**: Standard region with mixed properties.

---

### HIGH_VARIANCE_REGION (Cluster 3)

**Size**: 5 candidates

**Members**:
- `OctopusLike R4 (scale=4.0x) (spike variant 6)` (risk: 0.26)
- `Octopus Like (seed 23) (spike variant 12)` (risk: 0.48)
- `OctopusLike R5 (scale=8.0x) (spike variant 0)` (risk: 0.46)
- `Pulse Central (seed 11) (spike variant 9)` (risk: 0.47)
- `OctopusLike R6 (scale=6.0x) (spike variant 3)` (risk: 0.39)

**Characteristics**: Inconsistent performance across seeds. May need architectural refinement.

---

## Stress-Region Mapping

Based on candidate properties, regions show preferences for stress scenarios:

### region_2

- **Average Risk Score**: 0.163
- **Recommended For**: 
Low-risk, stable environments

### region_0

- **Average Risk Score**: 0.180
- **Recommended For**: 
Low-risk, stable environments

### stable_region

- **Average Risk Score**: 0.157
- **Recommended For**: 
All scenarios (general purpose)

### high_variance_region

- **Average Risk Score**: 0.414
- **Recommended For**: 
Specific scenarios (see individual candidates)

## Recommendations

### For Mainline (OctopusLike)

- **Current Status**: Located in `stable_region`

- **Assessment**: ✅ Stable

### For Surprise Lane

- **High-risk candidates**: 0 in seed-spike zone

- **Action**: Require additional seed testing before promotion

### For OQS Line
