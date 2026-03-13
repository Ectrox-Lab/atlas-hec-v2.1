#!/usr/bin/env python3
"""
PHASE B2: Parallel Heavy Mode - Full Machine Utilization
Target: CPU > 800%, RAM > 64GB on 128C/512GB machine
"""

import numpy as np
import json
import time
import gc
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from multiprocessing import Pool, cpu_count, Process, Queue
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil

class ParallelHeavyWorker:
    """單個worker - 處理一批候選者"""
    
    def __init__(self, worker_id: int, n_candidates: int = 5000):
        self.worker_id = worker_id
        self.n_candidates = n_candidates
        self.results = []
        
    def compute_chunk(self, chunk_data: Tuple[int, int]) -> Dict:
        """計算一塊距離矩陣"""
        start_idx, end_idx = chunk_data
        n = self.n_candidates
        
        # 生成隨機向量
        vectors = np.random.random((end_idx - start_idx, 128)).astype(np.float32)
        all_vectors = np.random.random((n, 128)).astype(np.float32)
        
        # 計算距離
        diff = vectors[:, np.newaxis, :] - all_vectors[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff**2, axis=2))
        
        return {
            "worker_id": self.worker_id,
            "chunk": (start_idx, end_idx),
            "mean_dist": float(np.mean(distances)),
            "max_dist": float(np.max(distances)),
            "memory_mb": distances.nbytes / (1024**2)
        }
    
    def run_heavy_computation(self) -> Dict:
        """運行重計算"""
        start = time.time()
        
        # 分塊計算 - 每塊1000
        chunk_size = 1000
        chunks = [
            (i, min(i + chunk_size, self.n_candidates))
            for i in range(0, self.n_candidates, chunk_size)
        ]
        
        # 順序計算所有塊 (在單worker內)
        results = []
        for chunk in chunks:
            result = self.compute_chunk(chunk)
            results.append(result)
        
        elapsed = time.time() - start
        
        return {
            "worker_id": self.worker_id,
            "elapsed": elapsed,
            "chunks": len(chunks),
            "total_memory_mb": sum(r["memory_mb"] for r in results),
            "mean_dist": np.mean([r["mean_dist"] for r in results])
        }


def run_worker_task(args: Tuple[int, int]) -> Dict:
    """
    模塊級別的worker函數 (可pickle)
    
    Args:
        args: (worker_id, n_candidates_per_worker)
    """
    worker_id, n_candidates = args
    worker = ParallelHeavyWorker(worker_id, n_candidates)
    return worker.run_heavy_computation()


def launch_parallel_workers(n_workers: int = 16, n_candidates_per_worker: int = 5000) -> Dict:
    """
    Phase B2: 啟動多進程並行 workers
    
    Args:
        n_workers: 並行worker數量 (建議 16-32)
        n_candidates_per_worker: 每個worker處理的候選者數量
    """
    print(f"\n[PHASE-B2] Launching {n_workers} parallel workers")
    print(f"           Each worker: {n_candidates_per_worker} candidates")
    print(f"           Total candidates: {n_workers * n_candidates_per_worker}")
    print(f"           Available CPUs: {cpu_count()}")
    
    start_time = time.time()
    
    # 準備參數
    worker_args = [(i, n_candidates_per_worker) for i in range(n_workers)]
    
    # 使用進程池
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        # 提交所有worker (使用模塊級函數)
        futures = [executor.submit(run_worker_task, args) for args in worker_args]
        
        # 收集結果
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                print(f"  Worker {result['worker_id']} complete: {result['elapsed']:.1f}s, "
                      f"RAM: {result['total_memory_mb']:.0f}MB")
            except Exception as e:
                print(f"  Worker failed: {e}")
    
    total_time = time.time() - start_time
    
    # 統計
    if results:
        total_memory = sum(r.get("total_memory_mb", 0) for r in results) / 1024  # GB
        avg_time = np.mean([r["elapsed"] for r in results])
        throughput = (n_workers * n_candidates_per_worker) / total_time if total_time > 0 else 0
    else:
        total_memory = 0
        avg_time = 0
        throughput = 0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "n_workers": n_workers,
        "n_candidates_per_worker": n_candidates_per_worker,
        "total_candidates": n_workers * n_candidates_per_worker,
        "total_time": total_time,
        "avg_worker_time": avg_time,
        "total_memory_gb": total_memory,
        "throughput": throughput,
        "worker_results": results
    }


def launch_multi_instance(n_instances: int = 8, n_workers_per_instance: int = 4) -> Dict:
    """
    更激進的方案：多實例 + 每實例多worker
    """
    print(f"\n[PHASE-B2] Multi-Instance Mode")
    print(f"           Instances: {n_instances}")
    print(f"           Workers per instance: {n_workers_per_instance}")
    print(f"           Total parallelism: {n_instances * n_workers_per_instance}")
    
    start_time = time.time()
    
    # 這裡簡化為順序啟動多個並行池
    all_results = []
    for instance_id in range(n_instances):
        print(f"\n[Instance {instance_id+1}/{n_instances}]")
        result = launch_parallel_workers(
            n_workers=n_workers_per_instance,
            n_candidates_per_worker=5000
        )
        all_results.append(result)
    
    total_time = time.time() - start_time
    
    return {
        "n_instances": n_instances,
        "total_time": total_time,
        "instance_results": all_results
    }


def monitor_resources(duration: int = 60) -> Dict:
    """
    監控系統資源使用
    """
    print(f"\n[MONITOR] Monitoring for {duration}s...")
    
    cpu_samples = []
    ram_samples = []
    
    start = time.time()
    while time.time() - start < duration:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().used / (1024**3)
        cpu_samples.append(cpu)
        ram_samples.append(ram)
        
        if len(cpu_samples) % 10 == 0:
            print(f"  CPU: {cpu:.1f}%, RAM: {ram:.1f}GB")
    
    return {
        "avg_cpu": np.mean(cpu_samples),
        "max_cpu": max(cpu_samples),
        "avg_ram_gb": np.mean(ram_samples),
        "max_ram_gb": max(ram_samples),
        "samples": len(cpu_samples)
    }


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["single", "parallel", "multi"], default="parallel")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--candidates", type=int, default=5000)
    parser.add_argument("--monitor", type=int, default=30)
    args = parser.parse_args()
    
    print("="*70)
    print("PHASE B2: PARALLEL HEAVY MODE - FULL MACHINE UTILIZATION")
    print("="*70)
    print(f"Target: CPU > 800%, RAM > 64GB")
    print(f"Mode: {args.mode}")
    print()
    
    # 啟動資源監控 (背景)
    monitor_result = monitor_resources(duration=args.monitor)
    
    # 運行主測試
    if args.mode == "single":
        result = ParallelHeavyWorker(0, args.candidates).run_heavy_computation()
    elif args.mode == "parallel":
        result = launch_parallel_workers(args.workers, args.candidates)
    else:  # multi
        result = launch_multi_instance(4, 4)
    
    # 最終報告
    print("\n" + "="*70)
    print("FINAL REPORT")
    print("="*70)
    
    print(f"\nResource Usage:")
    print(f"  Avg CPU: {monitor_result['avg_cpu']:.1f}%")
    print(f"  Max CPU: {monitor_result['max_cpu']:.1f}%")
    print(f"  Avg RAM: {monitor_result['avg_ram_gb']:.1f}GB")
    print(f"  Max RAM: {monitor_result['max_ram_gb']:.1f}GB")
    
    if args.mode in ["parallel", "multi"]:
        print(f"\nParallel Performance:")
        print(f"  Total time: {result['total_time']:.1f}s")
        print(f"  Throughput: {result['throughput']:.1f} candidates/s")
        print(f"  Total memory: {result['total_memory_gb']:.1f}GB")
    
    # 保存結果
    output_file = f"/tmp/parallel_heavy_result_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "monitor": monitor_result,
            "result": result
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("="*70)
    
    # 判定是否達標
    if monitor_result['avg_cpu'] < 800:
        print(f"\n⚠️  CPU utilization LOW: {monitor_result['avg_cpu']:.1f}% (target: >800%)")
    else:
        print(f"\n✓ CPU utilization GOOD: {monitor_result['avg_cpu']:.1f}%")
        
    if monitor_result['avg_ram_gb'] < 64:
        print(f"⚠️  RAM utilization LOW: {monitor_result['avg_ram_gb']:.1f}GB (target: >64GB)")
    else:
        print(f"✓ RAM utilization GOOD: {monitor_result['avg_ram_gb']:.1f}GB")


if __name__ == "__main__":
    main()
