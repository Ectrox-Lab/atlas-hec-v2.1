#!/usr/bin/env python3
"""
Ralph Hour Gate - Atlas-HEC Adaptation v2.0
External budget controller for 1-hour experiment batches

Key Design Principles:
1. Three-state evaluation: POSITIVE / MARGINAL / FAIL
2. Complete audit trail with SHA256 hashes
3. STOP-APPLY-APPROVE-EXECUTE discipline
4. Ralph is budget gatekeeper, not experiment logic
"""

import json
import subprocess
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
import argparse

class RalphHourGate:
    """
    Ralph-style external controller for Atlas-HEC experiments
    Enforces: 1-hour rule + positive feedback → prepare next hour config (but STOP)
    """
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
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
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.output_dir / f"{self.experiment_name}_ralph.log"
        
    def _file_hash(self, filepath):
        """Compute SHA256 hash of file for audit trail"""
        if not Path(filepath).exists():
            return None
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def log(self, level, message, data=None):
        """Structured logging"""
        timestamp = datetime.utcnow().isoformat() + 'Z'
        entry = {
            "timestamp": timestamp,
            "level": level,
            "experiment": self.experiment_name,
            "batch": self.batch_number,
            "hour_budget": self.hour_budget,
            "message": message
        }
        if data:
            # Convert Path objects to strings for JSON serialization
            entry["data"] = self._serialize_for_json(data)
        
        # Console output
        print(f"[{timestamp}] [{level}] Batch-{self.batch_number}: {message}")
        
        # File logging
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    
    def _serialize_for_json(self, obj):
        """Convert non-JSON-serializable objects to strings"""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        return obj
    
    def run_batch(self, hour_number):
        """Execute one hour batch with timeout enforcement"""
        
        # Record start time and input hashes
        started_at = datetime.utcnow().isoformat() + 'Z'
        config_hash = self._file_hash(self.config_path)
        
        self.log("INFO", f"Starting Hour-{hour_number}", {
            "command": self.command,
            "timeout": 3600,
            "working_dir": str(self.working_dir),
            "config_sha256": config_hash
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
            ended_at = datetime.utcnow().isoformat() + 'Z'
            
            self.log("INFO", f"Hour-{hour_number} completed", {
                "elapsed_seconds": round(elapsed, 1),
                "return_code": result.returncode,
                "stdout_preview": result.stdout[:200] if result.stdout else None,
                "ended_at": ended_at
            })
            
            return {
                "success": result.returncode == 0,
                "elapsed": elapsed,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output_dir": self.output_dir / f"hour_{hour_number}",
                "audit": {
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "config_sha256": config_hash
                }
            }
            
        except subprocess.TimeoutExpired:
            self.log("ERROR", f"Hour-{hour_number} exceeded 1-hour limit")
            return {
                "success": False, 
                "error": "TIMEOUT_VIOLATION",
                "audit": {"started_at": started_at, "config_sha256": config_hash}
            }
        except Exception as e:
            self.log("ERROR", f"Hour-{hour_number} execution failed", {"error": str(e)})
            return {
                "success": False, 
                "error": str(e),
                "audit": {"started_at": started_at, "config_sha256": config_hash}
            }
    
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
    
    def evaluate_three_state(self, metrics):
        """
        Four-state evaluation with POSITIVE_AUTO for continuous operation:
        POSITIVE_AUTO / POSITIVE_MANUAL / MARGINAL / FAIL
        
        POSITIVE_AUTO: Exceeds strict thresholds → auto-continue (sleep mode)
        POSITIVE_MANUAL: Meets standard thresholds → generate config, wait approval
        MARGINAL: Ambiguous → freeze for analysis  
        FAIL: Clear failure → freeze and recommend rollback
        
        Returns: (verdict, details)
        """
        
        # Extract key metrics
        tg = metrics.get('transfer_gap_pp', 0)
        cr = metrics.get('code_retention_pct', 0)
        sg = metrics.get('self_gap_pp', 0)
        ls = metrics.get('leakage_status', 'unknown')
        
        # Check thresholds from config
        tg_threshold = self.thresholds.get('transfer_gap_pp', {}).get('value', 5)
        cr_threshold = self.thresholds.get('code_retention_pct', {}).get('value', 85)
        sg_threshold = self.thresholds.get('self_gap_pp', {}).get('value', 0)
        ls_threshold = self.thresholds.get('leakage_status', {}).get('value', 'clean')
        
        # Auto-approve strict thresholds (for sleep mode continuous operation)
        auto_thresholds = self.config.get('auto_approve_thresholds', {})
        tg_auto = auto_thresholds.get('transfer_gap_pp', {}).get('value', 10)
        cr_auto = auto_thresholds.get('code_retention_pct', {}).get('value', 90)
        sg_auto = auto_thresholds.get('self_gap_pp', {}).get('value', 5)
        ls_auto = auto_thresholds.get('leakage_status', {}).get('value', 'clean')
        
        # Circuit breakers (FAIL conditions)
        if tg <= 0:
            return "FAIL", {
                "reason": "NEGATIVE_TRANSFER",
                "transfer_gap_pp": tg,
                "description": "Transfer gap <= 0, no meaningful transfer"
            }
        
        if cr < 80:
            return "FAIL", {
                "reason": "CATASTROPHIC_FORGETTING",
                "code_retention_pct": cr,
                "description": "Retention below 80%, catastrophic forgetting detected"
            }
        
        if ls != ls_threshold:
            return "FAIL", {
                "reason": "LEAKAGE_DETECTED",
                "leakage_status": ls,
                "description": "Data leakage detected"
            }
        
        # Check POSITIVE_AUTO (strict thresholds for auto-continue)
        if (tg >= tg_auto and 
            cr >= cr_auto and 
            sg > sg_auto and 
            ls == ls_auto):
            return "POSITIVE_AUTO", {
                "reason": "AUTO_APPROVE_THRESHOLDS_MET",
                "transfer_gap_pp": tg,
                "code_retention_pct": cr,
                "self_gap_pp": sg,
                "thresholds": {"tg": tg_auto, "cr": cr_auto, "sg": sg_auto},
                "description": "Strict thresholds met - AUTO CONTINUING (sleep mode)"
            }
        
        # Check POSITIVE_MANUAL (standard thresholds)
        if (tg >= tg_threshold and 
            cr >= cr_threshold and 
            sg > sg_threshold and 
            ls == ls_threshold):
            return "POSITIVE_MANUAL", {
                "reason": "ALL_THRESHOLDS_MET",
                "transfer_gap_pp": tg,
                "code_retention_pct": cr,
                "self_gap_pp": sg,
                "description": "Standard thresholds satisfied - awaiting manual approval"
            }
        
        # MARGINAL: Some progress but not meeting full thresholds
        if tg > 0 and cr >= 80:
            return "MARGINAL", {
                "reason": "PARTIAL_PROGRESS",
                "transfer_gap_pp": tg,
                "code_retention_pct": cr,
                "description": f"Some progress (tg={tg}pp) but below threshold ({tg_threshold}pp)"
            }
        
        # FAIL: Default catch-all
        return "FAIL", {
            "reason": "INSUFFICIENT_PROGRESS",
            "transfer_gap_pp": tg,
            "code_retention_pct": cr,
            "description": "Insufficient progress on all metrics"
        }
    
    def write_positive_decision(self, hour_number, metrics, audit_trail, details):
        """Write POSITIVE decision with complete audit trail"""
        
        # Generate next hour config
        next_config = self.config.copy()
        next_config["batch_number"] = hour_number + 1
        next_config["previous_batch"] = hour_number
        next_config["hour_budget"] = self.hour_budget + 1
        next_config["approved_at"] = None  # Must be filled by human
        next_config["ralph_note"] = "AWAITING_APPROVAL - Do not execute until approved"
        
        config_path = self.output_dir / f"hour_{hour_number + 1}_config.json"
        with open(config_path, 'w') as f:
            json.dump(next_config, f, indent=2)
        
        # Write decision.json with full audit trail
        decision = {
            "verdict": "POSITIVE",
            "hour": hour_number,
            "metrics": {
                "transfer_gap_pp": metrics.get('transfer_gap_pp'),
                "code_retention_pct": metrics.get('code_retention_pct'),
                "self_gap_pp": metrics.get('self_gap_pp'),
                "leakage_status": metrics.get('leakage_status')
            },
            "details": details,
            "audit_trail": {
                "started_at": audit_trail.get('started_at'),
                "ended_at": audit_trail.get('ended_at'),
                "config_sha256": audit_trail.get('config_sha256'),
                "metrics_sha256": self._file_hash(
                    self.output_dir / f"hour_{hour_number}" / "metrics.json"
                ),
                "next_config_path": str(config_path),
                "next_config_sha256": self._file_hash(config_path)
            },
            "ralph_action": f"STOPPED - Hour-{hour_number + 1} config generated, awaiting approval",
            "human_required": True,
            "recommendation": "APPROVE_CONTINUE"
        }
        
        decision_path = self.output_dir / f"hour_{hour_number}_decision.json"
        with open(decision_path, 'w') as f:
            json.dump(decision, f, indent=2)
        
        self.log("INFO", f"POSITIVE: Hour-{hour_number + 1} config generated", {
            "decision_path": str(decision_path),
            "config_path": str(config_path)
        })
        
        return decision_path, config_path
    
    def write_negative_decision(self, hour_number, verdict, metrics, audit_trail, details):
        """Write MARGINAL or FAIL decision with complete audit trail"""
        
        # Write decision.json with full audit trail
        decision = {
            "verdict": verdict,  # MARGINAL or FAIL
            "hour": hour_number,
            "metrics": metrics,
            "details": details,
            "audit_trail": {
                "started_at": audit_trail.get('started_at'),
                "ended_at": audit_trail.get('ended_at'),
                "config_sha256": audit_trail.get('config_sha256'),
                "metrics_sha256": self._file_hash(
                    self.output_dir / f"hour_{hour_number}" / "metrics.json"
                ) if metrics else None
            },
            "ralph_action": f"FROZEN - {verdict} at Hour {hour_number}",
            "human_required": True,
            "recommendation": "ANALYZE" if verdict == "MARGINAL" else "ROLLBACK"
        }
        
        decision_path = self.output_dir / f"hour_{hour_number}_decision.json"
        with open(decision_path, 'w') as f:
            json.dump(decision, f, indent=2)
        
        # Write FROZEN marker
        freeze_file = self.output_dir / "FROZEN"
        with open(freeze_file, 'w') as f:
            f.write(f"FROZEN at Hour {hour_number}\n")
            f.write(f"Verdict: {verdict}\n")
            f.write(f"Reason: {details.get('reason', 'Unknown')}\n")
            f.write(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"Decision: {decision_path}\n")
            if metrics:
                f.write(f"\nMetrics:\n")
                f.write(json.dumps(metrics, indent=2))
        
        self.log("WARN" if verdict == "MARGINAL" else "ERROR", 
                 f"{verdict}: Experiment frozen at Hour-{hour_number}", {
            "decision_path": str(decision_path),
            "freeze_file": str(freeze_file),
            "details": details
        })
        
        return decision_path
    
    def run(self):
        """Main execution loop with three-state evaluation"""
        
        self.log("INFO", "Ralph Hour Gate v2.0 starting", {
            "config": str(self.config_path),
            "max_hours": self.max_hours,
            "three_state_mode": True,
            "audit_trail": True
        })
        
        hour = 1
        
        while hour <= self.max_hours:
            self.log("INFO", f"=== Hour {hour} of max {self.max_hours} ===")
            
            # Execute batch
            batch_result = self.run_batch(hour)
            
            if not batch_result["success"]:
                self.log("ERROR", f"Hour-{hour} execution failed", batch_result)
                self.write_negative_decision(
                    hour, "FAIL", None, 
                    batch_result.get("audit", {}),
                    {"reason": "EXECUTION_FAILURE", "error": batch_result.get("error")}
                )
                return False
            
            # Read metrics
            metrics = self.read_metrics(hour)
            
            if metrics is None:
                self.write_negative_decision(
                    hour, "FAIL", None,
                    batch_result.get("audit", {}),
                    {"reason": "METRICS_UNAVAILABLE"}
                )
                return False
            
            # Three-state evaluation
            verdict, details = self.evaluate_three_state(metrics)
            
            if verdict == "POSITIVE_AUTO":
                self.hour_budget += 1
                self.log("INFO", f"POSITIVE_AUTO: Strict thresholds met - AUTO CONTINUING", details)
                
                # Generate next hour config and AUTO-CONTINUE (sleep mode)
                decision_path, config_path = self.write_positive_decision(
                    hour, metrics, batch_result.get("audit", {}), details
                )
                
                # Check if auto_continue is enabled
                if self.config.get("auto_continue", False):
                    self.log("INFO", f"Auto-continue enabled - proceeding to Hour {hour + 1}", {
                        "sleep_mode": self.config.get("sleep_mode", {}).get("enabled", False),
                        "note": "Running continuously while user sleeps"
                    })
                    hour += 1
                    continue  # Continue to next hour without stopping
                else:
                    self.log("INFO", "Auto-continue disabled - stopping for external approval", {
                        "next_config": str(config_path),
                        "decision": str(decision_path)
                    })
                    return {
                        "status": "POSITIVE_AUTO",
                        "verdict": "POSITIVE_AUTO",
                        "hours_completed": hour,
                        "next_hour_available": hour + 1,
                        "next_config": str(config_path),
                        "decision": str(decision_path),
                        "auto_continue": False
                    }
                
            elif verdict == "POSITIVE_MANUAL":
                self.hour_budget += 1
                self.log("INFO", f"POSITIVE_MANUAL: Standard thresholds met - awaiting approval", details)
                
                # Generate next hour config but STOP for manual approval
                decision_path, config_path = self.write_positive_decision(
                    hour, metrics, batch_result.get("audit", {}), details
                )
                
                self.log("INFO", "Stopping for external approval", {
                    "next_config": str(config_path),
                    "decision": str(decision_path)
                })
                
                return {
                    "status": "POSITIVE_MANUAL",
                    "verdict": "POSITIVE_MANUAL",
                    "hours_completed": hour,
                    "next_hour_available": hour + 1,
                    "next_config": str(config_path),
                    "decision": str(decision_path)
                }
                
            elif verdict == "MARGINAL":
                self.log("WARN", f"MARGINAL FEEDBACK: Partial progress, freezing for analysis", details)
                
                decision_path = self.write_negative_decision(
                    hour, "MARGINAL", metrics,
                    batch_result.get("audit", {}), details
                )
                
                return {
                    "status": "MARGINAL_FEEDBACK",
                    "verdict": "MARGINAL",
                    "hours_completed": hour,
                    "decision": str(decision_path),
                    "recommendation": "ANALYZE"
                }
                
            else:  # FAIL
                self.log("ERROR", f"FAIL FEEDBACK: Clear failure, freezing", details)
                
                decision_path = self.write_negative_decision(
                    hour, "FAIL", metrics,
                    batch_result.get("audit", {}), details
                )
                
                return {
                    "status": "FAIL_FEEDBACK",
                    "verdict": "FAIL",
                    "hours_completed": hour,
                    "decision": str(decision_path),
                    "recommendation": "ROLLBACK"
                }
            
            hour += 1
        
        self.log("INFO", f"Reached max hours ({self.max_hours})")
        return True

def main():
    parser = argparse.ArgumentParser(description="Ralph Hour Gate v2.0 for Atlas-HEC")
    parser.add_argument("--config", required=True, help="Gate configuration JSON")
    parser.add_argument("--output-dir", default="ralph_runs", help="Output directory")
    
    args = parser.parse_args()
    
    gate = RalphHourGate(args.config)
    result = gate.run()
    
    print("\n" + "="*70)
    print("RALPH HOUR GATE v2.0 COMPLETE")
    print("="*70)
    
    if result == True:
        print("Status: All hours completed successfully")
    elif result == False:
        print("Status: STOPPED (execution failure)")
        sys.exit(1)
    else:
        print(f"Status: {result.get('status')}")
        print(f"Verdict: {result.get('verdict')}")
        print(f"Hours completed: {result.get('hours_completed')}")
        print(f"Decision file: {result.get('decision')}")
        if result.get('next_config'):
            print(f"Next config: {result.get('next_config')}")
        if result.get('recommendation'):
            print(f"Recommendation: {result.get('recommendation')}")
    
    # Exit codes: 0 = positive, 1 = marginal/fail, 2 = error
    if isinstance(result, dict):
        if result.get('verdict') in ['MARGINAL', 'FAIL']:
            sys.exit(1)

if __name__ == "__main__":
    main()
