# Hyperbrain 研究任务总清单 (Master TODO)

**版本**: v1  
**创建**: 2026-03-10  
**更新**: 跟随实验进度  
**原则**: Falsification-first, Minimal validation before scale

---

## 🎯 当前活跃任务 (Active)

### P0: D4 Semantic Metric Validation [IN-PROGRESS]
- [x] **D4.1** 收集001现有实验logs (coherence/consistency数据) ✅
  - 已生成12个CSV文件 (4 modes × 3 trials)
  - 包含tick/decision/action/marker_coherence时间序列
- [x] **D4.2** 拆解aggregate coherence → sub-metrics ✅
  - [x] Decision-level vs tick-level variance
  - [x] Temporal stability (trend analysis)
  - [x] Decision-tick correlation
  - [x] Signal-to-noise ratio
  - [x] Coherence-action correlation
- [ ] **D4.3** 收集002现有实验logs (stability/recovery数据)
- [ ] **D4.4** 拆解stability → dynamics-aware metrics
  - [ ] Overshoot magnitude
  - [ ] Settling time distribution
  - [ ] Integrated error
  - [ ] Smoothness/jerk
  - [ ] Final deviation
- [ ] **D4.5** 撰写D4验证报告
  - [x] 001初步发现:
    - ReadOnly: decision_variance=0, SNR=0 (fixed marker无变化)
    - Baseline/WriteOnly/Full: decision_variance=1451, SNR=6.36
    - 所有模式tick_smoothness相同(253)
  - [ ] 判断: 当前指标语义是否可靠?
  - [ ] 若不可靠, 列出受影响的001/002结论
- **资源**: 4-8核, <16GB内存
- **状态**: D4.1/D4.2完成, 等待D4.3-D4.5
- **Kill条件**: 若指标语义验证失败, 暂停001/002基于这些指标的所有结论

### P0: D1 Paired-Seed Comparative Harness [PENDING]
- [ ] **D1.1** 设计paired-seed实验框架
- [ ] **D1.2** 实施A/A测试 (验证无偏差)
- [ ] **D1.3** 计算variance reduction ratio
- [ ] **D1.4** 撰写D1验证报告
- **资源**: 16-32核, 适合sweep
- **时限**: 48小时
- **Kill条件**: 若配对设计无增益或有偏差, 直接kill D1

---

## 📋 待启动任务 (Pending - 按优先级排序)

### P1: A1 × A5 2×2因子诊断 [BLOCKED-D4]
- [ ] **A1/A5.1** 设计2×2实验矩阵
  - Write Gating: OFF/ON
  - Read Gating: OFF/ON
  - + Ablated no-marker control
- [ ] **A1/A5.2** 实施Baseline (no marker)
- [ ] **A1/A5.3** 实施WriteOnly (update but don't read)
- [ ] **A1/A5.4** 实施ReadOnly (frozen marker, agents read)
- [ ] **A1/A5.5** 实施Full (dynamic update + read)
- [ ] **A1/A5.6** 运行实验 (建议3-5 trials each)
- [ ] **A1/A5.7** 分析结果, 定位问题层
  - Write path problem?
  - Read path problem?
  - Both?
  - Gating ineffective → semantic mismatch?
- **资源**: 32-48核, 适合sweep
- **前置条件**: D4指标语义验证通过
- **时限**: D4完成后48小时

### P1: B6 Recovery Dynamics Metrics [BLOCKED-D4]
- [ ] **B6.1** 定义新metrics
  - [ ] Overshoot: max_drift / steady_state_drift
  - [ ] Settling time: ticks to within 10% of final
  - [ ] Integrated error: sum(|drift|) over time
  - [ ] Smoothness: variance of acceleration
  - [ ] Final deviation: residual at end
- [ ] **B6.2** Retrospective分析现有002 logs
- [ ] **B6.3** (条件) 若retrospective有新signal, 设计新实验验证
- [ ] **B6.4** (条件) 若retrospective无新signal, 运行新batch验证
- **资源**: 8核, <16GB (retrospective)
- **前置条件**: D4指标语义验证通过
- **时限**: D4完成后24小时
- **Kill条件**: 若新metrics对现有和新batch都不分离, 升级"controller no advantage"假设

### P1: C1 Episodic Failure Recall [PENDING]
- [ ] **C1.1** 设计实验环境
  - Repeated task with failure modes
  - Retrievable failure memory
- [ ] **C1.2** 实施Control (no memory)
- [ ] **C1.3** 实施Random retrieval
- [ ] **C1.4** 实施Failure-indexed retrieval
- [ ] **C1.5** 定义主指标
  - [ ] Revisit rate (same failure)
  - [ ] Time to escape repeated failure
  - [ ] Retrieval precision/recall
  - [ ] Performance: similar vs novel situations
- [ ] **C1.6** 运行实验 (建议10+ episodes)
- [ ] **C1.7** 分析结果
- **资源**: 16-24核, 较高内存观察
- **前置条件**: D1框架验证通过 (建议)
- **时限**: D1/D4完成后72小时
- **Kill条件**: 若无法击败random retrieval, 不能进主线默认组件

---

## 🔄 条件触发任务 (Conditional)

### Week 2 条件式路线

#### 若 A1×A5 表明marker salvageable [CONDITIONAL]
- [ ] **A2** Uncertainty-Weighted Marker Channel
- [ ] **A5-refined** 精细化read gating机制
- **触发条件**: A1/A5显示read gating概念成立

#### 若 B6 显示dynamics metrics能分离 [CONDITIONAL]
- [ ] **B1** Single-Shot Shape Recovery
- [ ] **B2** Delayed Perturbation Anticipation
- **触发条件**: B6新metrics暴露feedback advantage
- **优先级**: B2优于其他fancy变体

#### 若 C1 有稳定正信号 [CONDITIONAL]
- [ ] **C3** Self-Critique with Persistence Bias
- **触发条件**: C1成功且failure recall形成持续bias
- **并行**: 可与C1探索并行

#### 若 temporal fragmentation 明显 [CONDITIONAL]
- [ ] **C4** Continuity Signature / Identity Trace
- **触发条件**: C1显示agent行为有明显时间碎片化
- **优先级**: 可提升, 但不抢C1短期优先

---

## 🚫 Kill/Archive 决策点

### 001 Markers Kill条件检查
- [ ] **CHECK-001.1**: A1×A5 Write Gating无效 + Read Gating无效?
  - 若✓ → 标记001为ARCHIVE候选
- [ ] **CHECK-001.2**: A1×A5表明Write机制有害?
  - 若✓ → 标记Family 1为KILLED
- [ ] **CHECK-001.3**: A1×A5表明Read机制有害且无法修复?
  - 若✓ → 标记Family 2为KILLED

### 002 Soft Robot Kill条件检查
- [ ] **CHECK-002.1**: B6 retrospective + new batch均无分离?
  - 若✓ → 确认002 KILL, 资源归零
- [ ] **CHECK-002.2**: B1/B2尝试后仍无分离?
  - 若✓ → 彻底KILL 002方向

### C1 Kill条件检查
- [ ] **CHECK-C1.1**: C1无法击败random retrieval?
  - 若✓ → C1降级, 探索其他C类

---

## 📅 每日检查点 (Daily Checklist)

### 任务开始前
- [ ] 检查free/available memory > 96GB?
- [ ] 检查活跃任务是否按优先级排序?
- [ ] 新任务是否完成准入检查?

### 任务进行中
- [ ] 单任务峰值内存是否超过估计?
- [ ] 是否有任务进入swap压力?
- [ ] 低优先级任务是否可暂停?

### 任务结束后
- [ ] 结果是否可解释?
- [ ] 是否满足kill/continue条件?
- [ ] 是否需要调整后续优先级?

---

## 📆 每周检查点 (Weekly Review)

### Gate决策审查
- [ ] P0任务是否完成?
- [ ] Gate条件是否满足?
- [ ] Kill/Continue/Archive决策是否明确?

### 资源重分配审查
- [ ] 当前分配是否符合优先级?
- [ ] 是否有任务需要增加/减少资源?
- [ ] 新发现是否改变任务排序?

### 进度同步
- [ ] 本周完成哪些任务?
- [ ] 下周计划哪些任务?
- [ ] 阻塞/依赖是否解决?

---

## 📊 任务状态图

```
[P0] D4 ─────────────────────────────┐
     (retrospective)                 │
                                      ▼
[P0] D1 ────────────────────────────┬┴──┐
     (framework)                    │   │
                                     ▼   ▼
[P1] A1×A5 ────────────────────────┬┐  │
     (factorial)                   ││  │
                                    ▼│  ▼
[P1] B6 ──────────────────────────┬┴┘  │
     (metrics)                    │    │
                                   ▼    ▼
[P1] C1 ──────────────────────────┴────┘
     (episodic memory)

分支:
A1×A5 ✓ → A2, A5-refined
B6 ✓ → B1, B2
C1 ✓ → C3, C4
```

---

## 📝 任务准入检查表模板

```markdown
## 新任务: [TASK-ID]

### 基本信息
- **任务名称**: 
- **优先级**: P0/P1/P2/P3
- **前置条件**: 

### 资源估计
- **CPU需求**: 
- **内存峰值**: 
- **建议并发**: 
- **预计时长**: 

### 准入检查
- [ ] 单任务峰值内存已估计?
- [ ] 最大同时任务数已计算?
- [ ] 提交后不会压到96GB保护线以下?
- [ ] 若不清楚, 已采用保守值?

### Kill条件
- **什么情况下kill**: 
- **什么情况下continue**: 
- **什么情况下pivot**: 

### 批准
- [ ] 资源批准
- [ ] 优先级批准
- [ ] 开始执行
```

---

## 🔍 当前阻塞项

| 阻塞任务 | 被什么阻塞 | 预计解除时间 |
|----------|-----------|-------------|
| A1×A5 | D4指标验证 | D4完成后 |
| B6 retrospective | D4指标验证 | D4完成后 |
| C1 | D1框架验证 (建议) | D1完成后 |

---

## 📈 进度追踪

| 日期 | 完成任务 | 关键决策 |
|------|----------|----------|
| 2026-03-10 | 指令创建, Week1判决 | 001 REFRAME, 002 KILL |
| | | |
| | | |

---

**下次更新**: 每完成一个P0/P1任务后更新

**立即开始**: D4.1 - 收集001现有实验logs
