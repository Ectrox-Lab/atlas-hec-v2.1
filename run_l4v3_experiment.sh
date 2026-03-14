#!/bin/bash
#
# L4-v3 Experiment Runner
# Task-2: Multi-stage pipeline scheduling with mechanism-first inheritance
#

set -e

WORKSPACE="/tmp/l4v3_task2"
COUNT=100
V3_PACKAGE="/tmp/task2_inheritance_package_v3.json"

echo "======================================================================"
echo "L4-v3 EXPERIMENT: Task-2 Multi-Stage Pipeline"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Task: Multi-stage pipeline scheduling"
echo "Inheritance: Mechanism-first v3"
echo "Anti-leakage: Fixed at 0.2"
echo ""

# Check Task-2 simulator exists
if [ ! -f "/home/admin/atlas-hec-v2.1-repo/superbrain/task2_simulator/pipeline_simulator.py" ]; then
    echo "[ERROR] Task-2 simulator not found"
    echo "Build: superbrain/task2_simulator/pipeline_simulator.py first"
    exit 1
fi

# Generate v3 package if not exists
if [ ! -f "$V3_PACKAGE" ]; then
    echo "[SETUP] Creating Task-2 v3 mechanism package..."
    python3 << 'EOF'
import json

package = {
    "package_type": "task2_pipeline_orchestration",
    "package_version": "3.0-mechanism-first",
    "timestamp": "2026-03-14T17:00:00+08:00",
    "stable_mechanisms": {
        "stage_handoff_patterns": [
            {"pattern": "trust_based_handoff", "success_rate": 0.90, "context": "stable_executor"},
            {"pattern": "adaptive_stage_migration", "success_rate": 0.85, "context": "degraded_stage"}
        ],
        "recovery_sequences": [
            {"sequence": ["detect_stage_failure", "isolate_stage", "reroute_tasks", "restore_pipeline"],
             "context": "stage_collapse", "success_rate": 0.82},
            {"sequence": ["reduce_injection_rate", "stabilize_queue", "gradual_recovery"],
             "context": "pressure_cascade", "success_rate": 0.78}
        ],
        "trust_priors": {
            "stage_reliability_decay": {"mean": 0.08, "std": 0.02, "optimal_range": [0.05, 0.12]},
            "stage_recovery_rate": {"mean": 0.06, "std": 0.02, "optimal_range": [0.04, 0.10]}
        }
    },
    "routing_geometry": {
        "high_value_regions": [
            {"signature": "P2-3_T4_M3-4_D1", "expected_stability": 0.85, "mechanisms": ["trust_handoff", "adaptive_migration"]},
            {"signature": "P2_T3-4_M3_D1", "expected_stability": 0.80, "mechanisms": ["conservative_handoff"]}
        ],
        "avoid_regions": [
            {"signature": "P1_T2_M1-2", "risk": "underutilization"},
            {"signature": "P4_T5_M5", "risk": "cascade_failure"}
        ]
    },
    "anti_leakage": {
        "enabled": True,
        "strength": 0.2,
        "max_family_distance": 1,
        "untested_pressure": [1, 4],
        "untested_triage": [2, 5],
        "penalty_per_step": 0.15
    },
    "generator_priors": {
        "triage_preference": 4,  # T4 prior
        "pressure_range": [2, 3],
        "memory_range": [2, 3, 4],
        "delegation": 1
    }
}

with open('/tmp/task2_inheritance_package_v3.json', 'w') as f:
    json.dump(package, f, indent=2)

print('Created Task-2 v3 mechanism package')
EOF
fi

mkdir -p $WORKSPACE

echo ""
echo "======================================================================"
echo "ROUND A-v3: Pure Exploration (baseline)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 5000 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_a

echo ""
echo "======================================================================"
echo "ROUND B-v3: Mechanism-First Inheritance"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 5000 \
    --inheritance-package $V3_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.2 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/round_b

echo ""
echo "======================================================================"
echo "ABLATION-v3: Control Purity"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 5000 \
    --inheritance-package $V3_PACKAGE \
    --bias-strength 0.0 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_ablation

echo ""
echo "======================================================================"
echo "L4-v3 GENERATION COMPLETE"
echo "======================================================================"
echo ""
echo "Candidate counts:"
for round in a b ablation; do
    count=$(ls $WORKSPACE/round_$round/candidates/*.json 2>/dev/null | wc -l)
    echo "  Round ${round}: $count"
done
echo ""
echo "Next: Task-2 evaluation"
echo "  ./run_l4v3_task2_eval.sh"
