# Kimi 超脑组最终研究指令

**版本**: 融合版 v1.1  
**日期**: 2026-03-10  
**状态**: 立即执行  
**目标**: 将32+6个候选方向收敛为可执行的实验序列

**更新**: 新增E类 - Critical Synchronization & Emergent Rhythm (6个方向)

---

## Deliverable A: Executive Summary

### 现在最该做什么

| 优先级 | 任务 | 目标 |
|--------|------|------|
| P0 | **D4 Semantic Metric Validation** | 确认001/002指标语义正确 (001部分✅, 002待完成) |
| P0 | **D1 Paired-Seed Comparative Harness** | 建立低方差实验框架 (与D4并行) |
| P1 | **E1 Critical Coupling Sweep** | 寻找节律起始临界点 (与v19 r/CI/P对接) |
| P1 | **E3 Density/Percolation Threshold** | 测试percolation→同步→节律阈值 (与v19对接) |
| P2 | **A1 × A5 2×2因子诊断** | 定位001问题在write/read/semantic哪一层 (D4完成后) |
| P2 | **B6 Recovery Dynamics Metrics** | 确认002 signal是被metric压扁还是真的不存在 (D4完成后) |
| P3 | **C1 Episodic Failure Recall** | 第一个进主线的Hyperbrain候选验证 |

**执行顺序调整**:
1. D4 (继续) + D1 (并行启动) - 现在
2. E1 + E3 (新增) - D4 001部分完成后立即启动
3. A1×A5 + B6 - D4全部完成后启动
4. C1 - D1框架验证后启动

### 现在最不该做什么

| 类别 | 暂缓原因 |
|------|----------|
| A2/A3/A4/A6/A8 Marker语义重设计 | 先证明marker值得救，再做大修 |
| B1/B2/B3/B4/B7/B8 任务重设计 | B6未验证前，容易优化错指标 |
| C2/C5/C6 宏大规划 | 成本高、前置多、缺少已验证memory interface |
| D2/D3/D5/D7/D8 进阶验证工具 | D1/D4未落地前，属于第二层优化 |

---

## Deliverable B: 32个原始候选方向（完整保留）

### A类：001 Marker机制修正
- A1 Event-Gated Marker Writing
- A2 Uncertainty-Weighted Marker Channel
- A3 Local Relational Marker Memory
- A4 Marker-as-Router-Only
- A5 Conflict-Triggered Marker Retrieval
- A6 Counterfactual Query Cache Marker
- A7 TD-Based Marker Update
- A8 Sparse Distributed Marker Representation

### B类：002 Soft Robot任务与指标重构
- B1 Single-Shot Shape Recovery
- B2 Delayed Perturbation Anticipation
- B3 Localized Structural Damage Compensation
- B4 Dynamic Boundary Tracking
- B5 Feedback Dropout Sensitivity
- B6 Recovery Dynamics Metrics Redesign
- B7 Multi-Modal Feedback Fusion
- B8 Adversarial Perturbation Pattern

### C类：更接近超脑主线的替代机制
- C1 Episodic Failure Recall
- C2 Memory-Gated Hierarchical Planner
- C3 Self-Critique with Persistence Bias
- C4 Continuity Signature / Identity Trace
- C5 Constrained Long-Horizon Proposal Ranking
- C6 Hypothesis Memory with Anti-Oracle Boundary
- C7 Attention-Directed Memory Consolidation
- C8 Self-Model as Compressed Predictive Abstraction

### D类：验证框架与实验设计创新
- D1 Paired-Seed Comparative Harness
- D2 Adaptive Stopping Rules
- D3 Intervention-Specific Probes
- D4 Semantic Metric Validation Layer
- D5 State vs Behavior Disentangling Instrumentation
- D6 Proxy Task Redesign for Faster Falsification
- D7 Cross-Mechanism Interaction Mapping
- D8 Automated Negative Control Generation

### E类：临界同步与节律涌现 (新增)
**核心假设**: 全局节律不是中心命令触发，而是大量局部可激发单元耦合增强后跨越临界点涌现

- E1 Critical Coupling Sweep - 寻找节律起始临界点
- E2 Pacemaker Emergence vs No-Center - 测试是否需中心节律源
- E3 Density / Percolation Threshold - 测试percolation阈值假说
- E4 Hub Knockout After Rhythm Onset - 测试节律是否依赖少数hub
- E5 Noise-Assisted Synchronization - 测试微噪声是否帮助跨越临界点
- E6 Phase Reset / Re-entrainment - 测试节律是否可重置再锁相

---

## Deliverable C: 10个机制家族

| 家族 | 成员 | 核心机制 | 依赖 | 优先级 |
|------|------|----------|------|--------|
| **Family 1** Marker Write Gating | A1, A7 | 事件触发写入 | D4指标验证 | P1 |
| **Family 2** Marker Read Gating | A5, A2, A6 | 读取路径控制 | Family 1验证通过 | P2 |
| **Family 3** Marker Semantic重设计 | A3, A4, A8 | 结构与语义重设计 | Family 1/2 salvageable | P3 |
| **Family 4** Task-Perturbation设计 | B1, B2, B3, B4, B8 | 暴露feedback价值的任务 | B6指标验证 | P2 |
| **Family 5** Metric & Observability | B5, B6, B7, D4, D5 | 动态指标与可观测性 | 基础设施 | **P0** |
| **Family 6** Comparative实验框架 | D1, D2, D3, D6, D7, D8 | 控制实验设计 | 基础设施 | **P0** |
| **Family 7** Episodic Memory | C1, C3, C7 | 情景记忆与自我评估 | D1/D4 | P1 |
| **Family 8** Continuity & Identity | C4, C8 | 连续性与身份追踪 | C1有正信号 | P2 |
| **Family 9** Structured Internal Models | C2, C5, C6 | 规划与假设管理 | 高前置依赖 | P3 |
| **Family 10** Critical Synchronization | E1-E6 | 临界同步与节律涌现 | Bio-World v19框架 | **P1** |

**Family 10 与v19对接**:
- E1/E3: 与r (Kuramoto order parameter)、CI (condensation)、P (percolation)直接兼容
- 短期优先: E1 + E3 (最便宜，phase transition探测)

---

## Deliverable D: 48-72小时优先验证方案

### D4 Semantic Metric Validation

| 属性 | 内容 |
|------|------|
| **核心假设** | 001/002当前aggregate指标可能失真，导致错误结论 |
| **最小实验** | 001: 拆解coherence→sub-metrics; 002: stability→dynamics-aware metrics |
| **Kill条件** | 若指标语义验证失败，暂停001/002基于这些指标的所有结论 |
| **资源建议** | 低并发(4-8核)，retrospective分析，内存<16GB |
| **可否retrospective** | ✅ 是，优先分析现有logs |
| **可否batch** | ❌ 否，需要人工审查metric语义 |

### D1 Paired-Seed Comparative Harness

| 属性 | 内容 |
|------|------|
| **核心假设** | 配对设计可降低实验方差，提高比较可信度 |
| **最小实验** | A/A测试验证无偏差；报告variance reduction ratio |
| **Kill条件** | 若配对设计无增益或有偏差，直接kill D1 |
| **资源建议** | 中并发(16-32核)，适合sweep |
| **可否retrospective** | ❌ 否，需新实验验证框架本身 |
| **可否batch** | ✅ 是 |

### A1 × A5 2×2因子诊断

| 属性 | 内容 |
|------|------|
| **核心假设** | 001问题可通过write/read分离定位 |
| **设计** | Write Gating(off/on) × Read Gating(off/on) + ablated control |
| **Kill条件** | 若gating全无效→semantic/environment mismatch；若write harmful→kill Family 1 |
| **资源建议** | 中高并发(32-48核)，适合sweep |
| **可否retrospective** | ❌ 否，需新实验 |
| **可否batch** | ✅ 是 |

### B6 Recovery Dynamics Metrics Redesign

| 属性 | 内容 |
|------|------|
| **核心假设** | 002 signal被旧metric压扁，新metrics可暴露差异 |
| **最小实验** | Retrospective跑现有轨迹，指标：overshoot, settling time, integrated error, smoothness, final deviation |
| **Kill条件** | 若新metrics对现有batch和新batch都不分离→"controller no advantage"假设升级 |
| **资源建议** | 低并发(8核)，retrospective分析，内存<16GB |
| **可否retrospective** | ✅ 是，优先 |
| **可否batch** | ⚠️ 部分可batch后处理 |

### C1 Episodic Failure Recall

| 属性 | 内容 |
|------|------|
| **核心假设** | 失败情节记忆能改变未来行为 |
| **对照** | no memory vs random retrieval vs failure-indexed retrieval |
| **主指标** | revisit rate, time to escape repeated failure, retrieval precision/recall |
| **Kill条件** | 若无法击败random retrieval→不能进主线默认组件 |
| **资源建议** | 中等并发(16-24核)，较高内存观察 |
| **可否retrospective** | ❌ 否，需新实验 |
| **可否batch** | ✅ 是 |

### E1 Critical Coupling Sweep (新增)

| 属性 | 内容 |
|------|------|
| **核心假设** | 存在"第一声心跳"式的临界点，同步突然涌现 |
| **最小实验** | 扫描communication_strength/sync_coupling，观察r(t)从低同步区突然跳到高同步区 |
| **记录指标** | phase-lock onset time, variance collapse, population stability/hazard |
| **与v19对接** | 直接使用r (Kuramoto order parameter)、CI (condensation)、P (percolation) |
| **资源建议** | 高并发(48-64核)，参数sweep友好，内存<32GB |
| **可否retrospective** | ❌ 否，需新实验 |
| **可否batch** | ✅ 是，参数sweep ideal |

### E3 Density/Percolation Threshold (新增)

| 属性 | 内容 |
|------|------|
| **核心假设** | 细胞增多→连接增多→跨越percolation threshold后突然能同步 |
| **最小实验** | 扫描agent/cell density + 连线概率/耦合半径，观察P先跨threshold，接着r上升，再接节律稳定 |
| **与v19对接** | 直接使用P (giant component ratio)和r指标 |
| **资源建议** | 高并发(48-64核)，参数sweep，内存<32GB |
| **可否retrospective** | ❌ 否，需新实验 |
| **可否batch** | ✅ 是 |

---

## Deliverable E: 1-2周条件式路线图

```
Week 1 (当前)
├── D4 (P0) → 001指标语义验证✅, 002待完成
│   └── 并行开启: D1
├── D1 (P0) → 框架验证
│   └── 所有后续实验使用paired design
├── E1 + E3 (P1) → 临界同步/节律涌现 (D4 001后启动)
│   └── 与v19 r/CI/P指标直接对接
│   └── 若发现临界点 → E2/E4/E5/E6进入队列
└── A1×A5 (P2) → 001诊断 (D4全部完成后)

Week 2 (条件满足时)
├── A1×A5 (若D4完成) → marker诊断
│   └── 若salvageable → A2 refinement
├── B6 (若D4完成) → 002 dynamics验证
│   └── 若分离 → B1, B2
├── E1/E3结果分析
│   └── 若发现临界点 → E2/E4/E5/E6
│   └── 若无临界点 → Family 10降级
├── C1 (若D1完成) → Episodic Failure
│   └── 若正信号 → C3, C4
└── E4 Hub Knockout (若E1/E3成功)

Kill/Archive条件
├── A1×A5全无效 → 001进入ARCHIVE评估
├── B6新metrics仍不分离 → 002 KILL确认
├── C1无法击败random → C1降级
└── E1/E3无临界点 → Family 10暂不扩展(E2/E4/E5/E6暂缓)
```

---

## Deliverable F: 暂不优先投入清单

| 类别 | 暂缓项 | 重启条件 |
|------|--------|----------|
| **A类延后** | A2, A3, A4, A6, A8 | A1/A5证明marker值得救 |
| **B类延后** | B1, B2, B3, B4, B7, B8 | B6验证metrics能分离signal |
| **C类延后** | C2, C5, C6 | C1有正信号且需要扩展 |
| **D类延后** | D2, D3, D5, D7, D8 | D1/D4已落地，需要进阶工具 |
| **E类延后** | E2, E4, E5, E6 | E1/E3发现临界点后扩展 |

---

## Deliverable G: 调度与资源方案

### 96核CPU并行方案

| 任务类型 | 建议并发 | CPU分配 | 优先级 |
|----------|----------|---------|--------|
| 基础设施型(D4, D1验证) | 低(4-8核) | 观测为主 | P0 |
| E1/E3 sweep | 高(48-64核) | 参数sweep | P1 |
| A1/A5 sweep | 中高(32-48核) | 批量实验 | P2 |
| B6 retrospective | 低(8核) | 后处理分析 | P2 |
| C1 | 中等(16-24核) | 高内存观察 | P3 |

### 内存保护策略

| 参数 | 值 |
|------|-----|
| 默认保护线 | 96 GB可用内存 |
| 保护区间 | 64-128 GB |
| 行动阈值 | 低于96GB时暂停新增任务 |
| 紧急措施 | 必要时停止低优先级sweep |

### 任务准入检查表

每个批次提交前必须回答：
- [ ] 单任务峰值内存估计？
- [ ] 最大同时任务数？
- [ ] 提交后是否会把服务器压到保护线以下？
- [ ] 若答案不清楚，先以保守值上线

### 实验类型推荐

| 实验 | 并发建议 | 内存估算 | 适合批量 |
|------|----------|----------|----------|
| D4 retrospective | 4-8核 | <16GB | ❌ |
| D1 A/A测试 | 16-32核 | <32GB | ✅ |
| E1 Critical Coupling | 48-64核 | <32GB | ✅ (ideal sweep) |
| E3 Percolation | 48-64核 | <32GB | ✅ (ideal sweep) |
| A1×A5 2×2 | 32-48核 | <48GB | ✅ |
| B6 analysis | 8核 | <16GB | ⚠️ |
| C1 | 16-24核 | 24-48GB | ✅ |

---

## 调度执行检查点

### 每日检查
- [ ] free/available memory > 96GB?
- [ ] 活跃任务是否按优先级排序?
- [ ] 新任务是否完成准入检查?

### 每周检查
- [ ] Gate条件是否满足?
- [ ] Kill/Continue决策是否明确?
- [ ] 资源分配是否需调整?

---

**一句话目标**: 将Hyperbrain研究从"很多想法+异常结果"收敛为**可执行、可证伪、可调度、可进主线、可快速kill错误方向**的正式研究指令。

**立即开始**:
1. **D4继续**: 完成002部分 (stability→dynamics metrics)
2. **D1并行**: Paired-Seed框架启动
3. **准备E1/E3**: 与Bio-World v19对接，准备临界同步实验

**版本更新**:
- v1.0: 初始版本 (32候选, 9家族)
- v1.1: 新增E类 (6方向), 调整执行顺序, Family 10加入
