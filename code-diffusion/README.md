# Code-DNA Diffusion

A Rust implementation of conditional diffusion models for code patch generation.
Adapted from [DNA-Diffusion](https://github.com/pinellolab/DNA-Diffusion) for the Hyperbrain project.

## Overview

Code-DNA Diffusion generates code patches using conditional diffusion models. It supports three representations:

1. **Edit-DNA** (recommended): Patch operations as token sequences
2. **Opcode-DNA**: Low-level IR instruction sequences
3. **Graph-DNA**: AST/CFG motif sequences

## Architecture

```
Raw Code/Diff → Tokenizer → Code-DNA → Diffusion Model → Generated DNA → Decoder → Patch
                                    ↑
                              Condition (bugfix/perf/safety)
```

## Quick Start

### Build

```bash
cd code-diffusion
cargo build --release
```

### Generate Patches

```bash
# Generate 10 bugfix patches
./target/release/code-diffusion generate \
    --condition bugfix \
    --num-samples 10 \
    --guidance-scale 2.0 \
    --output patches.txt
```

### System Info

```bash
./target/release/code-diffusion info
```

## Core Components

### 1. Diffusion Module (`src/diffusion/`)

Implements the core diffusion process:
- `q_sample`: Forward diffusion (add noise)
- `p_sample`: Reverse diffusion (denoise)
- `p_sample_guided`: Classifier-free guidance

### 2. Models (`src/models/`)

- `UNet`: Noise prediction network
- `TimeMLP`: Time embedding
- `ClassEmbedding`: Condition embedding

### 3. Data (`src/data/`)

- `EditToken`: Patch operation vocabulary
- `EditDNA`: Fixed-window representation
- `PatchCategory`: Condition labels

### 4. Sampling (`src/sampling/`)

- `CodeDNAGenerator`: Single-sample generation
- `BatchGenerator`: High-throughput generation

### 5. Verification (`src/verification/`)

- `PatchDecoder`: DNA → Patch
- `VerifierStack`: Multi-stage verification

## Configuration

Example config (`configs/default.yaml`):

```yaml
diffusion:
  timesteps: 1000
  beta_start: 0.0001
  beta_end: 0.02
  loss_type: huber
  p_uncond: 0.1

model:
  dim: 64
  dim_mults: [1, 2, 4]
  num_classes: 8
  time_emb_dim: 256

training:
  batch_size: 32
  num_epochs: 2000
  learning_rate: 0.0001
  patience: 100
```

## Integration with Hyperbrain

```rust
use code_diffusion::{CodeDNAComponent, Condition};

// Create component
let component = CodeDNAComponent::new(diffusion, unet, decoder, verifiers);

// Generate candidates
let candidates = component.generate_candidates(
    &context,
    Condition::BugFix,
    num_samples: 128,
    guidance_scale: 2.5,
);

// Returns verified candidates only
for candidate in candidates {
    apply_patch(candidate);
}
```

## Development Roadmap

### Phase 1: MVP (Current)
- [x] Core diffusion algorithms
- [x] Edit-DNA representation
- [ ] Full UNet implementation
- [ ] Training script
- [ ] Sampling script

### Phase 2: Feature Complete
- [ ] Classifier-free guidance
- [ ] All three DNA types
- [ ] Hydra configuration
- [ ] Checkpoint management

### Phase 3: Hyperbrain Integration
- [ ] Verifier stack
- [ ] Performance optimization
- [ ] A1×A5/E-class support

## Differences from DNA-Diffusion

| Aspect | DNA-Diffusion | Code-DNA Diffusion |
|--------|---------------|-------------------|
| Domain | DNA sequences | Code patches |
| Representation | One-hot (4×200) | Token sequences |
| Conditions | Cell types | Patch categories |
| Post-processing | Sequence analysis | Verifier stack |
| Output | Synthetic DNA | Verified patches |

## License

MIT License - See LICENSE file

## Acknowledgments

Based on [DNA-Diffusion](https://github.com/pinellolab/DNA-Diffusion) by Pinello Lab.
Adapted for the Hyperbrain research project.
