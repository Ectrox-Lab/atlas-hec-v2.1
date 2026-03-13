#!/bin/bash
# Stop all heavy mode experiments

echo "[STOP] Stopping all heavy experiments..."

pkill -f "heavy_akashic.py" 2>/dev/null || true
pkill -f "heavy_128_universe.py" 2>/dev/null || true
pkill -f "heavy_fast_genesis.py" 2>/dev/null || true

echo "[STOP] All heavy processes terminated"

# Final resource report
echo ""
echo "[REPORT] Final resource status:"
free -h
echo ""
uptime
echo ""
echo "[REPORT] Heavy logs saved to: heavy_logs/"
ls -la heavy_logs/ 2>/dev/null || echo "  (no logs directory)"
