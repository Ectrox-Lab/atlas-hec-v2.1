# Campaigns Decision

**Decision Owner**: RyanX  
**Decision Date**: 2026-03-12  
**Effective Date**: 2026-03-13  
**Status**: ✅ APPROVED

---

## 批准项

| 项 | 状态 | 备注 |
|----|------|------|
| P0 Active Trigger Campaign | ✅ Approved | 2 周主动施压，确认 6x 真实边界 |
| P2.6 Restart Readiness Campaign | ✅ Approved | 3 周数据积累，Week 3 GO/NO-GO |
| Resource Windows | ✅ Approved | 6x 14:00-16:00 UTC；8x research 02:00-06:00 UTC |
| Daily Reporting (P0) | ✅ Approved | 每日简报，5 个数 |
| Weekly Checkpoints (P2.6) | ✅ Approved | Week 1/2/3 checkpoint |

---

## 红线（不可突破）

- **8x 生产**: 绝对禁止，仅限研究环境
- **授权边界**: 不改写当前 Tier 1/2 生产授权
- **降级执行**: 触发条件满足时，立即执行，不犹豫

---

## 资源锁定

| Campaign | 负责人 | 窗口 | 资源 |
|----------|--------|------|------|
| P0 | Alex Chen | 每日 14:00-16:00 UTC | Tier 2 (6x) |
| P2.6 | Jordan Smith | 每日 02:00-06:00 UTC | 8x research + ~500 CPU-hours |

---

## 启动清单 (Day 0)

- [ ] 通知 Alex Chen 负责人锁定
- [ ] 通知 Jordan Smith 负责人锁定
- [ ] 确认 Tier 2 窗口预留
- [ ] 确认 8x research 环境就绪
- [ ] 每日简报模板就位
- [ ] 风险日志就位
- [ ] Week 1 checkpoint 日期锁定

---

## 关键日期

| 日期 | 事件 |
|------|------|
| 2026-03-13 | Day 0: 启动准备完成 |
| 2026-03-13 | Day 1: 双 Campaign 启动 |
| 2026-03-20 | Week 1 checkpoint (P2.6) |
| 2026-03-27 | P0 Campaign 结束 + envelope 报告 |
| 2026-03-27 | Week 2 checkpoint (P2.6) |
| 2026-04-03 | P2.6 Campaign 结束 + GO/NO-GO 决策 |

---

## 决策依据

> 不是想多做点事，而是：
> - P0: 主动确认 6x 真实边界，而非在平稳条件下误判为稳定
> - P2.6: 主动制造重启前提，否则无限期冻结
> - 两条线都在受控边界内，不改写生产授权，不突破 8x 红线

---

**决策人签字**: RyanX  
**日期**: 2026-03-12
