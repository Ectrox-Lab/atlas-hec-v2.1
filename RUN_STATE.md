# RUN_STATE — Single Source of Truth

**Date**: 2026-03-12 23:45 UTC  
**Git**: c7913a4  
**Rule**: No PID, no status.

---

## Allowed Status Values

- `NOT_STARTED` — No evidence of execution
- `RUNNING` — PID exists, logs updating, resources allocated
- `HALTED` — Was running, now stopped (crash, completion, or manual)

---

## Required Fields (All Experiments)

Every entry MUST have:

| Field | Required | Verification |
|-------|----------|--------------|
| `name` | Yes | Experiment identifier |
| `owner` | Yes | Person responsible |
| `launch_command` | Yes | Exact command used to start |
| `pid` | Yes | Process ID from pgrep/ps |
| `log_path` | Yes | Absolute path to primary log |
| `started_at` | Yes | ISO8601 timestamp |
| `last_heartbeat` | Yes | ISO8601 timestamp |
| `cpu_percent` | Yes | From top/ps |
| `ram_mb` | Yes | From top/ps |
| `status` | Yes | NOT_STARTED / RUNNING / HALTED |

---

## Current State

### Akashic v3 Skeleton

```yaml
name: akashic_v3_skeleton
owner: Jordan Smith
launch_command: TBD
pid: null
log_path: TBD
started_at: null
last_heartbeat: null
cpu_percent: null
ram_mb: null
status: NOT_STARTED
```

### E1 Executive Mechanisms

```yaml
name: e1_executive
owner: Jordan Smith
launch_command: TBD
pid: null
log_path: TBD
started_at: null
last_heartbeat: null
cpu_percent: null
ram_mb: null
status: NOT_STARTED
```

### G1 Long-Horizon

```yaml
name: g1_longhorizon
owner: Alex Chen
launch_command: TBD
pid: null
log_path: TBD
started_at: null
last_heartbeat: null
cpu_percent: null
ram_mb: null
status: NOT_STARTED
```

---

## Verification Commands

To verify a claim of RUNNING:

```bash
# 1. Check PID exists
ps -p <PID> -o pid,cmd,%cpu,%mem

# 2. Check log updating
ls -lh --full-time <log_path>
tail -n 30 <log_path>

# 3. Check resources
top -b -n 1 | grep <PID>
free -h

# 4. Check heartbeat
stat <heartbeat_json>
```

**All must pass** for status to be RUNNING.

---

## Update Rules

1. Only update this file after verifying with commands above
2. Never copy status from other documents
3. Never assume — always check PID
4. If PID dead → status = HALTED
5. If no PID → status = NOT_STARTED

---

## Launch Sequence (Revised)

**Order**:
1. Akashic v3 skeleton (easiest to verify)
2. E1 executive mechanisms (medium duration)
3. G1 long-horizon (longest, requires evidence chain)

**Rule**: Previous must show RUNNING with evidence before next starts.

---

**Next Action**: Launch Akashic v3 skeleton with full evidence chain.
