# P0 Weekly Operations

## 文件结构

| 文件 | 说明 |
|------|------|
| `WEEKLY_OPS_TEMPLATE.md` | **锁定模板 v1.0**，所有周报必须基于此格式，字段已冻结 |
| `P0_WEEKLY_OPERATIONS_REVIEW_2026Wxx.md` | 各周实际报告 |

## 使用规范

1. **创建新周报**: 复制 `WEEKLY_OPS_TEMPLATE.md` 为 `P0_WEEKLY_OPERATIONS_REVIEW_2026Wxx.md`
2. **禁止修改字段**: 模板字段已锁定，任何修改需经 Research Lead 批准并版本化
3. **提交时间**: 每周一 09:00 UTC 前
4. **审核流程**: Primary (Alex Chen) → Backup review → Research Lead sign-off

## 关键阈值速查

| 环境 | CWCI | Degraded Seeds | Failover |
|------|------|----------------|----------|
| Tier 1 (4x) | ≥ 0.65 | 0 | N/A |
| Tier 2 (6x) | ≥ 0.60 | ≤ 1 | ≤ 3/周 |
| 降级触发 | < 0.58 24h | ≥ 2 | 失败或 >10 ticks |

## 8x 红线

- **绝对禁止**: 任何 8x 流量进入生产环境
- **合规检查**: 每周必须确认 8x 隔离状态

