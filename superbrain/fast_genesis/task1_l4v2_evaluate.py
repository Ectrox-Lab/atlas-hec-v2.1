#!/usr/bin/env python3
"""
Task-1 L4-v2 Mainline Evaluator

Dedicated evaluation script for L4-v2 compositional reuse validation.
Direct binding to Task-1 simulator, no dependency on Octopus/Bio-World frameworks.

Metrics:
- Effectiveness: approve_rate, throughput_delta, failure_archetypes
- Compositionality: reuse_rate, f_p3t4m4_share, leakage, stable_path_winners
"""

import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add simulator path
sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
from baseline_fast import measure_baseline
from adaptive_fast import run_adaptive_scheduling


@dataclass
class EvalConfig:
    """Evaluation configuration"""
    baseline_throughput: float = 0.075  # From measure_baseline (~7.5%)
    approve_threshold: float = 0.04    # Throughput >= 4% (slightly below baseline)
    target_throughput_delta: float = 0.05  # +5% improvement target
    stable_families: List[str] = None
    leakage_families: List[str] = None
    
    def __post_init__(self):
        if self.stable_families is None:
            self.stable_families = ['F_P3T4M4', 'F_P2T4M3', 'F_P3T4M3', 'F_P2T3M2']
        if self.leakage_families is None:
            # P1, P4, T2, T5, M1, M5 families
            self.leakage_families = []


@dataclass
class CandidateResult:
    """Evaluation result for single candidate"""
    candidate_id: str
    family_id: str
    core_signature: Dict
    approved: bool
    throughput: float
    throughput_delta: float
    latency: float
    missed_rate: float
    is_stable_family: bool
    is_leakage_family: bool
    is_f_p3t4m4: bool
    anti_leakage_penalty: float
    mechanism_score: float


@dataclass  
class RoundSummary:
    """Summary for one round (A/B/Ablation)"""
    round_name: str
    total_evaluated: int
    approved_count: int
    approve_rate: float
    avg_throughput_delta: float
    reuse_rate: float  # approved from stable families
    f_p3t4m4_share: float  # F_P3T4M4 in approved
    leakage: float  # approved from leakage families
    stable_path_winners: float  # winners from stable families
    failure_archetypes: List[str]


class Task1L4V2Evaluator:
    """L4-v2 Mainline Evaluator"""
    
    def __init__(self, config: EvalConfig = None):
        self.config = config or EvalConfig()
        self.results: List[CandidateResult] = []
        
    def load_candidates(self, candidates_dir: Path) -> List[Dict]:
        """Load candidate JSONs from directory"""
        candidates = []
        for cand_file in sorted(candidates_dir.glob("C*.json")):
            with open(cand_file) as f:
                candidates.append(json.load(f))
        return candidates
    
    def stratified_sample(self, candidates: List[Dict], n: int = 30, seed: int = 42) -> List[Dict]:
        """Stratified sampling by family"""
        random.seed(seed)
        
        # Group by family
        by_family = {}
        for c in candidates:
            fam = c.get('family_id', 'unknown')
            by_family.setdefault(fam, []).append(c)
        
        # Sample proportionally
        sampled = []
        total = len(candidates)
        
        for fam, fam_cands in by_family.items():
            # Target: proportional representation, min 1 per family
            target = max(1, round(n * len(fam_cands) / total))
            sampled.extend(random.sample(fam_cands, min(target, len(fam_cands))))
        
        # Fill to exactly n if needed
        if len(sampled) < n:
            remaining = [c for c in candidates if c not in sampled]
            if remaining:
                sampled.extend(random.sample(remaining, min(n - len(sampled), len(remaining))))
        
        return sampled[:n]
    
    def evaluate_candidate(self, candidate: Dict, seed: int = 42) -> CandidateResult:
        """Evaluate single candidate with Task-1 simulator"""
        # Extract params
        trust_decay = candidate.get('trust_decay', 0.0)
        trust_recovery = candidate.get('trust_recovery', 0.0)
        family_id = candidate.get('family_id', 'unknown')
        
        # Parse core signature
        core_sig = {
            'P': candidate.get('pressure', 2),
            'T': candidate.get('perturbation', 3),
            'M': candidate.get('memory', 3)
        }
        
        # Check family types
        is_stable = family_id in self.config.stable_families
        is_f_p3t4m4 = family_id == 'F_P3T4M4'
        is_leakage = self._is_leakage_family(family_id, core_sig)
        
        # Run simulation
        try:
            metrics = run_adaptive_scheduling(
                num_tasks=500,  # More tasks for stability
                num_nodes=4,
                arrival_rate=8.0,
                seed=seed,
                trust_decay=trust_decay,
                trust_recovery=trust_recovery
            )
            
            throughput = metrics.get('throughput', 0.0)
            latency = metrics.get('avg_latency', 0.0)
            missed_rate = metrics.get('missed_deadline_rate', 0.0)
            
        except Exception as e:
            print(f"[WARN] Simulation failed for {candidate.get('id')}: {e}")
            throughput = 0.0
            latency = 999.0
            missed_rate = 1.0
        
        # Calculate delta
        throughput_delta = throughput - self.config.baseline_throughput
        
        # Approval check (relaxed to see distribution differences)
        approved = throughput >= self.config.approve_threshold and missed_rate < 0.95
        
        return CandidateResult(
            candidate_id=candidate.get('id', 'unknown'),
            family_id=family_id,
            core_signature=core_sig,
            approved=approved,
            throughput=round(throughput, 4),
            throughput_delta=round(throughput_delta, 4),
            latency=round(latency, 2),
            missed_rate=round(missed_rate, 4),
            is_stable_family=is_stable,
            is_leakage_family=is_leakage,
            is_f_p3t4m4=is_f_p3t4m4,
            anti_leakage_penalty=candidate.get('anti_leakage_penalty', 0.0),
            mechanism_score=candidate.get('mechanism_score', 0.0)
        )
    
    def _is_leakage_family(self, family_id: str, core_sig: Dict) -> bool:
        """Check if family represents structural leakage"""
        p = core_sig.get('P', 2)
        t = core_sig.get('T', 3)
        m = core_sig.get('M', 3)
        
        # Leakage: P1, P4, T2, T5, M1, M5
        return p in [1, 4] or t in [2, 5] or m in [1, 5]
    
    def evaluate_round(self, candidates: List[Dict], round_name: str, sample_size: int = 30) -> RoundSummary:
        """Evaluate a full round"""
        print(f"\n[EVAL] {round_name}: Loading {len(candidates)} candidates")
        
        # Stratified sampling
        sampled = self.stratified_sample(candidates, n=sample_size)
        print(f"[EVAL] {round_name}: Sampled {len(sampled)} candidates (stratified)")
        
        # Evaluate each
        results = []
        for i, cand in enumerate(sampled):
            result = self.evaluate_candidate(cand, seed=1000 + i)
            results.append(result)
            if (i + 1) % 10 == 0:
                print(f"[EVAL] {round_name}: {i+1}/{len(sampled)} evaluated")
        
        # Calculate summary
        total = len(results)
        approved = [r for r in results if r.approved]
        approved_count = len(approved)
        
        # Metrics
        approve_rate = approved_count / total if total > 0 else 0.0
        avg_throughput_delta = sum(r.throughput_delta for r in results) / total if total > 0 else 0.0
        
        # Compositionality
        reuse_rate = sum(1 for r in approved if r.is_stable_family) / approved_count if approved_count > 0 else 0.0
        f_p3t4m4_share = sum(1 for r in approved if r.is_f_p3t4m4) / approved_count if approved_count > 0 else 0.0
        leakage = sum(1 for r in approved if r.is_leakage_family) / approved_count if approved_count > 0 else 0.0
        stable_path_winners = reuse_rate  # Same metric
        
        # Failure archetypes
        failures = [r for r in results if not r.approved]
        failure_archetypes = self._classify_failures(failures)
        
        self.results.extend(results)
        
        return RoundSummary(
            round_name=round_name,
            total_evaluated=total,
            approved_count=approved_count,
            approve_rate=round(approve_rate * 100, 2),
            avg_throughput_delta=round(avg_throughput_delta * 100, 2),
            reuse_rate=round(reuse_rate * 100, 2),
            f_p3t4m4_share=round(f_p3t4m4_share * 100, 2),
            leakage=round(leakage * 100, 2),
            stable_path_winners=round(stable_path_winners * 100, 2),
            failure_archetypes=failure_archetypes
        )
    
    def _classify_failures(self, failures: List[CandidateResult]) -> List[str]:
        """Classify failure archetypes"""
        archetypes = []
        
        for f in failures:
            if f.missed_rate > 0.5:
                archetypes.append("high_deadline_miss")
            elif f.throughput < 0.5:
                archetypes.append("low_throughput")
            elif f.latency > 100:
                archetypes.append("high_latency")
            else:
                archetypes.append("marginal_performance")
        
        # Count unique
        from collections import Counter
        counts = Counter(archetypes)
        return [f"{k}:{v}" for k, v in counts.most_common()]
    
    def generate_report(self, summaries: List[RoundSummary], output_dir: Path):
        """Generate evaluation reports"""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        
        # 1. Effectiveness summary (JSON)
        effectiveness = {
            "timestamp": timestamp,
            "evaluation_type": "L4-v2 Mainline Effectiveness",
            "baseline_throughput": self.config.baseline_throughput,
            "results": {
                s.round_name: {
                    "approve_rate": s.approve_rate,
                    "throughput_delta": s.avg_throughput_delta,
                    "approved_count": s.approved_count,
                    "total_evaluated": s.total_evaluated,
                    "failure_archetypes": s.failure_archetypes
                }
                for s in summaries
            },
            "targets": {
                "approve_rate": "> 60%",
                "throughput_delta": "≥ +5.0%"
            }
        }
        
        with open(output_dir / "mainline_effectiveness_summary.json", 'w') as f:
            json.dump(effectiveness, f, indent=2)
        
        # 2. Compositionality summary (JSON)
        compositionality = {
            "timestamp": timestamp,
            "evaluation_type": "L4-v2 Mainline Compositionality",
            "stable_families": self.config.stable_families,
            "results": {
                s.round_name: {
                    "reuse_rate": s.reuse_rate,
                    "f_p3t4m4_share": s.f_p3t4m4_share,
                    "leakage": s.leakage,
                    "stable_path_winners": s.stable_path_winners
                }
                for s in summaries
            },
            "targets": {
                "reuse_rate": "> 70%",
                "f_p3t4m4_share": "> 30%",
                "leakage": "< 8%"
            }
        }
        
        with open(output_dir / "mainline_compositionality_summary.json", 'w') as f:
            json.dump(compositionality, f, indent=2)
        
        # 3. Detailed results
        detailed = {
            "timestamp": timestamp,
            "candidates": [asdict(r) for r in self.results]
        }
        with open(output_dir / "mainline_detailed_results.json", 'w') as f:
            json.dump(detailed, f, indent=2)
        
        # 4. Markdown report
        self._generate_md_report(summaries, output_dir / "mainline_phase2_report.md", timestamp)
        
        return effectiveness, compositionality
    
    def _generate_md_report(self, summaries: List[RoundSummary], path: Path, timestamp: str):
        """Generate human-readable report"""
        
        # Find Round B summary
        round_b = next((s for s in summaries if s.round_name == "Round B"), None)
        round_a = next((s for s in summaries if s.round_name == "Round A"), None)
        ablation = next((s for s in summaries if s.round_name == "Ablation"), None)
        
        lines = [
            "# L4-v2 Mainline Phase 2 Report",
            "",
            f"**Timestamp**: {timestamp}",
            f"**Evaluator**: Task-1 L4-v2 Dedicated",
            "",
            "---",
            "",
            "## Summary",
            "",
        ]
        
        if round_b:
            lines.extend([
                f"**Approve Rate**: {round_b.approve_rate}% (target: >60%)",
                f"**Reuse Rate**: {round_b.reuse_rate}% (target: >70%)",
                f"**F_P3T4M4 Share**: {round_b.f_p3t4m4_share}% (target: >30%)",
                f"**Leakage**: {round_b.leakage}% (target: <8%)",
                f"**Throughput Delta**: {round_b.avg_throughput_delta}% (target: ≥+5.0%)",
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "## Table A: Effectiveness",
            "",
            "| Round | Approve Rate | Throughput Δ | Approved | Failures |",
            "|-------|-------------|--------------|----------|----------|",
        ])
        
        for s in summaries:
            lines.append(f"| {s.round_name} | {s.approve_rate}% | {s.avg_throughput_delta:+.2f}% | {s.approved_count}/{s.total_evaluated} | {s.failure_archetypes[:2]} |")
        
        lines.extend([
            "",
            "**Targets**:",
            "- Approve rate: > 60%",
            "- Throughput delta: ≥ +5.0% (maintained from Round A)",
            "",
            "---",
            "",
            "## Table B: Compositionality",
            "",
            "| Round | Reuse Rate | F_P3T4M4 Share | Leakage | Stable Path Winners |",
            "|-------|-----------|----------------|---------|-------------------|",
        ])
        
        for s in summaries:
            lines.append(f"| {s.round_name} | {s.reuse_rate}% | {s.f_p3t4m4_share}% | {s.leakage}% | {s.stable_path_winners}% |")
        
        lines.extend([
            "",
            "**Targets**:",
            "- Reuse rate: > 70%",
            "- F_P3T4M4 share: > 30%",
            "- Leakage: < 8%",
            "- Stable path winners: > 60%",
            "",
            "---",
            "",
            "## Verification",
            "",
        ])
        
        if round_a and ablation:
            purity_pass = abs(round_a.approve_rate - ablation.approve_rate) < 1.0
            lines.extend([
                f"**Control Purity**: {'✅ PASS' if purity_pass else '❌ FAIL'}",
                f"- Round A approve rate: {round_a.approve_rate}%",
                f"- Ablation approve rate: {ablation.approve_rate}%",
                "",
            ])
        
        if round_b:
            # Judgment
            hard_passed = sum([
                round_b.approve_rate > 60,
                round_b.reuse_rate > 70,
                round_b.f_p3t4m4_share > 30,
                round_b.leakage < 8
            ])
            
            lines.extend([
                "---",
                "",
                "## Judgment",
                "",
                f"**Hard Criteria Passed**: {hard_passed}/6",
                "",
            ])
            
            if hard_passed >= 6:
                lines.append("**Status**: ✅ L4-v2 FULLY VALIDATED")
            elif hard_passed >= 4:
                lines.append("**Status**: ⚠️ L4-v2 PARTIAL - Parameter tuning needed")
            else:
                lines.append("**Status**: ❌ L4-v2 FAILED - Redesign required")
            
            lines.extend([
                "",
                "### Criteria Check",
                f"- [ {'x' if round_b.approve_rate > 60 else ' '} ] Approve rate > 60% ({round_b.approve_rate}%)",
                f"- [ {'x' if round_b.reuse_rate > 70 else ' '} ] Reuse rate > 70% ({round_b.reuse_rate}%)",
                f"- [ {'x' if round_b.f_p3t4m4_share > 30 else ' '} ] F_P3T4M4 share > 30% ({round_b.f_p3t4m4_share}%)",
                f"- [ {'x' if round_b.leakage < 8 else ' '} ] Leakage < 8% ({round_b.leakage}%)",
            ])
        
        lines.extend([
            "",
            "---",
            "",
            "*Generated by task1_l4v2_evaluate.py*",
        ])
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="L4-v2 Mainline Evaluator")
    parser.add_argument("--input-dir", type=str, default="/tmp/atlas_l4v2",
                        help="Input directory with round_a, round_b, round_ablation")
    parser.add_argument("--output-dir", type=str, default="/tmp/atlas_l4v2_results",
                        help="Output directory for results")
    parser.add_argument("--sample-size", type=int, default=30,
                        help="Number of candidates to evaluate per round")
    parser.add_argument("--baseline", type=float, default=0.075,
                        help="Baseline throughput for comparison")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("TASK-1 L4-v2 MAINLINE EVALUATOR")
    print("=" * 70)
    print(f"Input: {args.input_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Sample size: {args.sample_size}")
    print(f"Baseline throughput: {args.baseline}")
    print("")
    
    # Setup
    config = EvalConfig(baseline_throughput=args.baseline)
    evaluator = Task1L4V2Evaluator(config)
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    # Evaluate each round
    summaries = []
    
    for round_name, subdir in [
        ("Round A", "round_a"),
        ("Round B", "round_b"),
        ("Ablation", "round_ablation")
    ]:
        candidates_dir = input_dir / subdir / "candidates"
        if not candidates_dir.exists():
            print(f"[WARN] {candidates_dir} not found, skipping")
            continue
            
        candidates = evaluator.load_candidates(candidates_dir)
        summary = evaluator.evaluate_round(candidates, round_name, args.sample_size)
        summaries.append(summary)
        
        print(f"\n[RESULT] {round_name}:")
        print(f"  Approve rate: {summary.approve_rate}%")
        print(f"  Reuse rate: {summary.reuse_rate}%")
        print(f"  Leakage: {summary.leakage}%")
    
    # Generate reports
    print("\n" + "=" * 70)
    print("GENERATING REPORTS")
    print("=" * 70)
    
    effectiveness, compositionality = evaluator.generate_report(summaries, output_dir)
    
    print(f"\n✓ Effectiveness: {output_dir / 'mainline_effectiveness_summary.json'}")
    print(f"✓ Compositionality: {output_dir / 'mainline_compositionality_summary.json'}")
    print(f"✓ Detailed results: {output_dir / 'mainline_detailed_results.json'}")
    print(f"✓ Report: {output_dir / 'mainline_phase2_report.md'}")
    
    # Final judgment
    print("\n" + "=" * 70)
    print("L4-v2 JUDGMENT")
    print("=" * 70)
    
    round_b = next((s for s in summaries if s.round_name == "Round B"), None)
    if round_b:
        hard_passed = sum([
            round_b.approve_rate > 60,
            round_b.reuse_rate > 70,
            round_b.f_p3t4m4_share > 30,
            round_b.leakage < 8
        ])
        
        print(f"Hard criteria passed: {hard_passed}/4")
        print(f"Approve rate: {round_b.approve_rate}% {'✅' if round_b.approve_rate > 60 else '❌'}")
        print(f"Reuse rate: {round_b.reuse_rate}% {'✅' if round_b.reuse_rate > 70 else '❌'}")
        print(f"F_P3T4M4 share: {round_b.f_p3t4m4_share}% {'✅' if round_b.f_p3t4m4_share > 30 else '❌'}")
        print(f"Leakage: {round_b.leakage}% {'✅' if round_b.leakage < 8 else '❌'}")
        
        if hard_passed >= 4:
            print("\n✅ L4-v2 FULLY VALIDATED")
        elif hard_passed >= 2:
            print("\n⚠️ L4-v2 PARTIAL - Parameter tuning needed")
        else:
            print("\n❌ L4-v2 FAILED - Redesign required")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
