#!/bin/bash
#
# L4-v2 Experiment Runner
# Fast Genesis with Mechanism-Level Inheritance + Anti-Leakage Bias
#

set -e

WORKSPACE="/tmp/atlas_l4v2"
COUNT=150
V2_PACKAGE="/tmp/task1_inheritance_package_v2.json"

echo "======================================================================"
echo "ATLAS L4-v2 Experiment Runner"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Count per round: $COUNT"
echo "V2 Package: $V2_PACKAGE"
echo ""

# Create workspace
mkdir -p $WORKSPACE

# Generate v2 package if not exists
if [ ! -f "$V2_PACKAGE" ]; then
    echo "[SETUP] Creating v2 mechanism package..."
    python3 << 'EOF'
import json

package = {
    'package_type': 'task1_orchestration',
    'package_version': '2.1-mechanism',
    'timestamp': '2026-03-13T17:45:00+08:00',
    'stable_mechanisms': {
        'delegation_patterns': [
            {'pattern': 'adaptive_migration', 'success_rate': 0.92, 'context': 'general'},
            {'pattern': 'trust_based_routing', 'success_rate': 0.88, 'context': 'general'},
            {'pattern': 'pressure_threshold_based', 'success_rate': 0.85, 'context': 'p2p3'}
        ],
        'recovery_sequences': [
            {'sequence': ['detect_fault', 'isolate_node', 'redistribute_tasks', 'restore_trust'],
             'context': 'high_load_scenario', 'success_rate': 0.8},
            {'sequence': ['reduce_pressure', 'stabilize_triage', 'restore_memory'],
             'context': 'pressure_cascade', 'success_rate': 0.82}
        ],
        'trust_update_priors': {
            'decay_rate': {'mean': 0.1, 'std': 0.03, 'optimal_range': [0.05, 0.15]},
            'recovery_rate': {'mean': 0.05, 'std': 0.02, 'optimal_range': [0.03, 0.08]}
        }
    },
    'blocked_motifs': [
        {'motif': 'rapid_switching', 'penalty': 0.5, 'symptoms': ['high_variance', 'oscillation']},
        {'motif': 'migration_thrashing', 'penalty': 0.4, 'symptoms': ['frequent_migrations', 'low_throughput']},
        {'motif': 'trust_collapse_cascade', 'penalty': 0.6, 'symptoms': ['sudden_trust_drop', 'recovery_failure']},
        {'motif': 'pressure_cascade_uncontrolled', 'penalty': 0.5, 'symptoms': ['p4', 'high_memory_drain']}
    ],
    'route_constraints': {
        'pressure_range': {'min': 2, 'max': 3, 'optimal': [2, 3], 'penalty_outside': 0.2},
        'triage_range': {'min': 3, 'max': 4, 'optimal': [3, 4], 'penalty_outside': 0.15},
        'memory_range': {'min': 2, 'max': 4, 'optimal': [2, 3, 4], 'penalty_outside': 0.1}
    },
    'anti_expansion_hints': {
        'untested_pressure': [1, 4],
        'untested_triage': [2, 5],
        'untested_memory': [1, 5],
        'penalty_per_step': 0.15,
        'max_family_distance': 1,
        'novelty_threshold': 0.3
    },
    'family_mechanism_map': {
        'F_P3T4M4': {
            'stability_score': 0.92,
            'route_signature': {'P': 3, 'T': 4, 'M': 4},
            'mechanisms': ['trust_based_routing', 'adaptive_migration'],
            'context': 'high_throughput'
        },
        'F_P2T4M3': {
            'stability_score': 0.88,
            'route_signature': {'P': 2, 'T': 4, 'M': 3},
            'mechanisms': ['pressure_threshold_based', 'trust_based_routing'],
            'context': 'balanced_load'
        },
        'F_P3T4M3': {
            'stability_score': 0.85,
            'route_signature': {'P': 3, 'T': 4, 'M': 3},
            'mechanisms': ['adaptive_migration'],
            'context': 'mixed'
        },
        'F_P2T3M2': {
            'stability_score': 0.82,
            'route_signature': {'P': 2, 'T': 3, 'M': 2},
            'mechanisms': ['pressure_threshold_based'],
            'context': 'low_memory'
        }
    },
    'generator_priors': {
        'pressure': [2, 3],
        'triage': [3, 4],
        'memory': [2, 3, 4],
        'blocked_families': [],
        'preferred_families': ['F_P3T4M4', 'F_P2T4M3', 'F_P3T4M3']
    }
}

with open('/tmp/task1_inheritance_package_v2.json', 'w') as f:
    json.dump(package, f, indent=2)

print('Created v2 mechanism package')
EOF
fi

# Run Round A: Pure exploration (anti_leakage=0.0)
echo "======================================================================"
echo "ROUND A: Pure Exploration (anti_leakage=0.0)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 1000 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_a

# Run Round B: Mechanism bias + anti-leakage
echo ""
echo "======================================================================"
echo "ROUND B: Mechanism Bias + Anti-Leakage (strength=0.4)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 1000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.6 \
    --anti-leakage-strength 0.4 \
    --max-family-distance 1 \
    --prefer-stable-paths \
    --penalize-unjustified-expansion \
    --output $WORKSPACE/round_b

# Run Ablation: Package loaded but zero bias
echo ""
echo "======================================================================"
echo "ABLATION: Control Purity (anti_leakage=0.0, bias=0.0)"
echo "======================================================================"
python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/generate_candidates_v2.py \
    --count $COUNT \
    --seed 1000 \
    --inheritance-package $V2_PACKAGE \
    --bias-strength 0.0 \
    --anti-leakage-strength 0.0 \
    --output $WORKSPACE/round_ablation

# Analysis
echo ""
echo "======================================================================"
echo "L4-v2 Experiment Summary"
echo "======================================================================"

echo ""
echo "Round A (Pure Exploration):"
cat $WORKSPACE/round_a/family_distribution.json | jq '.family_distribution | to_entries | sort_by(.value.count) | reverse | .[:5] | from_entries'

echo ""
echo "Round B (Anti-Leakage + Mechanism Bias):"
cat $WORKSPACE/round_b/family_distribution.json | jq '.family_distribution | to_entries | sort_by(.value.count) | reverse | .[:5] | from_entries'

echo ""
echo "Ablation (Control Purity):"
cat $WORKSPACE/round_ablation/family_distribution.json | jq '.family_distribution | to_entries | sort_by(.value.count) | reverse | .[:5] | from_entries'

echo ""
echo "======================================================================"
echo "Anti-Leakage Statistics (Round B):"
echo "======================================================================"
cat $WORKSPACE/round_b/manifest.json | jq '.anti_leakage_stats'

echo ""
echo "======================================================================"
echo "Verification: Round A vs Ablation Distribution Match"
echo "======================================================================"
python3 << 'EOF'
import json

# Load distributions
with open('/tmp/atlas_l4v2/round_a/family_distribution.json') as f:
    dist_a = json.load(f)['family_distribution']
with open('/tmp/atlas_l4v2/round_ablation/family_distribution.json') as f:
    dist_ab = json.load(f)['family_distribution']

# Compare
match = all(dist_a.get(k, {}).get('count', 0) == dist_ab.get(k, {}).get('count', 0) 
            for k in set(list(dist_a.keys()) + list(dist_ab.keys())))

print(f"Round A and Ablation have identical distribution: {match}")
if match:
    print("✓ Control purity verified - anti_leakage_strength=0.0 produces identical output")
else:
    print("⚠ Warning: Distributions differ")
    
# Check Round B improvement
with open('/tmp/atlas_l4v2/round_b/family_distribution.json') as f:
    dist_b = json.load(f)['family_distribution']

f_p3t4m4_a = dist_a.get('F_P3T4M4', {}).get('percentage', 0)
f_p3t4m4_b = dist_b.get('F_P3T4M4', {}).get('percentage', 0)

print(f"\nF_P3T4M4 improvement: {f_p3t4m4_a:.2f}% → {f_p3t4m4_b:.2f}% (Δ +{f_p3t4m4_b - f_p3t4m4_a:.2f}%)")
EOF

echo ""
echo "======================================================================"
echo "L4-v2 Experiment Complete"
echo "======================================================================"
echo "Output: $WORKSPACE"
echo ""
echo "Next steps:"
echo "1. Run evaluation on generated candidates"
echo "2. Verify targets: approve >60%, reuse >70%, F_P3T4M4 >30%, leakage <8%"
