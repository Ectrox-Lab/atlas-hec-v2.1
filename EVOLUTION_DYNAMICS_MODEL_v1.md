# Bio-World v18 演化动力学模型 v1.0

**类型**: 三层最小可拟合模型  
**日期**: 2026-03-09  
**约束**: 所有变量必须从CSV可测量，禁止理论推测

---

## 模型架构

```
Layer A: Population Dynamics (最底层，必须最稳)
    ↓
Layer B: CDI Dynamics (复杂度增长)
    ↓
Layer C: Cooperation Gate (门控函数，非主方程)
```

---

## Layer A: Population / Survival Dynamics

### 主方程

```
dN/dt = N(t) × (r_eff(t) - m_eff(t))
```

### 有效出生率

```
r_eff(t) = r₀ + r_D·D(t) + r_A·A(t) + r_C·C(t)
```

| 符号 | 定义 | 测量方法 |
|------|------|---------|
| r₀ | 基础出生率 | CSV: births/population at t=0 |
| r_D | DNA适应增益系数 | 拟合参数 |
| D(t) | DNA平均适应参数 | CSV: avg(dna_params) |
| r_A | 阿卡西增益系数 | 拟合参数 |
| A(t) | 阿卡西学习 boost | CSV: akashic_stats.learning_boost |
| r_C | 协作增益系数 | 拟合参数 |
| C(t) | 协作强度 | CSV: collaboration_index |

### 有效死亡率

```
m_eff(t) = m₀ + m_B·B(t) + m_V·V_E(t)
```

| 符号 | 定义 | 测量方法 |
|------|------|---------|
| m₀ | 基础死亡率 | CSV: deaths/population at t=0 |
| m_B | Boss压力系数 | 拟合参数 |
| B(t) | Boss压力强度 | CSV: boss_disturbance_avg |
| m_V | 能量方差惩罚 | 拟合参数 |
| V_E(t) | 群体能量方差 | CSV: var(energy) across cells |

### 这层回答的问题

> 为什么种群上升、稳定或灭绝？

---

## Layer B: Complexity / CDI Dynamics

### 主方程（RyanX 资源受限版正式化）

```
dI/dt = (λ₁·M(t) + λ₂·S(t) + λ₃·C(t)) × (1 - I/K_I) - λ₄·V_E(t) - λ₅·B(t)
```

### 变量定义（全部CSV可测）

| 符号 | 定义 | 测量方法 | 单位 |
|------|------|---------|------|
| I(t) | CDI (复杂度指数) | CSV: cdi_avg | [0, 1] |
| M(t) | 有效记忆深度 | CSV: mem_ret (memory retention) | [0, 1] |
| S(t) | 信号/同步质量 | CSV: pha_coh (phase coherence) | [0, 1] |
| C(t) | 协作强度 | CSV: collaboration_index | [0, 1] |
| V_E(t) | 能量方差 | CSV: energy_var | normalized |
| B(t) | Boss扰动强度 | CSV: boss_disturbance | [0, 1] |
| K_I | CDI承载上限 | 拟合参数（预期≈0.8） | [0, 1] |

### 系数（全部拟合）

| 系数 | 物理意义 | 预期符号 |
|------|---------|---------|
| λ₁ | 记忆对复杂度的贡献 | + |
| λ₂ | 同步对复杂度的贡献 | + |
| λ₃ | 协作对复杂度的贡献 | + |
| λ₄ | 能量不稳定惩罚 | - |
| λ₅ | Boss扰动惩罚 | - |

### 这层回答的问题

> 复杂度如何增长？何时饱和？

### 与RyanX原式的对应

```
原式: dI/dt = (αL + βT)(1 - I/K) - γσ²

本模型: dI/dt = (λ₁M + λ₂S + λ₃C)(1 - I/K_I) - λ₄V_E - λ₅B

对应关系:
- L (语言) → M (记忆) + S (同步)  [v18当前无独立语言变量]
- T (工具) → C (协作)              [协作是v18可测的最接近"工具"的变量]
- σ² (资源波动) → V_E (能量方差)
- γσ² → λ₄V_E + λ₅B               [Boss扰动作为额外惩罚]
```

---

## Layer C: Cooperation Threshold

### 设计原则

**协作不作为独立主方程，而作为门控函数。**

避免与Layer A的r_C·C(t)重复计数。

### 门控函数

```
C(t) = σ((G(t) - θ(t)) / τ)

其中 sigmoid: σ(x) = 1 / (1 + e^(-x))
```

### 协作净收益

```
G(t) = w₁·boss_reward + w₂·neighbor_support - w₃·signal_cost - w₄·movement_cost
```

| 符号 | 定义 | 测量方法 |
|------|------|---------|
| w₁ | Boss击败奖励权重 | 拟合参数 |
| boss_reward | 击败Boss的累积收益 | CSV: boss_defeat_count × energy_gain |
| w₂ | 邻居支持权重 | 拟合参数 |
| neighbor_support | 邻居协作带来的能量节省 | CSV: energy_saved_by_collaboration |
| w₃ | 信号成本权重 | 拟合参数 |
| signal_cost | 信号发送能量消耗 | CSV: signal_investment × energy |
| w₄ | 移动成本权重 | 拟合参数 |
| movement_cost | 位置移动能量消耗 | CSV: move_count × move_cost |

### 协作门槛

```
θ(t) = θ₀ - θ_D·dna_collab - θ_A·akashic_prior
```

| 符号 | 定义 | 测量方法 |
|------|------|---------|
| θ₀ | 基础门槛 | 拟合参数 |
| θ_D | DNA协作倾向降低门槛 | 拟合参数 |
| dna_collab | DNA协作参数 | CSV: dna.collaboration_willingness |
| θ_A | 阿卡西经验降低门槛 | 拟合参数 |
| akashic_prior | 阿卡西协作经验 | CSV: akashic.collaboration_pattern_count |

### 温度参数

```
τ: 探索-利用温度
    - τ → 0: 刚性门槛（要么协作要么不协作）
    - τ → ∞: 完全随机（门槛失效）
```

### 这层回答的问题

> 在什么条件下，系统从单体行为切换到协作行为？

---

## K 分解（核心洞察）

```
K_I = f(K_space, K_resource, K_synaptic)

其中:
- K_space = 5000 (25×25×8 grid)
- K_resource = f(energy_spawn_rate, decay_rate)
- K_synaptic = 15/cell × max_cells

已查明的硬编码限制:
- K_population = 500 (硬编码 MAX_POPULATION)
- K_synaptic = 15/cell (硬编码 max_synapses)
- K_cdi_observed ≈ 0.8 (系统涌现表现)
```

---

## 超线性判定（严格版）

### 弱判定（Kimi版，不足够）

```
d²I/dt² > 0 ∧ dN/dt > 0
```

问题：局部加速不等于超线性 regime。

### 强判定（建议版）

离散化形式：

```
ΔI_t > α + β·I_t, 其中 β > 0

即: 增长速度本身随复杂度增加而增加
```

连续形式：

```
dI/dt > a + b·I, 其中 b > 0
```

物理意义：
- 系统进入自催化状态
- 复杂度产生更多复杂度
- 正反馈主导

---

## 拟合任务清单

### Task 1: 拟合 Population 层

**输入**: evolution.csv

**目标**: 
```
min RMSE(N_model(t) - N_observed(t))
```

**待拟合参数**: r₀, r_D, r_A, r_C, m₀, m_B, m_V

**输出**:
- 参数值 ± 置信区间
- RMSE, R²
- 残差图

### Task 2: 拟合 CDI 层

**输入**: evolution.csv

**目标**:
```
min RMSE(I_model(t) - I_observed(t))
```

**待拟合参数**: λ₁, λ₂, λ₃, λ₄, λ₅, K_I

**输出**:
- 参数值 ± 置信区间
- RMSE, R²
- 残差图
- K_I 估计值（验证是否为~0.8）

### Task 3: 拟合 Cooperation Gate

**输入**: evolution.csv (Boss3+时期数据)

**目标**:
```
max log-likelihood(C_observed | C_model)
```

**待拟合参数**: w₁, w₂, w₃, w₄, θ₀, θ_D, θ_A, τ

**输出**:
- 参数值 ± 置信区间
- ROC曲线
- 门槛θ(t)时间序列

---

## 禁止事项

| 禁止 | 原因 |
|------|------|
| ❌ 编造参数 | 必须用CSV数据拟合 |
| ❌ 使用未定义变量 L, T | v18当前无独立语言/工具测量 |
| ❌ 声称相变成立 | 必须先拟合再判定 |
| ❌ 层间重复计数 | C(t)只在Layer A出现，Layer C是门控 |
| ❌ 未运行就输出"理论值" | 必须实际拟合 |

---

## 交付物

1. **EVOLUTION_DYNAMICS_MODEL.md** (本文件)
2. **fit_population_model.py** - Layer A 拟合脚本
3. **fit_cdi_model.py** - Layer B 拟合脚本
4. **fit_cooperation_gate.py** - Layer C 拟合脚本
5. **MODEL_VALIDATION_REPORT.md** - 验证报告

---

## 下一步行动

1. [ ] 从CSV提取所有需要的时间序列
2. [ ] 运行三层拟合
3. [ ] 验证K_I ≈ 0.8
4. [ ] 测试K→∞预测
5. [ ] 设计K=500→5000实验验证

---

**模型状态**: 待拟合  
**预期完成**: 待数据准备后24小时内
