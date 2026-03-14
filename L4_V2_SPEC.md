# L4-v2 Specification

**Objective**: Shift inheritance from family-level bias to mechanism/routing-level bias, while suppressing unjustified structural leakage.

**Date**: 2026-03-14  
**Status**: SPEC LOCKED → Ready for Implementation

---

## 1. 问题定义 (L4-v1 教训)

### L4-v1 失败模式
- Inheritance package 使用 **family-level bias** (太粗)
- 推动候选向 "已知 family 的邻近变体" 跳跃
- 允许向未测试区域（P1, P4, T5）**结构性扩张**
- 结果：Reuse rate 下降，leakage 上升

### 目标转变
```
FROM: "受继承驱动的探索偏置"
  TO: "受继承驱动的模块复用式自我改进"
```

---

## 2. 两刀修复规格

### 刀 1: Akashic Package Schema (Mechanism-Level)

**新增字段** (v2 schema):

```json
{
  "package_version": "2.1-mechanism",
  "stable_mechanisms": {
    "delegation_patterns": [
      {"pattern": "adaptive_migration", "success_rate": 0.92, "context": "high_load"},
      {"pattern": "trust_based_routing", "success_rate": 0.88, "context": "degraded_node"}
    ],
    "recovery_sequences": [
      {"sequence": ["detect_fault", "isolate_node", "redistribute_tasks", "restore_trust"], "success_rate": 0.85},
      {"sequence": ["detect_fault", "immediate_switch", "gradual_recovery"], "success_rate": 0.79}
    ],
    "trust_update_priors": {
      "decay_rate": {"mean": 0.10, "std": 0.03, "range": [0.05, 0.15]},
      "recovery_rate": {"mean": 0.05, "std": 0.02, "range": [0.03, 0.08]}
    }
  },
  "blocked_motifs": [
    {"motif": "rapid_switching", "penalty": 0.5},
    {"motif": "migration_thrashing", "penalty": 0.4},
    {"motif": "trust_collapse_cascade", "penalty": 0.6}
  ],
  "route_constraints": {
    "pressure_range": {"min": 2, "max": 3, "optimal": [2, 3]},
    "triage_range": {"min": 3, "max": 4, "optimal": [3, 4]},
    "memory_range": {"min": 2, "max": 4, "optimal": [3, 4]}
  },
  "family_mechanism_map": {
    "F_P3T4M4": ["adaptive_migration", "trust_based_routing"],
    "F_P2T4M3": ["adaptive_migration"],
    "F_P3T4M3": ["trust_based_routing"]
  },
  "anti_expansion_hints": {
    "untested_pressure": [1, 4],
    "untested_triage": [2, 5],
    "penalty_per_step": 0.15
  }
}
```

**实现要求**:
- `Task1KnowledgeArchive.extract_mechanisms()` - 从 Mainline 结果提取模式
- `generate_task1_inheritance_package_v2()` - 输出 mechanism-level 包
- 向后兼容：v1 reader 能读 v2（忽略新字段）

---

### 刀 2: Fast Genesis Anti-Leakage Bias

**新增 CLI 参数**:

```bash
generate_candidates.py \
  --inheritance-package task1_inheritance_package_v2.json \
  --bias-strength 0.6 \
  --anti-leakage-strength 0.4 \          # NEW: 抗泄漏强度
  --max-family-distance 1 \               # NEW: 最大 family 距离
  --prefer-stable-paths true \            # NEW: 优先稳定路径
  --penalize-unjustified-expansion true   # NEW: 惩罚无根据扩张
```

**Anti-Leakage 评分函数**:

```python
def calculate_anti_leakage_penalty(candidate, inheritance_package):
    penalty = 0.0
    
    # 1. Family 距离惩罚
    known_families = inheritance_package.get("family_mechanism_map", {}).keys()
    if candidate.family_id not in known_families:
        min_dist = min(family_distance(candidate.family_id, kf) for kf in known_families)
        if min_dist > MAX_FAMILY_DISTANCE:
            penalty += ANTI_LEAKAGE_STRENGTH * (min_dist - MAX_FAMILY_DISTANCE) * 0.2
    
    # 2. 参数范围惩罚
    p = candidate.pressure
    t = candidate.perturbation
    m = candidate.memory
    
    constraints = inheritance_package.get("route_constraints", {})
    p_range = constraints.get("pressure_range", {}).get("optimal", [2, 3])
    t_range = constraints.get("triage_range", {}).get("optimal", [3, 4])
    m_range = constraints.get("memory_range", {}).get("optimal", [3, 4])
    
    if p not in p_range:
        penalty += ANTI_LEAKAGE_STRENGTH * 0.15
    if t not in t_range:
        penalty += ANTI_LEAKAGE_STRENGTH * 0.10
    if m not in m_range:
        penalty += ANTI_LEAKAGE_STRENGTH * 0.10
    
    # 3. 新 motif 惩罚
    expansion_hints = inheritance_package.get("anti_expansion_hints", {})
    untested_p = expansion_hints.get("untested_pressure", [])
    untested_t = expansion_hints.get("untested_triage", [])
    
    if p in untested_p:
        penalty += expansion_hints.get("penalty_per_step", 0.15)
    if t in untested_t:
        penalty += expansion_hints.get("penalty_per_step", 0.15)
    
    return min(penalty, 0.8)  # Cap at 0.8

# 最终得分
def generation_score(candidate):
    base = similarity_to_mechanism_patterns(candidate, inheritance_package)
    penalty = calculate_anti_leakage_penalty(candidate, inheritance_package)
    return base - penalty
```

**实现要求**:
- 新增 `AntiLeakageBias` 类
- 可调参数：`--anti-leakage-strength` (0.0-1.0)
- Ablation 测试：bias=0.0 时必须退回纯探索

---

## 3. 实验协议 (L4-v2)

### 固定不变
- **Round A-v2**: 无 inheritance (control)
- **Round B-v2**: Inheritance package v2 + anti-leakage
- **Ablation-v2**: Package loaded, but `--bias-strength 0.0 --anti-leakage-strength 0.0`
- **Sample**: 30 candidates per round, stratified (same as v1)
- **Evaluation**: Bridge → Mainline (same thresholds)

### 追加约束 (New)

| 约束 | 说明 |
|------|------|
| **Throughput maintained** | Round B-v2 throughput_delta ≥ Round A-v2 (不能为了复用牺牲性能) |
| **Ablation purity** | Ablation-v2 必须 ≡ Round A-v2 (控制基线不能丢) |

---

## 4. 通过标准 (L4-v2 HARD CRITERIA)

### 表 A: Effectiveness

| Metric | L4-v1 (Round B) | L4-v2 Target | Status |
|--------|-----------------|--------------|--------|
| Approve rate | 51.6% | **> 60%** | HARD |
| Throughput delta | +5.13% | **≥ +5.0%** (maintain) | HARD |
| Failure archetype | 0 | **≤ 1** | SOFT |

### 表 B: Compositionality

| Metric | L4-v1 (Round B) | L4-v2 Target | Status |
|--------|-----------------|--------------|--------|
| Reuse rate | 51.6% | **> 70%** | HARD |
| F_P3T4M4 share | 9.7% | **> 30%** | HARD |
| Leakage | 12.9% | **< 8%** | HARD |
| Winners from stable paths | 22.6% | **> 60%** | HARD |

### 判定矩阵

| 结果 | 条件 |
|------|------|
| ✅ **FULLY VALIDATED** | 6/6 hard criteria passed |
| ⚠️ **PARTIAL** | 4-5/6 hard criteria passed |
| ❌ **FAILED** | < 4/6 hard criteria passed |

---

## 5. Ablation 计划 (L4-v2 后)

测试机制 vs penalty 的独立贡献：

| 实验 | Package | Bias | Anti-Leakage | 目的 |
|------|---------|------|--------------|------|
| A | None | 0 | 0 | Control |
| B-full | v2 | 0.6 | 0.4 | Full treatment |
| B-mechanism-only | v2 | 0.6 | 0.0 | Is mechanism enough? |
| B-penalty-only | v1 | 0.6 | 0.4 | Is penalty enough? |
| Ablation | v2 | 0 | 0 | Baseline purity |

---

## 6. 实现顺序 (LOCKED)

1. **Akashic schema v2** (mechanism-level)
2. **Fast Genesis anti-leakage** (CLI + scoring)
3. **L4-v2 A/B/Ablation** (execute)
4. **Post-hoc ablation** (mechanism vs penalty)

**禁止**:
- ❌ 新任务 family
- ❌ 新架构层级
- ❌ 新实验设计
- ❌ 改 L4-v1 结果

---

## 7. 状态追踪

| 组件 | 状态 | Commit |
|------|------|--------|
| Akashic v2 schema | 🔴 TODO | - |
| Fast Genesis anti-leakage | 🔴 TODO | - |
| L4-v2 execution | 🔴 TODO | - |
| L4-v2 judgment | 🔴 TODO | - |

---

**批准**: Atlas-HEC Research Committee  
**生效**: 2026-03-14  
**版本**: L4-v2-SPEC-LOCKED
