# E-COMP-003: Core Module & Routing Map

**Status**: 🟢 ACTIVE  
**Date**: 2026-03-14  
**Parent**: L4-v2 Compositional Reuse (PARTIAL SUCCESS)  
**Type**: Mechanism Mapping Research  

---

## Research Goal

建立第一张模块/路由地图，系统回答：

> "到底复用了什么、怎么路由、哪些模块该共享、哪些该分离"

不是再跑大实验，而是基于 L4-v2 资产进行机制解剖。

---

## Background: Why Now

L4-v2 留下的关键认知：
- ✅ Mechanism/routing bias 方向对
- ✅ Family-level bias 太粗
- ✅ Leakage 可以被压住
- ✅ Reuse 信号能被拉起来

但核心问题未回答：
- ❓ "Reuse" 到底是什么？
- ❓ Routing 到底长什么样？
- ❓ Family 与 mechanism 的对应关系怎么定义？

---

## Five Core Questions

### Q1: 最稳定的 Delegation Pattern 是什么？

**研究内容**:
- 分析 L4-v2 Round B winners (approved candidates)
- 提取 trust-based routing vs adaptive migration 的实际表现
- 识别哪些 pattern 在不同 seed 下保持稳定

**交付物**:
- `delegation_pattern_catalog.json`: pattern → stability_score mapping
- Pattern 区分标准：consistency across seeds, throughput variance

### Q2: Recovery Sequence 有哪些可复用 Motif？

**研究内容**:
- 从 Task-1 simulator logs 提取 recovery sequences
- 识别 [detect_fault → isolate → redistribute → restore] 的变体
- 标注哪些 sequence 是高 throughput 候选的共性

**交付物**:
- `recovery_motif_library.json`: sequence → success_rate mapping
- Motif 分类：general purpose vs context-specific

### Q3: Trust Update 哪些是 Stable Prior，哪些是噪声？

**研究内容**:
- 统计 L4-v2 candidates 的 trust_decay/trust_recovery 分布
- 对比 approved vs rejected 候选的参数范围
- 识别真正的 stable prior (optimal range) vs 随机噪声

**交付物**:
- `trust_prior_v1.json`: {decay_range, recovery_range, confidence}
- 与 Akashic v2 package 中的 priors 对比验证

### Q4: F_P3T4M4 是 Family 标签还是 Mechanism Bundle？

**研究内容**:
- 解剖 F_P3T4M4 candidates 的具体 mechanism 组合
- 对比 "F_P3T4M4 但不同 mechanism" vs "不同 family 但相似 mechanism"
- 判定 F_P3T4M4 的预测力来自 family 标签还是 mechanism 复用

**交付物**:
- `f_p3t4m4_mechanism_profile.json`: 该 family 的 mechanism 指纹
- 判定结论：family proxy vs mechanism bundle

### Q5: 哪些 Candidate 属于"隐性重造结构"而非复用？

**研究内容**:
- 分析 approved candidates 中 mechanism_score 低的样本
- 识别"通过但未复用稳定机制"的异常模式
- 建立"pseudo-reuse"检测标准

**交付物**:
- `pseudo_reuse_detection.json`: 异常 candidate 列表 + 检测规则
- 判定标准：approved but low mechanism_score, novel motif, high variance

---

## Deliverables

### Required (v1.0)

| Deliverable | Format | Deadline |
|-------------|--------|----------|
| `family_mechanism_map_v1.json` | JSON | 2026-03-21 |
| `route_constraints_v1.json` | JSON | 2026-03-21 |
| `stable_vs_leakage_pattern_table.md` | Markdown | 2026-03-21 |
| `E-COMP-003_REPORT.md` | Markdown | 2026-03-21 |

### Optional (v1.1)

- `mechanism_similarity_matrix.json`: candidate × mechanism 相似度
- `routing_decision_tree.json": 从参数到 mechanism 的决策路径

---

## Methodology

### Data Sources
1. L4-v2 Round B winners (`/tmp/atlas_l4v2_results/mainline_detailed_results.json`)
2. Task-1 simulator logs (重新跑 winners 并记录详细 trace)
3. Akashic v2 mechanism package (`/tmp/task1_inheritance_package_v2.json`)

### Analysis Pipeline
```
Step 1: Load L4-v2 winners (approved candidates)
Step 2: Re-run with detailed logging (trust updates, routing decisions, recovery events)
Step 3: Extract patterns (delegation sequences, recovery motifs, trust trajectories)
Step 4: Cluster by mechanism similarity (not family)
Step 5: Build family_mechanism_map and route_constraints
Step 6: Document stable vs leakage patterns
```

### Validation Criteria
- ✅ Map 能预测 unseen candidate 的 mechanism 归属
- ✅ Route constraints 能解释为什么某些 family 稳定
- ✅ Pattern table 能区分 true reuse vs pseudo reuse

---

## Success Criteria

### Hard
- [ ] family_mechanism_map_v1.json 包含 ≥4 families 的 mechanism 分解
- [ ] route_constraints_v1.json 定义 ≥3 个维度的 optimal range
- [ ] stable_vs_leakage_pattern_table 明确区分 ≥2 种 reuse 类型

### Soft
- [ ] Map 能解释 F_P3T4M4 为什么 stable (>80% confidence)
- [ ] 识别出 1-2 个 "pseudo-reuse" 模式
- [ ] 为下一代 inheritance package (v3) 提供设计依据

---

## Relationship to Other Lines

### Enables (Downstream)
- **主线 2 (持续体)**: 自治壳知道自己在维护什么 mechanism
- **主线 3 (新任务族)**: 新任务泛化有清楚的 mechanism 参照

### Depends on (Upstream)
- **L4-v2**: 提供 winners 数据和 mechanism bias 验证

### Parallel (Same Layer)
- None — this is the current focus

---

## Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| L4-v2 winners 样本太少 | 放宽 approval 标准，纳入 marginal candidates |
| Mechanism 边界模糊 | 用 behavior trace 而非参数标签定义 mechanism |
| Pattern 不稳定 | 多 seed 验证，标注 confidence level |

---

## Timeline

| Week | Milestone |
|------|-----------|
| 1 (2026-03-14 ~ 03-21) | Data extraction, pattern analysis, v1 deliverables |
| 2 (2026-03-21 ~ 03-28) | Validation, refinement, documentation |
| 3 (2026-03-28 ~ 04-04) | Integration with inheritance package v3 design |

---

## Current Status

**2026-03-14**: E-COMP-003 启动，等待数据提取开始。

---

**Research Lead**: Atlas-HEC  
**Review Cycle**: Weekly checkpoint  
**Archival**: `docs/research/E-COMP-003/` (created upon completion)
