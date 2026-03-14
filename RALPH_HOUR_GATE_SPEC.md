# Ralph Hour Gate - Atlas-HEC Integration Spec

**Version**: 1.0  
**Based on**: ralph-wiggum plugin architecture  
**Purpose**: External 1-hour budget controller for Atlas-HEC experiments

---

## 1. 设计理念

Ralph Hour Gate 是一个**外层预算控制器**，不是实验的一部分。它负责：

1. **强制执行 1 小时规则** - 每个批次最多运行 60 分钟
2. **判定正向反馈** - 读取指标，检查阈值
3. **控制预算发放** - 只有通过时才生成下一小时配置
4. **记录决策日志** - 所有批准/拒绝都有审计追踪

**关键原则**: Ralph 不替代人类决策，它强制执行协议规则。

---

## 2. 与 Ralph-Wiggum 的关系

### 原版 Ralph-Wiggum (Claude Code Plugin)

原版 Ralph 是 Claude Code 的内部插件，负责：
- 外部状态监控
- 异常检测
- 安全审计
- 外部 API 集成

### Atlas-HEC 适配版 Ralph Hour Gate

我们提取了核心**预算门控**概念，创建专门用于 1 小时实验批次的控制器：

| 功能 | 原版 Ralph | Atlas Hour Gate |
|------|-----------|-----------------|
| 外部监控 | ✅ | ✅ (文件系统) |
| 异常检测 | ✅ | ✅ (阈值检查) |
| 预算控制 | ✅ | ✅ (核心功能) |
| 自动修复 | ✅ | ❌ (不允许自动修复，只控制预算) |
| 安全审计 | ✅ | ✅ (决策日志) |
| API 集成 | ✅ | ❌ (本地文件系统) |

---

## 3. 架构

```
┌─────────────────────────────────────────────┐
│         Atlas-HEC Experiment Layer          │
│  ┌─────────────┐  ┌─────────────┐          │
│  │ L5_BATCH1.py│  │ L5_BATCH2.py│  ...     │
│  └──────┬──────┘  └──────┬──────┘          │
│         │                │                 │
│         ▼                ▼                 │
│  ┌─────────────────────────────────────┐  │
│  │  Write metrics.json after each hour │  │
│  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│        Ralph Hour Gate (External)           │
│  ┌─────────────────────────────────────┐   │
│  │ 1. Read metrics.json                │   │
│  │ 2. Evaluate thresholds              │   │
│  │ 3. Decision: APPROVE / REJECT       │   │
│  │ 4. If APPROVE:                      │   │
│  │    - Write next_hour_config.json    │   │
│  │    - Log decision                   │   │
│  │ 5. If REJECT:                       │   │
│  │    - Write negative_result.json     │   │
│  │    - Freeze experiment              │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│         Human / Protocol Layer              │
│  - Review Ralph decision logs               │
│ - Approve/reject next hour (if needed)     │
│ - Override in emergency                     │
└─────────────────────────────────────────────┘
```

---

## 4. 工作流程

### 标准流程 (推荐)

```
Hour 1:
  1. Ralph 启动 L5_BATCH1.py (timeout 3600)
  2. Batch 完成，写入 metrics.json
  3. Ralph 读取 metrics，检查阈值
  4. 决策:
     - POSITIVE → 生成 Hour 2 配置，STOP，等待人工批准
     - NEGATIVE → 冻结实验，STOP

Hour 2 (需要批准):
  1. 人工审查 Ralph 日志和 Hour 1 结果
  2. 批准 Hour 2
  3. Ralph 启动 Hour 2 (timeout 3600)
  4. 重复上述流程
```

### 自动连续模式 (可选，需显式启用)

```
配置: auto_continue: true

Hour 1:
  - 自动评估
  - 若 POSITIVE → 自动继续 Hour 2
  - 最多 auto_continue_max_hours 小时

适用场景: 低风险的重复性验证
```

---

## 5. 配置文件

### Gate 配置示例

```json
{
  "experiment_name": "L5_FULL_BATCH1",
  "batch_number": 1,
  "batch_command": "L5_FULL_BATCH1.py",
  "batch_config": "L5_FULL_BATCH1_CONFIG.json",
  
  "working_dir": "/home/admin/atlas-hec-v2.1-repo",
  "output_dir": "ralph_runs/l5_batch1",
  
  "max_hours": 10,
  "auto_continue": false,
  
  "positive_feedback_thresholds": {
    "transfer_gap_pp": {
      "value": 5.0,
      "operator": ">="
    },
    "code_retention_pct": {
      "value": 85,
      "operator": ">="
    },
    "leakage_status": {
      "value": "clean",
      "operator": "=="
    }
  }
}
```

### Metrics 输出格式

实验脚本必须在每小时结束时写入:

```json
{
  "hour": 1,
  "timestamp": "2026-03-15T06:30:00Z",
  "transfer_gap_pp": 11.7,
  "code_retention_pct": 91.5,
  "self_gap_pp": 17.43,
  "leakage_status": "clean",
  "group_stats": {...},
  "raw_data_checksum": "sha256:..."
}
```

---

## 6. 决策规则

### 正向反馈判定 (必须全部满足)

| 指标 | 阈值 | 说明 |
|------|------|------|
| transfer_gap_pp | ≥5 | 跨任务迁移有效 |
| code_retention_pct | ≥85 | 无灾难性遗忘 |
| leakage_status | "clean" | 无源任务污染 |

### 决策动作

```python
if all_thresholds_met:
    action = "APPROVE_NEXT_HOUR"
    write_next_hour_config()
    if auto_continue:
        continue_to_next_hour()
    else:
        stop_and_wait_approval()
else:
    action = "REJECT_FREEZE"
    write_negative_result()
    freeze_experiment()
```

---

## 7. 集成到 L5 Full Batch

### 修改 L5_FULL_BATCH1.py

在每个小时结束时添加:

```python
def write_hourly_metrics(self, hour_number):
    """Write metrics for Ralph evaluation"""
    metrics = {
        "hour": hour_number,
        "timestamp": datetime.now().isoformat(),
        "transfer_gap_pp": self.calculate_transfer_gap(),
        "code_retention_pct": self.calculate_code_retention(),
        "leakage_status": self.check_leakage(),
        # ... other metrics
    }
    
    output_dir = Path(f"ralph_runs/l5_batch1/hour_{hour_number}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)
```

### 使用 Ralph 启动

```bash
# 方式1: Ralph 控制整个 Batch
python3 ralph_hour_gate.py --config L5_FULL_BATCH1_RALPH_CONFIG.json

# 方式2: Ralph 只控制单小时 (更细粒度)
python3 ralph_hour_gate.py --config L5_HOUR1_RALPH_CONFIG.json
```

---

## 8. 日志和审计

### Ralph 决策日志

```json
{
  "timestamp": "2026-03-15T06:30:00Z",
  "level": "INFO",
  "experiment": "L5_FULL_BATCH1",
  "batch": 1,
  "hour": 1,
  "hour_budget": 1,
  "message": "POSITIVE FEEDBACK: Hour-1 approved for extension",
  "data": {
    "all_passed": true,
    "checks": [
      {"metric": "transfer_gap_pp", "value": 11.7, "threshold": 5.0, "passed": true},
      {"metric": "code_retention_pct", "value": 91.5, "threshold": 85, "passed": true},
      {"metric": "leakage_status", "value": "clean", "threshold": "clean", "passed": true}
    ]
  }
}
```

### 审计追踪

每个实验都有完整的决策链:
1. 启动日志
2. 每小时执行日志
3. 指标评估日志
4. 决策日志 (批准/拒绝)
5. 下一小时配置 (如果批准)

---

## 9. 安全边界

### Ralph 不能做的事

❌ **不能**预先批准多小时连续执行  
❌ **不能**在没有显式指标时自动续时  
❌ **不能**修改实验内部逻辑  
❌ **不能**跳过人工审查 (除非 auto_continue 显式启用)  
❌ **不能**在负反馈时继续执行

### Ralph 必须做的事

✅ **必须**强制执行 1 小时 timeout  
✅ **必须**读取并验证指标  
✅ **必须**记录所有决策  
✅ **必须在**负反馈时 STOP  
✅ **必须在**正反馈时生成明确的下一小时配置

---

## 10. 与 Atlas 协议的对应

| Atlas 协议规则 | Ralph 实现 |
|---------------|-----------|
| Rule-H1: 1小时规则 | timeout 3600 |
| 正向反馈才续时 | threshold evaluation |
| 无反馈即停止 | NEGATIVE → freeze |
| STOP-APPLY-APPROVE-EXECUTE | 每个 hour 后 STOP，生成 config，等待批准 |
| 禁止预支长时预算 | max_hours 限制，逐小时评估 |

---

## 11. 快速开始

### 1. 安装

```bash
# Ralph Hour Gate 是单个 Python 文件，无需安装
cp ralph_hour_gate.py /home/admin/atlas-hec-v2.1-repo/
```

### 2. 创建配置

```bash
cat > L5_BATCH1_RALPH_CONFIG.json << 'EOF'
{
  "experiment_name": "L5_FULL_BATCH1",
  "batch_command": "L5_FULL_BATCH1.py",
  "batch_config": "L5_FULL_BATCH1_CONFIG.json",
  "working_dir": ".",
  "output_dir": "ralph_runs/l5_batch1",
  "max_hours": 10,
  "auto_continue": false,
  "positive_feedback_thresholds": {
    "transfer_gap_pp": {"value": 5.0, "operator": ">="},
    "code_retention_pct": {"value": 85, "operator": ">="},
    "leakage_status": {"value": "clean", "operator": "=="}
  }
}
EOF
```

### 3. 执行

```bash
python3 ralph_hour_gate.py --config L5_BATCH1_RALPH_CONFIG.json
```

---

## 12. 未来扩展

### 与原版 Ralph-Wiggum 集成

未来可以将 Atlas Hour Gate 作为插件接入原版 Ralph：

```python
# 在原版 Ralph 中注册 Atlas 适配器
from ralph_wiggum.adapters import AtlasHECAdapter

ralph.register_adapter("atlas-hec", AtlasHECAdapter(
    hour_gate_config="L5_BATCH1_RALPH_CONFIG.json"
))
```

### 多实验并行

Ralph 可以同时监控多个独立的 Atlas 实验：

```bash
# 并行监控 L4, L5, L6
python3 ralph_multi_experiment.py --experiments L4_CONFIG.json L5_CONFIG.json L6_CONFIG.json
```

---

**作者**: Atlas-HEC Research Committee  
**基于**: ralph-wiggum by Anthropic  
**协议**: Atlas Protocol v2.1-H1
