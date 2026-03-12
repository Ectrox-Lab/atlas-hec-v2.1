# Campaigns Approval Request

**To**: Dr. Sarah Williams (Research Lead)  
**From**: P0 Operations Team / P2.6 Research Team  
**Date**: 2026-03-12  
**Deadline**: 2026-03-13 18:00 UTC (24h)

---

## 为什么不能继续被动等待

| 现状 | 风险 |
|------|------|
| P0 6x 仅在平稳条件下运行 | 真实边界未知，可能在压力时意外崩溃 |
| P2.6 冻结，重启条件口头化 | 无限期停滞，资源无法决策 |
| 周报节奏太慢 | 触发条件可能整周未被发现 |

**被动 = 不可控的风险积累**

---

## 双 Campaign 收益

### P0 Active Trigger (2 周)
- **目标**: 主动确认 6x 真实运营边界
- **收益**: 知道何时该降级到 4x，而非意外崩溃
- **产出**: 验证过的 envelope + 可执行的降级流程

### P2.6 Restart Readiness (3 周)
- **目标**: 主动制造 SR1 重启前提
- **收益**: Week 3 形成明确 GO/NO-GO 决策，终止无限期冻结
- **产出**: scale-aware schema + baseline 数据 + challenger family

---

## 风险控制

| 红线 | 措施 |
|------|------|
| 绝不碰 8x 生产 | P0 全部在 Tier 2 (6x) 内，P2.6 的 8x 仅限研究环境 |
| 不降低生产稳定性 | P0 压力窗口 2 小时/天，可立即回滚 |
| 资源不冲突 | P0 14:00-16:00 UTC，P2.6 02:00-06:00 UTC |
| 有逃生通道 | 任何降级条件触发，立即执行，不犹豫 |

---

## 资源需求

| Campaign | 资源 | 数量 | 时间窗口 |
|----------|------|------|----------|
| P0 | Tier 2 (6x) | 1 instance | 每日 14:00-16:00 UTC |
| P0 | On-Call | Alex Chen | 2 周密集期 |
| P2.6 | 8x Research | 1 instance | 每日 02:00-06:00 UTC |
| P2.6 | Compute | ~500 CPU-hours | 3 周 |
| P2.6 | Storage | ~100GB | 3 周 |

---

## 明确批准项

请勾选并签字：

### P0 Active Trigger Campaign
- [ ] **批准启动** 2 周主动施压计划
- [ ] **批准** 每日 14:00-16:00 UTC 压力窗口
- [ ] **批准** Alex Chen 为 2 周 On-Call
- [ ] **批准** 触发即降级，无需二次审批

### P2.6 Restart Readiness Campaign  
- [ ] **批准启动** 3 周数据积累计划
- [ ] **批准** 8x 研究环境使用（仅限 seed-spike scan）
- [ ] **批准** ~500 CPU-hours + ~100GB 存储
- [ ] **批准** Week 3 GO/NO-GO 决策权归 Research Lead

### 汇报节奏
- [ ] **批准** 每日简报（P0）
- [ ] **批准** 每周 checkpoint（P2.6）

---

## 批准签字

**Research Lead**: _________________________ (Dr. Sarah Williams)

**日期**: _________________________

**生效**: 签字后 24h 内启动

---

## 附件清单

1. [CAMPAIGNS_OVERVIEW.md](CAMPAIGNS_OVERVIEW.md) - 双 Campaign 总体协调
2. [socs_universe_search/ACTIVE_TRIGGER_CAMPAIGN_P0.md](socs_universe_search/ACTIVE_TRIGGER_CAMPAIGN_P0.md) - P0 详细执行计划
3. [RESTART_READINESS_CAMPAIGN_P2.6.md](RESTART_READINESS_CAMPAIGN_P2.6.md) - P2.6 详细执行计划

---

**关键强调**:

> **这不是"想多做点事"，而是:**
> - P0: 主动确认 6x 真实边界，而非在平稳条件下误判为稳定
> - P2.6: 主动制造重启前提，否则无限期冻结
> - 两条线都在受控边界内，不改写生产授权，不突破 8x 红线
