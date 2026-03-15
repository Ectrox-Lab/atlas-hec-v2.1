# 3. L4 Results: Single-Task Self-Improvement

## 3.1 Overview

L4 establishes the foundational capability: can a system improve itself on a single task through inheritance mechanisms?

## 3.2 Experimental Design

**Control**: Baseline execution without inheritance packages  
**Treatment**: Execution with consumption of prior trajectory inheritance  
**Primary Metric**: Control Gap (percentage point improvement over baseline)

## 3.3 Results

| Metric | Value | Status |
|:-------|:------|:------:|
| Control Gap | 18.7pp | ✅ Validated |
| Lineage Depth | Multiple generations | ✅ Traceable |
| Reproducibility | Consistent across seeds | ✅ Confirmed |

## 3.4 Interpretation

The 18.7pp control gap demonstrates that inheritance mechanisms produce measurable, reproducible self-improvement on single tasks. This validates the foundational assumption: the system can improve itself through structured trajectory carryover.

## 3.5 Limitations

- Single task family only
- No cross-task claims
- Mechanism-level explanation (what specific structures transfer) not fully elucidated

## 3.6 Transition to L5

L4 establishes that improvement is possible. L5 asks whether this improvement can transfer across different tasks.
