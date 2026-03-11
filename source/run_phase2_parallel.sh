#!/bin/bash
# Phase 2 Parallel Smoke Test Runner

set -e

echo "========================================"
echo "Phase 2 Smoke Test - Parallel Execution"
echo "========================================"
echo ""

# Build all first
echo "Building all environments..."
cargo build --release --bin phase2/hub_failure --no-default-features 2>&1 | tail -3
cargo build --release --bin phase2/regime_shift --no-default-features 2>&1 | tail -3
cargo build --release --bin phase2/resource_competition --no-default-features 2>&1 | tail -3
cargo build --release --bin phase2/multigame_cycle --no-default-features 2>&1 | tail -3

echo ""
echo "Running 4 environments in parallel..."
echo ""

# Run all 4 in background
./target/release/phase2/hub_failure > /tmp/phase2_hub.log 2>&1 &
PID1=$!
./target/release/phase2/regime_shift > /tmp/phase2_regime.log 2>&1 &
PID2=$!
./target/release/phase2/resource_competition > /tmp/phase2_resource.log 2>&1 &
PID3=$!
./target/release/phase2/multigame_cycle > /tmp/phase2_multigame.log 2>&1 &
PID4=$!

# Wait for all
echo "Hub Failure World (PID: $PID1)..."
echo "Regime Shift World (PID: $PID2)..."
echo "Resource Competition (PID: $PID3)..."
echo "Multi-Game Cycle (PID: $PID4)..."
echo ""

wait $PID1
EXIT1=$?
wait $PID2
EXIT2=$?
wait $PID3
EXIT3=$?
wait $PID4
EXIT4=$?

echo "========================================"
echo "Results Summary"
echo "========================================"
echo ""

# Check results
PASSED=0
check_result() {
    local name=$1
    local exit_code=$2
    local log=$3
    if [ $exit_code -eq 0 ]; then
        echo "✓ $name: PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "✗ $name: FAILED"
        echo "  (see $log)"
    fi
}

check_result "Hub Failure World" $EXIT1 /tmp/phase2_hub.log
check_result "Regime Shift World" $EXIT2 /tmp/phase2_regime.log
check_result "Resource Competition" $EXIT3 /tmp/phase2_resource.log
check_result "Multi-Game Cycle" $EXIT4 /tmp/phase2_multigame.log

echo ""
echo "========================================"
echo "Overall: $PASSED/4 environments passed"
echo "========================================"

# Show detailed results
if [ $PASSED -ge 2 ]; then
    echo ""
    echo "Detailed results:"
    for f in /tmp/phase2_*.log; do
        echo ""
        echo "--- $(basename $f) ---"
        tail -4 "$f"
    done
fi

# Exit code: need 3/4 to pass overall
if [ $PASSED -ge 3 ]; then
    echo ""
    echo "✓ PHASE 2 SMOKE TEST: PASSED"
    exit 0
else
    echo ""
    echo "✗ PHASE 2 SMOKE TEST: FAILED"
    exit 1
fi
