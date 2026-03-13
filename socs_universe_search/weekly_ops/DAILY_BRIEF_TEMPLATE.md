# P0 Daily Brief - Template

> **Version**: v1.0  
> **Campaign**: Active Trigger  
> **Frequency**: Daily 09:00 UTC

---

## Date: YYYY-MM-DD

### Tier 1 (4x) - Production

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Mean CWCI | x.xxx | ≥ 0.65 | 🟢/🟡/🔴 |
| Alerts | x | 0 | 🟢/🟡/🔴 |
| Stability | xx.x% | > 98% | 🟢/🟡/🔴 |

**Degraded Seeds**: x / 4

### Tier 2 (6x) - Active Trigger Campaign

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Mean CWCI | x.xxx | ≥ 0.60 | 🟢/🟡/🔴 |
| Degraded Seeds | x / 6 | ≤ 1 | 🟢/🟡/🔴 |
| Failover Count | x | ≤ 3/week | 🟢/🟡/🔴 |
| Alerts | x | 0 | 🟢/🟡/🔴 |
| Stability | xx.x% | > 95% | 🟢/🟡/🔴 |

**Campaign Day**: Day X of 14

### Today's Pressure Test

| Item | Status |
|------|--------|
| Scheduled | Yes / No |
| Type | [High Comm / High Broadcast / Long Run / Multi-seed / Mixed] |
| Window | HH:MM - HH:MM UTC |
| Pre-check | ⏳ / ✅ / ❌ |

### Failover Drill

| Item | Status |
|------|--------|
| Scheduled | Yes / No |
| Type | [CPU throttle / Latency / Congestion / Loss / Delay] |
| Result | ⏳ / ✅ / ❌ |

### Actions Required

- [ ] None
- [ ] Monitor closely
- [ ] Prepare downgrade
- [ ] **EXECUTE DOWNSGRADE**
- [ ] Escalate to Research Lead

### Events Log

| Time | Event | Severity | Action Taken |
|------|-------|----------|--------------|
| - | - | - | - |

### On-Call Status

**Primary**: Alex Chen - Available / Unavailable  
**Backup**: Jordan Smith - Available / Unavailable

---

**Next Brief**: YYYY-MM-DD 09:00 UTC

**Emergency**: Trigger downgrade immediately if CWCI < 0.55 or ≥2 seeds degraded
