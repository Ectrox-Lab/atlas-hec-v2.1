#!/bin/bash
# 实验进度监控脚本
# 运行方式: bash source/scripts/monitor_experiment.sh (从仓库根目录)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$REPO_ROOT/source/logs/p3d"

echo "=== P3D-gamma Experiment Monitor ==="
echo "Time: $(date)"
echo "Repo: $REPO_ROOT"
echo ""

# 检查结果文件数量
RESULT_COUNT=$(ls "$LOG_DIR"/*_result.json 2>/dev/null | wc -l)
echo "Results: $RESULT_COUNT / 20 (expected)"

# 检查运行进程
if pgrep -f "p3d_main_runtime_native" > /dev/null; then
    echo "Status: 🔄 Running"
    ps aux | grep p3d_main_runtime | grep -v grep | awk '{print "  PID: " $2 " | CPU: " $3 "% | MEM: " $4 "% | Time: " $10}'
else
    echo "Status: ⏹️  Stopped"
fi

echo ""
echo "Recent results:"
ls -lt "$LOG_DIR"/*_result.json 2>/dev/null | head -5 | awk '{print "  " $9}'

echo ""
echo "Last 10 lines of log:"
tail -10 "$LOG_DIR"/experiment_run.log 2>/dev/null
