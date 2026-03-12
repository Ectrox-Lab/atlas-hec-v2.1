# Campaigns Day 0 Checklist

**目标**: 24 小时内完成启动准备  
**截止**: 2026-03-13 18:00 UTC

---

## P0 Active Trigger - Day 0

### 负责人确认
- [ ] Alex Chen 确认 availability (2 周 On-Call)
- [ ] 备用负责人 Jordan Smith 确认 backup availability
- [ ] Dr. Sarah Williams 确认 escalation path

### 环境准备
- [ ] Tier 2 (6x) 环境预留确认
- [ ] Backup pool (seed_55, seed_66) warm 状态确认
- [ ] Failover drill 预演通过
- [ ] Rollback plan 文档化并 accessible

### 监控就绪
- [ ] Per-seed CWCI tracking 启用 1-tick 粒度
- [ ] Alert pipeline (0.60/0.58/0.55) 测试通过
- [ ] Auto-failover 触发器测试通过
- [ ] Daily brief 模板就位

### 文档就位
- [ ] ACTIVE_TRIGGER_CAMPAIGN_P0.md accessible to team
- [ ] Trigger response matrix 打印/可见
- [ ] Downgrade checklist 打印/可见

---

## P2.6 Restart Readiness - Day 0

### 负责人确认
- [ ] Jordan Smith 确认 availability (3 周负责)
- [ ] 与 Alex Chen 协调资源窗口无冲突

### 环境准备
- [ ] 8x research 环境就绪
- [ ] Baseline 采样存储路径创建
- [ ] Seed-spike registry DB 初始化
- [ ] Challenger fingerprint 工具链就绪

### 数据准备
- [ ] Week 1 采样计划排程
- [ ] Seed scan 范围确认 (100-200)
- [ ] Schema redesign 工作区准备

### 文档就位
- [ ] RESTART_READINESS_CAMPAIGN_P2.6.md accessible to team
- [ ] Workstream 1-5 任务分配确认
- [ ] Week 1 checkpoint 日期确认

---

## 共同检查项

### 资源冲突
- [ ] 6x 窗口 (14:00-16:00 UTC) 与 P2.6 无冲突
- [ ] 8x 仅用于 research，不触碰生产
- [ ] Compute budget 确认 (~500 CPU-hours)
- [ ] Storage budget 确认 (~100GB)

### 风险准备
- [ ] 风险日志模板就位
- [ ] 事件升级流程确认
- [ ] 紧急联系人清单更新

---

## 启动信号

所有 checklist 完成后，发送启动通知:

```
TO: Alex Chen, Jordan Smith
CC: Dr. Sarah Williams
SUBJECT: [ACTION REQUIRED] Campaigns Launch - Day 1

双 Campaign 已批准启动 (CAMPAIGNS_DECISION.md)

P0 Active Trigger:
- 负责人: Alex Chen
- 首日压力测试: 2026-03-13 14:00 UTC
- 每日简报: 09:00 UTC

P2.6 Restart Readiness:
- 负责人: Jordan Smith  
- 首日采样: 2026-03-14 02:00 UTC
- Week 1 checkpoint: 2026-03-20

红线不变: 8x 生产禁止，触发即降级。
```

---

## 完成确认

**Day 0 完成签字**: _______________  
**时间**: _______________  
**启动状态**: ⏳ 准备中 / ✅ 已启动
