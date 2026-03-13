# 跨轮演化协议: Round k → Round k+1
## Cross-Round Evolution Protocol with Lineage Tracking

**版本**: v1.0  
**日期**: 2026-03-14  
**状态**: IMPLEMENTED (待验证)

---

## 核心结构: 6 → 128 → 6 → 128 迭代

```
Round k Input (6 elite candidates)
         ↓
    [Expansion Phase]
    - 父代克隆 + 邻域变异: 6 × 16 = 96
    - 两两重组交叉: C(6,2) × 8 = 120 → 取24
    - 随机移民注入: 8
         ↓
Round k Budget (128 seeds并行探索)
         ↓
    [Evaluation & Selection Phase]
    - NSGA-II多目标评分
    - Hall-of-Fame更新
    - 家族树追踪
         ↓
Round k Output (6 elite candidates for Round k+1)
```

---

## 三个必填字段 (Three Mandatory Fields)

### 字段1: 父代来源 (Parental Lineage)

每个新种子必须记录:

```json
{
  "seed_id": "R3_S047",
  "generation": 3,
  "parent_type": "mutation",     // mutation | crossover | immigrant
  "parent_ids": ["R2_E02"],      // 父代精英ID
  "mutation_operator": "P+1_T-1", // 具体变异操作
  "crossover_partner": null,      // 如为重组，记录另一方
  "lineage_depth": 7              // 追溯轮数
}
```

**变异操作符定义**:
- `P±n`: Persona depth 调整
- `T±n`: Transformation capacity 调整
- `M±n`: Memory layers 调整
- `D±n`: Diversity threshold 调整
- `SWAP`: 交换两个维度

### 字段2: 存活理由 (Survival Rationale)

晋级标准必须是以下之一或多维组合:

```json
{
  "candidate_id": "R3_E01",
  "survival_basis": {
    "primary": "stability",      // stability | efficiency | recovery | composite
    "stability_score": 0.94,     // drift < 0.3 持续时间
    "efficiency_score": 0.87,    // throughput / resource_ratio
    "recovery_score": 0.91,      // 从failure恢复速度
    "composite_rank": 1,         // NSGA-II帕累托前沿排名
    "dominates_count": 45        // 支配其他候选数量
  },
  "failure_archetype_resistance": {
    "octopus_like": "survived",
    "pulse_central": "survived",
    "delegation_chaos": "failed"  // 记录失败模式
  }
}
```

**存活理由分类**:
1. **stability**: 在高压下保持低drift
2. **efficiency**: 单位资源产出最大化
3. **recovery**: 故障后恢复能力
4. **composite**: 多目标帕累托最优

### 字段3: 家族延续性 (Family Continuity)

追踪架构家族在跨轮中的表现:

```json
{
  "family_id": "F_P2T3M3",       // 核心配置签名
  "family_age": 4,               // 连续存活轮数
  "generations": [
    {"round": 1, "rank": 3, "members": ["R1_E03"]},
    {"round": 2, "rank": 2, "members": ["R2_E01", "R2_E04"]},
    {"round": 3, "rank": 1, "members": ["R3_E01", "R3_E02", "R3_E05"]},
    {"round": 4, "rank": 1, "members": ["R4_E01", "R4_E03"]}
  ],
  "adaptation_trend": "improving", // improving | stable | declining
  "convergence_score": 0.89        // 家族内部一致性
}
```

**家族定义规则**:
- 核心配置签名: P{T}{M} (忽略D的微调)
- 家族成员: 配置在核心签名±1范围内的所有候选
- 延续判定: 连续3轮有成员进入top-6
- 收敛判定: 家族内部配置的average distance < threshold

---

## Round k → Round k+1 详细协议

### Phase 1: Expansion (6 → 128)

**输入**: Round k 的 top-6 精英候选 `[E01, E02, E03, E04, E05, E06]`

**生成规则**:

```python
def expand_elites_to_128(elites):
    seeds = []
    
    # 1. 邻域变异: 每个精英生成16个邻居 (96 total)
    for elite in elites:
        for i in range(16):
            mutation = select_mutation_operator(elite, i)
            child = apply_mutation(elite, mutation)
            child.lineage = {
                "parent_type": "mutation",
                "parent_ids": [elite.id],
                "mutation_operator": mutation
            }
            seeds.append(child)
    
    # 2. 重组交叉: C(6,2)=15 pairs, 每对生成~1-2个 (24 total)
    pairs = combinations(elites, 2)
    selected_pairs = weighted_sample(pairs, 24)
    for p1, p2 in selected_pairs:
        child = crossover(p1, p2)
        child.lineage = {
            "parent_type": "crossover",
            "parent_ids": [p1.id, p2.id]
        }
        seeds.append(child)
    
    # 3. 随机移民: 8个全局随机 (防止早熟收敛)
    for i in range(8):
        immigrant = random_global_config()
        immigrant.lineage = {
            "parent_type": "immigrant",
            "parent_ids": []
        }
        seeds.append(immigrant)
    
    assert len(seeds) == 128
    return seeds
```

**变异操作符选择策略**:
- 基于历史成功率动态调整权重
- 对表现好的维度减少变异幅度
- 对表现差的维度增加探索力度

### Phase 2: Parallel Exploration (128预算)

**执行**: 128 workers并行运行 heavy mode

**每种子记录**:
- runtime metrics (drift, throughput, recovery time)
- resource usage (CPU%, RAM, wall-clock time)
- failure mode (if any)

### Phase 3: Evaluation & Selection (128 → 6)

**NSGA-II多目标优化**:

目标函数 (最小化):
1. `f1 = avg_drift` (稳定性)
2. `f2 = 1/throughput` (效率)
3. `f3 = recovery_time` (恢复力)
4. `f4 = resource_cost` (资源消耗)

**选择规则**:
- 从帕累托前沿选前6
- 若前沿不足6，从第二前沿补充
- 确保多样性: 同一家族最多占2席

**Hall-of-Fame更新**:
```json
{
  "hof_version": 4,
  "all_time_best": {
    "config": "P2T3M3D1",
    "first_seen_round": 2,
    "survived_rounds": 3,
    "current_status": "active"
  },
  "retired_champions": [
    {"config": "P1T2M2D1", "dominated_in_round": 3}
  ]
}
```

### Phase 4: Family Continuity Assessment

**每轮结束计算**:

```python
def assess_family_continuity(current_top6, family_registry):
    for family in family_registry:
        # 检查当前轮是否有成员
        current_members = [c for c in current_top6 
                          if belongs_to_family(c, family)]
        
        if current_members:
            family.generations.append({
                "round": current_round,
                "rank": min_member_rank(current_members),
                "members": [c.id for c in current_members]
            })
            family.family_age += 1
        else:
            family.adaptation_trend = "declining"
            
        # 收敛判定
        if family.family_age >= 3:
            family.convergence_score = compute_intra_family_similarity(family)
```

---

## 输出格式: Round k+1 Input

```json
{
  "round": 4,
  "input_elites": [
    {
      "id": "R4_E01",
      "config": {"P": 2, "T": 3, "M": 3, "D": 1},
      "lineage": {
        "parent_type": "mutation",
        "parent_ids": ["R3_E01"],
        "mutation_operator": "D-1",
        "lineage_depth": 8
      },
      "survival_basis": {
        "primary": "composite",
        "composite_rank": 1,
        "dominates_count": 52
      },
      "family": {
        "family_id": "F_P2T3M3",
        "family_age": 4
      }
    }
    // ... 共6个
  ],
  "family_registry": {
    "F_P2T3M3": {
      "age": 4,
      "trend": "improving",
      "convergence_score": 0.91
    }
  },
  "hof_update": {
    "new_champions": ["R4_E01"],
    "retired": []
  }
}
```

---

## 成功判定标准

**协议验证成功**需满足:

1. **lineage完整性**: 100%种子可追溯到父代来源
2. **存活理由明确**: 每个精英有清晰的multi-objective评分
3. **家族延续**: 至少1个家族连续3轮进入top-6
4. **收敛迹象**: 某家族convergence_score > 0.85

**架构演化成功**需满足:

1. **Hall-of-Fame稳定性**: 某个配置连续5轮保持top-3
2. **帕累托前沿收敛**: 前沿解集变化率 < 5%连续3轮
3. **跨轮性能提升**: Round k+1的top-6整体优于Round k

---

## 与现有仓库的衔接

**已存在的基础设施**:
- `heavy_fast_genesis`: selection/variation/crossover 框架 ✓
- `parallel_heavy_mode_v5`: 128并行预算验证 ✓
- `multiverse_sweep/stage_3_128`: 128-universe运行记录 ✓
- `causal_fast_forward`: 邻域探索加速 ✓

**需新增的实现**:
1. `lineage_tracker.py`: 父代来源追踪
2. `family_registry.py`: 家族延续性管理
3. `hof_manager.py`: Hall-of-Fame更新
4. `round_controller.py`: Round k → k+1 流程编排

---

## 下一步验证计划

**Round 1**: 基线128 sweep，产出top-6  
**Round 2**: 应用本协议，验证6→128→6流程  
**Round 3-5**: 连续迭代，收集家族延续性证据  
**验证点**: 是否有家族稳定占据前列？是否出现收敛迹象？

---

**状态**: 协议已文档化，待实现验证模块后进入实验阶段。
