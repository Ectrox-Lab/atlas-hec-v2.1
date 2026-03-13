# Gate SR1 Validation Report

**Date**: 2026-03-12T19:06:12.195990
**Status**: ❌ FAIL
**Criteria**: 1/5 passed

---

## Clustering Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Silhouette Score | 0.468 | > 0.5 | ❌ |
| Davies-Bouldin | 0.650 | < 1.0 | ✅ |
| Calinski-Harabasz | 29.9 | - | ℹ️ |

## Validation Checks

### 1. Inter-Family Separation

- OctopusLike found: 16
- OQS found: 0
- Normalized separation: 0.000
- **Status**: ❌ FAIL

### 2. Seed-Spike Detection

- Seed-spike region found: False
- Candidates in region: 0
- Precision: 0.0%
- **Status**: ❌ FAIL

### 3. Mainline Stability

- Mainline candidates: 16
- In stable region: 6
- In noise: 0
- Stability ratio: 37.5%
- **Status**: ❌ FAIL

## Conclusion

❌ **Gate SR1 FAILED**: Some criteria not met. Review the specific failures above and consider:

- Refining fingerprint dimensions
- Collecting more candidate data
- Adjusting clustering parameters