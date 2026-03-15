# Claim Ladder: Explicit Scope and Limitations

## Overview

This document explicitly delineates what Atlas-HEC v2.1 claims, what it supports with scope limitations, and what it explicitly does not claim.

---

## TIER 1: Strong Claims (Directly Supported)

### 1.1 Single-Task Self-Improvement
**Claim**: Atlas-HEC achieves measurable self-improvement on single tasks through inheritance mechanisms.

**Evidence**: 18.7pp control gap (L4), validated lineage, reproducible across seeds.

**Confidence**: HIGH

### 1.2 Cross-Task Inheritance Exists
**Claim**: Within the evaluated Math/Code/Planning task family, cross-task inheritance is broadly viable.

**Evidence**: 6/6 pairs positive, 67/70 windows (95.7%), all 95% CIs > 0.

**Confidence**: HIGH

### 1.3 Source Suitability Hierarchy
**Claim**: Within evaluated tasks, source suitability follows hierarchy: Code > Math > Planning.

**Evidence**: Statistical significance (CI non-overlap Code vs Math), consistent across targets.

**Confidence**: HIGH for Code vs others; MODERATE for Math vs Planning

### 1.4 Learned Policy Viability
**Claim**: A lightweight policy learned from trajectory can match hand-coded heuristics.

**Evidence**: TIER_2_MATCH (3/3 runs), 0/3 circuit breakers, all metrics at parity.

**Confidence**: HIGH

### 1.5 Protocol Self-Correction
**Claim**: The experimental methodology can identify and correct its own flaws.

**Evidence**: CB v1.0 incident → v2.0 correction → Full L6 success validation.

**Confidence**: HIGH

---

## TIER 2: Supported with Scope Limitations

### 2.1 Directionality Structure
**Claim**: Transfer is bidirectionally viable but directionally asymmetric.

**Evidence**: Ratios 1.1-1.5 (moderate), no extreme asymmetry.

**Scope**: Within evaluated pairs only.

**Confidence**: MODERATE

### 2.2 Abstraction Hypothesis
**Claim**: Source suitability may correlate with task abstraction level.

**Evidence**: Post-hoc pattern (Code formal > Math symbolic > Planning concrete).

**Scope**: Hypothesis only; mechanism not proven.

**Confidence**: LOW (exploratory)

### 2.3 Robustness to Controls
**Claim**: Effects are robust to temporal shuffling and random pairing baselines.

**Evidence**: Control 1 (no effect), Control 2 (real >> random).

**Scope**: Within tested perturbations.

**Confidence**: HIGH

---

## TIER 3: Explicitly NOT Claimed

### 3.1 Universal Generalization
**NOT Claimed**: Inheritance works for arbitrary task families.

**Why**: Only 3 task types tested.

**What would be needed**: Evaluation on 5+ diverse task types.

### 3.2 Mechanism Identification
**NOT Claimed**: We know *why* Code is better source (e.g., specific transferable structures).

**Why**: Abstraction is post-hoc hypothesis; no causal mechanism isolated.

**What would be needed**: Ablation studies, latent analysis, feature importance.

### 3.3 Cross-Model Generalization
**NOT Claimed**: Results hold across different model architectures.

**Why**: Single model family (GPT-OSS-120B) tested.

**What would be needed**: Replication on 2+ different architectures.

### 3.4 Superhuman Performance
**NOT Claimed**: Learned policy exceeds human heuristic capability.

**Why**: TIER_2_MATCH (equal), not TIER_1 (superior).

**What would be needed**: Learned > Heuristic + 1pp with statistical significance.

### 3.5 Long-Term Stability
**NOT Claimed**: Effects persist over very long trajectories (>100 generations).

**Why**: Trajectory bounded by experimental scope.

**What would be needed**: Extended longitudinal study.

### 3.6 Recursive Self-Improvement
**NOT Claimed**: System can improve its own improvement mechanism (strong RSI).

**Why**: L6 learns selection policy, not learning algorithm itself.

**What would be needed**: L7 (algorithm improvement).

---

## Summary Table

| Claim | Tier | Confidence | Scope |
|:------|:----:|:----------:|:------|
| Self-improvement works | 1 | HIGH | Single-task |
| Cross-task works | 1 | HIGH | Math/Code/Planning |
| Source hierarchy | 1 | HIGH | Within evaluated |
| Learned matches heuristic | 1 | HIGH | L6 validation |
| Protocol self-correction | 1 | HIGH | Documented case |
| Directionality | 2 | MODERATE | Within evaluated |
| Abstraction hypothesis | 2 | LOW | Post-hoc only |
| Universal generalization | 3 | N/A | NOT CLAIMED |
| Mechanism identified | 3 | N/A | NOT CLAIMED |
| Cross-model valid | 3 | N/A | NOT CLAIMED |
| Superhuman performance | 3 | N/A | NOT CLAIMED |
| Long-term stability | 3 | N/A | NOT CLAIMED |
| Strong RSI | 3 | N/A | NOT CLAIMED |

---

## Responsible Claim-Making Statement

> Atlas-HEC v2.1 makes strong claims within tested scope and explicitly delineates boundaries. We believe this represents responsible research practice: maximizing what the evidence supports while transparently marking what remains unknown.

---

*This ladder ensures readers understand both what has been demonstrated and what has not.*
