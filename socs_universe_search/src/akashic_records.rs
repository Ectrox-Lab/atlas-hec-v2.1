//! 阿卡西记录系统
//! 
//! 跨宇宙实验记录与结构统计库。
//! 不是"祖先智慧直灌系统"，而是：
//! - 记录每个宇宙的完整配置和时间序列
//! - 统计哪些结构在哪些条件下表现好
//! - 为新一代提供结构偏置（不是具体答案）

use crate::{SearchResult, DynamicsScores, ParameterConfig, ArchitectureFamily};
use std::collections::{HashMap, VecDeque};
use std::fs::{self, File};

use std::path::Path;

/// 阿卡西记录系统
pub struct AkashicRecords {
    /// 所有宇宙的记录
    pub universes: Vec<UniverseRecord>,
    
    /// 事件日志
    pub event_log: VecDeque<AkashicEvent>,
    
    /// 结构统计
    pub structure_stats: StructureStatistics,
    
    /// 名人堂（顶级结构）
    pub hall_of_fame: Vec<HallOfFameEntry>,
    
    /// 墓地（失败结构）
    pub graveyard: Vec<GraveyardEntry>,
    
    /// 最大记录数
    max_records: usize,
}

/// 单个宇宙记录
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct UniverseRecord {
    pub universe_id: String,
    pub timestamp: u64,
    pub config: ParameterConfig,
    pub final_scores: DynamicsScores,
    pub survival_time: u64,
    pub key_events: Vec<UniverseEvent>,
    pub lineage: Option<String>, // 父代宇宙ID
}

/// 宇宙内事件
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct UniverseEvent {
    pub tick: u64,
    pub event_type: EventType,
    pub description: String,
    pub metrics: HashMap<String, f32>,
}

#[derive(Debug, Clone, Copy, PartialEq, serde::Serialize, serde::Deserialize)]
pub enum EventType {
    AttractorFormed,
    AttractorDissolved,
    RegimeShift,
    Failure,
    Recovery,
    BroadcastPeak,
    StructureChange,
}

/// 阿卡西事件（系统级）
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct AkashicEvent {
    pub timestamp: u64,
    pub event_type: AkashicEventType,
    pub universe_id: String,
    pub details: String,
}

#[derive(Debug, Clone, Copy, PartialEq, serde::Serialize, serde::Deserialize)]
pub enum AkashicEventType {
    UniverseCreated,
    UniverseCompleted,
    UniverseFailed,
    HallOfFameEntry,
    GraveyardEntry,
    PatternDiscovered,
}

/// 架构家族统计记录
#[derive(Debug, Clone, Default, serde::Serialize, serde::Deserialize)]
pub struct FamilyStatsRecord {
    pub count: usize,
    pub total_score: f32,
    pub passed_gates: usize,
}

impl FamilyStatsRecord {
    pub fn average_score(&self) -> f32 {
        self.total_score / self.count.max(1) as f32
    }
    
    pub fn pass_rate(&self) -> f32 {
        self.passed_gates as f32 / self.count.max(1) as f32
    }
}

/// 结构统计
#[derive(Debug, Clone, Default, serde::Serialize, serde::Deserialize)]
pub struct StructureStatistics {
    /// 按架构家族统计
    pub by_architecture: HashMap<String, FamilyStatsRecord>,
    
    /// 参数-性能关联
    pub parameter_correlations: HashMap<String, f32>,
    
    /// 成功模式模板
    pub success_patterns: Vec<SuccessPattern>,
    
    /// 失败模式模板
    pub failure_patterns: Vec<FailurePattern>,
}

/// 成功模式
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct SuccessPattern {
    pub pattern_id: String,
    pub description: String,
    pub key_parameters: HashMap<String, f32>,
    pub average_score: f32,
    pub occurrence_count: usize,
    pub example_universes: Vec<String>,
}

/// 失败模式
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct FailurePattern {
    pub pattern_id: String,
    pub description: String,
    pub key_parameters: HashMap<String, f32>,
    pub failure_mode: String,
    pub occurrence_count: usize,
}

/// 名人堂条目
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct HallOfFameEntry {
    pub rank: usize,
    pub universe_id: String,
    pub total_score: f32,
    pub config_summary: String,
    pub key_strengths: Vec<String>,
    pub inducted_at: u64,
}

/// 墓地条目
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct GraveyardEntry {
    pub universe_id: String,
    pub cause_of_death: String,
    pub survival_time: u64,
    pub lessons_learned: String,
}

impl AkashicRecords {
    pub fn new() -> Self {
        Self {
            universes: Vec::new(),
            event_log: VecDeque::with_capacity(10000),
            structure_stats: StructureStatistics::default(),
            hall_of_fame: Vec::new(),
            graveyard: Vec::new(),
            max_records: 100000,
        }
    }
    
    /// 记录一个宇宙的结果
    pub fn record(&mut self, result: &SearchResult) {
        let record = UniverseRecord {
            universe_id: result.universe_id.clone(),
            timestamp: current_timestamp(),
            config: result.parameter_config.clone(),
            final_scores: result.dynamics_scores.clone(),
            survival_time: result.survival_time,
            key_events: vec![], // 简化
            lineage: None,
        };
        
        // 检查是否进名人堂
        if self.should_enter_hall_of_fame(&result.dynamics_scores) {
            self.add_to_hall_of_fame(result);
        }
        
        // 检查是否进墓地
        if result.dynamics_scores.total() < 1.0 {
            self.add_to_graveyard(result);
        }
        
        // 更新统计
        self.update_statistics(result);
        
        // 存储记录
        self.universes.push(record);
        
        // 记录事件
        self.log_event(AkashicEvent {
            timestamp: current_timestamp(),
            event_type: AkashicEventType::UniverseCompleted,
            universe_id: result.universe_id.clone(),
            details: format!("Score: {:.2}", result.dynamics_scores.total()),
        });
        
        // 限制记录数
        if self.universes.len() > self.max_records {
            self.universes.remove(0);
        }
    }
    
    /// 检查是否该进名人堂
    fn should_enter_hall_of_fame(&self, scores: &DynamicsScores) -> bool {
        if self.hall_of_fame.len() < 100 {
            return scores.total() > 3.0;
        }
        
        scores.total() > self.hall_of_fame.last().map(|e| e.total_score).unwrap_or(0.0)
    }
    
    /// 加入名人堂
    fn add_to_hall_of_fame(&mut self, result: &SearchResult) {
        let entry = HallOfFameEntry {
            rank: 0, // 稍后计算
            universe_id: result.universe_id.clone(),
            total_score: result.dynamics_scores.total(),
            config_summary: format!("{:?}", result.architecture_family),
            key_strengths: self.identify_strengths(&result.dynamics_scores),
            inducted_at: current_timestamp(),
        };
        
        self.hall_of_fame.push(entry);
        
        // 排序并限制大小
        self.hall_of_fame.sort_by(|a, b| {
            b.total_score.partial_cmp(&a.total_score).unwrap()
        });
        
        if self.hall_of_fame.len() > 100 {
            self.hall_of_fame.truncate(100);
        }
        
        // 更新排名
        for (i, entry) in self.hall_of_fame.iter_mut().enumerate() {
            entry.rank = i + 1;
        }
        
        self.log_event(AkashicEvent {
            timestamp: current_timestamp(),
            event_type: AkashicEventType::HallOfFameEntry,
            universe_id: result.universe_id.clone(),
            details: format!("Rank {}, Score {:.2}", 
                self.hall_of_fame.iter().position(|e| e.universe_id == result.universe_id).unwrap_or(0) + 1,
                result.dynamics_scores.total()),
        });
    }
    
    /// 加入墓地
    fn add_to_graveyard(&mut self, result: &SearchResult) {
        let entry = GraveyardEntry {
            universe_id: result.universe_id.clone(),
            cause_of_death: self.diagnose_failure(&result.dynamics_scores),
            survival_time: result.survival_time,
            lessons_learned: String::new(), // 简化
        };
        
        self.graveyard.push(entry);
    }
    
    /// 更新统计
    fn update_statistics(&mut self, result: &SearchResult) {
        let arch = result.architecture_family;
        let arch_name = format!("{:?}", arch);
        let stats = self.structure_stats.by_architecture
            .entry(arch_name)
            .or_insert_with(FamilyStatsRecord::default);
        
        stats.count += 1;
        stats.total_score += result.dynamics_scores.total();
        
        if result.dynamics_scores.all_gates_passed(0.5) {
            stats.passed_gates += 1;
        }
        
        // 更新参数关联
        self.structure_stats.parameter_correlations
            .entry("learning_rate".to_string())
            .and_modify(|v| *v += result.parameter_config.learning_rate * result.dynamics_scores.total())
            .or_insert(result.parameter_config.learning_rate * result.dynamics_scores.total());
    }
    
    /// 识别强项
    fn identify_strengths(&self, scores: &DynamicsScores) -> Vec<String> {
        let mut strengths = Vec::new();
        
        if scores.attractor_formation > 0.7 {
            strengths.push("Strong Attractors".to_string());
        }
        if scores.memory_persistence > 0.7 {
            strengths.push("Persistent Memory".to_string());
        }
        if scores.failure_recovery > 0.7 {
            strengths.push("Resilient Recovery".to_string());
        }
        if scores.broadcast_emergence > 0.7 {
            strengths.push("Global Integration".to_string());
        }
        
        strengths
    }
    
    /// 诊断失败原因
    fn diagnose_failure(&self, scores: &DynamicsScores) -> String {
        if scores.attractor_formation < 0.2 {
            "No stable attractors formed".to_string()
        } else if scores.memory_persistence < 0.2 {
            "Memory not persistent".to_string()
        } else if scores.failure_recovery < 0.2 {
            "Could not recover from failure".to_string()
        } else {
            "General underperformance".to_string()
        }
    }
    
    /// 记录事件
    fn log_event(&mut self, event: AkashicEvent) {
        self.event_log.push_back(event);
        if self.event_log.len() > 10000 {
            self.event_log.pop_front();
        }
    }
    
    /// 获取洞察
    pub fn insights(&self) -> AkashicInsights {
        AkashicInsights {
            total_universes: self.universes.len(),
            hall_of_fame_size: self.hall_of_fame.len(),
            graveyard_size: self.graveyard.len(),
            best_architecture: self.find_best_architecture(),
            common_failure_modes: self.analyze_failure_patterns(),
            recommended_parameters: self.generate_recommendations(),
        }
    }
    
    /// 找出最佳架构
    fn find_best_architecture(&self) -> Option<(String, f32)> {
        self.structure_stats.by_architecture.iter()
            .map(|(arch, stats)| (arch.clone(), stats.average_score()))
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
    }
    
    /// 分析失败模式
    fn analyze_failure_patterns(&self) -> Vec<String> {
        let mut patterns: HashMap<String, usize> = HashMap::new();
        
        for entry in &self.graveyard {
            *patterns.entry(entry.cause_of_death.clone()).or_insert(0) += 1;
        }
        
        let mut sorted: Vec<_> = patterns.into_iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(&a.1));
        
        sorted.into_iter().take(5).map(|(p, _)| p).collect()
    }
    
    /// 生成参数推荐
    fn generate_recommendations(&self) -> HashMap<String, f32> {
        let mut recommendations = HashMap::new();
        
        // 基于名人堂统计推荐参数
        let top_configs: Vec<_> = self.hall_of_fame.iter()
            .take(10)
            .filter_map(|e| self.universes.iter().find(|u| u.universe_id == e.universe_id))
            .collect();
        
        if !top_configs.is_empty() {
            let avg_lr: f32 = top_configs.iter().map(|u| u.config.learning_rate).sum::<f32>() 
                / top_configs.len() as f32;
            recommendations.insert("learning_rate".to_string(), avg_lr);
            
            let avg_density: f32 = top_configs.iter().map(|u| u.config.connection_density).sum::<f32>()
                / top_configs.len() as f32;
            recommendations.insert("connection_density".to_string(), avg_density);
        }
        
        recommendations
    }
    
    /// 保存到文件
    pub fn save_to_disk(&self, base_path: &str) -> Result<(), std::io::Error> {
        fs::create_dir_all(base_path)?;
        
        // 保存名人堂
        let hall_file = File::create(Path::new(base_path).join("hall_of_fame.json"))?;
        serde_json::to_writer_pretty(hall_file, &self.hall_of_fame)?;
        
        // 保存墓地
        let grave_file = File::create(Path::new(base_path).join("graveyard.json"))?;
        serde_json::to_writer_pretty(grave_file, &self.graveyard)?;
        
        // 保存统计
        let stats_file = File::create(Path::new(base_path).join("statistics.json"))?;
        serde_json::to_writer_pretty(stats_file, &self.structure_stats)?;
        
        // 保存最近事件
        let events_file = File::create(Path::new(base_path).join("recent_events.json"))?;
        let recent: Vec<_> = self.event_log.iter().rev().take(1000).collect();
        serde_json::to_writer_pretty(events_file, &recent)?;
        
        Ok(())
    }
}

/// 阿卡西洞察
#[derive(Debug, Clone)]
pub struct AkashicInsights {
    pub total_universes: usize,
    pub hall_of_fame_size: usize,
    pub graveyard_size: usize,
    pub best_architecture: Option<(String, f32)>,
    pub common_failure_modes: Vec<String>,
    pub recommended_parameters: HashMap<String, f32>,
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
    fn test_akashic_record() {
        let mut akashic = AkashicRecords::new();
        
        let result = SearchResult {
            universe_id: "test_001".to_string(),
            architecture_family: ArchitectureFamily::WormLike,
            parameter_config: ParameterConfig::from_architecture(ArchitectureFamily::WormLike, 1),
            dynamics_scores: DynamicsScores {
                attractor_formation: 0.8,
                memory_persistence: 0.7,
                reorganization: 0.6,
                cluster_specialization: 0.9,
                broadcast_emergence: 0.5,
                failure_recovery: 0.8,
            },
            survival_time: 10000,
            stability_rating: 0.85,
        };
        
        akashic.record(&result);
        
        assert_eq!(akashic.universes.len(), 1);
        assert!(!akashic.hall_of_fame.is_empty());
    }
}
