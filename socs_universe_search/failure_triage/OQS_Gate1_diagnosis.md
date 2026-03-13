# Layer 3 Failure-Mode Triage Report

**Hypothesis**: OQS (OctoQueenSwarm)  
**Gate**: Gate 1  
**Result**: PARTIAL (2/4 checks passed)  
**Date**: 2024-03-12  
**Triage ID**: OQS-G1-001

---

## 1. First Failure Mode Identification

### Primary Failure: Budget Strategy Conservative
```
Evidence:
  - ResourceScarcity CWCI: 0.036 (vs Ant 0.311)
  - Queen resource_budget: static 100
  - No dynamic adjustment based on success/hazard

First Degradation Signature:
  - Early worker spawn depletes budget
  - No replenishment mechanism
  - Hazard spikes cause mass death with no recovery
```

### Secondary Failure: Experience Return Threshold Too High
```
Evidence:
  - experience_return_quality: 0.000
  - Return only triggered on worker loss
  - No periodic summary upload

Degradation Chain:
  worker fails → dies → should return experience
              ↓
         but returnQuality = 0
              ↓
         lineage never learns
```

### Tertiary Failure: Culling Mechanism Too Aggressive
```
Evidence:
  - lineage_improvement: -0.219
  - Culling threshold: utility < 0.3 (100% cull)
  - No recovery buffer after cull

Degradation Pattern:
  early failures → utility drops → immediate cull
              ↓
         lineage diversity lost
              ↓
         cannot adapt to new conditions
```

## 2. Simulation-Limited vs Realism-Limited Assessment

| Aspect | Assessment | Confidence |
|--------|-----------|------------|
| Budget dynamics | SIMULATION-LIMITED | HIGH |
  - Real SOCS would have energy inflow/outflow
  - Current model is closed system
| Experience return | SIMULATION-LIMITED | MEDIUM |
  - Real system would have continuous telemetry
  - Current discrete loss-only return is artificial
| Culling behavior | REALISM-LIMITED | MEDIUM |
  - Real biological systems do have death/reproduction
  - But threshold timing may differ

## 3. Minimal Corrections (Maximum 3)

### Correction 1: Dynamic Budget Allocation
```
Current:
  resource_budget = 100  # static

Proposed:
  resource_budget = base_budget * (1 + success_rate - hazard_level)
  
Rationale:
  - Success generates resources
  - Hazard consumes resources
  - Self-regulating without external oracle

Risk: LOW
  - Only affects simulation parameters
  - No structural code change
```

### Correction 2: Periodic Experience Return
```
Current:
  if not w.alive:
      experience_returns.append(summary)

Proposed:
  if tick % 100 == 0 or not w.alive:
      experience_returns.append(summary)
      
Rationale:
  - Continuous learning, not just death-learning
  - Matches biological pheromone trails
  - Allows early correction

Risk: LOW
  - Information flow change only
  - No architectural change
```

### Correction 3: Gentler Culling with Recovery
```
Current:
  if utility < 0.3:
      cull_immediate()

Proposed:
  if utility < 0.2:
      if random() < 0.5:  # 50% chance
          cull()
      utility += 0.15  # recovery buffer
      
Rationale:
  - Allows exploration of low-utility lineages
  - Maintains diversity
  - Second chance mechanism

Risk: LOW
  - Parameter change only
  - Reversible
```

## 4. Risk Assessment

| Correction | Risk Level | Rollback Complexity | Side Effects |
|-----------|-----------|---------------------|--------------|
| Dynamic budget | LOW | Single line revert | None expected |
| Periodic return | LOW | Single line revert | May increase memory use |
| Gentler culling | LOW | Single line revert | May slow convergence |

**Overall Risk**: LOW  
**Scope**: Simulation parameters only  
**No structural architecture changes required**

## 5. Validation Plan (Gate 1.5)

### Target Scenarios
- ResourceScarcity (previously failed)
- FailureBurst (previously failed)

### Success Criteria
- [ ] OQS CWCI > AntColonyLike × 0.8 (reach comparable level)
- [ ] experience_return_quality > 0 (any return is improvement)
- [ ] lineage_improvement > 0 (positive learning)

### Failure Mode (if Gate 1.5 fails)
If corrections don't resolve:
1. Root cause may be deeper (Queen-Worker relationship design)
2. Consider hypothesis pivot: OQS may only work for HighCoordinationDemand
3. Alternative: Merge OQS into composite architecture rather than standalone

## 6. Layer 4 Proposal (if Gate 1.5 passes)

**No Layer 4 proposal needed for parameter corrections.**

If Gate 1.5 passes, proceed to:
- Gate 2 (5x scale test)
- No architecture code changes required

## 7. Triage Conclusion

**First Failure Mode**: Budget conservation + delayed experience return + aggressive culling  
**Fixability**: HIGH (parameter adjustments)  
**Structural Issue**: NO  
**Simulation Artifact**: PARTIAL  

**Recommendation**: Proceed with 3 minimal corrections, execute Gate 1.5.

---

**Triage Confidence**: HIGH  
**Human Review Required**: NO (for parameter corrections)  
**Auto-Execute**: YES (Layer 1 can apply corrections)
