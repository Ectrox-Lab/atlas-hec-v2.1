#!/bin/bash
#
# L4-v3.0-Expanded: Validation Run
# Revert to v3.0 config, only expand sample to validate stability
#

set -e

WORKSPACE="/tmp/l4v3_0_expanded"
COUNT=300  # Expanded from 100
V30_PACKAGE="/tmp/task2_inheritance_package_v3.json"

echo "======================================================================"
echo "L4-v3.0-EXPANDED: Validation Run"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Status: REVERT to v3.0 after v3.1 failed refinement"
echo "Sample: $COUNT per round (validate 45% stability)"
echo "Config: v3.0 family-level, anti-leakage 0.2"
echo ""

# Ensure v3.0 package exists
if [ ! -f "$V30_PACKAGE" ]; then
    echo "[SETUP] Generating v3.0 package..."
    python3 << 'EOF'
import json
package = {
    "package_type": "task2_pipeline_orchestration",
    "package_version": "3.0-mechanism-first",
    "stable_mechanisms": {
        "delegation_patterns": [
            {"pattern": "trust_based_handoff", "success_rate": 0.90},
            {"pattern": "adaptive_stage_migration", "success_rate": 0.85}
        ],
        "recovery_sequences": [
            {"sequence": ["detect", "isolate", "reroute", "restore"], "success_rate": 0.82}
        ],
        "trust_priors": {
            "stage_reliability_decay": {"mean": 0.08, "optimal_range": [0.05, 0.12]},
            "stage_recovery_rate": {"mean": 0.06, "optimal_range": [0.04, 0.10]}
        }
    },
    "routing_geometry": {
        "high_value_regions": [
            {"signature": "P2-3_T4_M3-4_D1", "expected_stability": 0.85}
        ]
    },
    "anti_leakage": {
        "enabled": True,
        "strength": 0.2,
        "max_family_distance": 1
    },
    "generator_priors": {
        "triage_preference": 4,
        "pressure_range": [2, 3],
        "memory_range": [2, 3, 4]
    }
}
with open('/tmp/task2_inheritance_package_v3.json', 'w') as f:
    json.dump(package, f, indent=2)
print('Created v3.0 package')
EOF
fi

mkdir -p $WORKSPACE

echo "======================================================================"
echo "ROUND A-v3.0-EXP: Pure Exploration (n=$COUNT)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 7000 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_a

echo ""
echo "======================================================================"
echo "ROUND B-v3.0-EXP: v3.0 Mechanism Bias (n=$COUNT)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 7000 \
    --inheritance-package $V30_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.2 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/round_b

echo ""
echo "======================================================================"
echo "ABLATION-v3.0-EXP: Control Purity (n=$COUNT)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 7000 \
    --inheritance-package $V30_PACKAGE \
    --bias-strength 0.0 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_ablation

echo ""
echo "======================================================================"
echo "L4-v3.0-EXPANDED GENERATION COMPLETE"
echo "======================================================================"
echo ""
echo "Candidate counts:"
for round in a b ablation; do
    count=$(ls $WORKSPACE/round_$round/candidates/*.json 2>/dev/null | wc -l)
    echo "  Round ${round}: $count"
done
echo ""

echo "Key question: Is 45% reuse from L4-v3.0 stable?"
echo ""
echo "Target results:"
echo "  Round A: ~40% reuse"
echo "  Round B: ~45%+ reuse"
echo "  Effect: +5pp or better"
echo "  Leakage: ~0%"
echo ""
echo "Next: Evaluation"
echo "  ./run_l4v3_0_expanded_eval.sh"
