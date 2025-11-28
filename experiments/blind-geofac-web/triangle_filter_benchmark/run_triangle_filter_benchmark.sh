#!/usr/bin/env bash
# Triangle Filter Benchmark Script
# Compares 127-bit challenge factorization with triangle filter enabled vs disabled.
#
# Reference: https://github.com/zfifteen/geofac/pull/171
#
# Usage: ./run_triangle_filter_benchmark.sh [num_runs]
#   num_runs: Number of runs per configuration (default: 3)
#
# Output:
#   - Logs for each run in triangle_filter_benchmark/results/
#   - Summary stats printed to stdout

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$WEB_ROOT/../.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"

NUM_RUNS="${1:-3}"

mkdir -p "$RESULTS_DIR"

echo "=== Triangle Filter Benchmark ==="
echo "Reference: https://github.com/zfifteen/geofac/pull/171"
echo "Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Runs per configuration: $NUM_RUNS"
echo "Results directory: $RESULTS_DIR"
echo ""

# Function to run a single benchmark
run_benchmark() {
    local filter_enabled="$1"
    local run_num="$2"
    local label
    
    if [ "$filter_enabled" = "true" ]; then
        label="enabled"
    else
        label="disabled"
    fi
    
    local log_file="$RESULTS_DIR/run_${label}_${run_num}.log"
    
    echo "  Run $run_num (filter $label)..."
    
    # Capture start time
    local start_time
    start_time=$(date +%s.%N)
    
    # Run the test with triangle filter setting
    # Note: We use the existing test infrastructure with property overrides
    "$REPO_ROOT/gradlew" -p "$WEB_ROOT" test \
        -Dgeofac.runLongChallengeIT=true \
        -Dgeofac.triangle-filter-enabled="$filter_enabled" \
        --tests "com.geofac.blind.service.FactorServiceChallengeIT" \
        --info \
        2>&1 | tee "$log_file" || {
            echo "  FAILED (see $log_file)"
            return 1
        }
    
    local end_time
    end_time=$(date +%s.%N)
    
    # Calculate elapsed time
    local elapsed
    elapsed=$(echo "$end_time - $start_time" | bc)
    
    # Extract triangle filter stats from log
    local checked rejected reject_rate
    checked=$(grep -oP 'triangleFilterChecked=\K[0-9]+' "$log_file" 2>/dev/null || echo "0")
    rejected=$(grep -oP 'triangleFilterRejected=\K[0-9]+' "$log_file" 2>/dev/null || echo "0")
    reject_rate=$(grep -oP 'Triangle filter stats:.*\(\K[0-9.]+(?=%)' "$log_file" 2>/dev/null || echo "N/A")
    
    # Check for success
    local success="false"
    if grep -q "Factorization should succeed" "$log_file" && grep -q "BUILD SUCCESSFUL" "$log_file"; then
        success="true"
    fi
    
    # Extract duration from test output if available
    local duration_ms
    duration_ms=$(grep -oP 'durationMs=\K[0-9]+' "$log_file" 2>/dev/null || echo "N/A")
    
    echo "    Wall-clock: ${elapsed}s | Duration: ${duration_ms}ms | Success: $success"
    echo "    Triangle filter: checked=$checked, rejected=$rejected, rate=${reject_rate}%"
    
    # Append to summary CSV
    echo "$label,$run_num,$elapsed,$duration_ms,$success,$checked,$rejected,$reject_rate" >> "$RESULTS_DIR/summary.csv"
}

# Initialize summary CSV
echo "mode,run,wall_clock_s,duration_ms,success,checked,rejected,reject_rate_pct" > "$RESULTS_DIR/summary.csv"

echo ""
echo "--- Baseline (Filter Disabled) ---"
for i in $(seq 1 "$NUM_RUNS"); do
    run_benchmark "false" "$i"
done

echo ""
echo "--- Test (Filter Enabled) ---"
for i in $(seq 1 "$NUM_RUNS"); do
    run_benchmark "true" "$i"
done

echo ""
echo "=== Benchmark Complete ==="
echo "Results saved to: $RESULTS_DIR/summary.csv"
echo ""
echo "Summary:"
cat "$RESULTS_DIR/summary.csv"
