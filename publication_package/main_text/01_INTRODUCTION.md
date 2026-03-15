# 1. Introduction

## 1.1 The Self-Improvement Challenge

Current AI systems improve primarily through external intervention—human-designed curriculum, engineered reward functions, or brute-force scale increases. A fundamental open question remains: can a system improve itself through mechanisms it controls and validates?

Atlas-HEC addresses this through three sequential investigations:
- **L4**: Can a system improve itself on a single task?
- **L5**: Can improvement transfer across tasks?
- **L6**: Can the system learn *how* to transfer better?

## 1.2 The Sole Reference Principle

Traditional AI research relies on external benchmarks for validation. Atlas-HEC operates under a different paradigm: the **Sole Reference Principle**.

> The primary reference for progress is not external leaderboards, public datasets, or prior literature. The sole primary reference is the system's own historical trajectory.

Progress is measured by:
- Current generation vs. prior generation
- Trajectory clarity and reproducibility  
- Inheritance effectiveness across stages
- Self-audited evidence quality

This does not reject external observation—it prioritizes internal consistency and causal traceability over comparative benchmarking.

## 1.3 Contribution Structure

This paper presents:

**L4 (Single-Task)**: Validation that inheritance mechanisms produce measurable self-improvement on a control task.

**L5 (Multi-Task)**: Demonstration that improvement transfers across tasks with discoverable structure—source suitability hierarchy and directionality.

**L6 (Meta-Learning)**: Evidence that source selection policies can be learned from trajectory history, matching human-engineered heuristics.

**Protocol Evolution**: A documented case of rule-design failure (circuit-breaker v1.0), correction (v2.0), and validation—demonstrating self-correcting experimental methodology.

## 1.4 Scope and Limitations

This work explicitly scopes its claims:
- **Task Family**: Only Math, Code, Planning tasks evaluated
- **Model**: Single model family (no cross-model validation)
- **Mechanism**: Correlational evidence for structure; causal mechanism postulated but not proven
- **Generalization**: External validity to arbitrary tasks not claimed

We believe this represents responsible claim-making: strong evidence within tested scope, with explicit boundaries.

## 1.5 Roadmap

Section 2 describes the protocol and methodology. Section 3 presents L4 results. Section 4 details L5 cross-task inheritance. Section 5 covers L6 meta-learning. Section 6 documents the protocol evolution case study. Section 7 discusses limitations and future work.
