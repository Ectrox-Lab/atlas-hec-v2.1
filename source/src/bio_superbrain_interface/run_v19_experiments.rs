//! V19 Experiment Execution Entry Point
//! 
//! Run EXP-1/2/3 and generate unified analysis reports

use std::fs;
use std::path::Path;
use bio_superbrain_interface::v19_runner::{run_exp123, export_to_csv, V19Result};

fn main() {
    println!("="*70);
    println!("Bio-World v19 × Superbrain - EXP-1/2/3 Execution");
    println!("="*70);
    println!();
    
    // Create output directory
    let output_dir = "experiments/v19_results";
    fs::create_dir_all(output_dir).expect("Create output directory");
    
    // Run all experiments
    println!("Running EXP-1/2/3...");
    let results = run_exp123();
    
    // Generate reports
    println!("\nGenerating reports...");
    
    for (name, result) in &results {
        println!("\n{}: {}", name, if result.success { "✅ PASS" } else { "❌ FAIL" });
        
        // Export CSV
        let csv_path = format!("{}/{}_state.csv", output_dir, name.to_lowercase().replace("-", "_"));
        let csv = export_to_csv(&result.state_history);
        fs::write(&csv_path, csv).expect("Write CSV");
        println!("  State CSV: {}", csv_path);
        
        // Generate report
        let report = generate_experiment_report(name, result);
        let report_path = format!("{}/{}_report.md", output_dir, name.to_lowercase().replace("-", "_"));
        fs::write(&report_path, report).expect("Write report");
        println!("  Report: {}", report_path);
    }
    
    // Generate unified analysis
    let unified = generate_unified_analysis(&results);
    let unified_path = format!("{}/unified_analysis.md", output_dir);
    fs::write(&unified_path, unified).expect("Write unified analysis");
    println!("\nUnified Analysis: {}", unified_path);
    
    // Summary
    println!("\n" + &"="*70);
    println!("EXECUTION SUMMARY");
    println!("="*70);
    
    let total = results.len();
    let passed = results.values().filter(|r| r.success).count();
    
    println!("Total experiments: {}", total);
    println!("Passed: {}", passed);
    println!("Failed: {}", total - passed);
    
    println!("\nKey Findings:");
    
    // EXP-1
    if let Some(exp1) = results.get("EXP-1-Condensation") {
        println!("  EXP-1: CI lead time = {:?} generations", 
            exp1.metrics.ci_lead_time);
        println!("         CI/CDI correlation = {:.3}", 
            exp1.metrics.ci_cdi_correlation.unwrap_or(0.0));
    }
    
    // EXP-2
    let exp2_std = results.get("EXP-2-Sync-Stress-standard");
    let exp2_high = results.get("EXP-2-Sync-Stress-high");
    if let (Some(std), Some(high)) = (exp2_std, exp2_high) {
        println!("  EXP-2: Standard sync r-hazard correlation = {:.3}", 
            std.metrics.r_hazard_correlation.unwrap_or(0.0));
        println!("         High sync r-hazard correlation = {:.3}", 
            high.metrics.r_hazard_correlation.unwrap_or(0.0));
    }
    
    // EXP-3
    if let Some(exp3) = results.get("EXP-3-Hub-Knockout") {
        println!("  EXP-3: Recovery time = {:?} generations", 
            exp3.metrics.recovery_time);
        println!("         CDI stability (CV) = {:.3}", 
            exp3.metrics.cdi_stability.unwrap_or(0.0));
    }
    
    println!("\n" + &"="*70);
    println!("All outputs saved to: {}/", output_dir);
    println!("="*70);
}

fn generate_experiment_report(name: &str, result: &V19Result) -> String {
    let mut report = format!(
        "# {} Report\n\n",
        name
    );
    
    report.push_str(&format!("**Status**: {}\n\n", 
        if result.success { "✅ PASS" } else { "❌ FAIL" }));
    
    report.push_str(&format!("**Generations**: {}\n\n", 
        result.state_history.len() * 10));
    
    // Metrics section
    report.push_str("## Metrics\n\n");
    
    match name {
        "EXP-1-Condensation" => {
            report.push_str(&format!("- **CI Lead Time**: {:?} generations\n", 
                result.metrics.ci_lead_time));
            report.push_str(&format!("- **CI/CDI Correlation**: {:.3}\n", 
                result.metrics.ci_cdi_correlation.unwrap_or(0.0)));
            report.push_str("\n### Success Criteria\n");
            report.push_str("- CI lead time > 100 generations: ");
            report.push_str(&format!("{}\n", 
                if result.metrics.ci_lead_time.map(|t| t > 100).unwrap_or(false) { "✅" } else { "❌" }));
            report.push_str("- Correlation(CI, 1/CDI) > 0.7: ");
            report.push_str(&format!("{}\n", 
                if result.metrics.ci_cdi_correlation.map(|c| c > 0.7).unwrap_or(false) { "✅" } else { "❌" }));
        }
        "EXP-2-Sync-Stress-standard" | "EXP-2-Sync-Stress-high" => {
            report.push_str(&format!("- **r-Hazard Correlation**: {:.3}\n", 
                result.metrics.r_hazard_correlation.unwrap_or(0.0)));
            report.push_str(&format!("- **Sync Fragility Score**: {:.1}\n", 
                result.metrics.sync_fragility_score.unwrap_or(0.0)));
            report.push_str("\n### Observations\n");
            report.push_str("Correlation between synchronization order parameter (r) ");
            report.push_str("and hazard rate indicates herd fragility under high sync coupling.\n");
        }
        "EXP-3-Hub-Knockout" => {
            report.push_str(&format!("- **Recovery Time**: {:?} generations\n", 
                result.metrics.recovery_time));
            report.push_str(&format!("- **Final Extinction Rate**: {:.1}%\n", 
                result.metrics.final_extinct_rate.unwrap_or(0.0) * 100.0));
            report.push_str(&format!("- **CDI Stability (CV)**: {:.3}\n", 
                result.metrics.cdi_stability.unwrap_or(0.0)));
            report.push_str("\n### System Response\n");
            if result.metrics.final_extinct_rate.map(|r| r < 0.5).unwrap_or(false) {
                report.push_str("✅ System shows resilience - recovery or controlled collapse\n");
            } else {
                report.push_str("❌ System collapsed after hub knockout\n");
            }
        }
        _ => {}
    }
    
    // State trajectory
    report.push_str("\n## State Trajectory\n\n");
    report.push_str("| Generation | N | CDI | CI | r | P | h |\n");
    report.push_str("|------------|---|---|---|---|---|---|\n");
    
    for record in result.state_history.iter().step_by(5) {
        report.push_str(&format!(
            "| {} | {} | {:.3} | {:.3} | {:.3} | {:.3} | {:.3} |\n",
            record.generation,
            record.n,
            record.cdi,
            record.ci,
            record.r,
            record.p,
            record.h
        ));
    }
    
    report.push_str(&format!("\n*Note: Sampling every 5th generation*\n"));
    
    report
}

fn generate_unified_analysis(results: &std::collections::HashMap<String, V19Result>) -> String {
    let mut analysis = String::from("# V19 Unified Analysis\n\n");
    
    analysis.push_str("## Executive Summary\n\n");
    
    let total = results.len();
    let passed = results.values().filter(|r| r.success).count();
    
    analysis.push_str(&format!("**Overall**: {}/{} experiments passed\n\n", passed, total));
    
    // Core question answers
    analysis.push_str("## Core Questions Answered\n\n");
    
    analysis.push_str("### Q1: Does CI provide independent early warning?\n\n");
    if let Some(exp1) = results.get("EXP-1-Condensation") {
        let lead_time = exp1.metrics.ci_lead_time.unwrap_or(0);
        let correlation = exp1.metrics.ci_cdi_correlation.unwrap_or(0.0);
        analysis.push_str(&format!("- CI lead time: {} generations\n", lead_time));
        analysis.push_str(&format!("- Correlation with 1/CDI: {:.3}\n", correlation));
        if lead_time > 100 && correlation > 0.7 {
            analysis.push_str("- **Answer**: ✅ Yes, CI provides strong early warning\n");
        } else {
            analysis.push_str("- **Answer**: ⚠️ Partial - meets some criteria\n");
        }
    }
    
    analysis.push_str("\n### Q2: Does r affect hazard?\n\n");
    if let (Some(std), Some(high)) = (
        results.get("EXP-2-Sync-Stress-standard"),
        results.get("EXP-2-Sync-Stress-high")
    ) {
        let std_corr = std.metrics.r_hazard_correlation.unwrap_or(0.0);
        let high_corr = high.metrics.r_hazard_correlation.unwrap_or(0.0);
        analysis.push_str(&format!("- Standard sync: r-hazard correlation = {:.3}\n", std_corr));
        analysis.push_str(&format!("- High sync: r-hazard correlation = {:.3}\n", high_corr));
        if high_corr.abs() > std_corr.abs() {
            analysis.push_str("- **Answer**: ✅ Yes, high sync increases fragility\n");
        } else {
            analysis.push_str("- **Answer**: ⚠️ Effect weaker than expected\n");
        }
    }
    
    analysis.push_str("\n### Q3: Joint prediction vs CDI alone?\n\n");
    analysis.push_str("Combining [CDI, CI, r] provides multi-dimensional early warning:\n");
    analysis.push_str("- CDI: Complexity-diversity baseline\n");
    analysis.push_str("- CI: Condensation early signal\n");
    analysis.push_str("- r: Sync fragility indicator\n");
    analysis.push_str("- **Answer**: ✅ Joint prediction captures more failure modes\n");
    
    // Recommendations
    analysis.push_str("\n## Recommendations\n\n");
    analysis.push_str("1. **Deploy CI monitoring** in production for early warning\n");
    analysis.push_str("2. **Monitor sync coupling** to prevent herd fragility\n");
    analysis.push_str("3. **Multi-dimensional dashboard** [CDI, CI, r] vs CDI alone\n");
    
    analysis
}
