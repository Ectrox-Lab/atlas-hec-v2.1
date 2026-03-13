# Restart Readiness Campaign - P2.6

**目标**: 主动制造重启条件，让 SR1 重启从"口头可能"变成"数据就绪"  
**周期**: 3 周 (2026-03-13 ~ 2026-04-03)  
**负责人**: Jordan Smith  
**审批**: Dr. Sarah Williams

---

## 核心原则

- **不是重跑 SR1**，而是补齐重启前提
- **数据驱动**，每项产出必须可量化
- **schema 先行**，不等数据自然提醒

---

## 重启条件检查清单 (来源: P2_6_SCHEMA_REDESIGN_BRIEF.md)

| # | 条件 | 当前状态 | 目标 | 负责 |
|---|------|----------|------|------|
| 1 | Scale-aware fingerprint schema | ❌ 未写 | 完成 v1.0 spec | Week 1 |
| 2 | Baseline dataset (4+ weeks) | ⚠️ 1 周 | 4 周跨 scale 数据 | Week 3 |
| 3 | Valid seed-spike candidates | ⚠️ 部分 | ≥5 明确 spike | Week 2 |
| 4 | Clear SR hypothesis | ❌ 模糊 | 具体 mechanism | Week 2 |

---

## Workstream 1: Schema Redesign Spec (Week 1)

**产出**: `P2_6_SCALE_AWARE_SCHEMA_v1.0.md`

### 必须定义的维度

```yaml
# 1. Scale-Normalized Metrics
metrics:
  raw_cwci: "原始测量值"
  
  scale_normalized_cwci:
    formula: "(cwci - baseline_4x) / expected_6x_variance"
    baseline_4x: "同 seed 4x 基线"
    expected_6x_variance: "从 envelope 模型获取"
    interpretation: 
      - "> 0: 优于 6x 预期"
      - "= 0: 符合 6x 预期"
      - "< 0: 差于 6x 预期 (可能 SR 失效)"

  degradation_attribution:
    scale_component: "从 4x→6x 包络模型计算的预期值"
    sr_component: "残差，即 SR 真实效果"

# 2. Seed-Stratified Analysis
seed_classification:
  stable: "7/8 seeds，预期 CWCI ~0.64"
  degradable: "1/8 seeds，可能 dip 到 ~0.57"
  
analysis_requirement: "必须分别报告两类 seed 的 SR 效果"

# 3. Time-Resolved Comparison
comparison_windows:
  pre_degradation: "ticks 0-500，所有 seeds"
  during_degradation: "seed-specific，动态窗口"
  post_failover: "failover 后，比较 SR vs baseline 恢复速度"
```

### 必须解决的混淆问题

| 混淆来源 | 解决方案 |
|----------|----------|
| R4/R5/R6 数据被视为不同区域 | 增加 scale 维度，同一 universe 跨 scale 比较 |
| 6x 自然 degradation vs SR 效果 | 用 4x baseline 归一化，分离 scale 成分 |
| Averaging masks SR effect | 按 seed 类型分层，分别分析 |

---

## Workstream 2: Baseline Dataset (Week 1-3)

**目标**: OctopusLike 跨 scale 固定样本 ≥10

### 采样计划

| Week | 任务 | 样本数 | 存储 |
|------|------|--------|------|
| 1 | 4x 固定基线 (8 seeds, 3000 ticks) | 8 | `baseline/4x/week1/` |
| 1 | 6x 固定基线 (8 seeds, 3000 ticks) | 8 | `baseline/6x/week1/` |
| 2 | 重复采样 (验证稳定性) | 8+8 | `baseline/*/week2/` |
| 2 | 压力测试期间同步采样 | 8+8 | `baseline/*/stress/` |
| 3 | 补全到 ≥10 per scale | 10+10 | `baseline/*/final/` |

### 统一字段

```yaml
required_fields:
  - seed_id
  - scale_factor
  - tick
  - cwci
  - population
  - cooperation_rate
  - broadcast_count
  - message_latency
  - failover_events
  - degraded_periods
```

---

## Workstream 3: Seed-Spike Registry (Week 1-2)

**目标**: ≥5 个明确 spike / fail / rejected 样本

### 主动扫描计划

在研究环境 (8x allowed) 批量跑 seeds:

```bash
# 扫描范围: seeds 100-200
# 每个 seed: 8x, 3000 ticks
# 记录: high_variance, low_pass_rate, failover_precursor
```

### Registry 格式

```yaml
seed_spike_registry:
  entry_id: "SSP_001"
  seed_id: 127
  discovery_date: "2026-03-15"
  discovery_method: "active_scan_8x"
  
  spike_characteristics:
    variance_profile: "high_autonomy_low_hierarchy"
    cwci_pattern: "oscillating_decay"
    population_dynamics: "boom_bust"
    
  reproducibility:
    8x_reproduced: true
    6x_partial: true
    4x_stable: false
    
  classification:
    - " fragile_combination"
    - " high_broadcast_saturation"
    - " coordination_overload_candidate"
    
  usage:
    - "avoid_in_surprise_search"
    - "sr_test_candidate_if_schema_v2"
```

### Spike 类别定义

| 类别 | 特征 | 处理方式 |
|------|------|----------|
| Fragile combination | autonomy ↑ hierarchy ↓ | 避免在搜索中使用 |
| Broadcast saturation | message_count > threshold | 带宽测试候选 |
| Coordination overload | decision_latency ↑ | SR 潜在受益 |
| Population volatility | σ(population) > threshold | 稳定性测试 |

---

## Workstream 4: Challenger Family (Week 2-3)

**目标**: ≥3 个真实 OQS 候选，同一 schema 指纹

### 候选来源

| 来源 | 预期数量 | 优先级 |
|------|----------|--------|
| P2.5 历史 rejected | 2-3 | P0 |
| 主动变异 OctopusLike | 2 | P1 |
| 文献/外部 benchmark | 1-2 | P2 |

### 候选要求

```yaml
champion: OctopusLike
  primary: true
  validated_scales: [4, 6, 8]
  
challengers:
  - name: "OQS_Candidate_A"
    source: "P2.5_rejected_variance_based"
    fingerprint_status: "pending"
    structural_difference: "TBD"
    
  - name: "OQS_Candidate_B"
    source: "OctopusLike_variant_higher_broadcast"
    fingerprint_status: "pending"
    structural_difference: "TBD"
    
  - name: "OQS_Candidate_C"
    source: "literature_benchmark_adapted"
    fingerprint_status: "pending"
    structural_difference: "TBD"
```

### 指纹统一 schema

所有候选必须使用同一指纹出图:

```yaml
fingerprint_dimensions:
  - architecture_type
  - communication_pattern
  - decision_mechanism
  - memory_structure
  - scale_response_profile
  
comparison_matrix:
  OctopusLike: "baseline"
  Candidate_A: "vs baseline"
  Candidate_B: "vs baseline"
  Candidate_C: "vs baseline"
```

---

## Workstream 5: SR Hypothesis 具体化 (Week 2)

**产出**: 具体 mechanism，不是模糊"可能有用"

### Hypothesis 模板

```
Given:
  - Scale factor 6x
  - Seed type: degradable (1/8)
  - Phase: during_degradation
  
When:
  - Specialist routing activates
  
Then:
  - CWCI recovery speed improves by X%
  - Failover frequency reduces by Y%
  - Stability increases by Z%
  
Compared to:
  - Baseline 6x without SR
  
Measured by:
  - scale_normalized_cwci (Workstream 1)
```

### 必须回答的问题

| 问题 | 答案 |
|------|------|
| SR 对谁有用？ | degradable seeds / all seeds / specific pattern |
| SR 在什么时候有用？ | pre/during/post degradation |
| SR 的作用机制？ | reduce failover / improve recovery / prevent degradation |
| 如何测量 SR 效果？ | scale_normalized_cwci_delta |

---

## 周度检查点

### Week 1 Checkpoint

- [ ] Schema v1.0 spec 完成
- [ ] 4x/6x baseline 采样开始
- [ ] Seed scan 启动
- [ ] Challenger 候选清单确认

### Week 2 Checkpoint

- [ ] ≥3 seed-spike entries
- [ ] Baseline 样本 ≥6 per scale
- [ ] ≥2 challenger fingerprints 完成
- [ ] SR hypothesis 具体化

### Week 3 Checkpoint

- [ ] Baseline 样本 ≥10 per scale
- [ ] ≥5 seed-spike entries
- [ ] ≥3 challenger fingerprints 完成
- [ ] All restart conditions: GO/NO-GO

---

## 成功标准

**3 周后必须满足:**

- [ ] Scale-aware schema v1.0 已定义
- [ ] OctopusLike baseline ≥10 per scale
- [ ] Seed-spike registry ≥5 entries
- [ ] Challenger family ≥3 candidates
- [ ] SR hypothesis 具体到 mechanism

**决策点**: Week 3 结束，Research Lead 决定:

- ✅ **GO**: SR1 重启，用新 schema
- ❌ **NO-GO**: 终止 P2.6，资源转投其他线

---

## 资源需求

| 资源 | 数量 | 用途 |
|------|------|------|
| 8x 研究环境 | 1 instance | seed-spike scan |
| 4x/6x 采样 slot | 各 10 runs | baseline accumulation |
| Compute | ~500 CPU-hours | candidate fingerprinting |
| Storage | ~100GB | baseline + registry |

---

**启动审批**: _______________ (Dr. Sarah Williams)  
**启动日期**: _______________
