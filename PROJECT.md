# Atlas-HEC v2.1 Project

> **Trajectory Principle Edition**  
> **Version**: 3.0.0  
> **Status**: ACTIVE  
> **Effective**: 2026-03-15

---

## Trajectory Principle (軌跡優先原則)

### 四句核心紀律

1. **時間不是第一性對象，執行窗口只是軌跡切片。**
2. **隨機不是核心解釋，真正核心是可重播的因果展開。**
3. **努力不是反命定，而是生成後續軌跡的必要前因。**
4. **研究目標不是敘事勝利，而是把軌跡變成可審計、可複現、可繼承的工程對象。**

---

## 工程定義

### 什麼是軌跡 (Trajectory)

```
軌跡 = 前因 → 狀態轉移 → 產物 → 後效

前因 (Antecedent):
  - 初始種子 (seeds)
  - 繼承包裹 (inheritance package)
  - 選擇壓力 (selection pressure)
  - 環境配置 (config)

狀態轉移 (State Transition):
  - 真實計算發生
  - 可驗證的 checksum 變化
  - metrics 更新

產物 (Artifact):
  - 模型權重
  - 決策日志
  - 評估指標
  - lineage 記錄

後效 (Consequence):
  - 下一輪初始條件改變
  - 搜索空間壓縮
  - family shift 發生
  - 失敗模式被標記
```

### 軌跡的可審計標準

每個實驗批次必須留下：

| 字段 | 格式 | 用途 |
|------|------|------|
| `trajectory_id` | UUID | 全局唯一標識 |
| `antecedent_snapshot` | JSON | 前因完整記錄 |
| `transition_checksum` | SHA256 | 狀態轉移證明 |
| `artifact_locations` | Path[] | 產物存儲位置 |
| `consequence_metrics` | JSON | 後效量化指標 |
| `trajectory_delta_explained` | Text | 這一批改變了什麼 |

---

## 強制報告格式

### 每輪實驗報告結構

```markdown
## Trajectory Report: {batch_id}

### 1. Antecedent (前因)
- seeds: {n} (hash: {seed_hash})
- inheritance_package: {package_id} (consumption: {rate})
- lineage_source: {parent_trajectory_ids}
- config_version: {git_commit}

### 2. State Transition (狀態轉移)
- checksum_before: {hash_a}
- checksum_after: {hash_b}
- transition_verified: {bool}
- computation_cost: {flops | time | energy}

### 3. Artifact (產物)
- model_weights: {path} (size: {bytes})
- decision_log: {path} (entries: {n})
- metrics: {transfer_gap_pp, retention, ...}
- lineage_record: {path}

### 4. Consequence (後效)
- next_round_eligibility: {bool}
- search_space_compression: {ratio}
- family_shift_detected: {bool}
- failure_archetype_recorded: {id | null}

### 5. Trajectory Delta Explained (軌跡改變說明)
這一批次改變了後續分佈的具體機制：
{詳細說明哪些前因導致了哪些後效，如何避免表面波動}
```

---

## 實驗批次規範

### Batch-3 (B→A) 軌跡記錄

```yaml
trajectory_id: atlas-hec-l5-batch3-b2a-20260315
antecedent:
  seeds: 800 (10 windows × 80)
  source_task: Math
  target_task: Code
  lineage_source: [batch1-a2b, batch2-a2c]
  
state_transition:
  mechanism: bidirectional_transfer_test
  expected_tg: 10-12pp  # Math↔Code domain 接近
  
artifact_required:
  - metrics.json per window
  - decision.json per window
  - trajectory_delta_explained.txt
  
consequence_evaluation:
  success_criteria:
    - mean_tg >= 5pp
    - min_tg > 0pp
    - windows_positive >= 8/10
  
  trajectory_delta_question:
    "B→A (Math→Code) 是否與 A→B (Code→Math) 對稱？
     這將決定 transfer 是雙向普適還是有方向性偏好。"
```

---

## 從 g100 到 g300 的軌跡化

| 代際 | 舊表述 | 軌跡化表述 |
|------|--------|-----------|
| g100 | "突破了" | `checkpoint_100.tar` + `family_shift_log.json` + `uplift_metrics.csv` |
| g200 | "變異了" | `mutation_record_{id}.json` + `crossover_lineage.png` + `selection_pressure_delta` |
| g300 | "強化了" | `inheritance_consumption_rate` + `failure_compression_ratio` + `verified_replay_log` |

---

## 關鍵轉折點記錄

每當發生以下事件，強制生成 `critical_transition_record.json`：

- family shift (家族遷移)
- inheritance package consumption (包裹消費)
- failure archetype recurrence (失敗模式復現)
- search space phase transition (搜索空間相變)
- control gap → transfer gap 轉換

---

## 禁止事項

- ❌ 使用「變強了」等敘事詞，無具體軌跡證據
- ❌ 聲稱「成功」而無可重播 artifact
- ❌ 將世代數字 (g100/g200) 當成口號而非可驗證狀態
- ❌ 混淆「敘事連貫」與「因果可審計」

---

## 當前主線

| 批次 | 軌跡目標 | 狀態 |
|------|---------|------|
| Batch-1 (A→B) | 確立 Code→Math transfer 基準 (14.5pp) | ✅ 完成，軌跡已記錄 |
| Batch-2 (A→C) | 測試 domain gap 影響 (6.8pp) | ✅ 完成，軌跡已記錄 |
| **Batch-3 (B→A)** | **驗證 transfer 對稱性** | 🟡 **等待軌跡證據** |
| Batch-4 (B→C) | Math→Planning transfer 測試 | ⏸️ 等待 Batch-3 軌跡 |
| Batch-5 (C→A) | Planning→Code transfer 測試 | ⏸️ 等待 |
| Batch-6 (C→B) | Planning→Math transfer 測試 | ⏸️ 等待 |

---

## 捅破窗戶紙

**不是理解宇宙，而是把展開路徑抓到足夠清楚，讓它不再只能靠直覺描述。**

等待 Batch-3 的軌跡證據。

---

*Trajectory Principle v3.0 - 2026-03-15*
