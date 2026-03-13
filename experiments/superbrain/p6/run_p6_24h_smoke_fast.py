#!/usr/bin/env python3
"""
P6 24-Hour Smoke Test - FAST MODE (for verification)
=====================================================
This version runs 24 epochs quickly (seconds instead of hours)
for testing the pipeline before the real 24h run.

Real 24h run: Use run_p6_24h_smoke.py
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path

from p6_runner import P6Runner, P6Config, RunnerState


def setup_fast_config() -> P6Config:
    """Fast mode: 24 epochs, 1 second each (simulated)"""
    return P6Config(
        duration_hours=24,
        epoch_minutes=60,
        anomaly_injection_rate=0.1,
        checkpoint_interval=1
    )


def run_24h_smoke_fast():
    """Execute fast 24h smoke test (simulated)"""
    print("="*60)
    print("P6 24-HOUR SMOKE TEST (FAST MODE)")
    print("="*60)
    print("⚠️  This is a fast simulation for pipeline testing")
    print("⚠️  For real 24h run: python3 run_p6_24h_smoke.py")
    print("")
    
    config = setup_fast_config()
    runner = P6Runner(config)
    
    print(f"Configuration:")
    print(f"  Duration: {config.duration_hours} hours (simulated)")
    print(f"  Epochs: {config.total_epochs}")
    print(f"  Epoch time: ~1 second (simulated)")
    print(f"  Total run time: ~{config.total_epochs} seconds")
    print("")
    
    start_time = time.time()
    result = runner.run()
    elapsed = time.time() - start_time
    
    # Save results
    runner.save_final_results(result)
    
    # Summary
    print("")
    print("="*60)
    print("FAST SIMULATION COMPLETE")
    print("="*60)
    print(f"State: {result.state.name}")
    print(f"Verdict: {result.verdict}")
    print(f"Epochs: {len(result.epochs)}/{config.total_epochs}")
    print(f"Simulated time: {config.total_epochs} hours")
    print(f"Actual time: {elapsed:.2f} seconds")
    
    if result.stop_reason:
        print(f"⚠️  STOPPED: {result.stop_reason}")
    
    # Verify all epochs completed
    if len(result.epochs) == 24 and result.state == RunnerState.COMPLETE:
        print("✅ PASS: All 24 epochs completed")
        
        # Additional checks
        drift_count = sum(1 for e in result.epochs if e.metrics.core_drift)
        print(f"   Core drift epochs: {drift_count}/24")
        
        avg_recall = sum(e.metrics.detector_recall for e in result.epochs) / 24
        print(f"   Avg detector recall: {avg_recall:.2%}")
        
        avg_diversity = sum(e.metrics.capability_diversity for e in result.epochs) / 24
        print(f"   Avg capability diversity: {avg_diversity:.2%}")
        
        avg_overhead = sum(e.metrics.maintenance_overhead for e in result.epochs) / 24
        print(f"   Avg maintenance overhead: {avg_overhead:.2%}")
        
        print("")
        print("✅ Pipeline ready for real 24h run")
        print("   Command: python3 run_p6_24h_smoke.py")
        return True
    else:
        print("❌ FAIL: Did not complete all epochs")
        return False


if __name__ == "__main__":
    success = run_24h_smoke_fast()
    sys.exit(0 if success else 1)
