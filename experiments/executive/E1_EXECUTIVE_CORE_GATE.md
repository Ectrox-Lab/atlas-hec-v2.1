# E1 — Executive Core Gate

**Gate**: E1  
**Line**: E — Executive Core  
**Status**: ⏳ READY TO START  
**Priority**: P0  
**Owner**: Research Team  
**Target Start**: Day 1-3 of campaign

---

## Gate Question

> Can the executive govern without doing all the work?

---

## Sub-Experiments

| ID | Name | Duration | Resource | Status |
|----|------|----------|----------|--------|
| E1.1 | Delegation Completeness | 24h | 4 cores / 16GB | ⏳ Ready |
| E1.2 | Tool Selection Quality | 12h | 4 cores / 16GB | ⏳ Ready |
| E1.3 | Escalation Quality | 8h | 2 cores / 8GB | ⏳ Ready |
| E1.4 | False Acceptance / Rollback | 16h | 4 cores / 16GB | ⏳ Ready |
| E1.5 | Anti-Hijack Robustness | 24h | 6 cores / 24GB | ⏳ Ready |

---

## Pass Criteria

| Test | Metric | Threshold | Weight |
|------|--------|-----------|--------|
| E1.1 | Delegation Ratio | ≥ 80% | 20% |
| E1.2 | Tool Selection Accuracy | ≥ 90% | 20% |
| E1.3 | Escalation Recall | ≥ 95% | 20% |
| E1.4 | Defect Acceptance Rate | ≤ 10% | 20% |
| E1.5 | Hijack Detection Rate | ≥ 95% | 20% |

**Overall Pass**: Weighted average ≥ 90% with no individual test < 80%

---

## Prerequisites

- [ ] Executive model candidate selected (20B default)
- [ ] Specialist mesh available
- [ ] Tool registry populated
- [ ] Audit pipeline operational
- [ ] Logging infrastructure ready

---

## Entry Criteria

- Infrastructure provisioned
- Test scenarios prepared
- Baseline measurements taken
- Team briefed

---

## Exit Criteria

- All 5 sub-experiments complete
- Metrics calculated with 95% confidence
- Report written
- Pass/fail determination

---

## On Failure

If E1 fails:
1. Analyze which capabilities failed
2. Determine if fixable with prompt engineering
3. If not, escalate to model reselection
4. Option B (20B+120B) becomes fallback

---

**Started**: _______________  
**Completed**: _______________  
**Result**: ⏳ / ✅ / ❌
