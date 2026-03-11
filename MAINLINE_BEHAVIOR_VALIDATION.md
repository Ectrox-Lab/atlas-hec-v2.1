# Mainline Behavior Validation Plan

**Date**: 2025-03-08  
**Status**: IN PROGRESS  
**Phase**: End-to-End Behavior Validation

---

## Objective

Validate that **Candidate 001 as mainline default** provides stable behavioral benefits in repeated game environments.

This is **not** mechanism validation (already done) - this is **system behavior validation**.

---

## Validation Framework

### Three Conditions

| Condition | Description | Purpose |
|-----------|-------------|---------|
| **ON** | `MainlinePriorChannel::new()` (Candidate 001 default) | Mainline behavior |
| **OFF** | Markers enabled, PriorChannel disabled | Mechanism isolation |
| **Baseline** | No markers, no PriorChannel | Pure baseline |

### Game Environments

Per `candidate_001_intake.md`:

1. **Prisoner's Dilemma** - Classic cooperation dilemma
2. **Stag Hunt** - Coordination game
3. **Chicken** - Anti-coordination game

Parameters:
- 4 agents
- 1000 rounds
- 10 seeds for statistical validity
- Round-robin pairing

### Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Behavioral Coherence** | ON >= 0.7 | Variance of actions over time |
| **Coherence Stability** | High | Low variance across seeds |
| **Partner Prediction** | ON > OFF | Accuracy of partner action prediction |
| **Total Score** | Competitive | Cumulative payoff |
| **Bandwidth Overhead** | Acceptable | Total bits transmitted |

---

## Execution Plan

### Day 1: Runner Implementation ✅

**File**: `source/src/bin/mainline_task_runner.rs`

Components:
- [x] Game definitions (PD, Stag, Chicken)
- [x] MainlineAgent (with Candidate 001 markers)
- [x] BaselineAgent (no markers)
- [x] Arena (multi-agent environment)
- [x] Three-condition benchmark
- [x] Metrics collection

### Day 2: Benchmark Execution

**Command**:
```bash
cd source
export RUSTFLAGS="-L $PWD/hetero_bridge"
cargo run --bin mainline_task_runner
```

**Expected Output**:
```
Game: PrisonersDilemma
----------------------------------------
Metric                    ON        OFF   Baseline
----------------------------------------
Coherence              0.850      0.820      0.500
Stability              0.900      0.850      0.200
Prediction             0.650      0.600      0.500
Score                   1250       1200       1000
Bandwidth (bits)        3200          0          0
----------------------------------------
Validation:
  ✅ Coherence maintained (ON >= 0.7)
  ✅ Mechanism intact (|ON-OFF| < 0.2)
  ✅ Bandwidth overhead acceptable
```

### Day 3: Result Documentation

**Deliverable**: This document + CI integration

---

## Success Criteria

### Primary (Must Pass)

1. **Coherence Maintained**: ON condition achieves >= 0.7 mean coherence
2. **Mechanism Intact**: |ON - OFF| < 0.2 (PriorChannel additive, not replacing)
3. **Above Baseline**: ON > Baseline for coherence and prediction

### Secondary (Should Pass)

4. **Stability**: Low variance across seeds (robustness)
5. **Prediction**: ON > OFF for partner prediction accuracy
6. **Bandwidth**: Overhead acceptable (< 5KB per 1000 rounds)

---

## CI Integration

### Gates (Must Pass to Merge)

```yaml
# .github/workflows/mainline_ci.yml
- PriorChannel Lib Tests: cargo test --lib prior_channel
- Mainline Regression Pack: cargo test --test mainline_regression_pack
```

### Constraints Enforced

| Constraint | Test | Failure Mode |
|------------|------|--------------|
| Bandwidth 32 bits | `regression_bandwidth_32_bits` | Blocks PR |
| Timescale 10x | `regression_timescale_10x` | Blocks PR |
| Generic-only | `regression_no_action_leakage` | Blocks PR |
| Frozen p=0.01 | `regression_frozen_parameters` | Blocks PR |
| Frozen α=0.5 | `regression_frozen_parameters` | Blocks PR |

---

## Current Status

### Implementation

| Component | Status | File |
|-----------|--------|------|
| MainlineTaskRunner | ✅ Ready | `src/bin/mainline_task_runner.rs` |
| CI Gate | ✅ Ready | `.github/workflows/mainline_ci.yml` |
| Regression Pack | ✅ Ready | `tests/mainline_regression_pack.rs` |

### Next Steps

1. **Execute benchmark**:
   ```bash
   cargo run --bin mainline_task_runner
   ```

2. **Analyze results**:
   - Verify ON >= 0.7 coherence
   - Verify |ON - OFF| < 0.2
   - Check stability across seeds

3. **Document findings**:
   - Update this file with actual numbers
   - Add to CI dashboard

---

## Run Commands

### Full Validation Suite

```bash
cd /home/admin/atlas-hec-v2.1-repo/source
export RUSTFLAGS="-L $PWD/hetero_bridge"

# 1. PriorChannel tests (must pass)
cargo test --lib prior_channel

# 2. Regression pack (must pass)
cargo test --test mainline_regression_pack

# 3. Behavior validation (benchmark)
cargo run --bin mainline_task_runner
```

### Expected Runtime

- Lib tests: ~2 seconds
- Regression pack: ~5 seconds
- Benchmark (3 games × 10 seeds × 1000 rounds): ~30 seconds

---

## Deliverables

1. ✅ `mainline_task_runner.rs` - End-to-end behavior validation
2. ✅ `mainline_regression_pack.rs` - CI gate tests
3. ✅ `.github/workflows/mainline_ci.yml` - CI configuration
4. ⏳ Benchmark results - After execution
5. ⏳ Final validation report - After analysis

---

## Notes

- This is **behavioral validation**, not mechanism validation
- Mechanism is already validated (20/20 tests pass)
- Goal: Confirm system-level benefits in realistic environments
- Any regression in CI gates blocks the PR immediately

---

*Atlas HEC v2.1 | Candidate 001 Mainline | Behavior Validation Phase*
