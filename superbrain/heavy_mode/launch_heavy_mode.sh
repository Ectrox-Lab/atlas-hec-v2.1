#!/bin/bash
# HEAVY COMPUTE EXPERIMENT MODE
# 
# Target:
# - CPU: 70-95% on 128C
# - RAM: 200-400GB
# - NO SLEEP, pure compute
# - O(N^2) operations, matrix ops, heavy evolution

set -e

echo "=================================================================="
echo "  HEAVY COMPUTE EXPERIMENT MODE"
echo "  SOCS Universe Search v2.1 - Resource Punishment Edition"
echo "=================================================================="
echo ""
echo "Target Resource Usage:"
echo "  CPU: 70-95% (all 128 cores engaged)"
echo "  RAM: 200-400GB (no idle memory)"
echo "  Load: Pure computation, NO SLEEP"
echo ""
echo "Experiments:"
echo "  1. HEAVY AKASHIC    - 50k candidates, O(N^2) distances"
echo "  2. HEAVY 128 UNIV   - 128 universes, cross-analysis"
echo "  3. HEAVY FAST GENESIS - 10k population, heavy evolution"
echo ""
echo "=================================================================="
echo ""

# Create log directory
mkdir -p heavy_logs

# Get start time
START_TIME=$(date +%s)

echo "[INIT] Starting heavy experiments at $(date)"
echo ""

# Function to monitor resources
monitor_resources() {
    while true; do
        sleep 10
        
        # CPU usage
        CPU_IDLE=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}')
        CPU_USAGE=$(echo "100 - $CPU_IDLE" | bc)
        
        # Memory usage
        MEM_INFO=$(free -g | grep Mem)
        MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
        MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
        MEM_PCT=$(echo "scale=1; $MEM_USED * 100 / $MEM_TOTAL" | bc)
        
        # Load average
        LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
        
        ELAPSED=$(($(date +%s) - START_TIME))
        ELAPSED_HOURS=$(echo "scale=1; $ELAPSED / 3600" | bc)
        
        echo "[MONITOR] T+${ELAPSED_HOURS}h | CPU: ${CPU_USAGE}% | RAM: ${MEM_USED}/${MEM_TOTAL}GB (${MEM_PCT}%) | Load: ${LOAD}"
        
        # Check if processes are still running
        if ! pgrep -f "heavy_akashic.py" > /dev/null && \
           ! pgrep -f "heavy_128_universe.py" > /dev/null && \
           ! pgrep -f "heavy_fast_genesis.py" > /dev/null; then
            echo "[MONITOR] All processes stopped"
            break
        fi
    done
}

# Launch experiments in parallel
echo "[LAUNCH] Starting HEAVY AKASHIC..."
/usr/bin/python3 superbrain/heavy_mode/heavy_akashic.py > heavy_logs/akashic.log 2>&1 &
AKASHIC_PID=$!
echo "  PID: $AKASHIC_PID"

echo "[LAUNCH] Starting HEAVY 128 UNIVERSE..."
/usr/bin/python3 superbrain/heavy_mode/heavy_128_universe.py > heavy_logs/128universe.log 2>&1 &
UNIV_PID=$!
echo "  PID: $UNIV_PID"

echo "[LAUNCH] Starting HEAVY FAST GENESIS..."
/usr/bin/python3 superbrain/heavy_mode/heavy_fast_genesis.py > heavy_logs/genesis.log 2>&1 &
GENESIS_PID=$!
echo "  PID: $GENESIS_PID"

echo ""
echo "=================================================================="
echo "All heavy experiments launched!"
echo "=================================================================="
echo ""
echo "PIDs:"
echo "  Akashic:    $AKASHIC_PID"
echo "  128-Universe: $UNIV_PID"
echo "  Fast Genesis: $GENESIS_PID"
echo ""
echo "Logs:"
echo "  heavy_logs/akashic.log"
echo "  heavy_logs/128universe.log"
echo "  heavy_logs/genesis.log"
echo ""
echo "Monitor:"
echo "  tail -f heavy_logs/*.log"
echo ""
echo "Stop:"
echo "  kill $AKASHIC_PID $UNIV_PID $GENESIS_PID"
echo "  OR: ./superbrain/heavy_mode/stop_heavy_mode.sh"
echo ""
echo "=================================================================="
echo ""

# Start resource monitoring in background
monitor_resources &
MONITOR_PID=$!

# Wait for any process to exit
wait $AKASHIC_PID $UNIV_PID $GENESIS_PID

# Kill monitor
kill $MONITOR_PID 2>/dev/null || true

echo ""
echo "[DONE] Heavy experiments completed at $(date)"
