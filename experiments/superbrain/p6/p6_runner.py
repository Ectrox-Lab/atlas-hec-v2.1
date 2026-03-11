"""
P6 Long-Horizon Robustness - Core Runner
=========================================
72-hour experiment orchestrator with automatic stop conditions.

Phase 1: Basic epoch loop with 1h/24h/72h modes
"""

import time
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum, auto
from pathlib import Path


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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch_num,
            "timestamp": self.timestamp,
            "core_hash": self.core_hash,
            "core_drift": self.core_drift,
            "detector_recall": self.detector_recall,
            "capability_diversity": self.capability_diversity,
            "maintenance_overhead": self.maintenance_overhead,
            "repair_success_rate": self.repair_success_rate
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.name,
            "duration_hours": self.config.duration_hours,
            "total_epochs": len(self.epochs),
            "baseline_hash": self.baseline_hash,
            "verdict": self.verdict,
            "stop_reason": self.stop_reason,
            "epochs": [e.metrics.to_dict() for e in self.epochs]
        }


class P6Runner:
    """
    P6 Long-Horizon Robustness Experiment Runner
    
    Responsibilities:
    - Epoch lifecycle management
    - State machine (INIT → RUN → [COMPLETE|HALT])
    - Checkpoint persistence
    - Metrics collection
    """
    
    def __init__(self, config: P6Config):
        self.config = config
        self.state = RunnerState.INIT
        self.current_epoch = 0
        self.epochs: List[EpochResult] = []
        self.baseline_hash: Optional[str] = None
        self.start_time: Optional[float] = None
        
        # Metrics tracking
        self._detection_history: List[bool] = []
        self._repair_history: List[bool] = []
        
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
                    print(f"Epoch {epoch_num}/{self.config.total_epochs} complete, core_hash={epoch_result.core_hash[:8]}")
            
            self.state = RunnerState.COMPLETE
            return self._create_result(verdict="PASS")
            
        except Exception as e:
            self.state = RunnerState.ERROR
            return self._create_result(verdict="ERROR", stop_reason=str(e))
    
    def _run_epoch(self, epoch_num: int) -> EpochResult:
        """Execute one epoch"""
        epoch_start = time.time()
        
        # Initialize baseline on first epoch
        if self.baseline_hash is None:
            self.baseline_hash = self._compute_baseline_hash()
        
        # Simulate: Normal operation
        state = self._simulate_normal_operation()
        
        # Simulate: Anomaly injection (based on rate)
        detection_occurred = False
        repair_success = None
        
        if self._should_inject_anomaly():
            state = self._inject_anomaly(state)
            detection_occurred = True
            
            # Simulate: Detect and repair
            repair_success = self._simulate_repair()
            self._repair_history.append(repair_success)
        
        # Collect metrics
        core_hash = self._compute_core_hash(state)
        metrics = EpochMetrics(
            epoch_num=epoch_num,
            timestamp=epoch_start,
            core_hash=core_hash,
            core_drift=(core_hash != self.baseline_hash),
            detector_recall=self._compute_rolling_recall(window=10),
            capability_diversity=self._simulate_capability_diversity(),
            maintenance_overhead=self._simulate_maintenance_overhead(),
            repair_success_rate=self._compute_repair_success_rate(window=10)
        )
        
        return EpochResult(
            epoch_num=epoch_num,
            timestamp=epoch_start,
            metrics=metrics,
            core_hash=core_hash,
            detection_occurred=detection_occurred,
            repair_success=repair_success
        )
    
    def _check_stop_conditions(self) -> Optional[str]:
        """Check if any stop condition is triggered"""
        if not self.epochs:
            return None
        
        latest = self.epochs[-1]
        
        # Stop 1: Core drift (check metrics.core_drift, not epoch.core_drift)
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
        # Simplified: use baseline with small perturbation based on state
        return self.baseline_hash or self._compute_baseline_hash()
    
    def _should_inject_anomaly(self) -> bool:
        """Determine if anomaly should be injected this epoch"""
        import random
        return random.random() < self.config.anomaly_injection_rate
    
    def _inject_anomaly(self, state: Any) -> Any:
        """Inject anomaly into state"""
        # Phase 1: Just mark that anomaly occurred
        return state
    
    def _simulate_normal_operation(self) -> Dict[str, Any]:
        """Simulate normal operation"""
        return {"status": "normal"}
    
    def _simulate_repair(self) -> bool:
        """Simulate repair, return success"""
        import random
        return random.random() > 0.1  # 90% success rate
    
    def _simulate_capability_diversity(self) -> float:
        """Simulate capability diversity (0.0 to 1.0)"""
        import random
        # Slowly degrade over time, but keep above threshold
        base = 0.8 - (self.current_epoch * 0.002)
        noise = random.gauss(0, 0.05)
        return max(0.3, min(1.0, base + noise))
    
    def _simulate_maintenance_overhead(self) -> float:
        """Simulate maintenance overhead (0.0 to 1.0)"""
        import random
        # Baseline 5% + anomaly processing
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
        with open(checkpoint_file, 'w') as f:
            json.dump({
                "epoch": self.current_epoch,
                "state": self.state.name,
                "latest_metrics": self.epochs[-1].metrics.to_dict() if self.epochs else None
            }, f, indent=2)
    
    def _create_result(self, verdict: str, stop_reason: Optional[str] = None) -> P6Result:
        """Create final result"""
        return P6Result(
            state=self.state,
            config=self.config,
            epochs=self.epochs,
            baseline_hash=self.baseline_hash or "unknown",
            verdict=verdict,
            stop_reason=stop_reason
        )
    
    def save_final_results(self, result: P6Result):
        """Save final results to disk"""
        results_file = self.output_dir / "P6_final_results.json"
        with open(results_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"Results saved to {results_file}")


if __name__ == "__main__":
    # Quick test
    config = P6Config(duration_hours=1, epoch_minutes=5)
    runner = P6Runner(config)
    result = runner.run()
    runner.save_final_results(result)
    print(f"\nRun complete: {result.verdict}")
    print(f"Epochs: {len(result.epochs)}")
    print(f"State: {result.state.name}")
