#!/bin/bash
# P1 Causal Experiment Runner
# Phase 1: Directional Screening (n=3/group)
# Phase 2: Full Validation (n=5-8/group)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_BASE="/home/admin/zeroclaw-labs/p1_causal_experiments"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Configuration
PHASE="${1:-1}"  # 1 or 2
if [ "$PHASE" == "1" ]; then
    N_SEEDS=3
    echo "Running PHASE 1: Directional Screening (n=3/group)"
elif [ "$PHASE" == "2" ]; then
    N_SEEDS="${2:-5}"
    echo "Running PHASE 2: Full Validation (n=$N_SEEDS/group)"
else
    echo "Usage: $0 <phase> [n_seeds for phase 2]"
    echo "  phase 1: Quick screening with 3 seeds"
    echo "  phase 2: Full validation with 5-8 seeds"
    exit 1
fi

GENERATIONS=7000
mkdir -p "$OUTPUT_BASE"

echo "═══════════════════════════════════════════════════════════════"
echo "  P1 Causal Experiments - Phase $PHASE"
echo "  Seeds per group: $N_SEEDS"
echo "  Generations: $GENERATIONS"
echo "  Output: $OUTPUT_BASE"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Seed set (identical across all groups)
SEEDS=(1 2 3 4 5 6 7 8)
SEEDS_TO_USE=(${SEEDS[@]:0:$N_SEEDS})

echo "Using seeds: ${SEEDS_TO_USE[@]}"
echo ""

# Function to run single experiment
run_experiment() {
    local group=$1
    local seed=$2
    local config=$3
    
    local output_dir="$OUTPUT_BASE/${group}_seed${seed}_${TIMESTAMP}"
    mkdir -p "$output_dir"
    
    echo "  [$group | Seed $seed] Running..."
    
    # Build command with configuration
    local cmd="./source/target/release/atlas-hec-v2.1"
    cmd="$cmd --seed $seed"
    cmd="$cmd --generations $GENERATIONS"
    cmd="$cmd --output $output_dir"
    
    # Add group-specific config
    if [ "$group" == "P1-A" ]; then
        cmd="$cmd --memory-capacity 0"
    elif [ "$group" == "P1-B" ]; then
        cmd="$cmd --cooperation-willingness 0.3"
    elif [ "$group" == "P1-C" ]; then
        cmd="$cmd --boss-strength 1.5"
    fi
    
    # Run with timeout
    timeout 14400 $cmd 2>&1 | tee "$output_dir/run.log" || true
    
    # Verify output
    if [ -f "$output_dir/evolution.csv" ]; then
        local lines=$(wc -l < "$output_dir/evolution.csv")
        echo "    ✓ Complete: $lines lines"
        echo "$output_dir/evolution.csv"
    else
        echo "    ✗ Failed: no evolution.csv"
        return 1
    fi
}

# Export function for parallel execution
export -f run_experiment
export OUTPUT_BASE TIMESTAMP GENERATIONS

# Run all experiments
echo "Starting experiments..."
echo ""

CTRL_CSVS=()
P1A_CSVS=()
P1B_CSVS=()
P1C_CSVS=()

# CTRL Group
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GROUP: CTRL (Baseline)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in "${SEEDS_TO_USE[@]}"; do
    csv=$(run_experiment "CTRL" "$seed" "baseline")
    if [ $? -eq 0 ]; then
        CTRL_CSVS+=("$csv")
    fi
done
echo ""

# P1-A: Memory KO
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GROUP: P1-A (Memory Knockout)"
echo "Configuration: memory_capacity = 0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in "${SEEDS_TO_USE[@]}"; do
    csv=$(run_experiment "P1-A" "$seed" "memory_ko")
    if [ $? -eq 0 ]; then
        P1A_CSVS+=("$csv")
    fi
done
echo ""

# P1-B: Cooperation Suppression
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GROUP: P1-B (Cooperation Suppression)"
echo "Configuration: cooperation_willingness × 0.3"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in "${SEEDS_TO_USE[@]}"; do
    csv=$(run_experiment "P1-B" "$seed" "coop_suppress")
    if [ $? -eq 0 ]; then
        P1B_CSVS+=("$csv")
    fi
done
echo ""

# P1-C: Boss Pressure
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GROUP: P1-C (Boss Pressure Increase)"
echo "Configuration: boss_strength × 1.5"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for seed in "${SEEDS_TO_USE[@]}"; do
    csv=$(run_experiment "P1-C" "$seed" "boss_pressure")
    if [ $? -eq 0 ]; then
        P1C_CSVS+=("$csv")
    fi
done
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════"
echo "  EXPERIMENT SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "CTRL: ${#CTRL_CSVS[@]}/$N_SEEDS successful"
echo "P1-A: ${#P1A_CSVS[@]}/$N_SEEDS successful"
echo "P1-B: ${#P1B_CSVS[@]}/$N_SEEDS successful"
echo "P1-C: ${#P1C_CSVS[@]}/$N_SEEDS successful"
echo ""

# Run analysis if sufficient data
if [ ${#CTRL_CSVS[@]} -ge 2 ] && [ ${#P1A_CSVS[@]} -ge 2 ]; then
    echo "Running P1 causal analysis..."
    
    ALL_CSVS=("${CTRL_CSVS[@]}" "${P1A_CSVS[@]}" "${P1B_CSVS[@]}" "${P1C_CSVS[@]}")
    
    python3 "$SCRIPT_DIR/analyze_p1_causal.py" \
        --ctrl "${CTRL_CSVS[@]}" \
        --p1a "${P1A_CSVS[@]}" \
        --p1b "${P1B_CSVS[@]}" \
        --p1c "${P1C_CSVS[@]}" \
        --output "$OUTPUT_BASE/P1_analysis_${TIMESTAMP}"
    
    echo ""
    echo "Analysis complete: $OUTPUT_BASE/P1_analysis_${TIMESTAMP}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  P1 Phase $PHASE Complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
if [ "$PHASE" == "1" ]; then
    echo "  1. Review $OUTPUT_BASE/P1_analysis_${TIMESTAMP}/P1_RESULTS_SUMMARY.md"
    echo "  2. Determine which groups show correct effect direction"
    echo "  3. Run Phase 2 for confirmed groups:"
    echo "     $0 2 5  # 5 seeds per group"
fi
