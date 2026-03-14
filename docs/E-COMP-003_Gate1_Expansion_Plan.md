# E-COMP-003 Gate-1: Large Sample Validation Plan

**Status**: 🟢 APPROVED — Expand to n=100+  
**Date**: 2026-03-14  
**Decision**: Option A (Continue E-COMP-003, stabilize mechanism map)

---

## Decision Rationale

Current mechanism map based on n=4 winners:
- **T4M4 foundation**: 100% of winners ✓
- **F_P3T4M4 as mechanism bundle**: High mechanism_score (0.92) but n=1 ⚠️
- **P2 vs P3 tuning**: 3 vs 1 winners — medium confidence ⚠️

**Risk**: Small sample may conflate "current success bundle" with "universal core bundle"

**Solution**: Expand to n=100+ with structured validation before routing to L4-v3 or Task-2.

---

## Gate-1: Four Validation Targets

### Target 1: T4M4 Stability Foundation

**Question**: Is T4M4 truly a stable foundation, or just a local optimum?

**Validation Criteria**:
- [ ] T4M4 appears in ≥80% of winners
- [ ] Pass-rate for T4M4 candidates significantly higher than non-T4M4
- [ ] Seed variance low (stable across multiple seeds)
- [ ] Stress coverage: T4M4 holds under different load conditions

**Acceptance Threshold**: 
- T4M4 share ≥80% AND
- T4M4 pass-rate ≥2× non-T4M4

### Target 2: F_P3T4M4 as Mechanism Bundle

**Question**: Is F_P3T4M4 advantage from stable mechanisms or accidental configuration?

**Validation Criteria**:
- [ ] F_P3T4M4 mechanism_score consistently high (≥0.8) across samples
- [ ] Mechanism fingerprint stable across seeds
- [ ] Same mechanisms appear in other high-performing families
- [ ] Can predict F_P3T4M4 performance from mechanism composition

**Acceptance Threshold**:
- Mechanism_score ≥0.8 in ≥70% of F_P3T4M4 candidates AND
- Mechanism fingerprint correlation with performance ≥0.7

### Target 3: P2 vs P3 as Risk-Preference Tuning

**Question**: Is P2/P3 truly a tunable parameter, or is one universally better?

**Validation Criteria**:
- [ ] Both P2 and P3 produce winners in significant numbers
- [ ] P2 winners: higher consistency, lower variance
- [ ] P3 winners: higher peak performance, higher variance
- [ ] Clear risk/reward trade-off pattern

**Acceptance Threshold**:
- Both P2 and P3 have ≥15% win-rate AND
- Statistically significant difference in variance (P3 > P2)

### Target 4: Pattern Table Predictive Power

**Question**: Can stable vs leakage patterns predict Mainline success?

**Validation Criteria**:
- [ ] Stable families (per pattern table) have higher approve rates
- [ ] Leakage families have lower approve rates
- [ ] Pseudo-reuse detection correctly identifies false positives
- [ ] Mechanism_score correlates with approval

**Acceptance Threshold**:
- Stable family approve rate ≥3× leakage family AND
- Mechanism_score correlation with approval ≥0.6

---

## Execution Plan

### Phase 1: Generate Candidates (n=150 per round)

**Round A-v3**: Pure exploration (baseline)
- Count: 150
- Seed: 2000
- Config: No inheritance, uniform exploration

**Round B-v3**: Mechanism bias (current best)
- Count: 150
- Seed: 2000
- Config: Use current family_mechanism_map_v1 + route_constraints_v1

**Ablation-v3**: Control purity
- Count: 150
- Seed: 2000
- Config: Load package but bias_strength=0, anti_leakage=0

### Phase 2: Stratified Sampling (n=30 per round for Mainline)

Stratify by:
- Family distribution
- Mechanism_score buckets
- Anti-leakage penalty levels

### Phase 3: Mainline Evaluation

Evaluate 30 candidates per round with:
- Task-1 simulator (500 tasks)
- Multiple seeds (3 seeds per candidate)
- Detailed logging (delegation, recovery, trust trajectory)

### Phase 4: Mechanism Extraction

Run `mechanism_extractor.py` on all winners to:
- Update family_mechanism_map to v2
- Refine route_constraints
- Validate pattern table predictions

---

## Success Gates

### Gate-1A: Mechanism Map Stabilization

**Criteria**:
- All 4 validation targets meet thresholds
- family_mechanism_map_v2 shows consistent patterns with v1
- route_constraints_v2 confirms v1 constraints

**Outcome**: ✅ STABLE → Proceed to C (Route to L4-v3)

### Gate-1B: Mechanism Map Revision

**Criteria**:
- ≥2 validation targets fail
- New patterns emerge contradicting v1
- T4M4 foundation questioned

**Outcome**: ⚠️ REVISE → Continue E-COMP-003, update map

### Gate-1C: Mechanism Map Validated, Test Generalization

**Criteria**:
- All 4 validation targets meet thresholds
- Mechanism map stable and predictive
- Ready to test on new task

**Outcome**: 🔄 GENERALIZE → Proceed to B (Task-2 validation)

---

## Execution Script

```bash
# Generate candidates
cd /home/admin/atlas-hec-v2.1-repo
./run_ecomp003_gate1.sh

# Evaluate
./run_ecomp003_gate1_eval.sh

# Extract and validate
python3 superbrain/module_routing/mechanism_extractor.py \
    --l4v2-results /tmp/ecomp003_gate1_results \
    --output-dir docs/research/E-COMP-003/gate1

# Decision
python3 superbrain/module_routing/gate1_validator.py \
    --results /tmp/ecomp003_gate1_results \
    --criteria docs/E-COMP-003_Gate1_Expansion_Plan.md
```

---

## Resources Needed

| Resource | Amount | Notes |
|----------|--------|-------|
| Candidates generated | 450 | 150 × 3 rounds |
| Mainline evaluations | 90 | 30 × 3 rounds |
| Compute time | ~2 hours | Parallel evaluation on available GPUs |
| Storage | ~100 MB | Candidate configs + logs |

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Candidate generation | 30 min | 450 candidates |
| Stratified sampling | 15 min | 90 selected candidates |
| Mainline evaluation | 90 min | Detailed results with logs |
| Mechanism extraction | 30 min | family_mechanism_map_v2 |
| Gate validation | 15 min | Go/No-Go decision |
| **Total** | **~3 hours** | **Gate-1 decision** |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Evaluation takes too long | Use parallel evaluation, reduce tasks to 300 per run |
| Results inconsistent with v1 | Document divergence, analyze root cause |
| Still insufficient winners | Relax approval threshold slightly for pattern analysis |

---

## Expected Outcomes

### Best Case (70% confidence)
- All 4 targets validated
- Mechanism map stable
- Proceed to L4-v3 with confidence

### Medium Case (25% confidence)
- 2-3 targets validated
- Some map revisions needed
- One more iteration of E-COMP-003

### Worst Case (5% confidence)
- Major contradictions with v1
- T4M4 foundation not stable
- Back to mechanism hypothesis drawing board

---

## Documentation

All results will be archived in:
```
docs/research/E-COMP-003/gate1/
├── candidates/               # Generated candidates
├── results/                  # Evaluation results
├── family_mechanism_map_v2.json
├── route_constraints_v2.json
├── gate1_validation_report.md
└── decision_record.md        # Go/No-Go decision
```

---

**Approved**: Continue E-COMP-003 with large sample validation  
**Next Check**: After Gate-1 completion (expected 2026-03-14 + 3 hours)
