# P1 Execution Ready Status
## 因果实验协议 v1.0 - 执行就绪确认

**日期**: 2026-03-09  
**状态**: ✅ 协议完备，等待模拟引擎就绪  
**目标**: P1 Phase 1 方向性筛选 (n=3/group)

---

## 执行优先级（已确认）

| 优先级 | 实验 | 理由 | 预期结果 |
|--------|------|------|----------|
| **1** | **P1-C** | 最易验证"阈值vs压力"分离 | I_crit不变，hazard↑，灭绝提前 |
| **2** | **P1-A** | Memory是CDI核心组分 | CDI更快↓，灭绝更早 |
| **3** | **P1-B** | Cooperation依赖实现细节 | 若效果弱不否定理论 |

---

## Phase 1 通过标准（硬编码）

某实验组进入Phase 2，需满足 **≥2条**：

```python
PASS_CRITERIA = {
    'CDI_decline_earlier': 
        mean(treatment.decline_gen) < mean(ctrl.decline_gen),
    
    'extinction_earlier': 
        mean(treatment.first_extinct_gen) < mean(ctrl.first_extinct_gen),
    
    'hazard_higher': 
        mean(treatment.hazard_ratio_lowCDI) > mean(ctrl.hazard_ratio_lowCDI)
}

进入Phase 2条件: sum(PASS_CRITERIA.values()) >= 2
```

---

## P1-A 修订：渐进式KO

**原设计**: memory_capacity = 0（可能太猛）  
**修订设计**:

| Phase | Memory Capacity | 目的 |
|-------|----------------|------|
| 1A | 30% baseline | 先看效应方向 |
| 2A | 0% (KO) | 验证剂量效应 |

避免"粗暴损坏系统"，识别memory的**因果贡献**。

---

## 执行清单

### 预执行检查

- [ ] Bio-World v18.1 模拟引擎编译成功
- [ ] 支持参数：`--memory-capacity`, `--cooperation-willingness`, `--boss-strength`
- [ ] 输出格式：evolution.csv（包含generation, avg_cdi, population, extinct_count, alive_universes）

### 执行命令

```bash
# Phase 1: 方向性筛选 (预计12 runs × 3小时 = 36小时)
./run_p1_experiments.sh 1

# 实时监控
watch -n 60 'ls -lt /home/admin/zeroclaw-labs/p1_causal_experiments/*/evolution.csv'

# 完成后自动分析
# 输出: P1_analysis_*/P1_RESULTS_SUMMARY.md
```

### 成功判定

| 结果 | 标准 | 下一步 |
|------|------|--------|
| **强成功** | P1-A/B/C中≥2组满足≥2条标准 | 进入Phase 2 (n=5-8) |
| **中成功** | P1-C满足标准，或P1-A/C满足 | 扩P1-C，补充P1-A剂量 |
| **弱成功** | 仅1组满足，但方向一致 | 讨论：干预设计或CDI定义 |
| **未通过** | 无组满足≥2条 | 返回：重新审视理论假设 |

---

## 关键成功模式

### 强成功模式（最理想）
```
P1-A (30% memory): CDI decline ↑300代, extinction ↑500代, hazard ↑2x
P1-C (1.5x boss):  I_crit = 0.53±0.01 (stable), hazard ↑3x, extinction ↑400代

结论: CDI是causal state variable
```

### 中成功模式（P1-C单独成功，也很有价值）
```
P1-C: I_crit = 0.53±0.01 (stable)
      hazard curve shifted up
      extinction earlier
      
结论: 结构临界性 vs 环境压力分离成立
```

### 需解释模式
```
P1-A: CDI变了，但extinction没变
→ CDI只是局部结构，不足以控制系统级稳定性

或
P1-C: I_crit变了
→ 阈值是环境依赖的，非纯结构性
```

---

## 当前研究主线确认

### P0 已建立 ✅
```
CDI decline → Population decline → Extinction
     ↓
I_crit ≈ 0.53 ± 0.01
HR > 10x
lead = 500-3300 generations
```

### P1 要建立 🔄
```
do(X) → ΔCDI → Δh(t) → Δextinction
```

**升级目标**: 从"leading indicator"到"**causal state variable**"

---

## 执行后预期产出

| 文件 | 内容 |
|------|------|
| `P1_RESULTS_SUMMARY.md` | 执行摘要与因果结论 |
| `P1_EFFECT_SIZES.json` | 量化效应数据 |
| `P1_group_comparisons.png` | 组间对比可视化 |
| `P1_DOSE_RESPONSE.png` | 剂量-响应曲线 (Phase 2) |

---

## 最终可接受的因果结论（预定义）

### 强通过 (≥2组满足标准)
> "Intervening on memory or cooperation causally alters CDI trajectories and extinction dynamics, supporting CDI as a **causal state variable** rather than merely a leading indicator."

### 中通过 (P1-C成功，或单组强效应)
> "Environmental stress modulates extinction hazard without materially shifting the estimated CDI threshold, supporting a distinction between **structural criticality and stress modulation**."

### 未通过
> "Current intervention designs do not provide conclusive evidence for CDI as causal state variable. Further refinement of intervention targets or CDI definition may be required."

---

## 当前状态：等待执行

```
P0: ████████████████████ 100% ✅
P1 Protocol: ████████████████████ 100% ✅
P1 Execution: ░░░░░░░░░░░░░░░░░░░░ 0% ⏳
```

**下一步**: 模拟引擎就绪 → 执行 `./run_p1_experiments.sh 1`

---

*文档版本*: 1.0  
*最后更新*: 2026-03-09  
*状态*: 执行就绪，等待引擎
