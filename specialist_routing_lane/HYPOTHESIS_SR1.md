# HYPOTHESIS SR1: Structure Fingerprint Validity

## Metadata

| Field | Value |
|-------|-------|
| **Hypothesis ID** | SR1 |
| **Line** | P2.6 Specialist Routing Lane |
| **Phase** | Gate 1 - Foundation Validation |
| **Status** | 🟡 ACTIVE |
| **Created** | 2026-03-12 |
| **Target Completion** | 2026-03-19 |

---

## 1. Core Hypothesis

> **结构指纹能够有效区分不同架构家族，识别 seed-spike 高风险区，并将主线候选定位在稳定区域而非噪声区。**

### 1.1 Formal Statement

如果提取的**结构指纹**（Structure Fingerprint）包含：
- 结构组织特征（CWCI 6维 + 架构拓扑）
- 稳健性特征（scale retention, seed variance）
- 行为特征（recovery, energy, coordination, hazard）
- 失败特征（failure mode signature）

那么在嵌入空间（embedding space）中：
1. **OctopusLike** 与 **OQS** 应形成可分离的簇
2. **Seed-spike candidates** 应聚类在独立的高风险区域
3. **Mainline candidates** 应落在稳定区域，远离噪声边界

---

## 2. Motivation

### 2.1 Problem Statement

当前系统面临以下问题：

| Problem | Impact |
|---------|--------|
| 候选结构爆炸 | 无法有效筛选和分类 |
| Seed-spike 假阳性 | 浪费验证资源在低质量候选上 |
| 缺乏结构地图 | 无法判断候选的"邻近结构"和"进化路径" |
| 阿卡西记录碎片化 | 只有日志，没有结构化索引 |

### 2.2 Why This Matters

- **主线保护**：确保 OctopusLike Mainline 的地位不是基于评分器偏好
- **质量过滤**：提前识别 seed-spike 假阳性，降低验证成本
- **导航发现**：将随机惊喜发现升级为可导航的结构发现

---

## 3. Methodology

### 3.1 Structure Fingerprint Schema

```yaml
# 结构指纹 - 四维向量空间
fingerprint:
  # A. 结构组织指纹 (Organizational)
  organizational:
    cwci_total: float          # CWCI 总分
    specialization: float      # 专业化程度
    integration: float         # 整合程度
    broadcast: float           # 广播效率
    hierarchy_depth: int       # 层级深度
    autonomy_strength: float   # 自主性强度
    memory_partition_style: enum  # [distributed|centralized|hybrid]
  
  # B. 稳健性指纹 (Robustness)
  robustness:
    scale_retention: float     # 规模扩展保持率
    seed_variance: float       # seed 方差 (越低越稳定)
    cwci_min: float            # 最差表现
    cwci_max: float            # 最佳表现
    stress_coverage: float     # 压力场景覆盖率
    pass_rate: float           # 通过率
  
  # C. 行为指纹 (Behavioral)
  behavioral:
    recovery_time: float       # 恢复时间
    energy_stability: float    # 能量稳定性
    coordination_score: float  # 协调得分
    hazard_resistance: float   # 危险抵抗
    communication_cost: float  # 通信开销
  
  # D. 失败指纹 (Failure)
  failure:
    first_failure_mode: enum   # [coordination|energy|memory|broadcast]
    seed_spike_risk: float     # seed spike 风险评分
    collapse_signature: str    # 崩溃特征哈希
    bottleneck_type: enum      # [single_point|distributed|cascading]
```

### 3.2 Clustering Strategy

```
Stage 1: Raw Fingerprint Extraction
    │
    ▼
Stage 2: Dimensionality Reduction (UMAP/t-SNE)
    │
    ▼
Stage 3: Density-Based Clustering (HDBSCAN)
    │
    ▼
Stage 4: Region Labeling & Validation
```

### 3.3 Input Data Sources

| Source | Path | Data Type |
|--------|------|-----------|
| O1 Gate Results | `experiments/HYPOTHESIS_O1.md` | OctopusLike 性能数据 |
| OQS Gate Results | `experiments/HYPOTHESIS_OQS_*.md` | OQS 性能数据 |
| Smoke Results | `outputs/smoke_tests/` | 压力测试数据 |
| CWCI Reports | `outputs/cwci_reports/` | 6维意识指标 |
| Surprise Candidates | `surprise_search/candidates/` | 新发现候选 |

---

## 4. Success Criteria

### 4.1 Gate SR1 Pass Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| **Inter-family Separation** | Silhouette Score > 0.5 | OctopusLike vs OQS 分离度 |
| **Seed-spike Detection** | Precision > 80% | 高风险区识别准确率 |
| **Mainline Stability** | Distance to noise > 2σ | 主线候选距噪声边界距离 |
| **Cluster Coherence** | Davies-Bouldin Index < 1.0 | 簇内紧密度 |

### 4.2 Explicit Fail Criteria

以下情况将导致 Gate SR1 **失败**：

- [ ] OctopusLike 与 OQS 在嵌入空间中重叠 > 30%
- [ ] Seed-spike candidates 均匀分布，无明显聚类
- [ ] Mainline candidates 分布在噪声边界
- [ ] 指纹维度相关性过高（>0.9），存在冗余

### 4.3 Partial Success / Refinement Triggers

| Condition | Action |
|-----------|--------|
| Silhouette Score 0.3-0.5 | 增加指纹维度或调整权重 |
| Seed-spike precision 60-80% | 补充更多历史失败数据 |
| 簇数 > 10 | 合并相似区域，建立层级结构 |

---

## 5. Experiment Plan

### 5.1 Phase 1: Data Collection (Day 1-2)

```bash
# 提取所有候选的结构指纹
python scripts/extract_structure_fingerprint.py \
  --inputs experiments/outputs/ \
  --output data/candidate_fingerprints/
```

**Deliverable**: `data/candidate_fingerprints/fingerprint_v1.jsonl`

### 5.2 Phase 2: Clustering (Day 3-4)

```bash
# 构建结构索引
python scripts/build_structure_index.py \
  --input data/candidate_fingerprints/ \
  --config configs/clustering_config.yaml \
  --output data/clustered_regions/
```

**Deliverable**: 
- `data/clustered_regions/regions_v1.json`
- `data/clustered_regions/embedding_v1.npy`

### 5.3 Phase 3: Validation (Day 5-6)

```bash
# 验证聚类质量
python scripts/validate_clusters.py \
  --clusters data/clustered_regions/ \
  --ground-truth data/ground_truth_labels.csv \
  --output outputs/validation_report.md
```

**Deliverable**: `outputs/gate_sr1_validation_report.md`

### 5.4 Phase 4: Akashic Integration (Day 7)

```bash
# 写入阿卡西区域映射
python scripts/write_akashic_region_summary.py \
  --regions data/clustered_regions/ \
  --output data/akashic_region_map/
```

**Deliverable**: `data/akashic_region_map/region_summary_v1.md`

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 数据不足 | Medium | High | 放宽历史数据时间窗口 |
| 维度诅咒 | Low | Medium | 使用 UMAP 降维 |
| 标签噪声 | Medium | Medium | 多轮交叉验证 |

### 6.2 Research Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| 指纹设计缺陷 | Low | High | 预留维度扩展接口 |
| 聚类不稳定 | Medium | Medium | 多 seed 平均 |
| 与主线目标偏离 | Low | High | 每周与主线同步 |

---

## 7. Resource Requirements

| Resource | Amount | Notes |
|----------|--------|-------|
| Compute | 4 CPU cores | 聚类计算 |
| Storage | 1 GB | 指纹和嵌入数据 |
| Time | 7 days | 完整 Gate SR1 周期 |
| Human Review | 4 hours | 验证报告审查 |

---

## 8. Dependencies

### 8.1 Blocked By

- [x] OctopusLike R3 完成
- [x] OQS Gate 2 完成
- [x] CWCI 指标标准化

### 8.2 Blocks

- Gate SR2: Routing Usefulness
- Gate SR3: Akashic Upgrade
- Mainline R4 结构分析报告

---

## 9. Output Artifacts

### 9.1 Required Deliverables

```
outputs/
├── gate_sr1_validation_report.md      # 主要验证报告
├── region_report.md                    # 区域分析报告
├── specialist_map.json                 # 专家映射（V1）
└── candidate_routing_report.md         # 候选路由报告
```

### 9.2 Success Artifacts

若 Gate SR1 通过，将产出：

1. **Region Atlas V1**: 结构区域地图
2. **Fingerprint Library**: 可复用的指纹提取库
3. **Clustering Pipeline**: 自动化聚类流程
4. **Integration Guide**: 与主线/阿卡西的集成指南

---

## 10. Decision Log

| Date | Decision | Rationale | By |
|------|----------|-----------|-----|
| 2026-03-12 | 启动 SR1 | 主线需要结构导航层 | System |
| | 选择 HDBSCAN | 无需预设簇数，适合探索 | | 
| | 指纹 4 维度 | 平衡表达力和可解释性 | |

---

## 11. Appendix

### 11.1 Related Documents

- `../HYPOTHESIS_O1.md` - OctopusLike Mainline
- `../HYPOTHESIS_OQS_*.md` - OQS Challenger
- `../STATUS.md` - 项目总状态
- `README.md` - 本线说明

### 11.2 Glossary

| Term | Definition |
|------|------------|
| Structure Fingerprint | 结构的多维特征向量 |
| Seed-spike | 仅在特定 seed 下表现好的假阳性候选 |
| Region | 嵌入空间中的结构簇 |
| Mainline | OctopusLike 主线架构 |

---

**Next Step**: 执行 Phase 1 数据收集，见 `scripts/extract_structure_fingerprint.py`
