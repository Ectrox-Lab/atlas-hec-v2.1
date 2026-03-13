# Active Campaigns Overview

**生效日期**: 2026-03-12  
**模式切换**: 从"被动等待"到"主动施压 + 主动补数"

---

## 双线并行

| Campaign | 目标 | 周期 | 状态 |
|----------|------|------|------|
| [ACTIVE_TRIGGER_CAMPAIGN_P0](ACTIVE_TRIGGER_CAMPAIGN_P0.md) | 快速确认 6x 真实边界 | 2 周 | ⏳ 待启动 |
| [RESTART_READINESS_CAMPAIGN_P2.6](RESTART_READINESS_CAMPAIGN_P2.6.md) | 制造 P2.6 重启条件 | 3 周 | ⏳ 待启动 |

---

## P0: Active Trigger Campaign

**核心问题**: 6x 是真稳，还是只是没遇到压力？

**关键动作**:
- 每日短窗压力测试 (高通信、高广播、长时、多 seed 轮换)
- 每日故障注入演练
- 每日简报 (5 个数)
- 触发即降级，验证 checklist

**成功标准**:
- 确认 6x envelope 边界
- 验证降级流程可执行
- failover 延迟稳定 < 5 ticks

**红线**: 绝不碰 8x

---

## P2.6: Restart Readiness Campaign

**核心问题**: 如何让重启条件从"口头"变成"数据就绪"？

**关键动作**:
- Week 1: 写 scale-aware schema v1.0
- Week 1-3: 补 OctopusLike baseline ≥10 per scale
- Week 1-2: 主动 scan 制造 seed-spike registry ≥5
- Week 2-3: 补 ≥3 真实 OQS challenger
- Week 2: SR hypothesis 具体化到 mechanism

**决策点**: Week 3 结束，GO (重启 SR1) / NO-GO (终止 P2.6)

---

## 资源冲突检查

| 资源 | P0 需求 | P2.6 需求 | 冲突？ |
|------|---------|-----------|--------|
| Tier 2 (6x) | 压力测试 | baseline 采样 | ⚠️ 需协调时段 |
| 8x 环境 | ❌ 不用 | seed-spike scan | ✅ 无冲突 |
| On-Call | 高强度 | 正常 | ✅ Alex (P0) + Jordan (P2.6) |
| Research Lead | 审批 | 审批 | ✅ 同一人 |

**协调方案**:
- P0 压力测试安排在 UTC 14:00-16:00
- P2.6 baseline 采样安排在 UTC 02:00-06:00 (低峰)

---

## 审批流程

1. **Research Lead 审批** (Dr. Sarah Williams)
   - 确认资源分配
   - 确认红线理解
   - 签字启动

2. **On-Call 确认** (Alex Chen + Jordan Smith)
   - 确认 availability
   - 确认 escalation path

3. **启动**
   - 同步更新 CAMPAIGNS_STATUS.md
   - 每日/每周按模板汇报

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| P0 压力测试触发真实降级 | 这是设计目的，checklist 已就绪 |
| P2.6 3周后仍不满足重启条件 | 明确 NO-GO，终止 P2.6，资源释放 |
| 资源不足 | 优先保证 P0，P2.6 可延期 |
| On-Call burnout | 2 周密集期后轮换 |

---

**下一步**: 获取 Research Lead 审批，启动双 Campaign。
