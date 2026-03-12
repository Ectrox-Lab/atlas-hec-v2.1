# Operational Runbook - OctopusLike Production

**Version:** 1.0  
**Last Updated:** 2026-03-12  
**Applies to:** Tier 1 (4x) and Tier 2 (6x) deployments

---

## Quick Reference

| Tier | Scale | Risk | Monitoring | Action on Alert |
|------|-------|------|------------|-----------------|
| Tier 1 | 4x | Minimal | Optional | N/A (guaranteed safe) |
| Tier 2 | 6x | Low | Required | Failover if CWCI < 0.58 |

---

## Daily Operations

### Morning Check (Start of Shift)

```bash
# Tier 1 (4x) - Quick verification
socs-status --tier 1
# Expected: All green, no action needed

# Tier 2 (6x) - Full health check
socs-status --tier 2 --detailed
# Check:
#   - Active seeds: 8/8 healthy
#   - Backup pool: 2/2 available
#   - CWCI range: 0.60 - 0.65
#   - No alerts from last 24h
```

### Continuous Monitoring (Tier 2 only)

```yaml
monitoring_dashboard:
  refresh_interval: 30 seconds
  
  primary_metrics:
    - cwci_live: "watch for < 0.60"
    - healthy_seed_count: "alert if < 6"
    - degradation_events: "log all"
    
  secondary_metrics:
    - communication_cost: "trending"
    - specialization_ratio: "stable > 0.60"
    - integration_stability: "stable > 0.70"
```

---

## Deployment Procedures

### New Tier 1 Deployment (4x)

```bash
# 1. Pre-deployment checklist
socs-check --tier 1 --pre-deploy
[✓] Resources available
[✓] No existing conflicts
[✓] Seed pool validated

# 2. Deploy
socs-deploy \
  --tier 1 \
  --scale 4x \
  --config tier1_deployment_config.yaml \
  --name <service_name>

# 3. Post-deployment verification (within 100 ticks)
socs-verify --deployment <service_name>
[✓] CWCI > 0.65
[✓] No errors
[✓] Performance nominal

# 4. Mark production ready
socs-promote --deployment <service_name> --status production
```

### New Tier 2 Deployment (6x)

```bash
# 1. Pre-deployment checklist
socs-check --tier 2 --pre-deploy
[✓] Monitoring infrastructure ready
[✓] Alert rules configured
[✓] Failover procedure tested
[✓] On-call engineer assigned

# 2. Deploy with monitoring
socs-deploy \
  --tier 2 \
  --scale 6x \
  --config tier2_monitoring_config.yaml \
  --monitoring-config alert_rules.md \
  --name <service_name>

# 3. Initialize monitoring
socs-monitoring init --deployment <service_name>
socs-alerting enable --deployment <service_name>

# 4. Verification (within 500 ticks)
socs-verify --deployment <service_name> --extended
[✓] All 8 seeds healthy (CWCI > 0.60)
[✓] Backup pool ready
[✓] Alerts functioning (test alert sent)
[✓] Failover tested (dry-run)

# 5. Gradual traffic ramp
socs-traffic --deployment <service_name> --ramp 10% per 100 ticks
Monitor for degradation at each step

# 6. Full production
socs-promote --deployment <service_name> --status production
```

---

## Alert Response Procedures

### CWCI Warning (0.58 - 0.60)

```
1. Acknowledge alert
2. Check dashboard - is it trending down?
3. Review recent changes
4. Increase monitoring frequency
5. If continues trending: Prepare failover
6. Document in incident log
```

### CWCI Critical (< 0.58)

```
1. Acknowledge immediately
2. Auto-failover should trigger
3. Verify failover success:
   - New seed active
   - CWCI recovering > 0.60
   - Traffic flowing
4. Quarantine degraded seed
5. Notify team lead
6. Begin root cause analysis
```

### Multiple Seed Degradation

```
1. Emergency protocol
2. Consider scale-down to 4x
3. Page team lead immediately
4. Preserve all telemetry
5. Post-incident review within 24h
```

---

## Maintenance Windows

### Scheduled Maintenance

```bash
# 1. Schedule window
socs-maintenance schedule \
  --start <timestamp> \
  --duration <ticks> \
  --impact minimal

# 2. Suppress non-critical alerts
socs-alerting suppress --severity warning --window <maintenance_window>

# 3. Execute maintenance
# ... perform updates ...

# 4. Verify post-maintenance
socs-verify --full

# 5. Resume alerts
socs-alerting resume
```

### Emergency Maintenance

```
1. Assess risk of continuing vs stopping
2. If stopping: Execute Type B failover (scale-down)
3. Perform emergency fix
4. Verify thoroughly before restoring
5. Document all actions
```

---

## Troubleshooting Guide

### Issue: CWCI slowly declining

**Possible Causes:**
- Workload pattern change
- Resource contention
- Gradual degradation onset (seed 42 pattern)

**Actions:**
1. Review workload logs
2. Check resource utilization
3. If CWCI < 0.60: Prepare proactive failover
4. Consider moving to 4x if trend continues

### Issue: Intermittent spikes

**Possible Causes:**
- External interference
- Network instability
- Measurement noise

**Actions:**
1. Verify monitoring system health
2. Check external dependencies
3. If confirmed real: Investigate root cause

### Issue: Failover didn't work

**Immediate Actions:**
1. Manual seed replacement
2. If multiple seeds: Emergency scale-down
3. Page on-call immediately
4. Preserve all logs for analysis

---

## Reporting

### Daily Report (Tier 2)

```yaml
daily_summary:
  date: <YYYY-MM-DD>
  tier2_deployments:
    total: <count>
    healthy: <count>
    degraded_events: <count>
    failovers: <count>
    
  metrics:
    avg_cwci: <value>
    min_cwci: <value>
    healthy_seed_ratio: <percentage>
    
  incidents: <list or "none">
  
  actions_required: <list or "none">
```

### Weekly Review

- Degradation trends
- Failover effectiveness
- Alert noise review
- Capacity planning

---

## Contact Information

| Role | Contact | Escalation |
|------|---------|------------|
| On-call Engineer | PagerDuty Rotation | 15 min |
| Team Lead | Slack: @team-lead | 30 min |
| Architect | Slack: @architect | 1 hour |
| Emergency | Phone: +xxx | Immediate |

---

## Document Control

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-03-12 | Initial release | SOCS Autoresearch |

---

**Remember:** 
- Tier 1 (4x) = Set and forget (guaranteed safe)
- Tier 2 (6x) = Monitor actively (12.5% risk)
- When in doubt: Scale down to 4x
