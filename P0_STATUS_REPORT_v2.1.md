# P0 Hazard Rate Protocol v2.1 - Status Report

**日期**: 2026-03-09  
**协议版本**: P0 v2.1 (措辞修订)  

---

## 核心结论（修订版措辞）

> CDI measures structural quality rather than merely population size. In Bio-World v18.1, CDI degradation precedes both population decline and extinction onset, indicating that CDI functions as a **leading indicator of system instability**.

---

## 关键时序证据链（2-seed验证）

```
结构质量退化 → 系统脆弱化 → 数量崩塌 → 灭绝连锁

Gen 1600: CDI=0.680, Pop=17558  [峰值]
    ↓
Gen 3200: CDI=0.643, Pop=17558  [CDI开始下降，Pop未变]
    ↓ 500代领先
Gen 3700: CDI=0.630, Pop=15959  [Pop开始下降]
    ↓ 2800代
Gen 6500: CDI=0.539, Pop=790    [首次灭绝]
```

### 时间领先证据

| 指标 | 数值 | 意义 |
|------|-----|------|
| CDI领先Pop下降 | **500代** | 结构质量先于数量恶化 |
| CDI领先首次灭绝 | **3300代** | 长程预警窗口 |

---

## 科学地位评估

### 已确立（中强到强）

✅ **CDI是leading indicator**
- 时序领先：CDI下降明显早于Pop下降（500代）
- 非proxy验证：CDI下降时Pop仍为峰值（17558）

### 待验证（5-seed实验）

⏳ **CDI stability threshold (~0.52)**
- 当前：2-seed显示 I_crit = 0.519 ± 0.0002
- 需要：5-seed验证 CV < 10%

⏳ **Hazard rate modulation**
- 危险区vs安全区危险率比 > 2x
- 生存曲线按CDI区显著分离

### 未证明（P1阶段）

❓ **CDI是因果变量（causal state variable）**
- 需要扰动实验：
  - 删除memory → CDI应更快下降 → 更快灭绝
  - 降低cooperation → 验证CDI component
  - 提高boss pressure → 测试危险率响应

---

## 科学表述规范

### 避免（证据不足）

❌ "人工生命领域首个复杂度-稳定性临界阈值"

### 采用（证据支持）

✅ "Bio-World v18.1 provides strong evidence for a complexity–stability threshold within this artificial life system."

---

## 5-Seed实验执行计划

### 启动命令

```bash
# 后台运行（预计15小时）
nohup ./run_cross_seed_experiments.sh 5 7000 > cross_seed_run.log 2>&1 &

# 监控
ps aux | grep atlas-hec
tail -f cross_seed_run.log
ls -lt /home/admin/zeroclaw-labs/v18_1_experiments/cross_seed_*/evolution.csv
```

### 验收标准（三维度）

| 维度 | 权重 | 目标 | 当前(2-seed) |
|------|-----|------|-------------|
| I_crit稳定性 | 40% | 0.52 ± 0.01 | ✅ 0.519 ± 0.0002 |
| Hazard ratio | 40% | > 2x | ⏳ 待验证 |
| 生存曲线分离 | 20% | 明显分离 | ⏳ 待验证 |

### 最终评级

| 评级 | 标准 | 下一步 |
|-----|------|--------|
| **A (80-100)** | I_crit CV<5%, HR>5x | 进入P1 (Hazard Model v3 + 扰动实验) |
| **B (60-79)** | I_crit CV<10%, HR>2x | 补充3个seed或调整模型 |
| **C (40-59)** | I_crit在[0.45,0.60], HR>1.5x | 重新审视假设 |
| **D (<40)** | 不满足上述 | 返回问题定义 |

---

## 当前成果清单

| 成果 | 证据强度 | 状态 |
|------|---------|------|
| 三阶段灭绝动力学 | 强 | ✅ 已验证 |
| CDI时序领先性 | 中强-强 | ✅ 500代领先 |
| I_crit ≈ 0.52 | 中 | ⏳ 2-seed, 等5-seed |
| Hazard modulation | 中 | ⏳ 待验证 |
| 因果性 | 未证明 | ❓ P1阶段 |

---

## P1预览（成功后启动）

如果P0评级A或B：

```
P1: Causal Perturbation Experiments

目标: 将CDI从leading indicator推向causal state variable

实验设计:
  1. Memory deletion: CDI应更快下降
  2. Cooperation reduction: 验证component贡献
  3. Boss pressure increase: 测试危险率响应

理论问题:
  CDI改变是否因果性地改变灭绝动力学？
```

---

## 总结

当前Bio-World v18.1已建立：

```
观察 → 时序分解 → Leading indicator确认 → 待验证机制
```

下一步：**5-seed统计验证**，目标是将"有意思的观察"升级为"稳定的系统规律"。

---

*报告版本*: v2.1  
*修订*: 措辞规范化，避免过度宣称  
*下一步*: 5-seed实验运行与最终评级
