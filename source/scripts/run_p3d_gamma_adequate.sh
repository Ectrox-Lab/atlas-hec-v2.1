#!/bin/bash
# P3D-gamma Adequate-Sample Experiment Run
# 
# 固定参数：
# - Seeds: [1,2,3,4,5,6,7,8,9,10]
# - Episodes/seed: 50
# - Total: 500 episodes / condition
#
# 运行前确保：
# - cargo build --bin p3d_main_runtime_native --release
# - Git 工作区干净 (git status)

set -e

# 固定 Seed 集合（不得修改）
SEEDS=(1 2 3 4 5 6 7 8 9 10)
EPISODES=50
STEPS=500
BINARY="./target/release/p3d_main_runtime_native"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  P3D-gamma: Adequate-Sample Experiment Run                    ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  Date:     $(date -Iseconds)"
echo "║  Git:      $(git rev-parse HEAD)"
echo "║  Branch:   $(git branch --show-current)"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  Seeds:    ${SEEDS[@]}"
echo "║  Episodes: $EPISODES per seed"
echo "║  Steps:    $STEPS per episode"
echo "║  Total:    $(( ${#SEEDS[@]} * $EPISODES )) episodes / condition"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 检查 binary
if [ ! -f "$BINARY" ]; then
    echo "❌ Binary not found: $BINARY"
    echo "   Run: cargo build --bin p3d_main_runtime_native --release"
    exit 1
fi

# 创建结果目录
mkdir -p logs/p3d

# 保存实验配置
cat > logs/p3d/experiment_config.json << EOF
{
  "experiment_name": "P3D-gamma-adequate-sample",
  "experiment_date": "$(date -Iseconds)",
  "git": {
    "commit_hash": "$(git rev-parse HEAD)",
    "branch": "$(git branch --show-current)",
    "dirty": $(git diff --quiet && echo "false" || echo "true")
  },
  "build": {
    "command": "cargo build --bin p3d_main_runtime_native --release",
    "binary_path": "$BINARY"
  },
  "parameters": {
    "seed_list": [$(IFS=,; echo "${SEEDS[*]}")],
    "episodes_per_seed": $EPISODES,
    "max_steps_per_episode": $STEPS
  }
}
EOF

echo "📁 Experiment config saved: logs/p3d/experiment_config.json"
echo ""

# 运行成对实验
TOTAL=$(( ${#SEEDS[@]} * 2 ))
CURRENT=0

for seed in "${SEEDS[@]}"; do
    echo "═══════════════════════════════════════════════════════════════"
    echo "Seed $seed"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Baseline
    CURRENT=$((CURRENT + 1))
    echo "[$CURRENT/$TOTAL] Baseline (seed=$seed)..."
    $BINARY --preservation off --seed $seed --episodes $EPISODES --steps $STEPS > /dev/null 2>&1
    
    # P2-ON
    CURRENT=$((CURRENT + 1))
    echo "[$CURRENT/$TOTAL] P2-ON (seed=$seed)..."
    $BINARY --preservation on --seed $seed --episodes $EPISODES --steps $STEPS > /dev/null 2>&1
    
    echo ""
done

echo "═══════════════════════════════════════════════════════════════"
echo "✅ All experiments complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 统计分析
echo "📊 Running statistical analysis..."
python3 scripts/analyze_p3d_gamma.py logs/p3d/
echo ""

# 验收验证
echo "🔍 Running completion verification..."
python3 scripts/verify_p3d_gamma_completion.py logs/p3d/summary_report.json
EXIT_CODE=$?
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 P3D-gamma COMPLETE!"
    echo "   Ready to declare: P3D-gamma = COMPLETE"
else
    echo "⏳ P3D-gamma NOT YET COMPLETE"
    echo "   Review summary_report.json and consider additional runs"
fi

echo ""
echo "📁 Results saved in: logs/p3d/"
echo "   - summary_report.json"
echo "   - experiment_config.json"
echo "   - *_result.json (raw results)"
