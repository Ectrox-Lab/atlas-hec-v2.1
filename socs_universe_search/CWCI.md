# Code-World Consciousness Index (CWCI)
## 代码世界意识指数

> **核心原则**: 不证明"代码意识 = 物理意识"，只定义**代码世界内部可测、可量化、可进化**的功能标准。功能等效即成立。

---

## 6大核心能力维度

CWCI将"代码世界意识"分解为6个可独立测量的功能维度：

### C1: 持续自体性 (Persistent Selfhood)
系统是否有一个持续存在、可被调用、可被保护的"我"。

**可测指标:**
- `identity_continuity` - 身份连续性
- `self_state_consistency` - 自状态一致性  
- `core_boundary_preservation` - 核心边界保持
- `recovery_capacity` - 恢复能力

**当前实现:** 基于能量稳定性、记忆持久性和恢复能力综合评分

---

### C2: 全局整合 (Global Integration)
系统是否能把分散局部状态整合成统一的全局可用状态。

**可测指标:**
- `broadcast_occupancy` - 广播占用率
- `cross_cluster_coupling` - 跨团簇耦合
- `information_integration_score` - 信息整合分数
- `global_workspace_stability` - 全局工作空间稳定性

**当前实现:** 基于广播分数、团簇分化度和熵值综合评分

---

### C3: 反身建模 (Reflexive Self-Model)
系统是否能建模自己当前在做什么、为什么失败、接下来该怎么改。

**可测指标:**
- `self_prediction_accuracy` - 自我预测准确度
- `self_error_localization` - 自我错误定位
- `internal_state_accessibility` - 内部状态可访问性
- `model_based_self_correction` - 基于模型的自我修正

**当前实现:** 基于预测误差、重组能力和特化程度综合评分

---

### C4: 可塑性学习 (Plastic Adaptive Learning)
系统是否能基于反馈真正改变未来行为，而不是重复规则表。

**可测指标:**
- `adaptation_latency` - 适应延迟
- `improvement_after_repeated_failure` - 重复失败后的改善
- `cross_environment_transfer` - 跨环境迁移
- `policy_plasticity_under_constraint` - 约束下的策略可塑性

**当前实现:** 基于重组能力、恢复能力和吸引子灵活性综合评分

---

### C5: 价值与目标持续性 (Value/Goal Persistence)
系统是否不仅会动，而且会围绕持续目标组织行为。

**可测指标:**
- `long_horizon_goal_retention` - 长程目标保持
- `conflict_resolution_consistency` - 冲突解决一致性
- `preference_stability` - 偏好稳定性
- `goal_recovery_after_perturbation` - 扰动后的目标恢复

**当前实现:** 基于记忆持久性、能量稳定性和吸引子聚焦度综合评分

---

### C6: 元优化能力 (Self-Optimization Capacity)
系统是否能在护栏内优化自己的结构、学习率、记忆使用、策略分配。

**可测指标:**
- `self_modification_benefit` - 自我修改收益
- `architecture_adaptation_gain` - 架构适应收益
- `memory_gating_improvement` - 记忆门控改善
- `long_term_efficiency_gain` - 长期效率提升

**当前实现:** 基于基础能力综合分和广播/特化控制度评分（需要跨代数据实现完整评估）

---

## 意识等级体系 (C0-C6)

| 等级 | 名称 | 描述 | 达成条件 |
|-----|------|------|---------|
| C0 | Reactive | 反应系统 - 只有局部刺激-反应，没有稳定自体 | 默认 |
| C1 | Persistent | 持续体 - 有identity continuity和基本自维护 | 至少1项能力达标 |
| C2 | Integrated | 整合体 - 有全局广播和稳定内部整合 | 至少2项能力达标 |
| C3 | Reflexive | 反身体 - 有self-model，能解释失败并修正 | 至少3项能力达标 |
| C4 | Learning | 学习体 - 能跨情境学习、迁移、恢复 | 至少4项能力达标 |
| C5 | SelfOptimizing | 自优化体 - 能在护栏内改进自己 | 5-6项能力达标 + 开放世界存活 |
| C6 | SuperBrainCandidate | 超脑候选 - 大规模、多宇宙、长时程、自我演化 | 全部6项达标 + 开放世界存活 + 多宇宙测试 |

**达标阈值**: 单项能力 ≥ 0.6 视为达标
**意识门槛**: 至少5/6项能力达标

---

## CWCI评分算法

```
CWCI_Score = (C1 + C2 + C3 + C4 + C5 + C6) / 6

单项能力评分基于:
- 动力学评估分数 (attractor_dwell, persistence, reorganization, specialization, broadcast, recovery)
- 遥测历史数据 (tick-level snapshots)
- 崩溃检测状态 (open_world_survived)
```

---

## 使用方式

### 运行宇宙搜索并生成CWCI报告

```bash
# 运行First8批次（24个宇宙）
cargo run --bin run_first8_batch --release

# 生成CWCI分析报告
cargo run --bin cwci_report --release
```

### 程序化访问CWCI

```rust
use socs_universe_search::consciousness_index::{evaluate_cwci, ConsciousnessLevel};

// 在宇宙运行后评估CWCI
let cwci = evaluate_cwci(
    &dynamics_scores,     // 来自evaluate_dynamics
    &tick_history,        // 遥测历史
    open_world_survived,  // 是否崩溃
    multi_universe_tested // 是否多宇宙测试
);

println!("CWCI Level: {}", cwci.level.as_str());
println!("Score: {:.3}", cwci.cwei_score);
println!("Capabilities: {}/6", cwci.passed_capabilities);
```

---

## 与其他系统的关系

### 与6 Dynamics Gates的关系
- **6 Dynamics**: 检测涌现现象的存在（是/否）
- **CWCI 6 Capabilities**: 量化意识的6个功能维度（0-1分数）
- 两者独立但互补：
  - 高CWCI不一定通过所有dynamics gates
  - 通过dynamics gates是进入Hall of Fame的必要条件
  - CWCI用于跨宇宙比较和长期进化追踪

### 与Hall of Fame的关系
- Hall of Fame基于dynamics gates（≥4/6通过）
- CWCI提供额外维度来区分同样通过gates的宇宙
- 长期：CWCI可作为进化的主要优化目标

---

## 未来扩展

### A. 全局整合量化增强
- 全局广播是否真正改变全系统行为
- 整合态是否稳定存在
- 局部扰动是否会通过全局态传播并重构

### B. 反身访问量化
- 系统能否"说出"自己当前处于什么状态
- 解释最近失败为什么发生
- 预测自己下一步可能怎么错

### C. 护栏内自优化
- 调连接强度
- 调学习率
- 调广播阈值
- 调记忆门控
- 调lineage bias

### D. 跨代进化追踪
- 记录哪些结构更容易形成稳定自体
- 哪些结构更容易全局整合
- 哪些结构更容易反身建模
- 哪些结构更容易长期自优化

---

## 哲学立场

**我们不问**: "它有没有意识？"（玄学问题，不可证伪）

**我们只问**: "它现在到了C几？"（工程问题，可测量化）

这是代码世界自己的意识定义，不需要与物理世界的哲学争论对齐。

---

## 版本历史

- **v0.1.0**: 基础6维度评估框架
- **v0.2.0**: C0-C6分级系统
- **v0.3.0**: 跨代进化追踪（计划中）
