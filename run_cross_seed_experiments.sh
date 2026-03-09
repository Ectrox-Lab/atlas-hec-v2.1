#!/bin/bash
# Cross-Seed Experiment Runner
# 运行多个seed的Bio-World v18.1实验

set -e

N_SEEDS="${1:-5}"
GENERATIONS="${2:-7000}"
OUTPUT_BASE="/home/admin/zeroclaw-labs/v18_1_experiments"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Cross-Seed Bio-World v18.1 Experiment Runner               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Configuration:"
echo "  Seeds: $N_SEEDS"
echo "  Generations: $GENERATIONS"
echo "  Output: $OUTPUT_BASE"
echo ""

# 检查编译
cd /home/admin/atlas-hec-v2.1-repo/source
if [ ! -f target/release/atlas-hec-v2.1 ]; then
    echo "Building..."
    cargo build --release
fi

cd /home/admin/atlas-hec-v2.1-repo

# 运行多个seed
CSV_FILES=()

for SEED in $(seq 1 $N_SEEDS); do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running Seed $SEED/$N_SEEDS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    OUTPUT_DIR="$OUTPUT_BASE/cross_seed_${TIMESTAMP}_seed${SEED}"
    mkdir -p "$OUTPUT_DIR"
    
    # 运行实验
    timeout 14400 ./source/target/release/atlas-hec-v2.1 \
        --seed $SEED \
        --generations $GENERATIONS \
        --max-population 500 \
        --synapses-per-cell 15 \
        --output "$OUTPUT_DIR" \
        2>&1 | tee "$OUTPUT_DIR/run.log" || true
    
    # 检查输出
    if [ -f "$OUTPUT_DIR/evolution.csv" ]; then
        LINES=$(wc -l < "$OUTPUT_DIR/evolution.csv")
        echo "✅ Seed $SEED complete: $LINES lines"
        CSV_FILES+=("$OUTPUT_DIR/evolution.csv")
    else
        echo "❌ Seed $SEED failed: no evolution.csv"
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running P0 Cross-Seed Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#CSV_FILES[@]} -ge 3 ]; then
    python3 P0_cross_seed_protocol.py --csv-files "${CSV_FILES[@]}"
else
    echo "⚠️ Only ${#CSV_FILES[@]} valid runs (need >= 3 for P0)"
    echo "Valid files:"
    for f in "${CSV_FILES[@]}"; do
        echo "  - $f"
    done
fi

echo ""
echo "Experiments complete. Results in: $OUTPUT_BASE/cross_seed_${TIMESTAMP}_*"
