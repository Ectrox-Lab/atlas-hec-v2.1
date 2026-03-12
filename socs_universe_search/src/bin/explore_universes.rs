//! 宇宙探索主程序

use socs_universe_search::search_scheduler::run_first8_batch;

fn main() -> anyhow::Result<()> {
    println!("SOCS Universe Search Engine");
    println!("===========================\n");
    
    // 运行第一批8组实验
    run_first8_batch()?;
    
    Ok(())
}
