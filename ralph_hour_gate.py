#!/usr/bin/env python3
"""
Ralph Hour Gate - Atlas-HEC Adaptation
External budget controller for 1-hour experiment batches
Based on ralph-wiggum plugin architecture
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
import argparse

class RalphHourGate:
    """
    Ralph-style external controller for Atlas-HEC experiments
    Enforces: 1-hour rule + positive feedback → auto-extend
    """
    
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.experiment_name = self.config["experiment_name"]
        self.batch_number = self.config.get("batch_number", 1)
        self.max_hours = self.config.get("max_hours", 10)
        self.hour_budget = 0  # Accumulated approved hours
        
        # Thresholds for positive feedback
        self.thresholds = self.config["positive_feedback_thresholds"]
        
        # Execution config
        self.command = self.config["batch_command"]
        self.working_dir = Path(self.config.get("working_dir", "."))
        self.output_dir = Path(self.config.get("output_dir", "ralph_runs"))
        self.output_dir.mkdir(exist_ok=True)
        
        self.log_file = self.output_dir / f"{self.experiment_name}_ralph.log"
        
    def log(self, level, message, data=None):
        """Structured logging"""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "level": level,
            "experiment": self.experiment_name,
            "batch": self.batch_number,
            "hour_budget": self.hour_budget,
            "message": message
        }
        if data:
            entry["data"] = data
        
        # Console output
        print(f"[{timestamp}] [{level}] Batch-{self.batch_number}: {message}")
        
        # File logging
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    
    def run_batch(self, hour_number):
        """Execute one hour batch with timeout enforcement"""
        self.log("INFO", f"Starting Hour-{hour_number}", {
            "command": self.command,
            "timeout": 3600,
            "working_dir": str(self.working_dir)
        })
        
        # Build command with hour-specific config
        cmd = [
            "timeout", "3600",  # Hard 1-hour limit
            "python3", self.command,
            "--hour", str(hour_number),
            "--config", self.config["batch_config"],
            "--output-dir", str(self.output_dir / f"hour_{hour_number}")
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=3660  # Slightly over to catch timeout violations
            )
            
            elapsed = time.time() - start_time
            
            self.log("INFO", f"Hour-{hour_number} completed", {
                "elapsed_seconds": round(elapsed, 1),
                "return_code": result.returncode,
                "stdout_preview": result.stdout[:200] if result.stdout else None
            })
            
            return {
                "success": result.returncode == 0,
                "elapsed": elapsed,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output_dir": self.output_dir / f"hour_{hour_number}"
            }
            
        except subprocess.TimeoutExpired:
            self.log("ERROR", f"Hour-{hour_number} exceeded 1-hour limit")
            return {"success": False, "error": "TIMEOUT_VIOLATION"}
        except Exception as e:
            self.log("ERROR", f"Hour-{hour_number} execution failed", {"error": str(e)})
            return {"success": False, "error": str(e)}
    
    def read_metrics(self, hour_number):
        """Read metrics file produced by batch"""
        metrics_file = self.output_dir / f"hour_{hour_number}" / "metrics.json"
        
        if not metrics_file.exists():
            self.log("ERROR", f"Metrics file not found: {metrics_file}")
            return None
        
        try:
            with open(metrics_file) as f:
                metrics = json.load(f)
            
            self.log("INFO", f"Hour-{hour_number} metrics loaded", metrics)
            return metrics
            
        except Exception as e:
            self.log("ERROR", f"Failed to read metrics", {"error": str(e)})
            return None
    
    def evaluate_positive_feedback(self, metrics):
        """
        Check if metrics meet positive feedback thresholds
        Returns: (passed, reasons)
        """
        checks = []
        
        for metric_name, threshold in self.thresholds.items():
            if metric_name not in metrics:
                checks.append({
                    "metric": metric_name,
                    "status": "MISSING",
                    "passed": False
                })
                continue
            
            value = metrics[metric_name]
            operator = threshold.get("operator", ">=")
            target = threshold["value"]
            
            if operator == ">=":
                passed = value >= target
            elif operator == ">":
                passed = value > target
            elif operator == "<=":
                passed = value <= target
            elif operator == "==":
                passed = value == target
            else:
                passed = False
            
            checks.append({
                "metric": metric_name,
                "value": value,
                "threshold": target,
                "operator": operator,
                "passed": passed
            })
        
        all_passed = all(c["passed"] for c in checks)
        
        self.log("INFO", "Feedback evaluation complete", {
            "all_passed": all_passed,
            "checks": checks
        })
        
        return all_passed, checks
    
    def write_next_hour_config(self, hour_number):
        """Generate config for next hour if approved"""
        next_config = self.config.copy()
        next_config["batch_number"] = hour_number + 1
        next_config["previous_batch"] = hour_number
        next_config["hour_budget"] = self.hour_budget + 1
        
        config_path = self.output_dir / f"hour_{hour_number + 1}_config.json"
        with open(config_path, 'w') as f:
            json.dump(next_config, f, indent=2)
        
        self.log("INFO", f"Generated Hour-{hour_number + 1} config", {
            "config_path": str(config_path)
        })
        
        return config_path
    
    def write_negative_result(self, hour_number, reason):
        """Write negative result and freeze"""
        result = {
            "experiment": self.experiment_name,
            "batch": self.batch_number,
            "hour": hour_number,
            "status": "NEGATIVE",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "action": "FREEZE_EXPERIMENT",
            "ralph_decision": "STOP_NO_EXTENSION"
        }
        
        result_file = self.output_dir / f"hour_{hour_number}_ralph_decision.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        self.log("WARN", f"Negative result recorded", result)
    
    def run(self):
        """Main execution loop"""
        self.log("INFO", "Ralph Hour Gate starting", {
            "config": self.config,
            "max_hours": self.max_hours
        })
        
        hour = 1
        
        while hour <= self.max_hours:
            self.log("INFO", f"=== Hour {hour} of max {self.max_hours} ===")
            
            # Execute batch
            batch_result = self.run_batch(hour)
            
            if not batch_result["success"]:
                self.log("ERROR", f"Hour-{hour} execution failed", batch_result)
                self.write_negative_result(hour, "EXECUTION_FAILURE")
                return False
            
            # Read metrics
            metrics = self.read_metrics(hour)
            
            if metrics is None:
                self.write_negative_result(hour, "METRICS_UNAVAILABLE")
                return False
            
            # Evaluate feedback
            positive, checks = self.evaluate_positive_feedback(metrics)
            
            if positive:
                self.hour_budget += 1
                self.log("INFO", f"POSITIVE FEEDBACK: Hour-{hour} approved for extension", {
                    "accumulated_budget": self.hour_budget
                })
                
                # Generate next hour config (but don't auto-execute)
                next_config = self.write_next_hour_config(hour)
                
                self.log("INFO", f"Batch-{self.batch_number} can proceed to Hour-{hour + 1}", {
                    "next_config": str(next_config),
                    "manual_approval_required": True
                })
                
                # For auto-continuation mode (if enabled)
                if self.config.get("auto_continue", False) and hour < self.max_hours:
                    self.log("INFO", "Auto-continue enabled, proceeding to next hour")
                    hour += 1
                    continue
                else:
                    # Stop and wait for external approval
                    self.log("INFO", "Stopping for external approval")
                    return {
                        "status": "POSITIVE_FEEDBACK",
                        "hours_completed": hour,
                        "next_hour_available": hour + 1,
                        "next_config": str(next_config)
                    }
            else:
                self.log("WARN", f"NEGATIVE FEEDBACK: Hour-{hour} does not meet thresholds", {
                    "checks": checks
                })
                self.write_negative_result(hour, "NEGATIVE_FEEDBACK")
                return False
            
            hour += 1
        
        self.log("INFO", f"Reached max hours ({self.max_hours})")
        return True

def main():
    parser = argparse.ArgumentParser(description="Ralph Hour Gate for Atlas-HEC")
    parser.add_argument("--config", required=True, help="Gate configuration JSON")
    parser.add_argument("--output-dir", default="ralph_runs", help="Output directory")
    
    args = parser.parse_args()
    
    gate = RalphHourGate(args.config)
    result = gate.run()
    
    print("\n" + "="*70)
    print("RALPH HOUR GATE COMPLETE")
    print("="*70)
    
    if result == True:
        print("Status: All hours completed successfully")
    elif result == False:
        print("Status: STOPPED (negative feedback or error)")
        sys.exit(1)
    else:
        print(f"Status: {result.get('status')}")
        print(f"Hours completed: {result.get('hours_completed')}")
        print(f"Next hour available: {result.get('next_hour_available')}")
        print(f"Next config: {result.get('next_config')}")

if __name__ == "__main__":
    main()
