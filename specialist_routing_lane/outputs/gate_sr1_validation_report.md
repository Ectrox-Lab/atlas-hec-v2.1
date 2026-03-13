# Gate SR1 Validation Report

**Date**: 2026-03-12T14:12:50.301166
**Status**: ❌ FAIL
**Criteria**: 3/5 passed

---

## Clustering Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Silhouette Score | 0.396 | > 0.5 | ❌ |
| Davies-Bouldin | 0.843 | < 1.0 | ✅ |
| Calinski-Harabasz | 11.2 | - | ℹ️ |

## Validation Checks

### 1. Inter-Family Separation

- OctopusLike found: 2
- OQS found: 2
- Normalized separation: 2.969
- **Status**: ✅ PASS

### 2. Seed-Spike Detection

- Seed-spike region found: False
- Candidates in region: 0
- Precision: 0.0%
- **Status**: ❌ FAIL

### 3. Mainline Stability

- Mainline candidates: 2
- In stable region: 2
- In noise: 0
- Stability ratio: 100.0%
- **Status**: ✅ PASS

## Conclusion

❌ **Gate SR1 FAILED**: Some criteria not met. Review the specific failures above and consider:

- Refining fingerprint dimensions
- Collecting more candidate data
- Adjusting clustering parameters