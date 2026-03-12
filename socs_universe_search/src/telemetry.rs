//! 遥测记录系统
//! 
//! CSV时序 + JSON摘要 + Hall of Fame / Graveyard

use crate::evaluation::{EvaluationResult, TickSnapshot};
use crate::stress_profile::StressProfile;
use crate::universe_config::UniverseConfig;
use serde::{Serialize, Deserialize};
use std::fs::{create_dir_all, OpenOptions};
use std::io::{BufWriter, Write};
use std::path::{Path, PathBuf};

/// 宇宙运行摘要
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct UniverseSummary {
    pub universe_id: u64,
    pub family: String,
    pub stress: String,
    pub seed: u64,
    pub config_hash: String,
    pub evaluation: EvaluationResult,
    pub collapse_signature: Option<String>,
    pub passed_gates: usize,
    pub meets_minimum: bool,
    /// CWCI: Code-World Consciousness Index
    /// 代码世界意识指数 - 6维度可测量化
    pub cwci: Option<crate::consciousness_index::CWCIEvaluation>,
    pub consciousness_level: Option<String>,
    pub cwei_score: Option<f32>,
}

/// CSV遥测写入器
pub struct TelemetryWriter {
    csv: BufWriter<std::fs::File>,
    output_dir: PathBuf,
}

impl TelemetryWriter {
    pub fn new(output_dir: impl AsRef<Path>, label: &str) -> std::io::Result<Self> {
        create_dir_all(output_dir.as_ref())?;
        
        let csv_path = output_dir.as_ref().join(format!("{}_telemetry.csv", label));
        let file = OpenOptions::new()
            .create(true)
            .truncate(true)
            .write(true)
            .open(csv_path)?;
        
        let mut csv = BufWriter::new(file);
        writeln!(
            csv,
            "tick,universe_id,family,stress,seed,alive_units,avg_energy,active_clusters,\
             broadcast_count,cluster_entropy,specialization_score,hazard,recovery_event,\
             l1_reads,l2_inheritances,l3_hits"
        )?;
        
        Ok(Self {
            csv,
            output_dir: output_dir.as_ref().to_path_buf(),
        })
    }
    
    /// 写入单个tick
    pub fn write_tick(&mut self, cfg: &UniverseConfig, snap: &TickSnapshot) -> std::io::Result<()> {
        writeln!(
            self.csv,
            "{},{},{},{},{},{},{:.6},{},{},{:.6},{:.6},{:.6},{},{},{},{}",
            snap.tick,
            cfg.universe_id,
            cfg.family.as_str(),
            stress_name(cfg.stress_profile),
            cfg.seed,
            snap.alive_units,
            snap.avg_energy,
            snap.active_clusters,
            snap.broadcast_count,
            snap.cluster_entropy,
            snap.specialization_score,
            snap.hazard,
            snap.recovery_event as u8,
            snap.l1_reads,
            snap.l2_inheritances,
            snap.l3_hits,
        )
    }
    
    /// 刷新缓冲
    pub fn flush(&mut self) -> std::io::Result<()> {
        self.csv.flush()
    }
    
    /// 写入JSON摘要
    pub fn write_summary(&self, label: &str, summary: &UniverseSummary) -> std::io::Result<()> {
        let summary_path = self.output_dir.join(format!("{}_summary.json", label));
        let json = serde_json::to_string_pretty(summary)?;
        std::fs::write(summary_path, json)
    }
}

/// 追加到Hall of Fame
pub fn append_hall_of_fame(output_dir: impl AsRef<Path>, summary: &UniverseSummary) -> std::io::Result<()> {
    append_jsonl(output_dir.as_ref().join("hall_of_fame.jsonl"), summary)
}

/// 追加到Graveyard
pub fn append_graveyard(output_dir: impl AsRef<Path>, summary: &UniverseSummary) -> std::io::Result<()> {
    append_jsonl(output_dir.as_ref().join("graveyard.jsonl"), summary)
}

/// 追加JSON Lines格式
fn append_jsonl(path: PathBuf, summary: &UniverseSummary) -> std::io::Result<()> {
    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)?;
    
    let mut writer = BufWriter::new(file);
    let line = serde_json::to_string(summary)?;
    writeln!(writer, "{}", line)?;
    writer.flush()
}

/// 构建摘要
pub fn build_summary(
    cfg: &UniverseConfig,
    evaluation: EvaluationResult,
    collapse_signature: Option<String>,
    cwci: Option<crate::consciousness_index::CWCIEvaluation>,
) -> UniverseSummary {
    let cwei_score = cwci.as_ref().map(|c| c.cwei_score);
    let consciousness_level = cwci.as_ref().map(|c| c.level.as_str().to_string());
    
    UniverseSummary {
        universe_id: cfg.universe_id,
        family: cfg.family.as_str().to_string(),
        stress: stress_name(cfg.stress_profile).to_string(),
        seed: cfg.seed,
        config_hash: config_hash(cfg),
        passed_gates: evaluation.phenomena.pass_count(),
        meets_minimum: evaluation.phenomena.meets_minimum(),
        evaluation,
        collapse_signature,
        cwci,
        consciousness_level,
        cwei_score,
    }
}

/// 判断是否进Hall of Fame
pub fn should_enter_hall_of_fame(summary: &UniverseSummary) -> bool {
    summary.meets_minimum && summary.collapse_signature.is_none()
}

/// 判断是否进Graveyard
pub fn should_enter_graveyard(summary: &UniverseSummary) -> bool {
    summary.passed_gates <= 2 || summary.collapse_signature.is_some()
}

/// 配置哈希
fn config_hash(cfg: &UniverseConfig) -> String {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};
    
    let mut hasher = DefaultHasher::new();
    cfg.family.as_str().hash(&mut hasher);
    stress_name(cfg.stress_profile).hash(&mut hasher);
    cfg.n_units.hash(&mut hasher);
    cfg.seed.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

/// 压力名称
fn stress_name(stress: StressProfile) -> &'static str {
    stress.as_str()
}

/// 打印运行摘要
pub fn print_run_summary(summary: &UniverseSummary) {
    let total_score = summary.evaluation.scores.attractor_dwell_score 
        + summary.evaluation.scores.persistence_score
        + summary.evaluation.scores.reorganization_score
        + summary.evaluation.scores.specialization_score
        + summary.evaluation.scores.broadcast_score
        + summary.evaluation.scores.recovery_score;
    
    println!(
        "[SUMMARY] u{} {}×{} | Gates {}/6 | Dynamics: {:.2} | {}",
        summary.universe_id,
        summary.family,
        summary.stress,
        summary.passed_gates,
        total_score,
        if summary.meets_minimum { "✓ PASS" } else { "✗ FAIL" }
    );
    
    // 打印CWCI信息
    if let Some(ref cwci) = summary.cwci {
        println!(
            "  [CWCI] Level: {} | Score: {:.3} | Capabilities: {}/6",
            cwci.level.as_str(),
            cwci.cwei_score,
            cwci.passed_capabilities
        );
        
        if cwci.meets_threshold {
            println!("  ✓ Consciousness threshold MET (5/6 capabilities)");
        }
        
        if !cwci.notes.is_empty() {
            for note in &cwci.notes {
                println!("    - {}", note);
            }
        }
    }
    
    if !summary.evaluation.notes.is_empty() {
        for note in &summary.evaluation.notes {
            println!("  - {}", note);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::evaluation::{DynamicsScores, DynamicPhenomena};
    
    #[test]
    fn test_hall_of_fameCriteria() {
        let summary = UniverseSummary {
            universe_id: 0,
            family: "worm_like".to_string(),
            stress: "stable".to_string(),
            seed: 0,
            config_hash: "abc".to_string(),
            evaluation: EvaluationResult {
                scores: DynamicsScores::default(),
                phenomena: DynamicPhenomena {
                    stable_attractors: true,
                    memory_persistence: true,
                    regime_reorganization: true,
                    cluster_specialization: true,
                    global_broadcast_emergence: false,
                    failure_recovery: true,
                },
                notes: vec![],
            },
            collapse_signature: None,
            passed_gates: 5,
            meets_minimum: true,
            cwci: None,
            consciousness_level: None,
            cwei_score: None,
        };
        
        assert!(should_enter_hall_of_fame(&summary));
        assert!(!should_enter_graveyard(&summary));
    }
    
    #[test]
    fn test_graveyardCriteria() {
        let summary = UniverseSummary {
            universe_id: 0,
            family: "random".to_string(),
            stress: "high_competition".to_string(),
            seed: 0,
            config_hash: "def".to_string(),
            evaluation: EvaluationResult {
                scores: DynamicsScores::default(),
                phenomena: DynamicPhenomena {
                    stable_attractors: false,
                    memory_persistence: false,
                    regime_reorganization: false,
                    cluster_specialization: false,
                    global_broadcast_emergence: false,
                    failure_recovery: false,
                },
                notes: vec!["All failed".to_string()],
            },
            collapse_signature: Some("over_sync".to_string()),
            passed_gates: 0,
            meets_minimum: false,
            cwci: None,
            consciousness_level: None,
            cwei_score: None,
        };
        
        assert!(!should_enter_hall_of_fame(&summary));
        assert!(should_enter_graveyard(&summary));
    }
}
