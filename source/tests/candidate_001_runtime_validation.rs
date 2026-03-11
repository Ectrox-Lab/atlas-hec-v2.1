//! Candidate 001 Runtime Validation
//!
//! Minimal three-condition ablation test for runtime validation.
//! This test isolates Candidate 001 from other modules to ensure
//! clean validation without dependency on incomplete components.

use atlas_hec_v2::prior_channel::{
    PriorChannelMarkerAdapter, Marker, MarkerScheduler, PolicyModulation,
    PRIOR_SAMPLE_PROB, PRIOR_STRENGTH,
};
use rand::SeedableRng;
use rand::rngs::StdRng;
use rand::Rng;

// ============================================================================
// Minimal Test Agent
// ============================================================================

struct MinimalAgent {
    id: u8,
    scheduler: MarkerScheduler,
    coherence_history: Vec<f32>,
}

impl MinimalAgent {
    fn new(id: u8) -> Self {
        Self {
            id,
            scheduler: MarkerScheduler::new(id),
            coherence_history: Vec::new(),
        }
    }
    
    fn act(&mut self, action: f32) {
        if let Some(marker) = self.scheduler.tick(action) {
            let coherence: f32 = marker.coherence() as f32 / 255.0;
            self.coherence_history.push(coherence);
        }
    }
    
    fn mean_coherence(&self) -> f32 {
        if self.coherence_history.is_empty() {
            0.5
        } else {
            self.coherence_history.iter().sum::<f32>() / self.coherence_history.len() as f32
        }
    }
    
    fn current_marker(&self) -> Marker {
        self.scheduler.current_marker()
    }
}

// ============================================================================
// Three-Condition Arena
// ============================================================================

struct MinimalArena {
    agents: Vec<MinimalAgent>,
    adapter: Option<PriorChannelMarkerAdapter>,
    tick: usize,
    rng: StdRng,
}

impl MinimalArena {
    fn new(n_agents: usize, enable_pc: bool, seed: u64) -> Self {
        let agents: Vec<MinimalAgent> = (0..n_agents)
            .map(|i| MinimalAgent::new(i as u8))
            .collect();
        
        let adapter = if enable_pc {
            Some(PriorChannelMarkerAdapter::new(true))
        } else {
            None
        };
        
        Self {
            agents,
            adapter,
            tick: 0,
            rng: StdRng::seed_from_u64(seed),
        }
    }
    
    fn step(&mut self) {
        let n = self.agents.len();
        let mut actions: Vec<f32> = Vec::with_capacity(n);
        
        // Each agent observes others and acts
        for i in 0..n {
            let observed_markers: Vec<Marker> = self.agents
                .iter()
                .filter(|a| a.id != self.agents[i].id)
                .map(|a| a.current_marker())
                .collect();
            
            let avg_coherence: f32 = if observed_markers.is_empty() {
                0.5
            } else {
                observed_markers.iter()
                    .map(|m: &Marker| m.coherence() as f32)
                    .sum::<f32>() / (observed_markers.len() as f32 * 255.0)
            };
            
            // High coherence -> consistent action
            let action = if avg_coherence > 0.6 {
                0.0f32
            } else {
                self.rng.gen::<f32>()
            };
            
            actions.push(action);
        }
        
        // Apply PriorChannel modulation if enabled
        if let Some(ref mut adapter) = self.adapter {
            for i in 0..n {
                let marker = self.agents[i].current_marker();
                let pop_markers: Vec<Marker> = self.agents
                    .iter()
                    .filter(|a| a.id != self.agents[i].id)
                    .map(|a| a.current_marker())
                    .collect();
                
                let modulation = adapter.inject_prior(&marker, &pop_markers, &mut self.rng);
                
                if modulation.confidence > 0.0 {
                    actions[i] = actions[i] * (1.0 - modulation.confidence);
                }
            }
        }
        
        // Record actions
        for i in 0..n {
            self.agents[i].act(actions[i]);
        }
        
        self.tick += 1;
    }
    
    fn run(&mut self, n_ticks: usize) -> Metrics {
        for _ in 0..n_ticks {
            self.step();
        }
        
        let mean_coherence: f32 = self.agents.iter()
            .map(|a| a.mean_coherence())
            .sum::<f32>() / self.agents.len() as f32;
        
        Metrics {
            mean_coherence,
            adapter_enabled: self.adapter.is_some(),
        }
    }
}

#[derive(Clone, Debug)]
struct Metrics {
    mean_coherence: f32,
    adapter_enabled: bool,
}

// ============================================================================
// Three-Condition Ablation
// ============================================================================

fn run_three_condition_ablation(n_trials: usize, n_ticks: usize) -> AblationResults {
    let mut a_results = Vec::new();
    let mut b_results = Vec::new();
    let mut c_results = Vec::new();
    
    for trial in 0..n_trials {
        // Condition A: Standalone
        let mut arena_a = MinimalArena::new(4, false, trial as u64);
        a_results.push(arena_a.run(n_ticks).mean_coherence);
        
        // Condition B: PC(OFF)
        let mut arena_b = MinimalArena::new(4, false, trial as u64);
        b_results.push(arena_b.run(n_ticks).mean_coherence);
        
        // Condition C: PC(ON)
        let mut arena_c = MinimalArena::new(4, true, trial as u64);
        c_results.push(arena_c.run(n_ticks).mean_coherence);
    }
    
    AblationResults {
        a_mean: a_results.iter().sum::<f32>() / a_results.len() as f32,
        b_mean: b_results.iter().sum::<f32>() / b_results.len() as f32,
        c_mean: c_results.iter().sum::<f32>() / c_results.len() as f32,
    }
}

#[derive(Clone, Debug)]
struct AblationResults {
    a_mean: f32,
    b_mean: f32,
    c_mean: f32,
}

impl AblationResults {
    fn validate(&self) -> ValidationReport {
        // Criterion 1: Coherence maintained (C >= 0.7)
        let coherence_maintained = self.c_mean >= 0.7;
        
        // Criterion 2: Marker mechanism intact (|C-B| < 0.2)
        let mechanism_diff = (self.c_mean - self.b_mean).abs();
        let mechanism_intact = mechanism_diff < 0.2;
        
        ValidationReport {
            coherence_maintained,
            mechanism_intact,
            mechanism_diff,
            all_pass: coherence_maintained && mechanism_intact,
        }
    }
}

#[derive(Clone, Debug)]
struct ValidationReport {
    coherence_maintained: bool,
    mechanism_intact: bool,
    mechanism_diff: f32,
    all_pass: bool,
}

// ============================================================================
// Main Validation Test
// ============================================================================

#[test]
fn candidate_001_three_condition_ablation() {
    println!("\n" + &"=".repeat(70));
    println!("CANDIDATE 001 + PRIORCHANNEL RUNTIME VALIDATION");
    println!("&".repeat(70));
    
    let results = run_three_condition_ablation(10, 1000);
    
    println!("\nThree-Condition Results:");
    println!("  A (Standalone):     coherence = {:.3}", results.a_mean);
    println!("  B (PC OFF):         coherence = {:.3}", results.b_mean);
    println!("  C (PC ON):          coherence = {:.3}", results.c_mean);
    
    let report = results.validate();
    
    println!("\nValidation Criteria:");
    println!("  [1] Coherence maintained (C >= 0.7):     {} (got {:.3})",
        if report.coherence_maintained { "✅ PASS" } else { "❌ FAIL" },
        results.c_mean);
    println!("  [2] Mechanism intact (|C-B| < 0.2):      {} (diff={:.3})",
        if report.mechanism_intact { "✅ PASS" } else { "❌ FAIL" },
        report.mechanism_diff);
    
    println!("\n{}", "=".repeat(70));
    if report.all_pass {
        println!("🎉 INTEGRATION VALIDATED - READY FOR MAINLINE");
    } else {
        println!("⚠️  VALIDATION FAILED - NEEDS REFINEMENT");
    }
    println!("{}", "=".repeat(70));
    
    assert!(report.all_pass, "Runtime validation failed");
}

// ============================================================================
// Compliance Guards
// ============================================================================

#[test]
fn guard_bandwidth_32_bits() {
    let marker = Marker::new(255, 255, 127, -128);
    assert_eq!(marker.as_bytes().len(), 4, "Marker must be exactly 4 bytes");
}

#[test]
fn guard_timescale_10x() {
    let scheduler = MarkerScheduler::new(1);
    assert!(scheduler.check_timescale(), "Must enforce 10x timescale");
}

#[test]
fn guard_frozen_parameters() {
    assert_eq!(PRIOR_SAMPLE_PROB, 0.01, "p=0.01 is FROZEN");
    assert_eq!(PRIOR_STRENGTH, 0.5, "α=0.5 is FROZEN");
}

#[test]
fn guard_generic_only_no_action_ids() {
    let mut adapter = PriorChannelMarkerAdapter::new(true);
    let modulation = adapter.compute_modulation(200, 180);
    
    // Modulation should only have generic values
    assert!(modulation.confidence >= 0.0 && modulation.confidence <= 1.0);
    assert!(modulation.coherence_bias >= -1.0 && modulation.coherence_bias <= 1.0);
}
