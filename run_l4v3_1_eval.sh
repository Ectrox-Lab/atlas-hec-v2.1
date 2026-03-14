#!/bin/bash
#
# L4-v3.1 Evaluation
# Expanded sample (50/round) for better statistics
#

set -e

WORKSPACE="/tmp/l4v3_1_task2"
RESULTS="/tmp/l4v3_1_task2_results"
SAMPLE_SIZE=50  # Expanded from 20

echo "======================================================================"
echo "L4-v3.1 EVALUATION: Expanded Sample"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Eval sample: $SAMPLE_SIZE per round (expanded from 20)"
echo ""

mkdir -p $RESULTS

# Evaluate each round
for round in a b ablation; do
    round_name=$(echo "$round" | tr '[:lower:]' '[:upper:]')
    echo "======================================================================"
    echo "Evaluating Round $round_name..."
    echo "======================================================================"
    
    python3 /home/admin/atlas-hec-v2.1-repo/superbrain/task2_simulator/task2_evaluator.py \
        --candidates "$WORKSPACE/round_$round/candidates" \
        --output "$RESULTS/round_$round" \
        --sample-size $SAMPLE_SIZE \
        --baseline-completion 0.935 2>&1 | tail -15
    
    echo ""
done

echo "======================================================================"
echo "L4-v3.1 EVALUATION COMPLETE"
echo "======================================================================"
echo ""

# Results comparison
echo "RESULTS COMPARISON:"
echo "==================="
for round in a b ablation; do
    eff_file="$RESULTS/round_$round/effectiveness.json"
    comp_file="$RESULTS/round_$round/compositionality.json"
    
    if [ -f "$eff_file" ] && [ -f "$comp_file" ]; then
        approve=$(cat "$eff_file" | jq -r '.approve_rate // "N/A"')
        reuse=$(cat "$comp_file" | jq -r '.reuse_rate // "N/A"')
        leakage=$(cat "$comp_file" | jq -r '.leakage // "N/A"')
        echo "Round $round: Approve=${approve}%, Reuse=${reuse}%, Leakage=${leakage}%"
    fi
done

echo ""
echo "DECISION GATES:"
echo "==============="
echo ""

# Calculate differences if possible
A_reuse=$(cat $RESULTS/round_a/compositionality.json 2>/dev/null | jq -r '.reuse_rate // 0')
B_reuse=$(cat $RESULTS/round_b/compositionality.json 2>/dev/null | jq -r '.reuse_rate // 0')
A_leakage=$(cat $RESULTS/round_a/compositionality.json 2>/dev/null | jq -r '.leakage // 100')
B_leakage=$(cat $RESULTS/round_b/compositionality.json 2>/dev/null | jq -r '.leakage // 100')

if [ "$A_reuse" != "0" ] && [ "$B_reuse" != "0" ]; then
    effect=$(echo "$B_reuse - $A_reuse" | bc -l 2>/dev/null || echo "N/A")
    echo "Mechanism effect (B - A): ${effect}%"
    echo ""
    
    # Decision logic
    echo "Assessment:"
    
    # Reuse target
    if (( $(echo "$B_reuse >= 55" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ✅ Reuse target: PASS ($B_reuse% >= 55%)"
    elif (( $(echo "$B_reuse >= 50" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ⚠️  Reuse target: PARTIAL ($B_reuse% >= 50%)"
    else
        echo "  ❌ Reuse target: NEED REDESIGN ($B_reuse% < 50%)"
    fi
    
    # Mechanism effect
    if (( $(echo "$effect >= 10" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ✅ Mechanism effect: PASS (${effect}% >= +10pp)"
    elif (( $(echo "$effect >= 7" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ⚠️  Mechanism effect: PARTIAL (${effect}% >= +7pp)"
    else
        echo "  ❌ Mechanism effect: WEAK (${effect}% < +7pp)"
    fi
    
    # Leakage constraint
    if (( $(echo "$B_leakage <= 2" | bc -l 2>/dev/null || echo 0) )); then
        echo "  ✅ Leakage constraint: PASS ($B_leakage% <= 2%)"
    else
        echo "  ⚠️  Leakage constraint: ELEVATED ($B_leakage% > 2%)"
    fi
else
    echo "  (Awaiting results...)"
fi

echo ""
echo "Overall:"
echo "--------"
echo "PASS: Reuse ≥55% AND Effect ≥+10pp AND Leakage ≤2%"
echo "PARTIAL: Reuse 50-55% OR Effect +7-10pp"
echo "REDESIGN: Reuse <50% AND Effect <+7pp"
