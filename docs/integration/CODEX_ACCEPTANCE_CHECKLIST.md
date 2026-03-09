# Codex Acceptance Checklist

**Version**: v0.2.0  
**Date**: 2026-03-09  
**Purpose**: Verification checklist for Bio-World implementation

---

## Phase 1: Schema Verification

### 1.1 CSV Column Existence

Check that `population.csv` contains all required columns:

| Column | Type | Verification Method |
|--------|------|---------------------|
| tick | u32 | `head -1 population.csv` |
| population | u32 | `head -1 population.csv` |
| births | u32 | `head -1 population.csv` |
| deaths | u32 | `head -1 population.csv` |
| avg_energy | f32 | `head -1 population.csv` |
| lineage_count | u32 | `head -1 population.csv` |
| avg_stress_level | f32 | `head -1 population.csv` |
| archive_record_count | u32 | `head -1 population.csv` |
| **archive_sample_attempts** | u32 | `head -1 population.csv` [Required] |
| **archive_sample_successes** | u32 | `head -1 population.csv` [Required] |
| **archive_influenced_births** | u32 | `head -1 population.csv` [Required] |
| **lineage_diversity** | u32 | `head -1 population.csv` [Required] |
| **top1_lineage_share** | f32 | `head -1 population.csv` [Required] |
| **strategy_entropy** | f32 | `head -1 population.csv` [Required] |
| **collapse_event_count** | u32 | `head -1 population.csv` [Required] |

**Pass Criteria**: All 15 columns present with exact names

### 1.2 Column Name Exact Match

Run:
```bash
head -1 population.csv | tr ',' '\n' | sort > actual_columns.txt
cat << 'EOF' | sort > expected_columns.txt
archive_influenced_births
archive_record_count
archive_sample_attempts
archive_sample_successes
avg_energy
avg_stress_level
births
collapse_event_count
deaths
lineage_count
lineage_diversity
population
strategy_entropy
tick
top1_lineage_share
EOF
diff actual_columns.txt expected_columns.txt
```

**Pass Criteria**: No diff output

### 1.3 Data Type Validation

Check first 10 rows have valid numeric data:

```bash
awk -F',' 'NR>1 && NR<=11 {
  for(i=1;i<=NF;i++) {
    if($i+0 != $i && $i !~ /^[0-9]+\.[0-9]+$/) {
      print "Invalid data at row " NR ", col " i ": " $i
    }
  }
}' population.csv
```

**Pass Criteria**: No invalid data output

---

## Phase 2: Anti-God-Mode Assertions

### 2.1 Forbidden Access Patterns

Verify these patterns DO NOT exist in code:

| Pattern | File to Check | Verification |
|---------|---------------|--------------|
| `cell.*archive.*direct` | `cell.rs`, `world.rs` | `grep -r "cell.*archive" src/` should not show direct access |
| `archive.*cell.*policy` | `causal_archive.rs` | `grep -r "archive.*cell" src/` should not show policy override |
| `L3.*L1.*write` | `access_guard.rs` | Verify AccessGuard forbids this |
| `global.*teacher` | All `.rs` files | `grep -r "teacher\|oracle" src/` should be limited to comments |
| `perfect.*answer` | All `.rs` files | Should not exist |

### 2.2 AccessGuard Verification

Check `access_guard.rs` contains:

```rust
// Must have these checks:
(Accessor::Cell(_), Target::Archive, _) => Err(AccessError::Forbidden)
(Accessor::Archive, Target::CellMemory(_), AccessMode::Write) => Err(AccessError::Forbidden)
```

**Pass Criteria**: Both checks present and active

### 2.3 Sampling Probability Enforcement

Check that `ARCHIVE_SAMPLE_PROBABILITY = 0.01` is enforced:

```rust
// In constants.rs or causal_archive.rs:
pub const ARCHIVE_SAMPLE_PROBABILITY: f32 = 0.01;

// In reproduction logic:
if rng.f32() < ARCHIVE_SAMPLE_PROBABILITY {
    // Attempt archive sample
}
```

**Pass Criteria**: Constant defined and used, no hardcoded probability

---

## Phase 3: Experimental Conditions

### 3.1 Required Conditions

Verify these experimental conditions can be executed:

| Condition | Description | Verification Command |
|-----------|-------------|---------------------|
| `L3_real_p001` | Real L3 with p=0.01 sampling | `./p1_experiment --group CTRL` |
| `L3_shuffled_p001` | Shuffled L3 with p=0.01 | Must add shuffling flag |
| `L3_overpowered_direct` | Direct L3 access (violation) | For falsification only |
| `no_L1` | Cell memory disabled | `--disable-cell-memory` |
| `no_L2` | Lineage memory disabled | `--disable-lineage-memory` (exists) |
| `L3_off` | Archive completely disabled | `--disable-archive` |

### 3.2 Condition Implementation Check

Verify each condition produces different outputs:

```bash
# Run 100 generations of each condition
./p1_experiment --group CTRL --ticks 100 --output-dir test_ctrl
./p1_experiment --group P1A --ticks 100 --output-dir test_p1a
./p1_experiment --group P1C --ticks 100 --output-dir test_p1c

# Check outputs are different
md5sum test_*/seed_*/u0/population.csv | sort | uniq -c
```

**Pass Criteria**: Different MD5 hashes for different conditions

### 3.3 Per-Run CSV Output

Verify each run produces required CSV files:

```bash
for seed in 101 102 103; do
  for u in 0 1 2 3; do
    test -f "ctrl/seed_${seed}/u${u}/population.csv" || echo "Missing: ctrl/seed_${seed}/u${u}/population.csv"
    test -f "ctrl/seed_${seed}/u${u}/cdi.csv" || echo "Missing: ctrl/seed_${seed}/u${u}/cdi.csv"
    test -f "ctrl/seed_${seed}/u${u}/extinction.csv" || echo "Missing: ctrl/seed_${seed}/u${u}/extinction.csv"
  done
done
```

**Pass Criteria**: No "Missing" messages

---

## Phase 4: Integration Files

### 4.1 status-sync.json Update

Verify the file contains:

```json
{
  "repo": "bio-world",
  "interface_version": "v0.1.0",
  "owned_modules": [
    "l1_cell_memory",
    "l2_lineage_memory", 
    "l3_causal_archive",
    "metrics_export"
  ],
  "blocking_issues": [],
  "next_expected_inputs": []
}
```

### 4.2 open-questions.md Update

Verify at least Q1 (metrics format) and Q3 (lineage diversity) are marked resolved.

---

## Phase 5: Final Verification

### 5.1 End-to-End Test

Run complete verification:

```bash
#!/bin/bash
set -e

# 1. Build
cargo build --release

# 2. Run short experiment
./target/release/p1_experiment \
  --group CTRL \
  --seed 999 \
  --ticks 100 \
  --universes 2 \
  --output-dir acceptance_test

# 3. Check CSV columns
head -1 acceptance_test/seed_999/u0/population.csv | grep -q "archive_sample_attempts" || exit 1
head -1 acceptance_test/seed_999/u0/population.csv | grep -q "lineage_diversity" || exit 1

# 4. Check data non-zero
awk -F',' 'NR==2 {exit ($9 > 0 ? 0 : 1)}' acceptance_test/seed_999/u0/population.csv

echo "✓ All acceptance tests passed"
```

**Pass Criteria**: Script exits with 0

---

## Sign-off

| Item | Status | Checked By | Date |
|------|--------|------------|------|
| CSV columns present | ☐ | | |
| Column names exact | ☐ | | |
| Anti-God-Mode assertions | ☐ | | |
| All conditions runnable | ☐ | | |
| Per-run CSV output | ☐ | | |
| status-sync.json updated | ☐ | | |
| open-questions.md updated | ☐ | | |
| End-to-end test passes | ☐ | | |

**Overall Status**: ☐ PASS / ☐ FAIL

---

**Next**: Once all checked, proceed to SENTINEL_RUN_SPEC execution
