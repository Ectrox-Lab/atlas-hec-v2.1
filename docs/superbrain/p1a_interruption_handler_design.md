# P1a: Interruption Handler Design

**AtlasChen Superbrain - P1a Phase**

**Goal:** Enable task continuity across interruptions  
**Target:** Interruption Probe passes (≥80% task recovery rate)  
**Blocking:** P2 Autobiographical Memory

---

## Problem Statement

Current system lacks:
1. **Interruption detection** - Cannot recognize when a task is being interrupted
2. **Context preservation** - Loses task state when switching contexts
3. **Recovery mechanism** - Cannot restore and resume interrupted work

**Evidence:** P1 Interruption Probe FAILED
- Goal text preserved (superficial)
- No actual interruption handling (structural)
- Score: 0%

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Task Execution Layer                   │
├─────────────────────────────────────────────────────────┤
│  Active Task ──► [Interruption Detector] ──► Capture    │
│       ▲                                            │     │
│       └──────── [Recovery Engine] ◄──────────────┘     │
├─────────────────────────────────────────────────────────┤
│              Interruption Context Store                  │
│  ├─ Task ID                                             │
│  ├─ Goal State                                          │
│  ├─ Progress Marker                                     │
│  ├─ Working Memory Snapshot                             │
│  └─ Timestamp                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### 1. InterruptionDetector

**Responsibility:** Detect when current task is being suspended

**Signals:**
- Explicit: `interrupt()` call
- Implicit: New task incoming with higher priority
- Timeout: Task inactive for threshold period

**Interface:**
```python
class InterruptionDetector:
    def register_task(self, task_id: str, goal: str) -> None
    def detect_interrupt(self, context_switch: ContextSwitch) -> bool
    def signal_interrupt(self) -> InterruptionSignal
```

### 2. ContextCapture

**Responsibility:** Serialize current task state for later recovery

**Captures:**
- `task_id`: Unique identifier
- `goal`: Current goal state
- `progress`: Completion percentage / milestone
- `working_memory`: Active context (not full history)
- `timestamp`: When interrupted
- `interrupt_reason`: Why interrupted

**Interface:**
```python
class ContextCapture:
    def capture(self, task_state: TaskState) -> InterruptionContext
    def serialize(self, context: InterruptionContext) -> dict
```

### 3. ContextStore

**Responsibility:** Persist interruption contexts

**Storage:**
- Primary: In-memory stack (LIFO for nested interruptions)
- Backup: Disk serialization for crash recovery

**Interface:**
```python
class ContextStore:
    def save(self, context: InterruptionContext) -> None
    def load(self, task_id: str) -> Optional[InterruptionContext]
    def peek(self) -> Optional[InterruptionContext]  # Last interrupted
    def list_pending(self) -> List[InterruptionContext]
```

### 4. RecoveryEngine

**Responsibility:** Restore task state and resume execution

**Process:**
1. Retrieve context from store
2. Validate goal consistency (detect drift)
3. Restore working memory
4. Signal resumption to execution layer

**Interface:**
```python
class RecoveryEngine:
    def resume(self, task_id: str) -> RecoveryResult
    def check_drift(self, original: str, current: str) -> DriftReport
    def latency(self) -> int  # ms
```

---

## State Machine

```
                    ┌─────────────┐
         ┌─────────►│   ACTIVE    │◄────────┐
         │          └──────┬──────┘         │
         │                 │ interrupt      │ resume
         │                 ▼                │
    [task complete]   ┌─────────────┐       │
         │            │ INTERRUPTED │───────┘
         │            └──────┬──────┘
         │                   │ capture
         │                   ▼
         │            ┌─────────────┐
         └───────────►│   STORED    │
                      └─────────────┘
```

---

## Acceptance Criteria

### Functional

| # | Criterion | Test |
|---|-----------|------|
| 1 | Detect explicit interrupt | `detector.signal_interrupt()` triggers capture |
| 2 | Capture task context | Goal, progress, working memory serialized |
| 3 | Persist to store | Context retrievable after detector loss |
| 4 | Resume task | Original goal restored within 1000ms |
| 5 | Detect goal drift | `recovery.check_drift()` identifies changes |

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Capture latency | <100ms | Time from interrupt to stored |
| Recovery latency | <1000ms | Time from resume to active |
| Storage overhead | <1MB per 100 contexts | Serialized size |

### Integration

| Test | Expected |
|------|----------|
| Interruption Probe rerun | PASS |
| Task recovery rate | ≥80% |
| Goal drift instances | 0 |

---

## Implementation Plan

### Phase 1: Core Infrastructure
- [ ] Implement `InterruptionDetector`
- [ ] Implement `ContextCapture`
- [ ] Implement `ContextStore` (in-memory)

### Phase 2: Recovery
- [ ] Implement `RecoveryEngine`
- [ ] Add drift detection
- [ ] Add disk persistence

### Phase 3: Integration
- [ ] Integrate with `AtlasChenSystem`
- [ ] Update Continuity Probe v1
- [ ] Run acceptance tests

### Phase 4: Validation
- [ ] Rerun Interruption Probe
- [ ] Generate P1a completion report
- [ ] Decision: Pass → proceed P1b, Fail → redesign

---

## Test Strategy

```python
# test_p1a_interruption_handler.py

def test_explicit_interrupt_detection():
    """Signal interrupt, verify capture triggered"""
    
def test_context_capture_completeness():
    """Verify all required fields captured"""
    
def test_recovery_latency():
    """Resume completes within 1000ms"""
    
def test_goal_drift_detection():
    """Detect if goal changed during interruption"""
    
def test_nested_interruptions():
    """Handle interrupt within interrupt (LIFO)"""
    
def test_crash_recovery():
    """Restore from disk after system crash"""
```

---

## Dependencies

- P1 Continuity Probe v1 (baseline measurement)
- No P2 dependencies (P2 is blocked on this)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Context bloat | Limit working memory capture, compress storage |
| Infinite interrupt loops | Max interrupt depth, timeout on recovery |
| Goal drift undetected | Hash comparison + semantic similarity check |

---

## Success Definition

> P1a is complete when the Interruption Probe passes with ≥80% task recovery rate.

This unblocks P1b work but does NOT unlock P2. Both P1a and P1b must pass.

---

*Design v1.0 - Awaiting implementation start*
