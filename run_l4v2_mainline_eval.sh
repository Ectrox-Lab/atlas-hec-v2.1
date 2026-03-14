#!/bin/bash
#
# L4-v2 Mainline Evaluation Runner
# Dedicated evaluation script - no dependency on Octopus/Bio-World frameworks
#

set -e

WORKSPACE="/tmp/atlas_l4v2"
RESULTS="/tmp/atlas_l4v2_results"
SAMPLE_SIZE=30

echo "======================================================================"
echo "L4-v2 MAINLINE EVALUATION"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Workspace: $WORKSPACE"
echo "Results: $RESULTS"
echo "Sample size: $SAMPLE_SIZE per round"
echo ""

# Check if candidates exist
if [ ! -d "$WORKSPACE/round_a/candidates" ]; then
    echo "❌ Error: Candidates not found in $WORKSPACE"
    echo "   Run ./run_l4v2_experiment.sh first"
    exit 1
fi

# Count candidates
echo "Candidate counts:"
echo "  Round A: $(ls $WORKSPACE/round_a/candidates/*.json 2>/dev/null | wc -l)"
echo "  Round B: $(ls $WORKSPACE/round_b/candidates/*.json 2>/dev/null | wc -l)"
echo "  Ablation: $(ls $WORKSPACE/round_ablation/candidates/*.json 2>/dev/null | wc -l)"
echo ""

# Run evaluation
echo "======================================================================"
echo "RUNNING TASK-1 EVALUATION"
echo "======================================================================"

python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/task1_l4v2_evaluate.py \
    --input-dir "$WORKSPACE" \
    --output-dir "$RESULTS" \
    --sample-size $SAMPLE_SIZE

echo ""
echo "======================================================================"
echo "EVALUATION COMPLETE"
echo "======================================================================"
echo ""
echo "Output files:"
echo "  📊 $RESULTS/mainline_effectiveness_summary.json"
echo "  📊 $RESULTS/mainline_compositionality_summary.json"
echo "  📄 $RESULTS/mainline_phase2_report.md"
echo "  📋 $RESULTS/mainline_detailed_results.json"
echo ""
echo "Quick view:"
echo ""
cat "$RESULTS/mainline_phase2_report.md" | head -50
echo ""
echo "======================================================================"
echo "View full report: cat $RESULTS/mainline_phase2_report.md"
echo "======================================================================"
