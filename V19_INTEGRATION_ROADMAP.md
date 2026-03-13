# v19 Integration Roadmap
## Bridging v18 CDI Success to v19 Unified Framework

**Version**: 1.0  
**Date**: 2026-03-09  
**Status**: v18 P0 Complete → v19 Design Phase

---

## Executive Summary

### Current State (v18)
```
CDI established as leading indicator
I_crit = 0.53 ± 0.01 (stable)
P1 causal protocol ready
```

### Target State (v19)
```
Unified state vector: [CDI, CI, r, N]
Multi-modal complexity dynamics
Independent early warning mechanisms
```

### Integration Strategy
**Don't abandon v18** — extend it with backward compatibility.

---

## Phase 1: v18 → v19 Bridge (Immediate)

### Goal
Validate CDI-CI relationship before full v19 implementation.

### Bridge Experiment: EXP-0 "CI Probe"

**Design**:
```
Use existing v18 data
Retroactively compute CI from network snapshots
Test correlation: CDI vs CI
```

**Procedure**:
```bash
# 1. Extract network states from v18 evolution logs
./extract_network_snapshots.py \
    --input /zeroclaw-labs/v18_1_experiments/*/evolution.csv \
    --output v18_network_states/

# 2. Compute CI for each snapshot
./compute_ci_retroactive.py \
    --networks v18_network_states/ \
    --output ci_timeseries_v18.csv

# 3. Correlate with CDI
./analyze_cdi_ci_correlation.py \
    --cdi v18_cdi.csv \
    --ci ci_timeseries_v18.csv \
    --output correlation_report.md
```

**Success Criteria**:
- |correlation(CDI, 1/CI)| > 0.6
- CI lead time ≥ CDI lead time (both predict extinction)

**Timeline**: 2-3 days

**Outcome Decision**:
- If success → Proceed to Phase 2 (v19 implementation)
- If failure → Re-examine CI definition before full v19

---

## Phase 2: v19 Core Implementation

### Module Integration Order

#### Step 1: CI Module (Network Condensation)
```python
# Add to Bio-World core
class BioWorldV19:
    def __init__(self):
        self.cdi = CDICalculator()      # existing v18
        self.ci = CondensationIndex()   # new v19
        
    def step(self):
        # ... existing dynamics ...
        self.metrics['CDI'] = self.cdi.compute()
        self.metrics['CI'] = self.ci.compute(network_state)
```

**Validation**: EXP-1 Condensation Test

---

#### Step 2: Synchronization Module (r)
```python
class SynchronizationModule:
    def compute_r(self, agent_phases):
        """Kuramoto order parameter"""
        return abs(sum(np.exp(1j * theta) for theta in agent_phases)) / N
```

**Validation**: EXP-2 Sync Stress Test

---

#### Step 3: Percolation Module (P)
```python
class PercolationModule:
    def compute_P(self, network):
        components = network.connected_components()
        return max(len(c) for c in components) / network.n_nodes
```

**Integration**: Monitor percolation transitions alongside CDI thresholds.

---

### Enhanced Output Format

**v18 format** (backward compatible):
```csv
generation,population,avg_cdi,extinct_count,alive_universes
```

**v19 format** (extended):
```csv
generation,population,avg_cdi,condensation_index,sync_r,percolation_p,extinct_count,alive_universes
```

---

## Phase 3: v19 + P1 Integration

### Unified Causal Testing

**P1-v19 Combined Design**:

| Experiment | Intervention | Target Variable | Expected Effect |
|------------|-------------|-----------------|-----------------|
| P1-A-v19 | Memory KO | CDI ↓ | CI ↑, r ↓ |
| P1-B-v19 | Cooperation ×0.3 | Network structure | CI change, P shift |
| P1-C-v19 | Boss pressure ×1.5 | Hazard modulation | r sensitivity change |
| **EXP-4** | **Sync decoupling** | **r → 0** | **Hazard ↑ independent of CDI** |

**New Experiment EXP-4**: "Synchronization Decoupling"
- Purpose: Test if sync loss alone can trigger hazard
- Intervention: Disable inter-agent communication
- Prediction: r → 0, hazard ↑, potential extinction even with high CDI

---

## Phase 4: Validation & Comparison

### v18 vs v19 Prediction Comparison

**Experiment**:
```
Run identical seeds on both v18 and v19
Compare:
  - Extinction prediction accuracy
  - Early warning lead time
  - False positive rate
```

**Metrics**:
```python
# Prediction accuracy
v18_score = auc_roc(true_extinctions, v18_cdi_predictions)
v19_score = auc_roc(true_extinctions, v19_unified_predictions)

# Expected: v19_score > v18_score by ≥ 10%
```

---

## Implementation Timeline

```
Week 1: Phase 1 (Bridge)
  Day 1-2: EXP-0 CI Probe
  Day 3: Analysis & decision
  
Week 2-3: Phase 2 (Core)
  Week 2: CI + Sync modules
  Week 3: Percolation + integration
  
Week 4: Phase 3 (P1-v19)
  P1-A/B/C with extended metrics
  EXP-4 Sync decoupling
  
Week 5-6: Phase 4 (Validation)
  v18 vs v19 comparison
  Documentation
```

---

## Key Integration Points

### Backward Compatibility

```python
# v19 can emulate v18
class BioWorldV19:
    def run_v18_mode(self):
        """Disable v19 modules, use only CDI"""
        self.ci_enabled = False
        self.sync_enabled = False
        
    def run_v19_mode(self):
        """Full unified framework"""
        self.ci_enabled = True
        self.sync_enabled = True
```

### Data Continuity

```
v18 data → v19 analysis
  ↓
Retroactive CI computation
Historical correlation validation
```

---

## Risk Mitigation

### Risk 1: CI Computation Too Expensive

**Mitigation**: 
- Sample-based estimation (top 10% hubs only)
- Compute every 10 generations (not every tick)

### Risk 2: Sync Module Noisy

**Mitigation**:
- Moving average smoothing
- Phase definition from multiple behaviors

### Risk 3: No Clear CDI-CI Relationship

**Mitigation**:
- Alternative CI definitions
- Explore CI as independent indicator (not inverse)

---

## Success Criteria for v19

### Technical
- [ ] CI computation < 5% performance overhead
- [ ] All 3 modules (CI, sync, percolation) functional
- [ ] Backward compatible with v18 data format

### Scientific
- [ ] |correlation(CDI, CI)| > 0.5 or independent predictive value
- [ ] Combined [CDI, CI, r] AUC-ROC > CDI alone by ≥ 10%
- [ ] At least one v19 metric provides earlier warning than CDI

### Integration
- [ ] P1-v19 causal experiments executable
- [ ] Documentation complete
- [ ] Reproduction pipeline functional

---

## Current Action Items

### Immediate (Today)
1. ✅ Create v19 framework document (done)
2. ⏳ Prepare EXP-0 CI Probe scripts
3. ⏳ Extract network data from v18 logs

### This Week
4. ⏳ Execute EXP-0, analyze correlation
5. ⏳ Decision: proceed to full v19?

### Next 2 Weeks (if go)
6. ⏳ Implement CI module
7. ⏳ Implement sync module
8. ⏳ Integrated testing

---

## Decision Points

### DP1: EXP-0 Results (Day 3)
- **Go**: |correlation| > 0.6 → proceed to Phase 2
- **Caution**: 0.3 < |correlation| < 0.6 → re-examine CI definition
- **Stop**: |correlation| < 0.3 → CI not useful, abandon v19

### DP2: Module Performance (Week 2)
- **Go**: Overhead < 5%, stability confirmed
- **Modify**: 5-15% overhead → optimization required
- **Simplify**: > 15% overhead → reduce computation frequency

### DP3: P1-v19 Results (Week 4)
- **Full v19**: Combined metrics outperform CDI alone
- **Partial v19**: Some modules useful, others not
- **Revert v18**: No improvement, maintain v18 focus

---

## Summary

### v19 Value Proposition
**From**: Single-indicator early warning (CDI)  
**To**: Multi-modal complexity state monitoring (CDI × CI × r)

**Scientific**: Deeper mechanistic understanding  
**Practical**: Potentially more robust predictions

### Conservative Approach
Don't replace v18 — **extend** it.
- v18 P1 continues as planned
- v19 modules add complementary information
- Backward compatibility maintained

### Aggressive Option (if EXP-0 very successful)
v19 becomes primary, v18 becomes "legacy mode".

---

*Roadmap Version*: 1.0  
*Decision Pending*: EXP-0 CI Probe results  
*Status*: Framework designed, awaiting bridge validation
