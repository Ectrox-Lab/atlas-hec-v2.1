#!/bin/bash
# Check experiment status with hard evidence
# Usage: ./check_status.sh <experiment_name>

EXPERIMENT=${1:-"all"}

if [ "$EXPERIMENT" == "all" ] || [ "$EXPERIMENT" == "akashic_v3" ]; then
    echo "=== Akashic v3 Skeleton ==="
    
    PID_FILE="runs/akashic_v3/pid.txt"
    HEARTBEAT="runs/akashic_v3/heartbeat/heartbeat.json"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Status: RUNNING"
            echo "PID: $PID"
            ps -p "$PID" -o pid,cmd,%cpu,%mem
            
            if [ -f "$HEARTBEAT" ]; then
                echo "Heartbeat:"
                cat "$HEARTBEAT"
                echo ""
                echo "Last modified: $(stat -c %y "$HEARTBEAT")"
            fi
        else
            echo "Status: HALTED (PID $PID not found)"
        fi
    else
        echo "Status: NOT_STARTED (no PID file)"
    fi
    echo ""
fi

# Check resources
echo "=== System Resources ==="
top -b -n 1 | head -n 5
free -h | head -n 2
