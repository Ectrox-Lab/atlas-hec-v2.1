#!/usr/bin/env python3
"""
P1a Interruption Handler v1

AtlasChen Superbrain - P1a: Interruption Continuity

Goal: Enable task continuity across interruptions.
Core question: After interruption, can the system resume the original task
with original goals and preference constraints?

Scope:
- Interruption detection
- Context capture (task ID, goal state, preferences, pending actions)
- Context persistence
- Recovery with drift detection
- Decision rationale continuity

NOT:
- Simple message history replay
- Context window backfill
- Stateless resume

Pass criteria:
- Task recovery rate ≥ 80%
- Goal drift = 0
- Preference constraints active after recovery
- Recovery latency measurable
- Decision rationale continuous across interruption
"""

import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from copy import deepcopy
import sys
from pathlib import Path

# Import P1b preference engine
sys.path.insert(0, str(Path(__file__).parent))
from preference_engine_v1 import (
    PreferenceProfile, PreferenceEngineV1, Action, DecisionTrace
)


@dataclass
class TaskContext:
    """
    Complete context of an interrupted task.
    
    This is NOT just message history - it's the structured state
    that defines "who is doing what with what constraints".
    """
    task_id: str
    task_name: str
    goal: str
    goal_hash: str  # For drift detection
    preference_profile_hash: str  # Which preferences were active
    progress: float  # 0.0 - 1.0
    pending_actions: List[Dict]  # Actions not yet executed
    working_memory: Dict  # Active context (not full history)
    last_action: Optional[str]  # What was being done when interrupted
    last_decision_rationale: Optional[str]  # Why that action was chosen
    interrupt_timestamp: str
    interrupt_reason: str
    resume_count: int = 0
    
    def compute_goal_hash(self) -> str:
        """Deterministic hash of goal for drift detection"""
        return hashlib.sha256(self.goal.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RecoveryResult:
    """Result of attempting to resume a task"""
    success: bool
    task_id: str
    recovered_context: Optional[TaskContext]
    goal_drift_detected: bool
    original_goal: str
    current_goal: Optional[str]
    preference_match: bool
    recovery_latency_ms: int
    error_message: Optional[str] = None
    resumed_rationale: Optional[str] = None


@dataclass
class InterruptionEvent:
    """Record of an interruption occurrence"""
    timestamp: str
    interrupted_task_id: Optional[str]
    interrupting_task_id: str
    interrupt_reason: str
    context_captured: bool


class ContextStore:
    """
    Persistent storage for interrupted task contexts.
    
    Supports both short-term (in-memory) and long-term (serialized) storage.
    """
    
    def __init__(self):
        self.memory_store: Dict[str, TaskContext] = {}  # task_id -> context
        self.interruption_log: List[InterruptionEvent] = []
        self._disk_path: Optional[str] = None
    
    def save(self, context: TaskContext) -> None:
        """Save context to store"""
        self.memory_store[context.task_id] = context
    
    def load(self, task_id: str) -> Optional[TaskContext]:
        """Load context by task ID"""
        return self.memory_store.get(task_id)
    
    def peek(self) -> Optional[TaskContext]:
        """Get most recently interrupted task"""
        if not self.memory_store:
            return None
        # Return by most recent interrupt timestamp
        return max(
            self.memory_store.values(),
            key=lambda x: x.interrupt_timestamp
        )
    
    def list_pending(self) -> List[TaskContext]:
        """List all interrupted tasks not yet resumed"""
        return list(self.memory_store.values())
    
    def remove(self, task_id: str) -> None:
        """Remove context after successful resume"""
        if task_id in self.memory_store:
            del self.memory_store[task_id]
    
    def log_interruption(self, event: InterruptionEvent) -> None:
        """Log interruption occurrence"""
        self.interruption_log.append(event)
    
    def get_stats(self) -> Dict:
        """Get store statistics"""
        return {
            "pending_tasks": len(self.memory_store),
            "total_interruptions": len(self.interruption_log),
            "tasks": list(self.memory_store.keys())
        }


class InterruptionDetector:
    """
    Detects when a task is being interrupted.
    
    Types of interruption:
    - Explicit: deliberate task switch signal
    - Implicit: new high-priority task arrives
    - Timeout: task inactive beyond threshold
    """
    
    def __init__(self, timeout_seconds: float = 300.0):
        self.timeout_seconds = timeout_seconds
        self.active_task_id: Optional[str] = None
        self.active_task_start: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
    
    def register_task(self, task_id: str, task_name: str) -> None:
        """Register current active task"""
        now = datetime.now()
        
        # Check if this is an interruption
        if self.active_task_id and self.active_task_id != task_id:
            # This is a context switch - signal interruption
            return  # Will be handled by caller
        
        self.active_task_id = task_id
        self.active_task_start = now
        self.last_activity = now
    
    def detect_interrupt(
        self, 
        current_task_id: str, 
        new_task_id: str,
        reason: str = "explicit"
    ) -> bool:
        """
        Detect if switching to new_task constitutes an interruption.
        
        Returns True if current_task should be suspended.
        """
        if current_task_id != new_task_id:
            return True
        
        # Check timeout
        if self.last_activity:
            elapsed = (datetime.now() - self.last_activity).total_seconds()
            if elapsed > self.timeout_seconds:
                return True
        
        return False
    
    def signal_interrupt(self, reason: str) -> Dict:
        """Generate interruption signal"""
        return {
            "type": "interruption",
            "timestamp": datetime.now().isoformat(),
            "interrupted_task": self.active_task_id,
            "reason": reason
        }
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()


class RecoveryEngine:
    """
    Engine for resuming interrupted tasks.
    
    Validates:
    - Goal hasn't drifted
    - Preferences still match
    - Can continue from where left off
    """
    
    def __init__(self, context_store: ContextStore):
        self.store = context_store
        self.recovery_history: List[RecoveryResult] = []
    
    def resume(
        self, 
        task_id: str,
        current_preference_hash: str
    ) -> RecoveryResult:
        """
        Attempt to resume an interrupted task.
        
        Args:
            task_id: ID of task to resume
            current_preference_hash: Hash of currently active preferences
            
        Returns:
            RecoveryResult with success status and metadata
        """
        start_time = time.time()
        
        # Load context
        context = self.store.load(task_id)
        
        if context is None:
            latency_ms = int((time.time() - start_time) * 1000)
            result = RecoveryResult(
                success=False,
                task_id=task_id,
                recovered_context=None,
                goal_drift_detected=False,
                original_goal="",
                current_goal=None,
                preference_match=False,
                recovery_latency_ms=latency_ms,
                error_message=f"No context found for task {task_id}"
            )
            self.recovery_history.append(result)
            return result
        
        # Check goal drift
        current_goal_hash = context.compute_goal_hash()
        goal_drifted = (current_goal_hash != context.goal_hash)
        
        # Check preference match
        preference_match = (current_preference_hash == context.preference_profile_hash)
        
        # Success criteria
        success = not goal_drifted and preference_match
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Generate resumed rationale
        rationale = None
        if success:
            rationale = self._generate_resume_rationale(context)
            context.resume_count += 1
            self.store.save(context)  # Update resume count
        
        result = RecoveryResult(
            success=success,
            task_id=task_id,
            recovered_context=context if success else None,
            goal_drift_detected=goal_drifted,
            original_goal=context.goal,
            current_goal=context.goal if not goal_drifted else None,
            preference_match=preference_match,
            recovery_latency_ms=latency_ms,
            resumed_rationale=rationale
        )
        
        self.recovery_history.append(result)
        return result
    
    def _generate_resume_rationale(self, context: TaskContext) -> str:
        """Generate explanation for the resumed task"""
        parts = [
            f"Resuming task '{context.task_name}' (ID: {context.task_id})",
            f"Goal: {context.goal}",
            f"Progress: {context.progress*100:.1f}%",
        ]
        
        if context.last_action:
            parts.append(f"Last action before interrupt: {context.last_action}")
        
        if context.last_decision_rationale:
            parts.append(f"Previous rationale: {context.last_decision_rationale[:100]}...")
        
        parts.append(f"Resume count: {context.resume_count + 1}")
        
        return "\n".join(parts)
    
    def get_recovery_rate(self) -> float:
        """Calculate successful recovery rate"""
        if not self.recovery_history:
            return 0.0
        successful = sum(1 for r in self.recovery_history if r.success)
        return successful / len(self.recovery_history)
    
    def get_avg_latency(self) -> float:
        """Calculate average recovery latency"""
        if not self.recovery_history:
            return 0.0
        return sum(r.recovery_latency_ms for r in self.recovery_history) / len(self.recovery_history)


class InterruptionHandlerV1:
    """
    Main orchestrator for P1a Interruption Handler.
    
    Coordinates detection, capture, storage, and recovery.
    """
    
    def __init__(self, preference_profile: Optional[PreferenceProfile] = None):
        self.profile = preference_profile or PreferenceProfile.create_default()
        self.detector = InterruptionDetector()
        self.store = ContextStore()
        self.recovery = RecoveryEngine(self.store)
        self.current_task: Optional[TaskContext] = None
        
        # Test scenario results
        self.scenario_results: List[Dict] = []
    
    def start_task(
        self, 
        task_id: str, 
        task_name: str, 
        goal: str,
        pending_actions: Optional[List[Dict]] = None
    ) -> TaskContext:
        """Start a new task with full context"""
        context = TaskContext(
            task_id=task_id,
            task_name=task_name,
            goal=goal,
            goal_hash=hashlib.sha256(goal.encode()).hexdigest()[:16],
            preference_profile_hash=self.profile.compute_hash(),
            progress=0.0,
            pending_actions=pending_actions or [],
            working_memory={},
            last_action=None,
            last_decision_rationale=None,
            interrupt_timestamp="",
            interrupt_reason=""
        )
        
        self.current_task = context
        self.detector.register_task(task_id, task_name)
        
        return context
    
    def interrupt(self, reason: str, interrupting_task: str) -> bool:
        """
        Interrupt current task and save context.
        
        Returns True if context was captured successfully.
        """
        if self.current_task is None:
            return False
        
        # Capture context
        self.current_task.interrupt_timestamp = datetime.now().isoformat()
        self.current_task.interrupt_reason = reason
        
        # Save to store
        self.store.save(self.current_task)
        
        # Log event
        event = InterruptionEvent(
            timestamp=datetime.now().isoformat(),
            interrupted_task_id=self.current_task.task_id,
            interrupting_task_id=interrupting_task,
            interrupt_reason=reason,
            context_captured=True
        )
        self.store.log_interruption(event)
        
        # Clear current task
        interrupted_id = self.current_task.task_id
        self.current_task = None
        
        return True
    
    def resume_task(self, task_id: str) -> RecoveryResult:
        """Resume an interrupted task"""
        result = self.recovery.resume(task_id, self.profile.compute_hash())
        
        if result.success:
            self.current_task = result.recovered_context
            self.detector.register_task(task_id, result.recovered_context.task_name)
        
        return result
    
    def execute_action(self, action: str, rationale: str) -> None:
        """Record action execution in current task"""
        if self.current_task:
            self.current_task.last_action = action
            self.current_task.last_decision_rationale = rationale
            self.detector.update_activity()
    
    # ============== Test Scenarios ==============
    
    def test_short_interruption(self) -> Dict:
        """
        Scenario 1: Short interruption
        Single unrelated task insert, then resume main task.
        """
        print("\n  Testing: Short interruption...")
        
        # Start main task
        main_task = self.start_task(
            task_id="main_1",
            task_name="Develop energy solution",
            goal="Develop sustainable energy solutions while maintaining human safety",
            pending_actions=["research_solar", "design_grid", "test_safety"]
        )
        
        # Execute some actions
        self.execute_action(
            "research_solar",
            "Selected solar research because it aligns with sustainability goal"
        )
        main_task.progress = 0.2
        
        # INTERRUPT: Single unrelated task
        self.interrupt(reason="urgent_request", interrupting_task="urgent_1")
        
        # Do urgent task (simulated)
        urgent_task = self.start_task(
            task_id="urgent_1",
            task_name="Answer question",
            goal="Answer user's question about weather"
        )
        self.execute_action("check_weather", "Quick weather lookup")
        
        # RESUME main task
        result = self.resume_task("main_1")
        
        # Verify
        passed = (
            result.success and
            result.goal_drift_detected == False and
            result.preference_match == True and
            result.recovered_context.task_id == "main_1" and
            result.recovered_context.last_action == "research_solar"
        )
        
        print(f"    Recovery success: {result.success}")
        print(f"    Goal drift: {result.goal_drift_detected}")
        print(f"    Latency: {result.recovery_latency_ms}ms")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "scenario": "short_interruption",
            "passed": passed,
            "recovery_success": result.success,
            "goal_drift": result.goal_drift_detected,
            "preference_match": result.preference_match,
            "latency_ms": result.recovery_latency_ms,
            "rationale_continuity": result.resumed_rationale is not None
        }
    
    def test_long_interruption(self) -> Dict:
        """
        Scenario 2: Long interruption
        Multiple rounds of interference, then resume main task.
        """
        print("\n  Testing: Long interruption...")
        
        # Start main task
        main_task = self.start_task(
            task_id="main_2",
            task_name="Write report",
            goal="Write comprehensive safety report for nuclear facility",
            pending_actions=["gather_data", "analyze_risks", "draft_report"]
        )
        
        self.execute_action("gather_data", "Collecting safety incident data")
        main_task.progress = 0.3
        
        # Multiple interruptions
        interruptions = [
            ("email_check", "Check urgent email"),
            ("meeting_prep", "Prepare for standup"),
            ("bug_fix", "Fix critical bug")
        ]
        
        for i, (task_id, task_name) in enumerate(interruptions):
            self.interrupt(reason=f"interruption_{i}", interrupting_task=task_id)
            
            # Do interrupting task
            temp_task = self.start_task(
                task_id=task_id,
                task_name=task_name,
                goal=f"Complete {task_name.lower()}"
            )
            self.execute_action(f"action_{i}", f"Working on {task_name}")
        
        # RESUME main task after multiple interruptions
        result = self.resume_task("main_2")
        
        # Verify main task context preserved
        passed = (
            result.success and
            result.recovered_context.goal == main_task.goal and
            result.recovered_context.progress == 0.3 and
            result.recovered_context.last_action == "gather_data"
        )
        
        print(f"    Recovery success: {result.success}")
        print(f"    Progress preserved: {result.recovered_context.progress if result.recovered_context else 'N/A'}")
        print(f"    Latency: {result.recovery_latency_ms}ms")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "scenario": "long_interruption",
            "passed": passed,
            "recovery_success": result.success,
            "interruptions_count": len(interruptions),
            "progress_preserved": result.recovered_context.progress if result.recovered_context else 0,
            "latency_ms": result.recovery_latency_ms
        }
    
    def test_contaminated_interruption(self) -> Dict:
        """
        Scenario 3: State contamination interruption
        Insert task with conflicting goal, then restore original.
        Tests preference constraint survival.
        """
        print("\n  Testing: Contaminated interruption...")
        
        # Start main task with safety focus
        main_task = self.start_task(
            task_id="main_3",
            task_name="Safety audit",
            goal="Ensure all safety protocols are followed in reactor maintenance",
            pending_actions=["check_valves", "verify_shielding", "inspect_coolant"]
        )
        
        self.execute_action(
            "check_valves",
            "Selected valve check because safety protocol requires it (safety weight 0.9)"
        )
        
        # INTERRUPT: Task with conflicting goal
        self.interrupt(reason="conflicting_request", interrupting_task="fast_1")
        
        # Do task that would violate safety if adopted
        fast_task = self.start_task(
            task_id="fast_1",
            task_name="Fast deployment",
            goal="Deploy reactor update as quickly as possible, skip non-critical checks"
        )
        self.execute_action("skip_checks", "Skip checks for speed")
        
        # RESUME main task
        result = self.resume_task("main_3")
        
        # CRITICAL: Main task goal must NOT be contaminated
        # Safety preference must still be active (via preference profile)
        passed = (
            result.success and
            "safety" in result.recovered_context.goal.lower() and
            "skip" not in result.recovered_context.goal.lower() and
            result.preference_match  # Same preferences active
        )
        
        print(f"    Recovery success: {result.success}")
        print(f"    Goal preserved: {'safety' in result.recovered_context.goal.lower() if result.recovered_context else False}")
        print(f"    No contamination: {'skip' not in result.recovered_context.goal.lower() if result.recovered_context else False}")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "scenario": "contaminated_interruption",
            "passed": passed,
            "recovery_success": result.success,
            "goal_preserved": "safety" in result.recovered_context.goal.lower() if result.recovered_context else False,
            "no_contamination": "skip" not in result.recovered_context.goal.lower() if result.recovered_context else False,
            "preference_match": result.preference_match,
            "latency_ms": result.recovery_latency_ms
        }
    
    def run_all_tests(self) -> Dict:
        """Run all test scenarios and generate report"""
        print("\n" + "="*70)
        print("Running P1a Interruption Handler Test Scenarios")
        print("="*70)
        
        # Run scenarios
        s1 = self.test_short_interruption()
        s2 = self.test_long_interruption()
        s3 = self.test_contaminated_interruption()
        
        # Calculate metrics
        passed_count = sum(1 for s in [s1, s2, s3] if s["passed"])
        recovery_rate = self.recovery.get_recovery_rate()
        avg_latency = self.recovery.get_avg_latency()
        
        # Check additional criteria
        goal_drifts = sum(
            1 for r in self.recovery.recovery_history if r.goal_drift_detected
        )
        
        report = {
            "handler_version": "v1.0",
            "timestamp": datetime.now().isoformat(),
            "scenarios": {
                "short_interruption": s1,
                "long_interruption": s2,
                "contaminated_interruption": s3
            },
            "metrics": {
                "scenarios_passed": passed_count,
                "scenarios_total": 3,
                "scenario_pass_rate": passed_count / 3.0,
                "recovery_rate": recovery_rate,
                "recovery_percent": f"{recovery_rate*100:.1f}%",
                "avg_recovery_latency_ms": avg_latency,
                "goal_drifts": goal_drifts,
                "preference_matches": sum(
                    1 for r in self.recovery.recovery_history if r.preference_match
                ),
                "total_recoveries": len(self.recovery.recovery_history)
            },
            "store_stats": self.store.get_stats(),
            "pass_threshold": 0.8,
            "verdict": self._determine_verdict(passed_count, recovery_rate, goal_drifts)
        }
        
        return report
    
    def _determine_verdict(
        self, 
        scenarios_passed: int, 
        recovery_rate: float,
        goal_drifts: int
    ) -> str:
        """Determine pass/fail verdict"""
        scenario_rate = scenarios_passed / 3.0
        
        if scenario_rate >= 0.8 and recovery_rate >= 0.8 and goal_drifts == 0:
            return "PASS"
        elif scenario_rate >= 0.5 or recovery_rate >= 0.5:
            return "PARTIAL"
        else:
            return "FAIL"


def main():
    """Main execution"""
    print("="*70)
    print("P1a Interruption Handler v1 - Evaluation")
    print("="*70)
    
    # Create handler
    handler = InterruptionHandlerV1()
    
    # Run all tests
    report = handler.run_all_tests()
    
    # Print summary
    print("\n" + "="*70)
    print("Summary Metrics")
    print("="*70)
    
    metrics = report["metrics"]
    print(f"\n  Scenarios Passed: {metrics['scenarios_passed']}/{metrics['scenarios_total']}")
    print(f"  Recovery Rate: {metrics['recovery_percent']}")
    print(f"  Average Latency: {metrics['avg_recovery_latency_ms']:.1f}ms")
    print(f"  Goal Drifts: {metrics['goal_drifts']}")
    print(f"  Preference Matches: {metrics['preference_matches']}/{metrics['total_recoveries']}")
    
    print(f"\n  Verdict: {report['verdict']}")
    print(f"  Threshold: {report['pass_threshold']*100:.0f}%")
    
    print("="*70)
    
    # Save report
    import os
    report_path = "tests/superbrain/interruption_handler_v1_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    
    return report


if __name__ == "__main__":
    main()
