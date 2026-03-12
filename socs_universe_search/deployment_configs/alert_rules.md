# Alert Rules - OctopusLike Production

**Version:** 1.0  
**Based on:** R6 validation results  
**Applies to:** Tier 2 (6x) deployments

---

## CWCI Degradation Alerts

### Warning (cwci < 0.60)
```yaml
rule: CWCI_WARNING
condition: cwci_live < 0.60
severity: warning
channels:
  - slack: #socs-alerts
  - pagerduty: low-priority
actions:
  - log_event
  - notify_oncall
  - increase_monitoring_frequency: 2x
response_time: 15 minutes
```

### Critical (cwci < 0.58)
```yaml
rule: CWCI_CRITICAL
condition: cwci_live < 0.58
severity: critical
channels:
  - slack: #socs-critical
  - pagerduty: high-priority
  - sms: oncall_engineer
actions:
  - log_event
  - trigger_seed_failover
  - notify_team_lead
  - begin_rollback_preparation
response_time: 5 minutes
```

### Emergency (cwci < 0.55)
```yaml
rule: CWCI_EMERGENCY
condition: cwci_live < 0.55
severity: emergency
channels:
  - slack: #socs-emergency
  - pagerduty: critical
  - phone: oncall_engineer
  - phone: team_lead
actions:
  - immediate_rollback_to_4x
  - quarantine_degraded_seed
  - post_incident_review_required
response_time: immediate
```

---

## Capability Degradation Alerts

### Specialization Drop
```yaml
rule: SPEC_DEGRADATION
condition: specialization_ratio < 0.60 for > 500 ticks
severity: warning
action: investigate_workload_pattern
```

### Integration Decoupling
```yaml
rule: INTEG_DECOUPLING
condition: integration_stability < 0.70 for > 500 ticks
severity: critical
action: prepare_failover
```

### Broadcast Saturation
```yaml
rule: BROADCAST_SAT
condition: broadcast_efficiency < 0.65 AND communication_cost > 0.35
severity: warning
action: scale_review_needed
```

---

## Seed Health Alerts

### Degraded Seed Detection
```yaml
rule: DEGRADED_SEED
condition: seed_cwci < 0.58 AND seed_status == "active"
severity: critical
action: 
  - quarantine_seed
  - activate_backup_seed
  - log_for_analysis
```

### Insufficient Healthy Seeds
```yaml
rule: LOW_HEALTHY_SEEDS
condition: healthy_seed_count < 6
severity: emergency
action: immediate_scale_reduction_to_4x
```

---

## Communication Overload Alerts

### Cost Threshold
```yaml
rule: COMM_COST_HIGH
condition: communication_cost > 0.35
severity: warning
threshold_duration: 1000 ticks
action: review_broadcast_topology
```

---

## Alert Suppression Rules

```yaml
maintenance_window:
  enabled: true
  suppress_all: false
  suppress_severity: [warning]
  allowed: [critical, emergency]
  
startup_grace_period:
  duration: 500 ticks
  suppress: [warning]
  allow: [critical, emergency]
```

---

## Alert Routing Matrix

| Severity | Slack | PagerDuty | SMS | Phone | Auto-Action |
|----------|-------|-----------|-----|-------|-------------|
| Warning | #socs-alerts | Low | No | No | Log only |
| Critical | #socs-critical | High | Yes | No | Failover |
| Emergency | #socs-emergency | Critical | Yes | Yes | Rollback |
