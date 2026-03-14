#!/bin/bash
#
# E-COMP-003 B': Quick Anti-Leakage Strength Scan
# Test 0.2 vs 0.4, keep everything else constant
#

set -e

WORKSPACE="/tmp/ecomp003_bprime"
COUNT=100
V2_PACKAGE="/tmp/task1_inheritance_package_v2.json"

echo "======================================================================"
echo "E-COMP-003 B': Anti-Leakage Quick Scan"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Testing: strength=0.2 vs strength=0.4"
echo "Constant: mechanism bias=0.6, same package, same seeds"
echo ""

mkdir -p $WORKSPACE

# Condition X: Anti-leakage 0.2 (reduced)
echo "======================================================================"
echo "CONDITION X: Anti-Leakage 0.2 (reduced strength)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 4000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.2 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/condition_X_strength_02

# Condition Y: Anti-leakage 0.4 (original)
echo ""
echo "======================================================================"
echo "CONDITION Y: Anti-Leakage 0.4 (original strength)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 4000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.4 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/condition_Y_strength_04

echo ""
echo "======================================================================"
echo "B' QUICK SCAN: Generation Complete"
echo "======================================================================"
echo ""
echo "Candidate counts:"
echo "  Condition X (0.2): $(ls $WORKSPACE/condition_X_strength_02/candidates/*.json 2>/dev/null | wc -l)"
echo "  Condition Y (0.4): $(ls $WORKSPACE/condition_Y_strength_04/candidates/*.json 2>/dev/null | wc -l)"
echo ""

# Show anti-leakage stats
echo "Anti-leakage application:"
for cond in X Y; do
    strength=$( [ "$cond" = "X" ] && echo "0.2" || echo "0.4" )
    manifest="$WORKSPACE/condition_${cond}_strength_0${strength//./}/manifest.json"
    if [ -f "$manifest" ]; then
        applied=$(cat "$manifest" | jq -r '.anti_leakage_stats.applied // "N/A"')
        total=$(cat "$manifest" | jq -r '.anti_leakage_stats.total_penalty // "N/A"')
        echo "  Condition $cond (strength=$strength): $applied candidates penalized, total penalty=$total"
    fi
done
echo ""

echo "Next: Evaluate with corrected evaluator"
echo "  ./run_ecomp003_bprime_eval.sh"
