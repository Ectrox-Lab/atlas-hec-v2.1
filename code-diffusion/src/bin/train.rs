use clap::Parser;
use code_diffusion::{
    data::PatchCategory,
    diffusion::{Diffusion, DiffusionConfig},
    models::{UNet, UNetConfig},
    training::{create_toy_dataset, Trainer, TrainingConfig},
};
use std::fs;

/// Train Code-DNA Diffusion model
#[derive(Parser)]
#[command(name = "train")]
#[command(about = "Train Code-DNA Diffusion model")]
struct Args {
    /// Number of epochs
    #[arg(short, long, default_value = "100")]
    epochs: usize,
    
    /// Batch size
    #[arg(short, long, default_value = "32")]
    batch_size: usize,
    
    /// Learning rate
    #[arg(short, long, default_value = "0.0001")]
    learning_rate: f64,
    
    /// Dataset size (toy data for testing)
    #[arg(long, default_value = "1000")]
    dataset_size: usize,
    
    /// Output directory for checkpoints
    #[arg(short, long, default_value = "checkpoints")]
    output: String,
}

fn main() {
    env_logger::init();
    
    let args = Args::parse();
    
    println!("Code-DNA Diffusion Training");
    println!("===========================");
    println!();
    println!("Configuration:");
    println!("  Epochs: {}", args.epochs);
    println!("  Batch size: {}", args.batch_size);
    println!("  Learning rate: {}", args.learning_rate);
    println!("  Dataset size: {}", args.dataset_size);
    println!("  Output: {}", args.output);
    println!();
    
    // Create output directory
    fs::create_dir_all(&args.output).expect("Failed to create output directory");
    
    // Initialize model
    println!("Initializing model...");
    let diffusion = Diffusion::new(DiffusionConfig::default());
    let unet = UNet::new(UNetConfig::default());
    
    // Training config
    let train_config = TrainingConfig {
        batch_size: args.batch_size,
        num_epochs: args.epochs,
        learning_rate: args.learning_rate,
        patience: 10,
        min_epochs: 20,
        log_interval: 10,
        checkpoint_interval: 50,
    };
    
    // Create trainer
    let mut trainer = Trainer::new(diffusion, unet, train_config);
    
    // Create dataset (toy data for now)
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
    let history = trainer.train(train_data, val_data);
    
    // Summary
    println!();
    println!("Training complete!");
    println!("  Best val loss: {:.6} at epoch {}", history.best_val_loss, history.best_epoch);
    println!();
    println!("Checkpoints saved to: {}/", args.output);
}
