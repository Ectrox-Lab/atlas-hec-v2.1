#!/bin/bash
#
# E-COMP-003 Gate-1: Mainline Evaluation
# Evaluate 30 candidates per round with detailed logging
#

set -e

WORKSPACE="/tmp/ecomp003_gate1"
RESULTS="/tmp/ecomp003_gate1_results"
SAMPLE_SIZE=30

echo "======================================================================"
echo "E-COMP-003 GATE-1: Mainline Evaluation"
echo "======================================================================"
echo "Timestamp: $(date -Iseconds)"
echo "Sample size: $SAMPLE_SIZE per round (stratified)"
echo "Results: $RESULTS"
echo ""

# Check if candidates exist
if [ ! -d "$WORKSPACE/round_a_v3/candidates" ]; then
    echo "❌ Error: Candidates not found in $WORKSPACE"
    echo "   Run ./run_ecomp003_gate1.sh first"
    exit 1
fi

# Run evaluation
echo "======================================================================"
echo "RUNNING TASK-1 EVALUATION"
echo "======================================================================"

python3 /home/admin/atlas-hec-v2.1-repo/superbrain/fast_genesis/task1_l4v2_evaluate.py \
    --input-dir "$WORKSPACE" \
    --output-dir "$RESULTS" \
    --sample-size $SAMPLE_SIZE \
    --baseline 0.075

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

# Count winners
echo "Winner counts:"
echo "  Total approved: $(cat $RESULTS/mainline_detailed_results.json | jq '[.candidates[] | select(.approved == true)] | length')"
echo ""

echo "Next: Run mechanism extraction"
echo "  python3 superbrain/module_routing/mechanism_extractor.py \\"
echo "    --l4v2-results $RESULTS \\"
echo "    --output-dir docs/research/E-COMP-003/gate1"
