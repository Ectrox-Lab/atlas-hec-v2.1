# Trajectory Report: {batch_id}

> **Status**: {PENDING | RUNNING | COMPLETED | FAILED}  
> **Trajectory ID**: {uuid}  
> **Timestamp**: {ISO8601}

---

## 1. Antecedent (前因)

```yaml
seeds:
  total: 800
  per_window: 80
  windows: 10
  seed_hash: {sha256_of_seed_config}
  
inheritance_package:
  source: {parent_trajectory_ids}
  package_id: {uuid}
  consumption_rate: {0.0-1.0}
  
lineage:
  direct_parents: [batch1-a2b, batch2-a2c]
  family_tree_version: {git_tag}
  
environment:
  config_version: {git_commit}
  model: {gpt-oss-120b | nemotron-120b}
  compute: {3x4090 | 4x4090}
  
selection_pressure:
  target_task: {Math | Code | Planning}
  success_threshold: {transfer_gap >= Xpp}
  circuit_breaker: {negative_transfer | catastrophic_forgetting}
```

---

## 2. State Transition (狀態轉移)

| Window | Checksum Before | Checksum After | Verified | Transfer Gap |
|:------:|:---------------:|:--------------:|:--------:|:------------:|
| 1 | {hash} | {hash} | ✅ | {pp} |
| 2 | {hash} | {hash} | ✅ | {pp} |
| ... | ... | ... | ... | ... |
| 10 | {hash} | {hash} | ✅ | {pp} |

```yaml
computation_cost:
  flops: {estimated}
  wall_time: {seconds}
  energy: {kWh}
  
transition_validity:
  all_checksums_unique: {bool}
  no_empty_windows: {bool}
  ralph_decision: {POSITIVE_AUTO | POSITIVE_MANUAL | MARGINAL | FAIL}
```

---

## 3. Artifact (產物)

```yaml
model_weights:
  path: ralph_runs/{batch_id}/window_{N}/checkpoint.tar
  size_bytes: {int}
  checksum: {sha256}
  
decision_logs:
  path: ralph_runs/{batch_id}/window_{N}_decision.json
  entries: 10
  
metrics_summary:
  transfer_gap_mean: {pp}
  transfer_gap_min: {pp}
  transfer_gap_max: {pp}
  transfer_gap_std: {pp}
  code_retention_mean: {%}
  
lineage_record:
  path: ralph_runs/{batch_id}/lineage.json
  family_shift_detected: {bool}
```

---

## 4. Directionality Check (方向性驗證)

### Transfer 方向性評估

```yaml
directionality_check:
  source_task: {A}
  target_task: {B}
  
  forward_pair:  # 本批次 (A→B)
    mean_transfer_gap_pp: {pp}
    windows_positive: {n}/10
    
  reverse_pair:  # 對稱批次 (B→A)
    mean_transfer_gap_pp: {pp}
    reference_batch: {batch_id}
    
  gap_symmetry_ratio: {B_to_A / A_to_B}
    # 1.0 = 完美對稱
    # 0.5-1.5 = 近對稱但有方向偏好
    # <0.5 或 >2.0 = 明顯不對稱
    
  direction_bias: {source_stronger | target_stronger | near_equal}
    # source_stronger: A→B > B→A (本例)
    # target_stronger: B→A > A→B
    # near_equal: 比值接近 1.0
```

### 方向性判定標準

| Ratio 範圍 | 判定 | 科學意義 |
|:----------:|:----:|:---------|
| 0.9-1.1 | 完美對稱 | Transfer 方向中性，任務等價 |
| **0.5-0.9 或 1.1-1.5** | **近對稱但方向偏好** | **雙向可行，但 source→target 不等價 ← 當前** |
| 0.3-0.5 或 1.5-3.0 | 弱對稱 | 單向主導，反向較弱 |
| <0.3 或 >3.0 | 不對稱 | 幾乎單向，反向幾乎無效 |

---

## 5. Source Suitability Hypothesis (源適配性假說)

### 工作假說評估

```yaml
source_suitability_hypothesis:
  source_task: {Code | Math | Planning}
  
  evidence_strength: {weak | moderate | strong}
    # weak: 僅此一批對稱數據
    # moderate: 2-3 批相關數據支持
    # strong: 完整矩陣驗證
    
  supporting_pairs:
    - {source}→{target}: {tg}pp
    # 支持此假說的其他 task pairs
    
  contradicting_pairs:
    # 與此假說矛盾的数据（如有）
    
  current_status: {hypothesis | supported | stable_pattern}
    # hypothesis: 工作假說，待更多數據
    # supported: 多批數據支持
    # stable_pattern: 完整矩陣驗證的穩定模式
```

### 當前發現摘要

```markdown
[Verified from reported metrics]
- {Source}→{Target}: {X}pp
- Reverse: {Y}pp  
- Ratio: {Z}
- Both directions > 0 and > threshold

[Inference - Working Hypothesis]
{Source} appears to be a stronger source task than {Target} for this pair.
This remains a task-pair-specific finding until validated across the remaining matrix.

[Theoretical Implication]
Cross-task inheritance is bidirectionally viable, but not directionally neutral.
Transfer strength depends on source→target ordering.

[Next Validation Required]
- {Source}→{Other}
- {Other}→{Source}
- To determine if this is a local phenomenon or general pattern.
```

---

## 6. Symmetry Check (對稱性驗證)

### 與前代對稱比較

| Pair | Mean TG | Direction Bias | Status |
|:-----|:-------:|:--------------:|:------:|
| Code→Math | 14.69pp | Source Stronger | ✅ Verified |
| Math→Code | 9.77pp | Target Weaker | ✅ Verified |
| Code→Planning | {pp} | {bias} | ⏸️ Pending |
| Planning→Code | {pp} | {bias} | ⏸️ Pending |
| Math→Planning | {pp} | {bias} | ⏸️ Pending |
| Planning→Math | {pp} | {bias} | ⏸️ Pending |

### 科學發現狀態

```
Current Finding (Batch-3):
- Cross-task inheritance is bidirectionally viable, but not directionally neutral.
- Transfer effect depends not only on task pair existence, but also on 
  directional asymmetry between source and target.
- Gap Symmetry Ratio = 0.665 indicates near-symmetric but direction-biased transfer.

Open Questions:
- Is Code universally a stronger source task? (need Code→Planning, Planning→Code)
- Is the asymmetry related to abstraction level? (need Planning↔Math)
- What is the full source suitability × target receptivity matrix?
```

---

## 7. Trajectory Delta Explained (軌跡改變說明)

### 這一批次改變了後續分佈的具體機制

```
[Detailed Explanation]
- Which antecedents led to which consequences
- How to avoid surface fluctuations
- Causal chain of critical turning points
- Specific impact on subsequent generations
- Symmetric/asymmetric structure compared to A→B
- Directionality insight and its implications for L5 theory
```

### 後續實驗策略調整

```yaml
priority_adjustment:
  rationale: "Code appears to be stronger source; prioritize Code→X pairs"
  new_order:
    1: Code→Planning  # Test if Code source advantage generalizes
    2: Planning→Code  # Test reverse
    3: Math→Planning  # Fill matrix
    4: Planning→Math  # Lowest priority based on current pattern
```

---

## 附錄：可重播驗證

```bash
# 重播本軌跡
python3 replay_trajectory.py --trajectory-id {uuid}

# 驗證 checksum 鏈
python3 verify_checksum_chain.py --batch {batch_id}

# 比較與前代差異
python3 compare_trajectory.py --current {uuid} --baseline {parent_uuid}

# 方向性對稱檢查
python3 check_symmetry.py --forward {batch_a2b} --reverse {batch_b2a}
```

---

## 理論貢獻

```markdown
可發表的發現框架:

"Atlas-HEC L5 實驗發現：跨任務繼承存在方向梯度，{Source} 作為 source 時
產生顯著更強的 transfer effect（{X}pp vs {Y}pp, ratio={Z}）。

這挑戰了傳統多任務學習中任務對稱性的隱含假設，表明 transfer strength 
depends on source→target ordering, not just task pair existence.

工作假說：{Source} 的 [抽象層級/結構一致性/形式化程度] 可能使其成為
更優的 source task，但這需要完整 task matrix 驗證。"
```

---

*Trajectory Report v3.1 - Directionality Edition*
