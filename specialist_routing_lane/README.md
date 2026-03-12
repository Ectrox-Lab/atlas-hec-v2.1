# P2.6 Specialist Routing Lane

> **结构地图 + 专家路由 + 阿卡西区域索引层**

---

## 1. One-Line Positioning

P2.6 不是新的主线架构，而是**服务于主线的结构导航基础设施**。它的价值是帮助主线理解自己、识别邻近候选、过滤假阳性，并把惊喜发现从随机碰运气升级为**可导航的结构发现**。

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    多元宇宙扫描 / Surprise Search                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Candidate Fingerprint Extractor                     │
│              (结构指纹提取: CWCI + 稳健性 + 行为 + 失败)        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               Structure Embedding / Clustering                   │
│               (FAISS / UMAP / HDBSCAN)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Specialist Region Index                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │  Region  │  Region  │  Region  │  Region  │  Region  │      │
│  │    A     │    B     │    C     │    D     │    E     │      │
│  │(Octopus) │  (OQS)   │(Surprise)│(Seed-spk)│ (Stable) │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌─────────────────┐ ┌──────────┐ ┌─────────────────┐
    │  Akashic Memory │ │  Routing │ │  Surprise Lane  │
    │  (区域映射)     │ │  Layer   │ │  (质量提升)     │
    └─────────────────┘ └──────────┘ └─────────────────┘
```

---

## 3. Directory Structure

```
specialist_routing_lane/
├── README.md                           # 本文件
├── HYPOTHESIS_SR1.md                   # Gate 1: 结构指纹有效性
├── HYPOTHESIS_SR2.md                   # Gate 2: 路由有用性
├── HYPOTHESIS_SR3.md                   # Gate 3: 阿卡西升级
│
├── configs/
│   ├── fingerprint_schema.yaml         # 指纹维度定义
│   ├── clustering_config.yaml          # 聚类参数
│   └── routing_thresholds.yaml         # 路由阈值
│
├── data/
│   ├── candidate_fingerprints/         # 候选指纹原始数据
│   ├── clustered_regions/              # 聚类后的区域数据
│   └── akashic_region_map/             # 阿卡西区域映射
│
├── scripts/
│   ├── extract_structure_fingerprint.py
│   ├── build_structure_index.py
│   ├── cluster_candidates.py
│   ├── route_by_stress.py
│   └── write_akashic_region_summary.py
│
├── outputs/
│   ├── region_report.md
│   ├── specialist_map.json
│   └── candidate_routing_report.md
│
└── proposals/
    └── promotion_candidates.md         # 升级推荐候选
```

---

## 4. Gates

### Gate SR1: Structure Fingerprint Validity 🟡 ACTIVE

**目标**: 验证结构指纹能否有效区分不同架构家族

**通过标准**:
- OctopusLike 与 OQS 可分离 (Silhouette > 0.5)
- Seed-spike 候选聚类在高风险区 (Precision > 80%)
- 主线候选在稳定区域 (距噪声边界 > 2σ)

**交付物**: `outputs/gate_sr1_validation_report.md`

---

### Gate SR2: Routing Usefulness ⏸️ PENDING

**目标**: 验证路由层能给主线提供有效建议

**通过标准**:
- 能根据 stress 给出结构推荐
- 推荐结果与真实验证一致
- 能拦截假阳性候选

---

### Gate SR3: Akashic Upgrade ⏸️ PENDING

**目标**: 验证阿卡西区域映射提升惊喜发现质量

**通过标准**:
- 新候选假阳性率下降
- 结构区域稳定
- 某些区域稳定产出强候选

---

## 5. Relationship with Main Lines

```
┌────────────────────────────────────────────────────────────┐
│                     OctopusLike Mainline (P0)              │
│                     55% Resources                          │
│  Mission: 冲规模、冲真实 runtime、冲开放世界稳健性        │
└────────────────────────────────────────────────────────────┘
                              ▲
                              │ 服务
┌────────────────────────────────────────────────────────────┐
│              P2.6 Specialist Routing Lane (5%)             │
│                                                            │
│  • 给主线建结构地图                                        │
│  • 给主线找邻近替代者                                      │
│  • 给阿卡西建区域索引                                      │
│  • 给惊喜发现提升质量                                      │
└────────────────────────────────────────────────────────────┘
```

### What P2.6 Does NOT Do

- ❌ 替代 OctopusLike 主线
- ❌ 替代 OQS 挑战者线
- ❌ 替代真实 SOCS 本体
- ❌ 替代 CWCI 主评估器

### What P2.6 DOES

- ✅ 结构空间导航
- ✅ 阿卡西区域索引
- ✅ 场景路由推荐
- ✅ 假阳性过滤

---

## 6. Quick Start

### 6.1 Extract Fingerprints

```bash
cd /home/admin/atlas-hec-v2.1-repo/specialist_routing_lane

python scripts/extract_structure_fingerprint.py \
  --input ../experiments/outputs/ \
  --output data/candidate_fingerprints/
```

### 6.2 Build Index

```bash
python scripts/build_structure_index.py \
  --input data/candidate_fingerprints/ \
  --config configs/clustering_config.yaml \
  --output data/clustered_regions/
```

### 6.3 Route Query

```bash
python scripts/route_by_stress.py \
  --stress ResourceScarcity \
  --top-k 5 \
  --output outputs/recommendations.json
```

---

## 7. Input / Output

### Input Sources

| Source | Description |
|--------|-------------|
| O1/OQS Gate 结果 | 主线/副线实验数据 |
| Surprise Search | 新发现候选 |
| CWCI Reports | 6维意识指标 |
| Smoke Tests | 压力测试数据 |

### Output Artifacts

| Artifact | Description |
|----------|-------------|
| Region Atlas | 结构区域地图 |
| Specialist Map | 专家-场景映射 |
| Akashic Index | 阿卡西区域索引 |
| Routing API | 路由推荐接口 |

---

## 8. Fingerprint Schema

结构指纹是一个四维向量：

```python
fingerprint = {
    # A. 结构组织指纹
    "organizational": {
        "cwci_total": float,
        "specialization": float,
        "integration": float,
        "broadcast": float,
        "hierarchy_depth": int,
        "autonomy_strength": float,
        "memory_partition_style": str,
    },
    # B. 稳健性指纹
    "robustness": {
        "scale_retention": float,
        "seed_variance": float,
        "cwci_min": float,
        "cwci_max": float,
        "stress_coverage": float,
        "pass_rate": float,
    },
    # C. 行为指纹
    "behavioral": {
        "recovery_time": float,
        "energy_stability": float,
        "coordination_score": float,
        "hazard_resistance": float,
        "communication_cost": float,
    },
    # D. 失败指纹
    "failure": {
        "first_failure_mode": str,
        "seed_spike_risk": float,
        "collapse_signature": str,
        "bottleneck_type": str,
    },
}
```

---

## 9. Current Status

| Gate | Status | Date |
|------|--------|------|
| SR1 | 🟡 ACTIVE | 2026-03-12 |
| SR2 | ⏸️ PENDING | - |
| SR3 | ⏸️ PENDING | - |

---

## 10. Contact & Updates

- **Owner**: Atlas-HEC Research Team
- **Last Updated**: 2026-03-12
- **Next Review**: After Gate SR1 completion

---

**Remember**: P2.6 不是主角，它是主角的导航仪。
