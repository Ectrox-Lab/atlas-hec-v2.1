# Hyperbrain 研究任务总清单 (Master TODO)

**版本**: v1  
**创建**: 2026-03-10  
**更新**: 跟随实验进度  
**原则**: Falsification-first, Minimal validation before scale

---

## 🎯 当前活跃任务 (Active)

### P0: D4 Semantic Metric Validation [COMPLETE] ✅
- [x] **D4.1** 收集001现有实验logs ✅
- [x] **D4.2** 拆解aggregate coherence → sub-metrics ✅
- [x] **D4.3** 收集002现有实验logs ✅
- [x] **D4.4** 拆解stability → dynamics-aware metrics ✅
  - [x] 8个子指标全部完成
  - [x] 所有指标在3条件间完全相同
- [x] **D4.5** 撰写D4验证报告 ✅
  - 报告: `D4_VALIDATION_REPORT.md`
- **资源**: 4-8核, <16GB内存
- **状态**: ✅ **COMPLETE**
- **完成时间**: 2026-03-10

### D4 关键结论
| 项目 | 结论 | 决策 |
|------|------|------|
| **001** | Metric coupling已修复, fixed-marker失效但dynamic正常 | **REFRAME** → 继续A1×A5 |
| **002** | 当前任务环境8个dynamics指标无分离 | **Current task-line terminated** → 资源归零, family archived |

### 002 KILL 确认 ✅
- [x] Aggregate stability: 所有条件相同 (0.964)
- [x] Recovery time: 无分离
- [x] 8 dynamics sub-metrics: 全部相同
- [x] 结论: 不是metric问题, 是mechanism问题
- **状态**: 002终止, 资源转E1/E3

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
[COMPLETE] D4 ✅        - 001 REFRAME, 002 archived
[COMPLETE] E1 Phase A ✅ - 临界相变确认 (15/15配置)
[COMPLETE] E1 Phase B ✅ - 滞后效应+双稳态+K_c收敛
[EXECUTING] 001 A1×A5 🔥 - 立即启动
[REVISE] E3 🟡          - 模型需修正, 不阻塞主线
[PREP] E2/E4 ⏸️         - 基于滞后效应准备
```

### 状态标签 (正式)
| Family | 状态 | 标签 |
|--------|------|------|
| E-class (Family 10) | 🟢 | **STRONG MAINLINE CANDIDATE** |
| 001 (Family 1/2) | 🟡 | **ACTIVE DIAGNOSTIC TRACK** |
| E3 | 🟡 | **MODEL REVISE REQUIRED** |
| 002 | ⚫ | **ARCHIVED-NOT-DELETED** |

### 今日8小时执行清单 ✅ COMPLETE
- [x] **Hour 0-1**: 启动D1, 完成A/A测试 ✅
- [x] **Hour 1-4**: 完成D4.3-D4.5 (002 dynamics metrics) ✅
- [x] **Hour 4-6**: D4收尾, 002 KILL确认 ✅
- [x] **Hour 6-8**: E1/E3准备, 等待启动时机 ✅

### 执行完成状态
| 任务 | 状态 | 关键产出 |
|------|------|----------|
| **D1** | ✅ COMPLETE | Paired-seed framework, 80.1% variance reduction |
| **D4** | ✅ COMPLETE | Validation report, 001 REFRAME, 002 KILL |
| **001** | 🔄 **ACTIVE** | A1×A5诊断启动中 |
| **002** | 📁 ARCHIVED | Current task-line terminated |
| **E-class** | 🟢 **STRONG MAINLINE CANDIDATE** | Phase A跃迁+Phase B滞后/双稳态/K_c收敛 |
| **E3** | 🟡 REVISE | 模型修正中, 不阻塞主线 |
| **A1×A5** | 🔥 **EXECUTING** | D1框架, 立即启动 |

### 立即执行 [NOW - FINAL]

**优先级P0**:
1. **001 A1×A5** 🔥🔥 - **LAUNCH NOW**
   - 使用D1框架 (paired-seed, 80.1% variance reduction)
   - 目标: 钉死write/read gating效果, fixed-marker伤害是否可被gating消掉
   - 时机: D4已定位问题, E1 Phase B战略判断已完成, 不阻塞

2. **E1 Phase B深度分析** 🔥 - **继续**
   - 重点: hysteresis loop形状, 双稳态区宽度, K_c(N)收敛形式
   - 目标: 判断E-class是"现象级主线"还是"机制级主线"

**优先级P1**:
3. **E3 Revise** 🟡 - **模型修正**
   - 问题: P静态/r动态, 时间尺度不匹配
   - 决策: 需要修正, 但**不阻塞主线**
   - 角色: 机制链补强, 非Family 10存活支点

4. **E2/E4准备** ⏸️ - **预备启动**
   - 依据: 滞后效应+双稳态
   - 方向: pacemaker emergence, hub knockout after onset

### 正式措辞 (文档/汇报用)

> **E-class 状态**: 
> E-class 已从"主线候选"升级为"**强主线候选**"。
> 依据为: E1 Phase A 的稳定跃迁证据，以及 E1 Phase B 提供的滞后效应、双稳态与 K_c 收敛证据。
> 相变类型可判为**一阶**。
> E3 的 P→r 因果验证仍重要，但其当前模型修正需求**不构成 E-class 继续推进的阻塞条件**。

### E1 Phase A 完成总结 ✅
- **状态**: 临界相变确认 (15/15配置)
- **关键产出**: K_c随σ变化曲线, 有限尺寸效应数据
- **战略影响**: Family 10升级为"主线候选", E2/E4/E5/E6解锁
- **报告**: `docs/candidates/E1_PHASE_A_COMPLETE.md`

### 自治执行规则 (新增)
```
自动启动条件 (全部满足):
✓ 前置依赖已完成
✓ 资源已释放
✓ 优先级链第一
✗ 无新blocker

请求人工决策触发:
- 结果推翻既有路线
- 高优先级任务资源互斥  
- 触发kill/pivot/archive gate
- 服务器资源风险
```

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

### P1: A1 × A5 2×2因子诊断 [UNBLOCKED] ✅
**状态**: 🟢 **D1框架就绪, D4完成, 立即可用**
**决策**: 等待上层调度信号 (并行E1/E3或优先A1×A5)

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
- **前置条件**: ✅ D4完成, D1框架就绪
- **时限**: 48小时 (从启动时计)
- **执行**: `cargo run --bin a1_a5_runner` (使用D1框架)

### P1: B6 Recovery Dynamics Metrics [SKIPPED-ARCHIVED] 📁
- **状态**: 002 current task-line terminated, B6无需继续
- **原因**: 
  - D4.4已完成8个dynamics metrics分析
  - 所有指标在3条件间完全相同
  - 当前任务环境不支持feedback advantage hypothesis
- **决策**: B6 skip, 002资源释放
- **相关任务**: B1, B2 当前不继续 (002 family archived)

### 已验证的002 Metrics (D4.4完成)
- [x] Peak drift: 0.257 (所有条件相同)
- [x] Overshoot ratio: 4.14 (所有条件相同)
- [x] Time to 50%: 0.05s (所有条件相同)
- [x] Time to 90%: 0.39s (所有条件相同)
- [x] Settling time: None (所有条件相同)
- [x] Integrated error: 0.473 (所有条件相同)
- [x] Velocity variance: 1.3059 (所有条件相同)
- [x] Jerk metric: 0.0667 (所有条件相同)
- [x] Recovery success: false (所有条件相同)

### P1: E1 Critical Coupling Sweep [PHASE A COMPLETE] ✅
**实验规格**: `E_CLASS_EXPERIMENT_SPEC.md` - E1章节
**Phase A报告**: `E1_PHASE_A_COMPLETE.md`
**结果**: ✅ **临界相变确认 - 15/15配置检测到跃迁**

#### Phase A: 粗筛 (Coarse Sweep) [COMPLETE ✅]
- [x] **E1-A.1** 确认v19接口: r, P, CI ✅
- [x] **E1-A.2** 配置参数空间: N×K×σ sweep ✅
- [x] **E1-A.3** 准备相位模型 ✅
- [x] **E1-A.4** 启动sweep: 300 configs, 0.5分钟 ✅
- [x] **E1-A.5** 观测r跃迁: **确认检测到** ✅
  - 低同步(r<0.2): 148 configs (49.3%)
  - 高同步(r>0.8): 134 configs (44.7%)
  - 临界K值: σ=0.1→~0.2, σ=0.5→~1.0, σ=1.0→~1.8

**关键发现**: 临界相变确认，Family 10升级为"主线候选"

#### Phase B: 局部加密 [READY 🔥]
- [ ] **E1-B.1** 在K_c附近加密K到50-100点
  - σ=0.1: K ∈ [0.15, 0.40]
  - σ=0.5: K ∈ [0.80, 1.10]  
  - σ=1.0: K ∈ [1.50, 2.10]
- [ ] **E1-B.2** 增加N: [5e4, 7e4, 1e5, 3e5]
- [ ] **E1-B.3** 计算临界指数、有限尺寸标度
- [ ] **E1-B.4** 测试滞后效应（不同初始条件）

**状态**: 🟢 **Phase A成功，立即启动Phase B**
**资源**: 32-48核, ~2-3小时

#### Phase C: 机制验证 [BLOCKED-B结果]
- [ ] **E1-C.1** 准备E2/E4/E5/E6测试
- [ ] **E1-A.1** 确认v19接口: r, P, CI ✅ (S(t)=[CDI, CI, r, N, E])
- [ ] **E1-A.2** 配置参数空间: N×K×σ sweep
  - N: [1e3, 3e3, 1e4, 3e4, 1e5] (5点)
  - K: 0.1-5.0 (15-20点, 对数均匀)
  - σ: [0.1, 0.5, 1.0] (3点)
  - μ: 1.0 (固定)
  - 总计: ~1200-1500 configs
- [ ] **E1-A.3** 准备相位模型 (θ + 分布, 非精确Hz)
- [ ] **E1-A.4** 启动sweep: 48-64并发, 预计4-6小时
- [ ] **E1-A.5** 观测r跃迁: 从<0.2到>0.8?

#### Phase B: 局部加密 [BLOCKED-A结果]
- [ ] **E1-B.1** 仅在发现跃迁区域加密K到50-100点
- [ ] **E1-B.2** 增加N: [5e4, 7e4, 1e5, 3e5]
- [ ] **E1-B.3** 计算临界指数、滞后效应

#### Phase C: 机制验证 [BLOCKED-B结果]
- [ ] **E1-C.1** 准备E2/E4/E5/E6测试

**资源**: 48-64核, <32GB, Phase A约4-6小时
**状态**: 🟢 **D4完成, 资源已释放(002的15%), 立即启动**
**策略**: Coarse-to-fine, 避免暴力穷举
**Kill条件**: Phase A无相变(r始终<0.3或始终>0.9) → Family 10降级

### P1: E3 Density/Percolation Threshold [READY] 🔥
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

### 002 Current Line Termination ✅
- [x] **CHECK-002.1**: D4验证8个dynamics metrics均无分离 ✅
  - 结果: **Current task-line terminated**, 资源归零
- [x] **CHECK-002.2**: 当前任务环境不支持feedback advantage hypothesis ✅
  - 结果: **002 family archived-not-deleted**, B1/B2当前不继续
- **状态**: 002归档, 未来可redesign重启

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
| A1×A5 | D1框架验证通过 | 立即可用 ✅ |
| E1/E3 | D4完成 | 立即启动 🔥 |
| B6/002 | D4发现mechanism无效 | **KILL** ❌ |
| C1 | D1框架验证通过 | D1完成后 |

---

## 📈 进度追踪

| 日期 | 完成任务 | 关键决策 |
|------|----------|----------|
| 2026-03-10 | D1 COMPLETE | Paired-seed framework validated |
| 2026-03-10 | D4 COMPLETE | D4.1-D4.5全部完成 |
| 2026-03-10 | 001 REFRAME | Fixed-marker语义问题, dynamic正常 |
| 2026-03-10 | 002 archived | Current task-line terminated |
| 2026-03-10 | E1/E3 READY | D4完成, 资源释放, 立即启动 |

---

**下次更新**: E1 Phase A启动后

**立即开始**: E1-A.1 - 确认v19接口并启动Phase A粗筛
