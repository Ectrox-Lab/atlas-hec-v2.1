# DNA-Diffusion 分析总结与Rust重写规划

## 一、核心架构分析

### 1.1 系统组成

| 组件 | 功能 | 复杂度 |
|------|------|--------|
| **Diffusion** | 扩散过程核心（q_sample, p_sample, p_losses） | ⭐⭐⭐ |
| **UNet** | 噪声预测网络（time embedding + class embedding + UNet） | ⭐⭐⭐⭐ |
| **DataLoader** | 固定窗口数据加载（one-hot编码 + 条件标签） | ⭐⭐ |
| **Train Loop** | 训练流程（Hydra配置 + 早停 + checkpoint） | ⭐⭐⭐ |
| **Sampling** | 条件生成（classifier-free guidance） | ⭐⭐⭐ |

### 1.2 关键技术点

**Diffusion核心** (`diffusion.py`):
- 线性beta调度: `linear_beta_schedule(timesteps, beta_start, beta_end)`
- 前向加噪: `q_sample(x_start, t, noise)` 
- 反向去噪: `p_sample(x, t, t_index)`
- 条件引导: `p_sample_guided()` - classifier-free guidance实现
- 损失计算: `p_losses()` - Huber/L1/L2损失

**UNet架构** (`unet.py`):
- Time embedding: 正弦位置编码 + MLP
- Class embedding: nn.Embedding
- UNet结构: DownBlocks → Mid → UpBlocks + Skip connections
- Cross-attention: 用于条件关联

**数据流**:
```
Raw DNA (200bp) → One-hot (4×200) → Normalize (-1,1) → Diffusion Model → Generated Sequence
```

## 二、Code-DNA适配方案

### 2.1 三种Code-DNA表示

#### A. Opcode-DNA
```rust
// 低层IR指令序列
enum OpcodeToken {
    Load, Store, Add, Sub, Mul, Div,
    Branch, Call, Return, Alloc, Free,
    // ... 扩展指令集
}

// 固定窗口: 128 tokens
struct OpcodeDNA {
    tokens: [OpcodeToken; 128],
    condition: PatchType,  // bugfix/perf/safety
}
```

#### B. Edit-DNA (推荐先实现)
```rust
// Patch操作序列
enum EditToken {
    AddIf, RemoveCall, ChangeConst, InsertGuard,
    MoveAlloc, ReplaceLoop, WrapTry, AddTimeout,
    // 上下文token
    ContextBefore, ContextAfter, 
}

// 固定窗口: 64 tokens
struct EditDNA {
    tokens: [EditToken; 64],
    condition: PatchCategory,
}
```

#### C. Graph-DNA
```rust
// AST/CFG motif
enum GraphToken {
    LoopNode, BranchNode, CallNode, AssignNode,
    DataFlow, ControlFlow, Dependency,
}

// 固定窗口: 32-64 tokens
struct GraphDNA {
    tokens: [GraphToken; 48],
    condition: StructuralPattern,
}
```

### 2.2 条件标签设计

```rust
enum Condition {
    // 高层类别
    BugFix,
    Performance,
    Memory,
    Safety,
    Refactor,
    
    // 细粒度属性
    PassesTests,
    LatencyImproved,
    AllocReduced,
    DeadlockRiskReduced,
    StateMachineFix,
    
    // 模块家族
    ModuleConcurrency,
    ModuleIO,
    ModuleState,
}
```

## 三、Rust架构设计

### 3.1 项目结构

```
code-diffusion/
├── Cargo.toml
├── src/
│   ├── main.rs              # CLI入口
│   ├── lib.rs               # 库导出
│   ├── diffusion/
│   │   ├── mod.rs           # 扩散模块
│   │   ├── schedule.rs      # beta调度
│   │   ├── forward.rs       # q_sample
│   │   └── reverse.rs       # p_sample
│   ├── models/
│   │   ├── mod.rs
│   │   ├── unet.rs          # UNet架构
│   │   ├── embedding.rs     # time/class embedding
│   │   └── layers.rs        # ResNet/Attention层
│   ├── data/
│   │   ├── mod.rs
│   │   ├── tokenizer.rs     # Code-DNA tokenizer
│   │   ├── dataset.rs       # 数据集加载
│   │   └── loader.rs        # DataLoader
│   ├── training/
│   │   ├── mod.rs
│   │   ├── loop.rs          # 训练循环
│   │   ├── config.rs        # 配置管理
│   │   └── checkpoint.rs    # 检查点保存
│   ├── sampling/
│   │   ├── mod.rs
│   │   ├── generator.rs     # 候选生成
│   │   └── guidance.rs      # classifier-free guidance
│   └── verification/
│       ├── mod.rs
│       ├── decoder.rs       # DNA→Code解码
│       └── verifier.rs      # 验证器接口
├── configs/
│   └── default.yaml         # 训练配置
└── examples/
    └── edit_dna_train.rs    # 使用示例
```

### 3.2 核心 trait 设计

```rust
// 扩散模型接口
pub trait DiffusionModel {
    fn forward(&self, x: &Tensor, t: &Tensor, classes: &Tensor) -> Tensor;
    fn sample(&self, classes: &Tensor, shape: &[usize], cond_weight: f64) -> Vec<Tensor>;
}

// Code-DNA编码器
pub trait CodeDNAEncoder {
    type Token;
    fn encode(&self, code: &str) -> Vec<Self::Token>;
    fn decode(&self, tokens: &[Self::Token]) -> String;
    fn to_tensor(&self, tokens: &[Self::Token]) -> Tensor;
}

// 条件标签
pub trait ConditionLabel {
    fn to_tensor(&self) -> Tensor;
    fn num_classes() -> usize;
}

// 验证器
pub trait Verifier {
    fn verify(&self, code: &str) -> VerificationResult;
}
```

## 四、关键算法实现要点

### 4.1 扩散调度

```rust
// linear_beta_schedule
pub fn linear_beta_schedule(timesteps: usize, beta_start: f64, beta_end: f64) -> Vec<f64> {
    (0..timesteps)
        .map(|i| beta_start + (beta_end - beta_start) * i as f64 / (timesteps - 1) as f64)
        .collect()
}
```

### 4.2 Classifier-Free Guidance

```rust
// 核心公式: eps = (1 + w) * eps_cond - w * eps_uncond
// w = cond_weight
pub fn classifier_free_guidance(
    eps_cond: &Tensor,
    eps_uncond: &Tensor,
    cond_weight: f64,
) -> Tensor {
    eps_cond * (1.0 + cond_weight) - eps_uncond * cond_weight
}
```

### 4.3 采样循环

```rust
pub fn p_sample_loop_guided(
    &self,
    classes: &Tensor,
    shape: &[usize],
    cond_weight: f64,
) -> Vec<Tensor> {
    let mut img = Tensor::randn(shape, (Kind::Float, Device::Cpu));
    let mut imgs = vec![];
    
    // 准备条件掩码用于classifier-free guidance
    let (classes_masked, context_mask) = self.prepare_guidance(classes);
    
    for t in (0..self.timesteps).rev() {
        let t_tensor = Tensor::full(&[shape[0]], t as i64, (Kind::Int64, Device::Cpu));
        
        // 预测噪声（条件和无条件）
        let eps = self.predict_noise_with_guidance(
            &img, &t_tensor, &classes_masked, &context_mask, cond_weight
        );
        
        // 计算均值
        let model_mean = self.compute_mean(&img, &eps, t);
        
        // 添加噪声（除了最后一步）
        img = if t > 0 {
            let noise = Tensor::randn_like(&img);
            let posterior_var = self.extract_posterior_variance(t);
            model_mean + posterior_var.sqrt() * noise
        } else {
            model_mean
        };
        
        imgs.push(img.shallow_clone());
    }
    
    imgs
}
```

## 五、与超脑系统集成

### 5.1 组件定位

```
超脑架构:
├── 主控制器 (已有)
├── 记忆系统 (已有)
├── 实验执行器 (已有)
├── Code-DNA Diffusion (新增) ← 底层候选生成器
│   ├── 生成器: 扩散模型
│   ├── 解码器: DNA→Code
│   └── 验证器: 过滤层
└── Verifier Stack (已有/扩展)
```

### 5.2 数据流

```
超脑控制器 → 生成任务 → Code-Diffusion
                          ↓
                    生成N个候选DNA
                          ↓
                    解码器 → Patch/Code
                          ↓
                    Verifier Stack
                          ↓
                    通过候选 → 返回超脑
```

### 5.3 接口定义

```rust
// 超脑集成接口
pub struct CodeDNAComponent {
    diffusion: Diffusion,
    unet: UNet,
    decoder: Box<dyn DNADecoder>,
    verifiers: Vec<Box<dyn Verifier>>,
}

impl CodeDNAComponent {
    /// 生成候选补丁
    pub fn generate_candidates(
        &self,
        context: &CodeContext,
        condition: Condition,
        num_samples: usize,
        guidance_scale: f64,
    ) -> Vec<VerifiedCandidate> {
        // 1. 编码上下文
        let class_tensor = condition.to_tensor();
        
        // 2. 生成DNA序列
        let dna_samples = self.diffusion.sample(
            &class_tensor,
            &[num_samples, CHANNELS, SEQ_LEN],
            guidance_scale,
        );
        
        // 3. 解码为代码
        let candidates: Vec<_> = dna_samples.iter()
            .map(|dna| self.decoder.decode(dna))
            .collect();
        
        // 4. 验证过滤
        candidates.into_iter()
            .filter(|c| self.verify(c).is_pass())
            .collect()
    }
}
```

## 六、实施路线图

### Phase 1: 最小可行原型 (MVP)
- [ ] 实现线性扩散调度
- [ ] 实现简化的UNet (2-3层)
- [ ] 实现Edit-DNA tokenizer
- [ ] 训练脚本框架
- [ ] 采样脚本

**时间**: 1-2周  
**验证**: 能在小规模数据上收敛

### Phase 2: 功能完备版
- [ ] 完整UNet架构
- [ ] Classifier-free guidance
- [ ] 三种Code-DNA支持
- [ ] Hydra配置系统
- [ ] Checkpoint管理

**时间**: 2-3周  
**验证**: 生成质量与Python版相当

### Phase 3: 超脑集成
- [ ] 定义集成接口
- [ ] 实现Verifier Stack
- [ ] 性能优化 (批处理/并行)
- [ ] 与E-class/001系统联动

**时间**: 1-2周  
**验证**: 端到端工作流

## 七、关键取舍

### 保留 (必须实现)
- ✅ 扩散核心算法 (q_sample, p_sample)
- ✅ Classifier-free guidance
- ✅ UNet架构 (可简化)
- ✅ 条件标签系统
- ✅ 固定窗口表示

### 简化 (第一版可弱化)
- ⚠️ Cross-attention (可用更简单attention)
- ⚠️ 分布式训练 (先单卡)
- ⚠️ Wandb集成 (先日志文件)
- ⚠️ 复杂数据增强

### 新增 (Code-DNA特有)
- 🆕 多种Code tokenizer
- 🆕 Verifier接口
- 🆕 超脑集成层
- 🆕 批量生成优化

## 八、预期成果

### 短期 (4-6周)
- 可用的Rust Code-Diffusion库
- 能生成Edit-DNA候选
- 基本验证流程

### 中期 (8-12周)
- 三种Code-DNA支持
- 与超脑系统深度集成
- 大量生成+验证流水线

### 长期 (3-6月)
- 成为超脑底层候选生成器
- 支持A1×A5/E-class实验
- 自适应条件生成

---

**下一步**: 开始Phase 1 MVP实现
