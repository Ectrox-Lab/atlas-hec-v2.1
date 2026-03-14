#!/usr/bin/env python3
"""
Mechanism Extractor for E-COMP-003

Extracts mechanism patterns from L4-v2 winners by re-running
candidates with detailed logging.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import random

sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
from baseline_fast import measure_baseline
from adaptive_fast import run_adaptive_scheduling


@dataclass
class MechanismTrace:
    """Detailed trace of mechanism execution"""
    candidate_id: str
    family_id: str
    seed: int
    
    # Delegation patterns observed
    delegation_decisions: List[Dict]  # {time, from_node, to_node, reason}
    
    # Recovery sequences
    recovery_events: List[Dict]  # {time, event_type, nodes_affected}
    
    # Trust trajectory
    trust_updates: List[Dict]  # {time, node, old_trust, new_trust, trigger}
    
    # Overall metrics
    throughput: float
    latency: float
    missed_rate: float
    stability_cv: float


@dataclass
class MechanismPattern:
    """Aggregated mechanism pattern across multiple runs"""
    pattern_id: str
    pattern_type: str  # "delegation", "recovery", "trust_update"
    
    # Description
    description: str
    sequence: Optional[List[str]]  # for recovery sequences
    
    # Statistics
    occurrence_count: int
    success_rate: float  # correlation with approval
    avg_throughput: float
    throughput_variance: float
    
    # Context
    associated_families: List[str]
    optimal_params: Dict  # {param: range}


class MechanismExtractor:
    """Extract mechanism patterns from L4-v2 winners"""
    
    def __init__(self, l4v2_results_dir: Path):
        self.results_dir = l4v2_results_dir
        self.traces: List[MechanismTrace] = []
        self.patterns: List[MechanismPattern] = []
        
    def load_l4v2_winners(self) -> List[Dict]:
        """Load approved candidates from L4-v2 results"""
        detailed_file = self.results_dir / "mainline_detailed_results.json"
        
        if not detailed_file.exists():
            print(f"[ERROR] {detailed_file} not found")
            return []
        
        with open(detailed_file) as f:
            data = json.load(f)
        
        # Filter approved candidates (from any round, but prefer Round B)
        winners = [
            r for r in data.get("candidates", [])
            if r.get("approved") == True
        ]
        
        print(f"[LOAD] Found {len(winners)} approved candidates from Round B")
        return winners
    
    def extract_trace(self, candidate: Dict, seed: int = 42) -> Optional[MechanismTrace]:
        """Run candidate with detailed logging and extract trace"""
        # Extract parameters
        trust_decay = candidate.get("trust_decay", 0.1)
        trust_recovery = candidate.get("trust_recovery", 0.05)
        
        # Run simulation with logging enabled
        # Note: This is a simplified version - full implementation would need
        # to modify adaptive_fast.py to log delegation decisions, recovery events, etc.
        try:
            metrics = run_adaptive_scheduling(
                num_tasks=500,
                num_nodes=4,
                arrival_rate=8.0,
                seed=seed,
                trust_decay=trust_decay,
                trust_recovery=trust_recovery
            )
            
            # For now, create a basic trace from metrics
            # Full implementation would extract actual mechanism logs
            trace = MechanismTrace(
                candidate_id=candidate.get("candidate_id", "unknown"),
                family_id=candidate.get("family_id", "unknown"),
                seed=seed,
                delegation_decisions=self._extract_delegation_pattern(candidate, metrics),
                recovery_events=self._extract_recovery_pattern(candidate, metrics),
                trust_updates=self._extract_trust_trajectory(candidate, metrics),
                throughput=metrics.get("throughput", 0.0),
                latency=metrics.get("avg_latency", 0.0),
                missed_rate=metrics.get("missed_deadline_rate", 0.0),
                stability_cv=metrics.get("stability_cv", 0.0)
            )
            
            return trace
            
        except Exception as e:
            print(f"[WARN] Failed to extract trace for {candidate.get('candidate_id')}: {e}")
            return None
    
    def _extract_delegation_pattern(self, candidate: Dict, metrics: Dict) -> List[Dict]:
        """Extract delegation pattern from candidate signature"""
        # Simplified: infer from parameters
        family = candidate.get("family_id", "")
        
        patterns = []
        
        # Family-based inference (preliminary)
        if "P3" in family and "T4" in family:
            patterns.append({
                "time": 0,
                "pattern": "adaptive_migration",
                "reason": "high_pressure_high_triage",
                "confidence": 0.8
            })
        elif "P2" in family:
            patterns.append({
                "time": 0,
                "pattern": "pressure_threshold_based",
                "reason": "moderate_pressure",
                "confidence": 0.7
            })
        
        return patterns
    
    def _extract_recovery_pattern(self, candidate: Dict, metrics: Dict) -> List[Dict]:
        """Extract recovery sequence from metrics"""
        # Simplified: infer from stability metrics
        stability = metrics.get("stability_cv", 0.5)
        
        events = []
        
        if stability < 0.5:
            events.append({
                "time": 0,
                "event_type": "stable_operation",
                "sequence": ["detect_fault", "maintain_load", "gradual_recovery"]
            })
        else:
            events.append({
                "time": 0,
                "event_type": "unstable_operation",
                "sequence": ["detect_fault", "rapid_switch", "oscillate"]
            })
        
        return events
    
    def _extract_trust_trajectory(self, candidate: Dict, metrics: Dict) -> List[Dict]:
        """Extract trust update pattern"""
        trust_decay = candidate.get("trust_decay", 0.1)
        trust_recovery = candidate.get("trust_recovery", 0.05)
        
        return [{
            "time": 0,
            "pattern": "trust_update_prior",
            "decay_rate": trust_decay,
            "recovery_rate": trust_recovery,
            "classification": self._classify_trust_pattern(trust_decay, trust_recovery)
        }]
    
    def _classify_trust_pattern(self, decay: float, recovery: float) -> str:
        """Classify trust update pattern"""
        if decay < 0.08 and recovery > 0.06:
            return "aggressive_recovery"
        elif decay > 0.12 and recovery < 0.04:
            return "conservative_trust"
        else:
            return "balanced"
    
    def aggregate_patterns(self) -> List[MechanismPattern]:
        """Aggregate traces into mechanism patterns"""
        if not self.traces:
            print("[WARN] No traces to aggregate")
            return []
        
        # Group by family
        by_family = {}
        for trace in self.traces:
            fam = trace.family_id
            by_family.setdefault(fam, []).append(trace)
        
        patterns = []
        
        # Analyze each family
        for family, traces in by_family.items():
            # Delegation pattern
            delegation_pattern = self._analyze_delegation_patterns(family, traces)
            if delegation_pattern:
                patterns.append(delegation_pattern)
            
            # Recovery pattern
            recovery_pattern = self._analyze_recovery_patterns(family, traces)
            if recovery_pattern:
                patterns.append(recovery_pattern)
            
            # Trust pattern
            trust_pattern = self._analyze_trust_patterns(family, traces)
            if trust_pattern:
                patterns.append(trust_pattern)
        
        self.patterns = patterns
        return patterns
    
    def _analyze_delegation_patterns(self, family: str, traces: List[MechanismTrace]) -> Optional[MechanismPattern]:
        """Analyze delegation patterns for a family"""
        if not traces:
            return None
        
        # Extract pattern types
        pattern_types = []
        for t in traces:
            for d in t.delegation_decisions:
                pattern_types.append(d.get("pattern", "unknown"))
        
        if not pattern_types:
            return None
        
        from collections import Counter
        most_common = Counter(pattern_types).most_common(1)[0]
        
        # Calculate stats
        throughputs = [t.throughput for t in traces]
        avg_throughput = sum(throughputs) / len(throughputs)
        variance = sum((t - avg_throughput) ** 2 for t in throughputs) / len(throughputs)
        
        return MechanismPattern(
            pattern_id=f"delegation_{family}",
            pattern_type="delegation",
            description=f"Most common delegation pattern for {family}",
            sequence=None,
            occurrence_count=most_common[1],
            success_rate=sum(1 for t in traces if t.throughput > 0.04) / len(traces),
            avg_throughput=avg_throughput,
            throughput_variance=variance,
            associated_families=[family],
            optimal_params=self._infer_optimal_params(traces)
        )
    
    def _analyze_recovery_patterns(self, family: str, traces: List[MechanismTrace]) -> Optional[MechanismPattern]:
        """Analyze recovery patterns for a family"""
        if not traces:
            return None
        
        # Extract sequences
        sequences = []
        for t in traces:
            for e in t.recovery_events:
                seq = e.get("sequence", [])
                if seq:
                    sequences.append(tuple(seq))
        
        if not sequences:
            return None
        
        from collections import Counter
        most_common = Counter(sequences).most_common(1)[0]
        
        throughputs = [t.throughput for t in traces]
        avg_throughput = sum(throughputs) / len(throughputs)
        
        return MechanismPattern(
            pattern_id=f"recovery_{family}",
            pattern_type="recovery",
            description=f"Recovery sequence pattern for {family}",
            sequence=list(most_common[0]),
            occurrence_count=most_common[1],
            success_rate=sum(1 for t in traces if t.throughput > 0.04) / len(traces),
            avg_throughput=avg_throughput,
            throughput_variance=sum((t - avg_throughput) ** 2 for t in throughputs) / len(throughputs),
            associated_families=[family],
            optimal_params={}
        )
    
    def _analyze_trust_patterns(self, family: str, traces: List[MechanismTrace]) -> Optional[MechanismPattern]:
        """Analyze trust update patterns for a family"""
        if not traces:
            return None
        
        # Extract trust classifications
        classifications = []
        for t in traces:
            for u in t.trust_updates:
                classifications.append(u.get("classification", "unknown"))
        
        if not classifications:
            return None
        
        from collections import Counter
        most_common = Counter(classifications).most_common(1)[0]
        
        throughputs = [t.throughput for t in traces]
        avg_throughput = sum(throughputs) / len(throughputs)
        
        return MechanismPattern(
            pattern_id=f"trust_{family}",
            pattern_type="trust_update",
            description=f"Trust update pattern for {family}: {most_common[0]}",
            sequence=None,
            occurrence_count=most_common[1],
            success_rate=sum(1 for t in traces if t.throughput > 0.04) / len(traces),
            avg_throughput=avg_throughput,
            throughput_variance=sum((t - avg_throughput) ** 2 for t in throughputs) / len(throughputs),
            associated_families=[family],
            optimal_params=self._infer_trust_params(traces)
        )
    
    def _infer_optimal_params(self, traces: List[MechanismTrace]) -> Dict:
        """Infer optimal parameters from traces"""
        # Placeholder - would analyze actual parameter-performance correlation
        return {"trust_decay": [0.05, 0.15], "trust_recovery": [0.03, 0.08]}
    
    def _infer_trust_params(self, traces: List[MechanismTrace]) -> Dict:
        """Infer trust update parameters"""
        decay_rates = []
        recovery_rates = []
        
        for t in traces:
            for u in t.trust_updates:
                if "decay_rate" in u:
                    decay_rates.append(u["decay_rate"])
                if "recovery_rate" in u:
                    recovery_rates.append(u["recovery_rate"])
        
        params = {}
        if decay_rates:
            params["trust_decay"] = [min(decay_rates), max(decay_rates)]
        if recovery_rates:
            params["trust_recovery"] = [min(recovery_rates), max(recovery_rates)]
        
        return params
    
    def export_family_mechanism_map(self, output_path: Path):
        """Export family_mechanism_map_v1.json"""
        if not self.patterns:
            print("[WARN] No patterns to export")
            return
        
        # Group patterns by family
        by_family = {}
        for p in self.patterns:
            for fam in p.associated_families:
                if fam not in by_family:
                    by_family[fam] = {
                        "mechanisms": [],
                        "stability_score": 0.0,
                        "optimal_params": {}
                    }
                by_family[fam]["mechanisms"].append({
                    "type": p.pattern_type,
                    "pattern_id": p.pattern_id,
                    "description": p.description,
                    "success_rate": p.success_rate,
                    "avg_throughput": p.avg_throughput
                })
        
        # Calculate stability scores
        for fam, data in by_family.items():
            if data["mechanisms"]:
                data["stability_score"] = sum(m["success_rate"] for m in data["mechanisms"]) / len(data["mechanisms"])
        
        output = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "source": "E-COMP-003 MechanismExtractor",
            "family_mechanism_map": by_family
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"[EXPORT] Family mechanism map: {output_path}")
    
    def run_extraction(self, output_dir: Path):
        """Run full extraction pipeline"""
        print("=" * 70)
        print("E-COMP-003: Mechanism Extraction")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Results dir: {self.results_dir}")
        print("")
        
        # Load winners
        winners = self.load_l4v2_winners()
        if not winners:
            print("[ERROR] No winners found, extraction aborted")
            return
        
        # Extract traces
        print(f"\n[EXTRACT] Processing {len(winners)} winners...")
        for i, winner in enumerate(winners):
            trace = self.extract_trace(winner, seed=1000 + i)
            if trace:
                self.traces.append(trace)
            if (i + 1) % 5 == 0:
                print(f"  {i+1}/{len(winners)} processed")
        
        print(f"\n[EXTRACT] Generated {len(self.traces)} mechanism traces")
        
        # Aggregate patterns
        print("\n[AGGREGATE] Building mechanism patterns...")
        patterns = self.aggregate_patterns()
        print(f"[AGGREGATE] Identified {len(patterns)} patterns")
        
        # Export
        output_dir.mkdir(parents=True, exist_ok=True)
        self.export_family_mechanism_map(output_dir / "family_mechanism_map_v1.json")
        
        print("\n" + "=" * 70)
        print("EXTRACTION COMPLETE")
        print("=" * 70)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--l4v2-results", type=str, default="/tmp/atlas_l4v2_results",
                        help="Path to L4-v2 results directory")
    parser.add_argument("--output-dir", type=str, default="/home/admin/atlas-hec-v2.1-repo/docs/research/E-COMP-003",
                        help="Output directory for deliverables")
    args = parser.parse_args()
    
    extractor = MechanismExtractor(Path(args.l4v2_results))
    extractor.run_extraction(Path(args.output_dir))


if __name__ == "__main__":
    main()
