//! CWCI Report Generator Binary
//! 
//! 生成代码世界意识指数分析报告
//! 
//! Usage:
//!   cargo run --bin cwci_report --release

use socs_universe_search::cwci_report::{generate_cwci_report, print_cwci_report};

fn main() -> anyhow::Result<()> {
    println!("🔮 Code-World Consciousness Index (CWCI) Report Generator\n");
    
    let report = generate_cwci_report("outputs")?;
    print_cwci_report(&report);
    
    // 保存JSON报告
    let report_path = "outputs/cwci_report.json";
    let json = serde_json::to_string_pretty(&report)?;
    std::fs::write(report_path, json)?;
    println!("📄 Report saved to: {}\n", report_path);
    
    Ok(())
}
