# Ralph Hour Gate 集成总结 (v2.0)

## 概述

Ralph Hour Gate 是基于 ralph-wiggum 插件架构理念为 Atlas-HEC v2.1 设计的**预算守门员**系统。

**核心定位**: Ralph 是制度的化身，不是智能体。它不会思考，只会执行规则。

---

## 与原版 ralph-wiggum 的关系

| ralph-wiggum (编辑器插件) | Ralph Hour Gate (Atlas-HEC) |
|--------------------------|----------------------------|
| 监控编辑器状态 | 监控实验时间预算 |
| 检测代码异常 | 检测实验指标异常 |
| 控制器任务失败处理 | 正向反馈阈值判断 |
| 文件系统交互 | metrics.json 读取/决策输出 |

**提取的核心概念**:
- ✅ 外部监控
- ✅ 异常检测
- ✅ 预算控制 (核心)
- ✅ 安全审计

**Atlas 适配**:
- 文件系统交互 (而非编辑器 API)
- 只控制预算，不自动修复
- 强制执行 1-Hour Rule

---

## v2.0 关键改进

### 1. 三种状态评估 (Three-State Evaluation)

```
POSITIVE:  clear success → 生成下一小时配置，STOP，等待批准
MARGINAL:  ambiguous progress → FREEZE，要求分析  
FAIL:      clear failure → FREEZE，建议回退
```

**判别标准**:

| 条件 | 状态 | Ralph 动作 | 人工建议 |
|------|------|-----------|---------|
| transfer_gap >= 5pp AND retention >= 85% AND self_gap > 0 AND clean | **POSITIVE** | 生成 Hour+1 配置，STOP | 批准继续 |
| 0 < transfer_gap < 5pp AND retention >= 80% | **MARGINAL** | FREEZE | 分析原因 |
| transfer_gap <= 0 OR retention < 80% OR leakage | **FAIL** | FREEZE | 回退 L4-v2 |

### 2. 完整审计追踪 (Complete Audit Trail)

每个 `decision.json` 包含：

```json
{
  "verdict": "POSITIVE|MARGINAL|FAIL",
  "hour": 1,
  "metrics": { /* 原始指标 */ },
  "details": { /* 状态原因 */ },
  "audit_trail": {
    "started_at": "2026-03-15T03:49:27Z",
    "ended_at": "2026-03-15T04:49:15Z",
    "config_sha256": "abc123...",
    "metrics_sha256": "def456...",
    "next_config_path": "...",
    "next_config_sha256": "ghi789..."
  },
  "ralph_action": "STOPPED - Hour-2 config generated, awaiting approval",
  "human_required": true,
  "recommendation": "APPROVE_CONTINUE|ANALYZE|ROLLBACK"
}
```

### 3. 哈希链防篡改 (Hash Chain)

- `config_sha256`: 输入配置的哈希
- `metrics_sha256`: 产出指标的哈希
- `next_config_sha256`: 生成配置的哈希

防止"结果文件被覆盖但决策还在"的问题。

---

## 文件结构

```
ralph_runs/
├── l5_batch1_ralph.log              # 结构化日志
├── hour_1/
│   └── metrics.json                 # 实验产出指标
├── hour_1_decision.json             # Ralph 决策 (含审计)
├── hour_2_config.json               # 下一小时配置 (仅 POSITIVE)
└── FROZEN                            # 冻结标记 (MARGINAL/FAIL)
```

---

## 工作流程

```
┌─────────────────────────────────────────────┐
│           Atlas-HEC 实验流程                │
├─────────────────────────────────────────────┤
│                                             │
│  L5 Batch-1 科学代码 (专注实验逻辑)        │
│       ↓                                     │
│  metrics.json (数据产出)                   │
│       ↓                                     │
│  Ralph Hour Gate (预算守门员)              │
│       ↓                                     │
│  三种状态决策:                              │
│    ├─ POSITIVE → STOP + 生成配置           │
│    ├─ MARGINAL → FREEZE + 分析             │
│    └─ FAIL → FREEZE + 回退                 │
│       ↓                                     │
│  人工审查 (九叔确认)                        │
│       ↓                                     │
│  批准/拒绝/回退                            │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 使用示例

### 启动实验

```bash
cd /home/admin/atlas-hec-v2.1-repo

python3 ralph_hour_gate.py --config L5_BATCH1_RALPH_CONFIG.json
```

### 监控 Ralph 决策

```bash
# 实时查看日志
tail -f ralph_runs/l5_batch1_ralph.log

# 检查决策
cat ralph_runs/hour_1_decision.json
```

### 三种状态场景

#### 场景 A: POSITIVE

```bash
# Ralph 输出:
[2026-03-15T04:49:15Z] [INFO] Batch-1: POSITIVE FEEDBACK: All thresholds met
[2026-03-15T04:49:15Z] [INFO] Batch-1: POSITIVE: Hour-2 config generated
[2026-03-15T04:49:15Z] [INFO] Batch-1: Stopping for external approval

# 生成文件:
ralph_runs/hour_1_decision.json    # 完整审计
ralph_runs/hour_2_config.json      # 下一小时配置

# 九叔动作:
cat ralph_runs/hour_1_decision.json   # 验证数据
# 人工批准 Hour-2
```

#### 场景 B: MARGINAL

```bash
# Ralph 输出:
[2026-03-15T04:49:15Z] [WARN] Batch-1: MARGINAL FEEDBACK: Partial progress, freezing for analysis

# 生成文件:
ralph_runs/hour_1_decision.json    # 状态: MARGINAL
ralph_runs/FROZEN                   # 冻结标记

# 九叔动作:
cat ralph_runs/hour_1_decision.json   # 分析原因
# 决定: HOLD 或 REJECT
```

#### 场景 C: FAIL

```bash
# Ralph 输出:
[2026-03-15T04:49:15Z] [ERROR] Batch-1: FAIL FEEDBACK: Clear failure, freezing

# 生成文件:
ralph_runs/hour_1_decision.json    # 状态: FAIL
ralph_runs/FROZEN                   # 冻结标记

# 九叔动作:
# 直接回退 L4-v2
```

---

## 关键纪律

### Ralph 无权:

- ❌ 修改实验参数
- ❌ 自动修复异常
- ❌ 批准继续执行（即使 POSITIVE 也 STOP）
- ❌ 自动进入下一小时
- ❌ 跳过人工审查

### Ralph 有权:

- ✅ 强制 timeout 3600
- ✅ 读取 metrics 评估阈值
- ✅ 生成下一小时配置（仅 POSITIVE）
- ✅ 触发冻结（MARGINAL/FAIL）
- ✅ 写入完整审计记录

---

## 协议合规性

| Atlas 规则 | Ralph 实现 | 状态 |
|-----------|-----------|------|
| 1-Hour Rule | `timeout 3600` | ✅ 硬约束 |
| 正向反馈才续时 | 三种状态评估 | ✅ 明确阈值 |
| STOP-APPLY-APPROVE-EXECUTE | STOP 等待人工 | ✅ 强制停止 |
| 禁止预支预算 | max_hours 限制 | ✅ 无透支 |
| 异常检测 | MARGINAL/FAIL 熔断 | ✅ 熔断机制 |
| 可审计性 | 哈希链 + 时间戳 | ✅ v2.0 新增 |

---

## 版本历史

- **v1.0**: 基础实现，两种状态 (POSITIVE/NEGATIVE)
- **v2.0**: 三种状态 (POSITIVE/MARGINAL/FAIL)，完整审计追踪，哈希链

---

## Git 状态

- **Commit**: `607770b` + v2.0 更新
- **状态**: Ralph Hour Gate v2.0 - 三种状态 + 审计追踪

---

## 九叔最终确认

> "Ralph 是制度的化身，不是智能体。它不会思考，只会执行规则。这正是它存在的意义。"

- Ralph Hour Gate v2.0: ✅ **APPROVED AS BUDGET GATEKEEPER**
- 三种状态评估: ✅ **APPROVED**
- 完整审计追踪: ✅ **APPROVED**
- L5 Batch-1 执行: ✅ **APPROVED FOR EXECUTION**

---

**等待 Ralph T+60min 决策报告。**

**Atlas 协议合规**: ⏱️ 1-HOUR RULE ENFORCED | 🤖 RALPH v2.0 BUDGET GATEKEEPER ACTIVE | 🔒 AUDIT TRAIL ENABLED ⚡🛡️🔍
