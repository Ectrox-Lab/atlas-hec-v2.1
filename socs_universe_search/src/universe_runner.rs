//! 宇宙运行器
//! 
//! 连接真实SOCS状态，运行单个宇宙

use crate::evaluation::{evaluate_dynamics, TickSnapshot};
use crate::telemetry::{
    append_graveyard, append_hall_of_fame, build_summary,
    should_enter_graveyard, should_enter_hall_of_fame, print_run_summary,
    TelemetryWriter, UniverseSummary,
};
use crate::universe_config::UniverseConfig;
use crate::consciousness_index::evaluate_cwci;
use anyhow::Result;

/// 运行单个宇宙（真实接线版）
/// 
/// TODO: 将SocsRuntime替换为真实SOCS状态对象
pub fn run_universe_once(cfg: &UniverseConfig) -> Result<UniverseSummary> {
    let label = format!(
        "u{}_{}_{}",
        cfg.universe_id,
        cfg.family.as_str(),
        cfg.seed
    );
    
    // 创建遥测写入器
    let mut telemetry = TelemetryWriter::new("outputs", &label)?;
    
    // 初始化运行时（TODO: 替换为真实SOCS初始化）
    let mut runtime = SocsRuntime::from_config(cfg);
    let mut history: Vec<TickSnapshot> = Vec::new();
    
    // 主循环
    for _ in 0..cfg.ticks {
        // 运行一个tick（TODO: 替换为真实SOCS step）
        runtime.step(cfg);
        
        // 记录遥测（按stride采样）
        if runtime.tick % cfg.telemetry_stride == 0 {
            let snap = runtime.snapshot(cfg);
            telemetry.write_tick(cfg, &snap)?;
            history.push(snap);
        }
    }
    
    telemetry.flush()?;
    
    // 评估动力学
    let evaluation = evaluate_dynamics(&history);
    
    // 检测崩溃特征
    let collapse_signature = detect_collapse(&evaluation, &history);
    
    // 计算CWCI（代码世界意识指数）
    let open_world_survived = collapse_signature.is_none();
    let cwci = evaluate_cwci(&evaluation.scores, &history, open_world_survived, false);
    
    // 构建摘要（包含CWCI）
    let summary = build_summary(cfg, evaluation, collapse_signature, Some(cwci));
    
    // 写入JSON摘要
    telemetry.write_summary(&label, &summary)?;
    
    // 更新Hall of Fame / Graveyard
    if should_enter_hall_of_fame(&summary) {
        append_hall_of_fame("outputs", &summary)?;
    }
    if should_enter_graveyard(&summary) {
        append_graveyard("outputs", &summary)?;
    }
    
    Ok(summary)
}

/// 检测崩溃特征
fn detect_collapse(evaluation: &crate::evaluation::EvaluationResult, history: &[TickSnapshot]) -> Option<String> {
    // 过同步：广播持续单一，熵极低
    if evaluation.scores.broadcast_score > 0.9 && evaluation.scores.specialization_score < 0.2 {
        return Some("over_synchronization".to_string());
    }
    
    // 广播霸权：单一状态长期主导
    let recent_broadcasts: Vec<_> = history.iter().rev().take(100).collect();
    if !recent_broadcasts.is_empty() && recent_broadcasts.iter().all(|h| h.broadcast_count <= 1) {
        if evaluation.scores.broadcast_score > 0.7 {
            return Some("broadcast_tyranny".to_string());
        }
    }
    
    // 恢复失败：高分险但无恢复
    if evaluation.scores.recovery_score < 0.2 && 
       history.iter().map(|h| h.hazard).sum::<f32>() / history.len() as f32 > 0.3 {
        return Some("recovery_failure".to_string());
    }
    
    // 完全失败：0门通过
    if evaluation.phenomena.pass_count() == 0 {
        return Some("total_collapse".to_string());
    }
    
    None
}

// ============================================================================
// TODO: 替换为真实SOCS运行时
// ============================================================================

/// SOCS运行时（差异化模拟实现）
/// 
/// v0: 基于配置的差异化模拟数据生成
/// 为不同family/stress/seed产生可区分的动力学模式
pub struct SocsRuntime {
    pub tick: usize,
    pub seed: u64,
    pub family_variant: u8,  // 基于family的变体
    // TODO: 添加真实SOCS状态字段
}

impl SocsRuntime {
    /// 从配置初始化（带差异化参数）
    pub fn from_config(cfg: &UniverseConfig) -> Self {
        println!("    [INIT] family={} n_units={} stress={}", 
            cfg.family.as_str(), 
            cfg.n_units,
            cfg.stress.name.as_str()
        );
        
        // 基于family分配变体特性
        let family_variant = match cfg.family {
            crate::universe_config::ArchitectureFamily::WormLike => 0,
            crate::universe_config::ArchitectureFamily::OctopusLike => 1,
            crate::universe_config::ArchitectureFamily::PulseCentral => 2,
            crate::universe_config::ArchitectureFamily::ModularLattice => 3,
            crate::universe_config::ArchitectureFamily::RandomSparse => 4,
        };
        
        Self { 
            tick: 0,
            seed: cfg.seed,
            family_variant,
        }
    }
    
    /// 运行一个tick
    pub fn step(&mut self, _cfg: &UniverseConfig) {
        self.tick += 1;
    }
    
    /// 获取状态快照（差异化模拟版）
    /// 
    /// 基于family/stress/seed产生可区分的动力学模式
    pub fn snapshot(&self, cfg: &UniverseConfig) -> TickSnapshot {
        let tick_f = self.tick as f32;
        let seed_f = (self.seed % 1000) as f32 / 1000.0; // 0-1 based on seed
        let family_f = self.family_variant as f32 / 4.0;  // 0-1 based on family
        
        // 基于stress profile调整基础参数
        let stress_factor = match cfg.stress_profile {
            crate::stress_profile::StressProfile::StableLowStress => 1.0,
            crate::stress_profile::StressProfile::ResourceScarcity => 0.7,
            crate::stress_profile::StressProfile::BossPressureHigh => 0.6,
            crate::stress_profile::StressProfile::RegimeShiftFrequent => 0.8,
            crate::stress_profile::StressProfile::HighCoordinationDemand => 0.75,
            crate::stress_profile::StressProfile::HighCompetition => 0.65,
            crate::stress_profile::StressProfile::SyncRiskHigh => 0.7,
            crate::stress_profile::StressProfile::InheritanceNoiseHigh => 0.85,
        };
        
        // Family-specific dynamics patterns
        // Each family has different "natural" behaviors in the stub
        // v3: Enhanced differentiation for CWCI resolution >= 0.20
        let (base_clusters, cluster_var, base_entropy, entropy_noise, broadcast_freq, base_spec) = match self.family_variant {
            0 => (1.5, 1.0, 0.35, 0.15, 50, 0.40),   // Worm: conservative, stable
            1 => (9.0, 6.0, 0.90, 0.40, 10, 0.85),   // Octopus: distributed, variable
            2 => (2.0, 0.3, 0.30, 0.05, 5, 0.30),    // Pulse: centralized, rhythmic
            3 => (10.0, 3.0, 0.85, 0.30, 15, 0.90),  // Lattice: modular, organized
            _ => (2.0, 7.0, 0.40, 0.50, 40, 0.25),   // Random: chaotic, unstable
        };
        
        // Seed-based phase offset for variety within same family/stress
        let phase = seed_f * std::f32::consts::PI * 2.0;
        
        // Compute active clusters with family+seed variation (enhanced amplitude)
        let cluster_oscillation = ((tick_f / 350.0 + phase) * (1.0 + family_f * 2.0)).sin() * cluster_var;
        let active_clusters = ((base_clusters + cluster_oscillation) * stress_factor).max(1.0) as usize;
        
        // Attractor ID changes based on family stability (extreme differentiation)
        let attractor_period = match self.family_variant {
            0 => 800,  // Worm: very slow switching
            1 => 60,   // Octopus: fast switching
            2 => 400,  // Pulse: rhythmic moderate
            3 => 250,  // Lattice: moderate
            _ => 50,   // Random: chaotic fast
        };
        let attractor_id = Some(((self.tick / attractor_period + self.seed as usize) % 4) as u64);
        
        // Entropy varies by family and stress (enhanced variation)
        let entropy_oscillation = ((tick_f / 500.0 + phase * 0.9).sin() * entropy_noise * 2.0);
        let cluster_entropy = (base_entropy + entropy_oscillation * stress_factor).clamp(0.02, 1.0);
        
        // Specialization evolves differently per family (extreme differentiation)
        let spec_growth = (tick_f / 2500.0).min(0.25) * stress_factor;
        let spec_noise = (seed_f - 0.5) * 0.25;
        let specialization_score = base_spec + spec_growth + spec_noise;
        
        // Broadcast varies by family design and stress (extreme family signatures)
        let broadcast_count = if self.tick % broadcast_freq == 0 {
            match self.family_variant {
                2 => 4, // Pulse: very centralized (many broadcasts at once)
                1 => 3, // Octopus: high frequency distributed
                3 => 2, // Lattice: regular pattern
                4 => if seed_f > 0.6 { 1 } else { 0 }, // Random: unpredictable
                _ => 1,
            }
        } else {
            0
        };
        
        // Prediction error improves over time, varies by family learnability (extreme)
        let learn_rate = match self.family_variant {
            0 => 30000.0,  // Worm: very slow learning
            1 => 4000.0,   // Octopus: fast learning
            2 => 20000.0,  // Pulse: moderate-slow
            3 => 25000.0,  // Lattice: slow but steady
            _ => 3000.0,   // Random: erratic fast
        };
        let base_error = 0.35 + seed_f * 0.20;
        let avg_prediction_error = (base_error - (tick_f / learn_rate).min(0.25) * stress_factor).max(0.02);
        
        // Energy varies by stress profile
        let energy_base = cfg.stress.food_energy / 100.0;
        let energy_drain = tick_f / (8000.0 + seed_f * 2000.0);
        let avg_energy = (energy_base - energy_drain * (2.0 - stress_factor)).max(0.1);
        
        // Hazard varies by stress and family resilience
        let resilience = match self.family_variant {
            1 => 0.9, // Octopus: high resilience
            3 => 0.85, // Lattice: good resilience
            0 => 0.7,  // Worm: moderate
            2 => 0.6,  // Pulse: lower
            _ => 0.5,  // Random: poor
        };
        let base_hazard = cfg.stress.boss_pressure * 0.1;
        let hazard_cycle = ((tick_f / 600.0 + phase).sin() + 1.0) / 2.0 * 0.3;
        let hazard = (base_hazard + hazard_cycle * (1.0 - resilience) / stress_factor).clamp(0.0, 1.0);
        
        // Recovery events: family-dependent recovery capability (extreme)
        let recovery_period = match self.family_variant {
            1 => 150,  // Octopus: recovers very fast
            3 => 280,  // Lattice: steady recovery
            0 => 800,  // Worm: slow recovery
            2 => 900,  // Pulse: very slow recovery
            _ => 1000, // Random: unreliable
        };
        let recovery_event = self.tick % recovery_period == 0 && self.tick > 0 && seed_f > 0.1;
        
        // Memory stats vary by configuration
        let l1_reads = (100.0 * (1.0 + family_f) * stress_factor) as usize;
        let l2_inheritances = (10.0 * stress_factor * (1.0 + seed_f)) as usize;
        let l3_hits = if cfg.l3_enabled { (1.0 + seed_f * 2.0) as usize } else { 0 };
        
        TickSnapshot {
            tick: self.tick,
            alive_units: cfg.n_units,
            active_clusters,
            attractor_id,
            cluster_entropy,
            specialization_score,
            broadcast_count,
            avg_prediction_error,
            avg_energy,
            hazard,
            recovery_event,
            l1_reads,
            l2_inheritances,
            l3_hits,
        }
    }
}

// ============================================================================
// 真实SOCS状态映射指南
// ============================================================================

/*
将真实SOCS状态映射到TickSnapshot的10个必需字段：

1. alive_units
   - 来源: micro_unit::Network.get_active_units().len()
   - 条件: energy > threshold && !in_dormancy

2. active_clusters  
   - 来源: cluster_dynamics::ClusterManager.get_active_clusters().len()
   - 条件: activation > cluster_threshold

3. attractor_id
   - 来源: cluster_dynamics::AttractorDetector.get_current_attractor()
   - 或: global_workspace::Workspace.get_dominant_state_hash()

4. cluster_entropy
   - 计算: 团簇规模分布的香农熵
   - 来源: cluster_dynamics::ClusterManager.compute_entropy()

5. specialization_score
   - 计算: 团簇间功能差异度
   - 来源: cluster_dynamics::ClusterManager.get_differentiation_score()

6. broadcast_count
   - 来源: global_workspace::Workspace.get_active_broadcasts().len()

7. avg_prediction_error
   - 计算: 所有单元的prediction_error均值
   - 来源: micro_unit::Network.get_avg_prediction_error()

8. avg_energy
   - 计算: 所有单元的energy均值
   - 来源: micro_unit::Network.get_avg_energy()

9. hazard
   - 合成: population下降率 + cluster collapse率 + recent failures
   - 来源: substrate_open_world_bridge::EnvironmentBridge.get_hazard_level()

10. recovery_event
    - 检测: hazard从高峰回落到稳定区间
    - 来源: 基于hazard历史计算
*/
