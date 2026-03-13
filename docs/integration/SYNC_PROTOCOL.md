# Atlas-BioWorld Synchronization Protocol

**Version**: v0.1.0  
**Date**: 2026-03-09  
**Applies To**: Atlas-HEC v2.1 & Bio-World v19

---

## 1. Mandatory File Updates

After every work round, **MUST** update:

### 1.1 status-sync.json

Location: `docs/integration/status-sync.json`

Required fields to update:
- `commit` - Current git commit hash
- `commit_subject` - Current commit message
- `timestamp` - ISO 8601 timestamp
- `owned_modules` - List of modules this repo owns
- `blocking_issues` - Any blockers
- `next_expected_inputs` - What this repo needs from other repo

### 1.2 open-questions.md

Location: `docs/integration/open-questions.md`

Must categorize questions into 3 types:

```markdown
## Blockers
Questions that prevent progress. Must resolve before next phase.

## Semantic Mismatch  
Questions about interpretation differences between repos.

## Next-Phase Proposals
Questions about future enhancements, not blocking current work.
```

---

## 2. Commit Message Tags

Every commit message **MUST** include at least one tag:

| Tag | Usage |
|-----|-------|
| `[atlas-sync]` | Atlas-HEC side synchronization |
| `[bioworld-sync]` | Bio-World side synchronization |
| `[sentinel-run]` | Sentinel validation run completed |
| `[oracle-audit]` | Hidden oracle audit performed |
| `[contract-align]` | Contract specification alignment |

### Examples

```bash
# Good
git commit -m "[atlas-sync] Update ContinuityProbe spec

- Add read-only constraints
- Define CSV output format
- Update status-sync.json"

# Good
git commit -m "[bioworld-sync] [contract-align] Add 7 required CSV fields

- archive_sample_attempts
- lineage_diversity
- strategy_entropy
- Update open-questions.md (resolve Q1, Q3)"

# Bad - missing tags
git commit -m "Fix bug in memory"
```

---

## 3. Status Report Format

Every progress report **MUST** include:

### 3.1 Current Commit

```yaml
current_commit: "abc1234"
commit_subject: "[tag] Brief description"
timestamp: "2026-03-09T20:30:00Z"
```

### 3.2 Changed Files

```yaml
changed_files:
  - path: "src/foo.rs"
    change: "added archive_sample_attempts counter"
  - path: "docs/integration/status-sync.json"
    change: "updated commit hash"
```

### 3.3 Runnable Commands

```bash
# How to verify this work
./verify_command.sh
python3 validate.py
```

### 3.4 Unresolved Blockers

```yaml
unresolved_blockers:
  - id: "B1"
    description: "Missing CSV fields"
    owner: "bio-world"
    eta: "2026-03-12"
```

---

## 4. Open Questions Template

### 4.1 Blockers

Format:
```markdown
### B{N}: {Title}

**Question**: {Clear question}

**Impact**: {Why this blocks progress}

**Owner**: {Who must resolve}

**Status**: Open | Under Discussion | Resolved

**Resolution**: {If resolved, how}
```

### 4.2 Semantic Mismatch

Format:
```markdown
### S{N}: {Title}

**Atlas Interpretation**: {How Atlas-HEC sees it}

**Bio-World Interpretation**: {How Bio-World sees it}

**Mismatch**: {Specific difference}

**Proposed Resolution**: {How to align}
```

### 4.3 Next-Phase Proposals

Format:
```markdown
### P{N}: {Title}

**Proposal**: {What to do next phase}

**Value**: {Why this matters}

**Effort**: {Estimated work}

**Dependencies**: {What must complete first}
```

---

## 5. Sync Checklist

Before every commit, verify:

- [ ] `status-sync.json` updated with current commit
- [ ] `open-questions.md` updated with any new questions
- [ ] Commit message includes required tag
- [ ] Questions properly categorized (blocker/semantic/proposal)
- [ ] Status report includes all 4 sections

---

## 6. Example Workflow

### Step 1: Do Work
```bash
# Edit code
vim src/output/csv_logger.rs

# Update status
echo '{"commit":"'$(git rev-parse --short HEAD)'"...}' > docs/integration/status-sync.json
```

### Step 2: Update Questions
```bash
vim docs/integration/open-questions.md
# Add/remove questions as needed
# Categorize correctly
```

### Step 3: Commit with Tag
```bash
git add -A
git commit -m "[bioworld-sync] [contract-align] Add CSV fields

- archive_sample_attempts
- archive_sample_successes
- lineage_diversity

Update status-sync.json and open-questions.md"
```

### Step 4: Generate Report
```bash
cat << 'REPORT'
current_commit: "$(git rev-parse --short HEAD)"
commit_subject: "[bioworld-sync] [contract-align] Add CSV fields"
changed_files:
  - src/output/csv_logger.rs
  - docs/integration/status-sync.json
  - docs/integration/open-questions.md
runnable_commands:
  - "head -1 population.csv"
  - "./validate_csv.py"
unresolved_blockers: []
REPORT
```

---

## 7. Automation Scripts

### 7.1 Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check status-sync.json exists and is valid
if [ ! -f "docs/integration/status-sync.json" ]; then
    echo "ERROR: status-sync.json missing"
    exit 1
fi

# Check commit message has tag
COMMIT_MSG_FILE=$1
if ! grep -E '\[(atlas-sync|bioworld-sync|sentinel-run|oracle-audit|contract-align)\]' "$COMMIT_MSG_FILE"; then
    echo "ERROR: Commit message must include sync tag"
    echo "Valid tags: [atlas-sync], [bioworld-sync], [sentinel-run], [oracle-audit], [contract-align]"
    exit 1
fi
```

### 7.2 Status Generator

```bash
#!/bin/bash
# generate_status.sh

cat << EOF
current_commit: "$(git rev-parse --short HEAD)"
commit_subject: "$(git log -1 --pretty=%B | head -1)"
timestamp: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

changed_files:
$(git diff --name-only HEAD~1 | sed 's/^/  - /')

runnable_commands:
  - "./verify.sh"

unresolved_blockers:
  - See docs/integration/open-questions.md
EOF
```

---

## 8. Cross-Repo Sync

When both repos update:

1. Atlas-HEC updates and pushes
2. Bio-World pulls Atlas changes
3. Bio-World updates own status
4. Bio-World pushes
5. Atlas-HEC pulls Bio-World changes
6. Both repos now have synced status

**Golden Rule**: Always pull before push, always update status before commit.

---

**Adopted By**:
- Atlas-HEC v2.1
- Bio-World v19

**Effective Date**: 2026-03-09
