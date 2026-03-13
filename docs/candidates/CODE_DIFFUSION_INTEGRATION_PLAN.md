# Code-DNA Diffusion 集成方案

## 1. 系统定位

### 在超脑架构中的位置

```
┌─────────────────────────────────────────────────────────────┐
│                    超脑主控制器                              │
├─────────────────────────────────────────────────────────────┤
│  记忆系统  │  实验执行器  │  Code-DNA Diffusion (新增)      │
│            │              │  ├── 生成器                     │
│            │              │  ├── 解码器                     │
│            │              │  └── 验证器                     │
├─────────────────────────────────────────────────────────────┤
│                    Verifier Stack                           │
│  (语法检查/类型检查/测试/性能/安全)                           │
└─────────────────────────────────────────────────────────────┘
```

### 与现有组件的关系

| 现有组件 | 与Code-DNA关系 | 数据流 |
|----------|---------------|--------|
| **E-class** | 候选生成器 | E-class生成实验配置 → Code-DNA生成补丁 |
| **001** | Patch诊断 | 001标记问题 → Code-DNA生成修复 |
| **D1** | 评估框架 | Code-DNA生成候选 → D1 paired-seed评估 |
| **Verifier** | 下游过滤 | Code-DNA输出 → Verifier Stack验证 |

## 2. 集成接口

### 2.1 核心接口定义

```rust
/// 超脑集成接口
pub trait HyperbrainIntegration {
    /// 接收实验任务，生成候选
    fn generate_for_experiment(
        &self,
        experiment: &ExperimentConfig,
        num_candidates: usize,
    ) -> Vec<VerifiedCandidate>;
    
    /// 接收001诊断结果，生成修复
    fn generate_fixes(
        &self,
        diagnosis: &DiagnosisResult,
        num_variants: usize,
    ) -> Vec<VerifiedPatch>;
    
    /// 报告生成统计
    fn report_stats(&self) -> GenerationStats;
}

/// 实验配置
pub struct ExperimentConfig {
    pub experiment_type: ExperimentType,  // E1/E2/001/etc
    pub target_condition: Condition,      // bugfix/perf/etc
    pub constraints: Vec<Constraint>,     // 安全/性能要求
    pub context: CodeContext,             // 代码上下文
}

/// 验证候选
pub struct VerifiedCandidate {
    pub dna: EditDNA,
    pub patch: String,
    pub verification: VerificationResult,
    pub metadata: CandidateMetadata,
}
```

### 2.2 与E-class集成

```rust
// E-class生成临界实验配置
let experiment = ExperimentConfig {
    experiment_type: ExperimentType::CriticalCoupling,
    target_condition: Condition::Performance,
    constraints: vec![Constraint::LatencyImproved, Constraint::NoDeadlock],
    context: load_context("e1_phase_b_config.rs"),
};

// Code-DNA生成优化补丁
code_dna.generate_for_experiment(&experiment, 128);
```

### 2.3 与001集成

```rust
// 001诊断fixed-marker问题
let diagnosis = DiagnosisResult {
    problem: ProblemType::FixedMarkerHarmful,
    location: "marker.rs:45",
    severity: Severity::High,
};

// Code-DNA生成dynamic-marker修复
let fixes = code_dna.generate_fixes(&diagnosis, 64);

// 通过D1 paired-seed评估
let evaluated = d1_framework.evaluate_paired(&fixes);
```

## 3. 数据流设计

### 3.1 生成流程

```
超脑控制器
    ↓ 发送生成任务
Code-DNA Diffusion
    ├─→ 编码上下文 → Edit-DNA格式
    ├─→ 条件标签 → bugfix/perf/safety
    ├─→ 扩散模型 → 生成N个候选
    ├─→ 解码器 → Patch格式
    ↓ 批量验证
Verifier Stack
    ├─→ 语法检查
    ├─→ 类型检查
    ├─→ 单元测试
    ├─→ 性能测试
    └─→ 安全检查
    ↓ 返回通过的候选
超脑控制器 ← 候选列表
```

### 3.2 反馈循环

```
Verifier结果
    ↓
生成质量统计
    ↓
调整guidance_scale
    ↓
重新生成
    ↓
更精准候选
```

## 4. 实施计划

### Phase 1: 核心实现 (2-3周)

**Week 1**: 扩散核心
- [ ] Diffusion算法完整实现
- [ ] UNet架构（简化版）
- [ ] Edit-DNA tokenizer

**Week 2**: 生成与验证
- [ ] Sampling with guidance
- [ ] Patch decoder
- [ ] Verifier接口

**Week 3**: 集成测试
- [ ] 与超脑控制器联调
- [ ] 端到端流程验证
- [ ] 性能基准测试

### Phase 2: 功能增强 (2-3周)

**Week 4-5**: 完整UNet
- [ ] ResNet blocks
- [ ] Attention机制
- [ ] Cross-attention

**Week 6**: 训练系统
- [ ] 训练脚本
- [ ] Checkpoint管理
- [ ] Hydra配置

### Phase 3: 深度集成 (2周)

**Week 7**: E-class联动
- [ ] 实验配置自动生成
- [ ] 结果反馈集成

**Week 8**: 001联动
- [ ] 诊断-修复闭环
- [ ] D1评估集成

## 5. 资源规划

### 计算资源

| 任务 | CPU | 内存 | GPU | 时间 |
|------|-----|------|-----|------|
| 模型训练 | 16核 | 64GB | 1x A100 | 4-8小时 |
| 批量生成 | 8核 | 16GB | - | 分钟级 |
| 验证 | 4核 | 8GB | - | 秒级 |

### 存储需求

- 模型检查点: ~500MB
- 训练数据: ~1GB
- 生成缓存: ~100MB

## 6. 风险评估

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 生成质量不达标 | 中 | 高 | 从简单patch开始，逐步复杂化 |
| 训练时间过长 | 中 | 中 | 使用预训练权重，迁移学习 |
| 集成复杂度超预期 | 低 | 高 | 早期原型验证接口 |

### 缓解策略

1. **MVP优先**: 先实现简化版，验证端到端流程
2. **预训练**: 调研使用现有code model权重
3. **渐进增强**: 从Edit-DNA开始，逐步增加Opcode/Graph

## 7. 验收标准

### Phase 1 验收

- [ ] 能生成可编译的patch
- [ ] 通过基础语法验证
- [ ] 与超脑控制器成功通信

### Phase 2 验收

- [ ] 生成质量接近Python版
- [ ] 支持条件引导
- [ ] 训练流程完整

### Phase 3 验收

- [ ] E-class实验自动生成补丁
- [ ] 001诊断自动修复
- [ ] 成为超脑标准组件

## 8. 下一步行动

### 立即开始 (今天)

1. **完善扩散核心**
   - 实现完整的q_sample/p_sample
   - 添加测试覆盖

2. **创建训练脚本框架**
   - 数据加载器
   - 训练循环
   - 配置系统

3. **准备训练数据**
   - 从历史patch提取Edit-DNA
   - 标注条件标签

### 本周目标

- [ ] 可运行的训练脚本
- [ ] 基础采样功能
- [ ] 与超脑接口对接

---

**文档版本**: v1.0  
**创建时间**: 2026-03-11  
**关联**: DNA_DIFFUSION_ANALYSIS_SUMMARY.md
