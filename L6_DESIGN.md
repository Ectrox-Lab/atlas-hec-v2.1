# L6 Design: Learning to Select Sources

> **Status**: Design Phase  
> **Core Question**: Can the system learn a reusable transfer policy?  
> **Upgrade**: From task-level inheritance to strategy-level learning  

---

## L6 Core Proposition

**From L5**: The system can inherit across tasks (existence proof)  
**To L6**: The system can learn *how* to inherit better (capability learning)

> "The system can learn a reusable transfer policy that improves future cross-task inheritance beyond fixed heuristics."

---

## L6 Experimental Design

### Three Policies Compared

#### Policy 1: Random Baseline
```yaml
name: RANDOM_SOURCE
selection: Uniform random from {Code, Math, Planning}
purpose: Absolute baseline
expected_performance: Lowest mean TG, highest variance
```

#### Policy 2: Hand-Coded Heuristic
```yaml
name: CODE_FIRST_HEURISTIC
selection: 
  priority: [Code, Math, Planning]
  rule: Always use highest available source
purpose: Strong human-engineered baseline
expected_performance: Good mean TG, low variance
justification: L5 showed Code > Math > Planning
```

#### Policy 3: Learned Selection Policy
```yaml
name: LEARNED_POLICY
input_features:
  - target_task_type: {Math, Code, Planning}
  - historical_pair_data:
      - mean_tg_for_pair
      - success_rate
      - ci_lower_bound
  - source_stability: CV across windows
  - trajectory_quality: checksum_diversity
  
model: Lightweight predictor (linear / small MLP)
  
output: 
  - source_ranking: [best, second, third]
  - confidence: probability_best
  
learning_signal:
  - reward: achieved_transfer_gap
  - update: After each batch, update policy
  
purpose: Learn from L5 history to optimize future selections
expected_performance: Match or exceed Code-First heuristic
```

---

## L6 Success Criteria

### Primary Metrics

| Metric | Random | Code-First | Learned | Success Condition |
|:-------|:------:|:----------:|:-------:|:-----------------|
| Mean TG | ~6-7pp | ~10pp | **Target: >10pp** | Learned ≥ Code-First |
| Positive Rate | ~60% | ~85% | **Target: >85%** | Learned ≥ Code-First |
| CI Lower Bound | ~3pp | ~7pp | **Target: >7pp** | Learned ≥ Code-First |
| Worst-Case Floor | ~2pp | ~5pp | **Target: >5pp** | Robustness maintained |

### Secondary Metrics

```yaml
regret_vs_oracle:
  definition: TG_achieved - TG_best_possible_source
  target: Regret < 1pp on average
  
selection_accuracy:
  definition: % of times learned picks best source
  target: >80% accuracy
  
uplift_over_heuristic:
  definition: (Learned_mean - CodeFirst_mean) / CodeFirst_mean
  target: >5% improvement
```

---

## L6 Minimum Viable Experiment

### Phase 1: Policy Learning Setup

```bash
# 1. Train predictor on L5 historical data
python3 train_source_selector.py \
  --historical_data L5_EVIDENCE_PACKAGE/ \
  --features target_type,historical_tg,source_cv \
  --model linear_or_small_mlp \
  --output learned_policy_v1.pkl

# 2. Evaluate on held-out scenarios
# (e.g., predict for new target not in training)
```

### Phase 2: Policy Execution

```bash
# Execute 3 parallel experiment tracks

# Track 1: Random
python3 l6_experiment.py --policy RANDOM --n_targets 10

# Track 2: Code-First
python3 l6_experiment.py --policy CODE_FIRST --n_targets 10

# Track 3: Learned
python3 l6_experiment.py --policy LEARNED \
  --policy_model learned_policy_v1.pkl \
  --n_targets 10
```

### Phase 3: Comparison

```bash
python3 compare_policies.py \
  --random_results track1/ \
  --heuristic_results track2/ \
  --learned_results track3/
```

---

## Key Design Decisions

### Why Not Just "More Tasks"?

L5 already showed broad viability (6/6 pairs).  
Adding more tasks would test **external validity**, not **capability**.

L6 tests capability: can system learn from experience?

### Why Source Selection?

- Natural extension of L5 directionality discovery
- Clear optimization target
- Measurable improvement over fixed heuristic
- Gates to future: learned routing, adaptive curricula

### What If Learned Policy Fails?

**Scenario A**: Learned = Code-First (no improvement)
- Conclusion: Heuristic is near-optimal for current task family
- L6 still valuable: establishes baseline for future work

**Scenario B**: Learned < Code-First (negative transfer)
- Conclusion: Policy learning requires more data or better features
- Investigate: feature engineering, larger historical window

**Scenario C**: Learned > Code-First (success)
- Conclusion: System can learn to inherit better
- Opens: meta-learning, adaptive systems, continual improvement

---

## L6 Architecture Sketch

```
┌─────────────────────────────────────────┐
│           L6: Learned Selector          │
├─────────────────────────────────────────┤
│                                         │
│  Historical Data (L5)                   │
│     ↓                                   │
│  Feature Extractor                      │
│     - pair_history                      │
│     - source_stability                  │
│     - target_characteristics            │
│     ↓                                   │
│  Policy Model (Lightweight)             │
│     ↓                                   │
│  Source Ranking + Confidence            │
│     ↓                                   │
│  Execute Transfer                       │
│     ↓                                   │
│  Reward Signal (achieved TG)            │
│     ↓                                   │
│  Policy Update (optional)               │
│                                         │
└─────────────────────────────────────────┘
```

---

## Timeline Estimate

| Phase | Duration | Output |
|:------|:--------:|:-------|
| Policy Design | 1-2h | Feature set, model architecture |
| Training on L5 | 1h | Learned policy v1 |
| Execution (3 tracks) | 2-3h | Random, Heuristic, Learned results |
| Analysis | 1h | Comparison report |
| **Total** | **5-7h** | L6 validation complete |

---

## Risk Mitigation

| Risk | Mitigation |
|:-----|:-----------|
| Insufficient training data | Use all L5 data; consider data augmentation via window-level samples |
| Overfitting to 3 tasks | Explicitly test generalization to held-out task combinations |
| Feature engineering failure | Start with simple features (historical mean, source CV); iterate |
| No improvement over heuristic | Report null result; heuristic establishes strong baseline |

---

## Relation to L5

```
L5: "Can we inherit?" → YES (existence)
     "Which sources are better?" → Hierarchy discovered

L6: "Can we learn to pick better sources?" → TESTING
     "Can we improve beyond fixed rules?" → GOAL
```

**L5 is the foundation. L6 is the ascent.**

---

## Next Immediate Action

```bash
# 1. Extract features from L5 data
python3 extract_l5_features.py --input L5_EVIDENCE_PACKAGE/ --output l5_features.csv

# 2. Design policy model
vim L6_policy_model.py

# 3. Train initial version
python3 train_source_selector.py --features l5_features.csv
```

---

*L6 Design v1.0 - From Existence to Capability*
