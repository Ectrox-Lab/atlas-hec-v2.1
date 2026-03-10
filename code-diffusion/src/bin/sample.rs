use clap::Parser;
use code_diffusion::{
    data::PatchCategory,
    diffusion::{Diffusion, DiffusionConfig},
    models::{UNet, UNetConfig},
    sampling::CodeDNAGenerator,
    verification::{PatchDecoder, DNADecoder},
};

/// Generate samples from Code-DNA Diffusion model
#[derive(Parser)]
#[command(name = "sample")]
#[command(about = "Generate code patches using trained diffusion model")]
struct Args {
    /// Condition (bugfix/perf/memory/safety/refactor)
    #[arg(short, long, default_value = "bugfix")]
    condition: String,
    
    /// Number of samples
    #[arg(short, long, default_value = "10")]
    num_samples: usize,
    
    /// Guidance scale (1.0 = no guidance, higher = stronger condition)
    #[arg(short, long, default_value = "1.0")]
    guidance_scale: f64,
    
    /// Checkpoint path (if not provided, uses untrained model)
    #[arg(short, long)]
    checkpoint: Option<String>,
    
    /// Output file
    #[arg(short, long, default_value = "generated_patches.txt")]
    output: String,
    
    /// Decode to patch format
    #[arg(long, default_value = "true")]
    decode: bool,
}

fn parse_condition(s: &str) -> PatchCategory {
    match s.to_lowercase().as_str() {
        "bugfix" | "bug" => PatchCategory::BugFix,
        "perf" | "performance" => PatchCategory::Performance,
        "memory" | "mem" => PatchCategory::Memory,
        "safety" | "safe" => PatchCategory::Safety,
        "refactor" => PatchCategory::Refactor,
        "io" => PatchCategory::IO,
        "concurrency" | "concurrent" => PatchCategory::Concurrency,
        _ => {
            eprintln!("Warning: Unknown condition '{}', using BugFix", s);
            PatchCategory::BugFix
        }
    }
}

fn main() {
    env_logger::init();
    
    let args = Args::parse();
    
    println!("Code-DNA Diffusion Sampling");
    println!("============================");
    println!();
    
    // Parse condition
    let condition = parse_condition(&args.condition);
    println!("Condition: {:?}", condition);
    println!("Number of samples: {}", args.num_samples);
    println!("Guidance scale: {}", args.guidance_scale);
    println!();
    
    // Initialize model
    println!("Initializing model...");
    let diffusion = Diffusion::new(DiffusionConfig::default());
    let unet = UNet::new(UNetConfig::default());
    
    // TODO: Load checkpoint if provided
    if let Some(ref checkpoint) = args.checkpoint {
        println!("Loading checkpoint: {} (placeholder)", checkpoint);
        // In real implementation: load model weights
    } else {
        println!("Using untrained model (random initialization)");
    }
    println!();
    
    // Create generator
    let generator = CodeDNAGenerator::new(diffusion, unet);
    
    // Generate samples
    println!("Generating samples...");
    let samples = generator.generate(condition, args.num_samples, args.guidance_scale);
    
    println!("Generated {} samples", samples.len());
    println!();
    
    // Decode if requested
    if args.decode {
        println!("Decoding to patches...");
        let decoder = PatchDecoder::new();
        
        let mut output_text = String::new();
        output_text.push_str(&format!("# Generated Patches (condition: {:?})\n", condition));
        output_text.push_str(&format!("# Guidance scale: {}\n", args.guidance_scale));
        output_text.push_str("#\n\n");
        
        for (i, sample) in samples.iter().enumerate() {
            output_text.push_str(&format!("## Sample {}\n", i + 1));
            output_text.push_str(&format!("Condition: {:?}\n", sample.condition));
            output_text.push_str("Tokens: ");
            for token in &sample.tokens[..10] {
                output_text.push_str(&format!("{:?} ", token));
            }
            output_text.push_str("...\n\n");
            
            let patch = decoder.decode(sample);
            output_text.push_str("Patch:\n");
            output_text.push_str(&patch);
            output_text.push_str("\n---\n\n");
        }
        
        // Write to file
        std::fs::write(&args.output, &output_text).expect("Failed to write output");
        println!("Saved to: {}", args.output);
        
        // Print preview
        println!();
        println!("Preview (first 20 lines):");
        for line in output_text.lines().take(20) {
            println!("{}", line);
        }
        if output_text.lines().count() > 20 {
            println!("... ({} more lines)", output_text.lines().count() - 20);
        }
    }
    
    println!();
    println!("Sampling complete!");
}
