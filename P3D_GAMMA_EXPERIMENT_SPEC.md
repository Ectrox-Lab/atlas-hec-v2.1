# P3D-gamma Experiment Specification

**Version**: 1.0  
**Date**: 2026-03-09  
**Status**: Framework Ready → Awaiting Adequate-Sample Validation

---

## 1. 固定 Seed 集合

```python
SEED_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

**约束**: 必须使用此精确列表，不得随机生成或修改顺序。

---

## 2. 代码版本记录

每次实验运行必须记录：

```json
{
  "git_commit_hash": "<full_40_char_hash>",
  "build_command": "cargo build --bin p3d_main_runtime_native --release",
  "binary_path": "./target/release/p3d_main_runtime_native",
  "experiment_date": "2026-03-09T00:00:00+00:00"
}
```

**获取 commit hash**:
```bash
git rev-parse HEAD
```

---

## 3. 实验运行命令

### 3.1 完整批量脚本

```bash
#!/bin/bash
# P3D-gamma Adequate-Sample Experiment Run
# Run this after: cargo build --bin p3d_main_runtime_native --release

set -e

SEEDS=(1 2 3 4 5 6 7 8 9 10)
EPISODES=50
STEPS=500
BINARY="./target/release/p3d_main_runtime_native"

echo "=== P3D-gamma Adequate-Sample Experiment ==="
echo "Git commit: $(git rev-parse HEAD)"
echo "Seeds: ${SEEDS[@]}"
echo "Episodes/seed: $EPISODES"
echo ""

for seed in "${SEEDS[@]}"; do
    echo "Running seed $seed..."
    
    # Baseline
    $BINARY --preservation off --seed $seed --episodes $EPISODES --steps $STEPS
    
    # P2-ON
    $BINARY --preservation on --seed $seed --episodes $EPISODES --steps $STEPS
done

echo ""
echo "=== Analysis ==="
python3 scripts/analyze_p3d_gamma.py logs/p3d/

echo ""
echo "=== Verification Check ==="
python3 scripts/verify_p3d_gamma_completion.py logs/p3d/summary_report.json
```

### 3.2 手动单条验证

```bash
# 记录当前版本
export GIT_HASH=$(git rev-parse HEAD)
echo "Running with commit: $GIT_HASH"

# Seed 1 Baseline
./target/release/p3d_main_runtime_native --preservation off --seed 1 --episodes 50 --steps 500

# Seed 1 P2-ON
./target/release/p3d_main_runtime_native --preservation on --seed 1 --episodes 50 --steps 500
```

---

## 4. 结果保存规范

### 4.1 必须保存的文件

| 文件 | 说明 |
|-----|------|
| `logs/p3d/*_seed{1-10}_*_result.json` | 20 个结果文件（10 baseline + 10 p2on）|
| `logs/p3d/summary_report.json` | 统计分析汇总 |
| `experiment_config.json` | 本次实验配置与版本信息 |

### 4.2 experiment_config.json 模板

```json
{
  "experiment_name": "P3D-gamma-adequate-sample",
  "experiment_date": "2026-03-09T12:00:00+00:00",
  "git": {
    "commit_hash": "1d98e72...",
    "branch": "master",
    "dirty": false
  },
  "build": {
    "command": "cargo build --bin p3d_main_runtime_native --release",
    "rust_version": "rustc 1.75.0",
    "binary_path": "./target/release/p3d_main_runtime_native"
  },
  "parameters": {
    "seed_list": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "episodes_per_seed": 50,
    "max_steps_per_episode": 500
  },
  "expected_outputs": {
    "baseline_files": 10,
    "p2on_files": 10,
    "total_episodes_per_condition": 500
  }
}
```

---

## 5. 验收标准（硬性）

### 5.1 必须同时满足

```python
# 从 summary_report.json 读取
assert verdict == "SUPPORTED_SHIFT"
assert sample_level == "adequate"
assert effect_detected == true
assert intervention_active == true
```

### 5.2 具体阈值

| 条件 | 阈值 | 说明 |
|-----|------|------|
| `n_paired_seeds` | ≥ 10 | 必须覆盖全部 seed list |
| `total_episodes` | ≥ 500 | 每组至少 500 episodes |
| `intervention_rate` | > 10% | P2-ON 组干预率 |
| `cohens_d_pooled` | ≥ 0.20 | 且 `pooled_significant == true` |
| `cohens_d_paired` | ≥ 0.20 | 且 `paired_significant == true` |

### 5.3 验证脚本

```python
# scripts/verify_p3d_gamma_completion.py
import json
import sys

def verify(summary_path):
    with open(summary_path) as f:
        data = json.load(f)
    
    checks = {
        "verdict_is_supported": data.get("verdict", "").startswith("SUPPORTED_SHIFT"),
        "sample_adequate": data.get("sample_level") == "adequate",
        "effect_detected": data.get("effect_detected") == True,
        "intervention_active": data.get("intervention_active") == True,
        "seeds_sufficient": data.get("n_paired_seeds", 0) >= 10,
        "episodes_sufficient": data.get("total_episodes", 0) >= 500,
    }
    
    print("=== P3D-gamma Completion Verification ===")
    all_pass = True
    for name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
        if not passed:
            all_pass = False
    
    print()
    if all_pass:
        print("🎯 P3D-gamma: COMPLETE")
        print("   Measured behavioral shift validated")
        return 0
    else:
        print("⏳ P3D-gamma: NOT YET COMPLETE")
        print("   Run more experiments or check configuration")
        return 1

if __name__ == "__main__":
    sys.exit(verify(sys.argv[1]))
```

---

## 6. 最终状态升级流程

```
当前: P3D-gamma = Framework Ready

实验运行后:
    ↓
运行 verify_p3d_gamma_completion.py
    ↓
if 全部检查通过:
    升级: P3D-gamma = COMPLETE
    状态: Measured behavioral shift validated
else:
    保持: P3D-gamma = Framework Ready
    动作: 补充实验或调整参数
```

---

## 7. 复现检查清单

- [ ] 使用固定 `SEED_LIST = [1,2,3,4,5,6,7,8,9,10]`
- [ ] 记录 `git rev-parse HEAD` 到 experiment_config.json
- [ ] 使用 `cargo build --release` 构建
- [ ] 每组 500+ episodes (10 seeds × 50 episodes)
- [ ] 运行 `analyze_p3d_gamma.py` 生成 summary_report.json
- [ ] 运行 `verify_p3d_gamma_completion.py` 验证全部通过
- [ ] 保存所有原始 result.json 文件

---

**最终目标**: 满足验收标准后，P3D-gamma 可正式声明为 **COMPLETE**。
