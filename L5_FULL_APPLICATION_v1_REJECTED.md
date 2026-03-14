# L5 Full Experiment Application

**申请时间**: 2026-03-15 (Hour-2成功后立即申请)  
**申请依据**: L5_HOUR2_RESULT.md (SUCCESS verdict)  
**前置**: L4-v2 CERTIFIED + L5 Pilot SUCCESS

---

## L5 Pilot 历程回顾

| Phase | 结果 | 关键指标 |
|-------|------|----------|
| **Hour-1** | Marginal (2/3 signals) | Transfer Gap: 0.0pp, Code Retention: 92.7% |
| **Hour-2** | **SUCCESS** ✅ | **Transfer Gap: 11.7pp**, Code Retention: 91.5% |

**关键发现**: Hour-1的marginal结果源于小样本(18 seeds)，Hour-2扩大至48 seeds后显示出清晰的正迁移信号。

---

## L5 Full 目标

验证：**Multi-task inheritance works across diverse task pairs, not just Code→Math**

具体目标:
1. 验证至少3个不同任务对的transfer可行性
2. 建立Transfer Gap基线数据库
3. 识别optimal task pair combinations
4. 排除task-specific overfitting

---

## 实验设计

### 3个Task定义

| Task ID | 领域 | 复杂度 | 与L4关系 |
|---------|------|--------|----------|
| **Task A** | Code / Tool-use | Medium | L4-v2已验证 |
| **Task B** | Math / Symbolic reasoning | Medium | Pilot已验证 (Code→Math) |
| **Task C** | Planning / Scheduler control | Medium | **NEW** |

### 6个Directed Pairs (最小完整矩阵)

```
Source → Target:
1. A → B (Code → Math)     [Pilot已验证, 11.7pp]
2. A → C (Code → Planning) [NEW]
3. B → A (Math → Code)     [Reverse验证]
4. B → C (Math → Planning) [NEW]
5. C → A (Planning → Code) [NEW]
6. C → B (Planning → Math) [NEW]
```

### 每组设计

沿用Pilot成功模式:
- G1 Transfer: 32 seeds
- G2 Sham: 32 seeds
- G3 Self-Ref: 16 seeds (参考)
- **每组总计**: 80 seeds

### 总规模

```
6 pairs × 80 seeds = 480 seeds total
```

---

## 执行计划

### Phase 1: A→B Replication (验证Pilot可重复)
- 80 seeds
- 目标: Transfer Gap ≥5pp (与Pilot 11.7pp一致)
- 时间: 4-6 hours

### Phase 2: Novel Pairs (A→C, B→C, etc.)
- 5 pairs × 80 = 400 seeds
- 分批执行，每pair独立验证
- 每pair 4-6 hours

### Phase 3: Meta-Analysis
- Cross-pair comparison
- Identify best transfer directions
- Optimal task sequencing

**总预计时间**: 30-40 hours (分多天执行)

---

## 成功标准 (L5 Full Certification)

### 必须满足

| 标准 | 阈值 | 测量 |
|------|------|------|
| Replicable A→B | ≥5pp | Phase 1 replication |
| Novel pairs positive | ≥3/5 pairs with Transfer Gap >0 | Phase 2 |
| No catastrophic forgetting | ≥85% retention on all source tasks | Across all pairs |
| Leakage controlled | <5% on all pairs | Source detection |

### 分级认证

- **L5-A (Full)**: 5/6 pairs positive, A→B replicable
- **L5-B (Partial)**: 3-4/6 pairs positive
- **L5-C (Limited)**: 1-2/6 pairs positive, task-specific
- **L5-X (Failed)**: <2 pairs positive or major forgetting

---

## 风险控制

### 已知风险

| 风险 | 缓解 |
|------|------|
| Task C设计不当 | Pilot Task C alone first (1 hour) |
| 计算资源不足 | Batch execution, checkpoint every pair |
| 负迁移对 | Early detection, skip if Transfer Gap < -2pp |

### 熔断条件

- Any pair: Code retention < 80% → STOP all
- Any pair: Leakage > 10% → STOP all
- 3+ pairs: Transfer Gap ≤ 0 → REJECT L5 concept

---

## 产出物

| 文件 | 内容 |
|------|------|
| `L5_FULL_PHASE1_RESULTS.md` | A→B replication |
| `L5_FULL_PHASE2_PAIR*.md` | Each novel pair results |
| `L5_FULL_META_ANALYSIS.md` | Cross-pair comparison |
| `L5_FULL_CERTIFICATION.md` | Final verdict |

---

## 资源需求

| 资源 | Pilot (H1+H2) | Full | 增量 |
|------|---------------|------|------|
| Seeds | 66 | 480 | ~7x |
| Compute | ~12K steps | ~96K steps | ~8x |
| Time | 2 hours | 30-40 hours | Multi-day |
| 存储 | Minimal | Moderate | + |

---

## 与L4的连续性

### 继承机制
- 128-seed discipline (scaled to 80 per pair)
- Pool A-F stratification
- Anti-leakage system
- Circuit breaker monitoring

### 升级机制
- Single-task (L4) → Multi-task (L5)
- Control Gap → Transfer Gap
- 1 task → 3 tasks
- 1 pair → 6 directed pairs

---

## 批准请求

**申请**: L5 Full Experiment  
**规模**: 480 seeds, 6 task pairs, multi-day  
**目标**: Multi-task inheritance certification  
**基于**: L4-v2 CERTIFIED + L5 Pilot SUCCESS (11.7pp Transfer Gap)

**批准状态**: 待审核

---

**提交**: Atlas-HEC Research Committee  
**前置**: Hour-2 SUCCESS  
**期望开始**: Upon approval

---

*"Hour-2的11.7pp证明了跨任务迁移可行。现在的问题是：这是否具有普遍性，还是仅限于Code→Math这一对？L5 Full将回答这个问题。"*
