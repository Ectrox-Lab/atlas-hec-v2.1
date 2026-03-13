//! 参数空间搜索（已迁移到 config_generator.rs）
//! 
//! 此模块保留用于兼容性，主要功能已移至 config_generator

use crate::universe_config::{ArchitectureFamily, UniverseConfig};

/// 参数空间（简化版）
pub struct ParameterSpace;

impl ParameterSpace {
    /// 生成所有配置（委托给 config_generator）
    pub fn generate_all() -> Vec<UniverseConfig> {
        crate::config_generator::SearchMatrix::round_one()
            .generate_all(0)
    }
    
    /// 估算总配置数
    pub fn estimated_total() -> usize {
        crate::config_generator::SearchMatrix::round_one().estimated_total()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_parameter_space() {
        let configs = ParameterSpace::generate_all();
        assert!(!configs.is_empty());
    }
}
