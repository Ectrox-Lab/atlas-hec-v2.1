#!/bin/bash
#
# E-COMP-003 Gate-1: Large Sample Validation
# Generate 450 candidates (150 per round) for mechanism map stabilization
#

set -e

WORKSPACE="/tmp/ecomp003_gate1"
COUNT=150
V2_PACKAGE="/tmp/task1_inheritance_package_v2.json"

echo "======================================================================"
echo "E-COMP-003 GATE-1: Large Sample Validation"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Target: n=150 per round, stratified to n=30 for Mainline"
echo "Workspace: $WORKSPACE"
echo ""

# Create workspace
mkdir -p $WORKSPACE

# Ensure v2 package exists
if [ ! -f "$V2_PACKAGE" ]; then
    echo "[ERROR] V2 package not found at $V2_PACKAGE"
    echo "Run: python3 -c '...create package...' first"
    exit 1
fi

# Round A-v3: Pure exploration (baseline)
echo "======================================================================"
echo "ROUND A-v3: Pure Exploration (baseline, seed=2000)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 2000 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_a_v3

# Round B-v3: Mechanism bias with current best config
echo ""
echo "======================================================================"
echo "ROUND B-v3: Mechanism Bias (current best, seed=2000)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 2000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.4 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/round_b_v3

# Ablation-v3: Control purity
echo ""
echo "======================================================================"
echo "ABLATION-v3: Control Purity (seed=2000)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 2000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.0 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_ablation_v3

echo ""
echo "======================================================================"
echo "E-COMP-003 GATE-1: Candidate Generation Complete"
echo "======================================================================"
echo ""
echo "Candidate counts:"
echo "  Round A-v3: $(ls $WORKSPACE/round_a_v3/candidates/*.json 2>/dev/null | wc -l)"
echo "  Round B-v3: $(ls $WORKSPACE/round_b_v3/candidates/*.json 2>/dev/null | wc -l)"
echo "  Ablation-v3: $(ls $WORKSPACE/round_ablation_v3/candidates/*.json 2>/dev/null | wc -l)"
echo ""
echo "Next: Run ./run_ecomp003_gate1_eval.sh for Mainline evaluation"
