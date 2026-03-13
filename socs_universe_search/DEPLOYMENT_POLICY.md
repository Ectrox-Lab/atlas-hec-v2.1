# Deployment Policy - OctopusLike

**Version:** 1.0  
**Date:** 2026-03-12  
**Based on:** P0 R1-R6 Validation Results

---

## Approved Deployments

### Tier 1: Mission-Critical (4x)
```yaml
scale: 4x
cwci_expected: 0.655
retention: 95.2%
degradation_risk: 0%
monitoring: none required
approval: IMMEDIATE
```

### Tier 2: Production (6x with Monitoring)
```yaml
scale: 6x
cwci_expected: 0.641
retention: 97.9%
degradation_risk: 12.5% (1/8 seeds)
monitoring: REQUIRED
  - seed_level_cwci: true
  - alert_threshold: 0.58
  - auto_failover: true
approval: WITH MONITORING INFRASTRUCTURE
```

## Prohibited Deployments

### Tier 3: Experimental Only (8x)
```yaml
scale: 8x
cwci_expected: 0.576 (mean), 0.300 (worst)
degradation_risk: 25% (2/8 seeds)
approval: RESEARCH USE ONLY
notes: Not suitable for production workloads
```

---

## Operational Checklist

### Pre-Deployment (Tier 1)
- [ ] Confirm 4x scale configuration
- [ ] No monitoring required
- [ ] Deploy

### Pre-Deployment (Tier 2)
- [ ] Confirm 6x scale configuration
- [ ] Verify monitoring infrastructure:
  - [ ] Per-seed CWCI tracking enabled
  - [ ] Alert rules configured (CWCI < 0.58)
  - [ ] Failover mechanism tested
- [ ] Deploy with monitoring

### Post-Deployment (Both Tiers)
- [ ] Initial health check (first 1000 ticks)
- [ ] Weekly performance review
- [ ] Quarterly envelope re-validation

---

## Emergency Procedures

### Degradation Detected (Tier 2)
1. Alert triggered: Seed CWCI < 0.58
2. Automatic: Trigger failover to healthy seed
3. Manual: Review telemetry, consider scale reduction to 4x
4. Document: Add to degradation registry

---

## References

- P0_OPERATIONAL_ENVELOPE.md - Full envelope definition
- outputs/r4_validation_report.json - 4x validation
- outputs/r6_validation_report.json - 6x validation  
- outputs/r5_validation_report.json - 8x boundary
- outputs/degradation_audit_report.json - Paired-seed analysis
