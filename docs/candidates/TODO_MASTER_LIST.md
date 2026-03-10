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

### P0: D1 Paired-Seed Comparative Harness [COMPLETE] ✅
- [x] **D1.1** 设计paired-seed实验框架 [DONE]
- [x] **D1.2** 实施A/A测试 (验证无偏差) [DONE]
  - 结果: PASS ✓
  - Independent variance: 0.019578
  - Paired variance: 0.003898
- [x] **D1.3** 计算variance reduction ratio [DONE]
  - 结果: **80.1%** (>30%阈值)
- [x] **D1.4** 撰写D1验证报告 [DONE]
  - 结论: Framework validated and operational
- **资源**: 16-32核, 适合sweep
- **状态**: ✅ **COMPLETE** 
- **完成时间**: 2026-03-10
- **执行**: `cargo run --bin d1_runner`
- **后续可用**: A1×A5, E1/E3, C1

### 当前执行状态更新
```
[COMPLETE] D1 ✅        - 基础设施就绪, 方差减少80.1%
[IN-PROGRESS] D4 🟡     - 001完成, 002 ongoing  
[READY] E1/E3 ⏸️        - 等D4 002收尾后大跑
[WAITING] A1×A5/B6 ⏸️   - 等D4全部完成
```

### 今日8小时执行清单
- [x] **Hour 0-1**: 启动D1, 完成A/A测试 ✅
- [ ] **Hour 1-4**: 继续D4.3-D4.5 (002 dynamics metrics)
- [ ] **Hour 4-6**: E1/E3接口准备和脚手架
- [ ] **Hour 6-8**: D4收尾, 准备E1/E3大规模sweep

### 今日执行顺序 (已确认)
1. **D1** (启动) - 基础设施, 低风险高杠杆
2. **D4** (继续) - 完成002部分
3. **E1/E3** (准备) - 接口+脚手架, 等大sweep时机
4. **A1×A5/B6** (等待) - 等D4全完成

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

### P1: E1 Critical Coupling Sweep [READY-等待D4间隙]
**实验规格**: `E_CLASS_EXPERIMENT_SPEC.md` - E1章节

#### Phase A: 粗筛 (Coarse Sweep) [READY]
- [ ] **E1-A.1** 确认v19接口: r, P, CI
- [ ] **E1-A.2** 配置参数空间:
  - N: [1e3, 3e3, 1e4, 3e4, 1e5] (5点)
  - K: 0.1-5.0 (15-20点, 对数均匀)
  - σ: [0.1, 0.5, 1.0] (3点)
  - μ: 1.0 (固定)
- [ ] **E1-A.3** 准备相位模型 (θ, 非精确Hz)
- [ ] **E1-A.4** 启动sweep: ~1200-1500 runs, 48-64并发
- [ ] **E1-A.5** 观测r跃迁: 从<0.2到>0.8?

#### Phase B: 局部加密 [BLOCKED-A结果]
- [ ] **E1-B.1** 仅在发现跃迁区域加密K到50-100点
- [ ] **E1-B.2** 增加N: [5e4, 7e4, 1e5, 3e5]
- [ ] **E1-B.3** 计算临界指数、滞后效应

#### Phase C: 机制验证 [BLOCKED-B结果]
- [ ] **E1-C.1** 准备E2/E4/E5/E6测试

**资源**: 48-64核, <32GB, Phase A约4-6小时
**前置条件**: D4 001部分完成 (理解指标语义)
**策略**: Coarse-to-fine, 避免暴力穷举
**Kill条件**: Phase A无相变(r始终<0.3或始终>0.9) → Family 10降级

### P1: E3 Density/Percolation Threshold [READY-等待D4间隙]
**实验规格**: `E_CLASS_EXPERIMENT_SPEC.md` - E3章节

#### Phase A: 粗筛 [READY]
- [ ] **E3-A.1** 配置参数空间:
  - N: [1e3, 1e4, 1e5] (3点, 固定规模)
  - K: E1中找到的临界区值 (3点)
  - ⟨k⟩ (average degree): 0.5-5.0 (15-20点, 覆盖k≈1)
- [ ] **E3-A.2** 启动sweep: ~900 runs, 48-64并发
- [ ] **E3-A.3** 观测P跳变 (percolation threshold)
- [ ] **E3-A.4** 观测r是否滞后于P上升

#### Phase B: 因果验证 [BLOCKED-A结果]
- [ ] **E3-B.1** 固定P值，变化其他参数，看r响应
- [ ] **E3-B.2** 扰动实验: 切断连接使P下降，观察r跟随

**资源**: 48-64核, <32GB, Phase A约3-4小时
**前置条件**: 可与E1 Phase A并行启动
**与v19对接**: 使用P (giant component ratio)
**通过标准**: P先上升，r后上升 → 确认"连通性→同步"链条

### P3: C1 Episodic Failure Recall [PENDING]
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

#### 若 E1/E3 发现临界点 [CONDITIONAL]
- [ ] **E2** Pacemaker Emergence vs No-Center
  - 测试: 中心节律源 vs 自发节律 vs 多seeds
- [ ] **E4** Hub Knockout After Rhythm Onset
  - 测试: 节律形成后移除top 5% hub, 观察是否崩溃
- [ ] **E5** Noise-Assisted Synchronization
  - 测试: 微噪声是否帮助跨越临界点
- [ ] **E6** Phase Reset / Re-entrainment
  - 测试: 节律是否可重置、可再锁相
- **触发条件**: E1/E3明确发现percolation/sync临界点
- **若E1/E3无临界点**: E2/E4/E5/E6暂缓, Family 10降级

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
[P0] D4 (001✅, 002 ongoing) ────────┬──┐
     (metrics)                      │  │
                                     ▼  │
[P0] D1 ────────────────────────────┘  │
     (framework)                        │
                                        ▼
[P1] E1 + E3 ─────────────────────┬─────┘
     (critical sync)               │
                                   ├── 若发现临界点 ─→ E2, E4, E5, E6
                                   └── 若无临界点 ───→ Family 10降级
                                        │
                                        ▼
[P2] A1×A5 ──────────────────────┬┐
     (factorial)                 ││
                                  ▼│
[P2] B6 ───────────────────────┬┴┘
     (metrics)                 │
                                ▼
[P3] C1 ──────────────────────┬┘
     (episodic memory)        │
                               ├── ✓ → C3, C4
                               └── ✗ → 降级

分支:
E1/E3 ✓ → E2, E4, E5, E6
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
