# L5 Architecture Design: Multi-task Inheritance

**状态**: DESIGN PHASE  
**版本**: v0.1-draft  
**日期**: 2026-03-15  
**前置条件**: L4-v2 CERTIFIED (9cd76cc)

---

## 1. L5 核心问题

### 1.1 问题陈述

> **Can Task A's inheritance package improve Task B's performance, without being task leakage, memorization, or shared heuristics?**

### 1.2 与L4的关键区别

| 维度 | L4 (单任务) | L5 (多任务) | 风险等级 |
|------|------------|-------------|----------|
| **Inheritance目标** | 单一任务优化 | 跨任务迁移 | 🔴 极高 |
| **Control Group** | 同任务对照 | 跨任务对照 | 🔴 极高 |
| **Leakage风险** | 任务内污染 | 任务间污染 | 🔴 极高 |
| **Success Metric** | Control Gap | **Transfer Gap** | 🟡 新指标 |
| **失败模式** | Exploration bias | **Catastrophic forgetting** | 🔴 致命 |

---

## 2. L5 最小实验骨架 (Pilot Protocol)

### 2.1 任务选择 (3个异质任务)

| 任务 | 领域 | 选择理由 |
|------|------|----------|
| **Task A** | Code / Tool-use | 结构化输出，精确验证 |
| **Task B** | Math / Symbolic reasoning | 抽象推理，与Code异质 |
| **Task C** | Planning / Scheduler control | 时序决策，第三类认知 |

**选择原则**: 任务间结构差异足够大，容易暴露negative transfer

### 2.2 实验组设计 (最小4组)

| 组别 | 描述 | 目的 |
|------|------|------|
| **B-base** | Task B无inheritance | B的baseline |
| **B-self** | Task B使用自身inheritance | 确认单任务继承仍有效 |
| **A→B transfer** | Task B使用Task A的package | **核心验证组** |
| **Sham-transfer** | Task B使用无关package/bias=0 | 防止"任何package都抬分" |

### 2.3 核心指标 (L5专用)

| 指标 | 定义 | 成功阈值 |
|------|------|----------|
| **self_gap_pp** | B-self vs B-base | ≥8pp (不低于L4-v2下限) |
| **transfer_gap_pp** | A→B vs B-base | >0且跨seed可重复 |
| **negative_transfer_rate** | 任务A知识损害B的比例 | 不显著(p>0.05) |
| **source_leakage_rate** | 源任务信息直接穿透 | <5% |
| **backward_compatibility** | Task A baseline不恶化 | 保持 |
| **family_diversity_post_transfer** | Transfer后family分布 | ≥6 unique families |

---

## 3. 风险分析与熔断条件

### 3.1 L5四大风险

| 风险 | 描述 | 检测方法 | 熔断条件 |
|------|------|----------|----------|
| **Catastrophic Forgetting** | 新任务覆盖旧任务记忆 | Task A性能vs L4基线 | Task A性能下降>10% |
| **Negative Transfer** | 任务A知识损害任务B | A→B组 vs B-base显著劣化 | Transfer Gap <0 |
| **Source Leakage** | 任务间信息污染 | Sham-transfer vs A→B对比 | Source Leakage >5% |
| **Shared Heuristics** | 误判表面共享为继承 | 跨任务mechanism分析 | 无独特mechanism激活 |

### 3.2 熔断器设计

```yaml
circuit_breakers:
  catastrophic_forgetting:
    metric: task_a_performance_drop_percent
    max_threshold: 10
    action: FREEZE_L5_REVERT_TO_L4
    
  negative_transfer:
    metric: transfer_gap_pp
    min_threshold: 0
    action: STOP_TASK_PAIR_INVESTIGATE
    
  source_leakage:
    metric: source_leakage_rate
    max_threshold: 0.05
    action: AUDIT_PACKAGE_SCHEMA_FIREWALL
    
  overfitting:
    metric: cross_seed_variance
    max_threshold: 0.15
    action: INCREASE_SAMPLE_SIZE_REDUCE_PERTURBATION
```

---

## 4. Package Schema v3 (Multi-task)

### 4.1 扩展字段

```json
{
  "package_version": "3.0-multi-task",
  "source_task": "task_a_code",
  "target_tasks": ["task_b_math", "task_c_planning"],
  
  "task_specific_mechanisms": {
    "task_a": ["code_structure_recognition", "tool_chain_optimization"],
    "task_b": ["symbolic_abstraction", "proof_step_pruning"],
    "task_c": ["temporal_dependency_tracking", "resource_contention_resolution"]
  },
  
  "transfer_candidates": {
    "task_a_to_b": [
      {"mechanism": "hierarchical_decomposition", "transfer_probability": 0.75},
      {"mechanism": "error_recovery_sequence", "transfer_probability": 0.60}
    ],
    "task_a_to_c": [
      {"mechanism": "state_space_pruning", "transfer_probability": 0.45}
    ]
  },
  
  "isolation_firewall": {
    "blocked_patterns": ["task_specific_syntax", "domain_vocabularies"],
    "allowed_abstractions": ["control_flow", "dependency_graphs", "optimization_strategies"]
  }
}
```

### 4.2 Task Isolation机制

| 层级 | 隔离策略 | 验证方法 |
|------|----------|----------|
| **Data** | 物理隔离不同任务训练数据 | Hash verification |
| **Mechanism** | Task-specific mechanism registry | Activation logging |
| **Package** | Source tagging + firewall rules | Leakage detection audit |
| **Evaluation** | Cross-task control groups | Sham-transfer validation |

---

## 5. 执行计划

### 5.1 Phase 1: Pilot (24小时)

- [ ] Task A/B/C baseline measurement
- [ ] B-self inheritance validation
- [ ] Single A→B transfer attempt
- [ ] Basic leakage detection

**产出**: L5_PILOT_RESULTS.md

### 5.2 Phase 2: Bi-directional (48小时)

- [ ] A→B and B→A transfer
- [ ] A→C and C→A transfer  
- [ ] B→C and C→B transfer
- [ ] Negative transfer analysis

**产出**: L5_BIDIRECTIONAL_ANALYSIS.md

### 5.3 Phase 3: Full Matrix (1周)

- [ ] All 6 directed task pairs
- [ ] Multi-hop transfer (A→B→C)
- [ ] Catastrophic forgetting long-term test
- [ ] Backward compatibility verification

**产出**: L5_FULL_CERTIFICATION.md

---

## 6. 成功标准 (L5 Certification)

### 6.1 必须全部满足

| 标准 | 阈值 | 理由 |
|------|------|------|
| Self-gap maintained | ≥8pp | 不丢失L4能力 |
| Transfer gap positive | >0pp, repeatable | 真正跨任务迁移 |
| No catastrophic forgetting | Task A性能不下降 | 持续改进而非替换 |
| Source leakage controlled | <5% | 防止污染 |
| Negative transfer rare | <20% task pairs | 大部分迁移有益 |

### 6.2 分级认证

- **L5-A (Full)**: 所有6个task pairs正向transfer
- **L5-B (Partial)**: 3+ task pairs正向，无negative
- **L5-C (Limited)**: 1-2 task pairs正向，需domain-specific调整
- **L5-X (Failed)**: 无consistent transfer或存在catastrophic forgetting

---

## 7. 与L4-v2的连续性

### 7.1 保留机制

- 128-seed discipline
- Pool A-F stratification
- Anti-leakage penalty system
- Circuit breaker monitoring

### 7.2 升级机制

- Control Gap → Transfer Gap
- Single-task mechanism map → Cross-task transfer candidates
- Pool E (control) → Multi-task control matrix
- Family diversity → Task-specific family survival

---

## 8. 禁止事项 (L5纪律)

1. **禁止**: 将L4-v2成功外推为L5必然成功
2. **禁止**: 未验证single-task inheritance仍有效就测transfer
3. **禁止**: 忽略sham-transfer control直接报告transfer gap
4. **禁止**: 发现catastrophic forgetting仍继续实验
5. **禁止**: 将shared heuristics包装为transfer success

---

**设计批准**: 待Atlas-HEC Research Committee  
**下一步**: L5_PILOT_PROTOCOL.md细化 → 24小时内Pilot执行

---

*"承认无知比假装全知更有价值。L4-v2是数据，不是胜利。L5的失败是可能的，甚至是预期的。但L5的尝试是必要的。"*
*— Atlas Protocol v2.1*
