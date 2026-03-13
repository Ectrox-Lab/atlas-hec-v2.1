#!/bin/bash
# Bio-World v18 演化动力学模型拟合脚本
# 运行三层最小模型拟合

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Bio-World v18 Evolution Dynamics Model Fitting               ║"
echo "║  三层最小可拟合模型                                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 查找CSV文件
CSV_FILE=""

# 检查P3D日志
if [ -f "source/logs/p3d/evolution.csv" ]; then
    CSV_FILE="source/logs/p3d/evolution.csv"
    echo "✅ Found P3D evolution.csv"
fi

# 检查v18实验
if [ -z "$CSV_FILE" ]; then
    V18_CSV=$(find /home/admin/zeroclaw-labs/v18_1_experiments -name "evolution.csv" 2>/dev/null | head -1)
    if [ ! -z "$V18_CSV" ]; then
        CSV_FILE="$V18_CSV"
        echo "✅ Found v18.1 evolution.csv: $CSV_FILE"
    fi
fi

if [ -z "$CSV_FILE" ]; then
    echo "❌ Error: No evolution.csv found"
    echo "Please provide path: ./run_model_fitting.sh <path/to/evolution.csv>"
    exit 1
fi

echo ""
echo "Using CSV: $CSV_FILE"
echo ""

# 创建输出目录
mkdir -p model_fit_results

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Layer A: Population / Survival Dynamics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 fit_population_model.py "$CSV_FILE" || echo "⚠️ Population model fitting failed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Layer B: CDI Dynamics (RyanX Innovation Law)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 fit_cdi_model.py "$CSV_FILE" || echo "⚠️ CDI model fitting failed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Layer C: Cooperation Gate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 fit_cooperation_gate.py "$CSV_FILE" || echo "⚠️ Cooperation gate fitting failed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Generating Summary Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 生成综合报告
python3 << 'EOF'
import json
from pathlib import Path

output_dir = Path('model_fit_results')

report = []
report.append("="*70)
report.append("EVOLUTION DYNAMICS MODEL FITTING - SUMMARY REPORT")
report.append("="*70)
report.append("")

# Layer A
if (output_dir / 'population_model_fit.json').exists():
    with open(output_dir / 'population_model_fit.json') as f:
        data = json.load(f)
    report.append("Layer A: Population Dynamics")
    report.append("-" * 40)
    report.append(f"R² = {data['fit_quality']['R_squared']:.4f}")
    report.append(f"RMSE = {data['fit_quality']['RMSE']:.2f}")
    report.append("")
    report.append("Key parameters:")
    for name, info in data['parameters'].items():
        report.append(f"  {name}: {info['value']:.6f} ({info['description']})")
    report.append("")

# Layer B
if (output_dir / 'cdi_model_fit.json').exists():
    with open(output_dir / 'cdi_model_fit.json') as f:
        data = json.load(f)
    report.append("Layer B: CDI Dynamics (RyanX Innovation Law)")
    report.append("-" * 40)
    report.append(f"R² = {data['fit_quality']['R_squared']:.4f}")
    report.append(f"RMSE = {data['fit_quality']['RMSE']:.4f}")
    report.append(f"K_I (CDI上限) = {data['parameters']['K_I']['value']:.4f}")
    report.append("")
    
    if 'superlinear_check' in data and 'error' not in data['superlinear_check']:
        sl = data['superlinear_check']
        report.append(f"Superlinear check: b = {sl['b']:.6f}, R² = {sl['R_squared']:.4f}")
        report.append(f"Is superlinear: {sl['is_superlinear']}")
    report.append("")

# Layer C
if (output_dir / 'cooperation_gate_fit.json').exists():
    with open(output_dir / 'cooperation_gate_fit.json') as f:
        data = json.load(f)
    report.append("Layer C: Cooperation Gate")
    report.append("-" * 40)
    report.append(f"R² = {data['fit_quality']['R_squared']:.4f}")
    report.append(f"RMSE = {data['fit_quality']['RMSE']:.4f}")
    report.append("")
    report.append(f"Base threshold θ₀ = {data['parameters']['theta_0']['value']:.4f}")
    report.append(f"Temperature τ = {data['parameters']['tau']['value']:.4f}")
    report.append("")

report.append("="*70)
report.append("Output files:")
report.append("  - model_fit_results/population_model_fit.json")
report.append("  - model_fit_results/population_model_fit.png")
report.append("  - model_fit_results/cdi_model_fit.json")
report.append("  - model_fit_results/cdi_model_fit.png")
report.append("  - model_fit_results/cooperation_gate_fit.json")
report.append("  - model_fit_results/cooperation_gate_fit.png")
report.append("="*70)

report_text = "\n".join(report)
print(report_text)

# 保存报告
with open(output_dir / 'MODEL_VALIDATION_REPORT.md', 'w') as f:
    f.write(report_text)
print("\n✅ Report saved to: model_fit_results/MODEL_VALIDATION_REPORT.md")
EOF

echo ""
echo "✅ All fitting complete!"
echo ""
echo "Results location: model_fit_results/"
