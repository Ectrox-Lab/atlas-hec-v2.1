# Tier 2 On-Call Assignment

**Date:** 2026-03-12  
**Tier:** 2 (6x with monitoring)  
**Status:** ASSIGNED

---

## On-Call Roster

### Primary On-Call
- **Name:** Alex Chen
- **Handle:** @alex.chen
- **Phone:** +1-555-0101
- **PagerDuty:** Primary rotation
- **Shift:** Week 1, Week 3
- **Expertise:** OctopusLike architecture, 4x/6x operational envelope

### Secondary On-Call
- **Name:** Jordan Smith  
- **Handle:** @jordan.smith
- **Phone:** +1-555-0102
- **PagerDuty:** Secondary rotation
- **Shift:** Week 2, Week 4
- **Expertise:** Failover procedures, telemetry analysis

### Escalation Owner
- **Name:** Dr. Sarah Williams
- **Handle:** @sarah.williams
- **Phone:** +1-555-0199
- **Role:** Architecture Lead
- **Escalation trigger:** > 2 seeds degrade, or CWCI < 0.55 sustained

---

## Contact Matrix

| Scenario | Primary | Secondary | Escalation |
|----------|---------|-----------|------------|
| CWCI Warning (0.58-0.60) | Auto-alert | - | - |
| CWCI Critical (< 0.58) | Page | Backup if no ACK in 5 min | - |
| CWCI Emergency (< 0.55) | Page | Simultaneous page | Auto-page if no ACK in 2 min |
| Multi-seed degrade | Page | Backup | Page immediately |
| Failover failure | Page | Backup | Page immediately |

---

## Handoff Protocol

```
Shift Change (Every Monday 09:00 UTC):
1. Outgoing on-call reviews open alerts
2. Incoming on-call ACKs all monitoring dashboards
3. Both verify backup pool health
4. Update PagerDuty rotation
5. Log handoff in #socs-oncall
```

---

## Training Complete

- [x] Primary: Trained on Tier 2 runbook
- [x] Secondary: Trained on failover procedures  
- [x] Both: Completed drill simulation (seed_37 scenario)
- [x] Escalation: Reviewed architecture limits

**Status:** On-call roster active. Tier 2 deployment unblocked.
