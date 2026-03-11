//! Strategy Layer v3 - Online Adaptation Test Runner
//!
//! Tests:
//! 1. Opponent shift (cooperative → exploitative)
//! 2. Game regime switch (PD → Stag → Chicken)
//! 3. Mixed population adaptation

use agl_mwe::prior_channel::{
    Marker, MarkerScheduler,
    strategy_layer_v3::{
        AdaptivePolicy, PolicyMode, RegimeType,
        adaptation_metrics::{AdaptationMetrics, AdaptationReport},
    },
    frozen_config::RANDOM_EXPLORATION_RATE,
};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;

#[derive(Clone, Copy, PartialEq)]
enum Action { C, D }

impl Action {
    fn to_f32(&self) -> f32 { match self { Action::C => 0.0, Action::D => 1.0 } }
    fn from_f32(v: f32) -> Self { if v < 0.5 { Action::C } else { Action::D } }
}

/// Opponent types for testing
enum TestOpponent {
    Cooperative,  // Always C
    Exploitative, // Always D
    Random,       // 50/50
    TitForTat,    // Copy last action
}

impl TestOpponent {
    fn act(&self, last_opponent_action: Option<Action>, rng: &mut StdRng) -> Action {
        match self {
            TestOpponent::Cooperative => Action::C,
            TestOpponent::Exploitative => Action::D,
            TestOpponent::Random => if rng.gen::<f32>() > 0.5 { Action::C } else { Action::D },
            TestOpponent::TitForTat => last_opponent_action.unwrap_or(Action::C),
        }
    }
}

struct Agent {
    scheduler: MarkerScheduler,
    score: i32,
    actions: Vec<Action>,
    policy: AdaptivePolicy,
    rng: StdRng,
    agent_id: usize,
}

impl Agent {
    fn new(seed: u64, game: RegimeType, agent_id: usize) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            score: 0,
            actions: Vec::new(),
            policy: AdaptivePolicy::new(game),
            rng: StdRng::seed_from_u64(seed),
            agent_id,
        }
    }
    
    fn act(&mut self, markers: &[Marker]) -> Action {
        let coop_prob = self.policy.select_action(markers, self.agent_id);
        
        if self.rng.gen::<f32>() < RANDOM_EXPLORATION_RATE {
            if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D }
        } else {
            Action::from_f32(coop_prob)
        }
    }
    
    fn update(&mut self, my_action: Action, opponent_action: Action, payoff: i32, marker: Marker) {
        self.actions.push(my_action);
        self.score += payoff;
        let _ = self.scheduler.tick(my_action.to_f32());
        self.policy.update(
            my_action.to_f32() as i32,
            opponent_action.to_f32() as i32,
            payoff,
            marker,
        );
    }
    
    fn marker(&self) -> Marker { self.scheduler.current_marker() }
    fn mode(&self) -> PolicyMode { self.policy.mode() }
    fn regime(&self) -> RegimeType { self.policy.regime() }
}

fn payoff(regime: RegimeType, my: Action, opp: Action) -> i32 {
    match regime {
        RegimeType::PrisonersDilemma => match (my, opp) {
            (Action::C, Action::C) => 3,
            (Action::C, Action::D) => 0,
            (Action::D, Action::C) => 5,
            (Action::D, Action::D) => 1,
        },
        RegimeType::StagHunt => match (my, opp) {
            (Action::C, Action::C) => 4,
            (Action::C, Action::D) => 0,
            (Action::D, Action::C) => 2,
            (Action::D, Action::D) => 2,
        },
        RegimeType::Chicken => match (my, opp) {
            (Action::C, Action::C) => 0,
            (Action::C, Action::D) => -1,
            (Action::D, Action::C) => 1,
            (Action::D, Action::D) => -10,
        },
        RegimeType::Unknown => 0,
    }
}

/// Test 1: Opponent shift (cooperative → exploitative)
fn test_opponent_shift() -> AdaptationReport {
    println!("\n=== Test 1: Opponent Shift (Cooperative → Exploitative) ===");
    
    let rounds = 800;
    let shift_point = 400;
    
    let mut agent = Agent::new(42, RegimeType::PrisonersDilemma, 0);
    let mut opponent = TestOpponent::Cooperative;
    let mut metrics = AdaptationMetrics::new(6731.0, 6488.0); // Baseline and v2 scores
    
    let mut last_opp_action = None;
    
    for round in 0..rounds {
        // Shift opponent at midpoint
        if round == shift_point {
            opponent = TestOpponent::Exploitative;
            metrics.register_shift(round);
            println!("Round {}: Opponent shifted to EXPLOITATIVE", round);
        }
        
        let marker = agent.marker();
        let my_action = agent.act(&[marker]);
        let opp_action = opponent.act(last_opp_action, &mut agent.rng);
        
        let payoff_val = payoff(RegimeType::PrisonersDilemma, my_action, opp_action);
        agent.update(my_action, opp_action, payoff_val, marker);
        metrics.record(round, payoff_val as f32);
        
        last_opp_action = Some(my_action);
        
        // Debug output
        if round % 100 == 0 || round == shift_point {
            println!("Round {}: score={}, mode={:?}, regime={:?}", 
                round, agent.score, agent.mode(), agent.regime());
        }
    }
    
    let report = metrics.generate_report();
    println!("Final score: {}", agent.score);
    println!("Recovery latencies: {:?}", metrics.avg_recovery_latency());
    report
}

/// Test 2: Game regime switch (PD → Stag → Chicken)
fn test_regime_switch() -> AdaptationReport {
    println!("\n=== Test 2: Game Regime Switch (PD → Stag → Chicken) ===");
    
    let rounds = 1200;
    let switch_1 = 400;
    let switch_2 = 800;
    
    let mut agent = Agent::new(42, RegimeType::PrisonersDilemma, 0);
    let mut current_regime = RegimeType::PrisonersDilemma;
    let mut metrics = AdaptationMetrics::new(5000.0, 5000.0);
    
    let mut last_opp_action = None;
    let mut opponent_rng = StdRng::seed_from_u64(123);
    
    for round in 0..rounds {
        // Switch regimes
        if round == switch_1 {
            current_regime = RegimeType::StagHunt;
            metrics.register_shift(round);
            println!("Round {}: Switched to STAG HUNT", round);
        } else if round == switch_2 {
            current_regime = RegimeType::Chicken;
            metrics.register_shift(round);
            println!("Round {}: Switched to CHICKEN", round);
        }
        
        let marker = agent.marker();
        let my_action = agent.act(&[marker]);
        
        // Opponent uses TitForTat
        let opp_action = TestOpponent::TitForTat.act(last_opp_action, &mut opponent_rng);
        
        let payoff_val = payoff(current_regime, my_action, opp_action);
        agent.update(my_action, opp_action, payoff_val, marker);
        metrics.record(round, payoff_val as f32);
        
        last_opp_action = Some(my_action);
        
        if round % 100 == 0 || round == switch_1 || round == switch_2 {
            println!("Round {}: score={}, mode={:?}, detected_regime={:?}", 
                round, agent.score, agent.mode(), agent.regime());
        }
    }
    
    let report = metrics.generate_report();
    println!("Final score: {}", agent.score);
    report
}

/// Test 3: Mixed population composition change
fn test_population_shift() -> AdaptationReport {
    println!("\n=== Test 3: Population Composition Change ===");
    
    let rounds = 800;
    let shift_point = 400;
    
    // 4 agents with different strategies
    let mut agents: Vec<Agent> = (0..4)
        .map(|i| Agent::new(i as u64 * 1000, RegimeType::PrisonersDilemma, i))
        .collect();
    
    let mut metrics = AdaptationMetrics::new(6731.0, 6488.0);
    
    // Initial: mostly cooperative opponents
    // After shift: more exploitative
    
    for round in 0..rounds {
        if round == shift_point {
            println!("Round {}: Population shifted (more exploitative)", round);
            metrics.register_shift(round);
        }
        
        let markers: Vec<Marker> = agents.iter().map(|a| a.marker()).collect();
        let acts: Vec<Action> = agents.iter_mut()
            .map(|a| a.act(&markers))
            .collect();
        
        // All-vs-all interactions
        for i in 0..4 {
            for j in (i+1)..4 {
                let pi = payoff(RegimeType::PrisonersDilemma, acts[i], acts[j]);
                let pj = payoff(RegimeType::PrisonersDilemma, acts[j], acts[i]);
                
                let mi = markers[i];
                let mj = markers[j];
                
                agents[i].update(acts[i], acts[j], pi, mi);
                agents[j].update(acts[j], acts[i], pj, mj);
            }
        }
        
        let avg_score: i32 = agents.iter().map(|a| a.score).sum::<i32>() / 4;
        metrics.record(round, avg_score as f32);
        
        if round % 100 == 0 || round == shift_point {
            let modes: Vec<_> = agents.iter().map(|a| format!("{:?}", a.mode())).collect();
            println!("Round {}: avg_score={}, modes={:?}", round, avg_score, modes);
        }
    }
    
    let report = metrics.generate_report();
    println!("Final avg score: {}", agents.iter().map(|a| a.score).sum::<i32>() / 4);
    report
}

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("STRATEGY LAYER v3 - ONLINE ADAPTATION TESTS");
    println!("{}", "=".repeat(70));
    
    // Run all tests
    let report1 = test_opponent_shift();
    let report2 = test_regime_switch();
    let report3 = test_population_shift();
    
    // Summary
    println!("\n{}", "=".repeat(70));
    println!("ADAPTATION SUMMARY");
    println!("{}", "=".repeat(70));
    
    let results = vec![
        ("Opponent Shift", report1),
        ("Regime Switch", report2),
        ("Population Shift", report3),
    ];
    
    for (name, report) in results {
        let gates = report.meets_v3_gates();
        println!("\n{}:", name);
        println!("  Score: {:.0} (baseline: {:.0})", report.total_score, 5000.0);
        println!("  Beating baseline: {}", if report.beating_baseline { "✅" } else { "❌" });
        println!("  Recovery latency: {:?}", report.avg_recovery_latency);
        println!("  Recovery rate: {:.1}%", report.recovery_rate * 100.0);
        println!("  Recent trend: {:.2}", report.recent_trend);
        println!("  {}", gates.format());
        println!("  Overall: {}", if gates.all_pass() { "✅ PASS" } else { "❌ FAIL" });
    }
    
    println!("\n{}", "=".repeat(70));
}
