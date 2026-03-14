# L5 Pilot Hour-1: 1-Hour Probe Protocol

**状态**: APPROVED  
**版本**: v3.0-hour1-compliant  
**批准日期**: 2026-03-15  
**批准依据**: Atlas Protocol 1-Hour Rule

---

## 0. 违规承认与纠正

### 0.1 已确认违规

| 违规项 | 原设计 | 合规要求 | 状态 |
|--------|--------|----------|------|
| 实验时长 | 24小时 | **≤1小时** | ❌ VIOLATION |
| 规模 | 144 seeds | 必须1小时内完成 | ❌ VIOLATION |
| 反馈延迟 | 多阶段慢反馈 | **1小时内必须有反馈** | ❌ VIOLATION |

### 0.2 纠正声明

> **九叔/LOGIC Layer确认**: L5 Pilot v2 (24h) 违反Atlas协议核心约束。  
> **立即执行**: v3 hour-1 compliant版本。

---

## 1. 核心规则 (Hard Rules)

```yaml
execution_rules:
  H1_MAX_DURATION: "1 hour real time"
  H2_FEEDBACK_REQUIREMENT: "observable signal within 1 hour"
  H3_ESCALATION_CONDITION: "positive signal only"
  H4_STOP_CONDITION: "no signal or negative signal"
  H5_NO_PRECOMMIT: "no long runs before hour-1 evidence"
```

---

## 2. Hour-1 最小实验设计

### 2.1 规模 (绝对上限)

| 组 | Seeds | Steps/Seed | 预计时间 |
|---|-------|-----------|---------|
| G1 Transfer | 6 | 50-100 | ~10min |
| G2 Sham | 6 | 50-100 | ~10min |
| G3 Self-Ref | 6 | 50-100 | ~10min |
| **总计** | **18** | - | **~30min** |

**预留30min**: 评估 + 决策 + 缓冲

### 2.2 组别定义

```yaml
G1_Transfer:
  n: 6
  task: Code → Math
  inheritance: enabled
  
G2_Sham:
  n: 6
  task: Code → Math
  inheritance: sham (bias=0)
  
G3_Self_Ref:
  n: 6
  task: Math → Math
  inheritance: self (upper bound reference)
```

---

## 3. 1小时执行流程

### T+0min: 启动
```bash
timeout 3600 python3 L5_HOUR1_PROBE.py \
  --seeds 18 \
  --steps 100 \
  --checkpoint-every 50
```

### T+15min: 第一检查点 (必须)

**检查项**:
1. G1 Math loss < G2 Math loss?
2. All groups training stable?
3. No OOM / crash?

**决策**:
- ✅ YES → 继续到T+45min
- ❌ NO → **立即终止**，T+20min提交负结果

### T+45min: 评估完成

**必须产出**:
```json
{
  "hour1_result": {
    "timestamp": "T+45min",
    "early_transfer_signal": "positive|negative|unclear",
    "math_loss_delta": "G1_vs_G2",
    "code_retention_estimate": "percentage",
    "leakage_flag": "detected|clean|unclear",
    "recommendation": "ESCALATE|STOP|AMBIGUOUS"
  }
}
```

### T+60min: 硬截止

**必须提交**: `L5_HOUR1_RESULT.md`

---

## 4. Hour-1 通过条件

### 4.1 申请Hour-2的条件 (满足任意2项)

| # | 条件 | 阈值 | 测量方法 |
|---|------|------|----------|
| 1 | G1 Math loss < G2 Math loss | 严格小于 | 训练loss曲线 |
| 2 | Early transfer gap > 0 | any positive | 快速评估指标 |
| 3 | Code retention ≥ 80% | ≥80% | Code能力快速测试 |
| 4 | No obvious leakage | clean | 人工抽查top-3 |

### 4.2 立即STOP条件 (满足任意1项)

| # | 条件 | 阈值 | 动作 |
|---|------|------|------|
| 1 | Transfer gap ≤ 0 | zero or negative | STOP, submit negative |
| 2 | Code retention < 80% | severe forgetting | STOP, catastrophic failure |
| 3 | Obvious leakage | detected | STOP, contamination |
| 4 | Timeout approaching | T>50min incomplete | STOP, partial results |

---

## 5. 1小时内交付的4个指标

不允许追求完整统计显著性，只交:

```yaml
hour1_deliverables:
  1_early_transfer_signal:
    description: "Direction of transfer effect"
    values: [positive, negative, unclear]
    
  2_math_loss_delta:
    description: "G1 vs G2 loss difference"
    format: "numeric or N/A"
    
  3_code_retention_estimate:
    description: "Quick check on forgetting"
    format: "percentage or N/A"
    
  4_leakage_flag:
    description: "Source contamination detected"
    values: [detected, clean, unclear]
```

---

## 6. 决策树 (T+60min)

```
Hour-1 Results
│
├─ STOP conditions triggered
│   └─ ❌ Submit L5_HOUR1_NEGATIVE.md
│   └─ Freeze L5, redesign
│
├─ 2+ positive signals
│   └─ ✅ APPLY for Hour-2
│   └─ Options:
│       ├─ Scale to 48 seeds
│       ├─ Add evaluation depth
│       └─ Extend to Hour-2 only
│
└─ Ambiguous (1 positive or unclear)
    └─ 🟡 OPTIONS:
        ├─ Quick Hour-1.5 (30min extension)
        ├─ Redesign with clearer signal
        └─ STOP and report marginal
```

---

## 7. 禁止事项 (Hour-1)

❌ **禁止**: 追求统计显著性 (p-values, confidence intervals)  
❌ **禁止**: 完整128-seed scale  
❌ **禁止**: 完整5-criteria evaluation  
❌ **禁止**: 长训练 (>100 steps)  
❌ **禁止**: 预承诺Hour-2 (必须先有Hour-1证据)  
❌ **禁止**: 解释负结果 ("如果再多时间可能会好")

---

## 8. 与后续Hours的关系

### Hour-1 ≠ 完整验证

> Hour-1 only validates: "Is there a signal worth investigating?"

### Hour-2 (if approved)

- Scale: 48 seeds (only if Hour-1 positive)
- Duration: +1 hour max
- Goal: Confirm signal stability

### Hour-3+ (rare)

- Only if Hour-2 also positive
- Must re-apply each hour
- Full validation only after multiple hours

---

## 9. 批准签名

```yaml
approval:
  protocol: L5_PILOT_HOUR1
  version: v3.0
  status: APPROVED
  
  constraints:
    max_duration: "1 hour"
    max_seeds: 18
    max_steps: 100
    feedback_deadline: "T+60min"
    
  violation_acknowledged:
    - v2_24h_design: CANCELLED
    - v2_144_seeds: CANCELLED
    - long_feedback_loop: PROHIBITED
    
  next_action: "Execute L5_HOUR1_PROBE immediately"
  escalation_rule: "Positive signal → apply for Hour-2"
  stop_rule: "No signal → submit negative, freeze L5"
```

---

**执行**: 立即启动，60分钟硬截止  
**命令**: `timeout 3600 python3 L5_HOUR1_PROBE.py`  
**产出**: `L5_HOUR1_RESULT.md` (T+60min必须提交)

---

*"1小时不是限制，是纪律。没有快速反馈，就没有快速学习。"*  
*— Atlas Protocol v2.1-H1*
