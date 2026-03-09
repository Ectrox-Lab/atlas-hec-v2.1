# Bio-World 研究平台体系结构

**Artificial Life + Complex Systems Experiments**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BIO-WORLD RESEARCH PLATFORM                         │
│                      (Atlas-HEC v2.1 + ZeroClaw Labs)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LAYER 0: 执行引擎                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Rust + CUDA Runtime                                                   │  │
│  │  • 128 Parallel Universes                                             │  │
│  │  • 25×25×8 Grid per Universe                                          │  │
│  │  • 6-Dimensional DNA                                                  │  │
│  │  • Akashic Cross-Universe Memory                                      │  │
│  │  • 10-BOSS Passive-Aggressive System                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌────────────────────────┐ ┌────────────────────────┐ ┌────────────────────────┐
│   EXPERIMENT TYPE A    │ │   EXPERIMENT TYPE B    │ │   EXPERIMENT TYPE C    │
│      Atlas V5          │ │      Bio-World         │ │     K→∞ Boundary       │
│   (CDI Saturation)     │ │    v18.1 (Extinction)  │ │    (Superlinearity)    │
├────────────────────────┤ ├────────────────────────┤ ├────────────────────────┤
│ • S-curve observation  │ │ • 3-phase dynamics     │ │ • MAX_POP 500→5000     │
│ • K_I estimation       │ │ • Cascade detection    │ │ • Synapse 15→?         │
│ • Memory effects       │ │ • Early warning        │ │ • Resource unbounded   │
└──────────┬─────────────┘ └──────────┬─────────────┘ └──────────┬─────────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LAYER 1: 数据采集层                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │  evolution   │  │   snapshot   │  │   akashic    │  │   lineage    │   │
│   │    .csv      │  │    .bin      │  │   records    │  │    tree      │   │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│          │                 │                 │                 │           │
│          ▼                 ▼                 ▼                 ▼           │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  Time-Series Metrics (per generation):                           │     │
│   │  • population, avg_cdi, avg_collaboration                        │     │
│   │  • extinct_count, alive_universes                                │     │
│   │  • boss_progress, total_births/deaths                            │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LAYER 2: 分析工具链                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    THREE-LAYER DYNAMICS MODEL                       │    │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────────────┐  │    │
│  │  │   Layer A       │ │   Layer B       │ │   Layer C            │  │    │
│  │  │  Population     │ │     CDI         │ │  Cooperation         │  │    │
│  │  │  Dynamics       │ │  Dynamics       │ │  Gate                │  │    │
│  │  │                 │ │                 │ │                      │  │    │
│  │  │ dU/dt = -h(t)·U │ │ dI/dt = (...)   │ │ C = σ((G-θ)/τ)       │  │    │
│  │  │  (hazard model) │ │  (RyanX Law)    │ │  (sigmoid)           │  │    │
│  │  └─────────────────┘ └─────────────────┘ └──────────────────────┘  │    │
│  │                                                                    │    │
│  │  Fitting Scripts:                                                  │    │
│  │  • fit_population_collapse_model.py   • extinction_precursor_      │    │
│  │  • fit_cdi_model_v2.py                    detector.py              │    │
│  │  • fit_cooperation_gate_v2.py                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PATTERN DETECTORS                                │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │   Phase     │  │    CDI      │  │  Cascade    │  │  Critical  │ │    │
│  │  │  Separator  │  │  Inflection │  │   Speed     │  │ Transition │ │    │
│  │  │             │  │  Detector   │  │  Analyzer   │  │  Detector  │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LAYER 3: 科学发现层                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  DISCOVERY 1: Three-Phase Extinction Dynamics                         │  │
│  │                                                                       │  │
│  │   Plateau Phase          Degradation Phase        Cascade Phase       │  │
│  │   ─────────────          ────────────────         ────────────        │  │
│  │   CDI: 0.42→0.68         CDI: 0.68→0.54          CDI: 0.54→0.01      │  │
│  │   N: ~17500 (stable)     N: slow decline         N: collapse          │  │
│  │   E: 0                   E: 0                    E: 0→126             │  │
│  │                                                                       │  │
│  │   Key Insight: CDI degradation PRECEDES extinction                    │  │
│  │                (structure degrades before quantity)                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  DISCOVERY 2: CDI as Early-Warning Indicator                          │  │
│  │                                                                       │  │
│  │   Gen 6500: CDI inflection (I ≈ 0.542)    ────100 gen────▶           │  │
│  │   Gen 6600: First extinction (E = 1)                                  │  │
│  │                                                                       │  │
│  │   Warning Window: Δt ≈ 100 generations                                │  │
│  │   Signal Type: d²I/dt² extremum (second derivative)                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  DISCOVERY 3: Extinction Cascade (Cross-Universe)                     │  │
│  │                                                                       │  │
│  │   E(t): 0 ──▶ 1 ──▶ 43 ──▶ 97 ──▶ 111 ──▶ 126                        │  │
│  │          ↑                                                    ↑       │  │
│  │       Trigger                                          Cascade        │  │
│  │       (Gen 6600)                                       Complete       │  │
│  │                                                    (Gen 6900, 300gen) │  │
│  │                                                                       │  │
│  │   Cascade Speed: 0.37 universes/generation (avg)                      │  │
│  │   Mechanism: Failure probability ∝ number_of_failed_neighbors         │  │
│  │   (Similar to: financial contagion, power grid cascade)               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  DISCOVERY 4: RyanX Innovation Law (Resource-Limited)                 │  │
│  │                                                                       │  │
│  │   dI/dt = (αL + βT)(1 - I/K_I) - γσ²                                 │  │
│  │                                                                       │  │
│  │   Verified: K_I ≈ 0.8 (emergent, not hardcoded)                       │  │
│  │   Verified: b > 0 (positive feedback, p < 0.001)                      │  │
│  │   NOT verified: Unbounded superlinearity                              │  │
│  │                                                                       │  │
│  │   Status: "Observed dynamic law in Bio-World systems"                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LAYER 4: 验证与迭代                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  VALIDATION PIPELINE:                                                       │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────┐  │
│   │  Single Run │────▶│  Cross-Seed │────▶│  Parameter  │────▶│  K→∞    │  │
│   │  (Current)  │     │  Validation │     │  Variation  │     │  Test   │  │
│   └─────────────┘     └─────────────┘     └─────────────┘     └─────────┘  │
│          │                   │                   │                 │        │
│          ▼                   ▼                   ▼                 ▼        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Evidence Strength:                                                 │   │
│   │  • Single run: Discovery (observed once)                           │   │
│   │  • Cross-seed: Pattern (reproducible)        ◄── CURRENT TARGET    │   │
│   │  • Parameter: Robustness (parameter-invariant)                     │   │
│   │  • K→∞: Universal law (system-independent)                         │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ITERATION CYCLE:                                                           │
│                                                                             │
│   Hypothesis ──▶ Experiment ──▶ Model Fit ──▶ Prediction ──▶ New Exp  ──▶  │
│       ▲                                                            │       │
│       └────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESEARCH OUTPUTS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DOCUMENTS:                                                                 │
│  • MODEL_VALIDATION_REPORT_v2.md    (Full technical report)                 │
│  • BIOWORLD_V18_DISCOVERY_SUMMARY.md (4 key findings)                       │
│  • REPRODUCIBLE_EXPERIMENT.md       (Replication guide)                     │
│  • BIOWORLD_RESEARCH_ARCHITECTURE.md (This document)                        │
│                                                                             │
│  CODE:                                                                      │
│  • fit_*_model_v2.py                (Three-layer fitting)                   │
│  • extinction_precursor_detector.py (Early warning system)                  │
│  • run_model_fitting_v2.sh          (Automated pipeline)                    │
│                                                                             │
│  DATA:                                                                      │
│  • model_fit_results/*.json         (Fitted parameters)                     │
│  • model_fit_results/*.png          (Visualizations)                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


================================================================================
                              RESEARCH PARADIGM
================================================================================

Bio-World follows the Artificial Life / Complex Systems research paradigm:

┌─────────────────────────────────────────────────────────────────────────────┐
│  Traditional ML/AI        vs.        Bio-World / ALife                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Optimize a target                Simulate open-ended dynamics              │
│  Fixed dataset                    Generated data (simulation)               │
│  Single agent                     Multi-agent, multi-universe               │
│  Static rules                     Evolving rules (DNA + Akashic)            │
│  Performance metrics              Emergent statistics (CDI, cascade)        │
└─────────────────────────────────────────────────────────────────────────────┘

Comparable Systems:
  • Avida (Lenski et al.)        - Digital evolution
  • Tierra (Ray)                 - Self-replicating programs
  • Open-ended evolution systems - ALife research

Bio-World Unique Features:
  • Memory (Akashic records)     - Cross-universe learning
  • Cooperation gate             - Threshold-based social behavior
  • 10-BOSS system               - Environmental pressure hierarchy
  • CDI metric                   - Complexity quantification


================================================================================
                           CURRENT STATUS (2026-03-09)
================================================================================

COMPLETED:
  ✅ Three-phase extinction dynamics identified
  ✅ CDI early-warning signal (100-gen window) detected
  ✅ Extinction cascade characterized
  ✅ RyanX law resource-limited form verified (K_I ≈ 0.8)
  ✅ Cooperation gate model fitted (R² = 0.99)
  ✅ Reproducible experiment pipeline established

IN PROGRESS:
  🔄 Cross-seed validation (P0 priority)
  🔄 Hazard rate model implementation

PLANNED:
  ⏳ Three-variable joint fitting (N, U, I)
  ⏳ K_I robustness testing
  ⏳ K→∞ boundary experiment

BLOCKED:
  ⏸️ None


================================================================================
                              KEY EQUATIONS
================================================================================

1. RyanX Innovation Law (Resource-Limited):
   
   dI/dt = (α·L + β·T)(1 - I/K_I) - γ·σ²
   
   Verified: K_I ≈ 0.8, α ≈ 0.1, β ≈ 0.05

2. Extinction Hazard Rate:
   
   h(t) = h₀ + α·B(t) + β·(I_crit - I(t))₊ + γ·E(t)
   
   Where E(t) = extinct_count / total_universes

3. Cooperation Gate:
   
   C(t) = σ((G(t) - θ)/τ) = 1 / (1 + exp(-(G(t) - θ)/τ))
   
   Verified: θ ≈ 0.984, τ ≈ 0.304, R² ≈ 0.99

4. Early-Warning Signal:
   
   Detection: d²I/dt² local extremum
   Window: Δt ≈ 100 generations
   Threshold: I_crit ≈ 0.54


================================================================================
                              NEXT MILESTONE
================================================================================

Target: Cross-Seed Validation of CDI Early-Warning Signal

Criteria:
  • Run Bio-World v18.1 with 3+ different seeds
  • Apply extinction_precursor_detector.py to each
  • Verify: inflection point consistently precedes extinction by ~100 generations
  • If consistent: Upgrade to "stable pattern"
  • If inconsistent: Investigate variability sources

Timeline: 1-2 weeks (parallel runs)

Success Metric: 
  warning_window = 100 ± 20 generations across 80% of runs


================================================================================
                              CONTACT
================================================================================

Repository: https://github.com/Ectrox-Lab/atlas-hec-v2.1
Documentation: See /docs directory
Issues: Create GitHub issue for questions/bugs

Last Updated: 2026-03-09
Version: 1.0
