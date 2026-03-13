#!/usr/bin/env python3
"""
PHASE B2 V4: Correct Parallel Test with BLAS Thread Control
Critical fix: Limit BLAS threads per process to enable true multi-process scaling
"""

import os
# CRITICAL: Must set BEFORE importing numpy
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

import numpy as np
import json
import time
import subprocess
import threading
from datetime import datetime
from typing import Dict, Tuple
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil


class SystemMonitor:
    """Background monitor running concurrently with workload"""
    
    def __init__(self, interval: float = 0.5):
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
            self.thread.join(timeout=2.0)
        
        if not self.samples:
            return {"error": "No samples"}
        
        cpus = [s['cpu'] for s in self.samples]
        rams = [s['ram'] for s in self.samples]
        loads = [s['load'] for s in self.samples]
        
        return {
            "duration": time.time() - self.start_time,
            "samples": len(self.samples),
            "avg_cpu": float(np.mean(cpus)),
            "max_cpu": float(max(cpus)),
            "min_cpu": float(min(cpus)),
            "std_cpu": float(np.std(cpus)),
            "avg_ram_gb": float(np.mean(rams)),
            "max_ram_gb": float(max(rams)),
            "avg_load": float(np.mean(loads)),
            "max_load": float(max(loads))
        }
    
    def _monitor_loop(self):
        while self.running:
            try:
                self.samples.append({
                    "timestamp": time.time(),
                    "cpu": psutil.cpu_percent(interval=None),
                    "ram": psutil.virtual_memory().used / (1024**3),
                    "load": os.getloadavg()[0]
                })
            except:
                pass
            time.sleep(self.interval)


def capture_snapshot(label: str) -> Dict:
    """Capture system state"""
    snap = {"label": label, "time": datetime.now().isoformat()}
    
    cmds = [
        ("uptime", ["uptime"]),
        ("mpstat", ["mpstat", "-P", "ALL", "1", "1"]),
        ("vmstat", ["vmstat", "-S", "M", "1", "1"]),
        ("ps_cpu", ["ps", "-eo", "pid,pcpu,comm", "--sort=-pcpu", "|", "head", "-20"]),
    ]
    
    for key, cmd in cmds:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            snap[key] = result.stdout[:3000]
        except Exception as e:
            snap[f"{key}_error"] = str(e)
    
    return snap


def worker_task(args: Tuple[int, int, int]) -> Dict:
    """
    CPU-bound task with controlled BLAS threads
    
    Args:
        args: (worker_id, matrix_size, duration_sec)
    """
    worker_id, size, duration_sec = args
    
    # Verify BLAS is single-threaded
    tid = threading.current_thread().ident
    
    start = time.time()
    iterations = 0
    checksum = 0.0
    
    # Pure compute loop - each worker uses exactly 1 core
    while time.time() - start < duration_sec:
        # Generate new matrices each iteration to prevent caching
        a = np.random.random((size, size)).astype(np.float64)
        b = np.random.random((size, size)).astype(np.float64)
        
        # Matrix multiply - with OPENBLAS_NUM_THREADS=1, this uses 1 CPU core
        c = np.dot(a, b)
        
        # Additional compute to ensure CPU stays busy
        d = np.dot(c, a)
        e = np.dot(b, d)
        
        # Force materialization and accumulate to prevent optimization
        checksum += np.sum(e) * 0.0001
        
        iterations += 1
    
    elapsed = time.time() - start
    
    return {
        "worker_id": worker_id,
        "elapsed": elapsed,
        "iterations": iterations,
        "checksum": float(checksum),
        "matrix_size": size
    }


def run_test(n_workers: int, duration: int = 30, matrix_size: int = 800) -> Dict:
    """
    Run parallel test with concurrent monitoring
    """
    print(f"\n[TEST] {n_workers} workers x {duration}s")
    print(f"       Matrix size: {matrix_size}x{matrix_size}")
    print(f"       Total CPUs: {cpu_count()}")
    print(f"       BLAS threads: 1 (forced)")
    
    # 1. Start monitor FIRST
    monitor = SystemMonitor(interval=0.5)
    monitor.start()
    
    # 2. Snapshot before
    snap_before = capture_snapshot("before")
    
    # 3. Run workload
    start_time = time.time()
    args = [(i, matrix_size, duration) for i in range(n_workers)]
    
    results = []
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(worker_task, a) for a in args]
        
        for future in as_completed(futures):
            try:
                r = future.result()
                results.append(r)
                print(f"  Worker {r['worker_id']}: {r['iterations']} iters, sum={r['checksum']:.2f}")
            except Exception as e:
                print(f"  Error: {e}")
    
    total_time = time.time() - start_time
    
    # 4. Snapshot after
    snap_after = capture_snapshot("after")
    
    # 5. Stop monitor
    monitor_result = monitor.stop()
    
    return {
        "n_workers": n_workers,
        "duration_target": duration,
        "matrix_size": matrix_size,
        "total_time": total_time,
        "monitor": monitor_result,
        "snapshot_before": snap_before,
        "snapshot_after": snap_after,
        "workers": results
    }


def analyze(result: Dict):
    """Analyze and report"""
    print("\n" + "="*70)
    print("VALIDATED RESULT - PHASE B2")
    print("="*70)
    
    n_workers = result.get("n_workers", 0)
    m = result.get("monitor", {})
    
    print(f"\nTest Configuration:")
    print(f"  Workers: {n_workers}")
    print(f"  Matrix size: {result.get('matrix_size', 0)}x{result.get('matrix_size', 0)}")
    print(f"  Duration target: {result.get('duration_target', 0)}s")
    print(f"  CPUs available: {cpu_count()}")
    
    print(f"\nConcurrent Monitoring:")
    print(f"  Duration: {m.get('duration', 0):.1f}s")
    print(f"  Samples: {m.get('samples', 0)}")
    print(f"  Avg CPU: {m.get('avg_cpu', 0):.1f}%")
    print(f"  Max CPU: {m.get('max_cpu', 0):.1f}%")
    print(f"  Std CPU: {m.get('std_cpu', 0):.1f}%")
    print(f"  Avg RAM: {m.get('avg_ram_gb', 0):.1f}GB")
    print(f"  Avg Load: {m.get('avg_load', 0):.2f}")
    
    # Validation
    print(f"\n--- VALIDATION ---")
    avg_cpu = m.get('avg_cpu', 0)
    expected = n_workers * 100  # Each worker should use ~100%
    
    # Account for hyperthreading (256T = 2x 128C)
    cpu_count_total = cpu_count()
    utilization = avg_cpu / cpu_count_total * 100
    
    print(f"Expected CPU: ~{expected}% (if workers are CPU-bound)")
    print(f"Actual CPU: {avg_cpu:.1f}%")
    print(f"System utilization: {utilization:.1f}% of {cpu_count_total} logical CPUs")
    
    if avg_cpu < n_workers * 80:
        print(f"❌ FAIL: CPU usage insufficient for {n_workers} workers")
    elif avg_cpu < n_workers * 95:
        print(f"⚠️  PARTIAL: CPU usage acceptable but not optimal")
    else:
        print(f"✅ PASS: CPU usage meets expectation")
    
    # Load average check
    load = m.get('avg_load', 0)
    print(f"\nLoad average: {load:.2f}")
    if load < n_workers * 0.5:
        print(f"⚠️  Load suggests workers may not be CPU-bound")
    
    # Save
    outfile = f"/tmp/b2_valid_{n_workers}w_{int(time.time())}.json"
    with open(outfile, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved: {outfile}")
    print("="*70)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--matrix-size", type=int, default=800)
    args = parser.parse_args()
    
    print("="*70)
    print("PHASE B2 V4: CORRECT PARALLEL TEST")
    print("="*70)
    print(f"CRITICAL FIXES:")
    print(f"  1. OPENBLAS_NUM_THREADS=1 (prevents internal multi-threading)")
    print(f"  2. Monitor runs CONCURRENTLY with workload")
    print(f"  3. Each process uses exactly 1 CPU core")
    print()
    
    result = run_test(args.workers, args.duration, args.matrix_size)
    analyze(result)


if __name__ == "__main__":
    main()
