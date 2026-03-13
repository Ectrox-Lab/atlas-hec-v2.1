#!/usr/bin/env bash
#
# Octopus Mainline Autoloop
# 一键执行主线研究循环
#

set -e

echo "=========================================="
echo "SOCS Octopus Mainline Autoloop"
echo "=========================================="
echo ""

# 记录开始时间
START_TIME=$(date +%s)
STATE_FILE="state/last_run.json"
mkdir -p state

# Step 1: 跑 OctopusLike Smoke
echo "[Step 1/6] Running OctopusLike Smoke Test..."
python socs_autoresearch_operator/tasks/smoke_scheduler.py \
  --config socs_autoresearch_operator/configs/octopus_smoke.yaml \
  2>&1 | tee state/smoke_output.log

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "❌ Smoke test failed"
    echo '{"step": 1, "status": "FAILED", "timestamp": "'$(date -Iseconds)'"}' > "$STATE_FILE"
    exit 1
fi
echo "✅ Smoke test completed"
echo ""

# Step 2: 跑 OQS Gate 1.5
echo "[Step 2/6] Running OQS Gate 1.5..."
python socs_autoresearch_operator/tasks/gate_operator.py \
  --config socs_autoresearch_operator/configs/oqs_gate15.yaml \
  2>&1 | tee state/oqs_output.log

GATE_EXIT=${PIPESTATUS[0]}
if [ $GATE_EXIT -eq 2 ]; then
    echo "⚠️ OQS Gate 1.5 FAILED"
elif [ $GATE_EXIT -eq 1 ]; then
    echo "⚠️ OQS Gate 1.5 PARTIAL"
else
    echo "✅ OQS Gate 1.5 PASSED"
fi
echo ""

# Step 3: 聚合结果
echo "[Step 3/6] Aggregating results..."
python socs_autoresearch_operator/tasks/result_aggregator.py \
  --input results/raw/ \
  --output results/aggregated/ \
  2>&1 | tee state/aggregate_output.log || echo "⚠️ Aggregation had warnings"
echo "✅ Results aggregated"
echo ""

# Step 4: 做 triage
echo "[Step 4/6] Running result triage..."
python socs_autoresearch_operator/tasks/result_triage.py \
  --results results/aggregated/octopus_smoke_latest.json results/aggregated/oqs_gate15_latest.json \
  --thresholds socs_autoresearch_operator/configs/thresholds.yaml \
  2>&1 | tee state/triage_output.log

echo "✅ Triage completed"
echo ""

# Step 5: 写报告
echo "[Step 5/6] Writing mainline reports..."
python socs_autoresearch_operator/tasks/notebook_writer.py \
  --type smoke \
  --output reports/octopus_smoke_report.md

python socs_autoresearch_operator/tasks/notebook_writer.py \
  --type oqs \
  --output reports/oqs_gate15_report.md

python socs_autoresearch_operator/tasks/notebook_writer.py \
  --type mainline \
  --output reports/mainline_status.md

echo "✅ Reports generated"
echo ""

# Step 6: 检查停机条件
echo "[Step 6/6] Checking halt conditions..."
python socs_autoresearch_operator/tasks/halt_checker.py \
  --state state/ \
  --thresholds socs_autoresearch_operator/configs/thresholds.yaml \
  2>&1 | tee state/halt_check.log

HALT_EXIT=${PIPESTATUS[0]}
if [ $HALT_EXIT -ne 0 ]; then
    echo "🛑 HALT CONDITION TRIGGERED"
    echo "   See: state/halt_check.log"
    echo "   Manual review required."
    exit $HALT_EXIT
fi

echo "✅ No halt conditions triggered"
echo ""

# 记录完成
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

cat > "$STATE_FILE" << STATE_EOF
{
  "cycle": "$(date +%Y%m%d_%H%M%S)",
  "timestamp": "$(date -Iseconds)",
  "duration_seconds": $DURATION,
  "status": "COMPLETED",
  "outputs": {
    "smoke_report": "reports/octopus_smoke_report.md",
    "oqs_report": "reports/oqs_gate15_report.md",
    "mainline_status": "reports/mainline_status.md",
    "proposals": "proposals/pending/"
  }
}
STATE_EOF

echo "=========================================="
echo "✅ Mainline cycle completed in ${DURATION}s"
echo "=========================================="
echo ""
echo "Outputs:"
echo "  - Smoke Report: reports/octopus_smoke_report.md"
echo "  - OQS Report:   reports/oqs_gate15_report.md"
echo "  - Mainline:     reports/mainline_status.md"
echo "  - Proposals:    proposals/pending/"
echo ""
echo "Next: Review proposals and approve/reject/modify"
