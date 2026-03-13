#!/bin/bash
# Start HEAVY COMPUTE instances

set -e

N_INSTANCES=${1:-4}  # Default 4 instances per experiment type

echo "Starting $N_INSTANCES instances of each heavy experiment..."
echo "Target: $(($N_INSTANCES * 3)) total processes"

mkdir -p heavy_logs
pkill -f "heavy_" 2>/dev/null || true
sleep 2

# Start Akashic instances
for i in $(seq 1 $N_INSTANCES); do
    nohup /usr/bin/python3 -u superbrain/heavy_mode/heavy_akashic.py > heavy_logs/akashic_${i}.log 2>&1 &
    echo "Akashic-$i: $!"
done

# Start 128-Universe instances  
for i in $(seq 1 $N_INSTANCES); do
    nohup /usr/bin/python3 -u superbrain/heavy_mode/heavy_128_universe.py > heavy_logs/univ_${i}.log 2>&1 &
    echo "Universe-$i: $!"
done

# Start Fast Genesis instances
for i in $(seq 1 $N_INSTANCES); do
    nohup /usr/bin/python3 -u superbrain/heavy_mode/heavy_fast_genesis.py > heavy_logs/genesis_${i}.log 2>&1 &
    echo "Genesis-$i: $!"
done

echo ""
echo "All instances started. Monitor with:"
echo "  watch -n 1 'ps aux | grep heavy_ | grep -v grep | wc -l'"
echo "  tail -f heavy_logs/*.log"
