#!/bin/bash
#
# L4-v3.0-Expanded Evaluation
# Validate stability of 45% reuse from original L4-v3.0
#

set -e

WORKSPACE="/tmp/l4v3_0_expanded"
RESULTS="/tmp/l4v3_0_expanded_results"
SAMPLE_SIZE=50

echo "======================================================================"
echo "L4-v3.0-EXPANDED EVALUATION"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Purpose: Validate 45% reuse stability from L4-v3.0"
echo ""

mkdir -p $RESULTS

# Evaluate all rounds
for round in a b ablation; do
    round_name=$(echo "$round" | tr '[:lower:]' '[:upper:]')
    echo "======================================================================"
    echo "Evaluating Round $round_name..."
    echo "======================================================================"
    
    python3 /home/admin/atlas-hec-v2.1-repo/superbrain/task2_simulator/task2_evaluator.py \
        --candidates "$WORKSPACE/round_$round/candidates" \
        --output "$RESULTS/round_$round" \
        --sample-size $SAMPLE_SIZE 2>&1 | tail -12
    
    echo ""
done

echo "======================================================================"
echo "VALIDATION RESULTS"
echo "======================================================================"
echo ""

# Comparison with L4-v3.0 reference
echo "Comparison with L4-v3.0 Reference:"
echo "==================================="
echo ""
echo "L4-v3.0 (original, n=100/20):"
echo "  Round A: 40% reuse"
echo "  Round B: 45% reuse"
echo "  Effect: +5pp"
echo ""
echo "L4-v3.0-Expanded (n=300/50):"
echo "--------------------------------"

for round in a b ablation; do
    comp_file="$RESULTS/round_$round/compositionality.json"
    if [ -f "$comp_file" ]; then
        reuse=$(cat "$comp_file" | jq -r '.reuse_rate // "N/A"')
        leakage=$(cat "$comp_file" | jq -r '.leakage // "N/A"')
        echo "  Round $round: Reuse=${reuse}%, Leakage=${leakage}%"
    fi
done

# Calculate effect
A_reuse=$(cat $RESULTS/round_a/compositionality.json 2>/dev/null | jq -r '.reuse_rate // 0')
B_reuse=$(cat $RESULTS/round_b/compositionality.json 2>/dev/null | jq -r '.reuse_rate // 0')

echo ""
if [ "$A_reuse" != "0" ] && [ "$B_reuse" != "0" ]; then
    effect=$(echo "$B_reuse - $A_reuse" | bc -l 2>/dev/null || echo "N/A")
    echo "Mechanism effect (B - A): ${effect}%"
    echo ""
    
    # Stability assessment
    echo "STABILITY ASSESSMENT:"
    echo "===================="
    echo ""
    
    # Check if results match L4-v3.0 pattern
    ref_A=40
    ref_B=45
    ref_effect=5
    
    if (( $(echo "$A_reuse >= 38 && $A_reuse <= 42" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ✅ Round A: Matches reference (~40%)"
    else
        echo "  ⚠️  Round A: Deviates from reference ($A_reuse% vs ~40%)"
    fi
    
    if (( $(echo "$B_reuse >= 43" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ✅ Round B: At or above reference (≥43%)"
    else
        echo "  ⚠️  Round B: Below reference ($B_reuse% vs ~45%)"
    fi
    
    if (( $(echo "$effect >= 3" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ✅ Effect: Positive mechanism bias (≥+3pp)"
    else
        echo "  ❌ Effect: Weak or negative (<+3pp)"
    fi
    
    echo ""
    echo "CONCLUSION:"
    echo "-----------"
    
    if (( $(echo "$A_reuse >= 38 && $A_reuse <= 42 && $B_reuse >= 43 && $effect >= 3" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ✅ STABLE: 45% reuse is real phenomenon"
        echo "     → v3.0 is solid foundation"
        echo "     → v3.1 failure was motif definition error"
        echo "     → Can attempt corrected v3.2"
    elif (( $(echo "$A_reuse < 38 || $B_reuse < 40" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ⚠️  UNSTABLE: 45% was small-sample noise"
        echo "     → Current architecture ceiling lower than expected"
        echo "     → Reassess targets or fundamental approach"
    else
        echo "  ⚠️  AMBIGUOUS: Partial stability"
        echo "     → May need even larger sample"
        echo "     → Or architecture has moderate ceiling (~40%)"
    fi
else
    echo "  (Results pending...)"
fi

echo ""
echo "ARCHIVAL:"
echo "---------"
echo "Results: $RESULTS/"
echo "Reference: L4-v3.0 results for comparison"
