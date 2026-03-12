#!/usr/bin/env python3
"""
Multiverse Stage 3: 128-UNIVERSE SWEEP
8 core configs × 16 repeats = 128 universes
Full pressure matrix with statistical power
"""

import os
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("multiverse_sweep/stage_3_128")

# 8 core configs from Stage 2, expanded to 16 repeats each
CORE_CONFIGS = [
    {"pressure": 2, "perturb": 3, "memory": 1, "delegation": 1},  # 1: P2T3M1D1
    {"pressure": 2, "perturb": 3, "memory": 1, "delegation": 2},  # 2: P2T3M1D2
    {"pressure": 2, "perturb": 3, "memory": 3, "delegation": 1},  # 3: P2T3M3D1
    {"pressure": 2, "perturb": 3, "memory": 3, "delegation": 2},  # 4: P2T3M3D2
    {"pressure": 3, "perturb": 4, "memory": 1, "delegation": 1},  # 5: P3T4M1D1
    {"pressure": 3, "perturb": 4, "memory": 1, "delegation": 2},  # 6: P3T4M1D2
    {"pressure": 3, "perturb": 4, "memory": 3, "delegation": 1},  # 7: P3T4M3D1
    {"pressure": 3, "perturb": 4, "memory": 3, "delegation": 2},  # 8: P3T4M3D2
]

def generate_stage3_configs():
    """Generate 128 configs: 8 core × 16 repeats"""
    configs = []
    for i, core in enumerate(CORE_CONFIGS, 1):
        for repeat in range(1, 17):  # 16 repeats for statistical power
            config = core.copy()
            config['id'] = f"{i}_{repeat}"
            config['core_id'] = i
            config['repeat'] = repeat
            configs.append(config)
    return configs

def launch_universe(config):
    """Launch single universe"""
    uid = config['id']
    udir = BASE_DIR / f"universe_{uid}"
    udir.mkdir(parents=True, exist_ok=True)
    
    with open(udir / "config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    udir_abs = udir.absolute()
    
    # G1 v2 (config-responsive)
    g1_cmd = f"cd {udir} && python3 ../../../implementations/g1/workload_continuous_v2.py --output-dir {udir_abs}/g1_output > g1.log 2>&1"
    g1_proc = subprocess.Popen(g1_cmd, shell=True)
    
    # E1
    e1_cmd = f"cd {udir} && python3 ../../../implementations/e1/workload_continuous.py --output-dir {udir_abs}/e1_output > e1.log 2>&1"
    e1_proc = subprocess.Popen(e1_cmd, shell=True)
    
    return {
        "id": uid,
        "core_id": config['core_id'],
        "repeat": config['repeat'],
        "g1_pid": g1_proc.pid,
        "e1_pid": e1_proc.pid,
        "started": datetime.now().isoformat()
    }

def main():
    print("=" * 70)
    print("MULTIVERSE STAGE 3: 128-UNIVERSE FULL SWEEP")
    print("=" * 70)
    print()
    
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    configs = generate_stage3_configs()
    
    print(f"Configuration: 8 core × 16 repeats = {len(configs)} universes")
    print(f"Estimated processes: {len(configs) * 2} (G1 + E1)")
    print(f"Estimated vCPUs needed: ~{len(configs)}")
    print()
    
    # Check resources
    import shutil
    free_gb = shutil.disk_usage("/home/admin").free / (1024**3)
    print(f"Free disk: {free_gb:.1f} GB")
    if free_gb < 20:
        print("WARNING: Low disk space")
    print()
    
    print("Launching in 5 seconds...")
    time.sleep(5)
    
    launched = []
    batch_size = 16
    for batch_start in range(0, len(configs), batch_size):
        batch = configs[batch_start:batch_start + batch_size]
        print(f"\nBatch {batch_start//batch_size + 1}/{(len(configs)-1)//batch_size + 1}:")
        
        for config in batch:
            try:
                info = launch_universe(config)
                launched.append(info)
                print(f"  {info['id']}: G1={info['g1_pid']}, E1={info['e1_pid']}")
                time.sleep(0.2)
            except Exception as e:
                print(f"  {config['id']}: FAILED - {e}")
        
        time.sleep(2)  # Brief pause between batches
    
    # Manifest
    manifest = {
        "stage": 3,
        "count": len(launched),
        "timestamp": datetime.now().isoformat(),
        "universes": launched,
        "matrix": CORE_CONFIGS
    }
    with open(BASE_DIR / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print()
    print("=" * 70)
    print(f"LAUNCHED: {len(launched)}/128 universes")
    print("=" * 70)
    print()
    print(f"Monitor: ls -l {BASE_DIR}/universe_*/")

if __name__ == "__main__":
    main()
