# 状态核验分层说明

**日期**: 2026-03-10  
**目的**: 严格区分 repo-grounded 状态 vs 最新运行结果

---

## Layer 1: Repo-Grounded（可核验）

以下状态可在当前仓库中直接验证：

### D1: ✅ COMPLETE
**核验路径**: `docs/candidates/TODO_MASTER_LIST.md`

```
Independent variance: 0.019578
Paired variance: 0.003898  
Reduction ratio: 80.1%
Status: Framework validated and operational
```

**复现命令**: `cargo run --bin d1_runner` (in 001_markers)

### D4: 🟡 PARTIAL COMPLETE
**核验路径**: `docs/candidates/TODO_MASTER_LIST.md`

- ✅ D4.1/D4.2 (001): 已完成，记录在TODO中
- 🟡 D4.3-D4.5 (002): 运行完成，但TODO更新滞后

**001 关键发现**（已入库）：
```
ReadOnly: decision_variance=0, SNR=0 (fixed-marker无动态)
WriteOnly/Full/Baseline: decision_variance=1451.6, SNR=6.36 (正常)
所有模式 tick_smoothness=253 (动作层不受影响)
```

### 001/002 决策: ✅ RECORDED
**核验路径**: `docs/candidates/FINAL_EXPERIMENTS_WEEK1_VERDICT.md`

- **001**: REFRAME - "伤害来自 fixed-marker read，不是 write 机制"
- **002**: Current task-line terminated, family archived-not-deleted

### E1/E3 实验规格: ✅ SPECIFIED
**核验路径**: `docs/candidates/E_CLASS_EXPERIMENT_SPEC.md`

- E1 Phase A 设计: N×K×σ sweep, 通关标准 r跃迁 (<0.2 → >0.8)
- E3 设计: 验证 P 先于 r 上升的因果链

---

## Layer 2: 最新运行结果（待入库）

以下结果刚生成，尚未完全同步到仓库文档：

### E1 Phase A: ✅ COMPLETE（结果待落库）
**数据路径**: `results/e1_phase_a/`

```
Configs: 300 (N=5 × K=20 × σ=3)
Transitions detected: 15/15 (100%)
K_c approx: σ=0.1→~0.2, σ=0.5→~1.0, σ=1.0→~1.8
Sync distribution:
  r<0.2: 49.3% (disordered)
  0.2<r<0.8: 6.0% (transition, narrow)
  r>0.8: 44.7% (ordered)
```

**分析脚本**: `results/e1_phase_a/analyze_transition.py`

### E1 Phase B: 🔥 EXECUTING
**日志路径**: `/tmp/e1_phase_b.log`

```
Configs: 1200 (N=4 × K=50 × σ=3 × 2初始条件)
Status: Running (started 2026-03-10 09:25)
Purpose: 临界区精细刻画 + 滞后效应检测
```

---

## Layer 3: 基于结果的判断（建议性）

基于Layer 1+2的综合判断，**建议但不等同于事实**：

### 建议: E-class 升级为主线候选
**依据**: 
- E1 Phase A 100%检测到相变 (符合 E_CLASS_EXPERIMENT_SPEC 成功标准)
- 过渡区狭窄 (6%)，暗示锐利相变
- K_c 随 σ 变化符合物理直觉

**待验证**（E1 Phase B决定最终地位）：
- [ ] K_c 随 N 收敛趋势
- [ ] 滞后效应 / 临界指数
- [ ] 有限尺寸标度

### 建议: 001 退居次位
**依据**:
- D4已确认 WriteOnly 正常、ReadOnly 有害
- 问题定位清晰：fixed-marker 语义错误
- 非紧急修复，可排在 E-class 之后

---

## 措辞规范模板

### ❌ 不推荐
```
"E 类已经证明是主线"
"E1 成功验证了临界相变"
"Family 10 正式成为主线"
```

### ✅ 推荐
```
"E1 Phase A 已提供强烈的临界相变证据，
 Family 10 升级为主线候选；
 是否正式进入主线，取决于 E1 Phase B 的有限尺度收敛
 与 E3 的 P→r 因果验证。"
```

---

## 当前优先级（建议）

| 优先级 | 任务 | 状态 | 准入条件 |
|--------|------|------|----------|
| P0 | E1 Phase B | 🔥 EXECUTING | Phase A完成 |
| P0 | E3 Phase A | ⏸️ READY | Phase A完成 |
| P1 | A1×A5 | ⏸️ WAITING | E1 Phase B结果 |
| P1 | C1 | ⏸️ PENDING | 资源允许 |
| P2 | 001优化 | ⏸️ BACKLOG | E-class完成后 |

---

## 下次状态更新触发条件

1. **E1 Phase B 完成** → 更新 Layer 2，评估主线地位
2. **E3 Phase A 完成** → 验证/推翻 P→r 因果链
3. **Layer 2 数据落库** → 合并到 Layer 1

---

**核验人**: [待填写]  
**核验日期**: [待填写]
