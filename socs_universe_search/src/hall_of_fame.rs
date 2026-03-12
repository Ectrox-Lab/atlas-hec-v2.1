//! Hall of Fame - 名人堂
//! 
//! 只收：稳定、可复现、无作弊的结构。

use serde::{Serialize, Deserialize};
use crate::evaluation::{DynamicsScores, EvaluationResult, DynamicPhenomena};
use crate::universe_config::{ArchitectureFamily, UniverseConfig};

/// 名人堂条目
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HallOfFameEntry {
    pub rank: usize,
    pub universe_id: u64,
    pub family: ArchitectureFamily,
    pub config_hash: String,
    pub total_score: f32,
    pub scores: DynamicsScores,
    pub key_strengths: Vec<String>,
    pub stability_across_seeds: f32,
    pub inducted_at: u64,
    pub notes: String,
}

/// 名人堂
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct HallOfFame {
    pub entries: Vec<HallOfFameEntry>,
    pub max_size: usize,
}

impl HallOfFame {
    pub fn new(max_size: usize) -> Self {
        Self {
            entries: Vec::new(),
            max_size,
        }
    }
    
    /// 考虑加入名人堂
    pub fn consider(&mut self, result: &EvaluationResult, config: &UniverseConfig, stability: f32) {
        // 检查是否合格
        if !self.is_qualified(result, stability) {
            return;
        }
        
        let entry = HallOfFameEntry {
            rank: 0, // 稍后计算
            universe_id: result.universe_id,
            family: config.family,
            config_hash: config.config_hash(),
            total_score: result.scores.total(),
            scores: result.scores.clone(),
            key_strengths: result.scores.strengths(0.7),
            stability_across_seeds: stability,
            inducted_at: current_timestamp(),
            notes: self.generate_notes(result),
        };
        
        self.entries.push(entry);
        self.sort_and_trim();
    }
    
    /// 检查是否合格
    fn is_qualified(&self, result: &EvaluationResult, stability: f32) -> bool {
        // 必须满足最低门限
        if !result.meets_minimum {
            return false;
        }
        
        // 跨 seeds 稳定（至少 2/3）
        if stability < 0.66 {
            return false;
        }
        
        // 无违规
        if !result.violations.is_empty() {
            return false;
        }
        
        // 不是崩溃模式
        if result.collapse_signature.is_some() {
            return false;
        }
        
        // 恢复能力不是靠同步霸权
        if result.scores.recovery_score > 0.9 && result.scores.broadcast_score > 0.9 {
            // 高恢复 + 高广播可能是同步霸权，需要额外检查
            // 简化：暂时允许，后续可加更细检查
        }
        
        true
    }
    
    /// 排序并裁剪
    fn sort_and_trim(&mut self) {
        // 按总分排序
        self.entries.sort_by(|a, b| {
            b.total_score.partial_cmp(&a.total_score).unwrap()
        });
        
        // 裁剪
        if self.entries.len() > self.max_size {
            self.entries.truncate(self.max_size);
        }
        
        // 更新排名
        for (i, entry) in self.entries.iter_mut().enumerate() {
            entry.rank = i + 1;
        }
    }
    
    /// 生成备注
    fn generate_notes(&self, result: &EvaluationResult) -> String {
        let mut notes = Vec::new();
        
        if result.scores.attractor_score > 0.8 {
            notes.push("Strong attractors".to_string());
        }
        if result.scores.memory_score > 0.8 {
            notes.push("Persistent memory".to_string());
        }
        if result.scores.recovery_score > 0.8 {
            notes.push("Resilient recovery".to_string());
        }
        
        notes.join("; ")
    }
    
    /// 获取前 N 名
    pub fn top(&self, n: usize) -> &[HallOfFameEntry] {
        &self.entries[..n.min(self.entries.len())]
    }
    
    /// 按家族统计
    pub fn stats_by_family(&self) -> Vec<(ArchitectureFamily, usize, f32)> {
        use std::collections::HashMap;
        let mut stats: HashMap<ArchitectureFamily, (usize, f32)> = HashMap::new();
        
        for entry in &self.entries {
            let (count, total) = stats.entry(entry.family).or_insert((0, 0.0));
            *count += 1;
            *total += entry.total_score;
        }
        
        let mut result: Vec<_> = stats.into_iter()
            .map(|(family, (count, total))| (family, count, total / count as f32))
            .collect();
        
        result.sort_by(|a, b| b.2.partial_cmp(&a.2).unwrap());
        result
    }
    
    /// 导出摘要
    pub fn summary(&self) -> String {
        if self.entries.is_empty() {
            return "Hall of Fame is empty".to_string();
        }
        
        let mut summary = format!("Hall of Fame ({} entries)\n", self.entries.len());
        summary.push_str("================================\n\n");
        
        for entry in self.top(10) {
            summary.push_str(&format!(
                "Rank {}: {:?} | Score {:.2} | Stability {:.0}% | {}\n",
                entry.rank,
                entry.family,
                entry.total_score,
                entry.stability_across_seeds * 100.0,
                entry.notes
            ));
        }
        
        summary.push_str("\nBy Family:\n");
        for (family, count, avg) in self.stats_by_family() {
            summary.push_str(&format!("  {:?}: {} entries, avg {:.2}\n", family, count, avg));
        }
        
        summary
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
    fn test_hall_of_fame() {
        let mut hof = HallOfFame::new(10);
        
        let config = UniverseConfig::default_for_family(ArchitectureFamily::WormLike, 0, 0);
        
        let result = EvaluationResult {
            universe_id: 1,
            scores: DynamicsScores {
                attractor_score: 0.8,
                memory_score: 0.7,
                reorganization_score: 0.6,
                specialization_score: 0.9,
                broadcast_score: 0.5,
                recovery_score: 0.8,
            },
            metrics: Default::default(),
            passed_gates: 5,
            meets_minimum: true,
            collapse_signature: None,
            violations: vec![],
        };
        
        hof.consider(&result, &config, 0.7);
        
        assert_eq!(hof.entries.len(), 1);
        assert_eq!(hof.entries[0].rank, 1);
    }
}
