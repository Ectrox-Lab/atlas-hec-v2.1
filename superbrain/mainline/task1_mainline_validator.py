#!/usr/bin/env python3
"""
Task-1 Mainline Validator

High-cost reality judge for heterogeneous executor coordination.

Input: Bridge queue candidates (Tier B)
Output: APPROVE / HOLD / REJECT with full metrics

Evaluation regime:
- 10k tasks
- Multiple seeds
- Fault injection
- Strict resource constraints
"""

import json
import sys
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Add task1_simulator to path
sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
from adaptive_fast import run_adaptive_scheduling


@dataclass
class MainlineMetrics:
    """Mainline evaluation metrics for a single candidate"""
    candidate_id: str
    
    # Throughput metrics
    throughput_mean: float
    throughput_std: float
    throughput_min: float
    throughput_max: float
    throughput_delta: float  # vs baseline
    
    # Latency metrics
    latency_mean: float
    latency_std: float
    latency_delta: float  # vs baseline
    
    # Recovery metrics
    recovery_time_mean: float
    recovery_time_delta: float
    
    # Switching metrics
    switching_rate_mean: float
    switching_delta: float
    
    # Stability
    stability_cv: float
    variance_cv: float
    
    # Quality
    missed_deadline_rate: float
    missed_delta: float
    
    # Seeds tested
    seeds_tested: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


class Task1MainlineValidator:
    """
    Mainline reality judge for Task-1.
    
    Responsibilities:
    1. Run high-cost evaluation (10k tasks, multiple seeds)
    2. Compare against baseline
    3. Determine APPROVE / HOLD / REJECT
    4. Emit structured results for Akashic
    """
    
    # Baseline reference values (measured from task1_simulator)
    BASELINE = {
        'throughput': 0.0214,      # 2.14%
        'latency': 253.9,          # ms
        'recovery_time': 289.5,    # ms
        'switching_rate': 0.0036,  # fraction
        'missed_rate': 0.9088,     # 90.88%
        'stability_cv': 0.668
    }
    
    # Decision thresholds (weighted as per v0.2 spec)
    THRESHOLDS = {
        'throughput': {
            'weight': 0.30,
            'approve': 0.023,      # > 2.3% (target: > 87% relative)
            'hold': 0.0214         # > baseline
        },
        'latency': {
            'weight': 0.20,
            'approve': 240.0,      # < 240ms
            'hold': 253.9          # < baseline
        },
        'recovery_time': {
            'weight': 0.25,
            'approve': 260.0,      # < 260ms
            'hold': 289.5          # < baseline
        },
        'switching_rate': {
            'weight': 0.15,
            'approve': 0.003,      # < 0.3%
            'hold': 0.0036         # < baseline
        },
        'stability': {
            'weight': 0.10,
            'approve_cv': 0.65,    # cv < 0.65
            'hold_cv': 0.70        # cv < 0.70
        }
    }
    
    def __init__(self, output_dir: str = "../../benchmark_results/task1_mainline"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_log: List[Dict] = []
        self.approved_candidates: List[str] = []
        self.held_candidates: List[str] = []
        self.rejected_candidates: List[str] = []
    
    def load_candidate_from_bridge(self, queue_file: Path) -> Optional[Dict]:
        """Load candidate from Bridge queue"""
        try:
            with open(queue_file) as f:
                data = json.load(f)
            return data.get("candidate", data)  # Handle both formats
        except Exception as e:
            print(f"[MAINLINE] Error loading {queue_file}: {e}")
            return None
    
    def evaluate_candidate(
        self,
        candidate: Dict,
        num_tasks: int = 10000,
        num_seeds: int = 10
    ) -> Tuple[MainlineMetrics, str, str]:
        """
        Run full Mainline evaluation on candidate.
        
        Returns:
            (metrics, decision, rationale)
        """
        candidate_id = candidate.get("id", candidate.get("candidate_id", "unknown"))
        print(f"\n[MAINLINE] Evaluating candidate: {candidate_id}")
        print(f"  Tasks: {num_tasks}, Seeds: {num_seeds}")
        
        # Extract candidate parameters
        trust_decay = candidate.get("trust_decay", 0.0)
        trust_recovery = candidate.get("trust_recovery", 0.0)
        
        # Run multi-seed evaluation
        all_results = []
        for seed_idx in range(num_seeds):
            seed = hash(candidate_id) % 10000 + seed_idx * 1000
            print(f"  Running seed {seed_idx+1}/{num_seeds}...", end=" ", flush=True)
            
            try:
                result = run_adaptive_scheduling(
                    num_tasks=num_tasks,
                    num_nodes=6,
                    arrival_rate=8.0,
                    seed=seed,
                    trust_decay=trust_decay,
                    trust_recovery=trust_recovery
                )
                all_results.append(result)
                print(f"throughput={result['throughput']:.2%}")
            except Exception as e:
                print(f"ERROR: {e}")
                continue
        
        if not all_results:
            raise RuntimeError("All seeds failed")
        
        # Aggregate metrics
        throughputs = [r['throughput'] for r in all_results]
        latencies = [r['avg_latency'] for r in all_results]
        recovery_times = [r['recovery_time'] for r in all_results]
        switching_rates = [r['unnecessary_switches'] for r in all_results]
        missed_rates = [r['missed_deadline_rate'] for r in all_results]
        
        # Calculate statistics
        tp_mean = statistics.mean(throughputs)
        tp_std = statistics.stdev(throughputs) if len(throughputs) > 1 else 0
        tp_min = min(throughputs)
        tp_max = max(throughputs)
        tp_delta = tp_mean - self.BASELINE['throughput']
        
        lat_mean = statistics.mean(latencies)
        lat_std = statistics.stdev(latencies) if len(latencies) > 1 else 0
        lat_delta = lat_mean - self.BASELINE['latency']
        
        rec_mean = statistics.mean(recovery_times)
        rec_delta = rec_mean - self.BASELINE['recovery_time']
        
        sw_mean = statistics.mean(switching_rates)
        sw_delta = sw_mean - self.BASELINE['switching_rate']
        
        missed_mean = statistics.mean(missed_rates)
        missed_delta = missed_mean - self.BASELINE['missed_rate']
        
        # Stability (coefficient of variation)
        cv_tp = tp_std / tp_mean if tp_mean > 0 else float('inf')
        cv_lat = lat_std / lat_mean if lat_mean > 0 else float('inf')
        stability_cv = (cv_tp + cv_lat) / 2
        
        metrics = MainlineMetrics(
            candidate_id=candidate_id,
            throughput_mean=tp_mean,
            throughput_std=tp_std,
            throughput_min=tp_min,
            throughput_max=tp_max,
            throughput_delta=tp_delta,
            latency_mean=lat_mean,
            latency_std=lat_std,
            latency_delta=lat_delta,
            recovery_time_mean=rec_mean,
            recovery_time_delta=rec_delta,
            switching_rate_mean=sw_mean,
            switching_delta=sw_delta,
            stability_cv=stability_cv,
            variance_cv=cv_tp,
            missed_deadline_rate=missed_mean,
            missed_delta=missed_delta,
            seeds_tested=len(all_results)
        )
        
        # Decision
        decision, rationale = self._make_decision(metrics)
        
        return metrics, decision, rationale
    
    def _make_decision(self, metrics: MainlineMetrics) -> Tuple[str, str]:
        """
        Make APPROVE / HOLD / REJECT decision based on metrics.
        
        Rules (from v0.2 spec):
        - APPROVE: All critical metrics improve over baseline, weighted result meaningful
        - HOLD: Improvement but variance high or unstable
        - REJECT: Below baseline or reproduces known failures
        """
        checks = []
        
        # Throughput check
        if metrics.throughput_mean >= self.THRESHOLDS['throughput']['approve']:
            checks.append(('throughput', 'PASS', metrics.throughput_delta))
        elif metrics.throughput_mean >= self.THRESHOLDS['throughput']['hold']:
            checks.append(('throughput', 'MARGINAL', metrics.throughput_delta))
        else:
            checks.append(('throughput', 'FAIL', metrics.throughput_delta))
        
        # Latency check (lower is better)
        if metrics.latency_mean <= self.THRESHOLDS['latency']['approve']:
            checks.append(('latency', 'PASS', -metrics.latency_delta))  # Negative delta is good
        elif metrics.latency_mean <= self.THRESHOLDS['latency']['hold']:
            checks.append(('latency', 'MARGINAL', -metrics.latency_delta))
        else:
            checks.append(('latency', 'FAIL', -metrics.latency_delta))
        
        # Recovery time check
        if metrics.recovery_time_mean <= self.THRESHOLDS['recovery_time']['approve']:
            checks.append(('recovery', 'PASS', -metrics.recovery_time_delta))
        elif metrics.recovery_time_mean <= self.THRESHOLDS['recovery_time']['hold']:
            checks.append(('recovery', 'MARGINAL', -metrics.recovery_time_delta))
        else:
            checks.append(('recovery', 'FAIL', -metrics.recovery_time_delta))
        
        # Switching rate check
        if metrics.switching_rate_mean <= self.THRESHOLDS['switching_rate']['approve']:
            checks.append(('switching', 'PASS', -metrics.switching_delta))
        elif metrics.switching_rate_mean <= self.THRESHOLDS['switching_rate']['hold']:
            checks.append(('switching', 'MARGINAL', -metrics.switching_delta))
        else:
            checks.append(('switching', 'FAIL', -metrics.switching_delta))
        
        # Stability check
        if metrics.stability_cv <= self.THRESHOLDS['stability']['approve_cv']:
            checks.append(('stability', 'PASS', metrics.stability_cv))
        elif metrics.stability_cv <= self.THRESHOLDS['stability']['hold_cv']:
            checks.append(('stability', 'MARGINAL', metrics.stability_cv))
        else:
            checks.append(('stability', 'FAIL', metrics.stability_cv))
        
        # Decision logic
        pass_count = sum(1 for _, status, _ in checks if status == 'PASS')
        fail_count = sum(1 for _, status, _ in checks if status == 'FAIL')
        marginal_count = sum(1 for _, status, _ in checks if status == 'MARGINAL')
        
        # Weighted score
        weighted_score = 0.0
        for metric_name, status, value in checks:
            weight = self.THRESHOLDS.get(metric_name, {}).get('weight', 0.1)
            if status == 'PASS':
                weighted_score += weight
            elif status == 'MARGINAL':
                weighted_score += weight * 0.5
        
        # Decision
        if fail_count == 0 and pass_count >= 4 and weighted_score >= 0.75:
            decision = "APPROVE"
            rationale = f"Strong improvement across metrics (score={weighted_score:.2f}, pass={pass_count}/5)"
        elif fail_count == 0 and (pass_count + marginal_count) >= 4:
            decision = "HOLD"
            rationale = f"Promising but needs more validation (score={weighted_score:.2f}, marginal={marginal_count})"
        else:
            decision = "REJECT"
            rationale = f"Below baseline or unstable (fails={fail_count}, score={weighted_score:.2f})"
        
        return decision, rationale
    
    def process_queue(self, queue_dir: str = "../bridge/to_mainline"):
        """Process all candidates in Bridge queue"""
        queue_path = Path(queue_dir)
        if not queue_path.exists():
            print(f"[MAINLINE] Queue directory not found: {queue_dir}")
            return
        
        queue_files = list(queue_path.glob("*.json"))
        print(f"[MAINLINE] Processing {len(queue_files)} candidates from queue")
        
        for queue_file in queue_files:
            candidate = self.load_candidate_from_bridge(queue_file)
            if not candidate:
                continue
            
            try:
                metrics, decision, rationale = self.evaluate_candidate(candidate)
                
                # Record result
                result = {
                    "candidate_id": metrics.candidate_id,
                    "evaluated_at": datetime.now().isoformat(),
                    "decision": decision,
                    "rationale": rationale,
                    "metrics": metrics.to_dict(),
                    "baseline_reference": self.BASELINE,
                    "source_file": str(queue_file.name)
                }
                
                self.results_log.append(result)
                
                # Track by decision
                if decision == "APPROVE":
                    self.approved_candidates.append(metrics.candidate_id)
                elif decision == "HOLD":
                    self.held_candidates.append(metrics.candidate_id)
                else:
                    self.rejected_candidates.append(metrics.candidate_id)
                
                print(f"[MAINLINE] Decision: {decision} - {rationale}")
                
                # Move processed file
                processed_dir = queue_path / "processed_by_mainline"
                processed_dir.mkdir(exist_ok=True)
                queue_file.rename(processed_dir / queue_file.name)
                
            except Exception as e:
                print(f"[MAINLINE] Error evaluating candidate: {e}")
                import traceback
                traceback.print_exc()
    
    def save_results(self):
        """Save all results to JSON and Markdown report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON results
        results_data = {
            "validator": "task1_mainline_validator",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
            "baseline": self.BASELINE,
            "thresholds": self.THRESHOLDS,
            "summary": {
                "total_evaluated": len(self.results_log),
                "approved": len(self.approved_candidates),
                "held": len(self.held_candidates),
                "rejected": len(self.rejected_candidates)
            },
            "approved_candidates": self.approved_candidates,
            "held_candidates": self.held_candidates,
            "rejected_candidates": self.rejected_candidates,
            "detailed_results": self.results_log
        }
        
        json_path = self.output_dir / f"task1_mainline_results_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        # Markdown report
        report = self._generate_report()
        md_path = self.output_dir / f"task1_mainline_report_{timestamp}.md"
        with open(md_path, 'w') as f:
            f.write(report)
        
        print(f"\n[MAINLINE] Results saved:")
        print(f"  JSON: {json_path}")
        print(f"  Report: {md_path}")
        
        return json_path, md_path
    
    def _generate_report(self) -> str:
        """Generate Markdown report"""
        lines = [
            "# Task-1 Mainline Validation Report",
            "",
            f"**Validator**: task1_mainline_validator v0.1.0",
            f"**Timestamp**: {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total Evaluated**: {len(self.results_log)}",
            f"- **APPROVED**: {len(self.approved_candidates)}",
            f"- **HELD**: {len(self.held_candidates)}",
            f"- **REJECTED**: {len(self.rejected_candidates)}",
            "",
            "## Baseline Reference",
            "",
            "| Metric | Baseline Value |",
            "|--------|----------------|",
            f"| Throughput | {self.BASELINE['throughput']:.2%} |",
            f"| Latency | {self.BASELINE['latency']:.1f} ms |",
            f"| Recovery Time | {self.BASELINE['recovery_time']:.1f} ms |",
            f"| Switching Rate | {self.BASELINE['switching_rate']:.3f} |",
            f"| Missed Deadline | {self.BASELINE['missed_rate']:.2%} |",
            "",
            "## Decision Thresholds",
            "",
            "| Metric | Weight | APPROVE Threshold | HOLD Threshold |",
            "|--------|--------|-------------------|----------------|",
            f"| Throughput | {self.THRESHOLDS['throughput']['weight']:.2f} | > {self.THRESHOLDS['throughput']['approve']:.2%} | > {self.THRESHOLDS['throughput']['hold']:.2%} |",
            f"| Latency | {self.THRESHOLDS['latency']['weight']:.2f} | < {self.THRESHOLDS['latency']['approve']:.1f} ms | < {self.THRESHOLDS['latency']['hold']:.1f} ms |",
            f"| Recovery | {self.THRESHOLDS['recovery_time']['weight']:.2f} | < {self.THRESHOLDS['recovery_time']['approve']:.1f} ms | < {self.THRESHOLDS['recovery_time']['hold']:.1f} ms |",
            "",
            "## Approved Candidates",
            ""
        ]
        
        if self.approved_candidates:
            for cid in self.approved_candidates:
                lines.append(f"- {cid}")
        else:
            lines.append("None")
        
        lines.extend(["", "## Detailed Results", ""])
        
        for result in self.results_log:
            m = result['metrics']
            lines.extend([
                f"### {result['candidate_id']}",
                "",
                f"**Decision**: {result['decision']}",
                f"**Rationale**: {result['rationale']}",
                "",
                "| Metric | Mean | Delta vs Baseline |",
                "|--------|------|-------------------|",
                f"| Throughput | {m['throughput_mean']:.2%} | {m['throughput_delta']:+.2%} |",
                f"| Latency | {m['latency_mean']:.1f} ms | {m['latency_delta']:+.1f} ms |",
                f"| Recovery | {m['recovery_time_mean']:.1f} ms | {m['recovery_time_delta']:+.1f} ms |",
                f"| Switching | {m['switching_rate_mean']:.3f} | {m['switching_delta']:+.3f} |",
                f"| Stability CV | {m['stability_cv']:.3f} | - |",
                ""
            ])
        
        return "\n".join(lines)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task-1 Mainline Validator')
    parser.add_argument('--queue', default='../bridge/to_mainline',
                       help='Bridge queue directory')
    parser.add_argument('--output', default='../../benchmark_results/task1_mainline',
                       help='Output directory')
    parser.add_argument('--tasks', type=int, default=10000,
                       help='Tasks per seed')
    parser.add_argument('--seeds', type=int, default=10,
                       help='Number of seeds')
    
    args = parser.parse_args()
    
    print("="*70)
    print("TASK-1 MAINLINE VALIDATOR")
    print("="*70)
    
    validator = Task1MainlineValidator(output_dir=args.output)
    validator.process_queue(queue_dir=args.queue)
    
    if validator.results_log:
        validator.save_results()
        
        print("\n" + "="*70)
        print("VALIDATION COMPLETE")
        print("="*70)
        print(f"Total: {len(validator.results_log)}")
        print(f"Approved: {len(validator.approved_candidates)}")
        print(f"Held: {len(validator.held_candidates)}")
        print(f"Rejected: {len(validator.rejected_candidates)}")
    else:
        print("\n[MAINLINE] No candidates to evaluate")


if __name__ == "__main__":
    main()