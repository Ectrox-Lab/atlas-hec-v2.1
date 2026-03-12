# Self-Organizing Cognitive Substrate (SOCS)

## Vision
从局部简单规则出发，逐层长出复杂认知能力的可扩展基底。

## Architecture

### L0: Micro-Unit (细胞/神经元层级)
每个单元只保留最小状态：
- activation
- energy
- local memory trace
- prediction error
- plasticity state

能力：
- 接收局部输入
- 更新自身状态
- 向邻居发送低带宽信号
- 按局部规则调整连接强度

### L1: Meso-Cluster (局部团簇)
单元组形成局部稳定结构：
- 稳定attractors
- 工作记忆样状态
- 局部目标维持
- 竞争/协调

### L2: Global Workspace (共享场)
不从外部写入，而从下层涌现：
- 哪些团簇占据全局带宽
- 哪些状态被广播
- 哪些误差驱动重构

## Design Principles

1. **少规则，不少约束** - 有护栏，无环境特定策略表
2. **局部可学习，全球不直控** - 单元只看局部状态
3. **学习来自反馈，不来自人工答案** - 不给手写策略
4. **先长结构，再长能力** - 先验证动力学现象
5. **自优化从受限自改开始** - 固定护栏内自调参数

## Verification Goals (Not Benchmark Scores)

验证6个动力学现象：
1. ✅ 稳定attractors
2. ✅ 记忆persistence
3. ✅ regime shift后重组
4. ✅ cluster specialization
5. ✅ global broadcast emergence
6. ✅ failure → recovery

## Directory

```
self_organizing_substrate/
├── README.md
├── src/
│   ├── micro_unit.rs      # L0: 微单元
│   ├── plasticity.rs      # 可塑性规则
│   ├── cluster_dynamics.rs # L1: 团簇动力学
│   ├── global_workspace.rs # L2: 全局工作空间
│   └── substrate_open_world_bridge.rs # 与Bio-World连接
└── tests/
    ├── test_attractor_formation.rs
    ├── test_memory_persistence.rs
    └── test_broadcast_emergence.rs
```

## Relation to Existing Work

现有工作作为基础设施：
- PriorChannel → 约束和护栏
- Three-Layer Memory → 记忆架构参考
- Bio-World v19 → 环境耦合测试床
- Phase 2 Validation → 生存能力基线

但它们不再是本体。SOCS是新的核心。
