# TARGET_COMMANDS.md - 未来目标验证命令 (v2.3-v2.5)

> **这些命令描述的是P2/P4目标功能，当前v2.1还不存在**  
> 当前可用命令见 `REPRO_COMMANDS.md`

---

## 🎯 关于本文档

本文档描述的是**未来目标**，不是当前能运行的命令。

它用于：
- 明确v2.3-v2.5要实现的功能
- 作为开发目标
- 作为验证标准

**当前状态**: v2.1不具备这些能力。

---

## P2目标: 真正自我维持 (v2.4)

### 目标命令格式

```bash
# 启动带学习得来的自我维持的系统
cargo run --release --bin atlas_hec_burn \
  --mode hetero \
  --self-preservation learned  # 学习模式，非硬编码
```

### 预期输出 (未来目标)
```
═══════════════════════════════════════════════════════
🔥 Atlas-HEC v2.4 - Learned Self-Preservation
═══════════════════════════════════════════════════════

[0h00m] Initializing with learned survival strategy...
[0h00m] Self-preservation threshold: ADAPTIVE (learning)
...
[2h30m] High load detected
[2h30m] Learned response: reduce non-essential compute
[2h30m] Survival probability: 0.85 -> 0.92
...
```

### 关键区别

| 版本 | 睡眠触发 | 类型 |
|------|----------|------|
| v2.1 (当前) | `if adenosine > 0.6` | 硬编码规则 |
| v2.4 (目标) | `if survival_model.predict() < threshold` | 学习得来 |

---

## P4目标: 72小时持久Agent (v2.5)

### 目标命令格式

```bash
# 启动72小时自主运行
timeout 73h ./target/release/atlas_hec_burn \
  --mode hetero \
  --duration 259200 \
  --self-preservation learned \
  --self-report-enabled \
  --log logs/72h-autonomous-test.log
```

### 预期输出 (未来目标)
```
═══════════════════════════════════════════════════════
🔥 Atlas-HEC v2.5 - Persistent Agent Loop
═══════════════════════════════════════════════════════
Duration: 72 hours (259200 seconds)
Self-Kernel: ACTIVE
Self-Report: ENABLED
═══════════════════════════════════════════════════════

[0h00m] System initialized
[0h00m] SelfState: {
  identity: "atlas-v2.5-001",
  creation: "2026-03-09T00:00:00Z",
  current_goal: "survive_and_learn",
  status: "healthy"
}

[24h00m] 24h checkpoint
[24h00m] Self-report: "I have been running for 24 hours. 
          I have learned X patterns. 
          I have adjusted my parameters Y times."
[24h00m] Auto-adjusting learning rate: 0.005 -> 0.003

[48h00m] 48h checkpoint
[48h00m] Self-diagnosis: minor memory fragmentation detected
[48h00m] Self-repair: initiating defragmentation
[48h00m] Self-repair: complete, performance restored

[72h00m] 72h complete
[72h00m] Final self-report: "I am Atlas-v2.5-001. 
          I was created 72 hours ago. 
          I have survived without human intervention."

✅ 72H AUTONOMOUS RUN COMPLETE
   Zero crashes
   Zero human intervention
   Self-maintained throughout
```

### 关键能力 (未来目标)

- [ ] **SelfState active**: 系统有活跃的SelfKernel
- [ ] **Self-reported status**: 能报告自己的健康状态
- [ ] **Auto-adjusted parameters**: 能自主调整参数
- [ ] **Self-diagnosis**: 能诊断自身问题
- [ ] **Self-repair**: 能修复自身问题
- [ ] **72h complete**: 完成72小时自主运行

---

## P1目标: Self Kernel验证 (v2.2-v2.3)

### 目标命令格式

```bash
# 测试Self Kernel
cargo test --bin self_kernel_test

# 运行带Self Kernel的burn test
cargo run --release --bin atlas_hec_burn \
  --self-kernel-enabled \
  --test-self-report
```

### 预期输出 (未来目标)
```
═══════════════════════════════════════════════════════
🧠 Atlas-HEC v2.3 - Self Kernel Test
═══════════════════════════════════════════════════════

Test 1: who_am_i()
  Response: "I am atlas-v2.3-001, created at 2026-03-09T00:00:00Z"
  Result: ✅ PASS

Test 2: what_did_i_just_do()
  Response: "Recent actions: [explore_north, learn_pattern_x, rest]"
  Result: ✅ PASS

Test 3: what_if_i_continue(explore_south)
  Prediction: "Energy will decrease by 0.15, reward may increase"
  Result: ✅ PASS

Test 4: should_preserve_self()
  Current state: load=0.8, energy=0.3
  Decision: true (initiate rest sequence)
  Result: ✅ PASS

═══════════════════════════════════════════════════════
All Self Kernel tests PASSED
═══════════════════════════════════════════════════════
```

### Self Kernel能力 (未来目标)

1. **Identity Token**: 系统有稳定的"这是我"
2. **Internal State Snapshot**: 能查询当前状态
3. **Self History Window**: 能引用最近N个自我事件
4. **Self Prediction**: 能预测"如果我做X，我会变成什么"

---

## 开发路线图对照

| 文档 | 内容 | 状态 |
|------|------|------|
| `REPRO_COMMANDS.md` | 当前能跑的命令 | ✅ v2.1可用 |
| `TARGET_COMMANDS.md` | 未来要实现的命令 | ⏸️ v2.3-v2.5目标 |

---

## 如何实现这些目标

### P1: Self Kernel (v2.2-v2.3)
1. 实现 `source/src/self_kernel/mod.rs`
2. 添加 IdentityToken, InternalState, SelfHistoryWindow
3. 实现 `who_am_i()`, `what_did_i_just_do()`, `what_if_i_continue()`
4. 验证测试通过

### P2: 真正自我维持 (v2.4)
1. 用学习算法替代 `needs_rem()` 中的硬编码阈值
2. 实现 `SelfPredictor` 预测生存概率
3. 实现自适应的自我保护决策

### P4: 72小时持久Agent (v2.5)
1. 整合 Self Kernel + 学习得来的自我维持
2. 添加自我诊断和自我修复机制
3. 运行72小时测试

---

*本文档描述的是目标，不是当前现实*  
*当前现实见 `PROJECT_STATE.md` 和 `REPRO_COMMANDS.md`*
