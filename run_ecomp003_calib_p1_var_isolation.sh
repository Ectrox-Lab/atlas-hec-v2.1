#!/bin/bash
#
# E-COMP-003 Phase 1: Variable Isolation
# 4 conditions: A (baseline), B (mech only), C (anti only), D (full)
#

set -e

WORKSPACE="/tmp/ecomp003_calibration/p1_var_isolation"
COUNT=100
V2_PACKAGE="/tmp/task1_inheritance_package_v2.json"

echo "======================================================================"
echo "E-COMP-003 PHASE 1: Variable Isolation"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Conditions: A (baseline), B (mech), C (anti), D (full)"
echo "Per condition: $COUNT candidates"
echo ""

mkdir -p $WORKSPACE

# Ensure v2 package exists
if [ ! -f "$V2_PACKAGE" ]; then
    echo "[ERROR] V2 package not found"
    exit 1
fi

# Condition A: Pure exploration (baseline)
echo "======================================================================"
echo "CONDITION A: Pure Exploration (baseline)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 3000 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/condition_A

# Condition B: Mechanism bias only
echo ""
echo "======================================================================"
echo "CONDITION B: Mechanism Bias Only"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 3000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/condition_B

# Condition C: Anti-leakage only (0.4)
echo ""
echo "======================================================================"
echo "CONDITION C: Anti-Leakage Only (strength=0.4)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 3000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.0 \
    --anti-leakage-strength 0.4 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/condition_C

# Condition D: Full treatment (mechanism + anti-leakage)
echo ""
echo "======================================================================"
echo "CONDITION D: Full Treatment (mechanism + anti-leakage)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 3000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.4 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/condition_D

echo ""
echo "======================================================================"
echo "PHASE 1: Generation Complete"
echo "======================================================================"
echo ""
echo "Candidate counts:"
for cond in A B C D; do
    echo "  Condition $cond: $(ls $WORKSPACE/condition_$cond/candidates/*.json 2>/dev/null | wc -l)"
done
echo ""
echo "Next: Run evaluation"
echo "  ./run_ecomp003_calib_p1_eval.sh"
