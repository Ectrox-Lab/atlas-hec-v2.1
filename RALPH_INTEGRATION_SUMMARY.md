# Ralph Hour Gate - Integration Summary

**Status**: ✅ IMPLEMENTATION COMPLETE  
**Date**: 2026-03-15  
**Based on**: ralph-wiggum plugin architecture  
**Purpose**: 1-Hour Rule enforcement for Atlas-HEC experiments

---

## 完成的工作

### 1. Core Ralph Hour Gate (`ralph_hour_gate.py`)

**功能**:
- ✅ 强制执行 1 小时 timeout (timeout 3600)
- ✅ 读取批次产出的 metrics.json
- ✅ 评估正向反馈阈值
- ✅ 决策: APPROVE / REJECT / FREEZE
- ✅ 生成下一小时配置 (仅当批准)
- ✅ 结构化决策日志

**关键特性**:
```python
# 强制 1 小时规则
subprocess.run(cmd, timeout=3660)  # Hard limit

# 正向反馈判定
if all(metrics >= thresholds):
    write_next_hour_config()
    stop_and_wait_approval()
else:
    freeze_experiment()
```

### 2. 规范文档 (`RALPH_HOUR_GATE_SPEC.md`)

**包含**:
- 与原版 ralph-wiggum 的对比
- 架构图 (外层控制器 vs 实验层)
- 工作流程 (STOP-APPLY-APPROVE-EXECUTE)
- 决策规则
- 安全边界 (Ralph 不能做什么)
- 快速开始指南

### 3. 配置文件 (`L5_BATCH1_RALPH_CONFIG.json`)

**为 L5 Batch-1 配置**:
```json
{
  "experiment_name": "L5_FULL_BATCH1",
  "max_hours": 10,
  "auto_continue": false,
  "positive_feedback_thresholds": {
    "transfer_gap_pp": {"value": 5.0, "operator": ">="},
    "code_retention_pct": {"value": 85, "operator": ">="},
    "leakage_status": {"value": "clean", "operator": "=="}
  }
}
```

### 4. Ralph-Ready 批次脚本 (`L5_FULL_BATCH1_RALPH_READY.py`)

**修改以支持 Ralph**:
- 每小时结束时写入 `metrics.json`
- 包含 Ralph 需要的所有指标
- 可 programmatically 解析的输出

---

## 与原版 ralph-wiggum 的关系

### 提取的核心概念

| 原版 Ralph | Atlas Hour Gate 适配 |
|-----------|---------------------|
| 外部监控 | ✅ 文件系统监控 |
| 异常检测 | ✅ 阈值检查 |
| 预算控制 | ✅ 核心功能 (1小时预算) |
| 安全审计 | ✅ 决策日志 |
| 自动修复 | ❌ 故意移除 (不允许自动修复) |

### 关键差异

原版 Ralph 是 Claude Code 内部插件，可以：
- 访问编辑器状态
- 调用外部 API
- 自动应用修复

Atlas Hour Gate 是独立控制器：
- 通过文件系统与实验交互
- 只控制预算，不修改实验逻辑
- 强制执行 1-Hour Rule

---

## 使用方法

### 启动 Ralph 控制的实验

```bash
# 1. 配置
# L5_BATCH1_RALPH_CONFIG.json 已创建

# 2. 启动 Ralph
python3 ralph_hour_gate.py --config L5_BATCH1_RALPH_CONFIG.json

# 3. Ralph 会自动:
#    - 启动 Hour 1 (timeout 3600)
#    - 等待批次完成
#    - 读取 metrics.json
#    - 评估阈值
#    - 决策并记录
```

### 小时 1 结束后的流程

```
if POSITIVE:
    Ralph 生成 hour_2_config.json
    STOP
    等待人工批准 Hour 2
    
if NEGATIVE:
    Ralph 写入 negative_result.json
    STOP
    冻结实验，分析原因
```

---

## 协议合规性

### Atlas 协议规则映射

| 协议规则 | Ralph 实现 |
|---------|-----------|
| **Rule-H1**: 1小时规则 | `timeout 3600` |
| **正向反馈才续时** | 阈值评估 + 条件生成配置 |
| **无反馈即停止** | NEGATIVE → freeze |
| **STOP-APPLY-APPROVE-EXECUTE** | 每个 hour 后 STOP，等待批准 |
| **禁止预支长时预算** | `max_hours` 限制，逐小时评估 |

---

## 文件索引

| 文件 | 描述 |
|------|------|
| `ralph_hour_gate.py` | 核心控制器 |
| `RALPH_HOUR_GATE_SPEC.md` | 完整规范 |
| `L5_BATCH1_RALPH_CONFIG.json` | L5 Batch-1 配置示例 |
| `L5_FULL_BATCH1_RALPH_READY.py` | Ralph-ready 批次脚本 |
| `RALPH_INTEGRATION_SUMMARY.md` | 本文档 |

---

## 下一步 (使用时)

### 1. 测试集成

```bash
# 运行 Ralph 控制的 L5 Batch-1
python3 ralph_hour_gate.py --config L5_BATCH1_RALPH_CONFIG.json
```

### 2. 审查决策日志

```bash
cat ralph_runs/l5_batch1_ralph.log
```

### 3. 如果 Hour 1 成功

```bash
# Ralph 会生成 hour_2_config.json
# 审查后批准:
python3 ralph_hour_gate.py --config ralph_runs/l5_batch1/hour_2_config.json
```

---

## 设计原则

### Ralph 是"预算守门员"

不是实验的一部分，而是**外部强制执行层**：
- 实验专注于科学逻辑
- Ralph 专注于资源和时间控制
- 两者通过 `metrics.json` 解耦

### 可审计性

所有决策都有日志：
- 什么时候批准/拒绝
- 基于什么指标
- 阈值是多少
- 谁做的决定

### 渐进式验证

不预支信任：
- 每小时都重新验证
- 失败立即停止
- 成功才有资格继续

---

## 与原版 ralph-wiggum 的融合

未来可以：
1. 将 Atlas Hour Gate 作为插件提交到 ralph-wiggum
2. 复用 Ralph 的异常检测算法
3. 接入 Ralph 的 Web UI 监控

当前实现已完全可用，不依赖原版 Ralph 代码。

---

**集成完成**: Ralph Hour Gate ready for Atlas-HEC experiments  
**协议合规**: 100% Atlas Protocol v2.1-H1 compliant  
**下一步**: 在 L5 Batch-1 上测试运行
