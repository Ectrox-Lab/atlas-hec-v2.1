# Atlas-HEC v2.1 Project Rules

> **Version**: 2.1  
> **Status**: ACTIVE  
> **Effective**: 2026-03-15

---

## Hard Rule 1: No Publication ( Until Conditions Met )

### 当前状态
**🚫 禁止发表论文**

Atlas-HEC v2.1 已完成 L4→L5→L6 完整验证，但**现阶段禁止任何形式的论文发表**。

### 发表条件（必须全部满足）

发表前必须完成以下前置条件：

| 条件 | 状态 | 完成标准 |
|:-----|:----:|:---------|
| **超脑挂载显卡** | ⏸️ PENDING | 核心计算模块可调用GPU加速 |
| **异构架构完善** | ⏸️ PENDING | CPU+GPU同时满载的专用架构 |
| **主流SOTA测评** | ⏸️ PENDING | 完成所有主流AI智能模型对比测试 |

### 允许的行为
- ✅ 内部文档记录
- ✅ Git版本控制
- ✅ ArXiv预印本（仅作为技术备份，不主动推广）
- ✅ 技术博客（概念性介绍，无学术声称）

### 禁止的行为
- ❌ 向ICML/NeurIPS/ICLR等会议投稿
- ❌  claiming 学术原创性发表
- ❌  媒体宣传"突破性成果"

### 条件满足后的流程
```
超脑挂载显卡        ✓
    ↓
异构架构完善        ✓
    ↓
主流SOTA测评完成    ✓
    ↓
重新评估发表可行性
    ↓
[可选] 提交论文
```

---

## Hard Rule 2: 1-Hour Experiment Limit

### 绝对约束
**任何单次实验不得超过现实时间 1 小时。**

### 执行机制
```yaml
ralph_window_gate:
  timeout: 3600  # 秒
  action_on_timeout: FORCE_STOP
  logging: required
  
experiment_design:
  max_windows_per_batch: 10
  max_duration_per_window: 360s  # 6分钟，确保10窗口<1小时
  checkpoint_frequency: every_window
```

### 例外情况
无例外。即使是：
- 最终验证实验
- 大规模消融研究
- 对比基准测试

**所有实验必须可在1小时内完成或分段完成。**

---

## Hard Rule 3: Architecture-First Priority

### 当前优先事项
项目资源优先投入：

| 优先级 | 事项 | 状态 |
|:------:|:-----|:----:|
| P0 | 超脑显卡挂载 | 🔄 IN PROGRESS |
| P0 | CPU+GPU异构架构 | 🔄 IN PROGRESS |
| P1 | 主流SOTA测评框架 | ⏸️ QUEUED |
| P2 | 论文发表评估 | 🚫 BLOCKED |

### 禁止的资源分配
- ❌ 为论文写作投入>10%时间
- ❌ 为美化图表投入>5%时间
- ❌ 为投稿准备投入>0%时间（直到条件满足）

---

## Hard Rule 4: Sole Reference Maintained

继续使用 **Sole Reference Principle**：
> 进度以自我历史轨迹为参照，而非外部基准。

### 当前参照系
```
L4: 18.7pp Control Gap ✅
L5: 9.34pp Mean Transfer, 6/6 pairs ✅
L6: Tier 2 Match, learned=heuristic ✅
```

**未来参照**（架构完成后）：
```
GPU加速后的性能基准
异构架构效率指标
SOTA对比结果
```

---

## 当前执行指令

### 立即执行
1. **冻结Publication Package**
   ```bash
   git tag publication-frozen-v1.0 d2a8064
   # 标记完成但不发布
   ```

2. **转向架构开发**
   ```bash
   mkdir -p architecture/{gpu_integration,heterogeneous,sota_benchmark}
   # 开始P0优先级任务
   ```

3. **维持1小时纪律**
   ```bash
   # 所有后续实验继续遵守Ralph Window 3600s限制
   ```

---

## 违反后果

- 超过1小时的实验：**自动强制停止，结果废弃**
- 提前发表论文：**项目冻结，回滚至L5状态**
- 资源错配：**重新分配，违规者移除项目权限**

---

## 签署

**项目约束已更新，所有团队成员必须遵守。**

- 不发论文（直到三大条件满足）
- 实验≤1小时（绝对）
- 架构优先（GPU挂载+异构完善）
- Sole Reference（自我参照验证）

---

*Atlas-HEC v2.1 Project Rules - Architecture First, Publication Later*
