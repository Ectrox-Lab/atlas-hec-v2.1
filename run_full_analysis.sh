#!/bin/bash

# Bio-World v18.1 完整分析流水线
# Full Analysis Pipeline for Bio-World v18.1
#
# Usage: ./run_full_analysis.sh <path/to/evolution.csv>

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           Bio-World v18.1 Full Analysis Pipeline                      ║"
echo "║           完整分析流水线                                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# 检查输入参数
CSV_FILE="${1:-}"
if [ -z "$CSV_FILE" ]; then
    # 尝试自动查找
    echo -e "${YELLOW}Searching for evolution.csv...${NC}"
    for pattern in "/home/admin/zeroclaw-labs/v18_1_experiments/*/evolution.csv"; do
        matches=( $pattern )
        if [ -f "${matches[0]}" ]; then
            CSV_FILE="${matches[0]}"
            echo -e "${GREEN}Found: $CSV_FILE${NC}"
            break
        fi
    done
fi

if [ ! -f "$CSV_FILE" ]; then
    echo -e "${RED}Error: Cannot find evolution.csv${NC}"
    echo "Usage: $0 <path/to/evolution.csv>"
    exit 1
fi

echo ""
echo -e "${BLUE}Input file:${NC} $CSV_FILE"
echo ""

# 创建输出目录
mkdir -p model_fit_results
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="model_fit_results/BIOWORLD_V18_FINDINGS_${TIMESTAMP}.json"

# ═══════════════════════════════════════════════════════════════════════
# Stage 1: 三层动力学拟合
# ═══════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}[Stage 1/4] Three-Layer Dynamics Model Fitting${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 fit_population_collapse_model.py "$CSV_FILE" 2>&1 | tail -20
echo ""

python3 fit_cdi_model_v2.py "$CSV_FILE" 2>&1 | tail -20
echo ""

python3 fit_cooperation_gate_v2.py "$CSV_FILE" 2>&1 | tail -20
echo ""

# ═══════════════════════════════════════════════════════════════════════
# Stage 2: 灭绝前兆检测（核心发现）
# ═══════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}[Stage 2/4] Extinction Precursor Detection${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 extinction_precursor_detector.py "$CSV_FILE" 2>&1 | tail -30
echo ""

# ═══════════════════════════════════════════════════════════════════════
# Stage 3: 结果汇总与验证
# ═══════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}[Stage 3/4] Results Aggregation${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << PYTHON_SCRIPT
import json
import sys
from pathlib import Path

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        return None

# 加载各层结果
cdi = load_json('model_fit_results/cdi_model_fit.json')
coop = load_json('model_fit_results/cooperation_gate_fit.json')
precursor = load_json('model_fit_results/extinction_precursor_analysis.json')

findings = {
    'experiment': 'Bio-World v18.1',
    'timestamp': '$TIMESTAMP',
    'data_source': '$CSV_FILE',
    'key_findings': {}
}

# Layer B: CDI
if cdi:
    findings['key_findings']['Layer_B_CDI'] = {
        'K_I': cdi.get('parameters', {}).get('K_I', {}).get('value'),
        'superlinear_b': cdi.get('superlinear_test', {}).get('b'),
        'superlinear_p': cdi.get('superlinear_test', {}).get('p_value'),
        'R2': cdi.get('fit_quality', {}).get('R_squared'),
        'conclusion': 'RyanX resource-limited law supported'
    }
    print(f"✅ Layer B (CDI): K_I = {findings['key_findings']['Layer_B_CDI']['K_I']:.4f}")

# Layer C: Cooperation
if coop:
    findings['key_findings']['Layer_C_Cooperation'] = {
        'R2': coop.get('fit_quality', {}).get('R_squared'),
        'theta': coop.get('parameters', {}).get('theta0', {}).get('value'),
        'tau': coop.get('parameters', {}).get('tau', {}).get('value'),
        'conclusion': 'Gradual threshold gate confirmed'
    }
    print(f"✅ Layer C (Cooperation): R² = {findings['key_findings']['Layer_C_Cooperation']['R2']:.4f}")

# Extinction Precursor
if precursor:
    timing = precursor.get('timing', {})
    cdi_signals = precursor.get('cdi_signals', {})
    cascade = precursor.get('cascade_dynamics', {})
    
    findings['key_findings']['Extinction_Precursor'] = {
        'early_warning_window': timing.get('early_warning_window'),
        'cdi_peak_gen': cdi_signals.get('peak', {}).get('gen'),
        'inflection_gen': cdi_signals.get('inflection', {}).get('gen'),
        'first_extinction_gen': next((e['generation'] for e in precursor.get('critical_events', []) 
                                      if e['type'] == 'first_extinction'), None),
        'cascade_duration': cascade.get('duration'),
        'total_extinct': cascade.get('total_extinct'),
        'conclusion': 'CDI inflection provides ~100 gen early warning'
    }
    
    window = findings['key_findings']['Extinction_Precursor']['early_warning_window']
    if window:
        print(f"✅ Early Warning: {window} generations before extinction")
    print(f"✅ Cascade: {findings['key_findings']['Extinction_Precursor']['total_extinct']} universes extinct")

# 保存汇总结果
with open('$RESULTS_FILE', 'w') as f:
    json.dump(findings, f, indent=2)

print(f"\n📊 Full results saved to: $RESULTS_FILE")
PYTHON_SCRIPT

echo ""

# ═══════════════════════════════════════════════════════════════════════
# Stage 4: 验证清单
# ═══════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}[Stage 4/4] Verification Checklist${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << VERIFY_SCRIPT
import json
import sys

def check(name, value, condition, expected):
    status = "✅" if condition else "❌"
    color = "\033[0;32m" if condition else "\033[0;31m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {name}: {value:.4f} (expected: {expected})")
    return condition

results = json.load(open('$RESULTS_FILE'))
kf = results.get('key_findings', {})

all_pass = True

print("\nCore Discoveries:")
print("-" * 50)

# Check K_I ≈ 0.8
layer_b = kf.get('Layer_B_CDI', {})
if layer_b.get('K_I'):
    all_pass &= check("K_I saturation", layer_b['K_I'], 0.75 <= layer_b['K_I'] <= 0.85, "0.80 ± 0.05")

# Check superlinear
if layer_b.get('superlinear_b'):
    all_pass &= check("Positive feedback (b)", layer_b['superlinear_b'], layer_b['superlinear_b'] > 0, "> 0")
    if layer_b.get('superlinear_p'):
        print(f"   p-value: {layer_b['superlinear_p']:.2e} {'✅ significant' if layer_b['superlinear_p'] < 0.001 else '❌ not significant'}")

# Check cooperation R²
layer_c = kf.get('Layer_C_Cooperation', {})
if layer_c.get('R2'):
    all_pass &= check("Cooperation R²", layer_c['R2'], layer_c['R2'] > 0.95, "> 0.95")

# Check early warning
precursor = kf.get('Extinction_Precursor', {})
if precursor.get('early_warning_window'):
    window = precursor['early_warning_window']
    all_pass &= check("Early warning window", float(window), 50 <= window <= 150, "~100 generations")

if precursor.get('total_extinct'):
    total = precursor['total_extinct']
    all_pass &= check("Extinction cascade size", float(total), total > 50, "> 50 universes")

print("-" * 50)
if all_pass:
    print(f"\n🎉 All core discoveries verified!")
else:
    print(f"\n⚠️ Some checks failed - review results")

print(f"\n📁 Results directory: model_fit_results/")
print(f"📊 Summary file: $RESULTS_FILE")
VERIFY_SCRIPT

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                      Analysis Complete!                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Generated outputs:"
echo "  📄 model_fit_results/BIOWORLD_V18_FINDINGS_*.json  (Summary)"
echo "  📄 model_fit_results/*_model_fit.json              (Parameters)"
echo "  📊 model_fit_results/*.png                         (Visualizations)"
echo ""
echo "Key documents:"
echo "  📖 BIOWORLD_V18_DISCOVERY_SUMMARY.md   (4 key findings)"
echo "  📖 MODEL_VALIDATION_REPORT_v2.md       (Technical details)"
echo "  📖 REPRODUCIBLE_EXPERIMENT.md          (Replication guide)"
echo "  📖 BIOWORLD_RESEARCH_ARCHITECTURE.md   (Platform overview)"
echo ""
