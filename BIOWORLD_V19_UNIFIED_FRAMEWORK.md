# Bio-World v19 Unified Framework
## Integrating Historical Mechanisms with CDI Dynamics

**Version**: v19.0-alpha  
**Date**: 2026-03-09  
**Goal**: Unify network condensation, synchronization, percolation with CDI framework

---

## 1. Historical Mechanisms Inventory

### Verified Mechanisms from Legacy Experiments

| Mechanism | Evidence | System Behavior | Integration Priority |
|-----------|----------|-----------------|---------------------|
| **Network Condensation** | CI → structural concentration | CDI ↓ correlates with collapse | **Tier 1 - Required** |
| **Percolation Transition** | k ≈ 1 → giant component | Knowledge network connectivity | **Tier 1 - Required** |
| **Scale-free Hub Emergence** | Synapse ~ power law | Tool/language/memory hubs | **Tier 1 - Required** |
| **Synchronization Order Parameter** | Kuramoto r ≈ 0.5 threshold | Collective coordination | **Tier 1 - Required** |
| Intrinsic Drives | Hunger/curiosity/social | Agent-level behavior | Tier 2 - Module |
| Energy-Metabolism Coupling | ATP field, diffusion | Resource pressure | Tier 2 - Module |

---

## 2. Unified State Vector

### Extended System State

```python
S(t) = [CDI, CI, r, N, E]

Where:
  CDI = Complexity-Degradation-Index        [0, 1]
  CI  = Condensation Index (structural)     [0, 1]  
  r   = Synchronization order parameter     [0, 1]
  N   = Population                          [0, K]
  E   = Energy/resource availability        [0, ∞]
```

### Hypothesized Structural Relationships

```
CDI = f(memory, cooperation, innovation)
  ↓
CI = g(network hubs, degree distribution)
  ↓  
r = h(connectivity, communication strength)
  ↓
dN/dt = -hazard(CDI, CI, r, E)
```

**Key Hypothesis**: CDI ≈ inverse structural condensation

---

## 3. New Computational Modules

### MODULE 1: Network Condensation (CI)

**Definition**:
```
CI = Σ(k_i²) / (Σ k_i)²

Where k_i = degree of node i
Alternative: CI = hub_concentration = k_max / Σk_i
```

**Integration**:
- Track CI(t) alongside CDI(t)
- Test: CI ↑ before collapse?
- Relationship: dCI/dt = -α · dCDI/dt (?)

**Implementation**:
```python
def compute_condensation_index(network):
    degrees = [node.degree for node in network.nodes]
    k_squared_sum = sum(k**2 for k in degrees)
    k_sum_squared = sum(degrees)**2
    return k_squared_sum / k_sum_squared if k_sum_squared > 0 else 0
```

---

### MODULE 2: Synchronization (r)

**Definition** (Kuramoto order parameter):
```
r = | Σ e^(iθ_j) | / N

Where θ_j = phase of agent j
  (behavior phase or communication phase)
```

**Integration**:
- Compute r(t) from agent coordination patterns
- Test relationship: r vs CDI
- Hypothesis: High sync → stability, Low sync → hazard

**Implementation**:
```python
def compute_sync_order_parameter(phases):
    """phases: array of agent phase angles"""
    complex_sum = sum(np.exp(1j * theta) for theta in phases)
    return abs(complex_sum) / len(phases)
```

---

### MODULE 3: Percolation

**Definition**:
```
P = largest_component_size / N

Percolation transition when P jumps from ~0 to ~1
```

**Integration**:
- Monitor knowledge/tool network connectivity
- Detect giant component formation
- Test: Percolation threshold vs I_crit

**Implementation**:
```python
def compute_percolation_parameter(network):
    components = network.find_connected_components()
    largest = max(len(c) for c in components) if components else 0
    return largest / network.n_nodes if network.n_nodes > 0 else 0
```

---

## 4. Enhanced Monitoring Dashboard

### Generation-Level Metrics Output

| Metric | Symbol | Computation | Purpose |
|--------|--------|-------------|---------|
| Population | N | count(agents) | System size |
| CDI | CDI | complexity_function() | Structural quality |
| Condensation | CI | Σk²/(Σk)² | Network concentration |
| Synchronization | r | \|Σe^(iθ)\|/N | Collective coordination |
| Percolation | P | max_component/N | Connectivity phase |
| Energy | E | total_energy | Resource pressure |
| Hazard | h | d(extinctions)/dt | Instability rate |

**Output File**: `system_state.csv`

```csv
generation,N,CDI,CI,r,P,E,h,extinct_count,alive_universes
```

---

## 5. Critical Scientific Questions

### Q1: CDI Collapse vs Network Condensation

**Hypothesis**: CDI decline ↔ CI increase (inverse relationship)

**Test**:
```python
# Compute correlation
corr = pearsonr(dCDI/dt, dCI/dt)
# Expected: strong negative correlation
```

**Implication**: If confirmed, CI can serve as early warning independent of CDI.

---

### Q2: Hub Formation → Instability?

**Hypothesis**: Excessive hub concentration reduces system resilience

**Test**: Remove top 5% connectivity agents, observe:
- CDI stability change
- Hazard rate change
- Extinction timing

**Implication**: Scale-free structure may have optimal hub concentration.

---

### Q3: Synchronization → Extinction Cascade?

**Hypothesis**: Loss of synchronization precedes/hastens extinction

**Test**: Manipulate communication strength, observe:
- r change
- hazard change
- cascade dynamics

**Implication**: Coordination breakdown may be causal factor, not just symptom.

---

## 6. New Experiment Designs (v19)

### EXP-1: Condensation Test

**Purpose**: Does CI rise before extinction?

**Procedure**:
```
Run 5 seeds with CI tracking
Monitor: CI(t), CDI(t), extinction(t)
Test: CI peaks before CDI minimum?
```

**Success Criteria**:
- CI lead time > 100 generations before extinction
- Correlation(CI, 1/CDI) > 0.7

---

### EXP-2: Synchronization Stress

**Purpose**: Communication overload effect

**Intervention**:
```
communication_strength × 2
or
sync_coupling ↑ 50%
```

**Measurements**:
- r(t) trajectory
- hazard rate change
- extinction timing shift

**Hypothesis**: Over-synchronization may increase fragility ("herd behavior")

---

### EXP-3: Hub Knockout

**Purpose**: Network resilience test

**Intervention**:
```
At generation 3000:
  Identify top 5% connectivity agents
  Remove or disable
Monitor recovery or collapse
```

**Measurements**:
- CDI stability
- Network reorganization time
- Final extinction outcome

**Implication**: Tests whether hubs are critical infrastructure.

---

## 7. Legacy Experiment Integration

### Directory Structure

```
experiments/
├── legacy/
│   ├── legacy_sync/           # Synchronization baselines
│   │   ├── run_legacy.sh
│   │   └── analyze_legacy.py
│   ├── legacy_fractal/        # Network structure
│   ├── legacy_ecosystem/      # Energy/metabolism
│   └── legacy_biobrain/       # Memory/learning
└── integrated/
    ├── v19_unified/           # New unified experiments
    └── v18_cdi_only/          # CDI baseline
```

### Baseline Comparison

Use legacy experiments to validate:
- CI computation consistency
- r measurement accuracy
- Percolation detection sensitivity

---

## 8. Minimum Reproduction Pipeline

```bash
# 1. Run experiment
./run_bioworld_v19.sh --config unified_config.yaml

# 2. Compute metrics
./compute_cdi.py --input evolution.csv --output cdi_series.csv
./compute_ci.py --input network_state.json --output ci_series.csv
./compute_sync.py --input agent_phases.json --output r_series.csv
./detect_percolation.py --input network.json --output percolation_events.csv

# 3. Unified analysis
./analyze_unified.py \
    --cdi cdi_series.csv \
    --ci ci_series.csv \
    --sync r_series.csv \
    --output unified_analysis/

# 4. Generate report
./generate_v19_report.py --analysis unified_analysis/ --output report.md
```

---

## 9. Unified Theory Structure

### Complete Dynamics

```
[COMPLEXITY LAYER]
CDI = f(memory, cooperation, innovation, learning)
  ↓
  
[STRUCTURE LAYER]  
CI = g(CDI, network_plasticity)     [condensation]
P = h(CI, connection_probability)   [percolation]
  ↓
  
[COORDINATION LAYER]
r = k(P, communication_strength)    [synchronization]
  ↓
  
[POPULATION LAYER]
dN/dt = -hazard(CDI, CI, r) · N     [extinction]
  ↓
  
[EXTINCTION CASCADE]
when N < N_crit: cascade propagation
```

### State Space Visualization

```python
# 3D phase space: CDI × CI × r
def plot_state_space(states):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(states.CDI, states.CI, states.r, c=states.N, cmap='viridis')
    ax.set_xlabel('CDI')
    ax.set_ylabel('CI')
    ax.set_zlabel('Sync r')
    plt.show()
```

---

## 10. Priority Roadmap

### Phase 1: Validation (v18 → v19 bridge)

**Priority**: Prove CDI-CI relationship

**Experiments**:
1. EXP-1: Condensation test (5 seeds)
2. Correlation analysis: CDI vs CI
3. Compare with P0 results

**Timeline**: 1 week

---

### Phase 2: Integration (v19 core)

**Priority**: Full unified framework

**Experiments**:
1. EXP-2: Synchronization stress
2. EXP-3: Hub knockout
3. Combined metric validation

**Timeline**: 2 weeks

---

### Phase 3: Universality (v19+ extension)

**Priority**: Cross-environment stability

**Tests**:
- I_crit stability across parameter variations
- CI-r-CDI relationship robustness
- Predictive power comparison

**Timeline**: 2 weeks

---

## 11. Key Historical Assets to Recover

### Must-Have Modules

| Asset | Source | Priority | Integration |
|-------|--------|----------|-------------|
| Fractal network generator | legacy_fractal | High | Network initialization |
| Condensation metric | legacy_sync | High | CI computation |
| Kuramoto sync | legacy_sync | High | r computation |
| Intrinsic drives | legacy_ecosystem | Medium | Agent behavior |
| Energy field | legacy_ecosystem | Medium | Resource dynamics |

---

## 12. Success Metrics for v19

### v19 is successful if:

1. **Relationship Confirmed**: CDI and CI show strong inverse correlation (|r| > 0.7)
2. **Early Warning**: CI provides independent early warning (lead time > 100 gen)
3. **Synchronization Effect**: r changes causally affect hazard rate
4. **Unified Prediction**: Combined [CDI, CI, r] predicts extinction better than CDI alone
5. **Mechanism Separation**: Can distinguish structural (CI) vs environmental (E) effects

---

## Summary

### Current Achievement (v18)
```
CDI → hazard → extinction  [ESTABLISHED]
```

### v19 Extension
```
[CDI, CI, r] → unified hazard → extinction  [TARGET]
```

### Scientific Advance
From: Single indicator (CDI)  
To: Multi-modal complexity state (CDI × CI × r)

### Expected Outcome
More robust early warning, mechanistic understanding of collapse.

---

*Framework Version*: v19.0-alpha  
*Based on*: v18 CDI foundation + historical mechanism integration  
*Next Milestone*: EXP-1 Condensation Test validation
