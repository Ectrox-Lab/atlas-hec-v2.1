# Bio-World v18.1 可复现实验指南

**版本**: v1.0  
**日期**: 2026-03-09  
**实验**: Bio-World v18.1 灭绝动力学研究  
**核心发现**: CDI早期预警信号 + 三阶段灭绝连锁

---

## 快速开始（5分钟复现）

```bash
# 1. 进入实验目录
cd /home/admin/atlas-hec-v2.1-repo

# 2. 使用已有数据运行完整分析
./run_full_analysis.sh \
    /home/admin/zeroclaw-labs/v18_1_experiments/20260301_055827_306668/evolution.csv

# 3. 查看结果
cat model_fit_results/BIOWORLD_V18_FINDINGS.json
```

---

## 完整复现流程

### 阶段0: 环境准备

**依赖**:
```bash
# Rust环境
cargo --version  # >= 1.70

# Python环境
python3 --version  # >= 3.9
pip install pandas numpy scipy matplotlib

# CUDA (可选，用于GPU加速)
nvidia-smi
```

**仓库结构**:
```
atlas-hec-v2.1-repo/
├── source/              # Rust源码
│   └── src/main.rs     # Bio-World v18.1主程序
├── zeroclaw-labs/       # 实验数据目录
│   └── v18_1_experiments/
│       └── <timestamp>/
│           └── evolution.csv
├── fit_*_model_v2.py    # 三层动力学拟合
├── extinction_precursor_detector.py  # 前兆检测器
└── model_fit_results/   # 输出目录
```

---

### 阶段1: 生成实验数据

**方式A: 使用已有数据（推荐复现）**
```bash
# 使用已存档的v18.1实验数据
CSV_PATH=/home/admin/zeroclaw-labs/v18_1_experiments/20260301_055827_306668/evolution.csv
```

**方式B: 运行新实验（验证稳定性）**
```bash
# 1. 编译
cd source
cargo build --release

# 2. 运行v18.1（约需2-4小时，7000代）
./target/release/atlas-hec-v2.1 \
    --mode bio-world-v18 \
    --max-population 500 \
    --synapses-per-cell 15 \
    --generations 7000 \
    --output ../zeroclaw-labs/v18_1_experiments/

# 3. 确认输出
cat ../zeroclaw-labs/v18_1_experiments/*/evolution.csv
```

---

### 阶段2: 三层动力学拟合

```bash
cd /home/admin/atlas-hec-v2.1-repo

# 运行所有拟合脚本
./run_model_fitting_v2.sh $CSV_PATH

# 输出:
# - model_fit_results/population_model_fit.json
# - model_fit_results/cdi_model_fit.json
# - model_fit_results/cooperation_gate_fit.json
```

**验证K_I ≈ 0.8**:
```bash
cat model_fit_results/cdi_model_fit.json | jq '.parameters.K_I'
# 预期输出: 0.8000（±0.05范围内可接受）
```

---

### 阶段3: 灭绝前兆检测（核心发现）

```bash
# 运行前兆检测器
python3 extinction_precursor_detector.py $CSV_PATH

# 输出:
# - model_fit_results/extinction_precursor_analysis.json
# - model_fit_results/extinction_precursor_analysis.png
```

**验证100代预警窗口**:
```bash
cat model_fit_results/extinction_precursor_analysis.json | jq '.timing'
# 预期看到:
# {
#   "early_warning_window": 100 (左右)
#   "inflection_gen": 6500 (左右)
#   "first_extinction_gen": 6600 (左右)
# }
```

---

### 阶段4: 结果汇总

```bash
# 生成完整发现报告
python3 -c "
import json
from pathlib import Path

results = {
    'experiment': 'Bio-World v18.1',
    'timestamp': '2026-03-09',
    'key_findings': {
        'K_I': json.load(open('model_fit_results/cdi_model_fit.json'))['parameters']['K_I']['value'],
        'cooperation_R2': json.load(open('model_fit_results/cooperation_gate_fit.json'))['fit_quality']['R_squared'],
        'warning_window': json.load(open('model_fit_results/extinction_precursor_analysis.json'))['timing']['early_warning_window'],
    }
}
print(json.dumps(results, indent=2))
"
```

---

## 验证清单

### 核心发现验证

| 发现 | 验证命令 | 预期结果 |
|------|----------|----------|
| K_I ≈ 0.8 | `jq '.parameters.K_I.value' cdi_model_fit.json` | 0.75-0.85 |
| 正反馈项 | `jq '.superlinear_test.b' cdi_model_fit.json` | > 0, p < 0.001 |
| 协作R² | `jq '.fit_quality.R_squared' cooperation_gate_fit.json` | > 0.98 |
| 100代预警 | `jq '.timing.early_warning_window' extinction_precursor_analysis.json` | 80-120 |
| 灭绝连锁 | `jq '.cascade_dynamics.total_extinct' extinction_precursor_analysis.json` | > 100 |

### 三阶段动力学验证

```bash
# 查看阶段识别
python3 -c "
import json
data = json.load(open('model_fit_results/extinction_precursor_analysis.json'))
for event in data['critical_events']:
    print(f\"Gen {event['generation']:4d}: {event['type']}\")
"

# 预期输出:
# Gen 1600: cdi_peak
# Gen 6500: cdi_inflection
# Gen 6600: first_extinction
# Gen 6900: cascade_complete
```

---

## 跨实验验证（P0优先级）

### 不同Seed测试

```bash
# 运行3个不同seed
for SEED in 42 123 456; do
    ./target/release/atlas-hec-v2.1 \
        --seed $SEED \
        --generations 7000 \
        --output ../zeroclaw-labs/v18_1_seed_${SEED}/
done

# 批量分析
for CSV in ../zeroclaw-labs/v18_1_seed_*/evolution.csv; do
    python3 extinction_precursor_detector.py $CSV
done

# 比较预警窗口
python3 -c "
import json, glob
for f in glob.glob('model_fit_results/*/extinction_precursor_analysis.json'):
    data = json.load(open(f))
    seed = f.split('/')[-2]
    window = data['timing']['early_warning_window']
    print(f'{seed}: {window} generations')
"
```

---

## 故障排除

### 问题: K_I拟合值远离0.8

**可能原因**:
- 数据长度不足（需要Gen 100-7000完整数据）
- CDI列名不匹配（应为`avg_cdi`）

**诊断**:
```bash
head -5 $CSV_PATH
cut -d',' -f1,3 $CSV_PATH | head -10
```

### 问题: 预警窗口为null

**可能原因**:
- 灭绝未发生（extinct_count全为0）
- CDI始终低于临界值

**诊断**:
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('$CSV_PATH')
print('Max extinct_count:', df['extinct_count'].max())
print('CDI range:', df['avg_cdi'].min(), '-', df['avg_cdi'].max())
"
```

---

## 数据格式规范

### evolution.csv 必需列

| 列名 | 类型 | 描述 |
|------|------|------|
| generation | int | 代际（100, 200, ...） |
| population | int | 总细胞数 |
| avg_cdi | float | 平均CDI [0,1] |
| avg_collaboration | float | 平均协作强度 [0,1] |
| extinct_count | int | 已灭绝宇宙数 |
| alive_universes | int | 存活宇宙数 |

### 数据质量检查

```bash
python3 << 'EOF'
import pandas as pd

df = pd.read_csv('evolution.csv')

# 检查数据完整性
assert len(df) >= 50, "数据点不足"
assert df['generation'].is_monotonic_increasing, "代际非单调"
assert 0 <= df['avg_cdi'].min() <= df['avg_cdi'].max() <= 1, "CDI超出[0,1]"
assert df['extinct_count'].max() > 0, "无灭绝发生（无法分析连锁）"

print("✅ 数据质量检查通过")
EOF
```

---

## 引用信息

**研究发现**:
```bibtex
@misc{bioworld_v18_discovery,
  title={Bio-World v18.1: Extinction Cascade Dynamics and CDI Early Warning Signals},
  author={Atlas-HEC Team},
  year={2026},
  note={\url{https://github.com/Ectrox-Lab/atlas-hec-v2.1}},
  key_findings={
    three_phase_extinction={plateau, degradation, cascade},
    cdi_early_warning={inflection_point_at_gen_6500, 100_gen_window},
    K_I_saturation={0.8, reproducible},
    cooperation_gate={R2=0.99, gradual_threshold}
  }
}
```

**核心文件版本**:
- `fit_cdi_model_v2.py`: commit 4142c20
- `extinction_precursor_detector.py`: commit 4142c20
- `MODEL_VALIDATION_REPORT_v2.md`: commit 2ba22db

---

## 联系与反馈

**问题报告**: 创建GitHub Issue  
**数据分享**: 实验CSV可上传至`zeroclaw-labs/v18_1_experiments/`

---

*最后更新*: 2026-03-09  
*文档版本*: v1.0
