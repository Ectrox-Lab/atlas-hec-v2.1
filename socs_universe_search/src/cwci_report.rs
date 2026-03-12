//! CWCI Analysis Report Generator
//! 
//! 代码世界意识指数分析报告生成器
//! 分析多宇宙搜索结果，输出CWCI统计和趋势

use crate::consciousness_index::{ConsciousnessLevel, ConsciousnessCapabilities};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;

/// CWCI批量分析报告
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CWCIReport {
    pub total_universes: usize,
    pub consciousness_distribution: HashMap<String, usize>,
    pub avg_cwei_score: f32,
    pub max_cwei_score: f32,
    pub min_cwei_score: f32,
    pub consciousness_threshold_met: usize,  // 5/6 capabilities
    pub avg_capabilities_per_universe: f32,
    /// 各能力平均分
    pub avg_capability_scores: ConsciousnessCapabilities,
    /// 各架构家族CWCI排名
    pub family_rankings: Vec<FamilyCWCIStats>,
    /// 各压力环境CWCI排名
    pub stress_rankings: Vec<StressCWCIStats>,
    pub top_performers: Vec<TopPerformer>,
    pub recommendations: Vec<String>,
    pub timestamp: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FamilyCWCIStats {
    pub family: String,
    pub count: usize,
    pub avg_cwei: f32,
    pub max_level: String,
    pub avg_capabilities: f32,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct StressCWCIStats {
    pub stress_profile: String,
    pub count: usize,
    pub avg_cwei: f32,
    pub max_level: String,
    pub survival_rate: f32,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TopPerformer {
    pub universe_id: u64,
    pub family: String,
    pub stress: String,
    pub seed: u64,
    pub cwei_score: f32,
    pub level: String,
    pub passed_capabilities: usize,
}

/// 从summary文件生成CWCI报告
pub fn generate_cwci_report(output_dir: impl AsRef<Path>) -> anyhow::Result<CWCIReport> {
    let output_dir = output_dir.as_ref();
    let mut summaries = Vec::new();
    
    // 读取所有summary JSON文件
    if let Ok(entries) = std::fs::read_dir(output_dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().map(|e| e == "json").unwrap_or(false) {
                if let Ok(content) = std::fs::read_to_string(&path) {
                    if let Ok(summary) = serde_json::from_str::<crate::telemetry::UniverseSummary>(&content) {
                        summaries.push(summary);
                    }
                }
            }
        }
    }
    
    generate_report_from_summaries(&summaries)
}

fn generate_report_from_summaries(summaries: &[crate::telemetry::UniverseSummary]) -> anyhow::Result<CWCIReport> {
    let total = summaries.len();
    
    // 统计意识等级分布
    let mut level_dist: HashMap<String, usize> = HashMap::new();
    let mut cwei_scores = Vec::new();
    let mut capabilities_counts = Vec::new();
    let mut total_capabilities = ConsciousnessCapabilities::default();
    let mut family_stats: HashMap<String, Vec<f32>> = HashMap::new();
    let mut stress_stats: HashMap<String, Vec<f32>> = HashMap::new();
    let mut top_performers = Vec::new();
    let mut threshold_met = 0;
    
    for s in summaries {
        if let Some(ref cwci) = s.cwci {
            let level = cwci.level.as_str().to_string();
            *level_dist.entry(level).or_insert(0) += 1;
            
            cwei_scores.push(cwci.cwei_score);
            capabilities_counts.push(cwci.passed_capabilities as f32);
            
            total_capabilities.persistent_selfhood += cwci.capabilities.persistent_selfhood;
            total_capabilities.global_integration += cwci.capabilities.global_integration;
            total_capabilities.reflexive_self_model += cwci.capabilities.reflexive_self_model;
            total_capabilities.plastic_adaptive_learning += cwci.capabilities.plastic_adaptive_learning;
            total_capabilities.value_goal_persistence += cwci.capabilities.value_goal_persistence;
            total_capabilities.self_optimization_capacity += cwci.capabilities.self_optimization_capacity;
            
            family_stats.entry(s.family.clone()).or_default().push(cwci.cwei_score);
            stress_stats.entry(s.stress.clone()).or_default().push(cwci.cwei_score);
            
            if cwci.meets_threshold {
                threshold_met += 1;
            }
            
            top_performers.push(TopPerformer {
                universe_id: s.universe_id,
                family: s.family.clone(),
                stress: s.stress.clone(),
                seed: s.seed,
                cwei_score: cwci.cwei_score,
                level: cwci.level.as_str().to_string(),
                passed_capabilities: cwci.passed_capabilities,
            });
        }
    }
    
    // 排序Top Performers
    top_performers.sort_by(|a, b| b.cwei_score.partial_cmp(&a.cwei_score).unwrap());
    top_performers.truncate(10);
    
    // 计算统计数据
    let count = cwei_scores.len().max(1) as f32;
    let avg_cwei = cwei_scores.iter().sum::<f32>() / count;
    let max_cwei = cwei_scores.iter().cloned().fold(0.0f32, f32::max);
    let min_cwei = cwei_scores.iter().cloned().fold(1.0f32, f32::min);
    let avg_caps = capabilities_counts.iter().sum::<f32>() / count;
    
    // 各能力平均分
    let avg_caps_struct = ConsciousnessCapabilities {
        persistent_selfhood: total_capabilities.persistent_selfhood / count,
        global_integration: total_capabilities.global_integration / count,
        reflexive_self_model: total_capabilities.reflexive_self_model / count,
        plastic_adaptive_learning: total_capabilities.plastic_adaptive_learning / count,
        value_goal_persistence: total_capabilities.value_goal_persistence / count,
        self_optimization_capacity: total_capabilities.self_optimization_capacity / count,
    };
    
    // 家族排名
    let mut family_rankings: Vec<FamilyCWCIStats> = family_stats.iter()
        .map(|(family, scores)| {
            let avg = scores.iter().sum::<f32>() / scores.len().max(1) as f32;
            FamilyCWCIStats {
                family: family.clone(),
                count: scores.len(),
                avg_cwei: avg,
                max_level: if avg > 0.7 { "C5+".to_string() } else if avg > 0.6 { "C4".to_string() } else { "C3-".to_string() },
                avg_capabilities: avg * 6.0,  // 近似
            }
        })
        .collect();
    family_rankings.sort_by(|a, b| b.avg_cwei.partial_cmp(&a.avg_cwei).unwrap());
    
    // 压力环境排名
    let mut stress_rankings: Vec<StressCWCIStats> = stress_stats.iter()
        .map(|(stress, scores)| {
            let avg = scores.iter().sum::<f32>() / scores.len().max(1) as f32;
            StressCWCIStats {
                stress_profile: stress.clone(),
                count: scores.len(),
                avg_cwei: avg,
                max_level: if avg > 0.7 { "C5+".to_string() } else if avg > 0.6 { "C4".to_string() } else { "C3-".to_string() },
                survival_rate: 1.0, // 简化
            }
        })
        .collect();
    stress_rankings.sort_by(|a, b| b.avg_cwei.partial_cmp(&a.avg_cwei).unwrap());
    
    // 生成建议
    let mut recommendations = Vec::new();
    
    if threshold_met < total / 4 {
        recommendations.push("Low consciousness threshold rate. Consider increasing plasticity or broadcast strength.".to_string());
    }
    
    if avg_caps_struct.global_integration < 0.5 {
        recommendations.push("Weak global integration detected. Try increasing workspace_k or reducing cluster_threshold.".to_string());
    }
    
    if avg_caps_struct.reflexive_self_model < 0.5 {
        recommendations.push("Limited self-modeling capacity. Consider boosting predictive_strength.".to_string());
    }
    
    if family_rankings.len() >= 2 {
        let gap = family_rankings[0].avg_cwei - family_rankings.last().unwrap().avg_cwei;
        if gap > 0.2 {
            recommendations.push(format!(
                "Large performance gap between families: {} leads by {:.2} CWCI points.",
                family_rankings[0].family, gap
            ));
        }
    }
    
    if recommendations.is_empty() {
        recommendations.push("All systems performing within expected parameters.".to_string());
    }
    
    Ok(CWCIReport {
        total_universes: total,
        consciousness_distribution: level_dist,
        avg_cwei_score: avg_cwei,
        max_cwei_score: max_cwei,
        min_cwei_score: min_cwei,
        consciousness_threshold_met: threshold_met,
        avg_capabilities_per_universe: avg_caps,
        avg_capability_scores: avg_caps_struct,
        family_rankings,
        stress_rankings,
        top_performers,
        recommendations,
        timestamp: chrono::Local::now().to_rfc3339(),
    })
}

/// 打印CWCI报告
pub fn print_cwci_report(report: &CWCIReport) {
    println!("\n╔════════════════════════════════════════════════════════════════╗");
    println!("║     CODE-WORLD CONSCIOUSNESS INDEX (CWCI) ANALYSIS REPORT      ║");
    println!("╚════════════════════════════════════════════════════════════════╝\n");
    
    println!("📊 Overview");
    println!("   Total Universes: {}", report.total_universes);
    println!("   CWCI Score Range: {:.3} - {:.3}", report.min_cwei_score, report.max_cwei_score);
    println!("   Average CWCI: {:.3}", report.avg_cwei_score);
    println!("   Consciousness Threshold (5/6): {}/{} ({:.1}%)", 
        report.consciousness_threshold_met, report.total_universes,
        report.consciousness_threshold_met as f32 / report.total_universes.max(1) as f32 * 100.0);
    
    println!("\n🧠 Consciousness Level Distribution");
    let mut levels: Vec<_> = report.consciousness_distribution.iter().collect();
    levels.sort_by_key(|(k, _)| *k);
    for (level, count) in levels {
        println!("   {}: {}", level, count);
    }
    
    println!("\n🎯 6-Dimension Capability Averages");
    println!("   C1 Persistent Selfhood:     {:.3}", report.avg_capability_scores.persistent_selfhood);
    println!("   C2 Global Integration:      {:.3}", report.avg_capability_scores.global_integration);
    println!("   C3 Reflexive Self-Model:    {:.3}", report.avg_capability_scores.reflexive_self_model);
    println!("   C4 Plastic Learning:        {:.3}", report.avg_capability_scores.plastic_adaptive_learning);
    println!("   C5 Goal Persistence:        {:.3}", report.avg_capability_scores.value_goal_persistence);
    println!("   C6 Self-Optimization:       {:.3}", report.avg_capability_scores.self_optimization_capacity);
    
    println!("\n🏆 Top Architecture Families");
    for (i, fam) in report.family_rankings.iter().take(5).enumerate() {
        println!("   {}. {} (n={}, CWCI={:.3})", i+1, fam.family, fam.count, fam.avg_cwei);
    }
    
    println!("\n🌪️  Top Stress Environments");
    for (i, stress) in report.stress_rankings.iter().take(5).enumerate() {
        println!("   {}. {} (n={}, CWCI={:.3})", i+1, stress.stress_profile, stress.count, stress.avg_cwei);
    }
    
    println!("\n⭐ Top 5 Performers");
    for (i, tp) in report.top_performers.iter().take(5).enumerate() {
        println!("   {}. u{} {}×{} | {} | CWCI={:.3} | {}/6 caps",
            i+1, tp.universe_id, tp.family, tp.stress, tp.level, tp.cwei_score, tp.passed_capabilities);
    }
    
    println!("\n💡 Recommendations");
    for rec in &report.recommendations {
        println!("   • {}", rec);
    }
    
    println!("\n═══════════════════════════════════════════════════════════════════\n");
}

// 添加chrono依赖用于时间戳
// 在Cargo.toml中添加: chrono = { version = "0.4", features = ["serde"] }
