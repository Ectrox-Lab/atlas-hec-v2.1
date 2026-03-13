# Candidate 002: Soft Robot Proprioceptive Homeostasis

**Status**: BUILD_NOW  
**Date**: 2026-03-10  
**Risk**: Low  
**Readiness**: High  

---

## 1. Intake Memo (1 Page)

### Core Hypothesis
A soft robot with continuous proprioceptive feedback develops a body self-model through homeostatic regulation of pressure/strain distributions. The self-model emerges from prediction-error minimization between expected and actual proprioceptive states.

### Minimal Mechanism
- **Agent**: Soft body with deformable mesh (simulated or physical)
- **Sensors**: Pressure/strain sensors at mesh nodes
- **Controller**: Predictive model of body state + homeostatic setpoints
- **Feedback Loop**: Prediction → Action → Sensory Consequence → Error → Model Update

### Required State Variables
```python
{
  "proprioceptive_state": float[N_sensors],      # Current pressure/strain
  "predicted_state": float[N_sensors],           # Expected sensation
  "prediction_error": float[N_sensors],          # Mismatch signal
  "body_model_weights": float[N_sensors^2],      # Learned self-predictions
  "homeostatic_setpoint": float[N_sensors],      # Target state
  "self_boundary_map": bool[N_mesh_regions],     # What counts as "self"
}
```

### Minimal Experimental Environment
- **Task**: Boundary discrimination under pressure perturbation
- **Setup**: Robot body + external pressure sources + recovery tasks
- **Metrics**: 
  - Self-boundary discrimination accuracy
  - Prediction error recovery time
  - Body-map stability over perturbations

### Minimal Falsification Condition
- **Fail**: Removing proprioceptive feedback does NOT degrade self-boundary metrics
- **Fail**: Prediction loop does NOT affect identity-like state stability
- **Fail**: Body-map can be arbitrarily perturbed without recovery

### Most Likely Illusion
Treating any feedback loop as "self-model" without demonstrating:
- Persistent representation beyond immediate sensation
- Generalization to novel perturbations
- Resistance to contradictory evidence

---

## 2. Minimal Mechanism Spec

### Agent Definition
```
Agent: SoftBodyAgent
- Body: N-node deformable mesh
- Sensors: Pressure/strain at each node
- Actuators: Local stiffness modulation
- State: P(t) ∈ R^N (proprioceptive vector)
```

### Environment Definition
```
Environment: PressureChamber
- External pressure fields: E(t) ∈ R^N
- Perturbation sources: Random pressure injections
- Task boundary: Maintain pressure within viable range
```

### Key Feedback Loop
```
1. PREDICT: P̂(t+1) = f_body(P(t), A(t); θ)
2. ACT: A(t) = argmin_A ||P̂(t+1) - P_setpoint||
3. SENSE: P(t+1) = Environment(P(t), A(t), E(t))
4. ERROR: ε(t+1) = P(t+1) - P̂(t+1)
5. UPDATE: θ ← θ - α∇_θ ||ε||²
```

### Self-Model Variable
```python
# θ represents the learned body model
# Self-preservation: ||P(t) - P_setpoint|| < threshold
# Continuity: Smooth θ evolution over time
# Self-model quality: 1 / (1 + mean||ε||)
```

### Emergence Criteria
- **Appears**: System maintains stable θ despite perturbations; ε converges to low values
- **Absent**: θ fluctuates randomly; ε remains high; no recovery from perturbations

---

## 3. Minimal Experiment Design

### Experiment A: Self-Boundary Discrimination

**Setup**:
- Robot body in pressure chamber
- External pressure applied to random regions
- Task: Identify which region was perturbed

**Conditions**:
- **With feedback**: Full proprioceptive loop active
- **Without feedback**: Open-loop, no prediction error signal

**Metrics**:
```python
{
  "boundary_accuracy": correct_discriminations / total_trials,
  "recovery_time": steps_to_ε < threshold,
  "body_map_stability": 1 - ||θ(t) - θ(t-100)|| / ||θ||
}
```

**Success**: With-feedback >> Without-feedback on all metrics

### Experiment B: Prediction Error Recovery

**Setup**:
- Sudden pressure perturbation
- Measure return to setpoint

**Conditions**:
- Trained model (θ converged)
- Naive model (θ random)

**Metrics**:
- Recovery trajectory smoothness
- Steady-state error
- Oscillation damping

**Success**: Trained shows faster, smoother recovery

### Experiment C: Body Map Generalization

**Setup**:
- Train on pressure set A
- Test on novel pressure set B

**Metrics**:
- Transfer learning ratio
- Adaptation speed to new pressures

**Success**: Positive transfer (uses learned body structure)

---

## 4. Falsification Checklist

### Definite Fail Conditions

| # | Condition | If True |
|---|-----------|---------|
| F1 | Removing pressure feedback doesn't affect self-boundary metrics | Self-model is NOT proprioceptive |
| F2 | Prediction loop doesn't improve stability over reactive control | No self-model benefit |
| F3 | Body-map can be arbitrarily perturbed without recovery | No persistent representation |
| F4 | System performs equally well with randomized sensor positions | No spatial body structure |
| F5 | Performance doesn't generalize to novel pressure patterns | No learned model, just memorization |

### Warning Signs
- Performance improvement is marginal (< 20%)
- Self-model converges to trivial solution (e.g., zero)
- Requires hand-tuned setpoints for each condition

### Success Criteria
- [ ] Δ self-boundary accuracy > 30% with feedback
- [ ] Δ recovery speed > 50% with trained model
- [ ] Body-map weights show spatial structure (not random)
- [ ] Generalization to novel pressures > 70% of training performance

---

## 5. Priority Decision

**Decision**: BUILD_NOW

**Rationale**:
- Clear physical mechanism (proprioception)
- Testable in simulation or hardware
- Well-defined falsification conditions
- Moderate complexity (mesh + predictive model)

**Implementation Path**:
1. Week 1: 2D mesh simulation with pressure physics
2. Week 2: Add predictive model + learning
3. Week 3: Run Experiments A-C
4. Week 4: Analyze + document falsification results

**Fallback if Fails**:
- Simplify to 1D spring system
- Try different prediction architectures (RNN vs feedforward)
- Test if problem is embodiment vs learning

---

**Sign-off**: Ready for minimal implementation
