# L5 Full Batch-1 Application (1-Hour Compliant)

**申请时间**: 2026-03-15 (Hour-2成功后)  
**申请状态**: CORRECTED (原30-40h申请已废弃)  
**批次**: Batch 1 of 10 (max)  
**前置**: L5 Pilot SUCCESS (11.7pp Transfer Gap)

---

## 违规承认与纠正

### 原申请违规

| 违规项 | 原值 | 规则 | 状态 |
|--------|------|------|------|
| 时长 | 30-40 hours | ≤1 hour (Rule-H1) | ❌ **REJECTED** |
| 规模 | 480 seeds一次性 | 需分解为1小时批次 | ❌ **REJECTED** |

### 纠正声明

> **Atlas-HEC Research Committee确认**:  
> 原L5 Full申请(30-40h) **绝对禁止**，违反Atlas协议核心约束。  
> **立即执行**: 1小时批次合规版本。

---

## Batch-1 设计 (1小时硬约束)

### 基本参数

```yaml
batch: 1_of_10
max_seeds: 80
max_duration: 60 minutes (hard deadline)
task_pair: A→B (Code → Math)
purpose: Replicate Pilot 11.7pp Transfer Gap
```

### 组别设计

| 组 | Seeds | 描述 |
|---|-------|------|
| G1 Transfer | 32 | Code→Math, inheritance enabled |
| G2 Sham | 32 | Math only, sham package |
| G3 Self-Ref | 16 | Math→Math, self inheritance |

**总计**: 80 seeds

---

## 成功/失败标准 (T+60min)

### SUCCESS (申请Batch-2)

必须全部满足:
- Transfer Gap ≥ 5pp (G2 - G1)
- Code Retention ≥ 85% (G1)
- Leakage < 5%
- Self Gap > 0 (G3 vs G2)

### MARGINAL (HOLD, 分析后决定)

- 0 < Transfer Gap < 5pp
- 无严重遗忘
- 无显著泄漏

**动作**: 禁止Batch-2，分析Pilot-Batch1差异

### FAIL (冻结L5 Full)

任一满足:
- Transfer Gap ≤ 0pp
- Code Retention < 85%
- Leakage ≥ 5%
- T+60min未完成

**动作**: 冻结L5 Full，回退L4-v2，分析原因

---

## 为什么只做Batch-1?

### 当前状态

```
L4-v2: ✅ CERTIFIED (18.7pp)
  ↓
L5 Pilot Hour-2: ✅ SUCCESS (11.7pp, 48 seeds)
  ↓
L5 Full: 🟡 ONLY Batch-1 approved (80 seeds, 1 hour)
```

### Batch-1的核心问题

> **Hour-2的11.7pp是否在更大规模(80 seeds)下可复现?**

Hour-2: 48 seeds → 11.7pp  
Batch-1: 80 seeds → ???

**如果Batch-1失败**:
- Pilot结果可能是抽样幸运
- Code→Math可能不稳定
- 需要重新设计而非继续批次

**只有Batch-1成功，才值得Batch-2**。

---

## 与30-40h原方案的区别

| 维度 | 原方案(违规) | Batch-1(合规) |
|------|-------------|---------------|
| 时长 | 30-40h一次性 | 1h，逐批次 |
| 决策点 | 最后才知道 | T+60min必须决策 |
| 失败成本 | 30-40h浪费 | 1h止损 |
| 成功路径 | All-or-nothing | 渐进验证 |
| 纪律 | 违反Rule-H1 | 符合1-Hour Rule |

---

## 完整批次计划 (仅规划，非承诺)

```
Batch 1: A→B (80 seeds) - APPROVED NOW
    ↓ SUCCESS
Batch 2: A→C (80 seeds) - APPLY AFTER BATCH 1
    ↓ SUCCESS
Batch 3: B→A (80 seeds) - APPLY AFTER BATCH 2
...
Batch 10: C→B (48 seeds)

TOTAL: 最多10小时 (10个独立1小时实验)
NOT: 10小时连续跑
```

**关键**: 每批次结束必须STOP，申请，批准，才能下一批次。

---

## 熔断器

```yaml
CB1_T60_INCOMPLETE: {action: REJECT_BATCH1}
CB2_TRANSFER_GAP_LOW: {threshold: 5pp, action: REJECT_BATCH1}
CB3_FORGETTING: {threshold: 85%, action: REJECT_BATCH1}
CB4_LEAKAGE: {threshold: 5%, action: REJECT_BATCH1}
```

---

## 产出物 (T+60min必须提交)

1. `L5_BATCH1_RESULT.json` - 详细数据
2. `L5_BATCH1_RESULT.md` - 分析报告
3. `BATCH2_APPLICATION.md` (如果SUCCESS)

---

## 批准请求

**申请**: L5 Full Batch-1 only  
**规模**: 80 seeds, 1 hour  
**任务**: A→B replicate  
**目标**: Verify 11.7pp replicable at 80-seed scale  

**承诺**: 无论结果如何，T+60min停止，提交结果，申请下一批次(仅当SUCCESS)

---

**批准状态**: 待审核  
**违规原申请**: L5_FULL_APPLICATION_v1_REJECTED.md (已废弃)  

---

*"L5 Pilot的成功不能成为违反协议的理由。1小时规则是纪律，不是建议。"*  
*— Atlas Protocol v2.1-H1*
