# Active Trigger Campaign - P0

**目标**: 主动施加受控压力，快速确认 6x 真实运营边界  
**周期**: 2 周 (2026-03-13 ~ 2026-03-27)  
**负责人**: Alex Chen  
**审批**: Dr. Sarah Williams

---

## 核心原则

- **不是破坏系统**，而是让触发条件更快、更可解释地出现
- **所有压力在 Tier 2 (6x) 内进行**，绝不触碰 8x 红线
- **任何降级决策立即执行**，验证 checklist 可行性

---

## Phase 1: 短窗压力测试 (Week 1-2)

每天一个场景，窗口 2 小时，结束后恢复基线。

| 日期 | 场景 | 压力参数 | 观测目标 |
|------|------|----------|----------|
| D1 | 高通信负载 | 通信频率 x2 | CWCI 是否跌破 0.60 |
| D2 | 高广播频率 | 广播间隔 -50% | degraded seeds 是否上升 |
| D3 | 长时运行 | 连续 4h 无 failover | stability 是否下滑 |
| D4 | 多 seed 轮换 | 每 30min 轮换主 seed | failover 次数是否上升 |
| D5 | 混合压力 | D1+D2 同时 | 综合指标变化 |
| D6 | 恢复基线 | 正常参数 | 系统恢复速度 |
| D7 | **复盘** | - | envelope 边界确认 |

**Week 2 重复，调整压力强度**

### 压力测试执行清单

```yaml
pre_check:
  - backup_pool_warm: true
  - failover_dry_run_passed: true
  - on_call_available: true
  - rollback_plan_ready: true

execution:
  - window_start: "HH:MM UTC"
  - pressure_level: "1.5x / 2x / 2.5x"
  - telemetry_granularity: "1-tick"
  
abort_conditions:
  - CWCI < 0.55 for > 5 ticks
  - ≥3 seeds degraded simultaneously
  - failover latency > 10 ticks
  - manual abort trigger

post_check:
  - system_stability_restored: true
  - metrics_logged: true
  - incident_report_filed: true (if any)
```

---

## Phase 2: 故障注入演练 (Daily)

每天一次，验证监控和 failover 响应。

| 演练 | 注入点 | 预期响应 | 成功标准 |
|------|--------|----------|----------|
| 单 seed 性能下滑 | seed_37 CPU throttle 20% | CWCI alarm → failover | < 5 ticks |
| 延迟注入 | +50ms broadcast latency | warning alert | < 20 ticks |
| 局部广播拥塞 | 30% packet drop | degraded detection | accurate |
| telemetry 丢包 | 10% metrics loss | alert + recovery | self-heal |
| failover 延迟 | 人为 delay backup activation | escalation | phone call |

### 演练记录表

| 日期 | 演练类型 | 注入时间 | 检测时间 | failover 时间 | 总延迟 | 结果 |
|------|----------|----------|----------|---------------|--------|------|
| - | - | - | - | - | - | ✅/❌ |

---

## Phase 3: 每日简报机制

每日 09:00 UTC，只看 5 个数。

```
P0 Daily Brief - YYYY-MM-DD
================================

Tier 1 (4x):
  CWCI:        x.xxx  [target: ≥0.65]
  Alerts:      x      [target: 0]
  Stability:   xx.x%  [target: >98%]

Tier 2 (6x):
  CWCI:        x.xxx  [target: ≥0.60]
  Degraded:    x/6    [target: ≤1]
  Failovers:   x      [target: ≤3/week]
  Stability:   xx.x%  [target: >95%]

Status: 🟢 NORMAL / 🟡 WATCH / 🔴 ACTION

Actions Required:
  - [ ] None
  - [ ] Pressure test today at HH:MM
  - [ ] Failover drill today at HH:MM
  - [ ] Review envelope boundary

On-Call: Name (available/unavailable)
```

---

## 触发条件响应矩阵

| 条件 | 响应 | 决策人 | 时间限制 |
|------|------|--------|----------|
| CWCI < 0.60 | 观察，加大监控 | Alex Chen | 立即 |
| CWCI < 0.58 | 准备降级 | Alex Chen | 30min |
| CWCI < 0.55 | **立即降级到 4x** | Dr. Williams | 5min |
| ≥2 seeds degraded | 准备降级 | Alex Chen | 15min |
| failover latency > 10 ticks | 激活 backup pool | Jordan Smith | 10min |
| stability < 90% | 周末复盘 envelope | Dr. Williams | 24h |

---

## 成功标准

**2 周后必须确认:**

- [ ] 6x 在压力下是否仍满足运营要求
- [ ] 降级 checklist 是否真的能执行
- [ ] failover 延迟是否稳定在 < 5 ticks
- [ ] envelope 边界是否需要调整

**产出:**
- Active Trigger Campaign Report
- Updated envelope boundary (if needed)
- Validated downgrade procedure

---

## 红线

- ❌ **绝不测试 8x**
- ❌ **绝不同时压力 > 50% seeds**
- ❌ **绝不夜间无 on-call 时测试**
- ❌ **绝不跳过 pre-check**

---

**启动审批**: _______________ (Dr. Sarah Williams)  
**启动日期**: _______________
