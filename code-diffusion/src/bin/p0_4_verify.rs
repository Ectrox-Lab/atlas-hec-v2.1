//! P0-4 Verification: Trained vs Untrained Model Comparison
//!
//! This script performs rigorous comparison between trained and untrained models
//! to verify that training produces task-effective changes.
//!
//! Usage:
//!   cargo run --bin p0_4_verify -- --trained checkpoints/model_epoch1_loss1.091671.pt

use clap::Parser;
use code_diffusion::{
    data::PatchCategory,
    diffusion::{Diffusion, DiffusionConfig},
    models::RealUNet,
    sampling::CodeDNAGenerator,
    training::load_checkpoint,
};
use std::collections::HashMap;
use std::fs;
use std::time::Instant;

/// P0-4 Verification: Compare trained vs untrained models
#[derive(Parser)]
#[command(name = "p0_4_verify")]
#[command(about = "P0-4: Verify training produces task-effective changes")]
struct Args {
    /// Trained checkpoint path
    #[arg(short, long, required = true)]
    trained: String,
    
    /// Untrained checkpoint path (if not provided, creates fresh init)
    #[arg(short, long)]
    untrained: Option<String>,
    
    /// Number of samples per condition
    #[arg(long, default_value = "20")]
    num_samples: usize,
    
    /// Number of random seeds to test
    #[arg(long, default_value = "5")]
    num_seeds: usize,
    
    /// Guidance scale
    #[arg(long, default_value = "2.0")]
    guidance_scale: f64,
    
    /// Output JSON report path
    #[arg(short, long, default_value = "p0_4_report.json")]
    output: String,
}

/// Test conditions
const CONDITIONS: [PatchCategory; 4] = [
    PatchCategory::BugFix,
    PatchCategory::Performance,
    PatchCategory::Safety,
    PatchCategory::Refactor,
];

/// Generate deterministic seeds
fn generate_seeds(count: usize) -> Vec<u64> {
    (0..count as u64).map(|i| 42 + i * 17).collect()
}

/// Compute token distribution fingerprint
fn compute_fingerprint(samples: &[code_diffusion::data::EditDNA]) -> (u64, HashMap<String, usize>) {
    let mut token_counts: HashMap<String, usize> = HashMap::new();
    
    for sample in samples {
        for token in &sample.tokens {
            let name = format!("{:?}", token);
            *token_counts.entry(name).or_insert(0) += 1;
        }
    }
    
    // Compute hash from sorted token counts
    let mut items: Vec<_> = token_counts.iter().collect();
    items.sort_by_key(|(k, _)| *k);
    
    let mut hash: u64 = 0xcbf29ce484222325;
    for (token, count) in items {
        for b in token.bytes() {
            hash ^= b as u64;
            hash = hash.wrapping_mul(0x100000001b3);
        }
        hash ^= (*count as u64).wrapping_mul(31);
        hash = hash.wrapping_mul(0x100000001b3);
    }
    
    (hash, token_counts)
}

/// Compute Jensen-Shannon divergence between two distributions
fn js_divergence(
    dist1: &HashMap<String, usize>,
    dist2: &HashMap<String, usize>,
) -> f64 {
    let total1: usize = dist1.values().sum();
    let total2: usize = dist2.values().sum();
    
    if total1 == 0 || total2 == 0 {
        return 1.0;
    }
    
    // Get all unique keys
    let all_keys: std::collections::HashSet<_> = dist1
        .keys()
        .chain(dist2.keys())
        .cloned()
        .collect();
    
    let mut divergence = 0.0;
    
    for key in all_keys {
        let p1 = *dist1.get(&key).unwrap_or(&0) as f64 / total1 as f64;
        let p2 = *dist2.get(&key).unwrap_or(&0) as f64 / total2 as f64;
        
        // Average distribution
        let m = (p1 + p2) / 2.0;
        
        // KL divergence terms
        if p1 > 0.0 {
            divergence += 0.5 * p1 * (p1 / m).ln();
        }
        if p2 > 0.0 {
            divergence += 0.5 * p2 * (p2 / m).ln();
        }
    }
    
    divergence
}

/// Sample result for a single condition-seed pair
#[derive(Debug, Clone)]
struct SampleResult {
    condition: String,
    seed: u64,
    trained_hash: u64,
    untrained_hash: u64,
    divergence: f64,
}

fn main() {
    let args = Args::parse();
    let start_time = Instant::now();
    
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  P0-4 VERIFICATION: Trained vs Untrained Model Comparison       ║");
    println!("╚══════════════════════════════════════════════════════════════════╝");
    println!();
    
    // Load trained model
    println!("[1/5] Loading TRAINED model from: {}", args.trained);
    let trained_params = match load_checkpoint(&args.trained) {
        Some(p) => {
            println!("      ✅ Loaded {} parameters", p.len());
            p
        }
        None => {
            eprintln!("      ❌ Failed to load trained checkpoint");
            std::process::exit(1);
        }
    };
    
    // Load or create untrained model
    println!("[2/5] Loading/Creating UNTRAINED model...");
    let untrained_params = match &args.untrained {
        Some(path) => {
            println!("      Loading from: {}", path);
            match load_checkpoint(path) {
                Some(p) => {
                    println!("      ✅ Loaded {} parameters", p.len());
                    p
                }
                None => {
                    eprintln!("      ❌ Failed to load, creating fresh init");
                    create_untrained_checkpoint()
                }
            }
        }
        None => {
            println!("      Creating fresh random initialization");
            create_untrained_checkpoint()
        }
    };
    
    // Create output directory
    fs::create_dir_all("p0_4_results").unwrap_or_default();
    
    // Generate test matrix
    let seeds = generate_seeds(args.num_seeds);
    println!("[3/5] Test Configuration:");
    println!("      Conditions: {:?}", CONDITIONS.iter().map(|c| format!("{:?}", c)).collect::<Vec<_>>());
    println!("      Seeds: {:?}", seeds);
    println!("      Samples per cell: {}", args.num_samples);
    println!("      Total comparisons: {}", CONDITIONS.len() * seeds.len());
    println!();
    
    // Run comparison matrix
    println!("[4/5] Running comparison matrix...");
    let mut results: Vec<SampleResult> = vec![];
    let mut trained_wins = 0;
    let mut total_divergence = 0.0;
    
    for (cond_idx, condition) in CONDITIONS.iter().enumerate() {
        for (seed_idx, seed) in seeds.iter().enumerate() {
            print!("      Testing {}/{}: condition={:?}, seed={}", 
                cond_idx * seeds.len() + seed_idx + 1,
                CONDITIONS.len() * seeds.len(),
                condition, seed
            );
            
            // Test trained model
            let mut trained_unet = RealUNet::new(64, 128, 64, 8);
            trained_unet.load_params(&trained_params).expect("Failed to load trained params");
            
            let diffusion = Diffusion::new(DiffusionConfig::default());
            let trained_gen = CodeDNAGenerator::new(
                Diffusion::new(DiffusionConfig::default()), 
                trained_unet
            );
            let trained_samples = trained_gen.generate_with_seed(
                *condition, args.num_samples, args.guidance_scale, Some(*seed)
            );
            let (trained_hash, trained_dist) = compute_fingerprint(&trained_samples);
            
            // Test untrained model
            let mut untrained_unet = RealUNet::new(64, 128, 64, 8);
            untrained_unet.load_params(&untrained_params).expect("Failed to load untrained params");
            
            let untrained_gen = CodeDNAGenerator::new(
                Diffusion::new(DiffusionConfig::default()), 
                untrained_unet
            );
            let untrained_samples = untrained_gen.generate_with_seed(
                *condition, args.num_samples, args.guidance_scale, Some(*seed)
            );
            let (untrained_hash, untrained_dist) = compute_fingerprint(&untrained_samples);
            
            // Compute divergence
            let divergence = js_divergence(&trained_dist, &untrained_dist);
            total_divergence += divergence;
            
            // Heuristic: trained model should have more structured output
            // (lower variance in token distribution = more consistent patterns)
            let trained_entropy = compute_entropy(&trained_dist);
            let untrained_entropy = compute_entropy(&untrained_dist);
            if trained_entropy < untrained_entropy {
                trained_wins += 1;
            }
            
            results.push(SampleResult {
                condition: format!("{:?}", condition),
                seed: *seed,
                trained_hash,
                untrained_hash,
                divergence,
            });
            
            println!("  div={:.4}", divergence);
        }
    }
    println!();
    
    // Compute aggregate metrics
    let avg_divergence = total_divergence / results.len() as f64;
    let win_rate = trained_wins as f64 / results.len() as f64;
    
    // Reload test for determinism
    println!("[5/5] Testing reload determinism...");
    let mut reload_consistent = true;
    
    for seed in seeds.iter().take(3) {
        let mut unet1 = RealUNet::new(64, 128, 64, 8);
        unet1.load_params(&trained_params).unwrap();
        let gen1 = CodeDNAGenerator::new(Diffusion::new(DiffusionConfig::default()), unet1);
        let samples1 = gen1.generate_with_seed(PatchCategory::BugFix, 5, args.guidance_scale, Some(*seed));
        let (hash1, _) = compute_fingerprint(&samples1);
        
        let mut unet2 = RealUNet::new(64, 128, 64, 8);
        unet2.load_params(&trained_params).unwrap();
        let gen2 = CodeDNAGenerator::new(Diffusion::new(DiffusionConfig::default()), unet2);
        let samples2 = gen2.generate_with_seed(PatchCategory::BugFix, 5, args.guidance_scale, Some(*seed));
        let (hash2, _) = compute_fingerprint(&samples2);
        
        if hash1 != hash2 {
            reload_consistent = false;
            println!("      ⚠️  Reload inconsistency detected for seed {}", seed);
        }
    }
    
    if reload_consistent {
        println!("      ✅ Reload determinism verified (3/3 seeds)");
    }
    println!();
    
    // Generate report
    let duration = start_time.elapsed().as_secs_f64();
    
    println!("════════════════════════════════════════════════════════════════════");
    println!("P0-4 VERIFICATION RESULTS");
    println!("════════════════════════════════════════════════════════════════════");
    println!();
    println!("Summary:");
    println!("  Total comparisons: {}", results.len());
    println!("  Avg JS divergence: {:.4}", avg_divergence);
    println!("  Trained 'wins' (lower entropy): {:.1}%", win_rate * 100.0);
    println!("  Reload consistent: {}", reload_consistent);
    println!();
    
    // Pass/Fail criteria
    let divergence_pass = avg_divergence > 0.05;  // >5% divergence
    let win_rate_pass = win_rate > 0.5;           // >50% win rate
    let reload_pass = reload_consistent;          // 100% consistent
    
    println!("Pass Criteria:");
    println!("  [ {} ] Distribution divergence > 5%: {:.2}%", 
        if divergence_pass { "✅" } else { "❌" }, 
        avg_divergence * 100.0);
    println!("  [ {} ] Win rate > 50%: {:.1}%", 
        if win_rate_pass { "✅" } else { "❌" }, 
        win_rate * 100.0);
    println!("  [ {} ] Reload determinism 100%", 
        if reload_pass { "✅" } else { "❌" });
    println!();
    
    let overall_pass = divergence_pass && win_rate_pass && reload_pass;
    
    if overall_pass {
        println!("🎉 OVERALL RESULT: PASS");
        println!("   Training produces measurable, task-effective changes.");
    } else {
        println!("⚠️  OVERALL RESULT: FAIL");
        println!("   Training changes not sufficient or not reproducible.");
    }
    println!();
    
    // Write JSON report
    let report = format!(
        r#"{{
  "p0_4_verification": {{
    "timestamp": "{}",
    "trained_ckpt": "{}",
    "untrained_ckpt": "{}",
    "config": {{
      "num_conditions": {},
      "num_seeds": {},
      "num_samples": {},
      "guidance_scale": {}
    }},
    "results": {{
      "total_comparisons": {},
      "avg_js_divergence": {:.6},
      "trained_win_rate": {:.4},
      "reload_deterministic": {}
    }},
    "pass_criteria": {{
      "diversity_check": {},
      "win_rate_check": {},
      "reload_check": {},
      "overall_pass": {}
    }},
    "sample_details": {:?},
    "runtime_seconds": {:.2}
  }}
}}"#,
        chrono::Local::now().to_rfc3339(),
        args.trained,
        args.untrained.as_deref().unwrap_or("(fresh init)"),
        CONDITIONS.len(),
        args.num_seeds,
        args.num_samples,
        args.guidance_scale,
        results.len(),
        avg_divergence,
        win_rate,
        reload_consistent,
        divergence_pass,
        win_rate_pass,
        reload_pass,
        overall_pass,
        results.iter().map(|r| format!(
            "{{condition: {}, seed: {}, divergence: {:.4}}}",
            r.condition, r.seed, r.divergence
        )).collect::<Vec<_>>(),
        duration
    );
    
    fs::write(&args.output, report).expect("Failed to write report");
    println!("Report saved to: {}", args.output);
    
    // Exit code
    std::process::exit(if overall_pass { 0 } else { 1 });
}

/// Create untrained checkpoint parameters
fn create_untrained_checkpoint() -> Vec<f64> {
    let unet = RealUNet::new(64, 128, 64, 8);
    unet.get_params()
}

/// Compute entropy of distribution (lower = more structured)
fn compute_entropy(dist: &HashMap<String, usize>) -> f64 {
    let total: usize = dist.values().sum();
    if total == 0 {
        return f64::INFINITY;
    }
    
    let mut entropy = 0.0;
    for count in dist.values() {
        let p = *count as f64 / total as f64;
        if p > 0.0 {
            entropy -= p * p.ln();
        }
    }
    entropy
}
