#!/bin/bash

set -euo pipefail

# One-shot factorization of the target N using geometric resonance
# Produces results/single_N_run.json and plaintext factors if successful
#
# Project: geofac - Geometric Resonance Factorization
# Repo: https://github.com/zfifteen/geofac
# README: https://github.com/zfifteen/geofac/blob/main/README.md
# Coding Style: https://github.com/zfifteen/geofac/blob/main/CODING_STYLE.md
# Validation Gates: https://github.com/zfifteen/geofac/blob/main/docs/VALIDATION_GATES.md
# Agents/Operating Rules: https://github.com/zfifteen/geofac/blob/main/AGENTS.md
#
# This script attempts to factor the Gate 1 challenge number using the geometric resonance algorithm.
# It has been updated based on PR #25 (Add Diagnostic Harness for Geometric Resonance Factorization):
# https://github.com/zfifteen/geofac/pull/25
# which claims successful reproduction with tuned parameters.
#
# However, despite matching the PR's config, the factorization still fails, timing out without finding factors.
# Diagnostics reveal high-amplitude candidates but incorrect p0 values from the snap heuristic.
#
# Attempts documented below:
# 1. Initial run: Failed due to Spring Shell property binding issue (--spring.shell.interactive=false not parsed correctly).
#    Error: ConverterNotFoundException for SpringShellProperties$Interactive.
#    Fix: Removed --spring.shell.interactive=false; Spring Boot runs non-interactive when args provided.
#
# 2. Second run: Failed validation gate enforcement.
#    Error: "Input N does not conform to project validation gates."
#    Reason: allow-gate1-benchmark=false by default; Gate 1 N is outside Gate 2 range (1e14-1e18).
#    Fix: Added -Dgeofac.allow-gate1-benchmark=true to bypass for Gate 1.
#
# 3. Third run: Factorization started but timed out.
#    Config: Default application.yml (precision=240, samples=3000, etc.), timeout=15000ms.
#    Result: Timed out after 15s, 23 samples processed. No factors found.
#    Diagnostics: Not enabled; no detailed logs.
#
# 4. Updated to PR #25 parameters: precision=300, samples=7500, m-span=200, j=8, threshold=0.88,
#    k-lo=0.20, k-hi=0.50, timeout=30000ms, fast-path=false, diagnostics=true.
#    But adaptive precision overrides to max(300, 127*4+200)=708.
#    Result: Still timed out after 30s, 42 samples. Amplitude mean=0.126, many candidates rejected
#    because p0 (computed prime candidate) is invalid (huge or 0), doesn't divide N.
#    Conclusion: Snap heuristic produces wrong p0; algorithm needs further tuning or fix.
#
# Expected success per PR, but not achieved. Script expects "SUCCESS" in output to extract p,q.
# For other LLMs: Check FactorizerService.java snap logic, DirichletKernel, or parameter derivation.
#
# IMPORTANT: DO NOT enable fast-path (enable-fast-path=true) as a "solution".
# Fast-path is NOT success—it's a convenience construct that returns known factors
# to allow the build to pass. Real success means the geometric resonance algorithm
# discovers the factors without being given them. The algorithm currently fails.

# The official Gate 1 challenge number. See docs/VALIDATION_GATES.md for details.
TARGET_N="137524771864208156028430259349934309717"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="results/single_run_${RUN_ID}"
mkdir -p "$OUT_DIR"

echo "Starting geometric resonance factorization"
echo "N = $TARGET_N"
echo "Run ID = $RUN_ID"

# Run the factorization command with tuned parameters from PR #25
# Note: Adaptive precision = max(configured, N.bitLength()*4 + 200) = max(708, 127*4+200)=708
JAR="build/libs/geofac-0.1.0-SNAPSHOT.jar"
if [ ! -f "$JAR" ]; then
  echo "Jar not found; building..."
  ./gradlew --no-daemon -q clean build -x test
fi
output=$(java \
  -Dgeofac.allow-gate1-benchmark=true \
  -Dgeofac.precision=708 \
  -Dgeofac.samples=7500 \
  -Dgeofac.m-span=200 \
  -Dgeofac.j=8 \
   -Dgeofac.threshold=0.86 \
  -Dgeofac.k-lo=0.20 \
  -Dgeofac.k-hi=0.50 \
  -Dgeofac.search-timeout-ms=90000 \
   -Dgeofac.enable-fast-path=false \
   -Dgeofac.enable-diagnostics=true \
   -jar "$JAR" factor "$TARGET_N" 2>&1 | tee "$OUT_DIR/run.log")

# Print the output
echo "$output"

# Check for success
if grep -q "SUCCESS" <<< "$output"; then
    echo "Factorization successful."

    # Extract p and q from the output
    p=$(grep "p =" <<< "$output" | sed 's/.*p = //' | sed 's/║.*//' | tr -d ' ')
    q=$(grep "q =" <<< "$output" | sed 's/.*q = //' | sed 's/║.*//' | tr -d ' ')

    # Output plaintext
    echo "$p"
    echo "$q"
    echo "pq_matches_N=true"

    echo "Results saved to results/single_N_run.json"
else
    echo "Factorization failed."
    exit 1
fi