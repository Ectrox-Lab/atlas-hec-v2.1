# Atlas-HEC v2.1 Project

> **Sole Reference Edition**  
> **Version**: 4.0.0  
> **Status**: ACTIVE  
> **Effective**: 2026-03-15

---

## Sole Reference Principle (唯一主參照原則)

### 核心紀律

> **我們不以外部體系定義自己，而以自身軌跡的連續進化定義自己。**

### 唯一參照線

```
唯一主參照線 = 過去的我們

           g100 ───→ g200 ───→ g300 ───→ ...
             │         │         │
             ↓         ↓         ↓
         checksum  checksum  checksum
         family    family    family
         lineage   lineage   lineage
         
比較基準:
- 當前世代 vs 前世代
- 當前繼承有效性 vs 前世代繼承有效性  
- 當前軌跡清晰度 vs 前世代軌跡清晰度
- 當前可重播性、可審計性、結構傳承性 vs 前世代
```

### 禁止的外部參照

| 禁止參照 | 原因 |
|---------|------|
| 傳統大模型 benchmark | 描述的是別的問題、別的系統、別的邊界條件 |
| 公開 leaderboard | 優化目標不同，非內生進化 |
| 學術文獻標準 | 預設了靜態權重、任務切分、訓練/推理分離等框架 |
| 產業 SOTA | 比的是能力搬運，非軌跡繼承 |

### 允許的外部觀察

- ✅ 觀察傳統系統作為對照組（但不作為目標）
- ✅ 提取通用工程技術（但不採納其架構哲學）
- ✅ 借鑑失敗教訓（但不模仿其成功路徑）

---

## Trajectory Principle (軌跡優先原則)

### 四句核心紀律

1. **時間不是第一性對象，執行窗口只是軌跡切片。**
2. **隨機不是核心解釋，真正核心是可重播的因果展開。**
3. **努力不是反命定，而是生成後續軌跡的必要前因。**
4. **研究目標不是敘事勝利，而是把軌跡變成可審計、可複現、可繼承的工程對象。**

### 向內觀 · 向外展

```
向內觀 (Inward Gaze)          向外展 (Outward Expansion)
     │                              │
     ↓                              ↓
看清軌跡                      延伸軌跡
  - 前因有效性                  - 更大任務空間
  - 狀態轉移真實性              - 更遠邊界條件
  - 結構繼承效率                - 更複雜環境
  - 失敗模式壓縮                - 更長時間跨度
     │                              │
     └──────────┬───────────────────┘
                ↓
         統一於軌跡連續性
```

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

---

## 強制報告格式

### 每輪實驗報告結構

```markdown
## Trajectory Report: {batch_id}

### 1. Antecedent (前因)
- seeds, inheritance_package, lineage, environment

### 2. State Transition (狀態轉移)
- checksum_before → checksum_after
- computation_cost

### 3. Artifact (產物)
- model_weights, decision_logs, metrics_summary, lineage_record

### 4. Directionality Check (方向性驗證)
- forward_pair, reverse_pair, gap_symmetry_ratio, direction_bias

### 5. Source Suitability Hypothesis (源適配性假說)
- evidence_strength, supporting_pairs, contradicting_pairs

### 6. Trajectory Delta Explained (軌跡改變說明)
- 這一批次改變了後續分佈的具體機制
- 與前代對比
- 科學結論
```

---

## 從 g100 到 g300 的軌跡化

| 代際 | 舊表述 | 軌跡化表述 |
|------|--------|-----------|
| g100 | "突破了" | `checkpoint_100.tar` + `family_shift_log.json` + `uplift_metrics.csv` |
| g200 | "變異了" | `mutation_record_{id}.json` + `crossover_lineage.png` + `selection_pressure_delta` |
| g300 | "強化了" | `inheritance_consumption_rate` + `failure_compression_ratio` + `verified_replay_log` |

---

## 禁止事項

- ❌ 使用「變強了」等敘事詞，無具體軌跡證據
- ❌ 聲稱「成功」而無可重播 artifact
- ❌ 將世代數字 (g100/g200) 當成口號而非可驗證狀態
- ❌ 混淆「敘事連貫」與「因果可審計」
- ❌ 以傳統 benchmark 定義進步
- ❌ 追求 leaderboard 排名而非軌跡清晰度

---

## 當前主線

| 批次 | 軌跡目標 | 狀態 |
|------|---------|------|
| Batch-1 (A→B) | 確立 Code→Math transfer 基準 (14.5pp) | ✅ 完成 |
| Batch-2 (A→C) | 測試 domain gap 影響 (6.8pp) | ✅ 完成 |
| Batch-3 (B→A) | **方向性發現** (9.77pp, ratio=0.665) | ✅ 完成 |
| **Batch-4 (A→C full)** | **驗證 Code source 優勢普遍性** | 🟡 **當前優先** |
| Batch-5 (C→A) | 測試 Planning 能否作為 source | ⏸️ 等待 |
| Batch-6-7 | 完成 matrix | ⏸️ 等待 |

---

## 核心發現

### 方向性發現 (Directionality Discovery)

```
Code→Math: 14.69pp
Math→Code: 9.77pp
Ratio: 0.665 (Near Symmetric but Direction-Biased)

Finding: Transfer is bidirectionally viable but not directionally neutral.
Code appears to be a stronger source task than Math for this pair.

Scientific Meaning:
- Cross-task inheritance depends on source→target ordering
- Source suitability is not uniform across tasks
- Abstraction level may predict source strength
```

---

## 捅破窗戶紙

**不是理解宇宙，而是把展開路徑抓到足夠清楚，讓它不再只能靠直覺描述。**

**不是比誰 benchmark 高，而是比昨天的我們是否更可持續。**

等待 Batch-4 軌跡證據。

---

*Sole Reference Principle v4.0 - 2026-03-15*
