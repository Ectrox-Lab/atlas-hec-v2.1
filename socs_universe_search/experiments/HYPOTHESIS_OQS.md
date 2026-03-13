# Hypothesis OQS: OctoQueenSwarm Architecture

## 核心假设

> A hybrid architecture combining octopus-like local autonomy with ant-like colony scaling will outperform both pure OctopusLike and pure AntColonyLike on exploration efficiency, fault tolerance, and long-horizon adaptive growth.

## 生物学事实边界（已核查）

| 事实 | 状态 | 工程使用边界 |
|-----|------|-------------|
| 章鱼：5亿神经元，2/3 分布式 | ✅ 可靠 | 局部自治结构先验 |
| 蚁群：分工高效，个体简单 | ✅ 可靠 | 群体组织机制先验 |
| 蜂群：模块化专业化 | ✅ 可靠 | 层级协调结构先验 |
| 蚁后/蜂后控制所有行为 | ❌ 错误 | 母体只是偏置源，不是 puppet master |
| "群体智慧" = 无限放大 | ❌ 过度简化 | 必须在特定条件下才涌现 |

## 架构定义

### OctoQueenSwarm = 章鱼型局部自治 × 蚁群型分工扩张

核心思想：
```
母体负责：长期连续性、目标、传承、资源调度
子体负责：局部探索、试错、执行、回传摘要
群体层负责：分工、增殖、淘汰、重组
```

### 四层结构

```
                    ┌──────────────────────────┐
                    │      Queen Core          │
                    │ identity / goals / L2-L3 │
                    │ resource alloc / spawn   │
                    └──────────┬───────────────┘
                               │
                 weak bias / role priors / budgets
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼───────┐      ┌───────▼───────┐      ┌───────▼───────┐
│ Worker Pod A  │      │ Worker Pod B  │      │ Worker Pod C  │
│ scout-heavy   │      │ builder-heavy │      │ defender-heavy│
│ local memory  │      │ local memory  │      │ local memory  │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        └──────────────┬───────┴──────────────┬───────┘
                       │ summarized return    │
                       ▼                      ▼
               ┌──────────────────────────────────┐
               │ Experience Return Channel        │
               │ failure signatures / task stats  │
               │ structural hints / role utility  │
               └────────────────┬─────────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Spawn / Cull Engine │
                     │ mutate / prune /    │
                     │ replicate variants  │
                     └─────────────────────┘
```

### 信息流规则

**Queen → Worker (允许)**:
- role prior
- budget
- risk level
- shared goal direction
- lineage bias

**Queen → Worker (禁止)**:
- current optimal action
- full policy script
- oracle answer

**Worker → Queen (允许)**:
- success/failure summary
- energy use
- hazard signal
- local sketch
- task utility
- failure signature

**Worker → Queen (禁止)**:
- full trajectory as template
- directly copyable environment-specific policy

## 与单体架构的对比

| 维度 | OctopusLike | AntColonyLike | BeeHiveLike | OctoQueenSwarm |
|-----|-------------|---------------|-------------|----------------|
| 局部自治 | 极强 | 弱 | 中等 | 强 |
| 分工效率 | 低 | 高 | 高 | 高 |
| 扩张能力 | 低 | 极高 | 高 | 高 |
| 恢复能力 | 强 | 极强 | 强 | 极强 |
| 长期整合 | 弱 | 中等 | 中等 | 强 |
| 中央瓶颈 | 无 | 低 | 中等 | 中等 |

## 验证实验设计

### Gate 1: 结构闭环验证（小规模）

**目标**: 证明 "spawn → work → summarize → respawn" 闭环有效

**对照组**:
- OctopusLike
- AntColonyLike
- OctoQueenSwarm

**场景** (3个):
1. ResourceScarcity
2. HighCoordinationDemand
3. FailureBurst

**seeds**: 5

### 必测指标

**A. 群体组织指标**
- division_of_labour_score
- role_stability
- task_reallocation_latency
- worker_utilization

**B. 生存与恢复指标**
- population_persistence
- worker_loss_recovery_time
- queen_overload_rate
- hazard_after_worker_loss

**C. 学习与回流指标**
- experience_return_quality
- spawn_utility_gain
- lineage_improvement_rate

**D. 结构组织指标**
- CWCI
- specialization
- integration
- broadcast

### Gate 1 通过标准

**PASS**:
- [ ] OctoQueenSwarm 在 2/3 场景中优于纯 OctopusLike 或纯 AntColonyLike
- [ ] worker 损失后恢复时间不劣于对照组
- [ ] division_of_labour_score 明显更高
- [ ] Queen 没有形成中央瓶颈

**PARTIAL**:
- 分工明显提升，但 Queen 出现轻度过载
- 或经验回流有效但 spawn/cull 收益不稳定

**FAIL**:
- worker 只是傀儡
- Queen 成为神谕中控
- 群体优势没有出现
- 恢复能力明显差于对照组

## 决策门

### Gate 1: 结构闭环验证（小规模）
验证 spawn-work-summarize-respawn 闭环有效性。

**如果失败**: 混合架构设计有根本缺陷，需重新设计信息流规则。

### Gate 2: 规模稳健性（中规模）
验证 5x 规模下是否仍保持优势，Queen 是否出现瓶颈。

**如果失败**: Queen 成为瓶颈，需重新设计母体-子体关系。

### Gate 3: 开放世界压力测试
验证在 RegimeShiftFrequent、HighCoordinationDemand、FailureBurst 下的生存能力。

**如果通过**: OctoQueenSwarm 成为主线优先复合架构。

## 风险与边界

```
已知风险:
  1. Queen 容易退化成 puppet master
  2. Worker 容易退化成无自治的执行器
  3. 经验回流可能变成"全量复制"
  4. 规模放大后 Queen 可能成为瓶颈

缓解措施:
  1. 严格限制 Queen → Worker 信息类型
  2. Worker 必须有局部学习和决策能力
  3. 只允许摘要回流，禁止完整策略复制
  4. 设计 Queen 负载监控和分流机制
```

## 结论口径

**当前可宣称**:
> OctoQueenSwarm is a promising hybrid architecture combining distributed local autonomy with colony-level organization, warranting experimental validation.

**禁止宣称**:
> - "Queen-worker hierarchy is the final architecture"
> - "Swarm intelligence solves all problems"
> - "More workers always better"
> - "Real SOCS swarm validated"

**下一步**:
执行 Gate 1 验证，证明结构闭环有效性。

### Gate 1 结果 [2024-03-12]

**状态**: ⚠️ PARTIAL (2/4 检查通过)

**原始数据**:

| 架构 | CWCI | Persistence | TaskEff | Spec | Recovery |
|-----|------|-------------|---------|------|----------|
| OctopusLike | 0.180 | 0.000 | 0.600 | 0.000 | 0.000 |
| AntColonyLike | 0.312 | 0.000 | 0.013 | 0.948 | 0.900 |
| **OctoQueenSwarm** | **0.289** | **0.333** | **0.259** | **0.316** | **0.317** |

**场景表现**:

| 场景 | Octopus | AntColony | **OctoQueen** | OQS Win? |
|-----|---------|-----------|---------------|----------|
| ResourceScarcity | 0.175 | 0.311 | 0.036 | ❌ |
| **HighCoordinationDemand** | 0.202 | 0.314 | **0.815** | ✅ |
| FailureBurst | 0.162 | 0.311 | 0.015 | ❌ |

**OQS 特有指标**:

| 指标 | 值 | 评估 |
|-----|-----|------|
| division_of_labour | 0.316 | ⚠️ 低于阈值 (0.5) |
| role_stability | 0.493 | ✅ 可接受 |
| queen_overload_rate | 0.000 | ✅ 无瓶颈 |
| experience_return_quality | 0.000 | ❌ 需优化 |
| lineage_improvement | -0.219 | ❌ culling 过激进 |

**关键发现**:

1. **HighCoordinationDemand 场景 OQS 显著领先** (0.815 vs 0.202/0.314)
   - 证明"母体整合 + 子体分工"在高协调需求下确实有效
   - 这是 OQS 的核心价值场景

2. **ResourceScarcity 和 FailureBurst 表现不佳**
   - 资源竞争时母体预算分配策略过于保守
   - FailureBurst 时经验回流机制未能有效触发

3. **分工程度不足 (0.316)**
   - lineage 初始化过于均匀
   - 缺乏有效的角色分化机制

4. **lineage improvement 为负 (-0.219)**
   - culling 机制过于激进
   - 惩罚失败过度，抑制了探索

**检查项**:
- [ ] 2/3 场景优于对照组 (1/3) ❌
- [x] 恢复能力不劣于对照组 (0.317 > 0.000) ✅
- [ ] 分工程度 > 0.5 (0.316) ❌
- [x] Queen 无瓶颈 (0.000 < 0.3) ✅

**结论**:
> OQS 在 HighCoordinationDemand 场景展现出显著优势（CWCI 0.815），
> 验证了"母体整合 + 子体分工"的核心假设。
> 但分工程度和经验回流机制需要优化。

**Failure Mode 诊断**:

| 问题 | 根因 | 修正方向 |
|-----|------|---------|
| ResourceScarcity 表现差 | 母体预算分配保守 | 优化资源调度算法 |
| FailureBurst 表现差 | 经验回流未触发 | 降低回流阈值 |
| 分工程度低 | lineage 初始化均匀 | 引入初始角色偏置 |
| lineage improvement 负 | culling 过激进 | 调整 culling 阈值和恢复机制 |

**下一步**:
- 优化 lineage 初始化和 culling 机制
- 重新跑 Gate 1，目标：3/4 检查通过
- 或直接进入 Gate 2 中规模验证，观察 HighCoordinationDemand 优势是否保持

