# Execution Discipline - HARD LOCK

## 一句话

> 只执行 P0 与 P1；任何新家族、新场景、新指标、新机制，一律视为偏航。

## 当前状态

主线已收敛完成。接下来不是继续找路，而是严格执行 R2 和 Gate 1.5，并用停机规则防止研究自动化层把资源重新打散。

---

## P0: OctopusLike R2 (HARD LOCK)

### 只回答两个问题

1. 10x 之后还是不是主线候选？
2. First degradation mode 是什么？

### 强制输出 (6项，缺一不可)

| # | 指标 | 1x 基线 | 必须输出 | 停机阈值 |
|---|------|---------|----------|----------|
| 1 | CWCI retention | 0.688 | ✅ YES | < 0.55 |
| 2 | Specialization | 0.948 | ✅ YES | drop > 20% |
| 3 | Integration | 0.909 | ✅ YES | drop > 20% |
| 4 | Broadcast | 1.000 | ✅ YES | drop > 20% |
| 5 | Communication cost | baseline | ✅ YES | increase > 50% |
| 6 | First degradation mode | N/A | ✅ YES | identify |

### 不合格输出示例

- ❌ "总分还行，CWCI 0.60"
- ❌ "整体表现良好"
- ❌ "仍领先对照组"
- ❌ 缺少 6 项中任意一项

### 合格输出示例

```
R2 Validation Report:
  CWCI retention: 0.612 (89%) ✅
  Specialization: 0.891 (-6%) ✅
  Integration: 0.854 (-6%) ✅
  Broadcast: 0.923 (-8%) ✅
  Communication cost: +45% ⚠️
  First degradation mode: NONE ✅
  
  Verdict: SCALE_ROBUST → Proceed to 50x
```

---

## P1: OQS Gate 1.5 (HARD LOCK)

### 只回答一个问题

> 3 项最小修正后，OQS 能不能从"局部强"变成"整体稳"？

### 只允许验证 (3项，多一项都算偏航)

1. **division-of-labour**: Scene-adaptive bias
2. **lineage initialization**: Dynamic budget
3. **culling**: Gentle selection + recovery

### 禁止行为 (HARD NO)

- ❌ 加新机制
- ❌ 扩场景 (保持3个)
- ❌ 扩指标 (保持5个)
- ❌ 调评分标准
- ❌ 改核心架构

### 通过标准 (5/5，少一项都算 FAIL)

| 指标 | Gate 1 | Gate 1.5 Target | 必须达标 |
|------|--------|-----------------|----------|
| HighCoordinationDemand | 0.815 | ≥ 0.770 | ✅ |
| ResourceScarcity | 0.036 | ≥ 0.250 | ✅ |
| FailureBurst | 0.015 | ≥ 0.250 | ✅ |
| lineage_improvement | -0.219 | > 0 | ✅ |
| experience_return_quality | 0.000 | > 0 | ✅ |

---

## 停机规则 (HARD HALT)

### R2 停机条件 (任一触发即停)

```yaml
halt_conditions:
  cwci_retention_below: 0.55
  
  capability_degradation:
    specialization_drop_gt: 20%
    integration_drop_gt: 20%
    broadcast_drop_gt: 20%
    any_one: true  # 任一项触发即停
  
  communication_cost:
    increase_gt: 50%
    without_corresponding_gain: true
  
  action: STOP_AND_AUDIT
  next_step: DEGRADATION_AUDIT
  do_not: CONTINUE_TO_50X
```

### OQS 停机条件 (任一触发即停)

```yaml
halt_conditions:
  fixes_improved:
    count_lt: 1  # 0/3 改善
    
  queen_overload:
    not_zero: true  # 不再为 0
    
  action: STOP_AND_PRESERVE
  next_step: KEEP_AS_SECONDARY
  do_not: CONTINUE_PATCHING
```

---

## 偏航检测 (AUTOMATED)

以下行为自动触发偏航警报：

1. 提议添加新家族 (BeeHiveLike/AntColonyLike 等)
2. 提议扩展场景 (>3个)
3. 提议扩展指标 (>强制输出列表)
4. 提议添加新机制 (>3项修正)
5. 提议修改评分标准
6. 提议修改核心架构 (未经 L4 审核)
7. 结果缺少强制输出项

偏航响应：
- 🚨 ALERT: "偏航检测触发"
- 🛑 HALT: 停止当前执行
- 📝 LOG: 记录偏航行为
- 👤 ESCALATE: 等待人工审核

---

## 执行检查清单

### R2 执行前检查

- [ ] 配置文件中 scale = 10x
- [ ] 输出模板包含 6 项强制指标
- [ ] 停机规则已加载
- [ ] 偏航检测已启用

### R2 执行后检查

- [ ] 6 项强制指标全部输出
- [ ] First degradation mode 已识别
- [ ] 未触发停机条件
- [ ] 偏航检测无警报

### Gate 1.5 执行前检查

- [ ] 只应用 3 项修正
- [ ] 场景保持 3 个
- [ ] 指标保持 5 个
- [ ] 无新机制

### Gate 1.5 执行后检查

- [ ] 5/5 指标全部达标
- [ ] Queen overload = 0
- [ ] 未触发停机条件
- [ ] 偏航检测无警报

---

## 资源锁定

```
P0 (OctopusLike R2):     70% ████████████████████
P1 (OQS Gate 1.5):       25% ███████
P2 (New Families):        5% █ (FROZEN)
─────────────────────────────────────────────
任何试图从 P0/P1 移出资源的行为 = 偏航
```

---

## 一句话总结

> 主线已经收敛完成；接下来不是继续找路，而是严格执行 R2 和 Gate 1.5，并用停机规则防止研究自动化层把资源重新打散。

**偏航 = 停机 + 人工审核**
