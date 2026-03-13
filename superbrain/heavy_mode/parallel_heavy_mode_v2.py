#!/usr/bin/env python3
"""
PHASE B2 V2: Correct Parallel Heavy Mode with Valid Monitoring
Fixes:
1. Monitor runs CONCURRENTLY with workload (not before)
2. True parallel instance launch (not sequential)
3. System-level metrics (mpstat, vmstat, ps)
"""

import numpy as np
import json
import time
import gc
import os
import sys
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from multiprocessing import Pool, cpu_count, Process
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil


class SystemMonitor:
    """
    正確的系統監控 - 在背景運行，與 workload 同時執行
    """
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.running = False
        self.samples = []
        self.thread = None
        self.start_time = None
        
    def start(self):
        """啟動背景監控線程"""
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self) -> Dict:
        """停止監控並返回結果"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if not self.samples:
            return {"error": "No samples collected"}
        
        cpu_samples = [s['cpu_percent'] for s in self.samples]
        ram_samples = [s['ram_gb'] for s in self.samples]
        load_samples = [s.get('load_avg', 0) for s in self.samples]
        
        return {
            "duration": time.time() - self.start_time,
            "samples": len(self.samples),
            "avg_cpu": float(np.mean(cpu_samples)),
            "max_cpu": float(max(cpu_samples)),
            "min_cpu": float(min(cpu_samples)),
            "avg_ram_gb": float(np.mean(ram_samples)),
            "max_ram_gb": float(max(ram_samples)),
            "avg_load": float(np.mean(load_samples)) if load_samples else 0,
            "raw_samples": self.samples[:10]  # 前10個樣本用於調試
        }
    
    def _monitor_loop(self):
        """監控循環 - 在背景執行"""
        while self.running:
            try:
                sample = {
                    "timestamp": time.time(),
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "ram_gb": psutil.virtual_memory().used / (1024**3),
                    "load_avg": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
                }
                self.samples.append(sample)
            except Exception as e:
                print(f"[MONITOR] Error: {e}")
            
            time.sleep(self.interval)


def capture_system_state(label: str) -> Dict:
    """
    捕獲系統級狀態快照
    """
    state = {"label": label, "timestamp": datetime.now().isoformat()}
    
    # 1. uptime
    try:
        uptime_output = subprocess.run(
            ["uptime"], capture_output=True, text=True, timeout=2
        )
        state["uptime"] = uptime_output.stdout.strip()
    except Exception as e:
        state["uptime_error"] = str(e)
    
    # 2. mpstat (所有 CPU)
    try:
        mpstat_output = subprocess.run(
            ["mpstat", "-P", "ALL", "1", "1"],
            capture_output=True, text=True, timeout=5
        )
        state["mpstat"] = mpstat_output.stdout
    except Exception as e:
        state["mpstat_error"] = str(e)
    
    # 3. vmstat
    try:
        vmstat_output = subprocess.run(
            ["vmstat", "-S", "M"],
            capture_output=True, text=True, timeout=2
        )
        state["vmstat"] = vmstat_output.stdout
    except Exception as e:
        state["vmstat_error"] = str(e)
    
    # 4. Top processes by CPU
    try:
        ps_cpu_output = subprocess.run(
            ["ps", "-eo", "pid,pcpu,pmem,rss,comm", "--sort=-pcpu"],
            capture_output=True, text=True, timeout=2
        )
        state["top_cpu_processes"] = ps_cpu_output.stdout.split('\n')[:20]
    except Exception as e:
        state["ps_cpu_error"] = str(e)
    
    # 5. Top processes by RAM
    try:
        ps_ram_output = subprocess.run(
            ["ps", "-eo", "pid,pcpu,pmem,rss,comm", "--sort=-rss"],
            capture_output=True, text=True, timeout=2
        )
        state["top_ram_processes"] = ps_ram_output.stdout.split('\n')[:20]
    except Exception as e:
        state["ps_ram_error"] = str(e)
    
    # 6. 計數 python 進程
    try:
        python_procs = subprocess.run(
            ["pgrep", "-c", "python"],
            capture_output=True, text=True, timeout=2
        )
        state["python_processes"] = int(python_procs.stdout.strip())
    except:
        state["python_processes"] = 0
    
    return state


class ParallelHeavyWorker:
    """單個 worker - 處理一批候選者"""
    
    def __init__(self, worker_id: int, n_candidates: int = 5000):
        self.worker_id = worker_id
        self.n_candidates = n_candidates
        
    def run_heavy_computation(self) -> Dict:
        """運行重計算 - 更重的負載"""
        start = time.time()
        
        # 增加計算量以確保單 worker 能吃滿一個核心
        n = self.n_candidates
        chunk_size = 1000
        
        total_flops = 0
        memory_peak = 0
        
        # 多次迭代以增加 CPU 負載
        for iteration in range(3):
            for i in range(0, n, chunk_size):
                end_i = min(i + chunk_size, n)
                size = end_i - i
                
                # 生成向量
                vectors = np.random.random((size, 128)).astype(np.float32)
                all_vectors = np.random.random((n, 128)).astype(np.float32)
                
                # 計算距離矩陣 (主要計算)
                diff = vectors[:, np.newaxis, :] - all_vectors[np.newaxis, :, :]
                distances = np.sqrt(np.sum(diff**2, axis=2))
                
                # 強制同步以確保計算完成
                total_flops += distances.size
                memory_peak = max(memory_peak, distances.nbytes)
                
                # 一些額外計算以增加 CPU 時間
                _ = np.argsort(distances, axis=1)[:, :10]
        
        elapsed = time.time() - start
        
        return {
            "worker_id": self.worker_id,
            "elapsed": elapsed,
            "total_flops": int(total_flops),
            "memory_peak_mb": memory_peak / (1024**2),
            "cpu_time": elapsed  # 近似 CPU 時間
        }


def run_worker_task(args: Tuple[int, int]) -> Dict:
    """模塊級 worker 函數 (可 pickle)"""
    worker_id, n_candidates = args
    worker = ParallelHeavyWorker(worker_id, n_candidates)
    return worker.run_heavy_computation()


def launch_parallel_workers(n_workers: int = 16, n_candidates: int = 5000) -> Dict:
    """
    啟動多進程並行 workers - 正確實現
    """
    print(f"\n[PHASE-B2] Launching {n_workers} parallel workers")
    print(f"           Each: {n_candidates} candidates, 3 iterations")
    print(f"           CPUs: {cpu_count()}")
    
    # 1. 啟動背景監控
    monitor = SystemMonitor(interval=0.5)
    monitor.start()
    
    # 2. 捕獲系統狀態 (workload 前)
    state_before = capture_system_state("before_workload")
    
    # 3. 運行 workload
    start_time = time.time()
    worker_args = [(i, n_candidates) for i in range(n_workers)]
    
    results = []
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(run_worker_task, args) for args in worker_args]
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                print(f"  Worker {result['worker_id']}: {result['elapsed']:.1f}s, "
                      f"{result['total_flops']/1e9:.1f} GFLOPs")
            except Exception as e:
                print(f"  Worker failed: {e}")
    
    total_time = time.time() - start_time
    
    # 4. 捕獲系統狀態 (workload 後)
    state_after = capture_system_state("after_workload")
    
    # 5. 停止監控
    monitor_result = monitor.stop()
    
    # 6. 統計
    if results:
        total_memory = sum(r.get("memory_peak_mb", 0) for r in results) / 1024
        avg_time = np.mean([r["elapsed"] for r in results])
        total_flops = sum(r.get("total_flops", 0) for r in results)
    else:
        total_memory = avg_time = total_flops = 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "n_workers": n_workers,
        "n_candidates": n_candidates,
        "total_time": total_time,
        "avg_worker_time": avg_time,
        "total_memory_gb": total_memory,
        "total_flops": int(total_flops),
        "throughput": total_flops / total_time if total_time > 0 else 0,
        "monitor": monitor_result,
        "state_before": state_before,
        "state_after": state_after,
        "worker_results": results
    }


def launch_multi_instance_concurrent(n_instances: int = 8, workers_per_instance: int = 4) -> Dict:
    """
    真正的並行多實例啟動 - 使用進程池而非順序循環
    """
    print(f"\n[PHASE-B2] Multi-Instance CONCURRENT Mode")
    print(f"           Instances: {n_instances}")
    print(f"           Workers/instance: {workers_per_instance}")
    print(f"           TOTAL workers: {n_instances * workers_per_instance}")
    
    # 啟動背景監控
    monitor = SystemMonitor(interval=0.5)
    monitor.start()
    
    # 捕獲狀態前
    state_before = capture_system_state("before_multi")
    
    start_time = time.time()
    
    # 計算總 worker 數並一次性啟動
    total_workers = n_instances * workers_per_instance
    
    # 這裡直接使用 ProcessPoolExecutor 而非順序啟動
    # 這樣才是真正的並行
    worker_args = [(i, 3000) for i in range(total_workers)]  # 減少每個worker的負載
    
    results = []
    # 關鍵：max_workers = total_workers 確保全部並行
    with ProcessPoolExecutor(max_workers=total_workers) as executor:
        futures = [executor.submit(run_worker_task, args) for args in worker_args]
        
        completed = 0
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                completed += 1
                if completed % 4 == 0:
                    print(f"  Progress: {completed}/{total_workers} workers complete")
            except Exception as e:
                print(f"  Worker failed: {e}")
    
    total_time = time.time() - start_time
    
    # 捕獲狀態後
    state_after = capture_system_state("after_multi")
    
    # 停止監控
    monitor_result = monitor.stop()
    
    return {
        "mode": "multi_instance_concurrent",
        "n_instances": n_instances,
        "workers_per_instance": workers_per_instance,
        "total_workers": total_workers,
        "total_time": total_time,
        "monitor": monitor_result,
        "state_before": state_before,
        "state_after": state_after,
        "worker_results": results
    }


def main():
    """主入口 - 修正版本"""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["single", "parallel", "multi"], default="parallel")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--instances", type=int, default=8)
    parser.add_argument("--candidates", type=int, default=5000)
    args = parser.parse_args()
    
    print("="*70)
    print("PHASE B2 V2: CORRECT PARALLEL MONITORING")
    print("="*70)
    print(f"Mode: {args.mode}")
    print(f"CRITICAL FIX: Monitor runs CONCURRENTLY with workload")
    print()
    
    if args.mode == "single":
        result = ParallelHeavyWorker(0, args.candidates).run_heavy_computation()
        print(f"Single worker: {result['elapsed']:.1f}s")
    elif args.mode == "parallel":
        result = launch_parallel_workers(args.workers, args.candidates)
    else:  # multi
        result = launch_multi_instance_concurrent(args.instances, 4)
    
    # 報告
    print("\n" + "="*70)
    print("VALIDATED REPORT")
    print("="*70)
    
    if "monitor" in result:
        m = result["monitor"]
        print(f"\nMonitoring Method: CONCURRENT (correct)")
        print(f"Duration: {m.get('duration', 0):.1f}s")
        print(f"Samples: {m.get('samples', 0)}")
        print(f"  Avg CPU: {m.get('avg_cpu', 0):.1f}%")
        print(f"  Max CPU: {m.get('max_cpu', 0):.1f}%")
        print(f"  Avg RAM: {m.get('avg_ram_gb', 0):.1f}GB")
        print(f"  Max RAM: {m.get('max_ram_gb', 0):.1f}GB")
        print(f"  Avg Load: {m.get('avg_load', 0):.2f}")
        
        # 關鍵判定
        print("\n--- VALIDATION ---")
        if m.get('avg_cpu', 0) < 100:
            print("⚠️  FAIL: Avg CPU < 100% - Workload not stressing system")
        elif m.get('avg_cpu', 0) < 800:
            print(f"⚠️  PARTIAL: Avg CPU {m['avg_cpu']:.1f}% - Below 800% target")
        else:
            print(f"✓ PASS: Avg CPU {m['avg_cpu']:.1f}% - Target met")
    
    # 系統狀態對比
    if "state_before" in result and "state_after" in result:
        before_py = result["state_before"].get("python_processes", 0)
        after_py = result["state_after"].get("python_processes", 0)
        print(f"\nPython processes: {before_py} -> {after_py}")
    
    # 保存
    output_file = f"/tmp/parallel_heavy_v2_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nFull results: {output_file}")
    print("="*70)


if __name__ == "__main__":
    main()
