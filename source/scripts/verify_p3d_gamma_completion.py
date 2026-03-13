#!/usr/bin/env python3
"""
P3D-gamma Completion Verification Script

验收标准（必须同时满足）:
1. verdict == "SUPPORTED_SHIFT"
2. sample_level == "adequate"
3. effect_detected == True
4. intervention_active == True
5. n_paired_seeds >= 10
6. total_episodes >= 500

用法:
    python3 scripts/verify_p3d_gamma_completion.py logs/p3d/summary_report.json
"""

import json
import sys

def verify(summary_path):
    """验证 P3D-gamma 是否达到 COMPLETE 标准"""
    
    try:
        with open(summary_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {summary_path}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1
    
    # 定义检查项
    checks = {
        "verdict_is_supported": (
            data.get("verdict", "").startswith("SUPPORTED_SHIFT"),
            f"verdict = {data.get('verdict', 'N/A')}"
        ),
        "sample_adequate": (
            data.get("sample_level") == "adequate",
            f"sample_level = {data.get('sample_level', 'N/A')}"
        ),
        "effect_detected": (
            data.get("effect_detected") == True,
            f"effect_detected = {data.get('effect_detected', 'N/A')}"
        ),
        "intervention_active": (
            data.get("intervention_active") == True,
            f"intervention_active = {data.get('intervention_active', 'N/A')}"
        ),
        "seeds_sufficient": (
            data.get("n_paired_seeds", 0) >= 10,
            f"n_paired_seeds = {data.get('n_paired_seeds', 0)}"
        ),
        "episodes_sufficient": (
            data.get("total_episodes", 0) >= 500,
            f"total_episodes = {data.get('total_episodes', 0)}"
        ),
    }
    
    print("=" * 70)
    print("     P3D-gamma Completion Verification")
    print("=" * 70)
    print()
    
    all_pass = True
    for name, (passed, detail) in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        print(f"         ({detail})")
        if not passed:
            all_pass = False
    
    print()
    print("=" * 70)
    
    if all_pass:
        print("🎯 RESULT: P3D-gamma COMPLETE")
        print()
        print("  All criteria met:")
        print(f"    - Verdict: {data.get('verdict')}")
        print(f"    - Effect size: d = {data.get('cohens_d', 'N/A'):.2f}")
        print(f"    - Sample: {data.get('n_paired_seeds')} seeds, {data.get('total_episodes')} episodes")
        print(f"    - Intervention: {data.get('intervention_rate', 0)*100:.1f}%")
        print()
        print("  Measured behavioral shift validated.")
        print("  P3D-gamma can be declared COMPLETE.")
        print("=" * 70)
        return 0
    else:
        print("⏳ RESULT: P3D-gamma NOT YET COMPLETE")
        print()
        print("  Some criteria not met.")
        print("  Actions:")
        print("    1. Run more experiments (target: 10+ seeds, 500+ episodes)")
        print("    2. Check homeostasis thresholds if effect too small")
        print("    3. Verify intervention rate > 10%")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_p3d_gamma_completion.py <summary_report.json>")
        sys.exit(1)
    
    sys.exit(verify(sys.argv[1]))
