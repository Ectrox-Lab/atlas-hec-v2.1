#!/bin/bash
# P3D-gamma: Measured Native A/B Batch Experiment
# 
# 院长要求：
# - 固定 seed 成对实验
# - 每组 30-100 episodes
# - 输出统计显著性证据

set -e

# 实验配置
SEEDS=(42 123 456 789 2024 777 999 314 1618 2718)
EPISODES=50
STEPS=500
OUTPUT_DIR="logs/p3d"
mkdir -p "$OUTPUT_DIR"

# 设置环境
export RUSTFLAGS="-L $PWD/hetero_bridge"
export LD_LIBRARY_PATH="$PWD/hetero_bridge:$LD_LIBRARY_PATH"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  P3D-gamma: Measured Native A/B Batch Experiment              ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  Seeds:      ${#SEEDS[@]} (fixed set)"
echo "║  Episodes:   $EPISODES per seed"
echo "║  Max Steps:  $STEPS per episode"
echo "║  Output:     $OUTPUT_DIR"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 编译 release 版本
echo "🔨 Building release binary..."
cargo build --bin p3d_main_runtime_native --release 2>/dev/null
BINARY="./target/release/p3d_main_runtime_native"

# 检查 binary
if [ ! -f "$BINARY" ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✅ Build complete"
echo ""

# 总实验数
TOTAL=$(( ${#SEEDS[@]} * 2 ))
CURRENT=0

# 运行成对实验
for seed in "${SEEDS[@]}"; do
    echo "═══════════════════════════════════════════════════════════════"
    echo "Seed $seed: Running paired experiment..."
    echo "═══════════════════════════════════════════════════════════════"
    
    # Baseline (off)
    CURRENT=$((CURRENT + 1))
    echo "[$CURRENT/$TOTAL] Baseline (seed=$seed)..."
    $BINARY \
        --preservation off \
        --seed $seed \
        --episodes $EPISODES \
        --steps $STEPS > /dev/null 2>&1
    
    # 检查结果
    BASELINE_RESULT=$(ls -t $OUTPUT_DIR/baseline_*_result.json 2>/dev/null | head -1)
    if [ -n "$BASELINE_RESULT" ]; then
        echo "  ✅ Baseline complete: $(basename $BASELINE_RESULT)"
    else
        echo "  ⚠️  Baseline result not found"
    fi
    
    # P2-ON (on)
    CURRENT=$((CURRENT + 1))
    echo "[$CURRENT/$TOTAL] P2-ON (seed=$seed)..."
    $BINARY \
        --preservation on \
        --seed $seed \
        --episodes $EPISODES \
        --steps $STEPS > /dev/null 2>&1
    
    # 检查结果
    P2ON_RESULT=$(ls -t $OUTPUT_DIR/p2on_*_result.json 2>/dev/null | head -1)
    if [ -n "$P2ON_RESULT" ]; then
        echo "  ✅ P2-ON complete: $(basename $P2ON_RESULT)"
    else
        echo "  ⚠️  P2-ON result not found"
    fi
    
    echo ""
done

echo "═══════════════════════════════════════════════════════════════"
echo "✅ All experiments complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Running statistical analysis..."
python3 scripts/analyze_p3d_gamma.py "$OUTPUT_DIR"
echo ""
echo "📁 Results saved in: $OUTPUT_DIR"
echo ""
echo "To view summary:"
echo "  cat $OUTPUT_DIR/summary_report.json"
