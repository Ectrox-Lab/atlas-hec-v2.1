#!/bin/bash
# Full-Stack Superbrain Startup Script
# Launches all modules in coordinated fashion

set -e

echo "=================================================================="
echo "  SOCS UNIVERSE SEARCH v2.1 - FULL-STACK SUPERBRAIN MODE"
echo "=================================================================="
echo ""
echo "Architecture:"
echo "  Mainline    - 128 universe court (slow, careful, auditable)"
echo "  Fast Genesis- 3 lineages evolution (fast, high search)"
echo "  Bridge      - Rolling admission/shadow/dry run funnel"
echo "  Akashic     - Knowledge synthesis & inheritance"
echo ""
echo "Temporal Scales:"
echo "  Mainline    - 6h/24h cycles"
echo "  Fast Genesis- Minutes/hours (event-driven)"
echo "  Bridge      - Continuous rolling"
echo "  Akashic     - 1h synthesis"
echo ""
echo "Hard Constraints:"
echo "  - D1 (Strict Delegation): MANDATORY"
echo "  - P3+M3: GLOBALLY BLOCKED"
echo "  - Similarity to Config 3: ≥0.70"
echo "  - Distance from Config 6: ≥0.30"
echo ""
echo "=================================================================="
echo ""

# Ensure directories exist
mkdir -p superbrain/{mainline/{checkpoints,approved_configs},fast_genesis/{lineages,event_logs},bridge/{incoming,shadow_queue,dryrun_queue,to_mainline},akashic/{knowledge_base,inputs/{mainline,fast_genesis,bridge}},global_control,emergency}
mkdir -p candidate_generation/phase4/{candidates,event_logs,inheritance}

echo "[INIT] Directory structure verified"

# Check configuration
echo "[INIT] Loading configuration..."
python3 superbrain/global_control/global_supervisor.py &
SUPERVISOR_PID=$!

echo ""
echo "[INIT] Supervisor started (PID: $SUPERVISOR_PID)"
echo ""
echo "Dashboard:"
echo "  tail -f superbrain/global_control/supervisor.log"
echo ""
echo "To stop:"
echo "  kill $SUPERVISOR_PID"
echo "  OR: ./stop_superbrain.sh"
echo ""
echo "Emergency stop:"
echo "  touch superbrain/emergency/STOP_ALL"
echo ""

# Wait for supervisor
wait $SUPERVISOR_PID
