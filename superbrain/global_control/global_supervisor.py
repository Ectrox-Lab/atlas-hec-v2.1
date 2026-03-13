#!/usr/bin/env python3
"""
Global Supervisor - Tri-Loop Coordination

Responsibility: Ensure Mainline, Fast Genesis, Bridge, Akashic operate without cross-contamination
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class GlobalSupervisor:
    """Top-level coordination of all Superbrain modules"""
    
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
            
        self.modules = {
            "mainline": {"status": "STOPPED", "process": None},
            "fast_genesis": {"status": "STOPPED", "process": None},
            "bridge": {"status": "STOPPED", "process": None},
            "akashic": {"status": "STOPPED", "process": None}
        }
        
        self.isolation_rules = {
            "mainline_no_direct_adoption": True,
            "fast_genesis_no_mainline_injection": True,
            "akashic_readonly_for_policy": True
        }
        
        self.system_stats = {
            "start_time": None,
            "cycles_completed": 0,
            "policy_violations": 0,
            "candidates_generated": 0,
            "candidates_queued": 0
        }
        
    def start_all_modules(self):
        """Launch all Superbrain modules"""
        print("[SUPERVISOR] Starting FULL-STACK SUPERBRAIN MODE")
        print("=" * 60)
        
        # Start Akashic first (knowledge base)
        self._start_module("akashic", 
            "/home/admin/atlas-hec-v2.1-repo/superbrain/akashic/akashic_synthesizer.py")
            
        # Start Bridge (funnel)
        self._start_module("bridge",
            "/home/admin/atlas-hec-v2.1-repo/superbrain/bridge/bridge_scheduler.py")
            
        # Start Fast Genesis (fast evolution)
        self._start_module("fast_genesis",
            "/home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/fast_genesis_orchestrator.py")
            
        # Start Mainline (slow verification)
        self._start_module("mainline",
            "/home/admin/atlas-hec-v2.1-repo/superbrain/mainline/mainline_orchestrator.py")
            
        self.system_stats["start_time"] = datetime.now()
        print("=" * 60)
        print("[SUPERVISOR] All modules started")
        
    def _start_module(self, name: str, script_path: str):
        """Start individual module"""
        print(f"[SUPERVISOR] Starting {name}...")
        
        # In real implementation, this would spawn processes
        # For now, mark as started
        self.modules[name]["status"] = "RUNNING"
        self.modules[name]["started_at"] = datetime.now().isoformat()
        
        print(f"[SUPERVISOR] {name}: RUNNING")
        
    def check_isolation(self) -> bool:
        """Verify isolation rules are not violated"""
        violations = []
        
        # Check 1: Mainline only adopts from Bridge queue
        mainline_direct = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/mainline/direct_injections")
        if mainline_direct.exists() and any(mainline_direct.iterdir()):
            violations.append("MAINLINE_DIRECT_INJECTION_VIOLATION")
            
        # Check 2: Fast Genesis doesn't inject to Mainline
        fg_injection = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/mainline/from_fast_genesis")
        if fg_injection.exists() and any(fg_injection.iterdir()):
            violations.append("FAST_GENESIS_MAINLINE_INJECTION_VIOLATION")
            
        # Check 3: Akashic doesn't override policy directly
        akashic_override = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/policy_overrides")
        if akashic_override.exists() and any(akashic_override.iterdir()):
            violations.append("AKASHIC_POLICY_OVERRIDE_VIOLATION")
            
        if violations:
            self.system_stats["policy_violations"] += len(violations)
            print(f"[SUPERVISOR] ISOLATION VIOLATIONS: {violations}")
            return False
            
        return True
        
    def monitor_health(self) -> Dict:
        """Check health of all modules"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "system": self.system_stats.copy()
        }
        
        for name, info in self.modules.items():
            health["modules"][name] = {
                "status": info["status"],
                "started_at": info.get("started_at"),
                "uptime_seconds": self._calculate_uptime(info.get("started_at"))
            }
            
        # Check data flow
        health["data_flow"] = {
            "fast_genesis_to_bridge": self._check_flow("bridge/incoming"),
            "bridge_to_mainline": self._check_flow("bridge/to_mainline"),
            "mainline_to_akashic": self._check_flow("akashic/inputs/mainline"),
            "akashic_to_fast_genesis": self._check_flow("candidate_generation/phase4/inheritance")
        }
        
        return health
        
    def _calculate_uptime(self, started_at: str) -> int:
        """Calculate module uptime in seconds"""
        if not started_at:
            return 0
        start = datetime.fromisoformat(started_at)
        return int((datetime.now() - start).total_seconds())
        
    def _check_flow(self, path_str: str) -> str:
        """Check if data is flowing through path"""
        path = Path(f"/home/admin/atlas-hec-v2.1-repo/superbrain/{path_str}")
        if not path.exists():
            return "NOT_INITIALIZED"
        files = list(path.glob("*.json"))
        if not files:
            return "EMPTY"
        # Check if any file is recent (< 1 hour)
        recent = any((datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).seconds < 3600 
                     for f in files)
        return "FLOWING" if recent else "STALE"
        
    def display_dashboard(self):
        """Print system status dashboard"""
        print("\n" + "=" * 70)
        print(" FULL-STACK SUPERBRAIN DASHBOARD")
        print("=" * 70)
        
        health = self.monitor_health()
        
        # Module status
        print("\n[MODULES]")
        for name, info in health["modules"].items():
            status_icon = "✅" if info["status"] == "RUNNING" else "❌"
            uptime_mins = info["uptime_seconds"] // 60
            print(f"  {status_icon} {name:20s} {info['status']:10s} ({uptime_mins}m)")
            
        # Data flow
        print("\n[DATA FLOW]")
        for flow, status in health["data_flow"].items():
            icon = {"FLOWING": "✅", "EMPTY": "⚠️", "STALE": "⏸️", "NOT_INITIALIZED": "❌"}.get(status, "?")
            print(f"  {icon} {flow:40s} {status}")
            
        # System stats
        print("\n[SYSTEM STATS]")
        stats = health["system"]
        if stats["start_time"]:
            elapsed = (datetime.now() - datetime.fromisoformat(stats["start_time"])).total_seconds()
            print(f"  Runtime: {elapsed/3600:.1f} hours")
        print(f"  Cycles: {stats['cycles_completed']}")
        print(f"  Policy violations: {stats['policy_violations']}")
        
        # Isolation status
        print("\n[ISOLATION]")
        isolated = self.check_isolation()
        print(f"  {'✅' if isolated else '❌'} Cross-contamination check: {'PASS' if isolated else 'VIOLATION'}")
        
        print("=" * 70)
        
    def run_supervision_cycle(self):
        """One supervision cycle"""
        # Check isolation
        if not self.check_isolation():
            print("[SUPERVISOR] CRITICAL: Isolation violation detected!")
            # In production, would trigger alerts/self-healing
            
        # Update stats
        self.system_stats["cycles_completed"] += 1
        
        # Display dashboard
        self.display_dashboard()
        
    def run_continuous(self):
        """Main supervision loop"""
        print("[SUPERVISOR] Starting continuous supervision...")
        
        self.start_all_modules()
        
        try:
            while True:
                self.run_supervision_cycle()
                time.sleep(60)  # 1 minute supervision cycles
        except KeyboardInterrupt:
            print("\n[SUPERVISOR] Shutting down...")
            self._shutdown_all()
            
    def _shutdown_all(self):
        """Graceful shutdown"""
        for name in self.modules:
            self.modules[name]["status"] = "STOPPED"
            print(f"[SUPERVISOR] {name}: STOPPED")
            
    def emergency_stop(self, reason: str):
        """Emergency halt of all modules"""
        print(f"[SUPERVISOR] EMERGENCY STOP: {reason}")
        self._shutdown_all()


if __name__ == "__main__":
    supervisor = GlobalSupervisor(
        "/home/admin/atlas-hec-v2.1-repo/superbrain/global_control/superbrain_config.json"
    )
    supervisor.run_continuous()
