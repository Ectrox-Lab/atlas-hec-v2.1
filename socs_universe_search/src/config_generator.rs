//! 第一轮 300 Universes 搜索矩阵生成器
//! 
//! 5 families × 20 configs × 3 seeds = 300 universes
//! 保留 4 个扫描轴：Scale × Plasticity × Broadcast × Competition

use crate::universe_config::*;

/// 搜索矩阵生成器
pub struct SearchMatrix {
    pub families: Vec<ArchitectureFamily>,
    pub scale_profiles: Vec<ScaleProfile>,
    pub plasticity_profiles: Vec<PlasticityProfile>,
    pub broadcast_profiles: Vec<BroadcastProfile>,
    pub competition_profiles: Vec<CompetitionProfile>,
    pub env_families: Vec<EnvironmentFamily>,
    pub seeds_per_config: usize,
}

impl SearchMatrix {
    /// 创建第一轮搜索矩阵（v0 默认）
    pub fn round_one() -> Self {
        Self {
            families: ArchitectureFamily::all(),
            scale_profiles: ScaleProfile::all(),
            plasticity_profiles: PlasticityProfile::all(),
            broadcast_profiles: BroadcastProfile::all(),
            competition_profiles: CompetitionProfile::all(),
            env_families: EnvironmentFamily::all(),
            seeds_per_config: 3,
        }
    }
    
    /// 生成所有配置
    /// 
    /// 理论计算：5 families × 2 scales × 3 plasticities × 2 broadcasts × 2 competitions × 3 envs × 3 seeds
    /// = 2160 (太多)
    /// 
    /// 实际：每个 family 20 configs，通过策略性采样
    pub fn generate_all(&self, start_id: u64) -> Vec<UniverseConfig> {
        let mut configs = Vec::new();
        let mut universe_id = start_id;
        
        for family in &self.families {
            let family_configs = self.generate_for_family(*family, &mut universe_id);
            configs.extend(family_configs);
        }
        
        configs
    }
    
    /// 为单个 family 生成 20 个 configs
    fn generate_for_family(&self, family: ArchitectureFamily, universe_id: &mut u64) -> Vec<UniverseConfig> {
        let mut configs = Vec::with_capacity(20 * self.seeds_per_config);
        
        // 基础配置
        let base = UniverseConfig::default_for_family(family, 0, 0);
        
        // 策略：为每个 family 生成 20 个有意义的变体
        let variants = self.design_family_variants(family);
        
        for (idx, (scale, plasticity, broadcast, competition, env)) in variants.iter().enumerate() {
            for seed in 0..self.seeds_per_config {
                let config = base.with_variant(
                    *plasticity,
                    *broadcast,
                    *competition,
                    *scale,
                    *env,
                );
                
                configs.push(UniverseConfig {
                    universe_id: *universe_id,
                    seed: seed as u64,
                    ..config
                });
                
                *universe_id += 1;
            }
        }
        
        configs
    }
    
    /// 为每个 family 设计 20 个有意义的变体组合
    /// 
    /// 策略：
    /// - 确保覆盖所有 plasticity profiles
    /// - 重点测试 scale 差异
    /// - 环境均匀分布
    fn design_family_variants(&self, family: ArchitectureFamily) -> Vec<(ScaleProfile, PlasticityProfile, BroadcastProfile, CompetitionProfile, EnvironmentFamily)> {
        // ArchitectureFamily variants used directly
        
        let mut variants = Vec::with_capacity(20);
        
        // 基础网格：覆盖主要组合
        for scale in &self.scale_profiles {
            for plasticity in &self.plasticity_profiles {
                for broadcast in &self.broadcast_profiles {
                    for competition in &self.competition_profiles {
                        // 每个组合分配一个环境，循环分布
                        let env_idx = variants.len() % self.env_families.len();
                        let env = self.env_families[env_idx];
                        
                        variants.push((*scale, *plasticity, *broadcast, *competition, env));
                        
                        if variants.len() >= 20 {
                            break;
                        }
                    }
                    if variants.len() >= 20 {
                        break;
                    }
                }
                if variants.len() >= 20 {
                    break;
                }
            }
            if variants.len() >= 20 {
                break;
            }
        }
        
        // 如果不够 20 个，添加特定家族的额外测试
        while variants.len() < 20 {
            let idx = variants.len();
            let scale = if idx % 2 == 0 { ScaleProfile::Small } else { ScaleProfile::Medium };
            let plasticity = self.plasticity_profiles[idx % 3];
            let broadcast = self.broadcast_profiles[idx % 2];
            let competition = self.competition_profiles[idx % 2];
            let env = self.env_families[idx % 3];
            
            variants.push((scale, plasticity, broadcast, competition, env));
        }
        
        // 家族特定调整
        variants = self.adjust_for_family(family, variants);
        
        variants.truncate(20);
        variants
    }
    
    /// 家族特定调整
    fn adjust_for_family(
        &self,
        family: ArchitectureFamily,
        mut variants: Vec<(ScaleProfile, PlasticityProfile, BroadcastProfile, CompetitionProfile, EnvironmentFamily)>,
    ) -> Vec<(ScaleProfile, PlasticityProfile, BroadcastProfile, CompetitionProfile, EnvironmentFamily)> {
        match family {
            ArchitectureFamily::WormLike => {
                // 线虫型：更多小规模测试
                for i in 0..variants.len() {
                    if i % 2 == 0 {
                        variants[i].0 = ScaleProfile::Small;
                    }
                }
            }
            ArchitectureFamily::OctopusLike => {
                // 章鱼型：更多中等规模，强调分布式
                for i in 0..variants.len() {
                    variants[i].0 = ScaleProfile::Medium;
                    // 偏向低广播
                    if i % 3 != 0 {
                        variants[i].2 = BroadcastProfile::LowBroadcast;
                    }
                }
            }
            ArchitectureFamily::PulseCentral => {
                // 脉冲型：重点测试同步压力
                for i in 0..variants.len() {
                    // 偏向高广播
                    variants[i].2 = BroadcastProfile::MediumBroadcast;
                    // 更多 FailureBurst 环境
                    if i % 2 == 0 {
                        variants[i].4 = EnvironmentFamily::FailureBurst;
                    }
                }
            }
            ArchitectureFamily::ModularLattice => {
                // 模块化：标准分布即可
            }
            ArchitectureFamily::RandomSparse => {
                // 随机型：作为对照组，标准分布
            }
        }
        
        variants
    }
    
    /// 估算总配置数
    pub fn estimated_total(&self) -> usize {
        self.families.len() * 20 * self.seeds_per_config
    }
    
    /// 获取搜索矩阵摘要
    pub fn summary(&self) -> String {
        format!(
            "Search Matrix Summary:\n\
             - Families: {}\n\
             - Scales: {}\n\
             - Plasticities: {}\n\
             - Broadcasts: {}\n\
             - Competitions: {}\n\
             - Environments: {}\n\
             - Seeds per config: {}\n\
             - Total universes: {}\n\
             - Configs per family: 20",
            self.families.len(),
            self.scale_profiles.len(),
            self.plasticity_profiles.len(),
            self.broadcast_profiles.len(),
            self.competition_profiles.len(),
            self.env_families.len(),
            self.seeds_per_config,
            self.estimated_total(),
        )
    }
    
    /// 分批次生成（用于分批运行）
    pub fn generate_batches(&self, batch_size: usize, start_id: u64) -> Vec<Vec<UniverseConfig>> {
        let all_configs = self.generate_all(start_id);
        let mut batches = Vec::new();
        
        for chunk in all_configs.chunks(batch_size) {
            batches.push(chunk.to_vec());
        }
        
        batches
    }
}

/// 运行配置（用于控制实际运行）
#[derive(Clone, Debug)]
pub struct RunConfig {
    pub batch_size: usize,
    pub parallel_workers: usize,
    pub save_interval: usize,
    pub output_dir: String,
}

impl Default for RunConfig {
    fn default() -> Self {
        Self {
            batch_size: 50,
            parallel_workers: 4,
            save_interval: 10,
            output_dir: "./records".to_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_round_one_matrix() {
        let matrix = SearchMatrix::round_one();
        let configs = matrix.generate_all(0);
        
        println!("{}", matrix.summary());
        println!("Generated {} configs", configs.len());
        
        // 应该生成 300 个配置
        assert_eq!(configs.len(), 300);
        
        // 验证 ID 唯一
        let ids: std::collections::HashSet<_> = configs.iter().map(|c| c.universe_id).collect();
        assert_eq!(ids.len(), configs.len());
        
        // 验证每个 family 有 60 个配置 (20 configs × 3 seeds)
        for family in ArchitectureFamily::all() {
            let family_count = configs.iter().filter(|c| c.family == family).count();
            assert_eq!(family_count, 60, "Family {:?} should have 60 configs", family);
        }
    }
    
    #[test]
    fn test_batch_generation() {
        let matrix = SearchMatrix::round_one();
        let batches = matrix.generate_batches(50, 0);
        
        // 300 configs / 50 per batch = 6 batches
        assert_eq!(batches.len(), 6);
        
        // 验证批次大小
        assert_eq!(batches[0].len(), 50);
        assert_eq!(batches[5].len(), 50);
    }
    
    #[test]
    fn test_family_distribution() {
        let matrix = SearchMatrix::round_one();
        let configs = matrix.generate_all(0);
        
        // 验证环境分布
        let env_counts: std::collections::HashMap<_, _> = configs.iter()
            .map(|c| c.env_family)
            .fold(std::collections::HashMap::new(), |mut acc, env| {
                *acc.entry(env).or_insert(0) += 1;
                acc
            });
        
        println!("Environment distribution: {:?}", env_counts);
        
        // 每个环境应该都有一些
        assert_eq!(env_counts.len(), 3);
    }
}
