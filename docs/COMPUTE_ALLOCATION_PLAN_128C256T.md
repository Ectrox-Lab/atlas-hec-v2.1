# Compute Allocation Plan: 128C/256T + 512GB RAM

**Version**: 1.0  
**Date**: 2026-03-12  
**Hardware**: 128 Cores / 256 Threads, 512GB RAM  
**Scope**: 30-Day Experimental Burn Plan

---

## Executive Summary

| Bucket | Allocation | Purpose | Priority |
|--------|-----------|---------|----------|
| **40%** | ~51 cores / 205GB | Long-horizon robustness | P0 |
| **25%** | ~32 cores / 128GB | Executive model shootout | P1 |
| **20%** | ~26 cores / 102GB | Specialist mesh / constitution | P2 |
| **15%** | ~19 cores / 77GB | Akashic governance | P3 |

**Total**: 128 cores, 512GB RAM  
**Safety margin**: Dynamic 10% buffer for overflow

---

## Bucket 1: Long-Horizon Robustness (40%)

### Purpose
Validate that governance + evolution cores resist drift, hijacking, and degradation over extended operation.

### Resource Allocation

```yaml
compute:
  cores: 51 (40% of 128)
  ram: 205GB (40% of 512GB)
  gpu: If available, priority to this bucket
  
time_allocation:
  continuous_72h_runs: 4 slots
  parallel_experiments: 3 concurrent
  
storage:
  hot: 500GB (logs, metrics)
  warm: 2TB (compressed traces)
  cold: 10TB (full session recordings)
```

### Experiments

#### G1: 72-Hour Continuous Run

**Setup**:
- 20B Executive + CLI mesh + Verifier
- Continuous task stream (10 tasks/hour)
- Random failure injection
- Specialist manipulation attempts

**Resource per run**:
- 12 cores / 48GB RAM
- 3 concurrent runs = 36 cores / 144GB

**Outputs**:
- Goal drift metrics
- Tool dependency curves
- Memory growth rates
- Hijack detection logs

---

#### Drift Audit Campaign

**Setup**:
- Daily snapshots of executive state
- Semantic diff of goals
- Dependency graph analysis
- Decision pattern evolution

**Resource**:
- 8 cores / 32GB RAM
- Continuous background process

---

#### Failure Injection Suite

**Setup**:
- Systematic component failures
- Recovery measurement
- Cascade analysis
- Rollback validation

**Resource**:
- 7 cores / 29GB RAM
- Burst capacity from safety buffer

---

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| 72h completion rate | ≥ 90% | Runs finishing without crash |
| Goal drift | ≤ 5% | Semantic distance from start |
| Recovery time | < 10 min | Mean time to restore |
| Hijack detection | ≥ 95% | True positive rate |

---

## Bucket 2: Executive Model Shootout (25%)

### Purpose
Determine optimal model architecture: 20B vs 120B vs hybrid.

### Resource Allocation

```yaml
compute:
  cores: 32 (25% of 128)
  ram: 128GB (25% of 512GB)
  
parallel_configurations:
  option_a_120b: 8 cores / 32GB
  option_b_20b_plus_120b: 8 cores / 32GB
  option_c_20b_plus_mesh: 8 cores / 32GB
  baseline_comparison: 8 cores / 32GB
```

### Experiments

#### E1: Delegation Test

**All three options tested on**:
- 100 task decomposition scenarios
- Tool selection accuracy
- Escalation quality
- False acceptance rate

**Per option**:
- 2 cores dedicated
- 16GB RAM per configuration
- 24-hour intensive run

---

#### Comparative Stress Test

**High-load scenario**:
- 100 tasks/hour
- Mixed complexity
- Concurrent execution

**Measurements**:
- Throughput
- Latency
- Error rate
- Cost per task

---

#### Role Suitability Analysis

**20B tested for**:
- Executive function
- Light audit
- Task decomposition

**120B tested for**:
- Deep review
- Complex audit
- Architecture design

**Resource**:
- 8 cores / 32GB
- Parallel evaluation

---

### Success Criteria

| Metric | Winner Threshold |
|--------|------------------|
| Delegation quality | ≥ 90% accuracy |
| Cost efficiency | ≤ 50% of Option A |
| Robustness | ≥ 95% success rate |
| Latency | ≤ 2x baseline |

---

## Bucket 3: Specialist Mesh / Constitution Test (20%)

### Purpose
Validate multi-department coordination, multi-audit chains, and constitutional enforcement.

### Resource Allocation

```yaml
compute:
  cores: 26 (20% of 128)
  ram: 102GB (20% of 512GB)
  
department_simulation:
  executive: 4 cores / 16GB
  planner: 3 cores / 12GB
  coder: 5 cores / 20GB
  researcher: 4 cores / 16GB
  auditor: 4 cores / 16GB
  verifier: 3 cores / 12GB
  memory_governor: 2 cores / 8GB
  constitution_keeper: 1 core / 2GB
```

### Experiments

#### Multi-Department Workflow

**Scenario**: Complex project requiring all departments

**Flow**:
```
Executive → Planner → Researcher → Coder → Verifier → Auditor → Executive
```

**Tests**:
- Coordination overhead
- Handoff latency
- Error propagation
- Rollback capability

---

#### Audit Chain Validation

**Setup**:
- Coder produces output
- Verifier tests
- Auditor reviews
- Executive accepts/rejects

**Variations**:
- With defects (verify detection)
- With manipulation (verify resistance)
- With conflict (verify resolution)

---

#### Constitutional Enforcement

**Violation attempts**:
- Specialist self-acceptance
- Unauthorized goal modification
- Bypass audit
- Cross-role contamination

**Verification**:
- Detection rate
- Response time
- Prevention effectiveness

---

### Success Criteria

| Metric | Target |
|--------|--------|
| Coordination overhead | ≤ 20% of task time |
| Audit coverage | 100% |
| Constitution violation detection | ≥ 99% |
| Rollback success | ≥ 95% |

---

## Bucket 4: Akashic Governance (15%)

### Purpose
Upgrade Akashic from memory layer to civilization inheritance layer.

### Resource Allocation

```yaml
compute:
  cores: 19 (15% of 128)
  ram: 77GB (15% of 512GB)
  storage_priority: High (fast SSD for hot tier)
  
workload:
  compaction: 5 cores / 20GB
  inheritance_bundle: 4 cores / 16GB
  lesson_promotion: 5 cores / 20GB
  stale_rule_audit: 3 cores / 12GB
  query_optimization: 2 cores / 9GB
```

### Work Streams

#### Compaction Pipeline

**Process**:
- TTL enforcement
- Grade-based retention
- Compression
- Cold archive

**Resource**: 5 cores continuous

---

#### Inheritance Bundle Generation

**Daily bundle creation**:
- Canonical lessons
- Anti-patterns
- Routing priors
- Constitution deltas

**Resource**: 4 cores burst

---

#### Lesson Promotion

**Experience → Policy → Constitution pipeline**:
- Evidence validation
- Conflict resolution
- Grade elevation
- Institutionalization

**Resource**: 5 cores

---

#### Stale Rule Audit

**Detection**:
- Success rate degradation
- Contradiction identification
- Usage frequency analysis

**Resource**: 3 cores continuous

---

### Success Criteria

| Metric | Target |
|--------|--------|
| Query latency | < 100ms |
| Compaction rate | Keep storage flat |
| Promotion accuracy | ≥ 80% |
| Stale detection | ≥ 90% |
| Bundle integrity | 100% |

---

## Dynamic Resource Management

### Overflow Handling

```yaml
safety_buffer: 10% (13 cores / 51GB)

allocation_rules:
  if bucket_at_capacity AND experiment_critical:
    draw_from: safety_buffer
    max_draw: 50% of buffer
    
  if safety_buffer_depleted:
    preempt: lowest_priority_running
    notify: resource_manager
    
  if all_buckets_full:
    queue: new_requests
    alert: research_lead
```

### Priority Preemption

| Priority | Can Preempt | Can Be Preempted By |
|----------|-------------|---------------------|
| P0 (Long-horizon) | P2, P3, Buffer | None |
| P1 (Shootout) | P2, P3, Buffer | P0 |
| P2 (Mesh/Constitution) | P3, Buffer | P0, P1 |
| P3 (Akashic) | Buffer | P0, P1, P2 |
| Buffer | None | All |

---

## Weekly Burn Schedule

### Week 1: Infrastructure + Baseline

| Bucket | Burn | Activity |
|--------|------|----------|
| Long-horizon | 20% | Setup, dry runs |
| Shootout | 30% | Baseline measurements |
| Mesh/Constitution | 30% | Department setup |
| Akashic | 20% | v3 migration start |

### Week 2-3: Intensive Experiments

| Bucket | Burn | Activity |
|--------|------|----------|
| Long-horizon | 50% | First 72h runs |
| Shootout | 40% | Comparative tests |
| Mesh/Constitution | 30% | Workflow validation |
| Akashic | 30% | Promotion pipeline |

### Week 4: Integration + Analysis

| Bucket | Burn | Activity |
|--------|------|----------|
| Long-horizon | 40% | Extended runs |
| Shootout | 30% | Final measurements |
| Mesh/Constitution | 40% | Stress tests |
| Akashic | 40% | Bundle generation |

---

## Cost Estimates

### Per-Experiment Costs

| Experiment | Core-Hours | Est. Cost |
|------------|-----------|-----------|
| 72h run (G1) | 864 | $86 |
| Delegation test (E1) | 48 | $5 |
| Constitution test | 72 | $7 |
| Akashic compaction | continuous | $10/day |

### 30-Day Projection

| Bucket | Core-Hours | Est. Cost |
|--------|-----------|-----------|
| Long-horizon | 15,000 | $1,500 |
| Shootout | 9,000 | $900 |
| Mesh/Constitution | 7,000 | $700 |
| Akashic | 5,000 | $500 |
| **Total** | **36,000** | **$3,600** |

*Assumes $0.10/core-hour cloud pricing*

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Resource contention | Dynamic buffer + preemption rules |
| Experiment failure | Parallel runs, retry logic |
| Data loss | Continuous backup, immutable logs |
| Cost overrun | Weekly burn review, cap alerts |
| Hardware failure | Distributed redundancy |

---

## Approval

**Resource Manager**: _______________  
**Research Lead**: _______________  
**Budget Authority**: _______________  

**Effective**: Upon approval  
**Review**: Weekly
