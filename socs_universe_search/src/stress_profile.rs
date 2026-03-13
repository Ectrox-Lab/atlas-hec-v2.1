//! 8类宇宙压力画像
//! 
//! 系统化异质环境矩阵：结构家族 × 压力宇宙

use serde::{Serialize, Deserialize};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum StressProfile {
    StableLowStress,       // 低压稳定：看基础动力学
    ResourceScarcity,      // 资源稀缺：看生存/节能
    BossPressureHigh,      // 高压威胁：看恢复
    RegimeShiftFrequent,   // 高频切换：看重组
    HighCoordinationDemand,// 高协作门槛：看广播/协同
    HighCompetition,       // 高竞争：看分化/博弈
    SyncRiskHigh,          // 高同步风险：看过同步脆弱性
    InheritanceNoiseHigh,  // 高继承噪声：看L2/L3抗扰性
}

impl StressProfile {
    pub fn all() -> [StressProfile; 8] {
        [
            StressProfile::StableLowStress,
            StressProfile::ResourceScarcity,
            StressProfile::BossPressureHigh,
            StressProfile::RegimeShiftFrequent,
            StressProfile::HighCoordinationDemand,
            StressProfile::HighCompetition,
            StressProfile::SyncRiskHigh,
            StressProfile::InheritanceNoiseHigh,
        ]
    }
    
    pub fn as_str(&self) -> &'static str {
        match self {
            StressProfile::StableLowStress => "stable_low_stress",
            StressProfile::ResourceScarcity => "resource_scarcity",
            StressProfile::BossPressureHigh => "boss_pressure_high",
            StressProfile::RegimeShiftFrequent => "regime_shift_frequent",
            StressProfile::HighCoordinationDemand => "high_coordination_demand",
            StressProfile::HighCompetition => "high_competition",
            StressProfile::SyncRiskHigh => "sync_risk_high",
            StressProfile::InheritanceNoiseHigh => "inheritance_noise_high",
        }
    }
}

/// 压力配置详细参数
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StressProfileConfig {
    pub name: StressProfile,
    
    // 资源/生存
    pub food_spawn_rate: f32,
    pub food_energy: f32,
    pub metabolism_rate: f32,
    pub reproduction_cost: f32,
    pub reproduction_threshold: f32,
    
    // 扰动/环境变化
    pub perturbation_interval: usize,
    pub perturbation_strength: f32,
    pub regime_shift_interval: usize,
    pub regime_shift_magnitude: f32,
    
    // 压力项
    pub boss_pressure: f32,
    pub coordination_requirement: f32,
    pub competition_pressure: f32,
    pub sync_coupling_boost: f32,
    
    // 继承/记忆噪声
    pub inheritance_noise: f32,
}

impl StressProfileConfig {
    pub fn default_for(profile: StressProfile) -> Self {
        match profile {
            StressProfile::StableLowStress => Self {
                name: profile,
                food_spawn_rate: 0.12,
                food_energy: 60.0,
                metabolism_rate: 0.8,
                reproduction_cost: 30.0,
                reproduction_threshold: 35.0,
                perturbation_interval: 5000,
                perturbation_strength: 0.0,
                regime_shift_interval: 5000,
                regime_shift_magnitude: 0.0,
                boss_pressure: 0.0,
                coordination_requirement: 0.2,
                competition_pressure: 0.2,
                sync_coupling_boost: 0.0,
                inheritance_noise: 0.0,
            },
            
            StressProfile::ResourceScarcity => Self {
                name: profile,
                food_spawn_rate: 0.04,
                food_energy: 25.0,
                metabolism_rate: 1.4,
                reproduction_cost: 40.0,
                reproduction_threshold: 45.0,
                perturbation_interval: 2000,
                perturbation_strength: 0.1,
                regime_shift_interval: 4000,
                regime_shift_magnitude: 0.1,
                boss_pressure: 0.1,
                coordination_requirement: 0.3,
                competition_pressure: 0.5,
                sync_coupling_boost: 0.0,
                inheritance_noise: 0.0,
            },
            
            StressProfile::BossPressureHigh => Self {
                name: profile,
                food_spawn_rate: 0.08,
                food_energy: 40.0,
                metabolism_rate: 1.2,
                reproduction_cost: 38.0,
                reproduction_threshold: 42.0,
                perturbation_interval: 300,
                perturbation_strength: 0.8,
                regime_shift_interval: 2500,
                regime_shift_magnitude: 0.2,
                boss_pressure: 1.5,
                coordination_requirement: 0.4,
                competition_pressure: 0.4,
                sync_coupling_boost: 0.0,
                inheritance_noise: 0.0,
            },
            
            StressProfile::RegimeShiftFrequent => Self {
                name: profile,
                food_spawn_rate: 0.08,
                food_energy: 45.0,
                metabolism_rate: 1.0,
                reproduction_cost: 35.0,
                reproduction_threshold: 40.0,
                perturbation_interval: 1500,
                perturbation_strength: 0.2,
                regime_shift_interval: 500,
                regime_shift_magnitude: 0.7,
                boss_pressure: 0.2,
                coordination_requirement: 0.4,
                competition_pressure: 0.4,
                sync_coupling_boost: 0.0,
                inheritance_noise: 0.0,
            },
            
            StressProfile::HighCoordinationDemand => Self {
                name: profile,
                food_spawn_rate: 0.07,
                food_energy: 40.0,
                metabolism_rate: 1.0,
                reproduction_cost: 36.0,
                reproduction_threshold: 40.0,
                perturbation_interval: 2000,
                perturbation_strength: 0.1,
                regime_shift_interval: 3000,
                regime_shift_magnitude: 0.2,
                boss_pressure: 0.1,
                coordination_requirement: 0.8,
                competition_pressure: 0.2,
                sync_coupling_boost: 0.2,
                inheritance_noise: 0.0,
            },
            
            StressProfile::HighCompetition => Self {
                name: profile,
                food_spawn_rate: 0.06,
                food_energy: 35.0,
                metabolism_rate: 1.1,
                reproduction_cost: 38.0,
                reproduction_threshold: 42.0,
                perturbation_interval: 2000,
                perturbation_strength: 0.15,
                regime_shift_interval: 3500,
                regime_shift_magnitude: 0.2,
                boss_pressure: 0.1,
                coordination_requirement: 0.2,
                competition_pressure: 0.9,
                sync_coupling_boost: 0.0,
                inheritance_noise: 0.0,
            },
            
            StressProfile::SyncRiskHigh => Self {
                name: profile,
                food_spawn_rate: 0.08,
                food_energy: 40.0,
                metabolism_rate: 1.0,
                reproduction_cost: 35.0,
                reproduction_threshold: 40.0,
                perturbation_interval: 1000,
                perturbation_strength: 0.3,
                regime_shift_interval: 2500,
                regime_shift_magnitude: 0.1,
                boss_pressure: 0.2,
                coordination_requirement: 0.6,
                competition_pressure: 0.2,
                sync_coupling_boost: 0.5,
                inheritance_noise: 0.0,
            },
            
            StressProfile::InheritanceNoiseHigh => Self {
                name: profile,
                food_spawn_rate: 0.08,
                food_energy: 40.0,
                metabolism_rate: 1.0,
                reproduction_cost: 35.0,
                reproduction_threshold: 40.0,
                perturbation_interval: 1500,
                perturbation_strength: 0.2,
                regime_shift_interval: 2500,
                regime_shift_magnitude: 0.2,
                boss_pressure: 0.2,
                coordination_requirement: 0.4,
                competition_pressure: 0.3,
                sync_coupling_boost: 0.0,
                inheritance_noise: 0.25,
            },
        }
    }
}
