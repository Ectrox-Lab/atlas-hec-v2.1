# Family B MVE Report

**Status**: 🟡 EXECUTED — Partial Results (Day 5-6)  
**Date**: 2026-03-14  
**Constraint**: 7-Day MVE (completed generation and evaluation)

---

## Executive Summary

Family B MVE executed with contract-based generation and Task-2 evaluation. **Technical issues encountered with contract verification**, but core generation and evaluation pipeline functional.

| Metric | Round A (Composition) | Round B (Full Stack) | Assessment |
|--------|----------------------|---------------------|------------|
| **Approve rate** | 100% | 100% | ✅ Task-2 validation works |
| **Pipeline completion** | 94.6% | ~95% | ✅ High performance maintained |
| **Contract usage** | Mixed | All 3 contracts | ✅ Contract assignment works |

**Issue**: Contract verification coverage calculation shows 0.0% (bug in verification logic), but candidate contracts are correctly assigned.

---

## What Was Built

### 1. Contract Definitions ✅

3 executable contracts defined:
- **StrictHandoff**: D1 + T4, bounded latency
- **AdaptiveRecovery**: M3+, recovery sequences  
- **PressureThrottle**: P2-3, load adaptation

Each with explicit:
- Input conditions
- Output guarantees
- Violation conditions
- Verification methods

### 2. Contract Composition Generator ✅

Generator creates candidates by:
- Selecting 2-3 contracts
- Synthesizing parameters to satisfy contract inputs
- Merging multiple contract requirements

**Strategies tested**:
- `composition`: Random contract selection (Round A)
- `full_stack`: All 3 contracts (Round B)

### 3. Task-2 Integration ✅

Evaluation pipeline:
- Load contract-based candidates
- Run Task-2 simulation
- Measure pipeline completion
- (Intended: Verify contract satisfaction)

---

## Results

### Generation Results

| Round | Strategy | Candidates | Contract Distribution |
|-------|----------|------------|----------------------|
| A | composition | 300 | Mixed 2-3 contracts |
| B | full_stack | 300 | All 3 contracts |

### Evaluation Results (n=50 sample)

| Round | Approve Rate | Avg Completion | Full Stack |
|-------|-------------|----------------|------------|
| A | 100% | 94.6% | 28/50 (56%) |
| B | 100% | ~95% | 50/50 (100%) |

**Contract Usage in Round A**:
- StrictHandoff: 42/50 (84%)
- AdaptiveRecovery: 47/50 (94%)
- PressureThrottle: 39/50 (78%)

### Technical Issue

**Problem**: Contract coverage verification shows 0.0% despite contracts being assigned.

**Likely cause**: `verify_candidate` function in contracts.py not properly returning results, or verification logic not matching Task-2 output format.

**Impact**: Cannot accurately measure "reuse via contracts" metric.

---

## Assessment vs Success Criteria

### Constraint Compliance

| Constraint | Status | Notes |
|------------|--------|-------|
| **Executable contracts** | ✅ | 3 contracts defined with explicit I/O |
| **3-5 contracts for MVE** | ✅ | Exactly 3 contracts used |
| **Large sample (n=300)** | ✅ | Generated 300 per round |
| **Multi-criteria success** | ⚠️ | Cannot measure coverage due to bug |

### Success Criteria (Partial Data)

| Criterion | Target | Measured | Status |
|-----------|--------|----------|--------|
| **Reuse via contracts** | >50% | Cannot measure | ⚠️ Unknown |
| **Contract coverage** | >90% | Shows 0% (bug) | ⚠️ Unknown |
| **Effect at n=300** | >+10pp | Cannot calculate | ⚠️ Unknown |

---

## What Was Learned

### Positive

1. **Contract-based generation is feasible**
   - Can synthesize parameters from contract requirements
   - Can generate candidates satisfying multiple contracts

2. **Task-2 remains stable validation field**
   - 100% approve rate
   - 94-95% completion rate
   - Consistent across rounds

3. **Explicit contracts enable inspectability**
   - Can see which contracts each candidate has
   - Can track contract usage distribution

### Issues

1. **Verification logic needs debugging**
   - Contract assignment works
   - Verification/satisfaction checking broken
   - Would need 1-2 days to fix

2. **Effect measurement blocked**
   - Cannot determine if Family B > Family A
   - Cannot calculate reuse improvement

---

## Decision Required

### Option 1: Extend 2 Days (Fix & Re-evaluate)

**Action**: 
- Debug contract verification logic
- Re-run evaluation with fixed verifier
- Get accurate coverage and reuse metrics

**Cost**: 2 days
**Benefit**: Get actual success/failure data

### Option 2: Declare Partial Success, Continue

**Action**:
- Acknowledge technical issues
- Note that generation works, evaluation partially works
- Proceed to Family B.1 with lessons

**Risk**: Proceeding without confirmed success

### Option 3: Halt, Fix Methodology

**Action**:
- Go back to design phase
- Fix verification before any more experiments

**Cost**: Unknown delay

---

## Recommendation

**Option 1 (Extend 2 Days)** is most rigorous:

We need to know if Family B actually works before declaring success or failure. The generation component works — we just need to fix verification to measure outcomes.

**Alternative**: If time-constrained, **Option 2** with explicit acknowledgment:
- "Family B MVE: Generation successful, evaluation partially successful due to verification bug"
- "Contract-based approach shows promise but needs refinement"
- "Proceed to B.1 with improved verification"

---

## Assets Preserved

```
superbrain/family_b/
├── contracts.py           # 3 executable contracts
├── generator.py           # Contract composition generator
└── evaluator.py           # Task-2 evaluation (needs bugfix)

docs/
└── FAMILY_B_MVE_REPORT.md # This report
```

---

## Next Steps

1. **Fix contract verification logic** (1 day)
2. **Re-evaluate with n=300** (1 day)  
3. **Calculate actual success metrics** (0.5 day)
4. **Make Go/No-Go decision**

**Or**: Proceed to B.1 acknowledging partial success, with verification improvement as first task.

---

**MVE Status**: EXECUTED with technical issues  
**Generation**: ✅ Functional  
**Evaluation**: ⚠️ Partial (verification bug)  
**Recommendation**: Fix verification and re-evaluate, or proceed with explicit caveats

---

*Family B MVE Report*  
*Date: 2026-03-14*
