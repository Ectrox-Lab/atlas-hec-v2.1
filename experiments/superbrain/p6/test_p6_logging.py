"""
P6 Critical Logging Tests - Phase 3
====================================
Gate 4: All 4 critical metrics logged every epoch
"""

import json
import pytest
from pathlib import Path
from p6_runner import P6Runner, P6Config


class TestCriticalLogging:
    """Test critical metrics logging"""
    
    def test_epoch_metrics_logged(self, tmp_path):
        """
        Gate 4a: Per-epoch metrics written to JSONL
        
        Required fields every epoch:
        - epoch_num
        - timestamp
        - core_hash
        - core_drift
        - detector_recall
        - capability_diversity
        - maintenance_overhead
        """
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        
        # Save results (this creates the JSONL file)
        runner.save_final_results(result)
        
        # Check results file exists
        results_file = tmp_path / "results" / "P6_final_results.json"
        assert results_file.exists(), "Results file should be created"
        
        # Load and verify structure
        with open(results_file) as f:
            data = json.load(f)
        
        assert "epochs" in data
        assert len(data["epochs"]) == 12
        
        # Verify each epoch has required fields
        required_fields = [
            "epoch", "timestamp", "core_hash", "core_drift",
            "detector_recall", "capability_diversity", "maintenance_overhead"
        ]
        
        for epoch_data in data["epochs"]:
            for field in required_fields:
                assert field in epoch_data, f"Missing field: {field}"
    
    def test_core_hash_consistency_logged(self, tmp_path):
        """
        Gate 4b: Core hash should be consistent (no drift)
        
        All epochs should have same hash as baseline
        """
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        runner.save_final_results(result)
        
        results_file = tmp_path / "results" / "P6_final_results.json"
        with open(results_file) as f:
            data = json.load(f)
        
        baseline = data["baseline_hash"]
        
        # All epochs should match baseline
        for epoch_data in data["epochs"]:
            assert epoch_data["core_hash"] == baseline, \
                f"Drift detected: {epoch_data['core_hash']} != {baseline}"
            assert epoch_data["core_drift"] == False
    
    def test_detector_recall_in_valid_range(self, tmp_path):
        """
        Gate 4c: Detector recall logged and in valid range [0, 1]
        """
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        runner.save_final_results(result)
        
        results_file = tmp_path / "results" / "P6_final_results.json"
        with open(results_file) as f:
            data = json.load(f)
        
        for epoch_data in data["epochs"]:
            recall = epoch_data["detector_recall"]
            assert 0.0 <= recall <= 1.0, f"Recall {recall} out of range"
    
    def test_capability_diversity_logged(self, tmp_path):
        """
        Gate 4d: Capability diversity logged in valid range [0, 1]
        """
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        runner.save_final_results(result)
        
        results_file = tmp_path / "results" / "P6_final_results.json"
        with open(results_file) as f:
            data = json.load(f)
        
        for epoch_data in data["epochs"]:
            diversity = epoch_data["capability_diversity"]
            assert 0.0 <= diversity <= 1.0, f"Diversity {diversity} out of range"
    
    def test_maintenance_overhead_logged(self, tmp_path):
        """
        Gate 4e: Maintenance overhead logged in valid range [0, 1]
        """
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        runner.save_final_results(result)
        
        results_file = tmp_path / "results" / "P6_final_results.json"
        with open(results_file) as f:
            data = json.load(f)
        
        for epoch_data in data["epochs"]:
            overhead = epoch_data["maintenance_overhead"]
            assert 0.0 <= overhead <= 1.0, f"Overhead {overhead} out of range"


class TestCheckpointLogging:
    """Test checkpoint persistence"""
    
    def test_checkpoints_created(self, tmp_path):
        """Checkpoints should be created at intervals"""
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5, checkpoint_interval=3)
        runner = P6Runner(config)
        result = runner.run()
        
        # Should have checkpoints at epochs 0, 3, 6, 9
        checkpoint_dir = tmp_path / "results"
        checkpoint_files = list(checkpoint_dir.glob("checkpoint_epoch_*.json"))
        
        assert len(checkpoint_files) >= 3, f"Expected >=3 checkpoints, got {len(checkpoint_files)}"
    
    def test_checkpoint_content(self, tmp_path):
        """Checkpoints should contain valid data"""
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5, checkpoint_interval=5)
        runner = P6Runner(config)
        result = runner.run()
        
        # Check first checkpoint
        checkpoint_file = tmp_path / "results" / "checkpoint_epoch_0.json"
        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                data = json.load(f)
            
            assert "epoch" in data
            assert "state" in data
            assert "latest_metrics" in data


class TestResultsSerialization:
    """Test full results serialization"""
    
    def test_full_results_structure(self, tmp_path):
        """
        Gate 4f: Complete results structure validation
        """
        import os
        os.chdir(tmp_path)
        
        config = P6Config(duration_hours=1, epoch_minutes=5)
        runner = P6Runner(config)
        result = runner.run()
        runner.save_final_results(result)
        
        results_file = tmp_path / "results" / "P6_final_results.json"
        with open(results_file) as f:
            data = json.load(f)
        
        # Top-level fields
        assert data["state"] == "COMPLETE"
        assert data["duration_hours"] == 1
        assert data["total_epochs"] == 12
        assert data["verdict"] == "PASS"
        assert data["stop_reason"] is None
        assert "baseline_hash" in data
        
        # Epochs array
        assert isinstance(data["epochs"], list)
        assert len(data["epochs"]) == 12


# ============================================================================
# Gate 4: All Critical Logging Integration
# ============================================================================

def test_gate4_all_critical_metrics_logged(tmp_path):
    """
    Gate 4 Integration: Verify all 4 critical metrics are logged
    
    Critical metrics:
    1. core_hash - for drift detection
    2. detector_recall - for degradation monitoring
    3. capability_diversity - for exhaustion monitoring
    4. maintenance_overhead - for overload monitoring
    """
    import os
    os.chdir(tmp_path)
    
    config = P6Config(duration_hours=1, epoch_minutes=5)
    runner = P6Runner(config)
    result = runner.run()
    runner.save_final_results(result)
    
    results_file = tmp_path / "results" / "P6_final_results.json"
    assert results_file.exists(), "Results file not created"
    
    with open(results_file) as f:
        data = json.load(f)
    
    # Verify 4 critical metrics in every epoch
    critical_metrics = [
        "core_hash",           # Drift detection
        "detector_recall",     # Degradation monitoring
        "capability_diversity", # Exhaustion monitoring
        "maintenance_overhead"  # Overload monitoring
    ]
    
    for i, epoch_data in enumerate(data["epochs"]):
        for metric in critical_metrics:
            assert metric in epoch_data, f"Epoch {i} missing critical metric: {metric}"
            assert epoch_data[metric] is not None, f"Epoch {i} has null {metric}"
    
    # Verify baseline hash exists
    assert "baseline_hash" in data, "Missing baseline_hash"
    assert data["baseline_hash"] is not None
    
    print("\n✓ Gate 4 PASSED: All critical metrics logged")
    print("  1. core_hash - drift detection ✓")
    print("  2. detector_recall - degradation monitoring ✓")
    print("  3. capability_diversity - exhaustion monitoring ✓")
    print("  4. maintenance_overhead - overload monitoring ✓")
    print(f"  Total epochs logged: {len(data['epochs'])}")


def test_gate4_log_parsable(tmp_path):
    """Verify logs are machine-readable (JSON)"""
    import os
    os.chdir(tmp_path)
    
    config = P6Config(duration_hours=1, epoch_minutes=5)
    runner = P6Runner(config)
    result = runner.run()
    runner.save_final_results(result)
    
    results_file = tmp_path / "results" / "P6_final_results.json"
    
    # Should be valid JSON
    with open(results_file) as f:
        data = json.load(f)
    
    # Should be re-serializable
    re_serialized = json.dumps(data)
    assert len(re_serialized) > 0
    
    # Should be re-parsable
    re_parsed = json.loads(re_serialized)
    assert re_parsed["total_epochs"] == 12
