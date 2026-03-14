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

## 5. Trajectory Delta Explained (軌跡改變說明)

### 這一批次改變了後續分佈的具體機制：

```
[詳細說明]
- 哪些前因導致了哪些後效
- 如何避免表面波動
- 關鍵轉折點的因果鏈
- 對後續世代的具體影響
```

### 與前代對比：

| 指標 | Batch-1 (A→B) | Batch-2 (A→C) | 本批次 ({X→Y}) | 解讀 |
|------|--------------|--------------|---------------|------|
| Mean TG | 14.5pp | 6.8pp | {pp} | {} |
| 對稱性 | - | - | {symmetric/asymmetric} | {} |
| Domain Gap | 小 | 大 | {} | {} |

### 科學結論：

```
[這一批驗證了什麼假設，推翻了什麼假設，留下了什麼待解問題]
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
