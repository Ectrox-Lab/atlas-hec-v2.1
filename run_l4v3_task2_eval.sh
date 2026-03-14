#!/bin/bash
#
# L4-v3 Task-2 Evaluation
# Evaluate candidates on multi-stage pipeline simulator
#

set -e

WORKSPACE="/tmp/l4v3_task2"
RESULTS="/tmp/l4v3_task2_results"
SAMPLE_SIZE=20

echo "======================================================================"
echo "L4-v3 TASK-2 EVALUATION"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo ""

mkdir -p $RESULTS

# Evaluate each round
for round in a b ablation; do
    round_name=$(echo "$round" | tr '[:lower:]' '[:upper:]')
    echo "======================================================================"
    echo "Evaluating Round $round_name..."
    echo "======================================================================"
    
    # Use Task-2 evaluator
    python3 /home/admin/atlas-hec-v2.1-repo/superbrain/task2_simulator/task2_evaluator.py \
        --candidates "$WORKSPACE/round_$round/candidates" \
        --output "$RESULTS/round_$round" \
        --sample-size $SAMPLE_SIZE \
        --baseline-completion 0.935 2>&1 | tail -15
    
    echo ""
done

echo "======================================================================"
echo "TASK-2 EVALUATION COMPLETE"
echo "======================================================================"
echo ""

# Comparison
echo "RESULTS COMPARISON:"
echo "==================="
for round in a b ablation; do
    result_file="$RESULTS/round_$round/effectiveness.json"
    if [ -f "$result_file" ]; then
        approve=$(cat "$result_file" | jq -r '.approve_rate // "N/A"')
        reuse=$(cat "$result_file" | jq -r '.reuse_rate // "N/A"')
        echo "Round $round: Approve=${approve}%, Reuse=${reuse}%"
    fi
done

echo ""
echo "Decision criteria:"
echo "  - Round B > Round A + 15%: Mechanism bias working"
echo "  - Reuse > 60%: Compositionality achieved"
echo "  - Leakage < 10%: Anti-leakage effective"
