//! Trace Logger
//! 
//! 核心职责：记录每 step 的完整状态，用于 A/B 实验分析
//! 
//! 记录字段：
//! step, energy, fatigue, thermal_load, stability_score, reward_velocity, prediction_error,
//! risk_score, dominant_factor, action, 
//! exploration_rate, reward_bias, plasticity_scale, compute_budget, recovery_mode, step_rate_limit,
//! p3_enabled

use crate::self_preservation::{HomeostasisState, PreservationAction, SurvivalRiskEstimate};
use crate::p3_runtime_integration::RuntimeParameters;
use std::fs::File;
use std::io::{Write, BufWriter};
use std::path::Path;

/// 追踪日志记录器
pub struct TraceLogger {
    writer: Option<BufWriter<File>>,
    log_path: String,
    buffer: Vec<TraceRecord>,
    flush_interval: usize,
}

/// 单条 trace 记录
#[derive(Clone, Debug)]
pub struct TraceRecord {
    pub step: u64,
    pub timestamp_ms: u128,
    
    // HomeostasisState
    pub energy: f32,
    pub fatigue: f32,
    pub thermal_load: f32,
    pub stability_score: f32,
    pub reward_velocity: f32,
    pub prediction_error: f32,
    
    // Risk estimate (optional)
    pub risk_score: Option<f32>,
    pub dominant_factor: Option<String>,
    
    // Action
    pub action: String,
    
    // Runtime parameters
    pub exploration_rate: f32,
    pub reward_bias: f32,
    pub plasticity_scale: f32,
    pub compute_budget: f32,
    pub recovery_mode: bool,
    pub step_rate_limit: f32,
    
    // Config
    pub p3_enabled: bool,
}

impl TraceLogger {
    /// 创建新的 trace logger
    pub fn new(log_path: &str) -> Self {
        let mut logger = Self {
            writer: None,
            log_path: log_path.to_string(),
            buffer: Vec::with_capacity(1000),
            flush_interval: 100,
        };
        
        // 初始化文件并写入 header
        if let Err(e) = logger.init_file() {
            eprintln!("⚠️ TraceLogger init failed: {}", e);
        }
        
        logger
    }
    
    /// 初始化日志文件
    fn init_file(&mut self) -> std::io::Result<()> {
        let path = Path::new(&self.log_path);
        
        // 创建目录
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        
        let file = File::create(path)?;
        let mut writer = BufWriter::new(file);
        
        // 写入 CSV header
        writeln!(writer, "{}", Self::csv_header())?;
        writer.flush()?;
        
        self.writer = Some(writer);
        Ok(())
    }
    
    /// CSV header
    fn csv_header() -> &'static str {
        "step,timestamp_ms,energy,fatigue,thermal_load,stability_score,reward_velocity,prediction_error,risk_score,dominant_factor,action,exploration_rate,reward_bias,plasticity_scale,compute_budget,recovery_mode,step_rate_limit,p3_enabled"
    }
    
    /// 记录一个 step
    pub fn log_step(
        &mut self,
        step: u64,
        homeostasis: &HomeostasisState,
        risk: Option<&SurvivalRiskEstimate>,
        action: &PreservationAction,
        params: &RuntimeParameters,
        p3_enabled: bool,
    ) {
        let record = TraceRecord {
            step,
            timestamp_ms: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_millis(),
            energy: homeostasis.energy,
            fatigue: homeostasis.fatigue,
            thermal_load: homeostasis.thermal_load,
            stability_score: homeostasis.stability_score,
            reward_velocity: homeostasis.reward_velocity,
            prediction_error: homeostasis.prediction_error,
            risk_score: risk.map(|r| r.risk_score),
            dominant_factor: risk.map(|r| r.dominant_factor.clone()),
            action: action.as_str().to_string(),
            exploration_rate: params.exploration_rate,
            reward_bias: params.reward_bias,
            plasticity_scale: params.plasticity_scale,
            compute_budget: params.compute_budget,
            recovery_mode: params.recovery_mode,
            step_rate_limit: params.step_rate_limit,
            p3_enabled,
        };
        
        self.buffer.push(record);
        
        // 定期 flush
        if self.buffer.len() >= self.flush_interval {
            self.flush();
        }
    }
    
    /// 刷新缓冲区到文件
    pub fn flush(&mut self) {
        if let Some(writer) = &mut self.writer {
            for record in &self.buffer {
                if let Err(e) = writeln!(writer, "{}", record.to_csv()) {
                    eprintln!("⚠️ TraceLogger write failed: {}", e);
                }
            }
            
            if let Err(e) = writer.flush() {
                eprintln!("⚠️ TraceLogger flush failed: {}", e);
            }
        }
        
        self.buffer.clear();
    }
}

impl TraceRecord {
    /// 转换为 CSV 行
    fn to_csv(&self) -> String {
        format!(
            "{},{},{:.4},{:.4},{:.4},{:.4},{:.4},{:.4},{},{},{},{:.4},{:.4},{:.4},{:.4},{},{:.4},{}",
            self.step,
            self.timestamp_ms,
            self.energy,
            self.fatigue,
            self.thermal_load,
            self.stability_score,
            self.reward_velocity,
            self.prediction_error,
            self.risk_score.map(|f| format!("{:.4}", f)).unwrap_or_default(),
            self.dominant_factor.as_ref().unwrap_or(&String::new()),
            self.action,
            self.exploration_rate,
            self.reward_bias,
            self.plasticity_scale,
            self.compute_budget,
            self.recovery_mode,
            self.step_rate_limit,
            self.p3_enabled,
        )
    }
}

impl PreservationAction {
    /// 返回 action 的字符串表示
    fn as_str(&self) -> &'static str {
        match self {
            PreservationAction::ContinueTask => "ContinueTask",
            PreservationAction::EnterRecovery => "EnterRecovery",
            PreservationAction::SeekReward => "SeekReward",
            PreservationAction::ReduceExploration => "ReduceExploration",
            PreservationAction::StabilizeNetwork => "StabilizeNetwork",
            PreservationAction::SlowDown => "SlowDown",
        }
    }
}

/// 分析 trace 日志（用于 P3B 验证）
pub fn analyze_trace_log(log_path: &str) -> Result<TraceAnalysis, Box<dyn std::error::Error>> {
    use std::io::{BufRead, BufReader};
    
    let file = File::open(log_path)?;
    let reader = BufReader::new(file);
    let mut lines = reader.lines();
    
    // 跳过 header
    let _header = lines.next();
    
    let mut total_steps = 0u64;
    let mut intervention_count = 0u64;
    let mut recovery_entries = 0u64;
    let mut recovery_exits = 0u64;
    let mut time_in_recovery = 0u64;
    let mut energy_critical_count = 0u64;
    let mut total_exploration_rate = 0.0f32;
    let mut high_risk_steps = 0u64;
    let mut high_risk_interventions = 0u64;
    
    let mut prev_recovery_mode = false;
    
    for line in lines {
        let line = line?;
        let parts: Vec<&str> = line.split(',').collect();
        if parts.len() < 18 {
            continue;
        }
        
        total_steps += 1;
        
        // 解析字段
        let energy: f32 = parts[2].parse().unwrap_or(0.5);
        let risk_score: f32 = parts[8].parse().unwrap_or(0.0);
        let action = parts[10];
        let exploration_rate: f32 = parts[11].parse().unwrap_or(0.3);
        let recovery_mode: bool = parts[15].parse().unwrap_or(false);
        
        // 统计
        total_exploration_rate += exploration_rate;
        
        if recovery_mode {
            time_in_recovery += 1;
        }
        if !prev_recovery_mode && recovery_mode {
            recovery_entries += 1;
        }
        if prev_recovery_mode && !recovery_mode {
            recovery_exits += 1;
        }
        prev_recovery_mode = recovery_mode;
        
        if energy < 0.2 {
            energy_critical_count += 1;
        }
        
        if risk_score > 0.5 {
            high_risk_steps += 1;
            if action != "ContinueTask" {
                high_risk_interventions += 1;
            }
        }
        
        if action != "ContinueTask" {
            intervention_count += 1;
        }
    }
    
    let intervention_rate = if total_steps > 0 {
        intervention_count as f32 / total_steps as f32
    } else {
        0.0
    };
    
    let high_risk_intervention_rate = if high_risk_steps > 0 {
        high_risk_interventions as f32 / high_risk_steps as f32
    } else {
        0.0
    };
    
    let avg_exploration_rate = if total_steps > 0 {
        total_exploration_rate / total_steps as f32
    } else {
        0.0
    };
    
    Ok(TraceAnalysis {
        total_steps,
        intervention_count,
        intervention_rate,
        recovery_entries,
        recovery_exits,
        time_in_recovery,
        energy_critical_count,
        avg_exploration_rate,
        high_risk_steps,
        high_risk_intervention_rate,
    })
}

/// Trace 分析结果
#[derive(Debug, Clone, Default)]
pub struct TraceAnalysis {
    pub total_steps: u64,
    pub intervention_count: u64,
    pub intervention_rate: f32,
    pub recovery_entries: u64,
    pub recovery_exits: u64,
    pub time_in_recovery: u64,
    pub energy_critical_count: u64,
    pub avg_exploration_rate: f32,
    pub high_risk_steps: u64,
    pub high_risk_intervention_rate: f32,
}

impl TraceAnalysis {
    /// 格式化为报告
    pub fn to_report(&self) -> String {
        format!(
            r#"=== P3 Trace Analysis Report ===
Total Steps:              {}
Intervention Count:       {} ({:.1}%)
High-Risk Intervention:   {:.1}% of {} high-risk steps
Recovery Entries:         {}
Recovery Exits:           {}
Time in Recovery:         {} steps ({:.1}%)
Energy Critical Events:   {}
Avg Exploration Rate:     {:.3}
================================"#,
            self.total_steps,
            self.intervention_count,
            self.intervention_rate * 100.0,
            self.high_risk_intervention_rate * 100.0,
            self.high_risk_steps,
            self.recovery_entries,
            self.recovery_exits,
            self.time_in_recovery,
            (self.time_in_recovery as f32 / self.total_steps.max(1) as f32) * 100.0,
            self.energy_critical_count,
            self.avg_exploration_rate,
        )
    }
    
    /// 验证标准 A：高风险干预率 >= baseline 2x
    /// baseline_intervention_rate 通常是 0.0（不干预）或很低
    pub fn check_validation_a(&self, baseline_intervention_rate: f32) -> bool {
        if baseline_intervention_rate == 0.0 {
            // baseline 不干预，P3 应该在高风险时干预
            self.high_risk_intervention_rate > 0.5 // 至少 50% 干预率
        } else {
            self.high_risk_intervention_rate >= baseline_intervention_rate * 2.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_trace_record_to_csv() {
        let record = TraceRecord {
            step: 42,
            timestamp_ms: 1234567890,
            energy: 0.75,
            fatigue: 0.3,
            thermal_load: 0.4,
            stability_score: 0.8,
            reward_velocity: 0.1,
            prediction_error: 0.05,
            risk_score: Some(0.35),
            dominant_factor: Some("energy".to_string()),
            action: "ContinueTask".to_string(),
            exploration_rate: 0.25,
            reward_bias: 0.0,
            plasticity_scale: 1.0,
            compute_budget: 1.0,
            recovery_mode: false,
            step_rate_limit: 1.0,
            p3_enabled: true,
        };
        
        let csv = record.to_csv();
        assert!(csv.contains("ContinueTask"));
        assert!(csv.contains("42"));
    }
}
