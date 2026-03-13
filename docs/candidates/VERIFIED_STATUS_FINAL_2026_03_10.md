# 已核验状态终版 [2026-03-10]

**核验范围**: 当前repo可检索到的全部文件  
**核验日期**: 2026-03-10  
**状态版本**: v1.0 (Final)

---

## 核验状态表

| 项目 | 状态标签 | 核验依据 | 备注 |
|------|----------|----------|------|
| **D1** | ✅ INFRASTRUCTURE | `TODO_MASTER_LIST.md`, `d1_runner` | 80.1% variance reduction, A/A test passed |
| **001** | 🔄 REFRAME | `FINAL_EXPERIMENTS_WEEK1_VERDICT.md` | WriteOnly=1.0, ReadOnly=0.5, Full=1.0 |
| **002** | 📁 ARCHIVED-NOT-DELETED | `TODO_MASTER_LIST.md` | Current task-line terminated |
| **E-class** | 🟢 STRONG MAINLINE CANDIDATE | `E1_PHASE_A_COMPLETE.md`, `EXECUTIVE_SUMMARY_2026_03_10.md` | Phase A: 15/15 transitions confirmed |
| **E1 Phase B** | ✅ COMPLETE | `results/e1_phase_b/`, `analyze_hysteresis.py` | Hysteresis + bistability + K_c convergence |
| **E3** | 🟡 MODEL REVISE REQUIRED | `results/e3_phase_a/summary.txt` | 50% causality, needs dynamic network model |
| **A1×A5** | 🟡 ACTIVE | `src/bin/a1_a5_runner.rs`, `results/a1_a5/` | Launched, use D4 data or enhance model |

---

## 已核验核心发现

### D1: Infrastructure Verified
```
Independent variance: 0.019578
Paired variance: 0.003898
Reduction: 80.1%
Status: Default for all comparative experiments
```

### 001: REFRAME Confirmed
**From `FINAL_EXPERIMENTS_WEEK1_VERDICT.md`**:
- WriteOnly: 1.0 (safe)
- ReadOnly: 0.5 (harmful)
- Full: 1.0 (dynamic works)

**Conclusion**: Damage from fixed-marker read, not write mechanism itself.

### 002: Current Line Terminated
**From `TODO_MASTER_LIST.md`**:
- 8 dynamics metrics identical across conditions
- Not "mechanism permanently invalid" but "current task-line unsupported"
- Family archived-not-deleted for future redesign

### E1 Phase A: Phase Transition Confirmed
**From `E1_PHASE_A_COMPLETE.md`**:
```
Configs: 300
Transitions: 15/15 (100%)
Sync distribution:
  r<0.2: 49.3%
  0.2<r<0.8: 6.0% (narrow)
  r>0.8: 44.7%
```

### E1 Phase B: First-Order Transition Evidence
**From `results/e1_phase_b/summary.txt`**:
```
Hysteresis cases: 166/600 (27.7%)
Bistable cases: 75
K_c convergence (σ=1.0): 1.702 (all N identical)
Transition type: First-order (滞后+双稳态)
```

---

## 待执行优先级 (已确认)

### P0: E1 Phase B 深度分析
**目标**: 从"现象强"推进到"机制更硬"
- K_c(N) 收敛形式
- 滞后环面积
- 双稳态区宽度
- 临界指数/尺度律提取（若数据支持）

**边界条件**: 若数据质量不足以稳定支持临界指数估计，则至少完成K_c(N)收敛形式、滞后环面积与双稳态区宽度的稳健拟合，不强行过度解释

**产出**: 判断E-class是"现象级主线"还是"机制级主线"

### P0: 001 A1×A5
**建议**: 优先利用D4现有12个CSV做先验因子分析与效应预估
- D4数据包含4 modes × 3 trials时间序列
- 若交互项或主效应仍不够清晰，再补正式A1×A5 paired-seed因子实验
- 避免重复实验，最大化已有数据价值

### P1: E3 Revise
**目标**: 修正模型设计
- 方案A: 动态网络 (connections evolve)
- 方案B: K ramp (coupling increases over time)

**状态**: 不阻塞主线推进

### P1: E2/E4 准备
**解锁条件**: ✅ E1 Phase B 滞后效应确认
- **E2**: Pacemaker emergence vs no-center
- **E4**: Hub knockout after rhythm onset

---

## 战略排序 (已生效)

```
E-class (Family 10)
    ↓ 已压过
001 (Family 1/2)
    ↓ 继续诊断但不抢资源
E3 (Revise)
    ↓ 机制补强
E2/E4 (Prepare)
    ↓ 滞后效应解锁
C1 (Reserve)
```

---

## 正式措辞 (文档/汇报用)

> **E-class**: 已从"主线候选"升级为"强主线候选"。依据为: E1 Phase A 的稳定跃迁证据，以及 E1 Phase B 提供的滞后效应、双稳态与 K_c 收敛证据。相变类型可判为一阶。
>
> **001**: 保持ACTIVE DIAGNOSTIC TRACK，问题已定位至fixed-marker语义，write机制安全。
>
> **E3**: MODEL REVISE REQUIRED，但不构成E-class继续推进的阻塞条件。
>
> **002**: ARCHIVED-NOT-DELETED，当前任务线终止，family保留用于未来redesign。

---

## 核验文件清单

### 状态文档
- [x] `TODO_MASTER_LIST.md` - 主任务清单
- [x] `CURRENT_STATUS.md` - 当前状态
- [x] `VERIFIED_STATUS_FINAL_2026_03_10.md` - 本文件
- [x] `STATUS_VERIFICATION.md` - 核验分层说明

### 实验报告
- [x] `E1_PHASE_A_COMPLETE.md` - Phase A完成报告
- [x] `EXECUTIVE_SUMMARY_2026_03_10.md` - 执行摘要
- [x] `D4_VALIDATION_REPORT.md` - D4验证报告
- [x] `FINAL_EXPERIMENTS_WEEK1_VERDICT.md` - Week1判决

### 数据文件
- [x] `results/e1_phase_a/` - Phase A原始数据
- [x] `results/e1_phase_b/` - Phase B原始数据+分析
- [x] `results/e3_phase_a/` - E3原始数据
- [x] `results/a1_a5/` - A1×A5结果

### 代码
- [x] `src/candidates/e1_critical_coupling/` - E1 Phase A/B代码
- [x] `src/candidates/001_markers/src/bin/a1_a5_runner.rs` - A1×A5代码

---

## 默认执行顺序（自治执行规则 v2.0 生效）

**前提**: E-class已标记为STRONG MAINLINE CANDIDATE，E1 Phase B已完成，无新blocker

| 顺序 | 任务 | 目标 | 产出 |
|------|------|------|------|
| 1 | **E1 Phase B 深度分析** | hysteresis loop形状, 双稳态区宽度, K_c(N)收敛形式, 临界指数/尺度律（数据支持时） | 判断E-class是"现象级主线"还是"机制级主线" |
| 2 | **001 A1×A5** | 先用D4数据做先验分析，必要时补正式paired-seed因子实验 | 钉死write/read gating效果, fixed read伤害是否可被gating消掉 |
| 3 | **E3 Revise** | 改模型: 动态网络或K ramp | P→r因果链验证 |
| 4 | **E2/E4 Preparation** | pacemaker emergence, hub knockout after onset | E-class机制深化 |
| 5 | **C1** | 保持后手 | 不抢E-class和001位置 |

**战略排序公式**: `E-class > 001 > E3 > E2/E4 > C1`

**除非以下情况发生，否则不再请求人工确认**:
- 结果推翻既有路线
- 高优先级任务资源互斥
- 触发kill/pivot/archive gate
- 服务器资源风险
- 新证据推翻当前战略排序

---

## 下次检查点

**触发条件**: E1 Phase B深度分析完成

**决策项**:
1. E-class是否达到"机制级主线"标准
2. 001 D4先验分析是否足够或需补正式实验
3. E3 revise优先级与资源分配
4. E2/E4正式启动时机

---

**核验完成**: 所有关键文件已落库，状态标签已生效。

**文档版本**: v1.1 (修订版)  
**修订内容**: A1×A5表述严谨化，E1 Phase B边界条件，默认执行顺序正文化
