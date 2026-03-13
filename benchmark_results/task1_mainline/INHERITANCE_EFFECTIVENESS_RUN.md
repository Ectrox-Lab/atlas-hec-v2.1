# Task-1 Inheritance Effectiveness Run: Plan

**Goal**: Verify that Akashic Task-1 inheritance package actually improves next-round search quality.

**Status**: PLANNED - Ready for execution

---

## The Critical Question

Does inheritance work?

```
Without Inheritance          With Inheritance
      ↓                           ↓
[Random Candidates]  vs.  [Bias toward known-good]
      ↓                           ↓
   Bridge                      Bridge
      ↓                           ↓
   Mainline                    Mainline
      ↓                           ↓
  Success?                   Success?
```

**Null hypothesis**: Inheritance doesn't change outcomes (package ignored).  
**Alternative**: Inheritance measurably shifts candidate distribution toward better outcomes.

---

## Experimental Design

### Round A: Control (No Inheritance)

**Setup**:
- Fast Genesis generates candidates WITHOUT reading Task-1 inheritance package
- Generation uses default priors (trust_decay: 0.0-0.2, trust_recovery: 0.0-0.1)
- Random mutation around baseline

**Expected**:
- High variance in outcomes
- Many candidates FAIL at Bridge
- Few APPROVE at Mainline
- Throughput improvement scattered around zero

### Round B: Treatment (With Inheritance)

**Setup**:
- Fast Genesis reads `task1_inheritance_package.json` from Akashic
- Generation biased toward:
  - trust_decay ∈ [0.05, 0.15] (from successful priors)
  - trust_recovery ∈ [0.03, 0.08]
  - Migration_threshold ∈ [0.2, 0.4]
  - Avoid known failure patterns

**Expected**:
- Lower variance (more consistent)
- Higher Bridge pass rate
- More Mainline APPROVEs
- Throughput improvement clustered above baseline

---

## Success Metrics

| Metric | Round A (Control) | Round B (Inheritance) | Target Improvement |
|--------|-------------------|----------------------|-------------------|
| **Bridge Pass Rate** | ~30% | >40% | +10pp |
| **Mainline Approve Rate** | ~10% | >20% | +10pp |
| **Mean Throughput Δ** | ~0% | >+0.5% | +0.5pp |
| **Failure Archetype Reproduction** | ~20% | <10% | -10pp |
| **Candidate Variance** | High | Lower | CV reduction |

---

## Implementation Plan

### Phase 1: Generate Control Batch (Round A)

```bash
# Generate 50 candidates without inheritance
python superbrain/fast_genesis/generate_candidates.py \
  --count 50 \
  --task-family task1 \
  --no-inheritance \
  --output round_a_candidates/

# Run through Bridge
python superbrain/bridge/bridge_scheduler.py \
  --input round_a_candidates/ \
  --output round_a_bridge_results/

# Run approved through Mainline (subset)
python superbrain/mainline/task1_mainline_validator.py \
  --input round_a_bridge_results/ \
  --output round_a_mainline_results/
```

### Phase 2: Generate Treatment Batch (Round B)

```bash
# First, ensure Akashic has written inheritance package
python socs_universe_search/multiverse_engine/akashic_memory_v2.py \
  --save-inheritance task1_inheritance_package.json

# Generate 50 candidates WITH inheritance
python superbrain/fast_genesis/generate_candidates.py \
  --count 50 \
  --task-family task1 \
  --inheritance-package task1_inheritance_package.json \
  --output round_b_candidates/

# Same pipeline
python superbrain/bridge/bridge_scheduler.py \
  --input round_b_candidates/ \
  --output round_b_bridge_results/

python superbrain/mainline/task1_mainline_validator.py \
  --input round_b_bridge_results/ \
  --output round_b_mainline_results/
```

### Phase 3: Comparative Analysis

```python
# Compare metrics
compare_rounds(
    round_a_results="round_a_mainline_results/",
    round_b_results="round_b_mainline_results/",
    output="inheritance_effectiveness_report.md"
)
```

---

## Pre-requisites for This Run

### ✅ Completed
- [x] Task-1 Simulator working
- [x] Bridge with Task-1 thresholds integrated
- [x] Mainline validator operational
- [x] Akashic Task-1 inheritance package schema defined

### ⏳ Required Before Run
- [ ] Ensure Akashic has ingested at least 5-10 Task-1 results
- [ ] Verify inheritance package file is writable/readable
- [ ] Implement `--inheritance-package` flag in Fast Genesis
- [ ] Create batch generation scripts

### 🔄 During Run
- [ ] Use fixed seeds for reproducibility
- [ ] Log all decisions with timestamps
- [ ] Track computational cost (wall time per candidate)

---

## Decision Criteria

### Inheritance DECLARED EFFECTIVE if:

1. **Bridge pass rate** improves by ≥5 percentage points
2. **Mainline approve rate** improves by ≥5 percentage points  
3. **Mean throughput Δ** shifts from ~0% to >+0.3%
4. **Variance reduction**: CV of throughput Δ lower in Round B

### Inheritance DECLARED INEFFECTIVE if:

1. No significant difference in pass/approve rates
2. Candidate distribution unchanged
3. Package fields ignored by generation

### INCONCLUSIVE if:

- Sample size too small (<20 candidates per round)
- High noise swamps signal
- Technical issues corrupt data

---

## Files to Produce

```
benchmark_results/task1_inheritance/
├── round_a/
│   ├── candidates_generated.json
│   ├── bridge_passed.json
│   ├── mainline_results.json
│   └── summary_stats.json
│
├── round_b/
│   ├── candidates_generated.json
│   ├── bridge_passed.json
│   ├── mainline_results.json
│   └── summary_stats.json
│
├── comparison_report.md
├── statistical_analysis.txt
└── inheritance_effectiveness_verdict.md
```

---

## Next Action

**BLOCKER**: Need to implement inheritance consumption in Fast Genesis.

Current gap: `generate_candidates.py` doesn't yet read `--inheritance-package`.

**ETA**: 1-2 hours to implement + test.

**Then**: Run full effectiveness experiment (2-3 hours wall time).

---

## Significance

This run determines whether Task-1 is:

- **One-shot**: Ran once, proved concept, archived
- **Self-improving**: Each cycle makes next cycle better

**Target**: Self-improving.

---

*Document Version*: 0.1.0  
*Status*: Ready for implementation pending Fast Genesis update