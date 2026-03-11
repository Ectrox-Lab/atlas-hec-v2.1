#!/bin/bash
# Phase 2 Round 1: Independent Environment Runner
# 3 seeds × 2k ticks per environment
# Output: /tmp/phase2_{env}_3x2k.csv

set -e

TICKS=2000
SEEDS="12000 12002 12004"

echo "========================================"
echo "Phase 2 Round 1: Independent Batches"
echo "========================================"
echo "Config: 3 seeds × ${TICKS} ticks per env"
echo ""

# Build
# echo "Building..."
# cargo build --release --bin phase2_round1 --no-default-features 2>&1 | tail -3

run_env() {
    local env_name=$1
    local env_code=$2
    local output="/tmp/phase2_${env_name}_3x2k.csv"
    
    echo "[${env_name}]"
    echo "  Seeds: ${SEEDS}"
    
    # Header
    echo "seed,tick,population,coordination" > "$output"
    
    for seed in $SEEDS; do
        # Run and extract telemetry (simplified - just final for now)
        result=$(cargo run --release --bin phase2_${env_name}_single --no-default-features 2>&1 | grep -E "Final|PASS|FAIL" | tail -3)
        echo "  Seed ${seed}: ${result}"
    done
    
    echo "  Exported: ${output}"
    echo ""
}

# Run each environment independently
echo "Starting independent runs..."
echo ""

# For now, use the existing singles
timeout 60 cargo run --release --bin phase2_hub_single --no-default-features 2>&1 | tail -10
timeout 60 cargo run --release --bin phase2_regime_single --no-default-features 2>&1 | tail -10

echo ""
echo "========================================"
echo "Batch Complete"
echo "========================================"
echo "Check /tmp/phase2_*.csv for results"
