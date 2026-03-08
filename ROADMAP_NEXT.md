# ROADMAP_NEXT.md - 下一阶段工程路线图

> 只写未来2-3个阶段，实用导向，不哲学化  
> **当前阶段**: P0完成，准备进入P1

---

## P0: 项目记忆固定 (COMPLETED ✅)

**目标**: 建立不会失忆的研究系统

### 已完成任务
- [x] 创建PROJECT_STATE.md - 当前架构真相
- [x] 创建CLAIMS_REGISTRY.md - 声明证据注册表
- [x] 创建REPRO_COMMANDS.md - 可复现实验命令
- [x] 创建ROADMAP_NEXT.md - 本路线图
- [x] 路径标准化 (repo root: `/home/admin/atlas-hec-v2.1-repo`)

### 产出
- 4个核心文档已提交到GitHub
- 所有路径已标准化
- 实验可复现

---

## P1: 最小可验证 Self Kernel (CURRENT - 2-4周)

**目标**: 添加internal reference `this_is_me`，跨过第一个关键门槛

### 为什么是最小版本？
GPT建议：不要一开始就做完整的SelfState产品级结构，先做能跑的this_is_me kernel。

### 核心模块 (MVP版本)

```rust
// source/src/self_kernel/mod.rs

/// 1. Identity Token - "这是我"
pub struct IdentityToken {
    uuid: String,           // "atlas-v2.3-001"
    creation_time: Instant,
    version: String,        // "v2.3.0"
}

/// 2. Current Internal State - "我现在的状态"
pub struct InternalState {
    vigilance: VigilanceState,      // 来自DigitalMetabolism
    energy_budget: f32,
    compute_load: f32,
    current_goal: Option<Goal>,
}

/// 3. Active Goal Vector - "我想维持/达成什么"
pub struct GoalVector {
    primary: Goal,          // 当前主要目标
    secondary: Vec<Goal>,   // 次要目标
    survival_priority: f32, // 生存优先级
}

/// 4. Self History Window - "我刚才做了什么"
pub struct SelfHistoryWindow {
    recent_actions: VecDeque<Action>,  // 最近N个动作
    recent_states: VecDeque<StateSnapshot>, // 最近N个状态快照
    max_window: usize,      // 窗口大小
}

/// 5. Prediction of Self Change - "如果我做X，我会变成什么"
pub struct SelfPredictor {
    model: WorldModel,      // 简化的自我在世界中的模型
    prediction_horizon: Duration,
}

/// Self Kernel - 最小可验证版本
pub struct SelfKernel {
    identity: IdentityToken,
    state: InternalState,
    goals: GoalVector,
    history: SelfHistoryWindow,
    predictor: SelfPredictor,
}

impl SelfKernel {
    /// 核心能力1: 回答"我是谁"
    pub fn who_am_i(&self) -> String {
        format!(
            "I am {} ({}), created at {:?}, version {}",
            self.identity.uuid,
            self.identity.name(),
            self.identity.creation_time,
            self.identity.version
        )
    }
    
    /// 核心能力2: 回答"我刚才做了什么"
    pub fn what_did_i_just_do(&self) -> String {
        let recent = self.history.recent_actions
            .iter()
            .map(|a| format!("{:?}", a))
            .collect::<Vec<_>>()
            .join(", ");
        format!("Recent actions: {}", recent)
    }
    
    /// 核心能力3: 回答"如果我继续这样做，我会变成什么状态"
    pub fn what_if_i_continue(&self, action: Action) -> PredictedState {
        self.predictor.predict(&self.state, &action)
    }
    
    /// 核心能力4: 自我维持决策
    pub fn should_preserve_self(&self) -> bool {
        let survival_threat = self.assess_survival_threat();
        survival_threat > 0.7  // 学习得来的阈值，非硬编码
    }
}
```

### 验证标准 (P1完成标准)

- [ ] **系统有稳定 identity_token**
  - 验证: `self_kernel.who_am_i()` 返回一致的身份字符串
  - 证据: 运行日志中显示相同uuid

- [ ] **系统有可查询 internal state snapshot**
  - 验证: 能输出当前energy、vigilance、load等状态
  - 证据: 日志中有结构化的状态记录

- [ ] **系统能持久保存最近 N 个自我事件**
  - 验证: `self_kernel.what_did_i_just_do()` 返回最近动作
  - 证据: history window中有内容

- [ ] **系统能回答 3 个固定问题**
  1. "我是谁?" → 返回identity信息
  2. "我刚才做了什么?" → 返回recent actions
  3. "如果我继续这样做，我会变成什么状态?" → 返回predicted state

### 代码位置
```
source/src/self_kernel/mod.rs       # SelfKernel实现
source/src/self_kernel/identity.rs  # IdentityToken
source/src/self_kernel/state.rs     # InternalState
source/src/self_kernel/history.rs   # SelfHistoryWindow
source/src/self_kernel/predictor.rs # SelfPredictor
source/src/bin/self_kernel_test.rs  # 验证测试
```

---

## P2: 真正自我维持 (4-6周)

**目标**: 将硬编码规则变为学习得来的生存策略

### 当前问题
```rust
// 硬编码 (v2.1) - ❌
if adenosine_level > 0.6 {  // 硬编码阈值
    enter_rem();
}
```

### 目标
```rust
// 学习得来 (v2.4) - ✅
let survival_value = self.predictor.predict(
    "if I continue at this load, what happens to me?"
);
if survival_value < threshold {  // 学习得来的阈值
    self.preserve();  // 学习得来的自我保护
}
```

### 任务清单
- [ ] 实现`avoid_self_damage`学习
- [ ] 实现`maintain_internal_state`策略
- [ ] 实现`repair_subsystems`机制
- [ ] 验证: 生存策略是学来的，不是硬编码的

---

## P3: MNIST认证重试 (次线 - 3-4周)

**注意**: 这是**次线**，不是主主。原因：MNIST验证的是"感知/分类能力"，不是"持续自我"。

### 架构升级
```
当前: 784 → 10 (单层感知机) ❌
目标: 784 → Conv → Pool → Conv → Flatten → 10 (卷积SNN) ✅
```

### 任务清单
- [ ] 实现卷积SNN层
- [ ] 时间编码静态图像
- [ ] 复用STDP机制到视觉任务
- [ ] 达到>95%准确率

---

## P4: Persistent Agent Loop (6-8周)

**目标**: 72小时自主运行，自我维护

### 核心能力
1. **自我诊断**: 检测自身状态异常
2. **自我修复**: 主动调整参数/重启子系统
3. **长期目标**: 维护跨时间的任务一致性
4. **资源管理**: 自主管理计算资源

### 验证标准
- [ ] 72小时零崩溃
- [ ] 无人工干预
- [ ] 自我诊断日志
- [ ] 自我修复行为记录
- [ ] 能生成自我报告 (`who_am_i`)

---

## 🎯 优先级决策

### 现在不做 (推迟)
| 项目 | 原因 |
|------|------|
| ❌ 扩大神经元规模 (10K→100K) | 先解决self-model |
| ❌ 多GPU分片 | 等P4完成 |
| ❌ 数字达尔文生态 | 等单个agent稳定 |
| ❌ 哲学声称 | 先硬证据 |

### 现在做 (主主)
| 项目 | 优先级 |
|------|--------|
| ✅ P1: Self Kernel MVP | **最高** - 跨过agent门槛的关键 |
| ⚠️ P2: 真正自我维持 | 高 - 学习得来的生存策略 |
| ⏸️ P3: MNIST | 次线 - 感知能力非核心目标 |

---

## 📊 里程碑定义

| 里程碑 | 验证标准 | 代码证据 | 运行证据 |
|--------|----------|----------|----------|
| v2.2-self-mvp | 4个Self Kernel验证点通过 | `self_kernel/mod.rs` | `who_am_i()`输出 |
| v2.3-self-preservation | 学习得来的生存策略 | `learned_preservation.rs` | 自适应阈值日志 |
| v2.4-mnist | MNIST >95% | `conv_snn.rs` | 测试准确率 |
| v2.5-agent | 72小时自主运行 | N/A | 无干预日志 |

---

*实用导向 - 先跑通最小Self Kernel，再扩展*
