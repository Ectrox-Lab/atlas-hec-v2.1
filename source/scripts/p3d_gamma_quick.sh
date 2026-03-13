#!/bin/bash
# P3D-gamma: Quick Test (3 seeds × 20 episodes)

set -e
export RUSTFLAGS="-L $PWD/hetero_bridge"
export LD_LIBRARY_PATH="$PWD/hetero_bridge:$LD_LIBRARY_PATH"

SEEDS=(42 123 456)
EPISODES=20
STEPS=300

mkdir -p logs/p3d

echo "=== P3D-gamma Quick Test ==="
echo "Seeds: ${SEEDS[@]}"
echo "Episodes: $EPISODES"
echo ""

for seed in "${SEEDS[@]}"; do
    echo "Seed $seed: Baseline..."
    timeout 120 ./target/release/p3d_main_runtime_native --preservation off --seed $seed --episodes $EPISODES --steps $STEPS > /dev/null 2>&1 || true
    
    echo "Seed $seed: P2-ON..."
    timeout 120 ./target/release/p3d_main_runtime_native --preservation on --seed $seed --episodes $EPISODES --steps $STEPS > /dev/null 2>&1 || true
done

echo ""
echo "=== Analysis ==="
python3 scripts/analyze_p3d_gamma.py logs/p3d/
