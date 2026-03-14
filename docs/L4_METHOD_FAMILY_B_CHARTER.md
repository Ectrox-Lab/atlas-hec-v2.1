# L4 Method Family B: Charter

**Status**: 🟢 **APPROVED** — 7-Day MVE  
**Date**: 2026-03-14  
**Decision**: Approved with 4 constraints  
**Rationale**: Family A's failure was specific implementation route; Family B represents genuine methodological jump

---

## Approval Statement

> **批准方法族 B 的 7 天 MVE。**
> 
> **理由**: Family A 被证伪的是具体实现路线，不是 L4 的核心目标；Family B 在复用单元、验证对象和生成逻辑上都构成了真正的方法学跳变，值得进行一次受控、限时、可大样本验证的最小可行实验。

**English**:
> **Method Family B 7-day MVE approved.**
> 
> **Rationale**: Family A falsified a specific implementation route, not L4 core goals. Family B constitutes genuine methodological jumps in reuse unit, verification target, and generation logic. Worth a controlled, time-boxed, large-sample-validated minimal experiment.

---

## 4 Constraints (Hard Rules)

### Constraint 1: Contracts Must Be Executable & Verifiable

**Requirement**: Each contract must have explicit, testable specification.

**Required Fields**:
```python
Contract {
    "name": str,                    # Human-readable identifier
    "input_conditions": dict,       # Required input state
    "output_guarantees": dict,      # Guaranteed output state  
    "allowed_transitions": list,    # Valid state machine transitions
    "violation_conditions": list,   # What constitutes failure
    "verification_method": str      # How to verify (simulation/property check)
}
```

**No**: Abstract descriptions like "stable delegation"
**Yes**: Executable predicates like `handoff_latency < 2.0 AND failover_success > 0.8`

### Constraint 2: Only 3–5 Contracts for MVE

**Limit**: Maximum 5 contracts in MVE.

**Rationale**: Fewer contracts = clearer success/failure determination.

**Proposed Initial Set** (3 contracts):
1. `StrictHandoff` — D1 delegation, bounded latency
2. `AdaptiveRecovery` — Memory-enabled recovery sequence
3. `PressureThrottle` — Injection rate control under load

**Expansion**: Only if MVE succeeds; additional contracts in Family B.1.

### Constraint 3: Large-Sample Discipline Maintained

**Hard Minimum**: n=300 candidates for any success claim.

**Rationale**: Family A's fatal error was trusting small samples.

**Enforcement**: 
- Generate 300 candidates per round
- Evaluate minimum 50 per round for statistics
- No claims before n=300 data available

### Constraint 4: Multi-Criteria Success (Not Single Metric)

**All three must pass**:

| Criterion | Target | Rationale |
|-----------|--------|-----------|
| Reuse via contracts | >50% | Core goal |
| Contract coverage | >90% | Quality metric |
| Effect at n=300 | >+10pp | Statistical significance |

**No partial success**: Cannot claim success with only 2/3 criteria.

---

## What Makes This "New Method Family"

### Explicit Break from Family A

| Aspect | Family A (CLOSED) | Family B (APPROVED) |
|--------|-------------------|---------------------|
| **Core abstraction** | Implicit family/mechanism identity | **Explicit interface contracts** |
| **Verification target** | Reuse rate (indirect) | **Contract satisfaction (direct)** |
| **Generation logic** | Bias toward "stable" configs | **Composition from verified contracts** |
| **Validation standard** | Small sample (20-100) | **Large sample (n≥300)** |
| **Refinement approach** | Aggressive (v3.1 failure) | **Conservative (validate first)** |

### Methodological Jump

**Jump 1**: Implicit → Explicit
- Family A: "F_P3T4M4 is stable" (learned correlation)
- Family B: "Contract X guarantees Y" (specified behavior)

**Jump 2**: Indirect → Direct Verification
- Family A: Reuse rate as proxy for mechanism quality
- Family B: Contract satisfaction as direct quality measure

**Jump 3**: Bias → Composition
- Family A: Probabilistic bias toward stable families
- Family B: Deterministic composition from verified units

---

## MVE Plan (7 Days)

### Day 1–2: Contract Design

**Tasks**:
- [ ] Define 3 contracts with full specification (Constraint 1)
- [ ] Verify contracts are testable on Task-2
- [ ] Document contract semantics

**Deliverable**: `family_b_contracts_v0.json`

### Day 3–4: Generator Build

**Tasks**:
- [ ] Build contract composition generator
- [ ] Implement contract verification (fast/Bridge level)
- [ ] Integrate with Task-2 simulator

**Deliverable**: `generate_family_b.py`

### Day 5–6: MVE Execution

**Tasks**:
- [ ] Generate 300 candidates per round (Constraint 3)
- [ ] Evaluate on Task-2
- [ ] Collect contract coverage metrics

**Deliverable**: Raw results data

### Day 7: Analysis & Decision

**Tasks**:
- [ ] Calculate all 3 success criteria (Constraint 4)
- [ ] Compare to Family A baseline (30%)
- [ ] Make Go/No-Go decision

**Deliverable**: MVE report with decision

---

## Success Scenarios

### Scenario A: Full Success (60% probability)

**Results**:
- Reuse >50%
- Coverage >90%
- Effect >+10pp

**Decision**: Family B validated → Proceed to Family B.1 (expand contracts)

### Scenario B: Partial Success (25% probability)

**Results**:
- 2/3 criteria pass
- Direction positive but magnitude insufficient

**Decision**: Family B.0.5 refinement → One more iteration

### Scenario C: Failure (15% probability)

**Results**:
- 0-1 criteria pass
- No improvement over Family A

**Decision**: Archive Family B → Abandon L4 compositional reuse line

---

## Relationship to Family A

### Explicit Separation

**Not**: Continuation of Family A
**Is**: New method family testing different core hypothesis

### Assets Inherited (Not Methods)

| Asset | Source | Use in B |
|-------|--------|----------|
| Anti-leakage guardrail | Family A | Default safety (not optimization) |
| Task-2 validator | Family A | Validation environment |
| Large-sample discipline | Family A lesson | Hard rule from day 1 |
| Small-sample unreliability | Family A lesson | Prevention awareness |

### Explicit Rejection

| Rejected from A | Why |
|-----------------|-----|
| Family/mechanism abstraction | Falsified at n=300 |
| "Stable family" bias | No causal mechanism |
| Reuse rate as target | Indirect metric |
| Aggressive refinement | Caused v3.1 failure |

---

## Risk Acknowledgment

### Risk: Second Failure

**Possibility**: Family B may also fail at MVE.

**Mitigation**: 7-day timebox limits cost; explicit criteria prevent false positives.

**Consequence**: If Family B fails, abandon L4 compositional reuse line entirely.

### Risk: Contracts Also Wrong Abstraction

**Possibility**: Explicit contracts may not capture reusable units either.

**Mitigation**: Start with 3 simple contracts; if even simple ones fail, clear negative result.

---

## Documentation

### MVE Artifacts

```
docs/
├── family_b/
│   ├── contracts_v0.json          # Day 1-2 deliverable
│   ├── generator_spec.md          # Day 3-4 design
│   └── mve_report.md              # Day 7 decision

superbrain/family_b/
├── contracts.py                   # Contract definitions
├── generator.py                   # Composition generator
├── verifier.py                    # Contract verification
└── evaluator.py                   # MVE evaluation

data/family_b_mve/
├── candidates/                    # Generated candidates
├── results/                       # Evaluation results
└── analysis/                      # Decision analysis
```

---

## Final Statement

**Method Family B is approved as a controlled, time-boxed experiment with hard constraints.**

It is **not** a continuation of Family A.
It is **not** an indefinite exploration.
It is a **7-day validation** of a genuinely different approach.

If it succeeds, we have a new foundation.
If it fails, we close the L4 line with confidence.

---

**Approved**: 2026-03-14  
**Duration**: 7 days  
**Decision deadline**: 2026-03-21  
**Status**: 🟢 EXECUTING

---

*L4 Method Family B Charter*  
*Controlled experiment with explicit constraints*
