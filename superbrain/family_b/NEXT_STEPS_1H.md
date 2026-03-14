# Family B: Next Steps (1-Hour Format)

---

## Step 1: Baseline Freeze (1 Hour)

### 1-Hour Goal
固化当前通过的 contract schema + evaluator 口径，产出一份可复现的 freeze snapshot。

### 1-Hour Output
| Item | Status |
|------|--------|
| Contract schema frozen | ✅ |
| Evaluator logic archived | ✅ |
| Reproducibility snapshot | ✅ |
| **GO/NO-GO** | GO → Proceed to Step 2 |

### Append Condition
- Snapshot 可复现
- Key metrics 与 MVE 一致

---

## Step 2: Scale Signal Check (1 Hour)

### 1-Hour Goal
扩一批样本（n=100-200），验证 effect / reuse 是否保持，排除小样本运气。

### 1-Hour Output
| Metric | n=30 (MVE) | n=100 (Quick) | Delta | Status |
|--------|------------|---------------|-------|--------|
| Coverage | 93% | ? | ±5% acceptable | ? |
| Reuse | 90% | ? | ±10% acceptable | ? |
| Effect | +90pp | ? | Still >+50pp | ? |
| **GO/NO-GO** | ? | ? | ? | **TBD** |

### Append Condition (Only if ALL met)
- Coverage >= 85%
- Reuse >= 70%
- Effect >= +50pp
- Variance < 15%

If NO → Stop, report "scale instability"

---

## Step 3: Cross-Task Signal Probe (1 Hour)

### 1-Hour Goal
探测 Task-3 是否有可读信号，验证 contract 是否可迁移。

### 1-Hour Output
| Task | Contract Applied | Reuse | Effect vs Random | **GO/NO-GO** |
|------|------------------|-------|------------------|--------------|
| Task-2 (baseline) | StrictHandoff | 90% | +90pp | ✅ baseline |
| Task-3 (probe) | StrictHandoff | ?% | ?pp | **TBD** |

### Append Condition (Only if ALL met)
- Task-3 reuse > 40%
- Task-3 effect > +20pp
- No tool error

If NO → Stop, report "cross-task transfer failed"

---

## Summary Table

| Step | Time | Output | Decision Gate |
|------|------|--------|---------------|
| 1. Baseline Freeze | 1h | Snapshot | GO → Step 2 |
| 2. Scale Signal | 1h | n=100 metrics | GO (if stable) → Step 3 |
| 3. Cross-Task Probe | 1h | Task-3 signal | GO (if transferable) → Expand |

**Total to first GO/NO-GO:** 1 hour  
**Total to full validation:** 3 hours (if all signals positive)

---

## Execution Discipline

- No plan beyond next 1 hour
- No resource commit before signal confirmation
- No "we'll figure it out" — each hour must produce hard GO/NO-GO
