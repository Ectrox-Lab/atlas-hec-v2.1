#!/bin/bash
#
# L4-v3.1 Experiment Runner
# Larger sample (300/round) + Refined route motif semantics
#

set -e

WORKSPACE="/tmp/l4v3_1_task2"
COUNT=300  # Expanded from 100
V31_PACKAGE="/tmp/task2_inheritance_package_v3_1.json"

echo "======================================================================"
echo "L4-v3.1 EXPERIMENT: Reuse Amplification"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Sample size: $COUNT per round (expanded from 100)"
echo "Package: v3.1-route-motif (refined semantics)"
echo "Anti-leakage: Fixed at 0.2"
echo ""

# Ensure v3.1 package exists
if [ ! -f "$V31_PACKAGE" ]; then
    echo "[SETUP] Generating v3.1 package..."
    python3 /home/admin/atlas-hec-v2.1-repo/superbrain/task2_simulator/generate_v31_package.py
fi

mkdir -p $WORKSPACE

echo "======================================================================"
echo "ROUND A-v3.1: Pure Exploration (baseline, n=$COUNT)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 6000 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_a

echo ""
echo "======================================================================"
echo "ROUND B-v3.1: Refined Mechanism Bias (n=$COUNT)"
echo "======================================================================"
echo "Using v3.1 route-motif package with refined semantics"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 6000 \
    --inheritance-package $V31_PACKAGE \
    --bias-strength 0.7 \
    --anti-leakage-strength 0.2 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/round_b

echo ""
echo "======================================================================"
echo "ABLATION-v3.1: Control Purity (n=$COUNT)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 6000 \
    --inheritance-package $V31_PACKAGE \
    --bias-strength 0.0 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_ablation

echo ""
echo "======================================================================"
echo "L4-v3.1 GENERATION COMPLETE"
echo "======================================================================"
echo ""
echo "Candidate counts:"
for round in a b ablation; do
    count=$(ls $WORKSPACE/round_$round/candidates/*.json 2>/dev/null | wc -l)
    echo "  Round ${round}: $count"
done
echo ""

# Show generation stats
echo "Mechanism bias effect (Round B):"
cat $WORKSPACE/round_b/family_distribution.json | jq '.family_distribution | to_entries | sort_by(.value.count) | reverse | .[:5]' 2>/dev/null || echo "  (distribution analysis available post-completion)"

echo ""
echo "Next: Evaluation with expanded sample"
echo "  ./run_l4v3_1_eval.sh"
