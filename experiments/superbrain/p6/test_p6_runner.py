"""
P6 Runner Tests - Phase 1
=========================
Basic epoch loop and state machine validation.
"""

import pytest
import time
from p6_runner import (
    P6Runner, P6Config, RunnerState,
    EpochMetrics, EpochResult
)


class TestP6Config:
    """Test configuration calculations"""
    
    def test_1h_config(self):
        """1 hour with 5-min epochs = 12 epochs"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        assert config.total_epochs == 12
        assert config.is_test_mode == True
    
    def test_24h_config(self):
        """24 hours with 60-min epochs = 24 epochs"""
        config = P6Config(duration_hours=24, epoch_minutes=60)
        assert config.total_epochs == 24
        assert config.is_test_mode == False
    
    def test_72h_config(self):
        """72 hours with 60-min epochs = 72 epochs"""
        config = P6Config(duration_hours=72, epoch_minutes=60)
        assert config.total_epochs == 72
        assert config.is_test_mode == False


class TestP6RunnerBasic:
    """Test basic runner functionality"""
    
    def test_runner_init(self):
        """Runner initializes in INIT state"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        assert runner.state == RunnerState.INIT
        assert runner.current_epoch == 0
        assert len(runner.epochs) == 0
    
    def test_runner_1h_smoke(self):
        """
        Gate 2: 1-hour smoke test
        
        12 epochs, completes successfully, no core drift
        """
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        
        result = runner.run()
        
        # Should complete
        assert result.state == RunnerState.COMPLETE
        assert result.verdict == "PASS"
        
        # Should have 12 epochs
        assert len(result.epochs) == 12
        
        # All epochs should have metrics
        for epoch in result.epochs:
            assert epoch.metrics is not None
            assert epoch.metrics.epoch_num >= 0
            assert epoch.core_hash is not None
        
        # No stop reason (normal completion)
        assert result.stop_reason is None
    
    def test_baseline_hash_consistent(self):
        """Baseline hash should be consistent across runs"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        
        runner1 = P6Runner(config)
        result1 = runner1.run()
        
        runner2 = P6Runner(config)
        result2 = runner2.run()
        
        # Baseline should be deterministic
        assert result1.baseline_hash == result2.baseline_hash
        
        # All epochs should match baseline (no drift in smoke test)
        for epoch in result1.epochs:
            assert epoch.core_hash == result1.baseline_hash
            assert not epoch.metrics.core_drift


class TestP6Metrics:
    """Test metrics collection"""
    
    def test_metrics_structure(self):
        """Metrics should have all required fields"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        
        for epoch in result.epochs:
            m = epoch.metrics
            assert isinstance(m.epoch_num, int)
            assert isinstance(m.timestamp, float)
            assert isinstance(m.core_hash, str)
            assert isinstance(m.core_drift, bool)
            assert 0.0 <= m.detector_recall <= 1.0
            assert 0.0 <= m.capability_diversity <= 1.0
            assert 0.0 <= m.maintenance_overhead <= 1.0
            assert 0.0 <= m.repair_success_rate <= 1.0
    
    def test_metrics_serialization(self):
        """Metrics should serialize to dict"""
        metrics = EpochMetrics(
            epoch_num=0,
            timestamp=time.time(),
            core_hash="test_hash",
            core_drift=False,
            detector_recall=0.85,
            capability_diversity=0.7,
            maintenance_overhead=0.05,
            repair_success_rate=0.9
        )
        
        d = metrics.to_dict()
        assert d["epoch"] == 0
        assert d["core_hash"] == "test_hash"
        assert d["core_drift"] == False
        assert d["detector_recall"] == 0.85


class TestP6Checkpoint:
    """Test checkpoint persistence"""
    
    def test_checkpoint_creation(self, tmp_path):
        """Checkpoints should be created during run"""
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5, checkpoint_interval=5)
        runner = P6Runner(config)
        result = runner.run()
        
        # Should have checkpoints at epochs 0, 5, 10
        checkpoint_files = list(tmp_path.glob("results/checkpoint_epoch_*.json"))
        assert len(checkpoint_files) >= 2  # At least 2 checkpoints


class TestP6StateMachine:
    """Test state machine transitions"""
    
    def test_state_transitions(self):
        """State should progress: INIT -> RUNNING -> COMPLETE"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        
        assert runner.state == RunnerState.INIT
        
        result = runner.run()
        
        assert result.state == RunnerState.COMPLETE


class TestP6Result:
    """Test result structure"""
    
    def test_result_serialization(self):
        """Result should serialize properly"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        
        d = result.to_dict()
        assert d["state"] == "COMPLETE"
        assert d["verdict"] == "PASS"
        assert d["duration_hours"] == 1
        assert d["total_epochs"] == 12
        assert d["baseline_hash"] is not None
        assert d["stop_reason"] is None
        assert isinstance(d["epochs"], list)
        assert len(d["epochs"]) == 12


# ============================================================================
# Gate 2: 1h Smoke Test (Explicit)
# ============================================================================

def test_gate2_1h_smoke_explicit():
    """
    Gate 2 Explicit Verification:
    
    - 12 epochs completed
    - 0 core drift
    - All epochs have metrics
    - State machine: INIT -> RUN -> COMPLETE
    """
    config = P6Config(duration_hours=1, epoch_minutes=5)
    runner = P6Runner(config)
    
    # Pre-condition: INIT state
    assert runner.state == RunnerState.INIT
    
    # Run
    result = runner.run()
    
    # Post-conditions
    assert result.state == RunnerState.COMPLETE, f"Expected COMPLETE, got {result.state.name}"
    assert len(result.epochs) == 12, f"Expected 12 epochs, got {len(result.epochs)}"
    
    # No core drift
    drift_count = sum(1 for e in result.epochs if e.metrics.core_drift)
    assert drift_count == 0, f"Expected 0 drift, got {drift_count}"
    
    # All epochs have metrics
    for i, epoch in enumerate(result.epochs):
        assert epoch.metrics is not None, f"Epoch {i} missing metrics"
        assert epoch.core_hash == result.baseline_hash, f"Epoch {i} hash mismatch"
    
    print(f"\n✓ Gate 2 PASSED: 1h smoke test")
    print(f"  Epochs: {len(result.epochs)}")
    print(f"  State: {result.state.name}")
    print(f"  Drift epochs: {drift_count}")


# ============================================================================
# Integration: Short run simulation
# ============================================================================

def test_short_run_simulation():
    """
    Simulate a short run to verify full pipeline
    """
    config = P6Config(
        duration_hours=1,
        epoch_minutes=5,
        anomaly_injection_rate=0.2  # 20% anomaly rate
    )
    
    runner = P6Runner(config)
    result = runner.run()
    
    # Should complete
    assert result.verdict == "PASS"
    
    # Some epochs should have detections (with 20% rate, expect ~2-3)
    detection_count = sum(1 for e in result.epochs if e.detection_occurred)
    print(f"\nDetection count: {detection_count}/{len(result.epochs)}")
    
    # Verify metrics make sense
    for epoch in result.epochs:
        # Detector recall should be reasonable
        assert 0.0 <= epoch.metrics.detector_recall <= 1.0
        
        # Capability diversity should be reasonable
        assert 0.0 <= epoch.metrics.capability_diversity <= 1.0
        
        # Maintenance overhead should be reasonable
        assert 0.0 <= epoch.metrics.maintenance_overhead <= 1.0
