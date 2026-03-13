//! 进化引擎
//! 
//! 基于阿卡西记录的结构统计，生成新一代的宇宙配置。
//! 不是遗传算法那种直接复制参数，而是学习"结构模式"。

use crate::{ParameterConfig, ArchitectureFamily, PlasticityFamily, BroadcastFamily, MemoryCoupling};
use crate::akashic_records::AkashicRecords;

/// 进化引擎
pub struct EvolutionEngine {
    /// 当前代
    pub generation: usize,
    
    /// 代际统计
    pub generation_stats: Vec<GenerationStats>,
    
    /// 进化策略
    pub strategy: EvolutionStrategy,
}

#[derive(Debug, Clone)]
pub struct GenerationStats {
    pub generation: usize,
    pub num_universes: usize,
    pub avg_score: f32,
    pub best_score: f32,
    pub pass_rate: f32,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum EvolutionStrategy {
    /// 随机探索（无方向）
    RandomExploration,
    
    /// 向成功模式靠拢
    SuccessBiased,
    
    /// 避免失败模式
    FailureAvoidance,
    
    /// 组合：成功+避免失败
    Combined,
    
    /// 自适应：根据进展调整策略
    Adaptive,
}

impl EvolutionEngine {
    pub fn new() -> Self {
        Self {
            generation: 0,
            generation_stats: Vec::new(),
            strategy: EvolutionStrategy::Combined,
        }
    }
    
    /// 基于阿卡西记录生成新一代
    pub fn generate_next_generation(
        &mut self,
        akashic: &AkashicRecords,
        population_size: usize,
    ) -> Vec<ParameterConfig> {
        self.generation += 1;
        
        let configs = match self.strategy {
            EvolutionStrategy::RandomExploration => {
                self.random_generation(population_size)
            }
            EvolutionStrategy::SuccessBiased => {
                self.success_biased_generation(akashic, population_size)
            }
            EvolutionStrategy::FailureAvoidance => {
                self.failure_avoidance_generation(akashic, population_size)
            }
            EvolutionStrategy::Combined => {
                self.combined_generation(akashic, population_size)
            }
            EvolutionStrategy::Adaptive => {
                self.adaptive_generation(akashic, population_size)
            }
        };
        
        // 记录这一代统计
        let stats = self.compute_generation_stats(akashic);
        self.generation_stats.push(stats);
        
        configs
    }
    
    /// 随机生成（基线）
    fn random_generation(&self, n: usize) -> Vec<ParameterConfig> {
        use crate::parameter_space::ParameterSpace;
        ParameterSpace::full().random_sample(n)
    }
    
    /// 向成功模式靠拢
    fn success_biased_generation(
        &self,
        akashic: &AkashicRecords,
        n: usize,
    ) -> Vec<ParameterConfig> {
        let mut configs = Vec::with_capacity(n);
        
        // 从名人堂提取成功模式
        let hall_of_fame = &akashic.hall_of_fame;
        
        if hall_of_fame.is_empty() {
            return self.random_generation(n);
        }
        
        // 70% 基于成功模式变异
        for i in 0..(n * 7 / 10) {
            // 随机选择一个名人堂成员作为基础
            let base_idx = random_usize(hall_of_fame.len().min(10));
            let base_id = &hall_of_fame[base_idx].universe_id;
            
            // 找到对应配置
            if let Some(record) = akashic.universes.iter()
                .find(|u| &u.universe_id == base_id) {
                // 添加变异
                configs.push(self.mutate_config(&record.config, 0.1));
            }
        }
        
        // 30% 随机探索（保持多样性）
        configs.extend(self.random_generation(n - configs.len()));
        
        configs
    }
    
    /// 避免失败模式
    fn failure_avoidance_generation(
        &self,
        akashic: &AkashicRecords,
        n: usize,
    ) -> Vec<ParameterConfig> {
        let mut configs = Vec::with_capacity(n);
        let mut attempts = 0;
        
        while configs.len() < n && attempts < n * 10 {
            attempts += 1;
            
            // 生成随机配置
            let base = self.random_generation(1).pop().unwrap();
            
            // 检查是否与失败模式相似
            let is_similar_to_failure = self.check_similarity_to_failures(&base, akashic);
            
            if !is_similar_to_failure {
                configs.push(base);
            }
        }
        
        // 如果不够，补充随机
        if configs.len() < n {
            configs.extend(self.random_generation(n - configs.len()));
        }
        
        configs
    }
    
    /// 组合策略
    fn combined_generation(
        &self,
        akashic: &AkashicRecords,
        n: usize,
    ) -> Vec<ParameterConfig> {
        let mut configs = Vec::with_capacity(n);
        
        // 50% 成功偏向
        configs.extend(self.success_biased_generation(akashic, n / 2));
        
        // 30% 避免失败
        configs.extend(self.failure_avoidance_generation(akashic, n * 3 / 10));
        
        // 20% 随机探索
        configs.extend(self.random_generation(n - configs.len()));
        
        configs
    }
    
    /// 自适应策略
    fn adaptive_generation(
        &self,
        akashic: &AkashicRecords,
        n: usize,
    ) -> Vec<ParameterConfig> {
        // 根据历史进展选择策略
        if self.generation_stats.len() < 3 {
            return self.random_generation(n);
        }
        
        let recent = &self.generation_stats[self.generation_stats.len()-3..];
        let improving = recent[2].avg_score > recent[0].avg_score;
        
        if improving {
            // 如果进步，更多利用成功模式
            self.success_biased_generation(akashic, n)
        } else {
            // 如果停滞，更多随机探索
            let mut configs = self.random_generation(n / 2);
            configs.extend(self.success_biased_generation(akashic, n / 2));
            configs
        }
    }
    
    /// 变异配置
    fn mutate_config(&self, base: &ParameterConfig, rate: f32) -> ParameterConfig {
        ParameterConfig {
            architecture: if random_f32() < rate * 0.3 {
                random_architecture()
            } else {
                base.architecture
            },
            plasticity: if random_f32() < rate * 0.3 {
                random_plasticity()
            } else {
                base.plasticity
            },
            broadcast: if random_f32() < rate * 0.3 {
                random_broadcast()
            } else {
                base.broadcast
            },
            memory: if random_f32() < rate * 0.3 {
                random_memory()
            } else {
                base.memory
            },
            learning_rate: mutate_value(base.learning_rate, 0.001, 0.1, rate),
            connection_density: mutate_value(base.connection_density, 0.01, 0.15, rate),
            ..base.clone()
        }
    }
    
    /// 检查与失败模式的相似度
    fn check_similarity_to_failures(&self, config: &ParameterConfig, akashic: &AkashicRecords) -> bool {
        // 简化的相似度检查
        for entry in &akashic.graveyard {
            // 如果graveyard中有相同架构且参数接近，认为相似
            // 实际实现会更复杂
            if entry.universe_id.starts_with(&format!("{:?}", config.architecture).to_lowercase()) {
                return true; // 简化
            }
        }
        false
    }
    
    /// 计算代际统计
    fn compute_generation_stats(&self, akashic: &AkashicRecords) -> GenerationStats {
        // 简化：基于所有记录计算
        let records = &akashic.universes;
        
        if records.is_empty() {
            return GenerationStats {
                generation: self.generation,
                num_universes: 0,
                avg_score: 0.0,
                best_score: 0.0,
                pass_rate: 0.0,
            };
        }
        
        let total_score: f32 = records.iter()
            .map(|r| r.final_scores.total())
            .sum();
        let best_score = records.iter()
            .map(|r| r.final_scores.total())
            .fold(0.0, f32::max);
        let passed = records.iter()
            .filter(|r| r.final_scores.all_gates_passed(0.5))
            .count();
        
        GenerationStats {
            generation: self.generation,
            num_universes: records.len(),
            avg_score: total_score / records.len() as f32,
            best_score,
            pass_rate: passed as f32 / records.len() as f32,
        }
    }
    
    /// 获取进化报告
    pub fn evolution_report(&self) -> String {
        let mut report = String::new();
        
        report.push_str("# Evolution Report\n\n");
        report.push_str(&format!("Total generations: {}\n", self.generation));
        report.push_str(&format!("Current strategy: {:?}\n\n", self.strategy));
        
        report.push_str("## Generation Progress\n\n");
        report.push_str("| Gen | Universes | Avg Score | Best Score | Pass Rate |\n");
        report.push_str("|-----|-----------|-----------|------------|----------|\n");
        
        for stats in &self.generation_stats {
            report.push_str(&format!("| {} | {} | {:.2} | {:.2} | {:.1}% |\n",
                stats.generation,
                stats.num_universes,
                stats.avg_score,
                stats.best_score,
                stats.pass_rate * 100.0
            ));
        }
        
        report
    }
}

/// 变异数值
fn mutate_value(val: f32, min: f32, max: f32, rate: f32) -> f32 {
    let noise = (random_f32() - 0.5) * 2.0 * rate * (max - min);
    (val + noise).clamp(min, max)
}

fn random_f32() -> f32 {
    use std::sync::atomic::{AtomicU64, Ordering};
    static SEED: AtomicU64 = AtomicU64::new(1357924680);
    
    let old = SEED.fetch_add(1, Ordering::SeqCst);
    let new = old.wrapping_mul(6364136223846793005).wrapping_add(1);
    ((new >> 32) as u32) as f32 / u32::MAX as f32
}

fn random_usize(max: usize) -> usize {
    (random_f32() * max as f32) as usize % max
}

fn random_architecture() -> ArchitectureFamily {
    use ArchitectureFamily::*;
    let options = [WormLike, OctopusLike, TianxinPulse, RandomSparse, ModularLattice];
    options[random_usize(options.len())]
}

fn random_plasticity() -> PlasticityProfile {
    use crate::PlasticityProfile::*;
    let options = [PredictiveHeavy, Balanced, HebbianHeavy];
    options[random_usize(options.len())]
}

fn random_broadcast() -> BroadcastProfile {
    use crate::BroadcastProfile::*;
    let options = [LowBroadcast, MediumBroadcast];
    options[random_usize(options.len())]
}

fn random_memory() -> ScaleProfile {
    use crate::ScaleProfile::*;
    let options = [Small, Medium];
    options[random_usize(options.len())]
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_evolution_engine() {
        let mut engine = EvolutionEngine::new();
        let akashic = AkashicRecords::new();
        
        let configs = engine.generate_next_generation(&akashic, 10);
        assert_eq!(configs.len(), 10);
        assert_eq!(engine.generation, 1);
    }
    
    #[test]
    fn test_mutate_config() {
        let engine = EvolutionEngine::new();
        let base = ParameterConfig::from_architecture(ArchitectureFamily::WormLike, 1);
        
        let mutated = engine.mutate_config(&base, 1.0); // 100%变异率
        
        // 高度变异下，应该有变化
        // 实际上可能相同（概率），但测试基本功能
        assert!(mutated.learning_rate >= 0.001 && mutated.learning_rate <= 0.1);
    }
}
