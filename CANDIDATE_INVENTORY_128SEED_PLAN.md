# Atlas-HEC 候选池与 Akashic 资产盘点 + 128-Seed 补种方案

**生成时间**: 2026-03-15  
**盘点范围**: Task-1 L4-v1 实验完整候选池 + Akashic 记忆资产  
**合规检查**: 符合 PROJECT.md Rule-2 (128-Seed 恒常)

---

## 第一部分：当前候选池真实数量

### 1.1 已生成候选总量

| Round | Seeds | Candidates/Seed | 小计 | 状态 |
|-------|-------|-----------------|------|------|
| Round A (Control) | 3 (1000, 1001, 1002) | 50 | **150** | Generated |
| Round B (Inheritance) | 3 (1000, 1001, 1002) | 50 | **150** | Generated |
| Round Ablation | 3 (1000, 1001, 1002) | 50 | **150** | Generated |
| **总计** | **9** | - | **450** | - |

**实际路径**: `benchmark_results/task1_inheritance/round_{a,b,ablation}/seed_10{0,1,2}/candidates/C*.json`

### 1.2 Family 分布统计 (450 candidates)

#### 核心稳定区 (P2/P3 + T3/T4 + M2/M3/M4)
| Family | 数量 | 占比 | 状态 |
|--------|------|------|------|
| F_P3T3M4 | 44 | 9.8% | 高频 |
| F_P3T4M3 | 42 | 9.3% | 高频 |
| F_P2T4M4 | 41 | 9.1% | 高频 |
| F_P3T3M2 | 40 | 8.9% | 高频 |
| F_P2T3M4 | 39 | 8.7% | 高频 |
| F_P3T4M4 | 35 | 7.8% | **Dominant** |
| F_P2T4M3 | 32 | 7.1% | 稳定 |
| F_P2T3M3 | 31 | 6.9% | 稳定 |
| F_P2T3M2 | 31 | 6.9% | 稳定 |
| F_P2T4M2 | 30 | 6.7% | 稳定 |
| F_P3T4M2 | 24 | 5.3% | 稳定 |
| F_P3T3M3 | 21 | 4.7% | 稳定 |
| **小计** | **410** | **91.1%** | 可用父代 |

#### 边缘/泄漏区 (P1, P4, P5, T2, T5, M5等)
| Family | 数量 | 状态 |
|--------|------|------|
| F_P4T4M3 | 4 | 泄漏 |
| F_P4T5M4 | 2 | 泄漏 |
| F_P4T4M4 | 2 | 泄漏 |
| F_P4T4M2 | 2 | 泄漏 |
| F_P4T3M3 | 2 | 泄漏 |
| F_P3T5M5 | 2 | 泄漏 |
| F_P2T5M4 | 2 | 泄漏 |
| F_P2T2M3 | 2 | 泄漏 |
| F_P1T3M4 | 2 | 泄漏 |
| F_P1T3M3 | 2 | 泄漏 |
| 其他边缘 | 18 | 泄漏 |
| **小计** | **40** | **排除** |

### 1.3 关键发现

1. **数量已超 128**：450 > 128，问题不是"不够"，而是"需要重组"
2. **有效父代 91%**：410 candidates 来自稳定区 (P2/P3, T3/T4, M2/M3/M4)
3. **Dominant Family 确认**：F_P3T4M4 (35个, 7.8%) 是 Step 3 Convergence 确认的核心
4. **泄漏可控**：仅 40个 (8.9%) 来自非最优区域

---

## 第二部分：Akashic 记忆资产盘点

### 2.1 已实现并可用

| 资产 | 位置 | 状态 | 内容摘要 |
|------|------|------|----------|
| **Task-1 Inheritance Package v2.1** | `task1_inheritance_package.json` | ✅ 可用 | stable_delegation_patterns, recovery_sequences, trust_update_priors, avoid_switching_patterns, generator_priors |
| **Task-1 Inheritance Package v2.1-mechanism** | `task1_inheritance_package_v2.json` | ✅ 可用 | mechanism-level: delegation_patterns, recovery_sequences, trust_update_priors, **blocked_motifs**, **route_constraints**, **family_mechanism_map** |
| **Promoted Policies** | `implementations/akashic_v3/output/promoted_policies.json` | ✅ 可用 | 4条核心策略，confidence 0.9-1.0 |
| **Evidence Graded Entries** | `implementations/akashic_v3/output/evidence_graded_entries.json` | ✅ 可用 | 分级证据，evidence_grade: institutionalized/validated |

### 2.2 Akashic v2.1-mechanism 包核心内容

```yaml
# 已沉淀的机制资产
stable_mechanisms:
  delegation_patterns:
    - adaptive_migration (success_rate: 0.92)
    - trust_based_routing (success_rate: 0.88)
  
  recovery_sequences:
    - [detect_fault, isolate_node, redistribute_tasks, restore_trust] (0.8)
  
  trust_update_priors:
    decay_rate: {mean: 0.1, std: 0.03, optimal: [0.05, 0.15]}
    recovery_rate: {mean: 0.05, std: 0.02, optimal: [0.03, 0.08]}

# 负面知识 (blocked patterns)
blocked_motifs:
  - rapid_switching (penalty: 0.5)
  - migration_thrashing (penalty: 0.4)
  - trust_collapse_cascade (penalty: 0.6)

# 路由约束 (route_constraints)
pressure_range: {min: 2, max: 3, optimal: [2,3], expansion_penalty: 0.15}
triage_range: {min: 3, max: 4, optimal: [3,4], expansion_penalty: 0.10}
memory_range: {min: 2, max: 4, optimal: [3,4], expansion_penalty: 0.10}

# Family-机制映射
family_mechanism_map:
  F_P3T4M4: {stability_score: 0.85, mechanisms: [adaptive_migration, trust_based_routing]}
  F_P2T4M3: {stability_score: 0.78, mechanisms: [adaptive_migration]}
  F_P3T4M3: {stability_score: 0.75, mechanisms: [trust_based_routing]}
  F_P3T3M2: {stability_score: 0.70, mechanisms: [conservative_delegation]}
```

### 2.3 尚未实现 (仅规格)

| 资产 | 状态 | 说明 |
|------|------|------|
| extract_mechanisms() | ❌ TODO | 从 Mainline 自动抽取机制 |
| generate_task1_inheritance_package_v2() | ❌ TODO | 自动生成 v2 包 |
| Anti-leakage scoring | ❌ TODO | Fast Genesis 端实现 |

---

## 第三部分：128-Seed 重组方案

### 3.1 原则

- **不是新造 128**，而是从 450 中**精选父代 → 重组 → 变形 → 扩回 128**
- **排除泄漏区**：P1, P4, P5, T2, T5, M5 不进入父代池
- **符合 Rule-4**：必须回答"如何组合/变形/重采样/防收缩"

### 3.2 父代精英池 (24个)

| 类别 | Family | 数量 | 选择理由 |
|------|--------|------|----------|
| **核心** | F_P3T4M4 | 8 | Dominant family, stability_score 0.85 |
| **次核心** | F_P2T4M3 | 4 | stability_score 0.78, adaptive_migration |
| **次核心** | F_P3T4M3 | 4 | stability_score 0.75, trust_based_routing |
| **扩展** | F_P3T3M2 | 2 | stability_score 0.70, conservative |
| **扩展** | F_P3T3M4 | 2 | 高频出现 (44个), 保守变体 |
| **扩展** | F_P2T4M4 | 2 | 高频出现 (41个), P2变体 |
| **扩展** | F_P2T3M4 | 2 | 高频出现 (39个), T3变体 |
| **总计** | - | **24** | - |

### 3.3 128-Seed 分配方案

| Pool | Seeds | 来源/操作 | 具体说明 |
|------|-------|-----------|----------|
| **Pool-A: 保守复制** | 32 | 24父代 × 低扰动复制 | trust_decay/recovery 在 [0.05,0.15]/[0.03,0.08] 内微扰 |
| **Pool-B: 稳定重组** | 32 | 只允许跨族重组 | F_P3T4M4 × F_P2T4M3, F_P3T4M4 × F_P3T4M3 |
| **Pool-C: 机制微变形** | 24 | 机制级参数扰动 | delegation_threshold, recovery_step_order, switching_weight |
| **Pool-D: 边界探针** | 16 | 约束邻域探索 | P∈[2,3], T∈[3,4], M∈[3,4] 边界，带 anti-expansion |
| **Pool-E: 控制组** | 16 | 8无inheritance + 8有包但bias=0 | 用于验证 inheritance 效果 |
| **Pool-F: 泄漏监测** | 8 | 少量P4/T5/M5 | 监测泄漏是否被抑制 |
| **总计** | **128** | - | 符合 Rule-2 |

### 3.4 回答 Rule-4 四问

| 问题 | 答案 |
|------|------|
| **下一轮如何组合?** | 只允许: F_P3T4M4 × F_P2T4M3, F_P3T4M4 × F_P3T4M3, F_P2T4M3 × F_P3T4M3 |
| **下一轮如何变形?** | trust_decay: ±0.02扰动; trust_recovery: ±0.01扰动; delegation_threshold: ±0.05; switching_suppression: ±0.1 |
| **如何重采样回128?** | 24父代 → 32保守 + 32重组 + 24微变形 + 16边界 + 16控制 + 8监测 = 128 |
| **是否过早收缩?** | 监控指标: 24父代多样性保持 > 0.8; 新family生成率 < 15%; F_P3T4M4占比 25-35% (非垄断) |

### 3.5 Anti-Leakage 约束 (基于 v2.1-mechanism 包)

```python
# Fast Genesis 生成时必须应用的惩罚
anti_leakage_penalties = {
    "P_outside_2_3": 0.15,      # route_constraints.pressure_range.expansion_penalty
    "T_outside_3_4": 0.10,      # route_constraints.triage_range.expansion_penalty
    "M_outside_2_4": 0.10,      # route_constraints.memory_range.expansion_penalty
    "rapid_switching": 0.50,    # blocked_motifs
    "migration_thrashing": 0.40,
    "trust_collapse_cascade": 0.60,
}
```

---

## 第四部分：执行清单

### 4.1 立即执行

- [ ] 从 450 candidates 中提取 24个父代精英 (按上述方案)
- [ ] 验证每个父代的 JSON 完整性
- [ ] 准备 128-seed 生成脚本

### 4.2 生成阶段

- [ ] 生成 Pool-A: 32 seeds (保守复制)
- [ ] 生成 Pool-B: 32 seeds (稳定重组)
- [ ] 生成 Pool-C: 24 seeds (机制微变形)
- [ ] 生成 Pool-D: 16 seeds (边界探针, 带anti-leakage)
- [ ] 生成 Pool-E: 16 seeds (控制组)
- [ ] 生成 Pool-F: 8 seeds (泄漏监测)

### 4.3 验证阶段

- [ ] 验证总计 128 seeds
- [ ] 验证 family 分布符合预期
- [ ] 验证无严重泄漏 (P1/P4/T5/M5 占比 < 10%)
- [ ] 记录 `parent_candidates`, `reseed_count=128`, `variation_ops`

### 4.4 元数据登记

```yaml
# 必须写入实验登记
experiment: L4-v2-128seed
parent_candidates:
  - F_P3T4M4: 8
  - F_P2T4M3: 4
  - F_P3T4M3: 4
  - F_P3T3M2: 2
  - F_P3T3M4: 2
  - F_P2T4M4: 2
  - F_P2T3M4: 2
reseed_count: 128
variation_ops: [preserve, recombine, mechanism_perturb, boundary_probe, control, monitor]
inheritance_package: task1_inheritance_package_v2.json
anti_leakage: enabled
```

---

## 第五部分：关键判断

### 5.1 现状

| 维度 | 判断 |
|------|------|
| **候选数量** | ✅ 充足 (450 > 128) |
| **候选质量** | ⚠️ 需筛选 (91% 可用, 9% 泄漏) |
| **Akashic 资产** | ✅ v2.1-mechanism 包已可用 |
| **Anti-leakage** | ⚠️ 规格就绪, 待 Fast Genesis 实现 |
| **父代清晰度** | ✅ F_P3T4M4 dominant, 家族结构明确 |

### 5.2 主要差距

1. **Fast Genesis 未实现 anti-leakage scoring**：v2.1-mechanism 包里的 `blocked_motifs` 和 `route_constraints` 尚未被消费
2. **450 → 128 的重组脚本未执行**：需要实际提取 24父代并扩回 128
3. **模拟 vs 真实**：部分 Mainline 结果是 simulation mode，需要真实验证

### 5.3 下一步动作

**不是再生成更多候选，而是：**

1. **压缩**: 从 450 中提取 24 父代精英
2. **重组**: 按 Pool A-F 方案扩回 128
3. **约束**: 应用 v2.1-mechanism 包的 anti-leakage
4. **验证**: 跑 L4-v2 Round A/B/Ablation

---

**符合 PROJECT.md 主线硬规则**:
- ✅ Rule-1: 无终局锁定 (当前最佳仅作为父代)
- ✅ Rule-2: 128-Seed 恒常 (本方案严格维持 128)
- ✅ Rule-3: 当前最佳用途 (作为下一轮父代材料)
- ✅ Rule-4: 四问已回答 (组合/变形/重采样/防收缩)
