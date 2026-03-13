#!/usr/bin/env python3
"""
PHASE B2 V5: Correct Parallel Test with accurate CPU measurement
Uses /proc/stat for accurate CPU measurement instead of psutil
"""

import os
# Force single-threaded BLAS
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

import numpy as np
import json
import time
import threading
from datetime import datetime
from typing import Dict, Tuple
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


def read_cpu_stats() -> Dict:
    """Read CPU stats from /proc/stat"""
    stats = {}
    with open('/proc/stat', 'r') as f:
        for line in f:
            if line.startswith('cpu'):
                parts = line.split()
                name = parts[0]
                # user, nice, system, idle, iowait, irq, softirq
                values = [int(x) for x in parts[1:8]]
                stats[name] = values
    return stats


def calculate_cpu_percent(prev: Dict, curr: Dict) -> float:
    """Calculate overall CPU percentage"""
    if 'cpu' not in prev or 'cpu' not in curr:
        return 0.0
    
    prev_total = sum(prev['cpu'])
    curr_total = sum(curr['cpu'])
    
    prev_idle = prev['cpu'][3] + prev['cpu'][4]  # idle + iowait
    curr_idle = curr['cpu'][3] + curr['cpu'][4]
    
    total_diff = curr_total - prev_total
    idle_diff = curr_idle - prev_idle
    
    if total_diff == 0:
        return 0.0
    
    return (1.0 - idle_diff / total_diff) * 100.0


class AccurateMonitor:
    """Monitor using /proc/stat for accurate CPU measurement"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.running = False
        self.samples = []
        self.thread = None
        self.start_time = None
        
    def start(self):
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self) -> Dict:
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        
        if not self.samples:
            return {"error": "No samples"}
        
        cpus = [s['cpu_percent'] for s in self.samples]
        loads = [s['load'] for s in self.samples]
        
        # Calculate per-cpu average
        avg_per_cpu = np.mean(cpus) if cpus else 0
        # Scale to show as percentage of single core (like top)
        # But wait, /proc/stat already gives us overall %, multiply by n_cpus
        n_cpus = cpu_count()
        scaled_cpu = avg_per_cpu  # Keep as overall %
        
        return {
            "duration": time.time() - self.start_time,
            "samples": len(self.samples),
            "avg_cpu_percent": float(np.mean(cpus)),
            "max_cpu_percent": float(max(cpus)) if cpus else 0,
            "min_cpu_percent": float(min(cpus)) if cpus else 0,
            "avg_load": float(np.mean(loads)) if loads else 0,
            "max_load": float(max(loads)) if loads else 0,
            "cpu_count": n_cpus,
            "interpretation": f"{avg_per_cpu:.1f}% = {avg_per_cpu/n_cpus:.1f}% per core average"
        }
    
    def _monitor_loop(self):
        prev_stats = read_cpu_stats()
        
        while self.running:
            time.sleep(self.interval)
            
            try:
                curr_stats = read_cpu_stats()
                cpu_pct = calculate_cpu_percent(prev_stats, curr_stats)
                load = os.getloadavg()[0]
                
                self.samples.append({
                    "timestamp": time.time(),
                    "cpu_percent": cpu_pct,
                    "load": load
                })
                
                prev_stats = curr_stats
            except Exception as e:
                print(f"[MONITOR] Error: {e}")


def worker_task(args: Tuple[int, int, int]) -> Dict:
    """
    CPU-bound task
    
    Args:
        args: (worker_id, matrix_size, duration_sec)
    """
    worker_id, size, duration_sec = args
    
    start = time.time()
    iterations = 0
    checksum = 0.0
    
    # Heavy compute loop
    while time.time() - start < duration_sec:
        a = np.random.random((size, size)).astype(np.float64)
        b = np.random.random((size, size)).astype(np.float64)
        
        c = np.dot(a, b)
        d = np.dot(c, a)
        e = np.dot(b, d)
        
        checksum += np.sum(e) * 0.0001
        iterations += 1
    
    elapsed = time.time() - start
    
    return {
        "worker_id": worker_id,
        "elapsed": elapsed,
        "iterations": iterations,
        "checksum": float(checksum)
    }


def run_test(n_workers: int, duration: int = 30, matrix_size: int = 1000) -> Dict:
    """
    Run parallel test
    """
    print(f"\n[TEST] {n_workers} workers x {duration}s")
    print(f"       Matrix: {matrix_size}x{matrix_size}")
    print(f"       CPUs: {cpu_count()}")
    print(f"       BLAS threads: 1")
    
    # Start monitor
    monitor = AccurateMonitor(interval=1.0)
    monitor.start()
    
    # Run workload
    start_time = time.time()
    args = [(i, matrix_size, duration) for i in range(n_workers)]
    
    results = []
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(worker_task, a) for a in args]
        
        for future in as_completed(futures):
            try:
                r = future.result()
                results.append(r)
                print(f"  Worker {r['worker_id']}: {r['iterations']} iters")
            except Exception as e:
                print(f"  Error: {e}")
    
    total_time = time.time() - start_time
    
    # Stop monitor
    monitor_result = monitor.stop()
    
    return {
        "n_workers": n_workers,
        "duration_target": duration,
        "matrix_size": matrix_size,
        "total_time": total_time,
        "monitor": monitor_result,
        "workers": results
    }


def analyze(result: Dict):
    """Analyze and report"""
    print("\n" + "="*70)
    print("VALIDATED RESULT - PHASE B2 V5")
    print("="*70)
    
    n_workers = result.get("n_workers", 0)
    m = result.get("monitor", {})
    n_cpus = cpu_count()
    
    print(f"\nConfiguration:")
    print(f"  Workers: {n_workers}")
    print(f"  CPUs: {n_cpus}")
    
    print(f"\nMonitoring (/proc/stat):")
    print(f"  Duration: {m.get('duration', 0):.1f}s")
    print(f"  Samples: {m.get('samples', 0)}")
    
    avg_pct = m.get('avg_cpu_percent', 0)
    max_pct = m.get('max_cpu_percent', 0)
    
    print(f"  Avg CPU: {avg_pct:.1f}%")
    print(f"  Max CPU: {max_pct:.1f}%")
    print(f"  Avg Load: {m.get('avg_load', 0):.2f}")
    print(f"  Max Load: {m.get('max_load', 0):.2f}")
    
    # Validation
    print(f"\n--- VALIDATION ---")
    # With n_workers processes using single-threaded BLAS,
    # we expect ~n_workers * 100% CPU (in top's terms, this would be n_workers * 100 / n_cpus %)
    # But /proc/stat gives overall %, so 100% = all cores busy
    
    expected_overall = (n_workers / n_cpus) * 100
    actual_overall = avg_pct
    
    print(f"Expected overall CPU: ~{expected_overall:.1f}% ({n_workers}/{n_cpus} cores)")
    print(f"Actual overall CPU: {actual_overall:.1f}%")
    
    # Per-core utilization
    per_core = avg_pct / 100 * n_cpus
    print(f"Per-core utilization: {per_core:.1f}% equivalent")
    
    if per_core < n_workers * 0.5:
        print(f"❌ FAIL: CPU usage too low")
    elif per_core < n_workers * 0.8:
        print(f"⚠️  PARTIAL: CPU usage below optimal")
    else:
        print(f"✅ PASS: CPU usage good")
    
    # Save
    outfile = f"/tmp/b2_v5_{n_workers}w_{int(time.time())}.json"
    with open(outfile, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved: {outfile}")
    print("="*70)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--matrix-size", type=int, default=1000)
    args = parser.parse_args()
    
    print("="*70)
    print("PHASE B2 V5: ACCURATE PARALLEL TEST")
    print("="*70)
    print(f"Using /proc/stat for accurate CPU measurement")
    print()
    
    result = run_test(args.workers, args.duration, args.matrix_size)
    analyze(result)


if __name__ == "__main__":
    main()
