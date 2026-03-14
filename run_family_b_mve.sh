#!/bin/bash
#
# Family B MVE: 7-Day Minimal Viable Experiment
# Day 5-6: Execution (300 candidates per round)
#

set -e

WORKSPACE="/tmp/family_b_mve"
COUNT=300

echo "======================================================================"
echo "FAMILY B MVE: Contract Composition Experiment"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Sample: $COUNT candidates per round"
echo "Strategy: Contract composition"
echo ""

mkdir -p $WORKSPACE

# Generate contracts reference
echo "[SETUP] Exporting contracts..."
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/family_b/contracts.py > /dev/null

echo ""
echo "======================================================================"
echo "ROUND A: Pure Contract Composition (baseline)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/family_b/generator.py \
    --count $COUNT \
    --seed 8000 \
    --strategy composition \
    --output $WORKSPACE/round_a

echo ""
echo "======================================================================"
echo "ROUND B: Full Stack (all 3 contracts)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/family_b/generator.py \
    --count $COUNT \
    --seed 8000 \
    --strategy full_stack \
    --output $WORKSPACE/round_b

echo ""
echo "======================================================================"
echo "ABLATION: Random (no contract guidance)"
echo "======================================================================"
# For ablation, use standard generator without contract bias
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 8000 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_ablation

echo ""
echo "======================================================================"
echo "FAMILY B MVE: Generation Complete"
echo "======================================================================"
echo ""
echo "Candidate counts:"
for round in a b ablation; do
    count=$(ls $WORKSPACE/round_$round/*.json 2>/dev/null | grep -c "\.json" || echo 0)
    echo "  Round ${round}: $count"
done
echo ""
echo "Next: Contract verification on Task-2"
echo "  ./run_family_b_eval.sh"
