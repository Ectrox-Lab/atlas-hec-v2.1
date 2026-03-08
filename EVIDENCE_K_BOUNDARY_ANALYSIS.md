# K 边界来源与增长形态证据分析

## 第 1 轮：找 K（承载容量来源）

### Atlas V5 硬编码限制

**文件**: `zeroclaw-labs/atlas_evo_v5/src/main.rs`

```rust
Line 218: const MAX_POPULATION: usize = 500; // 人口上限
Line 220-223: 
    if self.cells.len() >= MAX_POPULATION {
        self.cells.truncate(MAX_POPULATION);
    }

Line 190: if !already_connected && self.cells[i].synapses.len() < 15
Line 208-211:
    if self.cells[i].synapses.len() > 15 {
        self.cells[i].synapses.truncate(15);  // 只保留最强的15个连接
    }
```

**结论**: 
- ✅ **K_population = 500** 是代码硬上限
- ✅ **K_synapses_per_cell = 15** 是代码硬上限
- 观测到的 882 总突触是 500 cells × ~1.76 平均连接（稀疏连接）的结果

---

## 第 2 轮：找 Innovation Metric (I)

### ACN Evolution Grid 实验中的 CDI 指标

**文件**: `acn_evolution_grid/baseline_v18_1.csv` (100,000代)

**列定义**:
- `cdi_avg`: CDI 平均值
- `cdi_max`: CDI 最大值  
- `cdi_var`: CDI 方差
- `cdi_growth`: CDI 增长率

### CDI 增长轨迹

| 代数 | 种群 | cdi_max | cdi_growth |
|------|------|---------|------------|
| 1 | 100 | 0.121 | 0.206 |
| 10 | 101 | 0.242 | 0.052 |
| 100 | 109 | **0.600** | **0.000** |
| 500 | 160 | 0.606 | -0.000 |
| 1000 | 75 | 0.633 | 0.000 |
| 5000 | 33 | 0.633 | 0.001 |
| 100000 | 29 | **0.800** | **0.001** |

### 不同实验条件的收敛结果

| 实验 | 条件 | Gen 50000 pop | Gen 50000 cdi_max | cdi_growth |
|------|------|---------------|-------------------|------------|
| AGENT_01 | MENTOR_CAP | 29 | 0.733 | 0.000 |
| AGENT_02 | FREQ_NOISE | 35 | 0.700 | 0.001 |
| AGENT_03 | ENERGY_CAP | 48 | 0.733 | 0.001 |
| AGENT_04 | DIVERSITY_FORCE | 52 | **0.800** | 0.000 |
| AGENT_14 | CONTROL | 34 | 0.700 | 0.001 |

**结论**:
- ✅ **Innovation Metric I = CDI** (Complexity Development Index?)
- ✅ CDI 在所有实验中都收敛到 **0.7-0.8** 区间
- ✅ 不同条件只影响收敛速度和最终种群的稳定性，不改变饱和形态

---

## 第 3 轮：找超线性案例

### 增长形态判定

**CDI 增长曲线**:
```
CDI
 0.8 ├────────────────────────────  ← 饱和平台 (K_cdi ≈ 0.8)
     │                        ╱
 0.6 ├───────────────────╱
     │               ╱
 0.4 ├──────────╱
     │      ╱
 0.2 ├─╱
     │
   0 └────┬─────┬─────┬────────────► Gen
         100   500  50000
         
    快速增长期 │  饱和期
```

**关键观察**:
- 早期（Gen 1-100）：近似指数增长（0.121 → 0.600）
- 中期（Gen 100-1000）：增速急剧下降
- 后期（Gen 1000-100000）：几乎平坦（0.633 → 0.800，10万代仅+27%）

### 与理论预测对比

| 预测 | 数学形式 | 观测 | 符合 |
|------|---------|------|------|
| 线性 | I ∝ t | ❌ 增速变化 | - |
| 指数 | I ∝ e^rt | ❌ 有明确上限 | - |
| **S曲线** | **Logistic** | **✅ 匹配** | **符合** |
| 超线性 | I ∝ t^p (p>1) | ❌ 无加速 | - |
| 超指数 | I ∝ e^(e^rt) | ❌ 无爆发 | - |

---

## 综合结论

### K 的来源
| K类型 | 来源 | 性质 | 可调性 |
|-------|------|------|--------|
| K_population | MAX_POPULATION = 500 | 硬编码 | ✅ 可改 |
| K_synapses | 15 per cell | 硬编码 | ✅ 可改 |
| K_cdi | ~0.8 | 系统涌现 | ❓ 待研究 |

### Innovation Metric
- **I = CDI** (在ACN实验网格中)
- CDI 可能对应：综合复杂度发展指数
- 但目前定义不明确，需要进一步澄清

### 增长形态
- **当前证据强烈支持 S曲线 (Logistic) 模型**
- **未观察到任何超线性或超指数增长的案例**

### RyanX 定律的修正形式

```
当前证据支持的版本 (Resource-Limited Form):

dI/dt = (αL + βT)(1 - I/K_cdi) - γσ²

其中 K_cdi ≈ 0.8 (系统涌现的复杂度上限)

待验证的假说 (Unbounded Form):

当 K_cdi → ∞ (移除架构限制) 时，
是否会出现 L×T > θ_critical ⇒ 超线性相变？

目前状态：❓ 待验证（无实验数据支持）
```

---

## 下一步建议

1. **明确 CDI 定义**: 在代码中找到 CDI 的计算公式
2. **测试 K_cdi 可调性**: 修改 MAX_POPULATION 和 synapse limit，观察是否会影响 CDI 上限
3. **设计无界实验**: 如果可能，移除所有硬编码上限，测试是否会出现持续加速增长
4. **接受 S曲线**: 如果 K 是系统固有属性，则将 RyanX 定律调整为 Logistic 形式
