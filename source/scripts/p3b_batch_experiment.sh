#!/bin/bash
# P3B: 批量 A/B 验证实验
# 
# 运行多个种子，生成统计对比报告
# 
# 用法: ./scripts/p3b_batch_experiment.sh [num_seeds] [steps]

set -e

NUM_SEEDS=${1:-10}
STEPS=${2:-5000}
OUTPUT_DIR="logs/p3b/batch_$(date +%Y%m%d_%H%M%S)"

# 设置编译环境
export RUSTFLAGS="-L $PWD/hetero_bridge"
export LD_LIBRARY_PATH="$PWD/hetero_bridge:$LD_LIBRARY_PATH"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     P3B: Batch A/B Validation Experiment                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Seeds:         $NUM_SEEDS"
echo "║  Steps/Seed:    $STEPS"
echo "║  Output:        $OUTPUT_DIR"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

mkdir -p "$OUTPUT_DIR"

# 编译
echo "🔨 Building..."
cargo build --bin p3b_ab_validation --release 2>/dev/null

echo "🧪 Running experiments..."
echo ""

# 运行 baseline
for seed in $(seq 1 $NUM_SEEDS); do
    echo -n "  Baseline seed $seed/$NUM_SEEDS... "
    ./target/release/p3b_ab_validation \
        --preservation off \
        --seed $seed \
        --steps $STEPS \
        --output "$OUTPUT_DIR" > /dev/null 2>&1
    echo "✓"
done

# 运行 P2-ON
for seed in $(seq 1 $NUM_SEEDS); do
    echo -n "  P2-ON seed $seed/$NUM_SEEDS... "
    ./target/release/p3b_ab_validation \
        --preservation on \
        --seed $seed \
        --steps $STEPS \
        --output "$OUTPUT_DIR" > /dev/null 2>&1
    echo "✓"
done

echo ""
echo "📊 Running analysis..."
python3 scripts/analyze_p3b.py "$OUTPUT_DIR"

echo ""
echo "📁 Results saved to: $OUTPUT_DIR"
