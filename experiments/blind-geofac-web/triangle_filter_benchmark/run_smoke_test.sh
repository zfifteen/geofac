#!/usr/bin/env bash
# Quick Triangle Filter Smoke Test
# Runs a single factorization with filter enabled vs disabled for comparison.
# Use this for quick validation; use run_triangle_filter_benchmark.sh for full benchmark.
#
# Reference: https://github.com/zfifteen/geofac/pull/171

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$WEB_ROOT/../.." && pwd)"

echo "=== Triangle Filter Smoke Test ==="
echo "Reference: https://github.com/zfifteen/geofac/pull/171"
echo ""

run_quick_test() {
    local filter_enabled="$1"
    local label
    
    if [ "$filter_enabled" = "true" ]; then
        label="ENABLED"
    else
        label="DISABLED"
    fi
    
    echo "Running with triangle filter $label..."
    
    local start_time
    start_time=$(date +%s)
    
    # Run quick test (not the long challenge)
    "$REPO_ROOT/gradlew" -p "$WEB_ROOT" test \
        -Dgeofac.triangle-filter-enabled="$filter_enabled" \
        --tests "com.geofac.blind.service.FactorServiceTest" \
        2>&1 | tee /tmp/smoke_test_${filter_enabled}.log
    
    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    
    # Extract stats
    local checked rejected rate
    checked=$(grep -oP 'triangleFilterChecked=\K[0-9]+' /tmp/smoke_test_${filter_enabled}.log 2>/dev/null | tail -1 || echo "0")
    rejected=$(grep -oP 'triangleFilterRejected=\K[0-9]+' /tmp/smoke_test_${filter_enabled}.log 2>/dev/null | tail -1 || echo "0")
    rate=$(grep -oP 'Triangle filter stats:.*\(\K[0-9.]+(?=%)' /tmp/smoke_test_${filter_enabled}.log 2>/dev/null | tail -1 || echo "N/A")
    
    echo ""
    echo "Filter $label:"
    echo "  Wall-clock: ${elapsed}s"
    echo "  Triangle filter: checked=$checked, rejected=$rejected, rate=${rate}%"
    echo ""
}

echo "--- Baseline (Filter Disabled) ---"
run_quick_test "false"

echo "--- Test (Filter Enabled) ---"
run_quick_test "true"

echo "=== Smoke Test Complete ==="
