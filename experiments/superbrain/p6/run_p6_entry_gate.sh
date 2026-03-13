#!/bin/bash
# P6 Entry Gate Verification
# ==========================
# Run this script to verify all 4 gates before starting 24h/72h experiments

set -e  # Exit on first failure

echo "P6 Entry Gate Verification"
echo "=========================="
echo ""

FAILED=0

# Gate 1: P5b reproducible
echo -n "Gate 1: P5b artifacts (25 tests)... "
cd ../p5b
if python3 -m pytest test_p5b_core_protection.py test_p5b_core_protection_extended.py test_p5b_week2_minimal_loop.py --tb=no -q > /dev/null 2>&1; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    FAILED=1
fi

# Gate 2: 1h smoke test
echo -n "Gate 2: 1h smoke test (13 tests)... "
cd ../p6
if python3 -m pytest test_p6_runner.py::test_gate2_1h_smoke_explicit --tb=no -q > /dev/null 2>&1; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    FAILED=1
fi

# Gate 3: Stop conditions
echo -n "Gate 3: Stop conditions (10 tests)... "
if python3 -m pytest test_p6_stop_conditions.py --tb=no -q > /dev/null 2>&1; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    FAILED=1
fi

# Gate 4: Critical logging
echo -n "Gate 4: Critical logging (10 tests)... "
if python3 -m pytest test_p6_logging.py --tb=no -q > /dev/null 2>&1; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    FAILED=1
fi

echo ""
echo "=========================="

if [ $FAILED -eq 0 ]; then
    echo "✅ P6 ENTRY GATE: ALL PASSED"
    echo "Ready for 24h smoke test"
    echo "=========================="
    exit 0
else
    echo "❌ P6 ENTRY GATE: SOME FAILED"
    echo "Fix failures before proceeding"
    echo "=========================="
    exit 1
fi
