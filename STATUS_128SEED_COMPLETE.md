# 128-Seed 重组完成状态报告

**完成时间**: 2026-03-15  
**操作**: 从450候选中提取24父代 → 重组生成128 seeds  
**符合规范**: PROJECT.md Rule-1/2/3/4 (主线硬规则)  
**状态**: ✅ **FROZEN - 等待L4-v2 Bridge验证**

---

## 执行摘要

| 阶段 | 输入 | 输出 | 状态 |
|------|------|------|------|
| 父代提取 | 450 candidates | 24 elite | ✅ 完成 |
| Pool-A 保守复制 | 24 elite | 32 seeds | ✅ 完成 |
| Pool-B 稳定重组 | 24 elite | 32 seeds | ✅ 完成 |
| Pool-C 机制微变形 | 24 elite | 24 seeds | ✅ 完成 |
| Pool-D 边界探针 | 24 elite | 16 seeds | ✅ 完成 |
| Pool-E 控制组 | 24 elite | 16 seeds | ✅ 完成 |
| Pool-F 泄漏监测 | 24 elite | 8 seeds | ✅ 完成 |
| **总计** | - | **128 seeds** | ✅ **完成** |

---

## 冻结状态声明 (FROZEN MANIFEST)

```yaml
manifest_frozen: true
frozen_at: "2026-03-15T05:00:00Z"
frozen_by: "Atlas-HEC Research Committee"
parent_pool_frozen: true
evaluation_axes_frozen: true
pass_fail_rules_frozen: true
```

**冻结后禁止**:
- ❌ 修改任何seed的元数据字段
- ❌ 增删seeds
- ❌ 变更pool分配
- ❌ 调整control/leakage/gray标记

---

## 父代精英池 (24个)

| Family | 数量 | 占比 | 机制特征 |
|--------|------|------|----------|
| F_P3T4M4 | 8 | 33% | adaptive_migration + trust_based_routing |
| F_P2T4M3 | 4 | 17% | adaptive_migration |
| F_P3T4M3 | 4 | 17% | trust_based_routing |
| F_P3T3M2 | 2 | 8% | conservative_delegation |
| F_P3T3M4 | 2 | 8% | - |
| F_P2T4M4 | 2 | 8% | - |
| F_P2T3M4 | 2 | 8% | - |

---

## 128-Seed 分布 (三区分层)

### 区域划分
| 区域 | Seeds | 占比 | 说明 |
|------|-------|------|------|
| **核心区** | 116 | 90.6% | 7个核心families |
| **灰区** | 6 | 4.7% | 边缘但未越界 |
| **泄漏区** | 6 | 4.7% | Pool-F + 2个边界探针 |

### 灰区Seeds明细 (必须单独追踪)
| Seed ID | Family | Pool | 位置 |
|---------|--------|------|------|
| S2088 | F_P2T3M3 | D | 边界探针 |
| S2096 | F_P2T3M3 | D | 边界探针 |
| S2092 | F_P3T3M3 | D | 边界探针 |
| S2100 | F_P3T3M3 | D | 边界探针 |
| S2126 | F_P2T2M3 | F | 泄漏监测 |
| S2127 | F_P3T2M4 | F | 泄漏监测 |

**注意**: S2126/S2127属于Pool-F泄漏监测，但T=2确实超出optimal [3,4]范围。

### Pool分布
| Pool | Seeds | 模式 | 关键标记 |
|------|-------|------|----------|
| A | 32 | preserve_low_perturb | is_control=false, is_leakage_monitor=false |
| B | 32 | recombine_stable | is_control=false, is_leakage_monitor=false |
| C | 24 | mechanism_perturb | is_control=false, is_leakage_monitor=false |
| D | 16 | boundary_probe | 含4个灰区 |
| E | 16 | control_baseline/bias_zero | **is_control=true** |
| F | 8 | leakage_monitor | **is_leakage_monitor=true**, 含2个灰区 |

### Family分布 (Top 10)
| Family | 数量 | 占比 | 类别 |
|--------|------|------|------|
| F_P3T4M4 | 56 | 43.8% | 核心/Dominant |
| F_P2T4M3 | 24 | 18.8% | 核心 |
| F_P3T4M3 | 14 | 10.9% | 核心 |
| F_P3T3M4 | 6 | 4.7% | 核心 |
| F_P2T4M4 | 6 | 4.7% | 核心 |
| F_P2T3M4 | 6 | 4.7% | 核心 |
| F_P3T3M2 | 4 | 3.1% | 核心 |
| F_P2T3M3 | 4 | 3.1% | **灰区** |
| F_P3T3M3 | 4 | 3.1% | **灰区** |
| F_P2T2M3 | 1 | 0.8% | **灰区** |

---

## Bridge/Mainline Readiness

```yaml
ready_for_bridge: true
manifest_frozen: true
parent_pool_frozen: true
evaluation_axes_frozen: true
control_group_present: true
leakage_monitor_present: true
gray_zone_seed_count: 6
next_stage: L4-v2-Bridge-Phase1
```

---

## 冻结比较轴 (L4-v2评估维度)

### 必看比较组
| 比较轴 | 对比组 | 关键问题 |
|--------|--------|----------|
| **A vs B** | Pool-A (保守) vs Pool-B (重组) | 重组是否优于保守复制？ |
| **B vs C** | Pool-B (重组) vs Pool-C (微变形) | 机制微变形是否增加robustness还是noise？ |
| **Inheritance vs Control** | A/B/C vs Pool-E | inheritance是否真的贡献增益？ |
| **Boundary Test** | Pool-D单独 | 边界探针是带来增益还是只增加波动？ |
| **Anti-leakage Check** | Pool-F | 泄漏监测是否在Bridge/Mainline被稳定压制？ |

### 核心指标 (8项)
| 指标 | 说明 | 关键阈值 |
|------|------|----------|
| `approve_rate` | Bridge/Mainline通过率 | - |
| `hold_rate` | 待观察率 | <20% |
| `reject_rate` | 拒绝率 | - |
| `throughput_delta` | 吞吐量变化 | >0 |
| `failure_archetype_recurrence` | 失败原型重现 | 下降 |
| `leakage_hit_rate` | 泄漏穿透率 | **<15%** |
| `family_shift_after_bridge` | Bridge后family分布变化 | 监控收缩 |
| `control_gap` | Inheritance池相对控制组的提升 | **>5pp** |

**最关键两项**:
- `control_gap`: 直接回答"Akashic继承到底有没有用"
- `leakage_hit_rate`: 直接回答"好结果是否混进了leakage路径"

---

## 冻结Pass/Fail规则

### Bridge判定
| 结果 | 条件 | 后续动作 |
|------|------|----------|
| **PASS** | throughput_delta > 0.5%, 无失败原型匹配 | 进入Mainline候选 |
| **HOLD** | throughput_delta ∈ [0, 0.5%], 或单一弱匹配 | 等待更多数据 |
| **REJECT** | throughput_delta < 0, 或明确失败原型匹配 | 拒绝，记录archetype |
| **LEAKAGE-REJECT** | Pool-F候选通过且非预期行为 | 触发anti-leakage校准 |

### Mainline判定
| 结果 | 条件 |
|------|------|
| **APPROVE** | 5/5指标达标，跨seed可重复 |
| **HOLD** | 2-3/5达标，需更多验证 |
| **REJECT** | <2/5达标，或方差爆炸 |

### 失败模式触发线
| 失败模式 | 触发条件 | 标记 |
|----------|----------|------|
| **Premature Contraction** | Bridge后F_P3T4M4占比>60% 且唯一families<15 | 🔴 contraction_warning |
| **Pool-C Noise** | Pool-C相对Pool-B无提升，jitter>Pool-B×1.5 | 🟡 mechanism_ineffective |
| **Leakage Penetration** | Pool-F通过率>控制组或>10% | 🔴 anti_leakage_fail |

---

## 分阶段验证计划

### Phase 1: Bridge全量128
**目标**:
- 快速筛掉明显弱候选
- 验证family分布是否失真
- 确认Pool-F是否异常穿透

**输出**:
- 每个pool的pass/marginal/fail分布
- 每个family的Bridge存活率
- 泄漏监测组穿透率
- 灰区seeds去向

### Phase 2: Mainline分层抽样
**不全部送高成本Mainline**，先抽46个:

| Pool | 抽样数 | 理由 |
|------|--------|------|
| A | 8 | 主轴代表 |
| B | 8 | 重组效果 |
| C | 8 | 微变形价值 |
| D | 6 | 边界探索，不需要太多 |
| E | 8 | **控制组必须足够** |
| F | 8 | **泄漏监测必须全跑** |
| **合计** | **46** | - |

### Phase 3: Mainline扩展
若Phase 2看出清楚分层，将表现最好的1-2个pool扩到全量。

---

## Seed元数据字段 (已冻结)

每个seed必须包含:
```json
{
  "seed_id": "S2000",
  "pool": "A",
  "source_pool": "Pool-A",
  "zone": "core",
  
  "parent_candidates": ["ELITE_000_F_P3T4M4"],
  "family_id": "F_P3T4M4",
  
  "variation_ops": ["preserve_low_perturb"],
  "generation_mode": "preserve_low_perturb",
  "inheritance_mode": "v2.1-mechanism-biased",
  
  "is_control": false,
  "is_leakage_monitor": false,
  "is_gray_zone": false,
  "expected_role": "stability_baseline",
  
  "manifest_version": "1.0-frozen",
  "frozen_at": "2026-03-15T05:00:00Z"
}
```

---

## 文件位置

```
next_128_seed/
├── parent_elite/                    # 24父代精英
│   ├── ELITE_000_F_P3T4M4.json
│   └── manifest.json
├── pool_a/ ~ pool_f/                # 128 seeds (S2000~S2127)
│   └── S*.json (含完整元数据)
└── manifest/
    ├── seed_manifest.json           # 完整清单
    ├── family_distribution.json     # Family分布
    └── frozen_manifest.json         # 冻结声明 ⭐

STATUS_128SEED_COMPLETE.md           # 本状态报告
```

---

## 下一步行动 (严格顺序)

1. **Phase 1**: Bridge全量128 → 产出pass/marginal/fail分层
2. **检查点**: 若leakage_hit_rate>15%或contraction_warning触发，暂停
3. **Phase 2**: Mainline分层抽样46个 → 产出control_gap和mechanism_effectiveness
4. **判定**: L4-v2是否满足"improvement来自compositional reuse而非exploration bias"
5. **Phase 3**: 若达标，扩展Mainline到全量；若失败，回查Akashic v2 schema

---

**批准**: Atlas-HEC Research Committee  
**冻结时间**: 2026-03-15T05:00:00Z  
**状态**: 🔒 **FROZEN - 等待L4-v2 Phase 1 Bridge执行**
