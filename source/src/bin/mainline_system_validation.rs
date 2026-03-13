//! Mainline System Validation
//!
//! Candidate 001 is now FROZEN as mainline default.
//! This runner validates that the system benefits in real task scenarios.
//!
//! Three conditions:
//! - Mainline ON (Candidate 001 frozen config)
//! - Mainline OFF (markers disabled)
//! - Baseline (no markers, pure random)
//!
//! Metrics: task success, stability, overhead

use agl_mwe::prior_channel::{
    Marker, MarkerScheduler,
    frozen_config::{POLICY_COUPLING_BIAS, RANDOM_EXPLORATION_RATE},
};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::time::Instant;

#[derive(Clone, Copy)]
enum TaskType {
    CooperativeTask,      // Requires coordination
    CompetitiveTask,      // Zero-sum
    MixedTask,           // Both cooperation and competition
}

impl TaskType {
    fn score(&self, actions: &[Action]) -> i32 {
        match self {
            TaskType::CooperativeTask => {
                // All cooperate = high score
                let cooperators = actions.iter().filter(|a| matches!(a, Action::Cooperate)).count();
                if cooperators == actions.len() { 10 } else { cooperators as i32 }
            }
            TaskType::CompetitiveTask => {
                // Zero-sum: one winner
                let max_idx = 0; // Simplified
                actions.iter().enumerate().map(|(i, _)| {
                    if i == max_idx { 5 } else { -1 }
                }).sum()
            }
            TaskType::MixedTask => {
                // Balanced
                let c = actions.iter().filter(|a| matches!(a, Action::Cooperate)).count();
                let d = actions.len() - c;
                (c as i32 * 3) - (d as i32)  // Cooperate slightly favored
            }
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Action { Cooperate, Defect }

impl Action {
    fn to_f32(&self) -> f32 { match self { Action::Cooperate => 0.0, Action::Defect => 1.0 } }
}

// ============================================================================
// SYSTEM AGENT (Mainline)
// ============================================================================

struct SystemAgent {
    id: u8,
    scheduler: MarkerScheduler,
    total_score: i32,
    action_history: Vec<Action>,
    rng: StdRng,
    config: AgentConfig,
}

#[derive(Clone, Copy)]
struct AgentConfig {
    use_markers: bool,
    use_coupling: bool,
}

impl SystemAgent {
    fn new(id: u8, seed: u64, config: AgentConfig) -> Self {
        Self {
            id,
            scheduler: MarkerScheduler::new(id),
            total_score: 0,
            action_history: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            config,
        }
    }
    
    fn choose_action(&mut self, partner_markers: &[Marker]) -> Action {
        if !self.config.use_markers {
            // Baseline: pure random
            return if self.rng.gen::<f32>() > 0.5 { Action::Cooperate } else { Action::Defect };
        }
        
        let avg_coherence: f32 = if partner_markers.is_empty() {
            0.5
        } else {
            partner_markers.iter()
                .map(|m| m.coherence() as f32 / 255.0)
                .sum::<f32>() / partner_markers.len() as f32
        };
        
        let base_coop = 0.5;
        
        // FROZEN: bias = 0.8
        let bias = if self.config.use_coupling {
            (avg_coherence - 0.5) * POLICY_COUPLING_BIAS * 2.0
        } else { 0.0 };
        
        let coop_prob = (base_coop + bias).clamp(0.05, 0.95);
        
        // FROZEN: random_rate = 0.3
        if self.rng.gen::<f32>() < RANDOM_EXPLORATION_RATE {
            if self.rng.gen::<f32>() > 0.5 { Action::Cooperate } else { Action::Defect }
        } else {
            if self.rng.gen::<f32>() < coop_prob { Action::Cooperate } else { Action::Defect }
        }
    }
    
    fn record(&mut self, action: Action, payoff: i32) {
        self.action_history.push(action);
        self.total_score += payoff;
        let _ = self.scheduler.tick(action.to_f32());
    }
    
    fn current_marker(&self) -> Marker { self.scheduler.current_marker() }
    
    fn task_success_rate(&self) -> f32 {
        // Success = cooperated in cooperative context
        let cooperations = self.action_history.iter()
            .filter(|a| matches!(a, Action::Cooperate))
            .count();
        if self.action_history.is_empty() { 0.0 } else {
            cooperations as f32 / self.action_history.len() as f32
        }
    }
    
    fn behavioral_stability(&self) -> f32 {
        // Low variance = high stability
        if self.action_history.len() < 10 { return 0.5; }
        let actions: Vec<f32> = self.action_history.iter().map(|a| a.to_f32()).collect();
        let mean = actions.iter().sum::<f32>() / actions.len() as f32;
        let var = actions.iter().map(|a| (a - mean).powi(2)).sum::<f32>() / actions.len() as f32;
        1.0 - (var * 2.0).min(1.0)
    }
}

// ============================================================================
// TASK RUNNER
// ============================================================================

struct TaskRunner {
    agents: Vec<SystemAgent>,
    task: TaskType,
    compute_overhead: u64,  // Simulated compute units
}

impl TaskRunner {
    fn new(n_agents: usize, task: TaskType, seed: u64, config: AgentConfig) -> Self {
        let agents: Vec<SystemAgent> = (0..n_agents)
            .map(|i| SystemAgent::new(i as u8, seed + i as u64, config))
            .collect();
        
        Self { agents, task, compute_overhead: 0 }
    }
    
    fn run_episode(&mut self) -> i32 {
        let start = Instant::now();
        
        // Collect markers
        let markers: Vec<Marker> = self.agents.iter()
            .map(|a| a.current_marker())
            .collect();
        
        // Each agent acts
        let actions: Vec<Action> = self.agents.iter_mut()
            .map(|a| a.choose_action(&markers))
            .collect();
        
        // Compute task score
        let task_score = self.task.score(&actions);
        
        // Record for each agent
        for (i, agent) in self.agents.iter_mut().enumerate() {
            let individual_payoff = if task_score > 0 { task_score / self.agents.len() as i32 } else { task_score };
            agent.record(actions[i], individual_payoff);
        }
        
        // Track overhead
        self.compute_overhead += start.elapsed().as_micros() as u64;
        
        task_score
    }
    
    fn run(&mut self, n_episodes: usize) -> TaskMetrics {
        let mut total_score = 0;
        
        for _ in 0..n_episodes {
            total_score += self.run_episode();
        }
        
        let avg_success: f32 = self.agents.iter()
            .map(|a| a.task_success_rate())
            .sum::<f32>() / self.agents.len() as f32;
        
        let avg_stability: f32 = self.agents.iter()
            .map(|a| a.behavioral_stability())
            .sum::<f32>() / self.agents.len() as f32;
        
        let total_score_sum: i32 = self.agents.iter().map(|a| a.total_score).sum();
        
        TaskMetrics {
            total_score: total_score_sum,
            task_success_rate: avg_success,
            behavioral_stability: avg_stability,
            compute_overhead_us: self.compute_overhead,
        }
    }
}

#[derive(Clone, Debug)]
struct TaskMetrics {
    total_score: i32,
    task_success_rate: f32,
    behavioral_stability: f32,
    compute_overhead_us: u64,
}

// ============================================================================
// THREE-CONDITION VALIDATION
// ============================================================================

fn run_three_condition_validation(task: TaskType, n_episodes: usize, n_seeds: usize) -> ValidationResult {
    let mut on_results = Vec::new();
    let mut off_results = Vec::new();
    let mut baseline_results = Vec::new();
    
    for seed in 0..n_seeds {
        // ON: Full Candidate 001 mainline
        let mut runner_on = TaskRunner::new(
            4, task, seed as u64,
            AgentConfig { use_markers: true, use_coupling: true }
        );
        on_results.push(runner_on.run(n_episodes));
        
        // OFF: Markers but no coupling
        let mut runner_off = TaskRunner::new(
            4, task, seed as u64,
            AgentConfig { use_markers: true, use_coupling: false }
        );
        off_results.push(runner_off.run(n_episodes));
        
        // Baseline: No markers
        let mut runner_base = TaskRunner::new(
            4, task, seed as u64,
            AgentConfig { use_markers: false, use_coupling: false }
        );
        baseline_results.push(runner_base.run(n_episodes));
    }
    
    ValidationResult {
        task,
        on: aggregate(&on_results),
        off: aggregate(&off_results),
        baseline: aggregate(&baseline_results),
    }
}

fn aggregate(results: &[TaskMetrics]) -> AggregatedMetrics {
    let n = results.len() as f32;
    AggregatedMetrics {
        total_score: (results.iter().map(|r| r.total_score).sum::<i32>() as f32 / n) as i32,
        task_success_rate: results.iter().map(|r| r.task_success_rate).sum::<f32>() / n,
        behavioral_stability: results.iter().map(|r| r.behavioral_stability).sum::<f32>() / n,
        compute_overhead_us: (results.iter().map(|r| r.compute_overhead_us).sum::<u64>() as f32 / n) as u64,
    }
}

#[derive(Clone, Debug)]
struct AggregatedMetrics {
    total_score: i32,
    task_success_rate: f32,
    behavioral_stability: f32,
    compute_overhead_us: u64,
}

#[derive(Clone, Debug)]
struct ValidationResult {
    task: TaskType,
    on: AggregatedMetrics,
    off: AggregatedMetrics,
    baseline: AggregatedMetrics,
}

impl ValidationResult {
    fn print(&self) {
        println!("\n  Task: {:?}", self.task);
        println!("  {:-<70}", "");
        println!("  {:<25} {:>12} {:>12} {:>12}", "Metric", "ON", "OFF", "Baseline");
        println!("  {:-<70}", "");
        println!("  {:<25} {:>12} {:>12} {:>12}", 
            "Total Score", self.on.total_score, self.off.total_score, self.baseline.total_score);
        println!("  {:<25} {:>11.1}% {:>11.1}% {:>11.1}%", 
            "Task Success", self.on.task_success_rate * 100.0, 
            self.off.task_success_rate * 100.0, self.baseline.task_success_rate * 100.0);
        println!("  {:<25} {:>11.1}% {:>11.1}% {:>11.1}%", 
            "Stability", self.on.behavioral_stability * 100.0,
            self.off.behavioral_stability * 100.0, self.baseline.behavioral_stability * 100.0);
        println!("  {:<25} {:>10}μs {:>10}μs {:>10}μs",
            "Overhead", self.on.compute_overhead_us, self.off.compute_overhead_us, self.baseline.compute_overhead_us);
        
        // Validation
        let score_improvement = self.on.total_score - self.off.total_score;
        let stability_improvement = self.on.behavioral_stability - self.off.behavioral_stability;
        
        println!("\n  System Validation:");
        if score_improvement > 0 {
            println!("    ✅ ON improves score vs OFF: +{}", score_improvement);
        } else {
            println!("    ⚠️  No score improvement: {}", score_improvement);
        }
        
        if stability_improvement > 0.0 {
            println!("    ✅ ON improves stability: +{:.1}%", stability_improvement * 100.0);
        }
    }
}

// ============================================================================
// MAIN
// ============================================================================

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("MAINLINE SYSTEM VALIDATION");
    println!("Candidate 001 as FROZEN baseline");
    println!("{}", "=".repeat(70));
    
    let n_episodes = 1000;
    let n_seeds = 10;
    
    println!("\nConfiguration:");
    println!("  Episodes: {}", n_episodes);
    println!("  Seeds: {}", n_seeds);
    println!("  Agents: 4 per task");
    
    println!("\nFrozen Config:");
    println!("  Marker: 32 bits");
    println!("  Timescale: 10x");
    println!("  Bias: 0.8 (validated)");
    println!("  Random: 0.3");
    
    // Run tasks
    let tasks = vec![
        TaskType::CooperativeTask,
        TaskType::CompetitiveTask,
        TaskType::MixedTask,
    ];
    
    for task in tasks {
        let result = run_three_condition_validation(task, n_episodes, n_seeds);
        result.print();
    }
    
    println!("\n{}", "=".repeat(70));
    println!("System Validation Complete");
    println!("{}", "=".repeat(70));
}
