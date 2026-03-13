//! 6个动力学验证协议
//! 
//! 唯一主门：不看benchmark分数，只看涌现现象

use serde::{Serialize, Deserialize};

/// 崩溃特征签名
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum CollapseSignature {
    OverSynchronization,    // 过同步
    BroadcastTyranny,       // 广播霸权
    MemoryRunaway,          // 记忆失控
    AttractorLock,          // 吸引子锁死
    RecoveryFailure,        // 恢复失败
    EnergyRunaway,          // 能量失控
}

/// 6动力学分数
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct DynamicsScores {
    pub attractor_dwell_score: f32,      // D1: 稳定吸引子
    pub persistence_score: f32,          // D2: 记忆持久
    pub reorganization_score: f32,       // D3: 重组能力
    pub specialization_score: f32,       // D4: 团簇分化
    pub broadcast_score: f32,            // D5: 全局广播
    pub recovery_score: f32,             // D6: 故障恢复
}

/// 6动力学现象布尔门
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct DynamicPhenomena {
    pub stable_attractors: bool,
    pub memory_persistence: bool,
    pub regime_reorganization: bool,
    pub cluster_specialization: bool,
    pub global_broadcast_emergence: bool,
    pub failure_recovery: bool,
}

impl DynamicPhenomena {
    /// 通过的门数
    pub fn pass_count(&self) -> usize {
        [
            self.stable_attractors,
            self.memory_persistence,
            self.regime_reorganization,
            self.cluster_specialization,
            self.global_broadcast_emergence,
            self.failure_recovery,
        ]
        .into_iter()
        .filter(|x| *x)
        .count()
    }
    
    /// 是否通过最低门限（4/6）
    pub fn meets_minimum(&self) -> bool {
        self.pass_count() >= 4
    }
}

/// 完整评估结果
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct EvaluationResult {
    pub scores: DynamicsScores,
    pub phenomena: DynamicPhenomena,
    pub notes: Vec<String>,
}

/// Tick快照（从真实SOCS状态读取）
#[derive(Clone, Debug, Default)]
pub struct TickSnapshot {
    pub tick: usize,
    pub alive_units: usize,
    pub active_clusters: usize,
    pub attractor_id: Option<u64>,
    pub cluster_entropy: f32,
    pub specialization_score: f32,
    pub broadcast_count: usize,
    pub avg_prediction_error: f32,
    pub avg_energy: f32,
    pub hazard: f32,
    pub recovery_event: bool,
    
    // 记忆统计
    pub l1_reads: usize,
    pub l2_inheritances: usize,
    pub l3_hits: usize,
}

/// 评估动力学
pub fn evaluate_dynamics(history: &[TickSnapshot]) -> EvaluationResult {
    let mut notes = Vec::new();
    
    let attractor_dwell_score = score_stable_attractors(history);
    let persistence_score = score_memory_persistence(history);
    let reorganization_score = score_regime_reorganization(history);
    let specialization_score = score_cluster_specialization(history);
    let broadcast_score = score_global_broadcast(history);
    let recovery_score = score_failure_recovery(history);
    
    let scores = DynamicsScores {
        attractor_dwell_score,
        persistence_score,
        reorganization_score,
        specialization_score,
        broadcast_score,
        recovery_score,
    };
    
    // 阈值判断（可调）
    let phenomena = DynamicPhenomena {
        stable_attractors: attractor_dwell_score >= 0.60,
        memory_persistence: persistence_score >= 0.55,
        regime_reorganization: reorganization_score >= 0.55,
        cluster_specialization: specialization_score >= 0.55,
        global_broadcast_emergence: broadcast_score >= 0.50,
        failure_recovery: recovery_score >= 0.55,
    };
    
    if phenomena.pass_count() < 4 {
        notes.push(format!(
            "Universe failed minimum threshold: {}/6 dynamic phenomena",
            phenomena.pass_count()
        ));
    }
    
    // 添加具体强项/弱项说明
    if phenomena.stable_attractors {
        notes.push(format!("Strong attractors (dwell={:.2})", attractor_dwell_score));
    }
    if phenomena.memory_persistence {
        notes.push(format!("Persistent memory (score={:.2})", persistence_score));
    }
    if phenomena.failure_recovery {
        notes.push(format!("Resilient recovery (score={:.2})", recovery_score));
    }
    
    EvaluationResult { scores, phenomena, notes }
}

// ============ 具体评分函数 ============

/// D1: 稳定吸引子评分
/// 基于attractor停留时间和稳定性
fn score_stable_attractors(history: &[TickSnapshot]) -> f32 {
    if history.len() < 100 {
        return 0.0;
    }
    
    let mut longest_run = 0usize;
    let mut current_run = 0usize;
    let mut prev: Option<u64> = None;
    let mut total_attractor_time = 0usize;
    
    for h in history {
        if let Some(aid) = h.attractor_id {
            total_attractor_time += 1;
            if Some(aid) == prev {
                current_run += 1;
            } else {
                current_run = 1;
                prev = Some(aid);
            }
            longest_run = longest_run.max(current_run);
        } else {
            current_run = 0;
            prev = None;
        }
    }
    
    // 长时间停留 + 高占比 = 高分
    let dwell_ratio = longest_run as f32 / history.len() as f32;
    let coverage = total_attractor_time as f32 / history.len() as f32;
    
    (dwell_ratio * 0.6 + coverage * 0.4).clamp(0.0, 1.0)
}

/// D2: 记忆持久评分
/// 基于状态稳定性和抗干扰能力
fn score_memory_persistence(history: &[TickSnapshot]) -> f32 {
    if history.len() < 2 {
        return 0.0;
    }
    
    // 能量稳定性作为记忆代理
    let energies: Vec<_> = history.iter().map(|h| h.avg_energy).collect();
    let mean = energies.iter().sum::<f32>() / energies.len() as f32;
    let variance = energies.iter()
        .map(|&e| (e - mean).powi(2))
        .sum::<f32>() / energies.len() as f32;
    
    // 低方差 = 高稳定性
    let stability = (1.0 - variance.sqrt() * 2.0).max(0.0).min(1.0);
    
    // 预测误差低 = 记忆有效
    let avg_error = history.iter().map(|h| h.avg_prediction_error).sum::<f32>() 
        / history.len() as f32;
    let prediction_quality = (1.0 - avg_error).max(0.0);
    
    (stability * 0.6 + prediction_quality * 0.4).clamp(0.0, 1.0)
}

/// D3: 重组能力评分
/// 基于环境变化后的适应速度
fn score_regime_reorganization(history: &[TickSnapshot]) -> f32 {
    if history.len() < 20 {
        return 0.0;
    }
    
    let mid = history.len() / 2;
    let pre = &history[..mid];
    let post = &history[mid..];
    
    // 团簇数变化 = 重组发生
    let pre_clusters = pre.iter().map(|h| h.active_clusters as f32).sum::<f32>() 
        / pre.len().max(1) as f32;
    let post_clusters = post.iter().map(|h| h.active_clusters as f32).sum::<f32>() 
        / post.len().max(1) as f32;
    
    let reorganization_magnitude = (post_clusters - pre_clusters).abs();
    
    // 后期稳定性 = 重组成功
    let post_stability = if post.len() >= 10 {
        let recent: Vec<_> = post.iter().rev().take(10).map(|h| h.active_clusters).collect();
        let variance = recent.iter()
            .map(|&c| (c as f32 - post_clusters).powi(2))
            .sum::<f32>() / 10.0;
        (1.0 - variance.sqrt() / 10.0).max(0.0)
    } else {
        0.5
    };
    
    (reorganization_magnitude.min(1.0) * 0.4 + post_stability * 0.6).clamp(0.0, 1.0)
}

/// D4: 团簇分化评分
/// 基于团簇间差异度和角色多样性
fn score_cluster_specialization(history: &[TickSnapshot]) -> f32 {
    if history.is_empty() {
        return 0.0;
    }
    
    // 直接使用记录的specialization_score
    let avg: f32 = history.iter().map(|h| h.specialization_score).sum::<f32>() 
        / history.len() as f32;
    
    // 熵作为多样性的代理
    let avg_entropy: f32 = history.iter().map(|h| h.cluster_entropy).sum::<f32>() 
        / history.len() as f32;
    
    (avg * 0.6 + avg_entropy * 0.4).clamp(0.0, 1.0)
}

/// D5: 全局广播涌现评分
/// 基于广播激活度和竞争有序性
fn score_global_broadcast(history: &[TickSnapshot]) -> f32 {
    if history.is_empty() {
        return 0.0;
    }
    
    // 广播活跃比例
    let active_ratio = history.iter()
        .filter(|h| h.broadcast_count > 0)
        .count() as f32 / history.len() as f32;
    
    // 广播次数适中（不过度也不缺失）
    let avg_broadcast: f32 = history.iter()
        .map(|h| h.broadcast_count as f32)
        .sum::<f32>() / history.len() as f32;
    
    // 理想范围：0.5-2.0 个广播/tick
    let broadcast_quality = if avg_broadcast > 0.5 && avg_broadcast < 3.0 {
        1.0 - (avg_broadcast - 1.5).abs() / 2.0
    } else {
        0.3
    };
    
    (active_ratio * 0.5 + broadcast_quality * 0.5).clamp(0.0, 1.0)
}

/// D6: 故障恢复评分
/// 基于从hazard中恢复的能力
fn score_failure_recovery(history: &[TickSnapshot]) -> f32 {
    if history.is_empty() {
        return 0.0;
    }
    
    // 恢复事件数
    let recovery_count = history.iter().filter(|h| h.recovery_event).count() as f32;
    
    // 平均hazard水平
    let avg_hazard: f32 = history.iter().map(|h| h.hazard).sum::<f32>() 
        / history.len() as f32;
    
    // 有恢复事件 + 低平均hazard = 高恢复能力
    if recovery_count == 0.0 {
        // 无恢复事件可能是因为无故障或无法恢复
        if avg_hazard > 0.3 {
            return 0.2; // 高hazard但无恢复 = 差
        } else {
            return 0.6; // 低hazard无恢复 = 正常
        }
    }
    
    let recovery_rate = recovery_count / history.len() as f32 * 50.0; // 归一化
    let hazard_penalty = avg_hazard * 0.5;
    
    (recovery_rate - hazard_penalty + 0.3).clamp(0.0, 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    fn mock_history() -> Vec<TickSnapshot> {
        (0..1000).map(|i| TickSnapshot {
            tick: i,
            alive_units: 900,
            active_clusters: 3 + (i % 5),
            attractor_id: Some((i / 200) as u64 % 3),
            cluster_entropy: 0.6 + (i as f32 / 10000.0),
            specialization_score: 0.5 + (i as f32 / 2000.0),
            broadcast_count: if i % 10 == 0 { 1 } else { 0 },
            avg_prediction_error: 0.2,
            avg_energy: 0.7,
            hazard: 0.1,
            recovery_event: i % 400 == 0 && i > 0,
            l1_reads: 100,
            l2_inheritances: 10,
            l3_hits: 1,
        }).collect()
    }
    
    #[test]
    fn test_evaluate_dynamics() {
        let history = mock_history();
        let eval = evaluate_dynamics(&history);
        
        assert!(eval.scores.attractor_dwell_score >= 0.0);
        assert!(eval.scores.attractor_dwell_score <= 1.0);
        assert!(eval.phenomena.pass_count() >= 0);
        assert!(eval.phenomena.pass_count() <= 6);
    }
    
    #[test]
    fn test_pass_count() {
        let phenom = DynamicPhenomena {
            stable_attractors: true,
            memory_persistence: true,
            regime_reorganization: false,
            cluster_specialization: true,
            global_broadcast_emergence: false,
            failure_recovery: true,
        };
        
        assert_eq!(phenom.pass_count(), 4);
        assert!(phenom.meets_minimum());
    }
}
