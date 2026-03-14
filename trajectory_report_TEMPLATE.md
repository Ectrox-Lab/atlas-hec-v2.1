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

## 4. Consequence (後效)

```yaml
next_round_eligibility:
  status: {APPROVED | CONDITIONAL | REJECTED}
  condition: {threshold_meeting}
  
search_space_compression:
  ratio: {0.0-1.0}
  mechanism: {inheritance_consumption}
  
family_shift:
  detected: {bool}
  from_family: {id}
  to_family: {id}
  trigger: {mutation | selection | crossover}
  
failure_archetype:
  recorded: {bool}
  archetype_id: {id | null}
  recurrence_count: {int}
  
scientific_finding:
  primary: {string}
  significance: {string}
```

---

## 5. Symmetry Check (對稱性驗證)

### Transfer 方向性評估

```yaml
pair_comparison:
  A_to_B:  # Batch-1 基準
    mean_tg: 14.5pp
    family_shift: {id}
    inheritance_consumption: {pattern}
    
  B_to_A:  # 本批次
    mean_tg: {pp}
    family_shift: {id}
    inheritance_consumption: {pattern}
    
gap_symmetry_ratio: {B_to_A_mean / A_to_B_mean}
  # 1.0 = 完美對稱
  # 0.5-1.5 = 基本對稱
  # <0.5 或 >2.0 = 明顯不對稱
  
shared_family_shift: {bool}
  # B→A 是否落在與 A→B 相似的族群
  
shared_inheritance_consumption_patterns: {bool}
  # 包裹消費模式是否相似
  
asymmetry_explanation: |
  [若不對稱，差異是出在：]
  - source task (Math vs Code 的起點差異)
  - target task (Code vs Math 的終點差異)
  - route / mechanism (傳播路徑差異)
  - 其他因素
```

### 科學意義判定

| 對稱性狀態 | 判定標準 | 意義 |
|-----------|---------|------|
| 完美對稱 | ratio ∈ [0.9, 1.1] | Transfer 是雙向普適，與方向無關 |
| 基本對稱 | ratio ∈ [0.5, 1.5] | Transfer 有一定對稱性，但存在方向偏好 |
| 明顯不對稱 | ratio < 0.5 或 > 2.0 | Transfer 高度依賴 source→target 選擇 |

---

## 6. Trajectory Delta Explained (軌跡改變說明)

### 這一批次改變了後續分佈的具體機制：

```
[詳細說明]
- 哪些前因導致了哪些後效
- 如何避免表面波動
- 關鍵轉折點的因果鏈
- 對後續世代的具體影響
- 與 A→B 的對稱/非對稱結構
```

### 與前代對比：

| 指標 | Batch-1 (A→B) | Batch-2 (A→C) | 本批次 (B→A) | 解讀 |
|------|--------------|--------------|-------------|------|
| Mean TG | 14.5pp | 6.8pp | {pp} | {} |
| Gap Symmetry | - | - | {ratio} | {} |
| Family Shift | {id} | {id} | {id} | {} |
| Domain Gap | 小 | 大 | {評估} | {} |

### 科學結論：

```
[這一批驗證了什麼假設，推翻了什麼假設，留下了什麼待解問題]
[特別回答：Transfer 是否有方向性？]
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
```

---

*Trajectory Report v3.0 - Trajectory Principle*
