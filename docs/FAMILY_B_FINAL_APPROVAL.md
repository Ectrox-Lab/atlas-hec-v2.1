# Family B Final Approval & Current Status

**Approval Date**: 2026-03-14  
**Approver**: Research Lead  
**Status**: ✅ APPROVED — Executing with explicit constraints

---

## Formal Approval Statement

> **批准方法族 B 的 7 天 MVE。**
> 
> **理由**: Family A 被证伪的是具体实现路线，不是 L4 核心目标；Family B 在复用单元、验证对象和生成逻辑上都构成了真正的方法学跳变，值得做一次受控、限时、可大样本验证的最小可行实验。

**English**:
> **Method Family B 7-day MVE approved.**
> 
> **Rationale**: Family A falsified a specific implementation route, not L4 core goals. Family B constitutes genuine methodological jumps in reuse unit, verification target, and generation logic. Worth a controlled, time-boxed, large-sample-validated minimal experiment.

---

## 4 Hard Constraints (Approved)

### Constraint 1: Contracts Must Be Executable & Verifiable ✅

**Status**: Implemented
- 3 contracts defined with explicit I/O
- Verification methods specified
- Bug encountered in verification logic (fix in progress)

### Constraint 2: Only 3–5 Contracts for MVE ✅

**Status**: Implemented
- Exactly 3 contracts: StrictHandoff, AdaptiveRecovery, PressureThrottle
- No expansion until MVE succeeds

### Constraint 3: Large-Sample Discipline Maintained ✅

**Status**: Implemented
- Generated 300 candidates/round (n=900 total)
- Sample size requirement enforced

### Constraint 4: Multi-Criteria Success (All 3) ⏳

**Status**: Pending verification fix
- Reuse >50%
- Contract coverage >90%
- Effect at n=300 >+10pp

---

## Current Execution Status

### Completed (Days 1-6)

| Component | Status | Notes |
|-----------|--------|-------|
| Contract design (3 contracts) | ✅ Complete | StrictHandoff, AdaptiveRecovery, PressureThrottle |
| Generator build | ✅ Complete | Contract composition working |
| Generation (n=300/round) | ✅ Complete | 900 candidates total |
| Task-2 integration | ✅ Complete | 100% approve rate confirmed |
| Verification logic | ⚠️ Bug found | Shows 0% coverage, needs fix |

### Pending (Day 7 + Extension)

| Task | Duration | Purpose |
|------|----------|---------|
| Fix verification bug | 1 day | Get accurate contract coverage metrics |
| Re-evaluate n=300 | 1 day | Calculate actual success criteria |
| Final decision | 0.5 day | Go/No-Go based on real data |

---

## Technical Issue Summary

### Problem
Contract verification logic returns 0% coverage despite contracts being correctly assigned to candidates.

### Root Cause
Verification function not properly matching Task-2 simulation output format with contract guarantees.

### Impact
Cannot calculate:
- Actual contract coverage
- Reuse via contracts metric
- Comparison to Family A baseline

### Solution Path
1. Debug verify_candidate() function
2. Align contract guarantees with Task-2 output keys
3. Re-run evaluation on generated candidates

---

## Next Actions (Approved)

### Immediate (Next 2 Days)

1. **Fix verification logic** (Day 7)
   - Debug contracts.py verify_candidate()
   - Fix Task-2 output mapping
   - Validate on small sample

2. **Re-evaluate with n=300** (Day 8)
   - Run fixed verification on all 900 candidates
   - Calculate accurate coverage and reuse metrics
   - Compare Round A vs Round B effect

3. **Decision** (Day 8.5)
   - Assess all 3 success criteria
   - Make Go/No-Go/Extend decision

---

## Success Criteria (Reminders)

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Reuse via contracts | >50% | Candidates with >90% contract coverage |
| Contract coverage | >90% | Avg coverage across all candidates |
| Effect at n=300 | >+10pp | Round B - Round A reuse difference |

**All three must pass for MVE success.**

---

## Risk Acknowledgment

### Risk: Verification Fix Fails
**Mitigation**: If verification cannot be fixed in 2 days, declare "partial success with methodology caveat" and proceed to B.1 with verification as first priority.

### Risk: Metrics Show No Improvement
**Acceptance**: If Family B shows no improvement over Family A after fix, accept failure and archive Family B, closing L4 compositional reuse line.

---

## Resource Commitment

**Approved**: 2 additional days to complete MVE properly  
**Deadline**: 2026-03-16 (MVE completion)  
**Decision**: 2026-03-16.5 (Go/No-Go)

---

## Methodological Integrity

**This is NOT continuing Family A.**

Family B represents:
- New abstraction (contracts vs families)
- New verification (direct vs indirect)
- New generation (composition vs bias)

**Success or failure of Family B is independent of Family A.**

---

**Status**: APPROVED — Executing with constraints  
**Next Milestone**: Verification fix + accurate metrics (48 hours)  
**Final Decision**: Based on real data, not speculation

---

*Family B Final Approval*  
*Approved: 2026-03-14*  
*Executing: With explicit constraints and 2-day extension*
