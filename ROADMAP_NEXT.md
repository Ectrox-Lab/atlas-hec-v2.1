# ROADMAP_NEXT.md - 下一阶段工程路线图

> 只写未来2-3个阶段，实用导向，不哲学化

---

## P0: 项目记忆固定 (IMMEDIATE - 1-2周)

**目标**: 建立不会失忆的研究系统

### 任务清单
- [x] 创建PROJECT_STATE.md (已完成)
- [x] 创建CLAIMS_REGISTRY.md (已完成)
- [ ] 创建REPRO_COMMANDS.md (正在进行)
- [ ] 建立实验命名规范
- [ ] 建立自动保存结果流程
- [ ] 每个milestone留下可回放证据

### 产出
- 4个核心文档固定
- 所有实验可复现
- 不再依赖"截图+记忆"

---

## P1: Self Kernel v0.1 (2-4周)

**目标**: 添加internal reference `this_is_me`

### 核心模块

```rust
// 1. SelfState - 自我状态结构
struct SelfState {
    identity: String,              // "atlas-v2.3-instance-001"
    creation_time: Timestamp,
    current_goals: Vec<Goal>,      // 自主目标
    capabilities: Vec<Skill>,      // 能力清单
    memory_index: MemoryIndex,     // 记忆索引
    self_model: WorldModel,        // 自我在世界中的模型
    runtime_metrics: RuntimeMetrics, // 运行指标
}

// 2. AutobiographicalMemory - 自传体记忆
struct AutobiographicalMemory {
    episodes: Vec<Episode>,        // 时间序列事件
    consolidation: Consolidation,  // 记忆固化
    retrieval: Retrieval,          // 检索机制
}

// 3. MetaController - 元控制器
struct MetaController {
    self_state: SelfState,
    memory: AutobiographicalMemory,
    preservation_drive: PreservationDrive, // 自我维持驱动
}

// 4. SelfReportInterface - 自我报告接口
impl SelfReportInterface {
    fn who_am_i(&self) -> String;  // 回答"你是谁"
    fn what_am_i_doing(&self) -> String;
    fn what_have_i_learned(&self) -> String;
}
```

### 关键验证点
- [ ] 系统能引用自己的历史 ("Yesterday I...")
- [ ] 系统能报告自己的状态
- [ ] 系统能评估过去行为
- [ ] 存在`this_is_me`神经元/节点激活

---

## P2: 真正自我维持 (4-6周)

**目标**: 将硬编码规则变为学习得来的生存策略

### 当前问题
```rust
// 硬编码 (v2.1)
if adenosine_level > 0.6 {
    enter_rem(); // 硬编码阈值
}
```

### 目标
```rust
// 学习得来 (v2.3)
let survival_value = self_model.predict(
    "if I continue at this load, what happens to me?"
);
if survival_value < threshold {
    self.preserve(); // 学习得来的自我保护
}
```

### 任务清单
- [ ] 实现`avoid_self_damage`学习
- [ ] 实现`maintain_internal_state`策略
- [ ] 实现`repair_subsystems`机制
- [ ] 验证：生存策略是学来的，不是硬编码的

---

## P3: MNIST认证重试 (并行 - 3-4周)

**目标**: 卷积SNN架构，>95%准确率

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
- [ ] 自我维护行为可被观察
- [ ] 能生成自我报告 (who_am_i)

---

## 🎯 优先级决策

**现在不做**:
- ❌ 扩大神经元规模 (10K→100K) - 先解决self-model
- ❌ 多GPU分片 - 等P4完成
- ❌ 数字达尔文生态 - 等单个agent稳定
- ❌ 哲学声称 - 先硬证据

**现在做**:
- ✅ P0: 项目记忆固定 (防止再次失忆)
- ✅ P1: Self Kernel v0.1 (跨过agent门槛的关键)
- ⚠️ P3: MNIST并行 (验证通用性)

---

## 📊 里程碑定义

| 里程碑 | 标准 | 验证方式 |
|--------|------|----------|
| v2.2-memory | 4个文档+可复现实验 | 任何人可重跑实验 |
| v2.3-self | SelfState存在+可报告 | 系统能回答"你是谁" |
| v2.4-alive | 真正自我维持 | 学习得来的生存策略 |
| v2.5-agent | 72小时自主运行 | 无人工干预日志 |

---

*实用导向 - 不追求"最大"，追求"不会失忆的下一步"*
