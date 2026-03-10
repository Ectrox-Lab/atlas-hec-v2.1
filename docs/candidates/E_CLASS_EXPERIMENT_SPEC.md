# E类实验规格：临界同步与节律涌现

**版本**: v1.0  
**日期**: 2026-03-10  
**策略**: Coarse-to-fine, 避免暴力穷举  
**对接**: Bio-World v19 Unified Framework

---

## 核心设计原则

### 不做
- ❌ 全频率暴力穷举（374.000001 Hz精细扫描）
- ❌ 每个单元固定超高精度频率再全组合
- ❌ 每tick全量高精度同步计算
- ❌ 绝对N暴力扫描（直接扫到10亿）

### 做
- ✅ **相位模型化**：每个单元一个phase θ，不是精确Hz
- ✅ **分布参数化**：ω ~ Normal(μ, σ)，只扫μ和σ
- ✅ **关键控制参数**：coupling K, density/connectivity, heterogeneity σ
- ✅ **粗到细搜索**：Phase A粗筛 → Phase B局部加密 → Phase C机制验证
- ✅ **v19指标对接**：直接使用r, P, CI, S(t)=[CDI, CI, r, N, E]

---

## E1: Critical Coupling Sweep

### 核心问题
是否存在"第一声心跳"式的临界点？耦合强度跨越某个阈值时，全局同步突然涌现。

### 实验设计

#### Phase A: 粗筛 (Coarse Sweep)
**目标**: 找是否存在相变区域

| 参数 | 范围 | 点数 | 说明 |
|------|------|------|------|
| N (系统规模) | 1e3, 3e3, 1e4, 3e4, 1e5 | 5 | 有限尺度测试 |
| K (coupling strength) | 0.1 - 5.0 | 15-20 | 对数均匀分布 |
| σ (heterogeneity width) | 0.1, 0.5, 1.0 | 3 | 固定几个离散度 |
| μ (平均频率) | 1.0 | 1 | 固定，不测绝对频率 |

**总配置数**: 5 × 20 × 3 = 300
**每配置seeds**: 3-5
**总运行数**: ~1200-1500

**观测指标** (v19已有):
- r(t) = |Σe^(iθ_j)| / N - Kuramoto order parameter
- r_mean (时间平均)
- r_variance (稳定性)
- onset time (达到r > 0.5的时间)

**通过标准** (任一满足即进入Phase B):
- [ ] 某K区间内r从<0.2跃迁到>0.8
- [ ] r的variance在某个K区间突然塌陷
- [ ] 不同N的跃迁点显示收敛趋势

#### Phase B: 局部加密 (Fine Sweep)
**目标**: 精确定位临界点

仅对Phase A发现跃迁的(K, N)区域:
- K加密到50-100个点
- 在该区域增加N: 5e4, 7e4, 1e5, 3e5

**额外观测**:
- 临界指数 (critical exponent)
- 滞后效应 (hysteresis)
- 多稳态 (multistability)

#### Phase C: 机制验证 (Mechanism)
**目标**: 验证同步的机制

若Phase B确认临界点:
- [ ] **E2预备**: Pacemaker Emergence测试
- [ ] **E4预备**: Hub Knockout测试
- [ ] **E5预备**: Noise-Assisted Sync测试

### 资源估算

| Phase | 并发建议 | CPU | 内存 | 时间 |
|-------|----------|-----|------|------|
| A | 48-64核 | ~1200 runs | <32GB | ~4-6小时 |
| B | 32-48核 | ~500 runs | <32GB | ~3-4小时 |
| C | 16-24核 | 单独设计 | <32GB | 视结果定 |

### Kill条件
- Phase A: 所有配置r都<0.3或都>0.9（无相变）
- Phase B: 跃迁点随N增加而发散（无收敛临界）
- 若Kill: Family 10降级，不进入E2/E4/E5/E6

---

## E3: Density / Percolation Threshold

### 核心问题
细胞增多→连接增多→跨越percolation threshold后突然能同步。测试P → r的因果关系。

### 实验设计

#### Phase A: 粗筛
**目标**: 找P与r的关联

| 参数 | 范围 | 点数 | 说明 |
|------|------|------|------|
| N | 1e3, 1e4, 1e5 | 3 | 固定规模 |
| K | 固定几个值（E1中找到的临界区） | 3 | 用E1结果 |
| density / average degree ⟨k⟩ | 0.5 - 5.0 | 15-20 | 覆盖k≈1阈值 |
| connection radius | 自适应 | - | 局部连接 |

**总配置数**: 3 × 3 × 20 = 180
**每配置seeds**: 5
**总运行数**: ~900

**观测指标** (v19已有):
- P = largest_component_size / N (percolation ratio)
- r (同步程度)
- CI (condensation index)
- 时序: P先上升？r后上升？

**通过标准**:
- [ ] P在某个⟨k⟩区间跳变（percolation threshold）
- [ ] r的上升滞后于P的上升
- [ ] 不同N的percolation threshold显示收敛

#### Phase B: 因果验证
**目标**: 验证P → r的因果链

- 固定P在某个值（如P=0.5），变化其他参数，看r是否响应
- 扰动实验：突然切断部分连接使P下降，观察r是否跟随

### 与E1的关联

```
E1结果 ─┬─→ 若发现K临界区 ──────┐
        │                        ├──→ E3 Phase B精细验证
        └─→ 若K临界区与N无关 ────┘
        
E3结果 ─┬─→ 若P-r因果成立 ────┐
        │                      ├──→ 确认"连通性→同步"链条
        └─→ 若percolation阈值 ─┘
```

### 资源估算

| Phase | 并发建议 | CPU | 内存 | 时间 |
|-------|----------|-----|------|------|
| A | 48-64核 | ~900 runs | <32GB | ~3-4小时 |
| B | 16-32核 | ~300 runs | <32GB | ~2-3小时 |

---

## 96核调度方案

### 并行策略

```
总资源: 96核

时段1 (0-6小时): E1 Phase A
├── 64核: E1 sweep (max parallel)
├── 16核: D1 A/A测试 (背景)
└── 16核: D4 002分析 (背景)

时段2 (6-10小时): E1 Phase B + E3 Phase A
├── 48核: E1 Phase B (加密)
├── 48核: E3 Phase A (并行的同时启动)

时段3 (10-14小时): E3 Phase B + 分析
├── 32核: E3 Phase B
├── 32核: 结果分析 + 可视化
└── 32核: 预留/其他

内存保护: 始终保留96GB可用
```

### 任务准入检查

每个sweep批次提交前:
- [ ] 单任务内存峰值 < 500MB (相位模型轻量)
- [ ] 并发任务数 × 500MB < 32GB (96核时约64并发)
- [ ] 系统剩余内存 > 96GB

---

## 与Bio-World v19对接

### 直接使用v19定义

```rust
// v19 Unified State Vector
S(t) = [CDI, CI, r, N, E]

// 其中:
// r = |Σ e^(iθ_j)| / N  (我们需要的同步指标)
// P = largest_component / N (连通性指标)
// CI = condensation index (结构凝聚)
```

### 采样频率优化

遵循v19 roadmap建议:
- 不每tick计算r, P, CI
- 每10 generations计算一次（性能优化）
- 但在相变区附近可加密到每5 generations

### 风险缓解（v19已有）

| 风险 | v19已有缓解策略 | E1/E3采用 |
|------|----------------|-----------|
| CI太贵 | sample-based, 只看top 10% hubs | ✅ 采用 |
| sync太噪 | moving average smoothing | ✅ 采用 |
| 性能过高 | 每10 generations计算 | ✅ 采用 |
| 相位定义 | 可由多种行为定义，不执着于单一频率 | ✅ 采用 |

---

## 预期产出

### 最小可接受结果

| 产出 | 标准 | 决定 |
|------|------|------|
| Phase A r-plot | 显示明显跃迁区 | Continue to Phase B |
| Phase B 临界收敛 | 临界K随N收敛 | Continue to Phase C (E2/E4/E5/E6) |
| E3 P-r因果 | P先上升，r后上升 | 确认"连通性→同步"链条 |
| 无上述任何 | 无相变或因果 | Kill Family 10扩展 |

### 可视化要求

1. **r vs K** 曲线（不同N叠加）
2. **P vs ⟨k⟩** 曲线（percolation threshold）
3. **r vs P** 散点图（因果验证）
4. **临界K vs N** 收敛图（finite-size scaling）

---

## 与D4/D1/A1×A5的协调

```
Week 1 执行流:

Day 1-2: D4 (002部分) + D1并行
         └── 产出: 002 metrics理解
         
Day 2-3: E1 Phase A启动 (利用D4间隙)
         └── 粗筛coupling空间
         
Day 3-4: E1 Phase A完成 → 决策
         ├── 若发现跃迁 → Phase B
         └── 若无跃迁 → Family 10降级标记
         
Day 4-5: E3 Phase A启动 (与E1 Phase B并行)
         └── 粗筛density/percolation
         
Day 5-6: E1 Phase B + E3 Phase B
         └── 精确定位临界点
         
Day 6-7: 分析 + 决策
         ├── 若成功 → 准备E2/E4/E5/E6
         └── 若失败 → 资源转回A1×A5
```

---

## 关键判断标准

### 这条线"值得继续"的最低标准

**不是**找到最终N_crit = ?

**而是**满足以下任一:
1. 有限尺度下，r出现稳定跃迁
2. P的形成和r的上升存在稳定先后关系
3. 随N扩大，临界区不是乱飘，而是有收敛趋势
4. 相变区附近的hazard/stability明显变化

只要有这些，就已经不是在瞎试，而是在抓一条真正的临界同步机制。

---

## 总结

| 问题 | 答案 |
|------|------|
| 要扫精确频率吗？ | 不，用相位θ + 分布(μ,σ) |
| 要扫到10亿N吗？ | 不，有限尺度(1e3-1e5)看收敛趋势 |
| 用什么指标？ | v19已有：r, P, CI |
| 怎么调度？ | 96核：E1/E3 sweep并行，粗到细 |
| Kill条件？ | 无相变、无因果、无收敛 |
| 成功标准？ | 有跃迁、有因果、有收敛趋势 |

**立即开始**: E1 Phase A粗筛 (coupling sweep)
