use clap::Parser;
use code_diffusion::{
    diffusion::{Diffusion, DiffusionConfig},
    models::RealUNet,
    training::{create_toy_dataset, Trainer, TrainingConfig},
};
use std::fs;

/// Train Code-DNA Diffusion model
#[derive(Parser)]
#[command(name = "train")]
#[command(about = "Train Code-DNA Diffusion model with REAL parameter updates")]
struct Args {
    /// Number of epochs
    #[arg(short, long, default_value = "20")]
    epochs: usize,
    
    /// Batch size
    #[arg(short, long, default_value = "16")]
    batch_size: usize,
    
    /// Learning rate
    #[arg(short, long, default_value = "0.001")]
    learning_rate: f64,
    
    /// Dataset size (toy data for testing)
    #[arg(long, default_value = "200")]
    dataset_size: usize,
    
    /// Output directory for checkpoints
    #[arg(short, long, default_value = "checkpoints")]
    output: String,
}

fn main() {
    env_logger::init();
    
    let args = Args::parse();
    
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║     Code-DNA Diffusion Training (REAL Parameters)        ║");
    println!("╚══════════════════════════════════════════════════════════╝");
    println!();
    
    // Configuration
    println!("Configuration:");
    println!("  Epochs: {}", args.epochs);
    println!("  Batch size: {}", args.batch_size);
    println!("  Learning rate: {}", args.learning_rate);
    println!("  Dataset size: {}", args.dataset_size);
    println!("  Output: {}", args.output);
    println!();
    
    // Create output directory
    fs::create_dir_all(&args.output).expect("Failed to create output directory");
    
    // Initialize REAL model with parameters
    println!("Initializing REAL model...");
    let diffusion = Diffusion::new(DiffusionConfig::default());
    let unet = RealUNet::new(64, 128, 64, 8);
    
    // Show initial parameter stats
    let initial_stats = unet.param_stats();
    println!("Initial parameters:");
    println!("  Count: {}", initial_stats.count);
    println!("  Mean: {:.6}", initial_stats.mean);
    println!("  Std: {:.6}", initial_stats.std);
    println!("  Range: [{:.4}, {:.4}]", initial_stats.min, initial_stats.max);
    println!();
    
    // Training config
    let train_config = TrainingConfig {
        batch_size: args.batch_size,
        num_epochs: args.epochs,
        learning_rate: args.learning_rate,
        patience: 10,
        min_epochs: 5,
        log_interval: 5,
        checkpoint_interval: 10,
    };
    
    // Create trainer
    let mut trainer = Trainer::new(diffusion, unet, train_config);
    
    // Record initial hash
    let initial_hash = trainer.current_param_hash();
    println!("Initial parameter hash: {:016x}", initial_hash);
    println!();
    
    // Create dataset
    println!("Creating dataset...");
    let dataset = create_toy_dataset(args.dataset_size);
    
    // Split train/val
    let split_idx = dataset.len() * 8 / 10;
    let train_data = &dataset[..split_idx];
    let val_data = &dataset[split_idx..];
    
    println!("  Train: {} samples", train_data.len());
    println!("  Val: {} samples", val_data.len());
    println!();
    
    // Train
    println!("Starting training...");
    println!("─────────────────────────────────────────────────────────");
    let history = trainer.train(train_data, val_data);
    println!("─────────────────────────────────────────────────────────");
    println!();
    
    // Final verification - get hash and stats BEFORE borrowing history
    let final_hash = trainer.current_param_hash();
    let final_stats = trainer.param_stats();
    
    // Extract history data we need
    let best_val_loss = history.best_val_loss;
    let best_epoch = history.best_epoch;
    let final_train_loss = *history.train_losses.last().unwrap_or(&0.0);
    
    println!("═══════════════════════════════════════════════════════════");
    println!("TRAINING SUMMARY");
    println!("═══════════════════════════════════════════════════════════");
    println!();
    println!("Parameter Hash Change:");
    println!("  Initial: {:016x}", initial_hash);
    println!("  Final:   {:016x}", final_hash);
    println!("  CHANGED: {} ✅", initial_hash != final_hash);
    println!();
    println!("Parameter Statistics:");
    println!("  Initial: mean={:.6}, std={:.6}", initial_stats.mean, initial_stats.std);
    println!("  Final:   mean={:.6}, std={:.6}", final_stats.mean, final_stats.std);
    println!();
    println!("Training History:");
    println!("  Best val loss: {:.6} at epoch {}", best_val_loss, best_epoch);
    println!("  Final train loss: {:.6}", final_train_loss);
    println!();
    
    // Parameter change verification
    if initial_hash == final_hash {
        eprintln!("❌ ERROR: Parameters did not change! Training failed.");
        std::process::exit(1);
    } else {
        println!("✅ VERIFIED: Parameters changed during training");
    }
    
    println!();
    println!("Checkpoints saved to: {}/", args.output);
}
