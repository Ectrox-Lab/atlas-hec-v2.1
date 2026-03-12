# Gate SR1 验收表
## Structure Fingerprint Validity

**Line**: P2.6 Specialist Routing Lane  
**Gate**: SR1  
**Status**: 🟡 ACTIVE  
**Created**: 2026-03-12  

---

## 验收目标

验证结构指纹能否有效区分不同架构家族，识别 seed-spike 高风险区，并将主线候选定位在稳定区域。

---

## 验收标准

### 1. Inter-Family Separation (家族分离度)

| 检查项 | 阈值 | 实测值 | 状态 |
|--------|------|--------|------|
| Silhouette Score | > 0.5 | ___ | ⬜ |
| OctopusLike-OQS 分离 | 可归区 | ___ | ⬜ |
| 簇重叠度 | < 30% | ___ | ⬜ |

**通过标准**: Silhouette Score > 0.5 且不同家族在嵌入空间可分离

### 2. Seed-Spike Detection (假阳性识别)

| 检查项 | 阈值 | 实测值 | 状态 |
|--------|------|--------|------|
| 高风险区 Precision | > 80% | ___ | ⬜ |
| Seed-spike 聚类集中度 | 明显聚类 | ___ | ⬜ |
| 自动拦截率 | 记录 | ___ | ⬜ |

**通过标准**: Seed-spike 候选被有效聚类到高风险区域

### 3. Mainline Stability (主线稳定性)

| 检查项 | 阈值 | 实测值 | 状态 |
|--------|------|--------|------|
| OctopusLike 所在区域 | 稳定区 | ___ | ⬜ |
| 距噪声边界距离 | > 2σ | ___ | ⬜ |
| 不在 seed-spike 区 | 是 | ___ | ⬜ |

**通过标准**: 主线候选落在稳定区域，远离噪声边界

### 4. Cluster Coherence (簇内紧密度)

| 检查项 | 阈值 | 实测值 | 状态 |
|--------|------|--------|------|
| Davies-Bouldin Index | < 1.0 | ___ | ⬜ |
| Calinski-Harabasz Index | > 100 | ___ | ⬜ |
| 跨 seed 稳定性 | AMI > 0.7 | ___ | ⬜ |

**通过标准**: 簇内紧密度指标达到阈值

---

## 执行步骤

### Phase 1: 数据收集

```bash
# 1.1 提取结构指纹
python scripts/extract_structure_fingerprint.py \
  --input ../experiments/outputs/ \
  --output data/candidate_fingerprints/fingerprint_v1.jsonl
```

**验收点**: 
- [ ] 指纹文件已生成
- [ ] 包含至少 10 个候选
- [ ] 所有必需字段完整

### Phase 2: 聚类构建

```bash
# 2.1 构建结构索引
python scripts/build_structure_index.py \
  --input data/candidate_fingerprints/fingerprint_v1.jsonl \
  --config configs/clustering_config.yaml \
  --output data/clustered_regions/
```

**验收点**:
- [ ] 聚类结果已生成
- [ ] 发现 3+ 个区域
- [ ] 可视化输出正常

### Phase 3: 验证测试

```bash
# 3.1 运行验证
python scripts/validate_clusters.py \
  --clusters data/clustered_regions/ \
  --output outputs/gate_sr1_validation_report.md
```

**验收点**:
- [ ] 验证报告已生成
- [ ] 所有指标已计算
- [ ] 通过/失败状态明确

### Phase 4: 阿卡西集成

```bash
# 4.1 写入区域映射
python scripts/write_akashic_region_summary.py \
  --regions data/clustered_regions/ \
  --output data/akashic_region_map/
```

**验收点**:
- [ ] 区域摘要已生成
- [ ] JSON 映射可用
- [ ] 升级候选列表已产出

---

## 通过条件

**必须全部满足**:

1. ⬜ Silhouette Score > 0.5
2. ⬜ Seed-spike Precision > 80%
3. ⬜ Mainline 在稳定区域
4. ⬜ Davies-Bouldin < 1.0

**满足 4/4**: ✅ **GATE SR1 PASSED** → 进入 Gate SR2  
**满足 3/4**: 🟡 **CONDITIONAL PASS** → 补充验证后决定  
**满足 <3/4**: ❌ **GATE SR1 FAILED** → 重新设计指纹或收集更多数据

---

## 失败处理

### 如果 Silhouette Score 不达标

**可能原因**:
- 指纹维度不足
- 候选数量太少
- OctopusLike 与 OQS 本质相似

**应对措施**:
1. 增加指纹维度（如通信模式、层次结构细节）
2. 收集更多历史数据
3. 重新评估 OQS 作为独立家族的合理性

### 如果 Seed-spike 检测不达标

**可能原因**:
- 历史 seed-spike 样本不足
- 风险评分公式不准确
- 聚类算法参数不当

**应对措施**:
1. 手动标注更多 seed-spike 案例
2. 调整风险权重
3. 尝试不同聚类算法

### 如果 Mainline 不在稳定区

**可能原因**:
- OctopusLike 实际上不够稳定
- 指纹设计有偏差
- 稳定区定义过于严格

**应对措施**:
1. 重新评估 OctopusLike R3 数据
2. 检查是否有遗漏的 stress 场景
3. 调整稳定区阈值

---

## 人工审查清单

在自动验证通过后，进行人工审查:

- [ ] 区域标签是否合理（stable_region, seed_spike_zone 等）
- [ ] OctopusLike 是否与已知特性一致
- [ ] OQS 是否被正确归类
- [ ] 噪声点是否有合理解释
- [ ] 区域数量是否过多/过少

**审查人**: _______________  **日期**: _______________

---

## 最终决策

| 项目 | 内容 |
|------|------|
| 执行日期 | _______________ |
| 验收结果 | ⬜ PASS / ⬜ CONDITIONAL / ⬜ FAIL |
| 主要发现 | |
| 阻塞问题 | |
| 下一步行动 | |
| 决策人 | _______________ |

---

## 附录

### A. 快速验证命令

```bash
# 一键运行全部验证
cd /home/admin/atlas-hec-v2.1-repo/specialist_routing_lane

python scripts/extract_structure_fingerprint.py \
  -i ../experiments/outputs/ \
  -o data/candidate_fingerprints/fingerprint_v1.jsonl && \
python scripts/build_structure_index.py \
  -i data/candidate_fingerprints/fingerprint_v1.jsonl \
  -c configs/clustering_config.yaml \
  -o data/clustered_regions/ && \
python scripts/validate_clusters.py \
  -c data/clustered_regions/ \
  -o outputs/gate_sr1_validation_report.md
```

### B. 预期输出文件

```
outputs/
├── gate_sr1_validation_report.md      # 本验收表对应的验证报告
├── region_report.md                    # 区域分析报告（Phase 4 后生成）
└── candidate_routing_report.md         # 路由报告（Phase 4 后生成）

data/clustered_regions/
├── regions_v1.json                     # 聚类结果
├── embedding_v1.npy                    # 嵌入向量
├── clusters_v1.npy                     # 簇标签
└── candidate_mapping.json              # 候选映射

data/akashic_region_map/
├── region_summary_v1.md                # 阿卡西可读摘要
├── region_mapping_v1.json              # 程序化映射
└── promotion_candidates_v1.json        # 升级推荐
```

### C. 相关文档

- `HYPOTHESIS_SR1.md` - 完整假设定义
- `README.md` - P2.6 线说明
- `../STATUS.md` - 项目总状态

---

*最后更新: 2026-03-12*
