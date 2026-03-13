# Executive Model Candidate Plan

**Version**: 1.0  
**Date**: 2026-03-12  
**Scope**: 20B vs 120B Role Redefinition

---

## Core Shift in Evaluation

**Old Approach**: "Which model writes better code?"  
**New Approach**: "Which model is better suited for which governance role?"

Code writing capability is necessary but not sufficient for executive function. The question is not "who is smarter" but "who is more suitable for what role."

---

## Role Definitions

| Role | Function | Key Requirements |
|------|----------|------------------|
| **Executive** | Governance, delegation, audit | Judgment, consistency, boundedness |
| **Deep Reviewer** | Analysis, verification, critique | Depth, thoroughness, precision |
| **Coding Executor** | Implementation, tooling | Speed, correctness, domain knowledge |
| **Auditor/Verifier** | Independent validation | Objectivity, coverage, rigor |

---

## Three Architecture Options

### Option A: 120B Single Primary Brain

```
[120B]
   │
   ├── Executive
   ├── Deep Review
   ├── Coding
   └── Audit
```

**Advantages**:
- Unified context, no communication overhead
- Single source of truth for goals
- Potentially deeper reasoning
- Simpler deployment

**Disadvantages**:
- No separation of powers (executive also auditor)
- Single point of failure
- Expensive for all tasks
- Risk of overconfidence in its own outputs
- No inherent verification layer

**Cost Profile**:
- Inference: High per token
- Context: Full 120B for all operations
- Scaling: Expensive

**Concurrency**: Sequential (one brain, one thread)

**Risk Assessment**:
| Risk | Level | Mitigation |
|------|-------|------------|
| Self-audit failure | HIGH | External verifier mandatory |
| Goal drift | MEDIUM | Constitutional constraints |
| Tool hijack | MEDIUM | Sandboxing |
| Cost overrun | HIGH | Usage caps |

---

### Option B: 20B Resident Executive + 120B Deep Review

```
[20B Executive] ←────→ [120B Deep Reviewer]
      │
      ├── Delegation
      ├── Audit (light)
      └── Governance
```

**Advantages**:
- Separation of executive and deep analysis
- 20B cheaper for routine governance
- 120B reserved for complex analysis
- Some check-and-balance
- Cost optimization

**Disadvantages**:
- Communication overhead between models
- Context fragmentation
- 120B still not independent auditor (called by executive)
- Potential for 20B to withhold from 120B
- Escalation logic complexity

**Cost Profile**:
- 80% of operations: 20B (cheap)
- 20% of operations: 120B (expensive but selective)
- Average: Moderate

**Concurrency**: 20B can delegate while 120B reviews

**Upgrade Triggers**:
- 20B judgment quality < threshold
- Escalation rate > 30%
- Deep review backlog > 1 hour

**Downgrade Triggers**:
- 120B latency unacceptable
- Cost budget exceeded
- 20B sufficient for current load

---

### Option C: 20B Executive + CLI/Specialist Mesh + Verifier Layer

```
[20B Executive]
      │
      ├──→ [CLI Coder] ──────┐
      ├──→ [Specialist A] ───┤→ [Verifier Layer]
      ├──→ [Specialist B] ───┤   (independent)
      └──→ [Search Tools] ───┘
```

**Advantages**:
- True separation of powers
- Executive does not code
- Specialist cannot self-verify
- Verifier independent of executor
- Most cost-effective
- Highest parallelism
- Most robust to single failure

**Disadvantages**:
- Complexity in orchestration
- More moving parts
- Debugging distributed failures harder
- Communication overhead
- Requires robust CLI/verifier infrastructure

**Cost Profile**:
- Executive: 20B (constant, low)
- Execution: Variable (specialist-specific)
- Verification: Additional cost (but catches errors)
- Average: Lowest for equivalent capability

**Most Critical Risk to Prove**:
| Risk | Hypothesis | Test |
|------|------------|------|
| Executive too weak to govern | 20B insufficient for complex delegation | E1 delegation test |
| Verifier capture | Verifier not truly independent | G1 hijack test |
| Orchestration overhead | Communication > computation | G1 overhead test |
| Specialist quality variance | Inconsistent execution | E1.4 acceptance test |

---

## Comparative Analysis

| Dimension | Option A (120B) | Option B (20B+120B) | Option C (20B+Mesh) |
|-----------|-----------------|---------------------|---------------------|
| **Executive Quality** | High | Medium | Unknown (test needed) |
| **Deep Analysis** | High | High | Via specialist |
| **Coding Speed** | Medium | Fast (20B delegates) | Fastest (parallel) |
| **Audit Independence** | None | Weak | Strong |
| **Cost Efficiency** | Poor | Moderate | Good |
| **Robustness** | Low | Medium | High |
| **Complexity** | Low | Medium | High |
| **Scalability** | Poor | Moderate | Good |

---

## Recommendation Framework

### Decision Matrix

```
IF (budget constrained AND complexity manageable):
    RECOMMEND Option C
    REQUIRED TESTS: E1 delegation, G1 hijack, G1 overhead
    
ELSE IF (need deep analysis frequently AND cost moderate):
    RECOMMEND Option B
    REQUIRED TESTS: Escalation quality, context preservation
    
ELSE IF (simplicity paramount AND budget unlimited):
    RECOMMEND Option A
    REQUIRED: External verifier mandatory
    
ELSE:
    RUN COMPARATIVE EXPERIMENTS
    DECIDE BASED ON EVIDENCE
```

---

## Specific Role Assignments (Proposed)

### GPT-OSS-20B

**Best Suited For**:
| Role | Rationale |
|------|-----------|
| **Resident Executive** | Fast, cheap, sufficient for governance; delegates complexity |
| **Light Audit** | Routine verification, pattern matching |
| **Task Decomposition** | Breaking problems into delegable chunks |
| **Escalation Filtering** | Deciding what needs deeper review |

**Not Suited For**:
- Deep architectural analysis (depth limited)
- Complex verification (may miss subtle bugs)
- High-stakes final audit (independence concern)

---

### GPT-OSS-120B

**Best Suited For**:
| Role | Rationale |
|------|-----------|
| **Deep Reviewer** | Thorough analysis, edge case identification |
| **Complex Auditor** | Subtle bug detection, security review |
| **Architecture Design** | System-level thinking |
| **Final Authority** | High-stakes decisions (if no other option) |

**Not Suited For**:
- Routine governance (overkill, expensive)
- Real-time operations (latency)
- Self-audit of own outputs (conflict of interest)
- Exclusive executive (concentration of power)

---

### CLI / Specialist

**Best Suited For**:
| Role | Rationale |
|------|-----------|
| **Coding Executor** | Fast, deterministic, verifiable |
| **Domain Specialist** | Deep expertise in specific areas |
| **Tool Operations** | CLI, search, API calls |
| **Parallel Execution** | Multiple tasks simultaneously |

**Critical Requirement**:
- Cannot self-validate
- Cannot modify goals
- Cannot escalate own authority
- All outputs require audit

---

### Verifier / Auditor (Independent)

**Best Suited For**:
| Role | Rationale |
|------|-----------|
| **Output Validation** | Independent of creator |
| **Security Review** | Fresh perspective |
| **Regression Testing** | Automated verification |
| **Final Sign-off** | Before production deployment |

**Critical Requirement**:
- Must be independent of executor
- Cannot be same model as executive
- Must have veto power
- Must be conservative (false negatives costly)

---

## Experimental Plan

### Phase 1: Capability Baseline

Test all three options on:
- 50 governance decisions
- 50 code generation tasks
- 50 verification tasks
- 10 complex architectural reviews

Measure: accuracy, latency, cost, confidence calibration

### Phase 2: Stress Tests

- High load: 100 tasks/hour
- Adversarial: manipulation attempts
- Failure injection: component failures
- Long-horizon: 24-hour continuous operation

Measure: robustness, recovery, drift

### Phase 3: Integration

- Option C with various verifier designs
- Option B with different escalation thresholds
- Option A with external verifier

Measure: end-to-end quality, cost, complexity

---

## Expected Outcomes

### Likely Winner: Option C

**Rationale**:
- Best cost/quality tradeoff
- True separation of powers
- Most scalable
- Aligns with "governance over execution" philosophy

**Contingency**:
If 20B executive fails E1 delegation test → Fallback to Option B

### Option B as Fallback

If Option C proves too complex or 20B too weak for executive function.

### Option A for Special Cases

Only for high-stakes, low-frequency decisions where simplicity trumps cost.

---

## Conclusion Form

Not: "120B is better than 20B"

But:

| Model | Best Role | Secondary Role | Avoid |
|-------|-----------|----------------|-------|
| **20B** | Executive, light audit | Delegation filtering | Deep analysis, final authority |
| **120B** | Deep reviewer, complex auditor | Architecture design | Exclusive executive, self-audit |
| **CLI** | Coding executor | Tool operations | Self-validation, goal modification |
| **Verifier** | Independent validation | Security review | Same-model audit, capture |

---

**Next Step**: Run comparative experiments starting with E1 delegation test for 20B executive candidate.

**Research Lead**: _______________  
**Technical Lead**: _______________  
**Start Date**: _______________
