#!/bin/bash

# Bio-World v18 Evolution Dynamics Model Fitting - v2
# 修复ODE数值稳定性问题，使用差分形式

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Bio-World v18 Evolution Dynamics Model Fitting v2            ║"
echo "║  三层最小可拟合模型 (差分形式)                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Find CSV file
CSV_FILE=""
if [ -n "$1" ]; then
    CSV_FILE="$1"
else
    # Try to find evolution.csv
    for pattern in "logs/p3d/evolution.csv" "/home/admin/zeroclaw-labs/v18_1_experiments/*/evolution.csv"; do
        matches=( $pattern )
        if [ -f "${matches[0]}" ]; then
            CSV_FILE="${matches[0]}"
            break
        fi
    done
fi

if [ ! -f "$CSV_FILE" ]; then
    echo "Error: Cannot find evolution.csv"
    echo "Usage: $0 <path/to/evolution.csv>"
    exit 1
fi

echo "✅ Found CSV: $CSV_FILE"
echo ""

# Create output directory
mkdir -p model_fit_results

# ═══════════════════════════════════════════════════════════════
# Layer A: Population / Survival Dynamics
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Layer A: Population / Survival Dynamics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 fit_population_model_v2.py "$CSV_FILE"
echo ""

# ═══════════════════════════════════════════════════════════════
# Layer B: CDI Dynamics (RyanX Innovation Law)
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Layer B: CDI Dynamics (RyanX Innovation Law)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 fit_cdi_model_v2.py "$CSV_FILE"
echo ""

# ═══════════════════════════════════════════════════════════════
# Layer C: Cooperation Gate
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Layer C: Cooperation Gate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 fit_cooperation_gate_v2.py "$CSV_FILE"
echo ""

# ═══════════════════════════════════════════════════════════════
# Summary Report
# ═══════════════════════════════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  MODEL FITTING COMPLETE                                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

OUTPUT_DIR="model_fit_results"

# Check results
if [ -f "$OUTPUT_DIR/population_model_fit.json" ]; then
    echo "✅ Layer A (Population): $OUTPUT_DIR/population_model_fit.json"
fi
if [ -f "$OUTPUT_DIR/cdi_model_fit.json" ]; then
    echo "✅ Layer B (CDI): $OUTPUT_DIR/cdi_model_fit.json"
fi
if [ -f "$OUTPUT_DIR/cooperation_gate_fit.json" ]; then
    echo "✅ Layer C (Cooperation): $OUTPUT_DIR/cooperation_gate_fit.json"
fi

echo ""
echo "Visualizations:"
ls -la $OUTPUT_DIR/*.png 2>/dev/null || echo "  No plots generated"

echo ""
echo "To view results:"
echo "  cat model_fit_results/*.json | jq '.parameters, .fit_quality'"
echo ""
