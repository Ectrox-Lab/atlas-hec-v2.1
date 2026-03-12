#!/usr/bin/env python3
"""
Multiverse 128 Sweep Launcher
Stage 1: 16 universes (2×2×2×2 matrix)
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# Config
BASE_DIR = Path("multiverse_sweep/stage_1_16")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# 16 Universe Configurations (2×2×2×2)
CONFIGS = [
    # Pressure (1-2) × Perturb (1-2) × Memory (1-2) × Delegation (1-2)
    {"id": "1111_1", "pressure": 1, "perturb": 1, "memory": 1, "delegation": 1},
    {"id": "1111_2", "pressure": 1, "perturb": 1, "memory": 1, "delegation": 1},
    {"id": "1112_1", "pressure": 1, "perturb": 1, "memory": 1, "delegation": 2},
    {"id": "1112_2", "pressure": 1, "perturb": 1, "memory": 1, "delegation": 2},
    {"id": "1121_1", "pressure": 1, "perturb": 1, "memory": 2, "delegation": 1},
    {"id": "1121_2", "pressure": 1, "perturb": 1, "memory": 2, "delegation": 1},
    {"id": "1122_1", "pressure": 1, "perturb": 1, "memory": 2, "delegation": 2},
    {"id": "1122_2", "pressure": 1, "perturb": 1, "memory": 2, "delegation": 2},
    {"id": "1211_1", "pressure": 1, "perturb": 2, "memory": 1, "delegation": 1},
    {"id": "1211_2", "pressure": 1, "perturb": 2, "memory": 1, "delegation": 1},
    {"id": "1212_1", "pressure": 1, "perturb": 2, "memory": 1, "delegation": 2},
    {"id": "1212_2", "pressure": 1, "perturb": 2, "memory": 1, "delegation": 2},
    {"id": "1221_1", "pressure": 1, "perturb": 2, "memory": 2, "delegation": 1},
    {"id": "1221_2", "pressure": 1, "perturb": 2, "memory": 2, "delegation": 1},
    {"id": "1222_1", "pressure": 1, "perturb": 2, "memory": 2, "delegation": 2},
    {"id": "1222_2", "pressure": 1, "perturb": 2, "memory": 2, "delegation": 2},
]

def launch_universe(config):
    """Launch single universe"""
    uid = config["id"]
    udir = BASE_DIR / f"universe_{uid}"
    udir.mkdir(exist_ok=True)
    
    # Write config
    with open(udir / "config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    # Launch G1 with isolated output directory
    udir_abs = udir.absolute()
    g1_cmd = f"cd {udir} && python3 ../../../implementations/g1/workload_continuous.py --output-dir {udir_abs}/g1_output > g1.log 2>&1"
    g1_proc = subprocess.Popen(g1_cmd, shell=True)
    
    # Launch E1 with isolated output directory
    e1_cmd = f"cd {udir} && python3 ../../../implementations/e1/workload_continuous.py --output-dir {udir_abs}/e1_output > e1.log 2>&1"
    e1_proc = subprocess.Popen(e1_cmd, shell=True)
    
    return {
        "id": uid,
        "g1_pid": g1_proc.pid,
        "e1_pid": e1_proc.pid,
        "dir": str(udir),
        "started": datetime.now().isoformat()
    }

def main():
    print("=" * 60)
    print("MULTIVERSE STAGE 1: Launching 16 Universes")
    print("=" * 60)
    print(f"Base directory: {BASE_DIR}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    launched = []
    for config in CONFIGS:
        print(f"Launching universe_{config['id']}...", end=" ")
        try:
            info = launch_universe(config)
            launched.append(info)
            print(f"OK (G1:{info['g1_pid']}, E1:{info['e1_pid']})")
            time.sleep(0.5)  # Stagger launches
        except Exception as e:
            print(f"FAILED: {e}")
    
    # Write launch manifest
    manifest = {
        "stage": 1,
        "count": len(launched),
        "timestamp": datetime.now().isoformat(),
        "universes": launched
    }
    with open(BASE_DIR / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print()
    print("=" * 60)
    print(f"LAUNCHED: {len(launched)}/16 universes")
    print("=" * 60)
    print()
    print("Validation (30s):")
    time.sleep(5)
    
    # Quick validation
    running = 0
    for info in launched:
        g1_running = os.system(f"kill -0 {info['g1_pid']} 2>/dev/null") == 0
        e1_running = os.system(f"kill -0 {info['e1_pid']} 2>/dev/null") == 0
        if g1_running and e1_running:
            running += 1
    
    print(f"  Running: {running}/{len(launched)}")
    print()
    print("Monitor with:")
    print(f"  ls -l {BASE_DIR}/universe_*/")
    print(f"  tail -f {BASE_DIR}/universe_*/g1.log")
    print()

if __name__ == "__main__":
    main()
