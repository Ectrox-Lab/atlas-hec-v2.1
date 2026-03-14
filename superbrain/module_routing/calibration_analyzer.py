#!/usr/bin/env python3
"""
Calibration Analyzer for E-COMP-003

Analyzes Phase 1 variable isolation results and determines:
- H1: Anti-leakage too strong?
- H2: Mechanism package wrong?
- H3: Task-1 too noisy?
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ConditionResult:
    name: str
    mechanism_bias: bool
    anti_leakage: float
    approve_rate: float
    reuse_rate: float
    leakage: float
    throughput_delta: float


def load_condition_results(results_dir: Path, condition: str) -> ConditionResult:
    """Load results for a single condition"""
    eff_file = results_dir / f"condition_{condition}" / "mainline_effectiveness_summary.json"
    comp_file = results_dir / f"condition_{condition}" / "mainline_compositionality_summary.json"
    
    if not eff_file.exists():
        print(f"[WARN] {eff_file} not found")
        return None
    
    with open(eff_file) as f:
        eff = json.load(f)
    with open(comp_file) as f:
        comp = json.load(f)
    
    # Map condition letter to round name
    round_name = f"Round {condition.upper()}"
    
    eff_data = eff.get("results", {}).get(round_name, {})
    comp_data = comp.get("results", {}).get(round_name, {})
    
    # Determine config from condition name
    config_map = {
        "A": (False, 0.0),
        "B": (True, 0.0),
        "C": (False, 0.4),
        "D": (True, 0.4)
    }
    mech, anti = config_map.get(condition, (False, 0.0))
    
    return ConditionResult(
        name=condition,
        mechanism_bias=mech,
        anti_leakage=anti,
        approve_rate=eff_data.get("approve_rate", 0.0),
        reuse_rate=comp_data.get("reuse_rate", 0.0),
        leakage=comp_data.get("leakage", 0.0),
        throughput_delta=eff_data.get("throughput_delta", 0.0)
    )


def analyze_phase1(results: List[ConditionResult]) -> Dict:
    """Analyze Phase 1 variable isolation results"""
    
    # Find conditions
    A = next((r for r in results if r.name == "A"), None)
    B = next((r for r in results if r.name == "B"), None)
    C = next((r for r in results if r.name == "C"), None)
    D = next((r for r in results if r.name == "D"), None)
    
    if not all([A, B, C, D]):
        print("[ERROR] Missing conditions")
        return {}
    
    analysis = {
        "conditions": {
            "A_baseline": {"approve": A.approve_rate, "reuse": A.reuse_rate, "leakage": A.leakage},
            "B_mech_only": {"approve": B.approve_rate, "reuse": B.reuse_rate, "leakage": B.leakage},
            "C_anti_only": {"approve": C.approve_rate, "reuse": C.reuse_rate, "leakage": C.leakage},
            "D_full": {"approve": D.approve_rate, "reuse": D.reuse_rate, "leakage": D.leakage}
        },
        "comparisons": {}
    }
    
    # Test H1: Anti-leakage too strong?
    # Evidence: C < A AND D < B
    c_vs_a = C.approve_rate - A.approve_rate
    d_vs_b = D.approve_rate - B.approve_rate
    
    analysis["comparisons"]["anti_leakage_effect"] = {
        "C_vs_A": round(c_vs_a, 2),
        "D_vs_B": round(d_vs_b, 2),
        "interpretation": "Anti-leakage reduces approval" if c_vs_a < -1 and d_vs_b < -1 else "Anti-leakage neutral or positive"
    }
    
    h1_supported = c_vs_a < -1 and d_vs_b < -1
    
    # Test H2: Mechanism package wrong?
    # Evidence: B < A
    b_vs_a = B.approve_rate - A.approve_rate
    
    analysis["comparisons"]["mechanism_effect"] = {
        "B_vs_A": round(b_vs_a, 2),
        "interpretation": "Mechanism bias reduces approval" if b_vs_a < -1 else "Mechanism bias neutral or positive"
    }
    
    h2_supported = b_vs_a < -1 and (not h1_supported or C.approve_rate >= A.approve_rate)
    
    # Test H3: Task-1 too noisy?
    # Evidence: A ≈ B ≈ C ≈ D (all within 2%)
    rates = [A.approve_rate, B.approve_rate, C.approve_rate, D.approve_rate]
    rate_range = max(rates) - min(rates)
    
    analysis["comparisons"]["variance"] = {
        "min_rate": round(min(rates), 2),
        "max_rate": round(max(rates), 2),
        "range": round(rate_range, 2),
        "interpretation": "High variance / Task-1 noisy" if rate_range < 3 else "Clear differences between conditions"
    }
    
    h3_supported = rate_range < 3
    
    # Determine conclusion
    if h1_supported and not h3_supported:
        analysis["conclusion"] = {
            "hypothesis": "H1",
            "description": "Anti-leakage too strong",
            "confidence": "medium" if d_vs_b < -2 else "low",
            "recommendation": "Proceed to Phase 2 (strength scan)"
        }
    elif h2_supported and not h3_supported:
        analysis["conclusion"] = {
            "hypothesis": "H2",
            "description": "Mechanism package semantic wrong",
            "confidence": "medium" if b_vs_a < -2 else "low",
            "recommendation": "Redesign mechanism package (Option C)"
        }
    elif h3_supported:
        analysis["conclusion"] = {
            "hypothesis": "H3",
            "description": "Task-1 validator too noisy",
            "confidence": "medium" if rate_range < 2 else "low",
            "recommendation": "Switch to Task-2 (Option B)"
        }
    else:
        # Complex pattern
        analysis["conclusion"] = {
            "hypothesis": "Complex",
            "description": "Mixed effects - need deeper analysis",
            "pattern": f"A={A.approve_rate}, B={B.approve_rate}, C={C.approve_rate}, D={D.approve_rate}",
            "recommendation": "Manual review + additional conditions"
        }
    
    return analysis


def generate_report(analysis: Dict, output_path: Path):
    """Generate Phase 1 analysis report"""
    output_path.mkdir(parents=True, exist_ok=True)
    
    # JSON output
    with open(output_path / "phase1_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Markdown report
    lines = [
        "# E-COMP-003 Phase 1 Analysis Report",
        "",
        "## Variable Isolation Results",
        "",
        "| Condition | Mechanism | Anti-Leakage | Approve Rate | Reuse Rate | Leakage |",
        "|-----------|-----------|--------------|--------------|------------|---------|",
    ]
    
    for name, data in analysis.get("conditions", {}).items():
        cond_letter = name.split("_")[0]
        config_desc = {
            "A": "OFF | OFF",
            "B": "ON | OFF",
            "C": "OFF | 0.4",
            "D": "ON | 0.4"
        }.get(cond_letter, "? | ?")
        lines.append(f"| {name} | {config_desc} | {data['approve_rate']}% | {data['reuse_rate']}% | {data['leakage']}% |")
    
    lines.extend([
        "",
        "## Hypothesis Tests",
        "",
        "### H1: Anti-Leakage Too Strong?",
        f"- C vs A: {analysis['comparisons']['anti_leakage_effect']['C_vs_A']:.2f}%",
        f"- D vs B: {analysis['comparisons']['anti_leakage_effect']['D_vs_B']:.2f}%",
        f"- **Interpretation**: {analysis['comparisons']['anti_leakage_effect']['interpretation']}",
        "",
        "### H2: Mechanism Package Wrong?",
        f"- B vs A: {analysis['comparisons']['mechanism_effect']['B_vs_A']:.2f}%",
        f"- **Interpretation**: {analysis['comparisons']['mechanism_effect']['interpretation']}",
        "",
        "### H3: Task-1 Too Noisy?",
        f"- Rate range: {analysis['comparisons']['variance']['range']:.2f}%",
        f"- Min: {analysis['comparisons']['variance']['min_rate']:.2f}%, Max: {analysis['comparisons']['variance']['max_rate']:.2f}%",
        f"- **Interpretation**: {analysis['comparisons']['variance']['interpretation']}",
        "",
        "## Conclusion",
        "",
        f"**Primary Hypothesis**: {analysis['conclusion']['hypothesis']} — {analysis['conclusion']['description']}",
        "",
        f"**Confidence**: {analysis['conclusion']['confidence']}",
        "",
        f"**Recommendation**: {analysis['conclusion']['recommendation']}",
        "",
        "## Next Steps",
        "",
    ])
    
    if analysis['conclusion']['hypothesis'] == 'H1':
        lines.extend([
            "1. Run Phase 2: Anti-leakage strength scan (0.0, 0.2, 0.3, 0.4)",
            "2. Find sweet spot with low leakage + reasonable approve rate",
            "3. Update v2 package with optimal strength",
        ])
    elif analysis['conclusion']['hypothesis'] == 'H2':
        lines.extend([
            "1. Analyze all winners (n=9 total) for common patterns",
            "2. Rebuild mechanism package from actual data",
            "3. Test v3 package in quick iteration",
        ])
    elif analysis['conclusion']['hypothesis'] == 'H3':
        lines.extend([
            "1. Archive Task-1 learnings",
            "2. Design Task-2 validator",
            "3. Port mechanism bias to new task",
        ])
    else:
        lines.extend([
            "1. Manual review of results",
            "2. Consider additional test conditions",
            "3. May need larger sample size",
        ])
    
    lines.extend([
        "",
        "---",
        "",
        "*Generated by calibration_analyzer.py*",
    ])
    
    with open(output_path / "phase1_analysis.md", 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"[REPORT] Phase 1 analysis: {output_path}/phase1_analysis.md")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=str, default="/tmp/ecomp003_calibration/p1_results",
                        help="Phase 1 results directory")
    parser.add_argument("--output-dir", type=str, default="/home/admin/atlas-hec-v2.1-repo/docs/research/E-COMP-003/calibration",
                        help="Output directory for analysis")
    args = parser.parse_args()
    
    results_dir = Path(args.results)
    output_dir = Path(args.output_dir)
    
    print("=" * 70)
    print("E-COMP-003 Phase 1 Analysis")
    print("=" * 70)
    print("")
    
    # Load all conditions
    results = []
    for cond in ["A", "B", "C", "D"]:
        result = load_condition_results(results_dir, cond)
        if result:
            results.append(result)
            print(f"[LOAD] Condition {cond}: Approve={result.approve_rate}%, Reuse={result.reuse_rate}%")
    
    if len(results) < 4:
        print("[ERROR] Insufficient data for analysis")
        return
    
    print("")
    
    # Analyze
    analysis = analyze_phase1(results)
    
    # Generate report
    generate_report(analysis, output_dir)
    
    # Print summary
    print("=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Primary Hypothesis: {analysis['conclusion']['hypothesis']}")
    print(f"Description: {analysis['conclusion']['description']}")
    print(f"Recommendation: {analysis['conclusion']['recommendation']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
