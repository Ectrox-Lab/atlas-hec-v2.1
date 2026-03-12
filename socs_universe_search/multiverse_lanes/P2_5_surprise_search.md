# P2.5 - Surprise Search Lane (多元宇宙/阿卡西惊喜发现)

## 目标
从多宇宙并行演化 + 阿卡西跨宇宙学习中，自动冒出"你没预设过"的候选结构。

## 资源占比
**15%** (不挑战主线，只负责发现)

## 核心机制

### 1. 随机结构组合空间
不局限于命名家族(Octopus/Bee/Ant)，而是混洗参数维度：

| 维度 | 范围 | 说明 |
|-----|------|------|
| local_autonomy | 0.1-0.9 | 局部自治强度 |
| broadcast_sparsity | 0.01-0.20 | 广播稀疏度 |
| division_strength | 0.0-0.8 | 分工强度 |
| lineage_bias | 0.0-0.5 | 谱系偏置 |
| culling_style | soft/hard/none | 淘汰风格 |
| memory_gating | L1/L2/L3/混合 | 记忆门控 |
| hierarchy_depth | 0-4 | 层级深度 |
| coupling_topology | small_world/random/regular | 耦合拓扑 |

### 2. 多宇宙并行筛选 (128 universes)

```
Universe Grid: 25×25×8 = 5000 agents max per universe
Total: 128 universes × variable sizes

Stress Profiles per Universe:
├── ResourceScarcity (20%)
├── FailureBurst (20%)
├── HighCoordinationDemand (20%)
├── RegimeShiftFrequent (15%)
├── SyncRiskHigh (15%)
└── StableLowStress (10% control)
```

### 3. 阿卡西记忆 - 只保留结构摘要

**不保留**: 具体动作答案
**保留**:
- 哪类结构组合在什么压力下活得更好
- 哪种 lineage 修正最有效  
- 哪种 failure signature 最常见
- 跨宇宙的 emergent pattern clusters

### 4. 惊喜提名机制

当发现以下情况时，自动提名新候选：

```python
SURPRISE_TRIGGERS = {
    "novelty": "CWCI > 0.65 且不在已知家族参数空间内",
    "resilience": "在3种以上stress场景都保持 CWCI > 0.60",
    "emergence": "出现未预设的集体行为模式",
    "lineage_jump": "谱系突变带来>20%性能提升",
    "cross_stress_transfer": "在某stress下学到的能力迁移到另一stress"
}
```

## 禁止事项
- ❌ 直接修改主线架构
- ❌ 直接宣布新冠军
- ❌ 吃掉主线资源(严格15%)

## 产出物
- `surprise_candidates.jsonl` - 惊喜候选提名
- `structure_signatures.json` - 结构签名聚类
- `failure_clusters.json` - 失败模式聚类
- `akashic_digest.json` - 阿卡西跨宇宙摘要

## 与主线关系
```
P0 (OctopusLike) ←────── 主线收敛 (60%)
        ↑
        └────────────────  Surprise提名可能进入P1挑战
        
P2.5 (Surprise Lane) ─── 持续扫描结构空间 (15%)
        ↓
        └────────────────  发现 → 提名 → P1验证 → 可能晋升
```
