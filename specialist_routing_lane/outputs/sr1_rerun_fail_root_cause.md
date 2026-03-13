# SR1 Rerun - Root Cause Analysis

**Date**: 2026-03-12
**Status**: ❌ FAIL (1/5 criteria passed)
**Data**: Real data from socs_universe_search/outputs/
**Candidates**: 22 (9 real + 13 variants)

---

## Results

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Silhouette Score | 0.468 | > 0.5 | ❌ FAIL |
| Davies-Bouldin | 0.650 | < 1.0 | ✅ PASS |
| Inter-Family Separation | 0.000 | > 0.5 | ❌ FAIL |
| Mainline Stability | 37.5% | > 80% | ❌ FAIL |
| Seed-Spike Detection | 0.0% | > 80% | ❌ FAIL |

---

## Root Cause Analysis

### 1. Silhouette Score 不足 (0.468 < 0.5)
**原因**: 数据质量问题
- 所有候选本质上是同一架构家族 (octopus_like) 的变体
- 缺少真正的 OQS/pulse_central 对抗样本
- 变体之间的特征差异不够显著

### 2. Inter-Family Separation 失败
**原因**: 缺乏真正的对抗家族
- 22个候选中 16个是 OctopusLike 及其变体
- 3个是 pulse_central (数据不足)
- 没有独立的 OQS challenger 数据

### 3. Mainline Stability 失败 (37.5% < 80%)
**原因**: 聚类算法将 OctopusLike 分散到多个区域
- 只有 6/16 OctopusLike 在 stable_region
- R4/R5/R6 被分散到不同区域
- 指纹维度对 scale factor 敏感

### 4. Seed-Spike Detection 失败
**原因**: 合成变体的风险值不够极端
- 最高 seed_spike_risk = 0.48 (未达到 0.7 阈值)
- 缺乏真实的失败/崩溃历史数据

---

## Decision

根据决策规则：
> 若 mainline stability 也失效 → 直接降级 P2.6 优先级

**结论**: P2.6 暂停，进入 schema redesign 阶段。

原因不是"数据不够"，而是：
1. 当前 fingerprint schema 无法区分同一架构的 scale variants
2. 缺少真正的对抗家族 (OQS) 数据
3. 需要引入新的维度（如 scale-specific features）

---

## Next Steps

1. **冻结 SR2/SR3** - 在 schema 修复前不启动
2. **Schema Redesign** - 添加 scale-aware 维度
3. **等待真实 OQS 数据** - 从副线获取 challenger 结果
4. **重新评估** - 当满足以下条件时重试 SR1:
   - 真正的 OQS 候选 >= 3
   - OctopusLike 跨 scale 数据 >= 10
   - 明确的失败/seed-spike 历史 >= 5

