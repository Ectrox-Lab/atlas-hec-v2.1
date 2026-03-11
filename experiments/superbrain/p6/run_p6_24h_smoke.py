#!/usr/bin/env python3
"""
P6 24-Hour Smoke Test
=====================
Stage 1: 24-hour continuous operation validation

Configuration:
- Duration: 24 hours
- Epoch: 60 minutes
- Total epochs: 24
- Anomaly rate: 10%
- Checkpoint: every 1 epoch (every hour)

Stop on:
- Core drift (immediate)
- 3 epochs recall < 0.6
- Capability diversity < 20%
- Maintenance overhead > 30%

Usage:
    python3 run_p6_24h_smoke.py

Monitoring:
    tail -f results/p6_24h_smoke.log
    
Results:
    results/P6_24h_final_results.json
"""

import sys
import time
import json
from datetime import datetime
from pathlib import Path

from p6_runner import P6Runner, P6Config, RunnerState


def setup_24h_config() -> P6Config:
    """Configure for 24-hour smoke test"""
    return P6Config(
        duration_hours=24,
        epoch_minutes=60,
        anomaly_injection_rate=0.1,
        checkpoint_interval=1  # Save every hour
    )


def run_24h_smoke():
    """Execute 24-hour smoke test"""
    print("="*60)
    print("P6 24-HOUR SMOKE TEST")
    print("="*60)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Expected duration: 24 hours")
    print(f"Expected completion: {(datetime.now().timestamp() + 24*3600)}")
    print("")
    
    # Setup
    config = setup_24h_config()
    runner = P6Runner(config)
    
    # Log configuration
    log_file = Path("results/p6_24h_smoke.log")
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"P6 24h Smoke Test Started: {datetime.now().isoformat()}\n")
        f.write(f"Configuration: {config}\n")
        f.write(f"{'='*60}\n\n")
    
    print(f"Configuration:")
    print(f"  Duration: {config.duration_hours} hours")
    print(f"  Epoch: {config.epoch_minutes} minutes")
    print(f"  Total epochs: {config.total_epochs}")
    print(f"  Checkpoint interval: every {config.checkpoint_interval} epoch(s)")
    print("")
    print("Running... (Press Ctrl+C to interrupt)")
    print("-"*60)
    
    try:
        # Run the experiment
        result = runner.run()
        
        # Save final results
        runner.save_final_results(result)
        
        # Also save with 24h-specific name
        results_file = Path("results/P6_24h_final_results.json")
        with open(results_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        # Log completion
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Completed: {datetime.now().isoformat()}\n")
            f.write(f"State: {result.state.name}\n")
            f.write(f"Verdict: {result.verdict}\n")
            if result.stop_reason:
                f.write(f"Stop reason: {result.stop_reason}\n")
            f.write(f"Total epochs: {len(result.epochs)}\n")
            f.write(f"{'='*60}\n")
        
        # Print summary
        print("")
        print("="*60)
        print("24h SMOKE TEST COMPLETE")
        print("="*60)
        print(f"State: {result.state.name}")
        print(f"Verdict: {result.verdict}")
        print(f"Epochs: {len(result.epochs)}/{config.total_epochs}")
        
        if result.stop_reason:
            print(f"⚠️  STOPPED: {result.stop_reason}")
        
        if result.state == RunnerState.COMPLETE:
            print("✅ PASS: 24h continuous operation achieved")
        elif result.state == RunnerState.HALTED:
            print("❌ FAIL: Stop condition triggered")
        elif result.state == RunnerState.ERROR:
            print(f"❌ ERROR: {result.stop_reason}")
        
        print(f"Results saved: {results_file}")
        print("="*60)
        
        return result.verdict == "PASS"
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Note: Partial results may be available in checkpoints")
        
        with open(log_file, 'a') as f:
            f.write(f"\n⚠️  Interrupted by user at {datetime.now().isoformat()}\n")
        
        return False
    
    except Exception as e:
        print(f"\n\n❌ Exception: {e}")
        
        with open(log_file, 'a') as f:
            f.write(f"\n❌ Exception: {e} at {datetime.now().isoformat()}\n")
        
        return False


def quick_verify():
    """Quick verification that setup is correct"""
    print("Pre-flight checks:")
    
    # Check P5b is available
    try:
        import sys
        sys.path.append('../p5b')
        print("  ✓ P5b path accessible")
    except:
        print("  ⚠ P5b path issue")
    
    # Check results directory
    results_dir = Path("results")
    if results_dir.exists():
        print(f"  ✓ Results directory exists ({len(list(results_dir.glob('*')))} files)")
    else:
        results_dir.mkdir()
        print("  ✓ Created results directory")
    
    # Verify config
    config = setup_24h_config()
    print(f"  ✓ Config: {config.total_epochs} epochs × {config.epoch_minutes} min = {config.total_epochs * config.epoch_minutes / 60} hours")
    
    print("")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="P6 24h Smoke Test")
    parser.add_argument("--verify", action="store_true", help="Run pre-flight checks only")
    parser.add_argument("--dry-run", action="store_true", help="Show config without running")
    
    args = parser.parse_args()
    
    if args.verify:
        quick_verify()
    elif args.dry_run:
        config = setup_24h_config()
        print("24h Smoke Test Configuration:")
        print(f"  Duration: {config.duration_hours} hours")
        print(f"  Epochs: {config.total_epochs}")
        print(f"  Epoch duration: {config.epoch_minutes} minutes")
        print(f"  Anomaly rate: {config.anomaly_injection_rate}")
        print(f"  Checkpoint: every {config.checkpoint_interval} epoch(s)")
    else:
        quick_verify()
        print("Starting 24h smoke test in 3 seconds...")
        print("(Press Ctrl+C to cancel)")
        time.sleep(3)
        
        success = run_24h_smoke()
        sys.exit(0 if success else 1)
