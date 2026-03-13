#!/usr/bin/env python3
"""
Round 18: RealUNet Single-Layer Gradient Pilot

Tests gradient-based learning on ONE layer (input_proj) of RealUNet.
Other layers remain frozen.

Usage:
    python3 experiments/realunet_gradient_pilot.py
    
Output:
    tests/realunet_gradient_pilot_report.json
"""

import subprocess
import json
import sys
import os

def run_rust_experiment():
    """Run the Rust-based gradient pilot experiment."""
    
    # Build and run
    cmd = [
        "cargo", "run", "--release",
        "--bin", "round18_gradient_pilot"
    ]
    
    print("Building and running Round 18 gradient pilot...")
    result = subprocess.run(
        cmd,
        cwd="/home/admin/atlas-hec-v2.1-repo/code-diffusion",
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    
    return result.returncode == 0

def load_report():
    """Load the generated report."""
    report_path = "/home/admin/atlas-hec-v2.1-repo/code-diffusion/tests/realunet_gradient_pilot_report.json"
    
    if not os.path.exists(report_path):
        print(f"ERROR: Report not found at {report_path}")
        return None
    
    with open(report_path) as f:
        return json.load(f)

def verify_report(report):
    """Verify the report meets all criteria."""
    
    print("\n" + "="*60)
    print("ROUND 18 VERIFICATION")
    print("="*60)
    
    checks = [
        ("Loss decreases", report.get("loss_decreasing", False)),
        ("Gradient non-zero", report.get("gradient_nonzero", False)),
        ("Frozen layers unchanged", report.get("frozen_unchanged", False)),
        ("Reload deterministic", report.get("reload_deterministic", False)),
        ("Structure preserved", report.get("structure_ok", False)),
    ]
    
    all_pass = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        all_pass = all_pass and passed
    
    print("-"*60)
    
    if all_pass:
        print("🎉 ROUND 18: PILOT SUCCESS")
        print("   Gradient mechanism works in RealUNet slice.")
    else:
        print("❌ ROUND 18: PILOT FAIL")
        print("   Needs investigation before scaling.")
    
    print("="*60)
    
    return all_pass

def main():
    # Run experiment
    if not run_rust_experiment():
        print("\n❌ Experiment failed to run")
        sys.exit(1)
    
    # Load and verify report
    report = load_report()
    if report is None:
        sys.exit(1)
    
    success = verify_report(report)
    
    # Print summary stats
    print("\nPilot Statistics:")
    print(f"  Initial loss: {report.get('loss_initial', 'N/A')}")
    print(f"  Final loss: {report.get('loss_final', 'N/A')}")
    print(f"  Loss reduction: {report.get('loss_reduction_pct', 'N/A')}%")
    print(f"  Gradient norm (dW): {report.get('grad_norm_dW', 'N/A')}")
    print(f"  Gradient norm (db): {report.get('grad_norm_db', 'N/A')}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
