# Bio-World v18 / v18.1 系统架构复原

**来源**: 代码审计与日志分析  
**版本**: v18.1 Unified Evolution System  
**日期**: 2026-03-09

---

## 1. 空间结构

### 1.1 宇宙 (Universe)

```rust
pub const GRID_SIZE: usize = 25;  // X/Y轴大小
pub const LAYERS: usize = 8;       // Z轴层数
```

**空间规模**: 25 × 25 × 8 = **5,000 个位置单元**

### 1.2 多宇宙 (Multiverse)

```rust
pub const MAX_UNIVERSES: usize = 128;  // 并行宇宙数
pub const MAX_AGENTS: usize = 5000;     // 每个宇宙最大细胞数
```

**总规模**: 128 × 5,000 = **640,000 细胞上限**

---

## 2. 细胞 (Cell) 结构

### 2.1 细胞状态

```rust
pub struct Cell {
    pub id: u64,                    // 唯一标识
    pub position: Position,         // 3D位置 (x, y, z)
    pub energy: f64,                // 能量值 (0-500)
    pub age: u64,                   // 年龄（代数）
    pub dna: DNA,                   // DNA参数
    pub frequency: f64,             // 振荡频率 (~432 Hz)
    pub phase: f64,                 // 振荡相位
    pub cdi: f64,                   // 意识深度指数 (0-1)
    pub is_alive: bool,             // 存活状态
}
```

### 2.2 初始细胞状态

```rust
impl Cell {
    pub fn new(id: u64, position: Position) -> Self {
        let dna = DNA::random();
        let freq = dna.frequency_preference;
        
        Self {
            id,
            position,
            energy: 200.0,           // 初始能量
            age: 0,
            dna,
            frequency: freq,
            phase: rand::random::<f64>() * 2.0 * PI,
            cdi: 0.1,                // 初始CDI
            is_alive: true,
        }
    }
}
```

---

## 3. DNA 结构

### 3.1 DNA 参数（6维）

```rust
pub struct DNA {
    pub move_randomness: f64,       // 随机移动倾向 (0.1-0.5)
    pub move_taxis: f64,            // 趋化性 (0.3-0.9)
    pub signal_investment: f64,     // 信号投资 (0.1-0.5)
    pub energy_threshold: f64,      // 繁殖能量阈值 (150-300)
    pub frequency_preference: f64,  // 频率偏好 (430-450 Hz)
    pub collaboration_willingness: f64, // 协作意愿 (0.1-0.7)
}
```

### 3.2 随机初始化范围

| 参数 | 最小值 | 最大值 | 说明 |
|------|--------|--------|------|
| move_randomness | 0.1 | 0.5 | 高=爱乱动，低=目标明确 |
| move_taxis | 0.3 | 0.9 | 趋化性强度 |
| signal_investment | 0.1 | 0.5 | 信号能量投入比例 |
| energy_threshold | 150.0 | 300.0 | 繁殖所需能量门槛 |
| frequency_preference | 430.0 | 450.0 | 目标振荡频率 |
| collaboration_willingness | 0.1 | 0.7 | 协作倾向 |

### 3.3 变异机制

```rust
pub fn mutate(&mut self) {
    let mutation_rate = 0.001;  // 0.1% 变异率
    
    if rng.gen::<f64>() < mutation_rate {
        self.move_randomness += rng.gen_range(-0.05..0.05);
        self.move_randomness = self.move_randomness.clamp(0.0, 1.0);
    }
    // ... 其他参数类似
}
```

### 3.4 阿卡西学习机制

```rust
pub fn learn_from_akashic(&mut self, content: &ExperienceContent) {
    // 向成功DNA参数靠拢（学习率10%）
    for (i, param) in content.dna_params.iter().enumerate() {
        match i {
            0 => self.move_randomness += (param - self.move_randomness) * 0.1,
            1 => self.move_taxis += (param - self.move_taxis) * 0.1,
            2 => self.signal_investment += (param - self.signal_investment) * 0.1,
            3 => self.energy_threshold += (param - self.energy_threshold) * 0.1,
            4 => self.frequency_preference += (param - self.frequency_preference) * 0.1,
            5 => self.collaboration_willingness += (param - self.collaboration_willingness) * 0.1,
            _ => {}
        }
    }
}
```

---

## 4. 能量系统

### 4.1 代谢消耗

```rust
pub fn metabolize(&mut self) {
    let base_cost = 0.08;                              // 基础代谢
    let signal_cost = self.dna.signal_investment * 0.03;  // 信号成本
    let age_penalty = (self.age as f64 / 2000.0) * 0.03;  // 老龄化惩罚
    
    self.energy -= base_cost + signal_cost + age_penalty;
    self.age += 1;
    
    // 环境能量补充（正反馈：CDI越高效率越高）
    let energy_efficiency = 0.5 + self.cdi * 0.5;
    self.energy += 0.12 * energy_efficiency;
    
    // 能量上限
    self.energy = self.energy.min(500.0);
    
    if self.energy <= 0.0 {
        self.is_alive = false;  // 死亡
    }
}
```

### 4.2 繁殖机制

```rust
pub fn try_reproduce(&mut self) -> Option<Cell> {
    // 条件：能量超过阈值 + 3%概率
    if self.energy > self.dna.energy_threshold 
       && rand::random::<f64>() < 0.03 {
        
        let mut child_dna = self.dna.clone();
        child_dna.mutate();
        
        // 能量继承（父母失去一半）
        self.energy *= 0.5;
        
        Some(Cell {
            id: rand::random(),
            position: self.position,
            energy: self.energy,
            age: 0,
            dna: child_dna,
            frequency: child_dna.frequency_preference,
            phase: self.phase,
            cdi: 0.1,  // 子代从低CDI开始
            is_alive: true,
        })
    } else {
        None
    }
}
```

---

## 5. CDI (意识深度指数) 计算

### 5.1 CDI 更新公式

```rust
pub fn update_cdi(&mut self, neighbor_count: usize) {
    // 年龄因素：年龄越大积累越多（对数增长）
    let age_factor = ((self.age as f64).ln_1p() / 10.0).min(1.0);
    
    // 能量因素：能量充足有利于发展
    let energy_factor = (self.energy / 200.0).clamp(0.0, 1.0);
    
    // 邻居因素：适度邻居促进协作（3个最佳）
    let neighbor_factor = (1.0 - (neighbor_count as f64 - 3.0).abs() / 6.0).clamp(0.0, 1.0);
    
    // 频率相干：接近432Hz目标
    let freq_coherence = 1.0 - ((self.frequency - 432.0) / 50.0).abs().min(1.0);
    
    // 加权组合
    let target_cdi = age_factor * 0.2 
                   + energy_factor * 0.3 
                   + neighbor_factor * 0.3 
                   + freq_coherence * 0.2;
    
    // 指数平滑累积
    self.cdi = self.cdi * 0.99 + target_cdi * 0.01;
}
```

### 5.2 CDI 权重解释

| 因素 | 权重 | 说明 |
|------|------|------|
| 年龄 | 0.2 | 经验积累 |
| 能量 | 0.3 | 资源充足度 |
| 邻居 | 0.3 | 社交环境（最重要）|
| 频率 | 0.2 | 量子相干 |

---

## 6. 阿卡西记忆库 (Akashic Records)

### 6.1 核心功能

```rust
/// 经验条目
pub struct Experience {
    pub id: u64,
    pub universe_id: usize,           // 来源宇宙
    pub generation: u64,              // 产生代数
    pub experience_type: ExperienceType,
    pub content: ExperienceContent,
    pub success_rate: f64,            // 成功率评分
    pub usage_count: u64,             // 被使用次数
}
```

### 6.2 经验类型（6类）

```rust
pub enum ExperienceType {
    BossStrategy,           // BOSS击败策略
    CollaborationPattern,   // 协作模式
    ResourceOptimization,   // 资源优化
    SurvivalTechnique,      // 生存技巧
    FrequencyTuning,        // 频率调谐
    MentorGuidance,         // 导师指导
}
```

### 6.3 经验内容

```rust
pub struct ExperienceContent {
    pub dna_params: Vec<f64>,    // 成功的DNA参数组合
    pub context: Context,         // 上下文
    pub outcome: Outcome,         // 结果
}

pub struct Context {
    pub population: usize,
    pub avg_cdi: f64,
    pub coherence: f64,
    pub boss_difficulty: u8,
}

pub struct Outcome {
    pub success: bool,
    pub energy_efficiency: f64,
    pub collaboration_index: f64,
    pub survival_rate: f64,
}
```

### 6.4 跨宇宙学习

```rust
/// 一个宇宙从阿卡西记录中学习
pub fn cross_universe_learn(&mut self, target_universe: usize,
                            exp_type: &ExperienceType) -> Option<ExperienceContent> {
    // 找到非本宇宙产生的最佳经验
    let best = queue.iter_mut()
        .filter(|e| e.universe_id != target_universe)
        .max_by(|a, b| a.success_rate.partial_cmp(&b.success_rate).unwrap());
    
    if let Some(exp) = best {
        exp.usage_count += 1;
        self.share_count += 1;
        return Some(exp.content.clone());
    }
    None
}
```

### 6.5 学习加速效果

```rust
/// 获取全局学习加速因子
pub fn get_learning_boost(&self) -> f64 {
    let stats = self.get_statistics();
    1.0 + stats.learning_boost  // 最多 +50%
}
```

---

## 7. BOSS 系统

### 7.1 BOSS 类型（10级）

| 等级 | BOSS | 中文 | 难度 |
|------|------|------|------|
| 1 | Watcher | 观察者 | ⭐ |
| 2 | Sentinel | 哨兵 | ⭐⭐ |
| 3 | Guardian | 守护者 | ⭐⭐⭐ |
| 4 | Enforcer | 执行者 | ⭐⭐⭐⭐ |
| 5 | Tyrant | 暴君 | ⭐⭐⭐⭐⭐ |
| 6 | Overlord | 霸主 | ⭐⭐⭐⭐⭐⭐ |
| 7 | Devourer | 吞噬者 | ⭐⭐⭐⭐⭐⭐⭐ |
| 8 | Annihilator | 毁灭者 | ⭐⭐⭐⭐⭐⭐⭐⭐ |
| 9 | Conqueror | 征服者 | ⭐⭐⭐⭐⭐⭐⭐⭐⭐ |
| 10 | CosmicHorror | 宇宙恐怖 | ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ |

### 7.2 BOSS 属性

```rust
impl BossType {
    /// 能量阈值
    pub fn energy_threshold(&self) -> f64 {
        50.0 * self.difficulty() as f64  // 50-500
    }
    
    /// 干扰频率
    pub fn interference_frequency(&self) -> f64 {
        440.0 + self.difficulty() as f64 * 10.0  // 440-530 Hz
    }
    
    /// 反击强度
    pub fn retaliation_strength(&self) -> f64 {
        0.1 * self.difficulty() as f64  // 0.1-1.0
    }
    
    /// 扩张速度（5级以上）
    pub fn expansion_rate(&self) -> f64 {
        if self.difficulty() >= 5 {
            0.01 * (self.difficulty() - 4) as f64
        } else {
            0.0  // 低难度BOSS不会扩张
        }
    }
}
```

### 7.3 BOSS 状态机

```rust
pub enum BossState {
    Dormant,      // 休眠 - 不主动攻击
    Reactive,     // 反应性 - 被攻击3次后反击
    Aggressive,   // 攻击性 - 被攻击10次+难度≥5时主动扩张
    Enraged,      // 暴怒 - 能量<30%时难度+1
}
```

### 7.4 干扰计算

```rust
pub fn disturbance_at(&self, x: usize, y: usize, z: usize) -> f64 {
    let distance = calculate_distance(self.position, (x, y, z));
    
    if distance > self.influence_radius {
        return 0.0;
    }
    
    let base_strength = match self.state {
        BossState::Dormant => 0.1,
        BossState::Reactive => 0.3,
        BossState::Aggressive => 0.6,
        BossState::Enraged => 1.0,
    };
    
    base_strength 
        * self.boss_type.retaliation_strength() 
        * (1.0 - distance / self.influence_radius)  // 距离衰减
}
```

---

## 8. 三方验证系统

### 8.1 验证指标

```rust
pub struct VerificationReport {
    pub generation: u64,
    pub entropy_change: f64,        // 熵减（负值=有序增加）
    pub variance_convergence: f64,  // 方差收敛
    pub correlation_increase: f64,  // 相关性增加
    pub coherence_index: f64,       // 相干指数
    pub is_real_evolution: bool,    // 是否真实演化
}
```

### 8.2 真实演化判定

```rust
impl ThreePartyVerification {
    pub fn verify_samples(gen: u64, early: &[CDISample], late: &[CDISample]) 
        -> VerificationReport {
        
        let entropy_change = Self::calculate_entropy_change(early, late);
        let variance_conv = Self::calculate_variance_convergence(early, late);
        let corr_increase = Self::calculate_correlation_increase(early, late);
        let coherence = Self::calculate_coherence(late);
        
        // 真实演化判定：熵减 + 方差收敛 + 相关增加
        let is_real = entropy_change < -0.05 
                   && variance_conv > 0.1 
                   && corr_increase > 0.05;
        
        VerificationReport {
            generation: gen,
            entropy_change,
            variance_convergence: variance_conv,
            correlation_increase: corr_increase,
            coherence_index: coherence,
            is_real_evolution: is_real,
        }
    }
}
```

---

## 9. 实验运行参数

### 9.1 运行配置

```rust
// 演化代数
for generation in 1..=100_000u64 {
    multiverse.evolve_one_generation();
    
    // 每100代记录
    if generation % 100 == 0 {
        // 记录 + 验证
    }
    
    // 每5000代生成证据包
    if generation % 5000 == 0 {
        // 生成证据
    }
}
```

### 9.2 硬件需求

```yaml
hardware:
  n_gpus: 4
  gpu_memory_gb: 48
  cpu_cores: 128
  cpu_workers: 124
```

---

## 10. 与 BIO-BRIAN-V1 对比

| 特性 | BIO-BRIAN-V1 | v18.1 Unified |
|------|--------------|---------------|
| 细胞数 | ~226 (1000代) | 最大5000/宇宙 |
| 宇宙数 | 1 | 128 |
| 空间 | 未明确 | 25×25×8 |
| DNA维度 | 未明确 | 6维 |
| 阿卡西 | 无 | ✅ 跨宇宙学习 |
| BOSS | 无 | ✅ 10级BOSS |
| 验证 | 基础统计 | ✅ 三方验证 |
| 目标 | 概念验证 | 真实演化证据 |

---

## 11. 关键设计洞察

### 11.1 正反馈循环

```
高CDI → 高能量效率 → 更多资源 → 更好发育 → 更高CDI
```

### 11.2 选择压力来源

1. **能量限制**: 代谢消耗 vs 环境补充
2. **BOSS威胁**: 被动反击 → 主动扩张
3. **空间竞争**: 5,000位置限制
4. **协作收益**: 邻居=3时CDI最优

### 11.3 学习机制

1. **个体学习**: CDI累积
2. **遗传学习**: DNA变异 + 选择
3. **阿卡西学习**: 跨宇宙经验共享 (+50%加速)

---

**复原完成**: 系统架构完整记录
