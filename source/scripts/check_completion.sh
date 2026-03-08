#!/bin/bash
# P3D-gamma 完成检测脚本

LOG_DIR="/home/admin/atlas-hec-v2.1-repo/source/logs/p3d"
EXPECTED_PAIRS=10  # seeds 1-10

echo "=== P3D-gamma Completion Check ==="
echo "Time: $(date)"
echo ""

# 检查进程
if pgrep -f "p3d_main_runtime_native" > /dev/null; then
    echo "Status: 🔄 Running"
    ps aux | grep p3d_main_runtime | grep -v grep | awk '{print "  PID: " $2 " | Time: " $10}'
else
    echo "Status: ⏹️  Stopped"
fi

echo ""
echo "Seed pairing status:"
ls "$LOG_DIR"/*_result.json 2>/dev/null | grep -E "baseline_seed|p2on_seed" | sed 's/.*seed\([0-9]*\).*/\1/' | sort -n | uniq -c | while read count seed; do
    if [ "$count" -eq 2 ]; then
        echo "  Seed $seed: ✅ Complete ($count files)"
    elif [ "$count" -eq 1 ]; then
        echo "  Seed $seed: ⏳ Partial ($count file)"
    else
        echo "  Seed $seed: ⚠️  Multiple ($count files)"
    fi
done

echo ""
echo "Summary:"
TOTAL_FILES=$(ls "$LOG_DIR"/*_result.json 2>/dev/null | grep -E "baseline_seed|p2on_seed" | wc -l)
UNIQUE_SEEDS=$(ls "$LOG_DIR"/*_result.json 2>/dev/null | grep -E "baseline_seed|p2on_seed" | sed 's/.*seed\([0-9]*\).*/\1/' | sort -n | uniq | wc -l)
COMPLETE_PAIRS=$(ls "$LOG_DIR"/*_result.json 2>/dev/null | grep -E "baseline_seed|p2on_seed" | sed 's/.*seed\([0-9]*\).*/\1/' | sort -n | uniq -c | grep -c "2$")

echo "  Total result files: $TOTAL_FILES"
echo "  Unique seeds: $UNIQUE_SEEDS / $EXPECTED_PAIRS"
echo "  Complete pairs: $COMPLETE_PAIRS / $EXPECTED_PAIRS"

if [ "$COMPLETE_PAIRS" -ge "$EXPECTED_PAIRS" ]; then
    echo ""
    echo "✅ EXPERIMENT COMPLETE!"
    echo "Ready to run: python3 scripts/analyze_p3d_gamma.py"
fi
