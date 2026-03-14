#!/bin/bash
#
# E-COMP-003 Phase 1: Evaluation
# Evaluate all 4 conditions with stratified sampling
#

set -e

WORKSPACE="/tmp/ecomp003_calibration/p1_var_isolation"
RESULTS="/tmp/ecomp003_calibration/p1_results"
SAMPLE_SIZE=20

echo "======================================================================"
echo "E-COMP-003 PHASE 1: Evaluation"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Sample size: $SAMPLE_SIZE per condition"
echo ""

mkdir -p $RESULTS

# Create symlinks for evaluator
for cond in A B C D; do
    if [ -d "$WORKSPACE/condition_$cond" ]; then
        ln -sf "$WORKSPACE/condition_$cond" "$WORKSPACE/round_${cond,,}"
    fi
done

# Evaluate each condition
for cond in A B C D; do
    echo "======================================================================"
    echo "Evaluating Condition $cond..."
    echo "======================================================================"
    
    cond_lower=$(echo "$cond" | tr '[:upper:]' '[:lower:]')
    
    python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/task1_l4v2_evaluate.py \
        --input-dir "$WORKSPACE" \
        --output-dir "$RESULTS/condition_$cond" \
        --sample-size $SAMPLE_SIZE \
        --baseline 0.075 2>&1 | grep -E "(Approve rate|Reuse rate|Leakage|Round)" | tail -10
    
    echo ""
done

echo "======================================================================"
echo "PHASE 1: Evaluation Complete"
echo "======================================================================"
echo ""
echo "Results location: $RESULTS"
echo ""

# Quick comparison
echo "Quick Comparison:"
echo "================="
for cond in A B C D; do
    eff_file="$RESULTS/condition_$cond/mainline_effectiveness_summary.json"
    if [ -f "$eff_file" ]; then
        approve=$(cat "$eff_file" | jq -r '.results["Round '$(echo "$cond" | tr '[:lower:]' '[:upper:]')'"].approve_rate // "N/A"')
        echo "  Condition $cond: Approve rate = $approve%"
    fi
done

echo ""
echo "Next: Run analysis"
echo "  python3 superbrain/module_routing/calibration_analyzer.py"
