# E1 夜间长跑批次任务单 [2026-03-10]

**批次名称**: E1 Overnight Long-Run Validation  
**执行时长**: 2-4小时（睡前启动，明晨收结果）  
**资源预算**: 48-64核，内存保护线64-128GB

---

## 一、实验设计

### 核心目标
验证E1 Phase B发现的一阶相变在长跑程下的稳定性与机制硬化：
- **滞后效应**是否长期保持
- **双稳态**是否稳定
- **K_c收敛**是否经得起长跑验证

### 对照组设计（3组）

| 组别 | K值 | 预期状态 | 核心验证点 |
|------|-----|----------|-----------|
| **CTRL** | K_c - Δ | 无序相 (r<0.3) | 长期保持低同步 |
| **CRIT** | K_c | 临界区 | 滞后、双稳态、路径依赖 |
| **HIGH** | K_c + Δ | 有序相 (r>0.8) | 长期保持高同步 |

**Δ = 0.15** (基于Phase B观察的过渡区宽度)

### σ层设计（3层）

| σ | K_c | CTRL | CRIT | HIGH |
|---|-----|------|------|------|
| 0.1 | 0.25 | 0.10 | 0.25 | 0.40 |
| 0.5 | 1.00 | 0.85 | 1.00 | 1.15 |
| 1.0 | 1.70 | 1.55 | 1.70 | 1.85 |

### 种子设计
- **5对paired seeds**（10个独立种子）
- **CRIT组额外**: ordered init vs random init（测试滞后）

### 总配置数
```
CTRL:  3σ × 5 seeds = 15
CRIT:  3σ × 5 seeds × 2 init = 30
HIGH:  3σ × 5 seeds = 15
总计: 60 configs
```

---

## 二、执行参数

| 参数 | 设置 |
|------|------|
| N | 50,000 (固定) |
| 代数 | 10,000 generations |
| dt | 0.005 |
| 记录起点 | 1,000 (跳过瞬态) |
| 并发 | 48线程 (内存保护) |

---

## 三、采集指标（v19统一状态向量）

| 指标 | 符号 | 说明 | 记录方式 |
|------|------|------|----------|
| 同步度 | r | Kuramoto order parameter | 全程时间序列 |
| 凝聚指数 | CI | Phase clustering degree | final state |
| 渗流比例 | P | Giant component proxy | final state |
| 早期r | r_early | avg gen 0-2000 | 轨迹特征 |
| 中期r | r_mid | avg gen 2000-5000 | 轨迹特征 |
| 晚期r | r_late | avg gen 5000-10000 | 轨迹特征 |
| 稳定性 | stability | r variance (last 1000) | 收敛度 |
| 初始r | r_init | generation 0 | 起点状态 |
| 路径偏差 | r_path_deviation | \|r_final - r_expected\| | 路径依赖 |

---

## 四、预期产出

### 主产出
1. **长程稳定性确认**: CTRL/HIGH是否保持各自相区
2. **临界区硬化**: CRIT是否显示更强滞后/双稳态证据
3. **路径依赖量化**: ordered vs random init在CRIT组的差异

### 关键判断点
| 观察 | 解读 |
|------|------|
| CRIT组r_ordered - r_random > 0.3 | ✓ 强滞后确认 |
| CRIT组r分布双峰 (r<0.3 和 r>0.7) | ✓ 双稳态确认 |
| CTRL/HIGH组stability < 0.01 | ✓ 长期稳定 |
| 与Phase B结果一致 | ✓ 可重复性确认 |

---

## 五、资源与安全

### 内存保护
- 启动前检查: `free -h` 确认 available > 128GB
- 运行中监控: 若available < 64GB，暂停新增任务
- 并发控制: 固定48线程，不超额订阅

### 启动命令
```bash
cd /home/admin/atlas-hec-v2.1-repo/src/candidates/e1_critical_coupling
nohup cargo run --release --bin e1_overnight > /tmp/e1_overnight.log 2>&1 &
```

### 监控命令
```bash
tail -f /tmp/e1_overnight.log        # 进度
ps aux | grep e1_overnight            # 进程状态
free -h                               # 内存检查
```

---

## 六、明晨检查点

**触发条件**: 批次完成（预计2-4小时）

**检查清单**:
- [ ] `results/e1_overnight_batch/overnight_results.csv` 存在
- [ ] 60 configs全部完成
- [ ] 无NaN/异常值
- [ ] CRIT组滞后效应确认

**决策分支**:
| 结果 | 行动 |
|------|------|
| 滞后效应强 + 双稳态确认 | → E-class机制级主线地位加固 |
| 结果不一致/异常 | → 人工审查，不自动推进 |
| 资源/系统问题 | → 暂停，请求人工决策 |

---

## 七、不跑的（资源保护）

**今晚明确不启动**:
- ❌ E2 pacemaker emergence
- ❌ E4 hub knockout
- ❌ E5 noise-assisted sync
- ❌ E6 phase reset
- ❌ 001 A1×A5（等E1长跑结果）

**理由**: E1机制硬化是当前最高优先级，其他任务等结果后再解锁。

---

**批次版本**: v1.0  
**创建**: 2026-03-10  
**执行状态**: READY TO LAUNCH
