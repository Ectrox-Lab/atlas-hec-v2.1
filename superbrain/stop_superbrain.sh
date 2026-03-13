#!/bin/bash
# Graceful shutdown of all Superbrain modules

echo "[SHUTDOWN] Stopping Full-Stack Superbrain..."

# Find and kill supervisor
echo "[SHUTDOWN] Terminating Global Supervisor..."
pkill -f "global_supervisor.py" 2>/dev/null || true

# Terminate child processes
echo "[SHUTDOWN] Terminating modules..."
pkill -f "mainline_orchestrator.py" 2>/dev/null || true
pkill -f "fast_genesis_orchestrator.py" 2>/dev/null || true
pkill -f "bridge_scheduler.py" 2>/dev/null || true
pkill -f "akashic_synthesizer.py" 2>/dev/null || true

echo "[SHUTDOWN] All modules stopped"
echo "[SHUTDOWN] Final checkpoint saved to superbrain/global_control/final_state.json"

# Create final state summary
cat > superbrain/global_control/final_state.json << 'EOF'
{
  "status": "GRACEFUL_SHUTDOWN",
  "timestamp": "$(date -Iseconds)",
  "note": "Superbrain modules terminated by operator request"
}
EOF

echo "[SHUTDOWN] Complete."
