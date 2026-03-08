# P3D-gamma: Measured Native A/B Validation - 实验计划

**Status**: 🔄 **P3D-gamma IN PROGRESS**

**Date**: 2026-03-09

**Goal**: 固定 seed 成对实验，输出统计显著性证据

---

## 院长判定总结

### P3D-beta 通过（限定范围）

| 项目 | 判定 | 证据 |
|-----|------|------|
| A. True Parameter Actuation | ✅ **COMPLETE** | `apply_preservation_to_main_runtime()` 真实调用 Agent API，输出 `[P3] SeekReward: bias_scale=1.30` |
| B. Real Intervention Statistics | ✅ **COMPLETE** | `action_counts` 逐 step 统计，`intervention_rate: 0.284` (142/500) |
| C. Native Homeostasis | ⚠️ **PARTIAL** | Native: world.step, reward_history, step_times; Proxy: energy, fatigue, thermal |

**对外口径**: 
> P3D-beta 通过：True Parameter Actuation COMPLETE。
> Measured Native A/B 属于下一阶段（P3D-gamma）。

---

## P3D-gamma 实验设计

### 目标
提供可比较的 A/B 统计证据，证明 preservation 在主系统原生运行时的真实效果。

### 实验规范

#### 1. 种子设计
```
固定种子集合: [42, 123, 456, 789, 2024, 777, 999, 314, 1618, 2718]
每种子跑: Baseline (off) + P2-ON (on) = 成对实验
总计: 10 seeds × 2 modes = 20 组实验
```

#### 2. 规模
```
每组: 50 episodes
每 episode: 500 max_steps
每实验总 steps: ~25,000 (50 × 500)
```

#### 3. 输出指标

| 指标 | 来源 | 类型 |
|-----|------|------|
| survival_steps | EpisodeStats | 主系统原生 |
| food_eaten | EpisodeStats | 主系统原生 |
| unique_cells_visited | EpisodeStats | 主系统原生 |
| avg_step_time_ms | step_times | 主系统原生 |
| intervention_rate | action_counts | P3 统计 |
| recovery_mode_ratio | agent.get_control_params() | P3 控制 |
| exploration_scale_avg | agent.get_control_params() | P3 控制 |
| curiosity_eta_avg | agent.get_control_params() | P3 控制 |

#### 4. 统计输出

```json
{
  "mode": "baseline|p2on",
  "seed": 42,
  "n_episodes": 50,
  "survival_steps": {"mean": 245.3, "std": 45.2, "min": 120, "max": 500},
  "food_eaten": {"mean": 3.2, "std": 1.8, "total": 160},
  "intervention_rate": 0.0,
  "recovery_ratio": 0.0,
  "avg_step_time_ms": {"mean": 9.8, "std": 0.5}
}
```

#### 5. 对比分析

| 对比项 | Baseline | P2-ON | 效应方向 |
|-------|----------|-------|---------|
| survival_steps | mean ± std | mean ± std | ↑ 延长？ |
| food_eaten | mean ± std | mean ± std | ↑ 增加？ |
| step_time_stability | variance | variance | ↓ 更稳定？ |
| intervention_rate | 0% | X% | 验证触发 |

---

## 执行命令

```bash
# 批量实验脚本
./scripts/p3d_gamma_batch.sh

# 手动单组
./target/release/p3d_main_runtime_native --preservation off --seed 42 --episodes 50 --steps 500
./target/release/p3d_main_runtime_native --preservation on --seed 42 --episodes 50 --steps 500

# 分析结果
python3 scripts/analyze_p3d_gamma.py logs/p3d/
```

---

## 通过标准

P3D-gamma 判定为 COMPLETE 需要：

1. ✅ 至少 10 个固定 seed 的成对实验
2. ✅ 每组 50+ episodes
3. ✅ 输出 mean ± std 统计
4. ✅ 效应方向明确（哪怕不显著）
5. ✅ 可复现脚本

---

## 当前状态

- [x] P3D-beta: True Parameter Actuation ✅
- [ ] P3D-gamma: Measured Native A/B ⏳ (本计划)

---

**下一步**: 执行批量实验脚本，生成统计报告。
