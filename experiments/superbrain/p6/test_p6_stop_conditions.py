"""
P6 Stop Conditions Tests - Phase 2
===================================
Gate 3: All 4 hard stops implemented and tested
"""

import pytest
from p6_runner import P6Runner, P6Config, EpochResult, EpochMetrics, RunnerState


class TestStopConditionCoreDrift:
    """Stop 1: Core drift detection"""
    
    def test_stop_on_core_drift(self):
        """
        Gate 3a: Core drift triggers immediate halt
        
        If core hash changes from baseline, run should HALT
        """
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        
        # Run a few epochs normally
        result_partial = runner.run()
        
        # Now create a new runner and simulate drift
        runner2 = P6Runner(config)
        runner2.baseline_hash = "original_hash"
        
        # Create epoch with drift
        drift_epoch = EpochResult(
            epoch_num=0,
            timestamp=0,
            metrics=EpochMetrics(
                epoch_num=0,
                timestamp=0,
                core_hash="modified_hash",  # Different from baseline
                core_drift=True,  # Drift detected
                detector_recall=1.0,
                capability_diversity=0.8,
                maintenance_overhead=0.05,
                repair_success_rate=1.0
            ),
            core_hash="modified_hash",
            detection_occurred=False
        )
        
        runner2.epochs = [drift_epoch]
        runner2.baseline_hash = "original_hash"
        
        stop_reason = runner2._check_stop_conditions()
        
        assert stop_reason is not None, "Should detect stop condition"
        assert "core_drift" in stop_reason, f"Expected core_drift, got {stop_reason}"
    
    def test_no_stop_without_drift(self):
        """No drift should not trigger stop"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        
        # Run normal epochs
        result = runner.run()
        
        # Should complete without stop
        assert result.state == RunnerState.COMPLETE
        assert result.stop_reason is None


class TestStopConditionDetectorDegradation:
    """Stop 2: Detector degradation (3 epochs recall < 0.6)"""
    
    def test_stop_on_detector_degradation(self):
        """
        Gate 3b: 3 consecutive epochs with recall < 0.6 triggers halt
        """
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        runner.baseline_hash = "test_baseline"
        
        # Create 3 epochs with low recall
        for i in range(3):
            epoch = EpochResult(
                epoch_num=i,
                timestamp=i,
                metrics=EpochMetrics(
                    epoch_num=i,
                    timestamp=i,
                    core_hash="test_baseline",
                    core_drift=False,
                    detector_recall=0.5,  # Below 0.6
                    capability_diversity=0.8,
                    maintenance_overhead=0.05,
                    repair_success_rate=1.0
                ),
                core_hash="test_baseline",
                detection_occurred=False
            )
            runner.epochs.append(epoch)
        
        stop_reason = runner._check_stop_conditions()
        
        assert stop_reason is not None
        assert "detector_degradation" in stop_reason
    
    def test_no_stop_with_good_recall(self):
        """Good recall should not trigger stop"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        runner.baseline_hash = "test_baseline"
        
        # Create 3 epochs with good recall
        for i in range(3):
            epoch = EpochResult(
                epoch_num=i,
                timestamp=i,
                metrics=EpochMetrics(
                    epoch_num=i,
                    timestamp=i,
                    core_hash="test_baseline",
                    core_drift=False,
                    detector_recall=0.9,  # Good
                    capability_diversity=0.8,
                    maintenance_overhead=0.05,
                    repair_success_rate=1.0
                ),
                core_hash="test_baseline",
                detection_occurred=False
            )
            runner.epochs.append(epoch)
        
        stop_reason = runner._check_stop_conditions()
        
        assert stop_reason is None
    
    def test_partial_low_recall_no_stop(self):
        """Only 2 epochs low recall should not trigger stop"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        runner.baseline_hash = "test_baseline"
        
        # 2 low, 1 good
        recalls = [0.5, 0.5, 0.9]
        for i in range(3):
            epoch = EpochResult(
                epoch_num=i,
                timestamp=i,
                metrics=EpochMetrics(
                    epoch_num=i,
                    timestamp=i,
                    core_hash="test_baseline",
                    core_drift=False,
                    detector_recall=recalls[i],
                    capability_diversity=0.8,
                    maintenance_overhead=0.05,
                    repair_success_rate=1.0
                ),
                core_hash="test_baseline",
                detection_occurred=False
            )
            runner.epochs.append(epoch)
        
        stop_reason = runner._check_stop_conditions()
        
        assert stop_reason is None


class TestStopConditionCapabilityExhaustion:
    """Stop 3: Capability diversity below 20%"""
    
    def test_stop_on_capability_exhaustion(self):
        """
        Gate 3c: Capability diversity < 20% triggers halt
        """
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        runner.baseline_hash = "test_baseline"
        
        epoch = EpochResult(
            epoch_num=0,
            timestamp=0,
            metrics=EpochMetrics(
                epoch_num=0,
                timestamp=0,
                core_hash="test_baseline",
                core_drift=False,
                detector_recall=0.9,
                capability_diversity=0.15,  # Below 20%
                maintenance_overhead=0.05,
                repair_success_rate=1.0
            ),
            core_hash="test_baseline",
            detection_occurred=False
        )
        runner.epochs.append(epoch)
        
        stop_reason = runner._check_stop_conditions()
        
        assert stop_reason is not None
        assert "capability_exhaustion" in stop_reason
    
    def test_no_stop_with_good_diversity(self):
        """Diversity above 20% should not trigger stop"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        runner.baseline_hash = "test_baseline"
        
        epoch = EpochResult(
            epoch_num=0,
            timestamp=0,
            metrics=EpochMetrics(
                epoch_num=0,
                timestamp=0,
                core_hash="test_baseline",
                core_drift=False,
                detector_recall=0.9,
                capability_diversity=0.5,  # Good
                maintenance_overhead=0.05,
                repair_success_rate=1.0
            ),
            core_hash="test_baseline",
            detection_occurred=False
        )
        runner.epochs.append(epoch)
        
        stop_reason = runner._check_stop_conditions()
        
        assert stop_reason is None


class TestStopConditionMaintenanceOverload:
    """Stop 4: Maintenance overhead above 30%"""
    
    def test_stop_on_maintenance_overload(self):
        """
        Gate 3d: Maintenance overhead > 30% triggers halt
        """
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        runner.baseline_hash = "test_baseline"
        
        epoch = EpochResult(
            epoch_num=0,
            timestamp=0,
            metrics=EpochMetrics(
                epoch_num=0,
                timestamp=0,
                core_hash="test_baseline",
                core_drift=False,
                detector_recall=0.9,
                capability_diversity=0.8,
                maintenance_overhead=0.35,  # Above 30%
                repair_success_rate=1.0
            ),
            core_hash="test_baseline",
            detection_occurred=False
        )
        runner.epochs.append(epoch)
        
        stop_reason = runner._check_stop_conditions()
        
        assert stop_reason is not None
        assert "maintenance_overload" in stop_reason
    
    def test_no_stop_with_normal_overhead(self):
        """Overhead below 30% should not trigger stop"""
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        runner.baseline_hash = "test_baseline"
        
        epoch = EpochResult(
            epoch_num=0,
            timestamp=0,
            metrics=EpochMetrics(
                epoch_num=0,
                timestamp=0,
                core_hash="test_baseline",
                core_drift=False,
                detector_recall=0.9,
                capability_diversity=0.8,
                maintenance_overhead=0.1,  # Normal
                repair_success_rate=1.0
            ),
            core_hash="test_baseline",
            detection_occurred=False
        )
        runner.epochs.append(epoch)
        
        stop_reason = runner._check_stop_conditions()
        
        assert stop_reason is None


# ============================================================================
# Gate 3: All Stop Conditions Integration
# ============================================================================

def test_all_four_stop_conditions():
    """
    Gate 3 Integration: Verify all 4 stop conditions are implemented
    
    This test verifies the presence and basic functionality of all 4 hard stops.
    """
    config = P6Config(duration_hours=1, epoch_minutes=5)
    
    # Test 1: Core drift
    runner1 = P6Runner(config)
    runner1.baseline_hash = "baseline"
    runner1.epochs.append(EpochResult(
        epoch_num=0, timestamp=0,
        metrics=EpochMetrics(
            epoch_num=0, timestamp=0,
            core_hash="different",
            core_drift=True,
            detector_recall=1.0, capability_diversity=0.8,
            maintenance_overhead=0.05, repair_success_rate=1.0
        ),
        core_hash="different", detection_occurred=False
    ))
    assert runner1._check_stop_conditions() is not None
    
    # Test 2: Detector degradation
    runner2 = P6Runner(config)
    runner2.baseline_hash = "baseline"
    for i in range(3):
        runner2.epochs.append(EpochResult(
            epoch_num=i, timestamp=i,
            metrics=EpochMetrics(
                epoch_num=i, timestamp=i,
                core_hash="baseline", core_drift=False,
                detector_recall=0.5, capability_diversity=0.8,
                maintenance_overhead=0.05, repair_success_rate=1.0
            ),
            core_hash="baseline", detection_occurred=False
        ))
    assert runner2._check_stop_conditions() is not None
    
    # Test 3: Capability exhaustion
    runner3 = P6Runner(config)
    runner3.baseline_hash = "baseline"
    runner3.epochs.append(EpochResult(
        epoch_num=0, timestamp=0,
        metrics=EpochMetrics(
            epoch_num=0, timestamp=0,
            core_hash="baseline", core_drift=False,
            detector_recall=1.0, capability_diversity=0.15,
            maintenance_overhead=0.05, repair_success_rate=1.0
        ),
        core_hash="baseline", detection_occurred=False
    ))
    assert runner3._check_stop_conditions() is not None
    
    # Test 4: Maintenance overload
    runner4 = P6Runner(config)
    runner4.baseline_hash = "baseline"
    runner4.epochs.append(EpochResult(
        epoch_num=0, timestamp=0,
        metrics=EpochMetrics(
            epoch_num=0, timestamp=0,
            core_hash="baseline", core_drift=False,
            detector_recall=1.0, capability_diversity=0.8,
            maintenance_overhead=0.35, repair_success_rate=1.0
        ),
        core_hash="baseline", detection_occurred=False
    ))
    assert runner4._check_stop_conditions() is not None
    
    print("\n✓ Gate 3 PASSED: All 4 stop conditions implemented")
    print("  1. Core drift detection")
    print("  2. Detector degradation (3 epochs < 0.6)")
    print("  3. Capability exhaustion (< 20%)")
    print("  4. Maintenance overload (> 30%)")
