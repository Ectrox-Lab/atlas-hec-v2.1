#!/bin/bash
#
# E-COMP-003 B': Evaluation for 0.2 vs 0.4
# Fixed to correctly evaluate each condition
#

set -e

WORKSPACE="/tmp/ecomp003_bprime"
RESULTS="/tmp/ecomp003_bprime_results"
SAMPLE_SIZE=20

echo "======================================================================"
echo "E-COMP-003 B': Evaluation (0.2 vs 0.4)"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo ""

mkdir -p $RESULTS

# Evaluate Condition X (0.2)
echo "======================================================================"
echo "Evaluating Condition X: Anti-Leakage 0.2"
echo "======================================================================"

# Create temp structure for evaluator
temp_input="$RESULTS/temp_input_X"
mkdir -p "$temp_input"
ln -sf "$WORKSPACE/condition_X_strength_02" "$temp_input/round_b"

python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/task1_l4v2_evaluate.py \
    --input-dir "$temp_input" \
    --output-dir "$RESULTS/condition_X" \
    --sample-size $SAMPLE_SIZE \
    --baseline 0.075 2>&1 | grep -E "(Approve rate|Reuse rate|Leakage|F_P3T4M4)" | tail -10

echo ""

# Evaluate Condition Y (0.4)
echo "======================================================================"
echo "Evaluating Condition Y: Anti-Leakage 0.4"
echo "======================================================================"

temp_input="$RESULTS/temp_input_Y"
mkdir -p "$temp_input"
ln -sf "$WORKSPACE/condition_Y_strength_04" "$temp_input/round_b"

python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/task1_l4v2_evaluate.py \
    --input-dir "$temp_input" \
    --output-dir "$RESULTS/condition_Y" \
    --sample-size $SAMPLE_SIZE \
    --baseline 0.075 2>&1 | grep -E "(Approve rate|Reuse rate|Leakage|F_P3T4M4)" | tail -10

echo ""
echo "======================================================================"
echo "B' EVALUATION COMPLETE"
echo "======================================================================"
echo ""

# Extract and compare key metrics
echo "QUICK COMPARISON:"
echo "================="

for cond in X Y; do
    strength=$( [ "$cond" = "X" ] && echo "0.2" || echo "0.4" )
    eff_file="$RESULTS/condition_$cond/mainline_effectiveness_summary.json"
    comp_file="$RESULTS/condition_$cond/mainline_compositionality_summary.json"
    
    if [ -f "$eff_file" ] && [ -f "$comp_file" ]; then
        approve=$(cat "$eff_file" | jq -r '.results["Round B"].approve_rate // "N/A"')
        reuse=$(cat "$comp_file" | jq -r '.results["Round B"].reuse_rate // "N/A"')
        leakage=$(cat "$comp_file" | jq -r '.results["Round B"].leakage // "N/A"')
        f_p3t4m4=$(cat "$comp_file" | jq -r '.results["Round B"].f_p3t4m4_share // "N/A"')
        
        echo ""
        echo "Condition $cond (strength=$strength):"
        echo "  Approve rate: ${approve}%"
        echo "  Reuse rate: ${reuse}%"
        echo "  Leakage: ${leakage}%"
        echo "  F_P3T4M4 share: ${f_p3t4m4}%"
    fi
done

echo ""
echo "Decision Gate:"
echo "=============="

# Simple comparison logic
echo "If 0.2 shows:"
echo "  - Higher approve rate"
echo "  - Similar or better reuse"
echo "  - Still low leakage"
echo "  - Comparable F_P3T4M4 share"
echo ""
echo "→ CONCLUSION: Anti-leakage 0.4 too strong, use 0.2 for L4-v3"
echo ""
echo "If 0.2 ≈ 0.4:"
echo "→ CONCLUSION: Not strength issue, consider other factors"
