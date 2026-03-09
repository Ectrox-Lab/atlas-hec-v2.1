# Phase 5 正式執行作戰單

**狀態**: READY_FOR_EXECUTION  
**日期**: 2026-03-09  
**執行者**: Kimi / Local Server  
**輔助**: Codex (判讀階段)

---

## 執行版 (Kimi / Local)

### 前置檢查

```bash
# 1. 確認 bio-world repo 在正確分支
cd /path/to/bio-world
git status  # 應該是 main 或 phase5-prep 分支

# 2. 確認 PR #12 已合併
git log --oneline | grep -i "phase5\|threshold\|invariant" | head -5

# 3. 確認磁盤空間
df -h .  # 需要至少 1GB 空閒

# 4. 確認編譯環境
rustc --version  # 需要 1.70+
cargo --version
```

---

### 編譯

```bash
cd bioworld_mvp

# 清理舊編譯（可選但建議）
cargo clean

# Release 編譯（優化，較慢但跑得快）
cargo build --release

# 確認產物
ls -lh target/release/bioworld_mvp
# 應該看到執行檔，約 5-20MB
```

**預期時間**: 2-5 分鐘  
**成功標誌**: 無錯誤，執行檔生成

---

### 執行四條件

**執行順序**（建議按此順序，但可並行）:

#### 條件 1: baseline_full

```bash
./target/release/bioworld_mvp \
  --ticks 10000 \
  --universes 16 \
  --sentinel-mode baseline_full \
  --output-dir runs/sentinel/baseline_full

# 預期時間: 30-120 分鐘（取決於 CPU）
# 預期輸出: 16 個 universe CSV + 匯總檔
```

**即時驗證**（每 10 分鐘檢查一次）:
```bash
ls runs/sentinel/baseline_full/
# 應該看到: universe_00/, universe_01/, ..., summary.json

wc -l runs/sentinel/baseline_full/universe_00/population.csv
# 應該在增長，最終約 10001 行（含 header）
```

---

#### 條件 2: no_L2

```bash
./target/release/bioworld_mvp \
  --ticks 10000 \
  --universes 16 \
  --sentinel-mode no_L2 \
  --output-dir runs/sentinel/no_L2
```

**關鍵觀察**:  
- 預期 L2 關閉後多樣性下降
- 若發現崩潰（population → 0），記錄並重跑

---

#### 條件 3: L3_real_p001

```bash
./target/release/bioworld_mvp \
  --ticks 10000 \
  --universes 16 \
  --sentinel-mode L3_real_p001 \
  --output-dir runs/sentinel/L3_real_p001
```

---

#### 條件 4: L3_shuffled_p001

```bash
./target/release/bioworld_mvp \
  --ticks 10000 \
  --universes 16 \
  --sentinel-mode L3_shuffled_p001 \
  --output-dir runs/sentinel/L3_shuffled_p001
```

**關鍵觀察**:  
- 這是 R1 驗證的關鍵對照
- archive_shuffle 必須為 true
- 若發現和 L3_real 太像，可能是 shuffle 未生效

---

### 執行中監控腳本

```bash
#!/bin/bash
# save as: monitor_phase5.sh

CONDITION=$1  # baseline_full, no_L2, L3_real_p001, L3_shuffled_p001

while true; do
    echo "=== $(date) ==="
    
    # 檢查進度
    for u in runs/sentinel/${CONDITION}/universe_*/population.csv; do
        if [ -f "$u" ]; then
            lines=$(wc -l < "$u")
            echo "$(basename $(dirname $u)): $lines lines"
        fi
    done
    
    # 檢查是否有崩潰（population = 0）
    for u in runs/sentinel/${CONDITION}/universe_*/population.csv; do
        if [ -f "$u" ]; then
            last_pop=$(tail -1 "$u" | cut -d',' -f2)
            if [ "$last_pop" = "0" ]; then
                echo "⚠️  ALERT: $(basename $(dirname $u)) has population = 0"
            fi
        fi
    done
    
    sleep 60
done
```

使用:
```bash
chmod +x monitor_phase5.sh
./monitor_phase5.sh baseline_full &
```

---

### 執行後即時驗證（每條件跑完立刻做）

```bash
CONDITION="baseline_full"  # 換成實際條件名

# 1. 檢查 universe 數量
echo "Universes completed:"
ls runs/sentinel/${CONDITION}/ | grep universe | wc -l
# 預期: 16

# 2. 檢查每個 universe 的 tick 數
echo "Tick counts per universe:"
for f in runs/sentinel/${CONDITION}/universe_*/population.csv; do
    echo "$(basename $(dirname $f)): $(($(wc -l < $f) - 1)) ticks"
done
# 預期: 每個都是 10000

# 3. 檢查 CSV header
head -1 runs/sentinel/${CONDITION}/universe_00/population.csv
# 預期: tick,population,births,deaths,...

# 4. 檢查 summary.json
ls runs/sentinel/${CONDITION}/summary.json
```

**若以上任何一項失敗**: 標記該條件為「需要重跑」，但不要刪除，保留給 Codex 分析失敗原因。

---

## 輔助版 (Codex)

### 判讀流程（四條件都跑完後）

#### Step 1: 數據收集

```bash
# 將四條件數據打包
tar czvf phase5_results_$(date +%Y%m%d).tar.gz \
  runs/sentinel/baseline_full/ \
  runs/sentinel/no_L2/ \
  runs/sentinel/L3_real_p001/ \
  runs/sentinel/L3_shuffled_p001/

# 上傳或提供給 Codex 分析
```

---

#### Step 2: Invariant 驗證（自動化腳本）

```python
# invariant_check.py
import pandas as pd
import json
from pathlib import Path

def check_invariants(condition_path):
    """檢查該條件是否通過所有不變量測試"""
    results = {"condition": Path(condition_path).name, "passed": True, "violations": []}
    
    for universe_dir in Path(condition_path).glob("universe_*"):
        csv_path = universe_dir / "population.csv"
        if not csv_path.exists():
            results["violations"].append(f"{universe_dir.name}: missing CSV")
            results["passed"] = False
            continue
            
        df = pd.read_csv(csv_path)
        
        # Invariant 1: Population stability
        final_pop = df['population'].iloc[-1]
        if not (500 <= final_pop <= 700):
            results["violations"].append(f"{universe_dir.name}: population={final_pop}, expected [500,700]")
            results["passed"] = False
        
        # Invariant 2: No crash (all ticks present)
        if len(df) != 10000:
            results["violations"].append(f"{universe_dir.name}: {len(df)} ticks, expected 10000")
            results["passed"] = False
        
        # Invariant 3: Archive access (L3 conditions)
        if 'L3' in condition_path:
            # 檢查是否有 archive_sample_attempts > 0
            pass  # 根據實際 CSV 列名調整
    
    return results

# 檢查四條件
for condition in ['baseline_full', 'no_L2', 'L3_real_p001', 'L3_shuffled_p001']:
    result = check_invariants(f"runs/sentinel/{condition}")
    print(json.dumps(result, indent=2))
```

---

#### Step 3: Effect Size 計算

```python
# effect_size_calculation.py
import pandas as pd
import numpy as np
from scipy import stats

def cohens_d(x, y):
    """計算 Cohen's d"""
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    pooled_std = np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)
    return (np.mean(x) - np.mean(y)) / pooled_std

def analyze_comparison(cond_a, cond_b, metric='adaptation_gain'):
    """比較兩個條件"""
    
    # 讀取數據（假設 summary.json 存在）
    with open(f"runs/sentinel/{cond_a}/summary.json") as f:
        data_a = json.load(f)
    with open(f"runs/sentinel/{cond_b}/summary.json") as f:
        data_b = json.load(f)
    
    values_a = [u[metric] for u in data_a['universes']]
    values_b = [u[metric] for u in data_b['universes']]
    
    # 統計檢定
    t_stat, p_value = stats.ttest_ind(values_a, values_b)
    d = cohens_d(values_a, values_b)
    
    # 相對差異
    delta = (np.mean(values_a) - np.mean(values_b)) / np.mean(values_b)
    
    return {
        "comparison": f"{cond_a} vs {cond_b}",
        "metric": metric,
        "mean_a": np.mean(values_a),
        "mean_b": np.mean(values_b),
        "delta": delta,
        "cohens_d": d,
        "p_value": p_value,
        "n_a": len(values_a),
        "n_b": len(values_b)
    }

# 關鍵比較
comparisons = [
    analyze_comparison('L3_real_p001', 'L3_shuffled_p001'),  # R1
    analyze_comparison('baseline_full', 'no_L2'),             # R3
    analyze_comparison('L3_real_p001', 'L3_off'),             # R2 (需要 L3_off 數據)
]

for comp in comparisons:
    print(f"\n{comp['comparison']}:")
    print(f"  δ = {comp['delta']:+.3f}")
    print(f"  Cohen's d = {comp['cohens_d']:.3f}")
    print(f"  p = {comp['p_value']:.4f}")
    
    # 應用門檻
    if comp['comparison'].startswith('L3_real'):
        if comp['delta'] > 0.20 and comp['cohens_d'] > 0.5 and comp['p_value'] < 0.05:
            print("  → ✅ GO (passes threshold)")
        elif -0.10 <= comp['delta'] <= 0.10:
            print("  → ❌ NO-GO (equivalence)")
        elif 0.10 < abs(comp['delta']) < 0.20:
            print("  → 🟡 EXTEND (ambiguous)")
        else:
            print("  → ⚠️ UNEXPECTED")
```

---

#### Step 4: 最終判決報告

```python
def generate_phase5_verdict(results):
    """生成 Phase 5 最終判決"""
    
    # 提取關鍵結果
    r1_result = next(r for r in results if 'shuffled' in r['comparison'])
    r3_result = next(r for r in results if 'no_L2' in r['comparison'])
    
    verdict = {
        "phase": "5",
        "date": pd.Timestamp.now().isoformat(),
        "r1_validation": None,
        "r3_validation": None,
        "final_decision": None,
        "evidence": {}
    }
    
    # R1 判讀
    if r1_result['delta'] > 0.20 and r1_result['cohens_d'] > 0.5:
        verdict["r1_validation"] = "PASSED - Content matters"
        verdict["evidence"]["r1"] = f"δ={r1_result['delta']:.3f}, d={r1_result['cohens_d']:.2f}"
    elif -0.10 <= r1_result['delta'] <= 0.10:
        verdict["r1_validation"] = "FAILED - Content irrelevant"
        verdict["final_decision"] = "NO_GO_HYPOTHESIS_FAIL"
        return verdict
    else:
        verdict["r1_validation"] = "AMBIGUOUS - Need more data"
        verdict["final_decision"] = "EXTEND"
        return verdict
    
    # R3 判讀（非阻塞但加強證據）
    if r3_result['delta'] > 0.10 and r3_result['cohens_d'] > 0.3:
        verdict["r3_validation"] = "SUPPORTED - L2 helps"
    else:
        verdict["r3_validation"] = "WEAK - L2 effect unclear"
    
    # 最終決策
    if verdict["r1_validation"].startswith("PASSED"):
        if verdict["r3_validation"].startswith("SUPPORTED"):
            verdict["final_decision"] = "STRONG_GO"
        else:
            verdict["final_decision"] = "GO"
    
    return verdict
```

---

## 執行後判讀標準流程

### 當四條件都乾淨完成後

1. **Invariant 檢查**（5 分鐘）
   - 運行 `invariant_check.py`
   - 所有條件必須 passed
   - 若有 violation，標記重跑

2. **Effect Size 計算**（10 分鐘）
   - 運行 `effect_size_calculation.py`
   - 記錄 δ, Cohen's d, p-value

3. **應用門檻**（5 分鐘）
   - L3_real vs shuffled: δ > 0.20, d > 0.5, p < 0.05
   - baseline vs no_L2: d > 0.3

4. **生成判決**（5 分鐘）
   - 運行 `generate_phase5_verdict()`
   - 輸出: STRONG_GO / GO / EXTEND / NO_GO

5. **文檔更新**（10 分鐘）
   - 更新 `status-sync.json`
   - 更新 `PHASE5_VERDICT.md`
   - 提交 git: `[phase5-complete] Verdict: XXXX`

---

## 故障排除

| 症狀 | 可能原因 | 解決方案 |
|------|----------|----------|
| 編譯失敗 | Rust 版本過舊 | `rustup update` |
| 運行極慢 | 未用 release 模式 | `cargo build --release` |
| population = 0 | Boss 壓力過大或參數錯誤 | 檢查 sentinel-mode 配置 |
| ticks < 10000 | 提前終止 | 檢查是否有 panic，重跑 |
| CSV 列缺失 | 舊版本 code | 確認 PR #12 已合併 |
| shuffle 未生效 | archive_shuffle flag 未設 | 檢查 L3_shuffled_p001 配置 |

---

## 預期時間表

| 階段 | 時間 | 檢查點 |
|------|------|--------|
| 編譯 | 2-5 min | 執行檔生成 |
| baseline_full | 30-120 min | 16 universes × 10000 ticks |
| no_L2 | 30-120 min | 同上 |
| L3_real_p001 | 30-120 min | 同上 |
| L3_shuffled_p001 | 30-120 min | 同上 |
| 判讀 | 30 min | 腳本自動化 |
| **總計** | **2-8 小時** | 取決於 CPU 核心數 |

**並行建議**: 若有多核 CPU，可同時跑多個條件（不同 terminal）

---

## 成功定義

✅ **Phase 5 成功** = 四條件都乾淨完成 + Invariant 全過 + R1 PASSED

🟡 **Phase 5 部分成功** = 四條件完成但 R3 不明確 → GO (with caveats)

❌ **Phase 5 失敗** = R1 FAILED (L3_real ≈ L3_shuffled) → NO_GO

---

**作戰單版本**: 1.0  
**執行就緒**: YES  
**下一步**: 開始編譯並執行第一條件
