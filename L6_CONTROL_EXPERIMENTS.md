# L6 Control Experiments Design

> **Status**: Design Phase  
> **Purpose**: Establish that L5 inheritance is not artifact of structured trajectory  
> **Principles**: Trajectory v3.0 + Sole Reference v4.0

---

## Control Hypothesis

**Null Hypothesis**: Any structured trajectory with similar checksum properties will show comparable "transfer" effects, regardless of actual task relationships.

**Alternative Hypothesis**: L5 transfer effects require genuine task-related inheritance structure.

---

## Control Experiments

### Control 1: Shuffled Trajectory (结构保留，语义破坏)

```yaml
name: SHUFFLED_TRAJECTORY
description: |
  Keep all checksums, window counts, and statistical properties.
  Shuffle the temporal order of windows within each batch.
  
  If transfer is genuine, shuffling should reduce or eliminate effect.
  If effect is artifact of structure, shuffling should not matter.

procedure:
  1. Take Batch-1 (Code→Math) metrics
  2. Randomly shuffle window order (reassign window IDs)
  3. Maintain same checksums, same values
  4. Recalculate "transfer gap" (now meaningless)
  5. Compare effect size

expected_result_if_null: Effect remains ~14pp
expected_result_if_real: Effect drops to ~0 or noise level
```

### Control 2: Random Source-Target Pairing

```yaml
name: RANDOM_PAIRING
description: |
  Pair tasks randomly, ignoring actual task relationships.
  
  Example: "Math→Math" or "Planning→Planning" as "transfer"
  Or pair unrelated task definitions

procedure:
  1. Define 3 dummy tasks: DummyA, DummyB, DummyC
  2. Run 6 "transfers": DummyA→DummyB, etc.
  3. Same computational structure as L5
  4. No semantic task relationship

expected_result_if_null: Similar effect sizes (structure-only)
expected_result_if_real: Near-zero effects
```

### Control 3: Checksum-Preserving Semantic Break

```yaml
name: SEMANTIC_BREAK
description: |
  Preserve all trajectory metadata (checksums, lineage)
  but replace actual task execution with random/no-op computation.
  
  Tests whether effect comes from metadata structure or actual computation.

procedure:
  1. Keep all trajectory_summary.json structures
  2. Replace window execution with: random TG generation
  3. Maintain same statistical distribution of TG values
  4. No actual task computation occurs

expected_result_if_null: Same "positive" effects
expected_result_if_real: Effects collapse
```

### Control 4: Temporal Order Inversion

```yaml
name: TEMPORAL_INVERT
description: |
  Run target task BEFORE source task.
  
  Tests whether "inheritance" requires temporal causality
  or if any correlation produces effect.

procedure:
  1. Execute "target" task first (e.g., Math)
  2. Execute "source" task second (e.g., Code)
  3. Measure "reverse inheritance"
  
expected_result_if_null: Same effect (correlation ≠ causation)
expected_result_if_real: Effect only in forward direction
```

### Control 5: Source-Target Label Swap

```yaml
name: LABEL_SWAP
description: |
  Swap source and target labels while keeping actual task execution same.
  
  Example: Actually run Code→Math, but label as Math→Code

procedure:
  1. Execute Code computation
  2. Execute Math computation  
  3. Label trajectory as "Math→Code"
  4. Compare to actual Math→Code batch

expected_result_if_null: Similar effect sizes regardless of labels
expected_result_if_real: Effect matches actual task relationship, not labels
```

---

## Experimental Design

### Minimum Viable Controls

| Priority | Control | Effort | Information Value |
|:--------:|:--------|:------:|:-----------------:|
| 1 | Shuffled Trajectory | Low | High |
| 2 | Random Pairing | Medium | High |
| 3 | Temporal Inversion | Low | Medium |
| 4 | Semantic Break | High | Medium |
| 5 | Label Swap | Low | Low |

### Recommended L6 Scope

**Phase 1: Quick Controls** (1-2 hours)
- Shuffled Trajectory on Batch-1
- Temporal Inversion on Batch-1

**Phase 2: Strong Controls** (2-3 hours)
- Random Pairing (6 pairs)
- If time: Semantic Break

---

## Success Criteria

### For L5 Validation to Hold

```yaml
shuffled_control:
  shuffled_effect: "< 50% of original"
  interpretation: "Temporal/structural order matters"
  
random_pairing_control:
  random_effect: "< 3pp or negative"
  interpretation: "Task relationship required"
  
temporal_inversion_control:
  inverted_effect: "< 50% of forward"
  interpretation: "Causality matters, not just correlation"
```

### If Controls Fail (Effect Persists)

```yaml
implications:
  - Effect may be artifact of trajectory structure
  - Need deeper mechanism analysis
  - L5 findings require qualification
  
next_steps:
  - Investigate what structural properties drive effect
  - Control for trajectory length, checksum diversity, etc.
  - Consider if effect is purely statistical
```

---

## Integration with L5 Report

### Where to Include

```markdown
## Robustness Controls (L6)

To establish that L5 effects are not artifacts of trajectory structure,
we conducted [N] control experiments:

### Control 1: Shuffled Trajectory
- Method: [Description]
- Result: [Effect reduced to X%]
- Interpretation: [Effect requires temporal structure]

### Control 2: Random Pairing
- Method: [Description]
- Result: [Mean TG = Ypp vs 9.34pp in real pairs]
- Interpretation: [Task relationship required]

Conclusion: L5 effects are robust to structural controls,
suggesting genuine task-related inheritance.
```

---

## Execution Plan

### Immediate (Next 2 hours)

```bash
# Control 1: Shuffled Batch-1
python3 shuffle_control.py --batch l5_batch1

# Control 2: Temporal Inversion
python3 temporal_invert.py --forward l5_batch1 --reverse l5_batch3_b2a
```

### Following Days

```bash
# Control 3: Random Pairing (full L6)
python3 random_pairing.py --n_pairs 6 --n_windows 10

# If needed: Semantic Break
python3 semantic_break.py --preserve bootstrap_analysis.json
```

---

## Expected Timeline

| Phase | Duration | Output |
|:------|:--------:|:-------|
| Quick Controls | 2 hours | Shuffled + Inversion results |
| Analysis | 1 hour | Comparison with L5 |
| Full Controls | 3 hours | Random pairing complete |
| Integration | 1 hour | Updated L5 report with controls |
| **Total** | **~7 hours** | Publication-ready robustness |

---

## Caution

**Do not over-control.** 

Each control should test a specific alternative hypothesis:
- Structure artifact? → Shuffle
- Random correlation? → Random pairing
- Causality vs correlation? → Temporal inversion

Avoid controls that test the same thing multiple times.

---

*L6 Control Experiments Design v1.0*
