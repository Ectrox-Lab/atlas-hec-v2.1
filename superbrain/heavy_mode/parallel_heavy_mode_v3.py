#!/usr/bin/env python3
"""
PHASE B2 V3: CPU-intensive Parallel Heavy Mode
Fixes:
1. Monitor runs CONCURRENTLY with workload
2. True CPU-bound computation (matrix operations, not memory-bound)
3. System-level metrics (mpstat, vmstat, uptime, ps)
4. Clear distinction: single-worker vs multi-instance vs concurrent
"""

import numpy as np
import json
import time
import os
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Tuple
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil


class SystemMonitor:
    """背景監控 - 與 workload 同時運行"""
    
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
            "avg_ram_gb": float(np.mean(rams)),
            "max_ram_gb": float(max(rams)),
            "avg_load": float(np.mean(loads))
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


def capture_system_snapshot(label: str) -> Dict:
    """捕獲完整系統快照"""
    snap = {"label": label, "time": datetime.now().isoformat()}
    
    cmds = {
        "uptime": ["uptime"],
        "mpstat": ["mpstat", "-P", "ALL", "1", "1"],
        "vmstat": ["vmstat", "-S", "M", "1", "2"],
        "ps_cpu": ["ps", "-eo", "pid,pcpu,rss,comm", "--sort=-pcpu"],
        "ps_ram": ["ps", "-eo", "pid,pmem,rss,comm", "--sort=-rss"],
        "top_mem": ["cat", "/proc/meminfo"]
    }
    
    for key, cmd in cmds.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            snap[key] = result.stdout[:2000]  # 限制輸出大小
        except Exception as e:
            snap[f"{key}_error"] = str(e)
    
    return snap


def cpu_intensive_task(args: Tuple[int, int]) -> Dict:
    """
    CPU-bound 計算任務 - 專門設計來吃滿單核心
    
    使用多次矩陣乘法來確保 CPU 不會閒置等待內存
    """
    worker_id, duration_sec = args
    
    start = time.time()
    iterations = 0
    
    # 使用 float64 增加計算密度
    size = 500
    
    while time.time() - start < duration_sec:
        # 矩陣乘法 - 純 CPU 計算，不受內存帶寬限制
        a = np.random.random((size, size))
        b = np.random.random((size, size))
        
        # 多次乘法以增加計算密度
        for _ in range(5):
            c = np.dot(a, b)
            a = c + np.random.random((size, size)) * 0.001
        
        # SVD 分解 - 高計算複雜度
        if iterations % 10 == 0:
            u, s, vh = np.linalg.svd(a[:100, :100])
        
        iterations += 1
    
    elapsed = time.time() - start
    
    return {
        "worker_id": worker_id,
        "elapsed": elapsed,
        "iterations": iterations,
        "flops_estimate": iterations * size**3 * 2  # 粗略估算
    }


def launch_workers(n_workers: int, duration_sec: int = 30) -> Dict:
    """
    啟動 n 個 worker 並行運行，監控與 workload 同時執行
    """
    print(f"\n[LAUNCH] {n_workers} workers, {duration_sec}s each")
    print(f"         Total CPUs: {cpu_count()}")
    
    # 1. 啟動監控（在 workload 之前）
    monitor = SystemMonitor(interval=0.5)
    monitor.start()
    
    # 2. 捕獲前狀態
    snap_before = capture_system_snapshot("before")
    
    # 3. 運行 workload
    start = time.time()
    args = [(i, duration_sec) for i in range(n_workers)]
    
    results = []
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(cpu_intensive_task, a) for a in args]
        
        for future in as_completed(futures):
            try:
                r = future.result()
                results.append(r)
                print(f"  Worker {r['worker_id']}: {r['elapsed']:.1f}s, {r['iterations']} iters")
            except Exception as e:
                print(f"  Error: {e}")
    
    total_time = time.time() - start
    
    # 4. 捕獲後狀態
    snap_after = capture_system_snapshot("after")
    
    # 5. 停止監控
    monitor_result = monitor.stop()
    
    return {
        "n_workers": n_workers,
        "duration_target": duration_sec,
        "total_time": total_time,
        "monitor": monitor_result,
        "snapshot_before": snap_before,
        "snapshot_after": snap_after,
        "workers": results
    }


def analyze_result(result: Dict):
    """分析並報告結果"""
    print("\n" + "="*70)
    print("VALIDATED RESULT")
    print("="*70)
    
    m = result.get("monitor", {})
    n_workers = result.get("n_workers", 0)
    
    print(f"\nConfiguration:")
    print(f"  Workers launched: {n_workers}")
    print(f"  CPUs available: {cpu_count()}")
    print(f"  Utilization target: {n_workers * 100 / cpu_count() * 100:.0f}% of total")
    
    print(f"\nMonitoring (CONCURRENT with workload):")
    print(f"  Duration: {m.get('duration', 0):.1f}s")
    print(f"  Samples: {m.get('samples', 0)}")
    print(f"  Avg CPU: {m.get('avg_cpu', 0):.1f}%")
    print(f"  Max CPU: {m.get('max_cpu', 0):.1f}%")
    print(f"  Avg RAM: {m.get('avg_ram_gb', 0):.1f}GB")
    print(f"  Max RAM: {m.get('max_ram_gb', 0):.1f}GB")
    print(f"  Avg Load: {m.get('avg_load', 0):.2f}")
    
    # 判定
    print(f"\n--- VALIDATION ---")
    avg_cpu = m.get('avg_cpu', 0)
    target = n_workers * 100
    
    if avg_cpu < target * 0.5:
        print(f"❌ FAIL: Avg CPU {avg_cpu:.1f}% << target ~{target}%")
        print(f"   Workers not utilizing cores effectively")
    elif avg_cpu < target * 0.8:
        print(f"⚠️  PARTIAL: Avg CPU {avg_cpu:.1f}% < target ~{target}%")
    else:
        print(f"✅ PASS: Avg CPU {avg_cpu:.1f}% ≈ target ~{target}%")
    
    # 系統狀態對比
    before = result.get("snapshot_before", {})
    after = result.get("snapshot_after", {})
    
    print(f"\nSystem State:")
    if "uptime" in before:
        print(f"  Before: {before['uptime'][:60]}...")
    if "uptime" in after:
        print(f"  After:  {after['uptime'][:60]}...")
    
    # 保存結果
    outfile = f"/tmp/valid_test_{n_workers}w_{int(time.time())}.json"
    with open(outfile, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nSaved: {outfile}")
    print("="*70)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()
    
    print("="*70)
    print("PHASE B2 V3: VALIDATED PARALLEL TEST")
    print("="*70)
    print(f"CRITICAL: Monitor runs CONCURRENTLY with workload")
    print(f"          NOT before/after")
    print()
    
    result = launch_workers(args.workers, args.duration)
    analyze_result(result)


if __name__ == "__main__":
    main()
