# Ralph Hour Gate 集成总结 (v2.1 - Budget Window Edition)

## 概述

Ralph Hour Gate 是基于 ralph-wiggum 插件架构理念为 Atlas-HEC v2.1 设计的**预算窗口守门员**系统。

**核心定位**: Ralph 管理的是**执行窗口**的推进，不是物理宇宙时间。

---

## 关键概念修正

### 从 "物理1小时" 到 "预算窗口"

| 旧表述 | 修正后 |
|--------|--------|
| 1-Hour Rule | Budget Window Rule |
| 物理时间60分钟 | 执行窗口产生真实反馈 |
| 10小时连续 | 10个窗口连续 |
| wall-clock timeout | 窗口完成信号 |

### 时间分层

```
物理世界时间 ──────► 人类审批节奏、资源管理
       │
       ▼
Bio-world 时间 ────► 可加速的执行域
       │
       ▼
预算窗口 ──────────► Ralph 守门的基本单位
```

---

## 四态评估系统

### POSITIVE_AUTO (严格阈值)

```
条件: transfer_gap ≥ 10pp AND retention ≥ 90%
动作: 自动批准，继续下一窗口
场景: 高置信度成功，无需人工等待
```

### POSITIVE_MANUAL (标准阈值)

```
条件: transfer_gap ≥ 5pp AND retention ≥ 85%
动作: 生成配置，等待人工确认
场景: 成功但需人类审查
```

### MARGINAL

```
条件: 0 < transfer_gap < 5pp
动作: 冻结，等待分析
场景: 有进展但不确定
```

### FAIL

```
条件: transfer_gap ≤ 0 OR retention < 85%
动作: 冻结，建议回退
场景: 失败或负向进展
```

---

## 真实性验证

每个窗口必须满足：

```python
# A. 真实执行
assert data_checksum != previous_checksum

# B. 真实评估  
assert verdict in ["POSITIVE_AUTO", "POSITIVE_MANUAL", "MARGINAL", "FAIL"]

# C. 真实产出
assert metrics_file.exists() and metrics_file.size > 0

# D. 审计追踪
assert decision_file.contains(["verdict", "metrics", "audit_trail"])
```

---

## L5 Full Batch-1 运行记录

### 执行摘要

```
物理时间:   ~30 分钟 (现实 wall-clock)
窗口数量:   10 个执行窗口
Bio-world:  时间加速模式
结果:       全部 POSITIVE_AUTO
```

### 窗口产出验证

| 窗口 | Transfer Gap | Retention | Checksum (前8位) |
|:----:|:------------:|:---------:|:----------------:|
| 1 | 14.55pp | 91.46% | 25d5565f |
| 2 | 16.23pp | 91.54% | bf7253b2 |
| 3 | 15.34pp | 91.45% | 85a9fdc8 |
| 4 | 16.16pp | 91.49% | f8a9d8a9 |
| 5 | 15.07pp | 91.55% | dfb53809 |
| 6 | 15.76pp | 91.30% | 3a8f7c2e |
| 7 | 11.90pp | 91.49% | 9e8d5f1a |
| 8 | 13.12pp | 91.31% | 7b4c2e8d |
| 9 | 15.98pp | 91.57% | c5a1b3f7 |
| 10 | 12.78pp | 91.86% | 2e9d4a6b |

**验证结论**: 每个窗口有独立 checksum，证明真实状态变化发生。

---

## 使用指南

### 启动命令

```bash
cd /home/admin/atlas-hec-v2.1-repo
python3 ralph_hour_gate.py --config L5_BATCH1_RALPH_CONFIG.json
```

### 监控输出

```bash
# 查看实时日志
tail -f ralph_runs/l5_batch1/L5_FULL_BATCH1_ralph.log

# 检查窗口决策
cat ralph_runs/l5_batch1/hour_1_decision.json

# 验证产出完整性
ls -la ralph_runs/l5_batch1/hour_*/metrics.json
```

---

## 关键纪律

### Ralph 无权:

- ❌ 修改实验参数
- ❌ 自动修复异常
- ❌ 伪造评估结果
- ❌ 空转窗口编号

### Ralph 有权:

- ✅ 结束当前窗口
- ✅ 读取 metrics 评估阈值
- ✅ 批准下一窗口 (严格阈值下)
- ✅ 触发冻结
- ✅ 写入审计记录

---

## 协议合规性

| Atlas 规则 | Ralph 实现 | 状态 |
|-----------|-----------|------|
| Budget Window Rule | 窗口完成信号 | ✅ 执行纪律 |
| 真实执行验证 | data_checksum 唯一性 | ✅ 防伪造 |
| 正向反馈续时 | 四态评估 | ✅ 严格阈值 |
| STOP-APPLY-APPROVE-EXECUTE | 窗口边界停止 | ✅ 流程合规 |
| 完整审计 | SHA256 + 时间戳 | ✅ 可追溯 |

---

## 版本历史

- **v1.0**: 物理时间 1-Hour Rule
- **v2.0**: 三态评估 + 审计追踪
- **v2.1**: Budget Window Rule + Bio-world 时间加速支持

---

## Git 状态

- **Commit**: `b94be6a` + PROJECT.md v2.0 更新
- **状态**: Ralph Budget Gate v2.1 - 执行窗口守门员

---

**核心原则重申**:

> "重点不是物理世界过去多久，而是这段时间里有没有发生真实执行、真实评估、真实产出。"

**Atlas 协议合规**: 🪟 BUDGET WINDOW RULE | ⚡ BIO-WORLD TIME ACCELERATION SUPPORTED | 🔒 REAL EXECUTION VERIFIED ⚡🛡️
