#!/usr/bin/env python3
"""
Multiverse Stage 2 Launcher - READY BUT NOT LAUNCHED
32 universes: 8 configs × 4 repeats
Pressure-focused matrix for drift dynamics testing
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# STATUS: DRAFT - DO NOT LAUNCH UNTIL CONDITIONS MET
LAUNCH_STATUS = "GO"  # Change to "GO" when ready

# Base directory
BASE_DIR = Path("multiverse_sweep/stage_2_32")

# Stage 2 Matrix: 8 core configurations
# Focus: P2/P3 pressure × T3/T4 perturb × M1/M3 memory × D1/D2 delegation
CORE_CONFIGS = [
    # P2 (medium pressure) zone
    {"pressure": 2, "perturb": 3, "memory": 1, "delegation": 1},  # 1: Controlled stress
    {"pressure": 2, "perturb": 3, "memory": 1, "delegation": 2},  # 2: D1 vs D2 test
    {"pressure": 2, "perturb": 3, "memory": 3, "delegation": 1},  # 3: M1 vs M3 test
    {"pressure": 2, "perturb": 3, "memory": 3, "delegation": 2},  # 4: Double aggressive
    
    # P3 (high pressure) zone
    {"pressure": 3, "perturb": 4, "memory": 1, "delegation": 1},  # 5: Conservative under max stress
    {"pressure": 3, "perturb": 4, "memory": 1, "delegation": 2},  # 6: D2 survival test
    {"pressure": 3, "perturb": 4, "memory": 3, "delegation": 1},  # 7: M3 under max stress
    {"pressure": 3, "perturb": 4, "memory": 3, "delegation": 2},  # 8: Everything aggressive (critical)
]

def generate_stage2_configs():
    """Generate 32 configs: 8 core × 4 repeats"""
    configs = []
    for i, core in enumerate(CORE_CONFIGS, 1):
        for repeat in range(1, 5):  # 4 repeats
            config = core.copy()
            config['id'] = f"{i}_{repeat}"
            config['core_id'] = i
            config['repeat'] = repeat
            configs.append(config)
    return configs

def launch_universe(config):
    """Launch single universe with G1 v2 and E1"""
    uid = config['id']
    udir = BASE_DIR / f"universe_{uid}"
    udir.mkdir(parents=True, exist_ok=True)
    
    # Write config
    with open(udir / "config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    udir_abs = udir.absolute()
    
    # Launch G1 v2 (config-responsive drift)
    g1_cmd = f"cd {udir} && python3 ../../../implementations/g1/workload_continuous_v2.py --output-dir {udir_abs}/g1_output > g1.log 2>&1"
    g1_proc = subprocess.Popen(g1_cmd, shell=True)
    
    # Launch E1
    e1_cmd = f"cd {udir} && python3 ../../../implementations/e1/workload_continuous.py --output-dir {udir_abs}/e1_output > e1.log 2>&1"
    e1_proc = subprocess.Popen(e1_cmd, shell=True)
    
    return {
        "id": uid,
        "core_id": config['core_id'],
        "repeat": config['repeat'],
        "config": {k: v for k, v in config.items() if k not in ['id', 'core_id', 'repeat']},
        "g1_pid": g1_proc.pid,
        "e1_pid": e1_proc.pid,
        "dir": str(udir),
        "started": datetime.now().isoformat()
    }

def check_launch_conditions():
    """Verify Stage 1 v2 stability before launch"""
    print("=" * 60)
    print("STAGE 2 LAUNCH CONDITION CHECK")
    print("=" * 60)
    print()
    
    stage1_dir = Path("multiverse_sweep/stage_1_16")
    if not stage1_dir.exists():
        print("❌ Stage 1 directory not found")
        return False
    
    # Check 1: G1 v2 drift range
    print("[1] Checking G1 v2 drift range...")
    drifts = []
    for udir in stage1_dir.glob("universe_*/g1_output/g1_timeseries.csv"):
        try:
            with open(udir) as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last = lines[-1].strip().split(',')
                    drifts.append(float(last[3]))  # drift column
        except:
            pass
    
    if len(drifts) < 10:
        print(f"  ❌ Only {len(drifts)} universes with data")
        return False
    
    drift_min, drift_max = min(drifts), max(drifts)
    print(f"  Drift range: {drift_min:.4f} - {drift_max:.4f}")
    
    if drift_max < 0.30:
        print("  ❌ Drift range too narrow (need > 0.30 max)")
        return False
    if drift_min > 0.15:
        print("  ❌ Drift floor too high (need < 0.15 min)")
        return False
    print("  ✅ Drift range acceptable")
    
    # Check 2: Repeat variance
    print("[2] Checking repeat variance...")
    # Group by config
    config_drifts = {}
    for udir in stage1_dir.glob("universe_*"):
        config_path = udir / "config.json"
        csv_path = udir / "g1_output" / "g1_timeseries.csv"
        if config_path.exists() and csv_path.exists():
            with open(config_path) as f:
                cfg = json.load(f)
            key = f"P{cfg['pressure']}T{cfg['perturb']}M{cfg['memory']}D{cfg['delegation']}"
            with open(csv_path) as f:
                lines = f.readlines()
                if len(lines) > 1:
                    drift = float(lines[-1].strip().split(',')[3])
                    config_drifts.setdefault(key, []).append(drift)
    
    high_variance = 0
    for cfg, vals in config_drifts.items():
        if len(vals) >= 2:
            mean = sum(vals) / len(vals)
            variance = sum((v - mean) ** 2 for v in vals) / len(vals)
            cv = (variance ** 0.5) / mean if mean > 0 else 0
            if cv > 0.30:  # >30% coefficient of variation
                high_variance += 1
    
    if high_variance > 3:
        print(f"  ⚠️ {high_variance} configs with high variance")
    else:
        print(f"  ✅ Repeat variance acceptable")
    
    # Check 3: Resource availability
    print("[3] Checking resources...")
    import shutil
    free_gb = shutil.disk_usage("/home/admin").free / (1024**3)
    print(f"  Free disk: {free_gb:.1f} GB")
    if free_gb < 5:
        print("  ❌ Insufficient disk space")
        return False
    print("  ✅ Resources OK")
    
    print()
    print("=" * 60)
    print("✅ ALL LAUNCH CONDITIONS MET")
    print("=" * 60)
    return True

def main():
    print("=" * 60)
    print("MULTIVERSE STAGE 2: 32-UNIVERSE LAUNCHER")
    print("=" * 60)
    print()
    print(f"Status: {LAUNCH_STATUS}")
    print()
    
    if LAUNCH_STATUS != "GO":
        print("⚠️  LAUNCH BLOCKED — Status is not 'GO'")
        print()
        print("To launch Stage 2:")
        print("1. Verify Stage 1 v2 stability (drift range, repeat variance)")
        print("2. Edit this file: change LAUNCH_STATUS = 'GO'")
        print("3. Re-run: python3 multiverse_launch_stage2.py")
        print()
        print("Current config preview:")
        configs = generate_stage2_configs()
        print(f"  Total universes: {len(configs)}")
        print(f"  Core configs: 8 (4 P2-zone + 4 P3-zone)")
        print(f"  Repeats per config: 4")
        print()
        print("Core matrix:")
        for i, cfg in enumerate(CORE_CONFIGS, 1):
            print(f"  {i}. P{cfg['pressure']}T{cfg['perturb']}M{cfg['memory']}D{cfg['delegation']}")
        return
    
    # Launch conditions check
    if not check_launch_conditions():
        print()
        print("❌ LAUNCH ABORTED — Conditions not met")
        return
    
    # Proceed with launch
    print()
    print("Proceeding with Stage 2 launch in 5 seconds...")
    time.sleep(5)
    
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    configs = generate_stage2_configs()
    
    launched = []
    for config in configs:
        print(f"Launching universe_{config['id']}...", end=" ")
        try:
            info = launch_universe(config)
            launched.append(info)
            print(f"OK (G1:{info['g1_pid']}, E1:{info['e1_pid']})")
            time.sleep(0.3)
        except Exception as e:
            print(f"FAILED: {e}")
    
    # Write manifest
    manifest = {
        "stage": 2,
        "count": len(launched),
        "timestamp": datetime.now().isoformat(),
        "universes": launched,
        "matrix": CORE_CONFIGS
    }
    with open(BASE_DIR / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print()
    print("=" * 60)
    print(f"LAUNCHED: {len(launched)}/32 universes")
    print("=" * 60)
    print()
    print("Monitor with:")
    print(f"  ls -l {BASE_DIR}/universe_*/")

if __name__ == "__main__":
    main()
