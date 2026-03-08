# Atlas-HEC v2.1 Self-Preservation System - STATUS

**Date**: 2026-03-09
**Reviewed By**: 院长

---

## 院长最终判定

### P3D-beta: ✅ COMPLETE（限定为 Actuation 层）

| 要求 | 状态 | 证据链 |
|-----|------|--------|
| **A. True Parameter Actuation** | ✅ **COMPLETE** | preservation decision → `apply_preservation_to_main_runtime()` → Agent runtime control API → 主系统参数改变<br>典型信号: `[P3] SeekReward: bias_scale=1.30` |
| **B. Real Intervention Statistics** | ✅ **COMPLETE** | `action_counts: {ContinueTask: 358, SeekReward: 142}`<br>`intervention_rate = 142 / (358+142) = 0.284` (逐 step 记录，非写死) |
| **C. Native Homeostasis** | ⚠️ **PARTIAL** | Native: `world.step`, `reward_history`, `step_times`, `food_eaten`<br>Proxy: `energy`, `fatigue`, `thermal`, `stability`, `prediction_error` |

**对外口径**:
> P3D-beta: True Parameter Actuation ✅ COMPLETE
> 
> 已实现：preservation decision → runtime API → 主系统参数改变的完整执行链
> 
> 未实现：全 native homeostasis（gridworld 本身无 metabolism 子系统）

---

## 阶段总览

```
P1:        Self Kernel                     ✅ COMPLETE
P2:        Self Preservation Kernel        ✅ COMPLETE  
P3A:       Runtime Integration             ✅ COMPLETE
P3B:       Simulated Validation            ✅ COMPLETE
P3C:       Runtime-like Harness            ✅ COMPLETE
P3D-alpha: Main-path Native Wiring         ✅ COMPLETE
P3D-beta:  True Parameter Actuation        ✅ COMPLETE (Actuation Layer)
P3D-gamma: Measured Native A/B             ⏳ PENDING (Measurement Layer)
```

**关键区分**:
- **P3D-beta** = Control Layer（控制层完成）
- **P3D-gamma** = Measurement Layer（测量层待验证）

---

## P3D-gamma 实验规范（院长标准）

### 目标
证明 preservation intervention 产生 **measurable behavioral shift**，而非仅证明 actuation 存在。

### 关键问题
> Does intervention produce measurable behavioral shift?

### 实验设计

| 参数 | 标准 |
|-----|------|
| Seeds | ≥ 10 固定种子 |
| Episodes / seed | ≥ 50 |
| 总样本 / condition | ≥ 500 episodes |
| 配对设计 | 每种子跑 Baseline + P2-ON |

### 输出指标

| 指标 | 类型 | 说明 |
|-----|------|------|
| survival_steps | 行为 | 平均生存步数 |
| food_eaten | 资源获取 | 食物获取总数 |
| reward_total | 奖励 | 累计奖励 |
| step_time_ms | 稳定性 | 步长时间（方差）|
| intervention_rate | P3 控制 | 干预比例 |
| recovery_mode_ratio | P3 控制 | 恢复模式占比 |
| action_distribution | P3 控制 | 各 action 分布 |

### 统计标准

**Cohen's d 解释**（固定规则）:
```
d < 0.2:   negligible (可忽略)
0.2–0.5:   small (小效应)  
0.5–0.8:   medium (中等效应)
> 0.8:     large (大效应)
```

### 判定标准（修正后）

#### 核心公式
```python
# 基础判定
intervention_active = intervention_rate > 0.10
effect_detected = abs(cohens_d) >= 0.20
sample_sufficient = n_episodes_per_condition >= 500

# 关键判定（修正：移除 sample_sufficient 作为 shift 替代条件）
behavioral_shift_detected = intervention_active AND effect_detected

# 证据强度（独立判定）
evidence_strength = "adequate" if sample_sufficient else "preliminary"
```

#### 四段式判定逻辑
```
if not intervention_active:
    verdict = "NO_SHIFT: intervention inactive"
    
elif not effect_detected:
    verdict = "NO_SHIFT: no measurable behavioral shift detected"
    # 关键失败模式：control parameters 未影响 policy dynamics
    
elif not sample_sufficient:
    verdict = "PRELIMINARY_SHIFT: effect detected but sample insufficient"
    
else:
    verdict = "SUPPORTED_SHIFT: measurable behavioral shift detected"
```

#### 常见失败模式（需警惕）
```
intervention_rate 很高 (如 80%)
但 behavior metrics 无变化 (d < 0.2)
→ verdict: "NO_SHIFT: no measurable behavioral shift detected"
→ 说明: control parameter 未真正影响 policy dynamics
```

**重要**: `sample_sufficient` 只影响证据强度，不影响 `behavioral_shift` 判定。

---

### 推荐输出模板

**检测到行为改变时**:
```json
{
  "intervention_rate": 0.284,
  "intervention_active": true,
  "cohens_d": 0.31,
  "effect_detected": true,
  "sample_sufficient": true,
  "behavioral_shift_detected": true,
  "evidence_strength": "adequate",
  "verdict": "SUPPORTED_SHIFT"
}
```

**无行为改变时**:
```json
{
  "intervention_rate": 0.284,
  "intervention_active": true,
  "cohens_d": 0.07,
  "effect_detected": false,
  "sample_sufficient": true,
  "behavioral_shift_detected": false,
  "evidence_strength": "adequate",
  "verdict": "NO_SHIFT"
}
```

---

## 运行命令

### 完整实验（~30分钟）
```bash
./scripts/p3d_gamma_batch.sh
# 10 seeds × 50 episodes × 500 steps
# 总样本: 500 episodes / condition
```

### 快速测试（~5分钟）
```bash
./scripts/p3d_gamma_quick.sh
# 3 seeds × 20 episodes (smoke test)
```

### 统计分析
```bash
python3 scripts/analyze_p3d_gamma.py logs/p3d/
# 输出: mean ± std, Cohen's d, behavioral shift 判定
```

---

## 文件索引

| 文件 | 阶段 | 说明 |
|-----|------|------|
| `src/p3_runtime_integration/` | P3A | Runtime Integration |
| `src/bin/p3b_ab_validation.rs` | P3B | Simulated Validation |
| `src/bin/p3c_real_validation.rs` | P3C | Runtime-like Harness |
| `src/bin/p3d_main_runtime_native.rs` | P3D | Main Runtime Native |
| `src/gridworld/mod.rs` | P3D | 主系统（P3 Control API）|
| `scripts/analyze_p3d_gamma.py` | P3D-γ | 统计分析（Cohen's d）|
| `scripts/p3d_gamma_batch.sh` | P3D-γ | 批量实验脚本 |
| `P3D_GAMMA_EXPERIMENT_PLAN.md` | P3D-γ | 实验规范文档 |
| `STATUS.md` | - | 本文件 |

---

## GitHub

**Repo**: https://github.com/Ectrox-Lab/atlas-hec-v2.1

**Latest Commit**: `47d479e` - 📋 STATUS: P3D-beta COMPLETE, P3D-gamma Framework Ready

---

**Last Updated**: 2026-03-09
**Next Step**: Run P3D-gamma full experiments and verify behavioral shift
