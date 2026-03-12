//! 搜索调度器
//! 
//! 运行第一批8组实验：8 plans × 3 seeds = 24 universes

use crate::experiment_plan::{first8_plans, ExperimentPlan};
use crate::stress_profile::StressProfileConfig;
use crate::telemetry::print_run_summary;
use crate::universe_config::UniverseConfig;
use crate::universe_runner::run_universe_once;
use anyhow::Result;

/// 运行第一批8组实验
pub fn run_first8_batch() -> Result<()> {
    let plans = first8_plans();
    let mut universe_id: u64 = 0;
    
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║     SOCS Universe Search v0 - First 8 Experiments          ║");
    println!("╚════════════════════════════════════════════════════════════╝");
    println!();
    println!("Total plans: {}", plans.len());
    println!("Seeds per plan: 3");
    println!("Total universes: {}", plans.len() * 3);
    println!();
    
    let mut success_count = 0;
    let mut fail_count = 0;
    
    for plan in &plans {
        println!("─────────────────────────────────────────────────────────────");
        println!("[PLAN] {}: {} × {}", 
            plan.label, 
            plan.family.as_str(), 
            plan.stress.as_str()
        );
        println!("       {}", plan.rationale);
        println!();
        
        let base_config = UniverseConfig::default_for_family(plan.family, 0, 0);
        
        for seed in plan.seeds {
            let mut cfg = base_config.clone();
            cfg.universe_id = universe_id;
            cfg.seed = *seed;
            cfg.stress_profile = plan.stress;
            cfg.stress = StressProfileConfig::default_for(plan.stress);
            
            print!("  [RUN] u{} seed={}... ", cfg.universe_id, seed);
            
            match run_universe_once(&cfg) {
                Ok(summary) => {
                    print!("done | ");
                    print_run_summary(&summary);
                    success_count += 1;
                }
                Err(e) => {
                    println!("ERROR: {}", e);
                    fail_count += 1;
                }
            }
            
            universe_id += 1;
        }
        
        println!();
    }
    
    println!("═════════════════════════════════════════════════════════════");
    println!("                    BATCH COMPLETE                            ");
    println!("═════════════════════════════════════════════════════════════");
    println!();
    println!("Successful: {}", success_count);
    println!("Failed: {}", fail_count);
    println!("Total: {}", universe_id);
    println!();
    println!("Output files:");
    println!("  - outputs/*_telemetry.csv     (tick-level time series)");
    println!("  - outputs/*_summary.json      (per-universe evaluation)");
    println!("  - outputs/hall_of_fame.jsonl  (top structures)");
    println!("  - outputs/graveyard.jsonl     (failure patterns)");
    
    Ok(())
}

/// 运行单个实验计划（用于测试）
pub fn run_single_plan(plan: &ExperimentPlan) -> Result<()> {
    let base_config = UniverseConfig::default_for_family(plan.family, 0, 0);
    
    for seed in plan.seeds {
        let mut cfg = base_config.clone();
        cfg.universe_id = 0;
        cfg.seed = *seed;
        cfg.stress_profile = plan.stress;
        cfg.stress = StressProfileConfig::default_for(plan.stress);
        
        println!("Running: {} seed={}", plan.label, seed);
        let summary = run_universe_once(&cfg)?;
        print_run_summary(&summary);
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::experiment_plan::first8_plans;
    
    #[test]
    fn test_batch_size() {
        let plans = first8_plans();
        assert_eq!(plans.len(), 8);
        
        let total_universes = plans.iter().map(|p| p.seeds.len()).sum::<usize>();
        assert_eq!(total_universes, 24); // 8 × 3
    }
}
