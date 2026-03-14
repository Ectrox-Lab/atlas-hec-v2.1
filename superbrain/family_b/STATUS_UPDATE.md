# Family B: Status Update (Post Step-2)

**Date:** 2026-03-14

---

## Decision: Mixed Contracts = Mainline

| Configuration | Status | Evidence |
|---------------|--------|----------|
| **Round A (Mixed)** | ✅ **MAINLINE** | Coverage 91%, Reuse 87%, stable at n=100 |
| **Round B (Full-stack)** | ⚠️ **DIAGNOSTIC** | Coverage 79% at n=100, below 85% threshold |

### Why Mixed = Mainline
- Stable across n=30 → n=100 (Coverage 93% → 91%, Reuse 90% → 87%)
- All thresholds met at n=100
- Effect +87pp >> +50pp requirement

### Why Full-stack = Diagnostic Only
- Coverage dropped to 79% at n=100 (below 85% threshold)
- 3-contract combination more fragile than expected
- Not blocked, but not default

---

## New Baseline (Step 2.5)

**Family B Mainline = Mixed Contracts**
- StrictHandoff + AdaptiveRecovery (2 contracts)
- Or StrictHandoff + PressureThrottle (2 contracts)
- Or AdaptiveRecovery + PressureThrottle (2 contracts)

**NOT Full-stack (3 contracts) as default**

---

## Next: Cross-Task Probe (Step 3)

**Goal:** Verify Mixed contracts work on Task-3

**Success:** Reuse > 40%, Effect > +20pp on Task-3

**Time:** 1 hour
