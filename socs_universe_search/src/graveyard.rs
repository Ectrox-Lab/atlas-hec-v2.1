//! Graveyard - 墓地
//! 
//! 保留失败结构，积累失败知识。
//! 不是只保留赢家，广泛尝试 + 详细记录 = 研究基础。

use serde::{Serialize, Deserialize};
use crate::evaluation::{CollapseSignature, EvaluationResult, DynamicsScores, DynamicPhenomena};
use crate::universe_config::{ArchitectureFamily, UniverseConfig};

/// 墓地条目
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GraveyardEntry {
    pub universe_id: u64,
    pub family: ArchitectureFamily,
    pub config_hash: String,
    pub cause_of_death: CollapseSignature,
    pub survival_time: usize,
    pub final_metrics: String,
    pub lessons_learned: String,
    pub buried_at: u64,
}

/// 墓地
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Graveyard {
    pub entries: Vec<GraveyardEntry>,
    pub collapse_patterns: Vec<CollapsePattern>,
}

/// 崩溃模式统计
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CollapsePattern {
    pub signature: CollapseSignature,
    pub occurrence_count: usize,
    pub affected_families: Vec<ArchitectureFamily>,
    pub common_conditions: Vec<String>,
    pub lessons: String,
}

impl Graveyard {
    pub fn new() -> Self {
        Self {
            entries: Vec::new(),
            collapse_patterns: Vec::new(),
        }
    }
    
    /// 埋葬一个失败的宇宙
    pub fn bury(&mut self, result: &EvaluationResult, config: &UniverseConfig, survival_time: usize) {
        // 只记录有明确崩溃特征的
        let cause = match &result.collapse_signature {
            Some(sig) => sig.clone(),
            None => return, // 不明原因失败，暂不记录
        };
        
        let entry = GraveyardEntry {
            universe_id: result.universe_id,
            family: config.family,
            config_hash: config.config_hash(),
            cause_of_death: cause.clone(),
            survival_time,
            final_metrics: format!("Score: {:.2}", result.scores.total()),
            lessons_learned: self.analyze_lessons(&cause, config),
            buried_at: current_timestamp(),
        };
        
        self.entries.push(entry);
        self.update_patterns(&cause, config);
    }
    
    /// 分析教训
    fn analyze_lessons(&self, cause: &CollapseSignature, config: &UniverseConfig) -> String {
        match cause {
            CollapseSignature::OverSynchronization => {
                if config.broadcast_sparsity > 0.1 {
                    "High broadcast sparsity may cause over-sync".to_string()
                } else {
                    "Consider reducing workspace_k".to_string()
                }
            }
            CollapseSignature::BroadcastTyranny => {
                if config.workspace_k == 1 {
                    "Single workspace slot too restrictive".to_string()
                } else {
                    "Check competition strength balance".to_string()
                }
            }
            CollapseSignature::MemoryRunaway => {
                "L1 trace decay may be too slow".to_string()
            }
            CollapseSignature::AttractorLock => {
                "Attractor decay too strong or energy budget too low".to_string()
            }
            CollapseSignature::RecoveryFailure => {
                "Homeostasis strength may be insufficient".to_string()
            }
            CollapseSignature::EnergyRunaway => {
                "Energy budget or metabolism needs adjustment".to_string()
            }
        }
    }
    
    /// 更新崩溃模式统计
    fn update_patterns(&mut self, cause: &CollapseSignature, config: &UniverseConfig) {
        // 查找或创建模式
        let pattern = self.collapse_patterns.iter_mut()
            .find(|p| p.signature == *cause);
        
        if let Some(pattern) = pattern {
            pattern.occurrence_count += 1;
            if !pattern.affected_families.contains(&config.family) {
                pattern.affected_families.push(config.family);
            }
        } else {
            self.collapse_patterns.push(CollapsePattern {
                signature: cause.clone(),
                occurrence_count: 1,
                affected_families: vec![config.family],
                common_conditions: vec![],
                lessons: self.initial_lesson(cause),
            });
        }
    }
    
    fn initial_lesson(&self, cause: &CollapseSignature) -> String {
        match cause {
            CollapseSignature::OverSynchronization => {
                "Over-synchronization: System loses diversity, all clusters align".to_string()
            }
            CollapseSignature::BroadcastTyranny => {
                "Broadcast tyranny: Single state dominates, no competition".to_string()
            }
            CollapseSignature::MemoryRunaway => {
                "Memory runaway: Traces accumulate without decay".to_string()
            }
            CollapseSignature::AttractorLock => {
                "Attractor lock: System stuck in single state".to_string()
            }
            CollapseSignature::RecoveryFailure => {
                "Recovery failure: Cannot bounce back from perturbation".to_string()
            }
            CollapseSignature::EnergyRunaway => {
                "Energy runaway: Positive feedback loop in energy dynamics".to_string()
            }
        }
    }
    
    /// 按崩溃类型统计
    pub fn stats_by_collapse(&self) -> Vec<(CollapseSignature, usize)> {
        use std::collections::HashMap;
        let mut counts: HashMap<CollapseSignature, usize> = HashMap::new();
        
        for entry in &self.entries {
            *counts.entry(entry.cause_of_death.clone()).or_insert(0) += 1;
        }
        
        let mut result: Vec<_> = counts.into_iter().collect();
        result.sort_by(|a, b| b.1.cmp(&a.1));
        result
    }
    
    /// 导出摘要
    pub fn summary(&self) -> String {
        if self.entries.is_empty() {
            return "Graveyard is empty - all universes survived!".to_string();
        }
        
        let mut summary = format!("Graveyard ({} entries)\n", self.entries.len());
        summary.push_str("================================\n\n");
        
        summary.push_str("Collapse Patterns:\n");
        for (sig, count) in self.stats_by_collapse() {
            summary.push_str(&format!("  {:?}: {} cases\n", sig, count));
        }
        
        summary.push_str("\nRecent Deaths:\n");
        for entry in self.entries.iter().rev().take(5) {
            summary.push_str(&format!(
                "  {:?} - {:?} after {} ticks\n",
                entry.family,
                entry.cause_of_death,
                entry.survival_time
            ));
        }
        
        summary
    }
    
    /// 获取对某家族的建议
    pub fn advice_for_family(&self, family: ArchitectureFamily) -> Vec<String> {
        let family_deaths: Vec<_> = self.entries.iter()
            .filter(|e| e.family == family)
            .collect();
        
        if family_deaths.is_empty() {
            return vec!["No recorded failures for this family".to_string()];
        }
        
        let mut advice = Vec::new();
        
        // 统计该家族的主要死因
        use std::collections::HashMap;
        let mut causes: HashMap<CollapseSignature, usize> = HashMap::new();
        for entry in &family_deaths {
            *causes.entry(entry.cause_of_death.clone()).or_insert(0) += 1;
        }
        
        // 给出建议
        let most_common = causes.iter().max_by_key(|&(_, count)| count);
        if let Some((sig, count)) = most_common {
            advice.push(format!(
                "Most common failure ({}/{}): {:?}",
                count,
                family_deaths.len(),
                sig
            ));
            
            // 基于死因给出具体建议
            match sig {
                CollapseSignature::OverSynchronization => {
                    advice.push("Try reducing broadcast_sparsity or increasing workspace_k".to_string());
                }
                CollapseSignature::RecoveryFailure => {
                    advice.push("Consider increasing homeostasis_strength or energy_budget".to_string());
                }
                _ => {}
            }
        }
        
        advice
    }
}

fn current_timestamp() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_graveyard() {
        let mut graveyard = Graveyard::new();
        
        let config = UniverseConfig::default_for_family(ArchitectureFamily::PulseCentral, 0, 0);
        
        let result = EvaluationResult {
            universe_id: 1,
            scores: DynamicsScores::default(),
            metrics: Default::default(),
            passed_gates: 2,
            meets_minimum: false,
            collapse_signature: Some(CollapseSignature::OverSynchronization),
            violations: vec![],
        };
        
        graveyard.bury(&result, &config, 1000);
        
        assert_eq!(graveyard.entries.len(), 1);
        assert!(!graveyard.collapse_patterns.is_empty());
        
        let stats = graveyard.stats_by_collapse();
        assert_eq!(stats[0].1, 1);
    }
}
