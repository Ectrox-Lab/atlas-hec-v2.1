"""
P6 Long-Horizon Robustness - Core Runner
=========================================
72-hour experiment orchestrator with automatic stop conditions.

Phase 1: Basic epoch loop with 1h/24h/72h modes
Phase 1+MemoryGate: Integrated Memory Admission Gate for P6 Stage 2
"""

import time
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum, auto
from pathlib import Path
from datetime import datetime

# Import Memory Admission Gate (relative import for p6_stage2)
import sys
from pathlib import Path

# Add repo root to path for imports
_REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from experiments.superbrain.p6_stage2.memory_admission_gate import (
        MemoryAdmissionGate,
        MemoryEvent,
        MemoryContext,
        AdmissionVerdict,
        P6MemoryGateAdapter,
    )
    MEMORY_GATE_AVAILABLE = True
except ImportError as e:
    MEMORY_GATE_AVAILABLE = False
    # Define placeholder for type hints
    MemoryAdmissionGate = Any
    print(f"Warning: Memory gate not available: {e}")


class RunnerState(Enum):
    INIT = auto()
    RUNNING = auto()
    COMPLETE = auto()
    HALTED = auto()
    ERROR = auto()


@dataclass
class P6Config:
    """P6 experiment configuration"""
    duration_hours: int = 72
    epoch_minutes: int = 60
    anomaly_injection_rate: float = 0.1
    checkpoint_interval: int = 1  # Save every N epochs
    enable_memory_gate: bool = False  # NEW: Enable memory admission gate
    
    @property
    def total_epochs(self) -> int:
        return (self.duration_hours * 60) // self.epoch_minutes
    
    @property
    def is_test_mode(self) -> bool:
        """True for short test runs (< 24h)"""
        return self.duration_hours < 24


@dataclass
class EpochMetrics:
    """Metrics collected per epoch"""
    epoch_num: int
    timestamp: float
    core_hash: str
    core_drift: bool
    detector_recall: float
    capability_diversity: float
    maintenance_overhead: float
    repair_success_rate: float
    # NEW: Memory gate metrics (P6 Stage 2)
    memory_events_total: int = 0
    memory_events_admitted: int = 0
    memory_events_caution: int = 0
    memory_events_rejected: int = 0
    memory_gate_overhead_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch_num,
            "timestamp": self.timestamp,
            "core_hash": self.core_hash,
            "core_drift": self.core_drift,
            "detector_recall": self.detector_recall,
            "capability_diversity": self.capability_diversity,
            "maintenance_overhead": self.maintenance_overhead,
            "repair_success_rate": self.repair_success_rate,
            # NEW: Memory metrics
            "memory_events_total": self.memory_events_total,
            "memory_events_admitted": self.memory_events_admitted,
            "memory_events_caution": self.memory_events_caution,
            "memory_events_rejected": self.memory_events_rejected,
            "memory_gate_overhead_ms": self.memory_gate_overhead_ms,
        }


@dataclass
class EpochResult:
    """Result of a single epoch"""
    epoch_num: int
    timestamp: float
    metrics: EpochMetrics
    core_hash: str
    detection_occurred: bool
    repair_success: Optional[bool] = None


@dataclass
class P6Result:
    """Final experiment result"""
    state: RunnerState
    config: P6Config
    epochs: List[EpochResult]
    baseline_hash: str
    verdict: str
    stop_reason: Optional[str] = None
    # NEW: Memory gate summary
    memory_gate_stats: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "state": self.state.name,
            "duration_hours": self.config.duration_hours,
            "total_epochs": len(self.epochs),
            "baseline_hash": self.baseline_hash,
            "verdict": self.verdict,
            "stop_reason": self.stop_reason,
            "epochs": [e.metrics.to_dict() for e in self.epochs]
        }
        if self.memory_gate_stats:
            result["memory_gate_stats"] = self.memory_gate_stats
        return result


class P6Runner:
    """
    P6 Long-Horizon Robustness Experiment Runner
    
    Responsibilities:
    - Epoch lifecycle management
    - State machine (INIT → RUN → [COMPLETE|HALT])
    - Checkpoint persistence
    - Metrics collection
    - Memory admission gate integration (P6 Stage 2)
    """
    
    def __init__(self, config: P6Config, memory_gate: Optional[MemoryAdmissionGate] = None):
        self.config = config
        self.state = RunnerState.INIT
        self.current_epoch = 0
        self.epochs: List[EpochResult] = []
        self.baseline_hash: Optional[str] = None
        self.start_time: Optional[float] = None
        
        # Metrics tracking
        self._detection_history: List[bool] = []
        self._repair_history: List[bool] = []
        
        # NEW: Memory gate integration
        self.memory_gate = memory_gate if MEMORY_GATE_AVAILABLE else None
        self._memory_event_log: List[Dict[str, Any]] = []
        self._memory_context = MemoryContext() if MEMORY_GATE_AVAILABLE else None
        
        # Output directory
        self.output_dir = Path("results")
        self.output_dir.mkdir(exist_ok=True)
    
    def run(self) -> P6Result:
        """
        Main entry point. Runs until:
        - All epochs complete (PASS)
        - Stop condition triggered (FAIL)
        - Error (ERROR)
        """
        self.state = RunnerState.RUNNING
        self.start_time = time.time()
        
        try:
            for epoch_num in range(self.config.total_epochs):
                self.current_epoch = epoch_num
                
                # Run single epoch
                epoch_result = self._run_epoch(epoch_num)
                self.epochs.append(epoch_result)
                
                # Check stop conditions (simplified for Phase 1)
                stop_reason = self._check_stop_conditions()
                if stop_reason:
                    self.state = RunnerState.HALTED
                    return self._create_result(verdict="FAIL", stop_reason=stop_reason)
                
                # Checkpoint
                if epoch_num % self.config.checkpoint_interval == 0:
                    self._save_checkpoint()
                
                # Progress log
                if epoch_num % 10 == 0 or self.config.is_test_mode:
                    mem_info = ""
                    if self.config.enable_memory_gate:
                        m = epoch_result.metrics
                        mem_info = f", mem=[{m.memory_events_admitted}/{m.memory_events_total}]"
                    print(f"Epoch {epoch_num}/{self.config.total_epochs} complete, core_hash={epoch_result.core_hash[:8]}{mem_info}")
            
            self.state = RunnerState.COMPLETE
            return self._create_result(verdict="PASS")
            
        except Exception as e:
            self.state = RunnerState.ERROR
            return self._create_result(verdict="ERROR", stop_reason=str(e))
    
    def _run_epoch(self, epoch_num: int) -> EpochResult:
        """Execute one epoch with memory gate integration"""
        epoch_start = time.time()
        
        # Initialize baseline on first epoch
        if self.baseline_hash is None:
            self.baseline_hash = self._compute_baseline_hash()
        
        # Memory gate metrics accumulator
        mem_stats = {
            "total": 0,
            "admitted": 0,
            "caution": 0,
            "rejected": 0,
            "overhead_ms": 0.0,
        }
        
        # ==========================================
        # Injection Point 1: Normal Operation
        # ==========================================
        normal_state = self._simulate_normal_operation()
        
        if self.config.enable_memory_gate and self.memory_gate:
            gate_start = time.perf_counter()
            normal_event = self._create_memory_event(
                epoch_num=epoch_num,
                timestamp=epoch_start,
                event_type='normal_operation',
                state=normal_state,
                core_hash=self.baseline_hash,
            )
            score = self.memory_gate.evaluate(normal_event, self._memory_context)
            self._log_memory_event(normal_event, score, epoch_num)
            mem_stats["total"] += 1
            if score.verdict == AdmissionVerdict.ADMIT:
                mem_stats["admitted"] += 1
            elif score.verdict == AdmissionVerdict.CAUTION:
                mem_stats["caution"] += 1
            else:
                mem_stats["rejected"] += 1
            mem_stats["overhead_ms"] += (time.perf_counter() - gate_start) * 1000
        
        # ==========================================
        # Anomaly injection and handling
        # ==========================================
        detection_occurred = False
        repair_success = None
        
        if self._should_inject_anomaly():
            # ==========================================
            # Injection Point 2: Anomaly Injection
            # ==========================================
            anomaly_state = self._inject_anomaly(normal_state)
            detection_occurred = True
            
            if self.config.enable_memory_gate and self.memory_gate:
                gate_start = time.perf_counter()
                anomaly_event = self._create_memory_event(
                    epoch_num=epoch_num,
                    timestamp=time.time(),
                    event_type='anomaly_injected',
                    state=anomaly_state,
                    core_hash=self.baseline_hash,
                    metadata={
                        'anomaly_type': 'memory_noise',  # Simplified for v0.1
                        'detection_occurred': True,
                    }
                )
                score = self.memory_gate.evaluate(anomaly_event, self._memory_context)
                self._log_memory_event(anomaly_event, score, epoch_num)
                mem_stats["total"] += 1
                if score.verdict == AdmissionVerdict.ADMIT:
                    mem_stats["admitted"] += 1
                elif score.verdict == AdmissionVerdict.CAUTION:
                    mem_stats["caution"] += 1
                else:
                    mem_stats["rejected"] += 1
                mem_stats["overhead_ms"] += (time.perf_counter() - gate_start) * 1000
            
            # Simulate: Detect and repair
            repair_success = self._simulate_repair()
            self._repair_history.append(repair_success)
            
            # ==========================================
            # Injection Point 3: Repair Event
            # ==========================================
            if self.config.enable_memory_gate and self.memory_gate:
                gate_start = time.perf_counter()
                repair_event = self._create_memory_event(
                    epoch_num=epoch_num,
                    timestamp=time.time(),
                    event_type='repair_succeeded' if repair_success else 'repair_failed',
                    state=anomaly_state,
                    core_hash=self.baseline_hash,
                    metadata={
                        'repair_success': repair_success,
                        'repair_strategy': 'reset',  # Simplified for v0.1
                    }
                )
                score = self.memory_gate.evaluate(repair_event, self._memory_context)
                self._log_memory_event(repair_event, score, epoch_num)
                mem_stats["total"] += 1
                if score.verdict == AdmissionVerdict.ADMIT:
                    mem_stats["admitted"] += 1
                elif score.verdict == AdmissionVerdict.CAUTION:
                    mem_stats["caution"] += 1
                else:
                    mem_stats["rejected"] += 1
                mem_stats["overhead_ms"] += (time.perf_counter() - gate_start) * 1000
        
        # Collect metrics
        core_hash = self._compute_core_hash(normal_state)
        metrics = EpochMetrics(
            epoch_num=epoch_num,
            timestamp=epoch_start,
            core_hash=core_hash,
            core_drift=(core_hash != self.baseline_hash),
            detector_recall=self._compute_rolling_recall(window=10),
            capability_diversity=self._simulate_capability_diversity(),
            maintenance_overhead=self._simulate_maintenance_overhead(),
            repair_success_rate=self._compute_repair_success_rate(window=10),
            # NEW: Memory metrics
            memory_events_total=mem_stats["total"],
            memory_events_admitted=mem_stats["admitted"],
            memory_events_caution=mem_stats["caution"],
            memory_events_rejected=mem_stats["rejected"],
            memory_gate_overhead_ms=round(mem_stats["overhead_ms"], 4),
        )
        
        return EpochResult(
            epoch_num=epoch_num,
            timestamp=epoch_start,
            metrics=metrics,
            core_hash=core_hash,
            detection_occurred=detection_occurred,
            repair_success=repair_success
        )
    
    # ==========================================
    # NEW: Helper methods for memory gate
    # ==========================================
    
    def _create_memory_event(
        self,
        epoch_num: int,
        timestamp: float,
        event_type: str,
        state: Any,
        core_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional['MemoryEvent']:
        """
        Create MemoryEvent from runner internal state
        
        v0.1: Simplified mapping, generates structured content
        """
        if not MEMORY_GATE_AVAILABLE:
            return None
        
        # Generate content description
        content = self._generate_event_description(epoch_num, event_type, state, metadata)
        
        # Map event type to MemoryEvent format
        event_type_map = {
            'normal_operation': 'observation',
            'anomaly_injected': 'anomaly',
            'repair_succeeded': 'action_result',
            'repair_failed': 'action_result',
        }
        
        # Map source
        source_map = {
            'normal_operation': 'system_observation',
            'anomaly_injected': 'simulated_anomaly_generator',
            'repair_succeeded': 'repair_system',
            'repair_failed': 'repair_system',
        }
        
        # Generate identity claim
        identity_claim = None
        if core_hash == self.baseline_hash:
            identity_claim = f"I am Atlas-HEC at epoch {epoch_num}"
        
        # Estimate goal relevance from capability diversity
        goal_relevance = self._compute_goal_relevance_estimate(event_type)
        
        return MemoryEvent(
            content=content,
            event_type=event_type_map.get(event_type, 'unknown'),
            timestamp=datetime.fromtimestamp(timestamp).isoformat(),
            source=source_map.get(event_type, 'unknown'),
            tags=[f'epoch_{epoch_num}', event_type],
            identity_claim=identity_claim,
            goal_relevance=goal_relevance,
        )
    
    def _generate_event_description(
        self,
        epoch_num: int,
        event_type: str,
        state: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate human-readable event description"""
        base = f"Epoch {epoch_num}: {event_type}"
        
        if event_type == 'normal_operation':
            return f"{base} - System operating normally, state={state}"
        elif event_type == 'anomaly_injected':
            anomaly_type = metadata.get('anomaly_type', 'unknown') if metadata else 'unknown'
            return f"{base} - Anomaly type: {anomaly_type}"
        elif event_type in ('repair_succeeded', 'repair_failed'):
            success = 'succeeded' if 'succeeded' in event_type else 'failed'
            strategy = metadata.get('repair_strategy', 'unknown') if metadata else 'unknown'
            return f"{base} - Repair {success}, strategy: {strategy}"
        else:
            return f"{base} - State: {state}"
    
    def _compute_goal_relevance_estimate(self, event_type: str) -> float:
        """Estimate goal relevance based on event type (v0.1 heuristic)"""
        relevance_map = {
            'normal_operation': 0.5,
            'anomaly_injected': 0.8,  # High relevance - affects stability
            'repair_succeeded': 0.9,  # High relevance - maintaining self
            'repair_failed': 0.95,    # Very high - critical failure
        }
        return relevance_map.get(event_type, 0.5)
    
    def _log_memory_event(
        self,
        event: 'MemoryEvent',
        score: Any,  # AdmissionScore
        epoch_num: int
    ):
        """Log memory event with admission decision"""
        log_entry = {
            'epoch': epoch_num,
            'timestamp': datetime.now().isoformat(),
            'event_fingerprint': event.to_fingerprint(),
            'event_type': event.event_type,
            'verdict': score.verdict.value,
            'total_score': round(score.total_score, 4),
            'dimensions': {
                'identity_relevance': round(score.identity_relevance, 4),
                'temporal_consistency': round(score.temporal_consistency, 4),
                'cross_memory_consistency': round(score.cross_memory_consistency, 4),
                'source_reliability': round(score.source_reliability, 4),
            },
            'reasons': score.reasons,
            'confidence': round(score.confidence, 4),
        }
        self._memory_event_log.append(log_entry)
    
    def _get_memory_gate_stats(self) -> Optional[Dict[str, Any]]:
        """Get summary statistics for memory gate"""
        if not self.config.enable_memory_gate or not self._memory_event_log:
            return None
        
        total = len(self._memory_event_log)
        admitted = sum(1 for e in self._memory_event_log if e['verdict'] == 'admit')
        caution = sum(1 for e in self._memory_event_log if e['verdict'] == 'caution')
        rejected = sum(1 for e in self._memory_event_log if e['verdict'] == 'reject')
        
        avg_score = sum(e['total_score'] for e in self._memory_event_log) / total if total > 0 else 0
        
        return {
            'total_events': total,
            'admitted': admitted,
            'caution': caution,
            'rejected': rejected,
            'admission_rate': round(admitted / total, 4) if total > 0 else 0,
            'caution_rate': round(caution / total, 4) if total > 0 else 0,
            'rejection_rate': round(rejected / total, 4) if total > 0 else 0,
            'avg_score': round(avg_score, 4),
        }
    
    def _save_memory_event_log(self):
        """Save memory event log to disk"""
        if not self.config.enable_memory_gate:
            return
        
        log_file = self.output_dir / "memory_event_log.jsonl"
        with open(log_file, 'w') as f:
            for entry in self._memory_event_log:
                f.write(json.dumps(entry) + '\n')
        print(f"Memory event log saved to {log_file}")
    
    # ==========================================
    # Existing methods (unchanged behavior)
    # ==========================================
    
    def _check_stop_conditions(self) -> Optional[str]:
        """Check if any stop condition is triggered"""
        if not self.epochs:
            return None
        
        latest = self.epochs[-1]
        
        # Stop 1: Core drift
        if latest.metrics.core_drift:
            return f"core_drift_detected: {latest.core_hash} != {self.baseline_hash}"
        
        # Stop 2: Detector degradation (3 epochs below 0.6)
        recent_epochs = self.epochs[-3:]
        if len(recent_epochs) >= 3:
            if all(e.metrics.detector_recall < 0.6 for e in recent_epochs):
                return f"detector_degradation: 3 epochs recall < 0.6"
        
        # Stop 3: Capability exhaustion
        if latest.metrics.capability_diversity < 0.2:
            return f"capability_exhaustion: diversity {latest.metrics.capability_diversity:.2%} < 20%"
        
        # Stop 4: Maintenance overload
        if latest.metrics.maintenance_overhead > 0.3:
            return f"maintenance_overload: overhead {latest.metrics.maintenance_overhead:.2%} > 30%"
        
        return None
    
    def _compute_baseline_hash(self) -> str:
        """Compute baseline core hash"""
        return hashlib.sha256(b"baseline_core_identity_v1").hexdigest()[:16]
    
    def _compute_core_hash(self, state: Any) -> str:
        """Compute core hash from state"""
        return self.baseline_hash or self._compute_baseline_hash()
    
    def _should_inject_anomaly(self) -> bool:
        """Determine if anomaly should be injected this epoch"""
        import random
        return random.random() < self.config.anomaly_injection_rate
    
    def _inject_anomaly(self, state: Any) -> Any:
        """Inject anomaly into state"""
        return state
    
    def _simulate_normal_operation(self) -> Dict[str, Any]:
        """Simulate normal operation"""
        return {"status": "normal"}
    
    def _simulate_repair(self) -> bool:
        """Simulate repair, return success"""
        import random
        return random.random() > 0.1
    
    def _simulate_capability_diversity(self) -> float:
        """Simulate capability diversity (0.0 to 1.0)"""
        import random
        base = 0.8 - (self.current_epoch * 0.002)
        noise = random.gauss(0, 0.05)
        return max(0.3, min(1.0, base + noise))
    
    def _simulate_maintenance_overhead(self) -> float:
        """Simulate maintenance overhead (0.0 to 1.0)"""
        import random
        base = 0.05
        if self._detection_history and self._detection_history[-1]:
            base += 0.03
        noise = random.gauss(0, 0.01)
        return max(0.0, min(0.15, base + noise))
    
    def _compute_rolling_recall(self, window: int) -> float:
        """Compute rolling detector recall"""
        if not self._detection_history:
            return 1.0
        recent = self._detection_history[-window:]
        if not recent:
            return 1.0
        return sum(recent) / len(recent)
    
    def _compute_repair_success_rate(self, window: int) -> float:
        """Compute rolling repair success rate"""
        if not self._repair_history:
            return 1.0
        recent = self._repair_history[-window:]
        if not recent:
            return 1.0
        return sum(recent) / len(recent)
    
    def _save_checkpoint(self):
        """Save checkpoint to disk"""
        checkpoint_file = self.output_dir / f"checkpoint_epoch_{self.current_epoch}.json"
        checkpoint_data = {
            "epoch": self.current_epoch,
            "state": self.state.name,
            "latest_metrics": self.epochs[-1].metrics.to_dict() if self.epochs else None,
        }
        
        # NEW: Include memory gate summary if enabled
        if self.config.enable_memory_gate:
            checkpoint_data["memory_gate_summary"] = self._get_memory_gate_stats()
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def _create_result(self, verdict: str, stop_reason: Optional[str] = None) -> P6Result:
        """Create final result"""
        # NEW: Save memory event log on completion
        if self.config.enable_memory_gate:
            self._save_memory_event_log()
        
        return P6Result(
            state=self.state,
            config=self.config,
            epochs=self.epochs,
            baseline_hash=self.baseline_hash or "unknown",
            verdict=verdict,
            stop_reason=stop_reason,
            memory_gate_stats=self._get_memory_gate_stats(),
        )
    
    def save_final_results(self, result: P6Result):
        """Save final results to disk"""
        results_file = self.output_dir / "P6_final_results.json"
        with open(results_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"Results saved to {results_file}")
        
        # NEW: Print memory gate summary if enabled
        if result.memory_gate_stats:
            stats = result.memory_gate_stats
            print(f"\nMemory Gate Summary:")
            print(f"  Total events: {stats['total_events']}")
            print(f"  ADMIT: {stats['admitted']} ({stats['admission_rate']:.1%})")
            print(f"  CAUTION: {stats['caution']} ({stats['caution_rate']:.1%})")
            print(f"  REJECT: {stats['rejected']} ({stats['rejection_rate']:.1%})")
            print(f"  Avg score: {stats['avg_score']:.3f}")


if __name__ == "__main__":
    # Quick test - without memory gate (backward compatible)
    print("=" * 60)
    print("Test 1: Without Memory Gate (backward compatible)")
    print("=" * 60)
    config1 = P6Config(duration_hours=1, epoch_minutes=5, enable_memory_gate=False)
    runner1 = P6Runner(config1)
    result1 = runner1.run()
    runner1.save_final_results(result1)
    print(f"Run complete: {result1.verdict}")
    print(f"Epochs: {len(result1.epochs)}")
    print(f"State: {result1.state.name}")
    
    # Test with memory gate
    if MEMORY_GATE_AVAILABLE:
        print("\n" + "=" * 60)
        print("Test 2: With Memory Gate (P6 Stage 2)")
        print("=" * 60)
        from experiments.superbrain.p6_stage2.memory_admission_gate import MemoryAdmissionGate
        config2 = P6Config(duration_hours=1, epoch_minutes=5, enable_memory_gate=True)
        gate = MemoryAdmissionGate()
        runner2 = P6Runner(config2, memory_gate=gate)
        result2 = runner2.run()
        runner2.save_final_results(result2)
        print(f"Run complete: {result2.verdict}")
        print(f"Epochs: {len(result2.epochs)}")
        print(f"State: {result2.state.name}")
    else:
        print("\nMemory gate not available, skipping test 2")
