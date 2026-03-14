# Atlas-HEC v2.1 Project Rules

> **Version**: 2.0.0  
> **Status**: ACTIVE  
> **Effective**: 2026-03-15

---

## Hard Rule: Execution Window, Not Physical Clock

### 核心原则

**约束对象不是原始物理时间，而是预算窗口内的真实执行。**

因为 bio-world / code-world 时间可以相对物理世界加速，真正重要的是：

1. **真实执行** - 实际发生的计算和状态转移
2. **真实评估** - 明确的阈值判定逻辑
3. **真实产出** - 可审计的 metrics / 决策记录
4. **真实反馈** - 正/负信号才允许进入下一窗口

### 时间定义

| 时间类型 | 定义 | 作用 |
|---------|------|------|
| **物理时间** | 现实 wall-clock time | 人类审批节奏、资源管理 |
| **Bio-world 时间** | 系统内部可加速的运行时间 | 真实执行发生的时间域 |
| **预算窗口** | 单次授权的执行单元 | Ralph 守门的基本单位 |

### 窗口纪律

```
Window N:
    ├─ 执行真实计算 (bio-world 时间可加速)
    ├─ 产生状态变化 (非伪造的独立结果)
    ├─ 生成 auditable outputs (metrics.json)
    ├─ 阈值评估 (POSITIVE_AUTO / POSITIVE_MANUAL / MARGINAL / FAIL)
    └─ Ralph 决策 → 停止
              ↓
    人工审查或自动批准 (严格阈值下)
              ↓
Window N+1 授权
```

### Ralph 守门规则

```python
# Ralph 是预算窗口守门员，不是物理时钟看守

if verdict == "POSITIVE_AUTO":  # ≥10pp AND ≥90%
    → 自动批准，继续下一窗口
    
elif verdict == "POSITIVE_MANUAL":  # ≥5pp AND ≥85%
    → 生成申请，等待人工确认
    
elif verdict in ["MARGINAL", "FAIL"]:
    → 冻结，等待人工决策
```

### 真实性验证标准

每个窗口必须留下：

| 验证项 | 检查点 | 审计文件 |
|--------|--------|----------|
| 真实执行 | data_checksum 唯一 | metrics.json |
| 真实评估 | verdict 明确 | decision.json |
| 真实产出 | 文件存在且非空 | hour_N/ 目录 |
| 审计追踪 | SHA256 + 时间戳 | decision.json |

---

## T0 - 预算窗口规则 (Budget Window Rule)

### 规则定义

**每个执行窗口必须产生真实可检验反馈，才允许进入下一窗口。**

### 自动批准与续时

Ralph **可以自动批准并继续下一窗口**，但阈值必须严格到**人工确认级别**。

### 自动批准标准（严格阈值）

| 条件 | 阈值 | Ralph 动作 |
|------|------|-----------|
| **POSITIVE_AUTO** | transfer_gap ≥ **10pp** AND retention ≥ **90%** | **自动批准，继续下一窗口** |
| **POSITIVE_MANUAL** | transfer_gap ≥ 5pp AND retention ≥ 85% | 生成申请，等待人工确认 |
| **MARGINAL** | 0 < transfer_gap < 5pp | 冻结，等待分析 |
| **FAIL** | transfer_gap ≤ 0 OR retention < 85% | 冻结，终止或回退 |

### 自动批准流程

```
Window 执行
    ↓
[Ralph] STOP (窗口结束)
    ↓
[评估阈值]
    ↓
├── POSITIVE_AUTO (≥10pp, ≥90%) 
│   → 自动批准
│   → 生成 window_{N+1}_config.json
│   → **自动继续下一窗口**
│   → 记录决策日志
│
├── POSITIVE_MANUAL (≥5pp, ≥85%)
│   → 生成申请材料
│   → 等待人工确认
│
└── MARGINAL / FAIL
    → 冻结
    → 等待人工决策
```

### 关键纪律

- ✅ **严格阈值**: 自动批准标准必须远高于最低门槛
- ✅ **可审计**: 每次自动批准必须记录完整决策链
- ✅ **可回滚**: 即使自动批准，后续发现异常仍可冻结
- ✅ **真实执行**: 每个窗口必须有独立的状态变化和产出
- ❌ **放宽标准**: 不得降低自动批准阈值
- ❌ **空转窗口**: 禁止无真实计算的编号递增

---

## 实验运行记录

### L5 Full Batch-1 (Budget Window Mode)

```
物理时间: ~30 分钟 (现实 wall-clock)
Bio-world 时间: 10 个执行窗口
执行结果: 全部 POSITIVE_AUTO
真实产出: 10 组独立 metrics + checksum
```

**验证**: 每个窗口有独立 data_checksum，证明真实状态变化发生。

---

*Rule T0 v2.0 Effective: 2026-03-15*
