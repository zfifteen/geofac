# Triangle Filter Benchmark Results

## Reference

- **Triangle Filter Implementation**: [PR #171](https://github.com/zfifteen/geofac/pull/171)
- **Benchmark Location**: `experiments/blind-geofac-web/triangle_filter_benchmark/`

## Configuration

The triangle filter was tested with these settings (from PR #171):

| Parameter | Value | Description |
|-----------|-------|-------------|
| `triangle-filter-enabled` | `true` / `false` | Toggle for the benchmark |
| `triangle-filter-balance-band` | `4.0` | p must be in [√N/4, √N×4] |
| `triangle-filter-max-log-skew` | `0.0` | Skew check disabled (band-only mode) |

## Benchmark Protocol

- **Target**: 127-bit challenge factorization (`N = 137524771864208156028430259349934309717`)
- **Test**: `FactorServiceChallengeIT.factorsChallengeWithFullBudget()`
- **Runs per configuration**: 3 (configurable)
- **Metrics captured**:
  - Wall-clock runtime (seconds)
  - Factorization duration (milliseconds, from test output)
  - Triangle filter statistics (checked, rejected, rejection rate %)
  - Factorization success/failure

## How to Run

### Quick Smoke Test

For a quick validation with a smaller Gate-4 composite (~47 bits):

```bash
cd experiments/blind-geofac-web/triangle_filter_benchmark
./run_smoke_test.sh
```

### Full Benchmark (127-bit Challenge)

For full evaluation with the 127-bit RSA challenge:

```bash
cd experiments/blind-geofac-web/triangle_filter_benchmark
./run_triangle_filter_benchmark.sh [num_runs]
```

Results are saved to:
- `results/summary.csv` — tabular summary
- `results/run_*.log` — full test logs for each run

## Results

> **Note**: Results below are placeholders. Run `./run_triangle_filter_benchmark.sh` to generate actual data for your environment.

### Filter Disabled (Baseline)

| Run | Wall-clock (s) | Duration (ms) | Success |
|-----|----------------|---------------|---------|
| 1   | —              | —             | —       |
| 2   | —              | —             | —       |
| 3   | —              | —             | —       |

**Mean runtime**: —  
**Std dev**: —

### Filter Enabled (Band-Only)

| Run | Wall-clock (s) | Duration (ms) | Checked | Rejected | Reject % | Success |
|-----|----------------|---------------|---------|----------|----------|---------|
| 1   | —              | —             | —       | —        | —        | —       |
| 2   | —              | —             | —       | —        | —        | —       |
| 3   | —              | —             | —       | —        | —        | —       |

**Mean runtime**: —  
**Std dev**: —  
**Mean rejection rate**: —

## Smoke Test Results (47-bit Gate-4 Composite)

Quick validation with `N = 100000980001501` (47 bits):

| Filter Mode | Wall-clock (s) | Checked | Rejected | Reject % | Success |
|-------------|----------------|---------|----------|----------|---------|
| Disabled    | ~7             | 0       | 0        | N/A      | ✓       |
| Enabled     | ~7             | 4       | 0        | 0.0%     | ✓       |

**Observation**: On this balanced Gate-4 semiprime, the triangle filter correctly accepts all valid candidates (no rejections). The true factors (10000019 × 10000079) are well within the balance band.

## Verdict

> To be filled after running the full 127-bit benchmark.

At `balanceBand=4.0` with skew check disabled:

- **Rejection rate**: —% of candidates filtered out
- **Runtime impact**: —% change compared to baseline
- **Failures observed**: —

## Interpretation

The triangle-closure filter is a cheap geometric pre-filter that rejects candidates whose implied q* = N/p would fall outside the valid balance band. For the 127-bit challenge, the true factors are:

- `p = 10508623501177419659`
- `q = 13086849276577416863`

The factor ratio is approximately `q/p ≈ 1.245`, which is well within the `balanceBand=4.0` constraint. Therefore, the filter should never reject the true factors.

## Expected Behavior

The triangle filter operates as a cheap pre-filter that:

1. **Never rejects true factors** — The balance band (4.0) is wide enough to guarantee valid factors pass.
2. **Rejects geometrically impossible candidates** — Candidates too small or too large are pruned.
3. **Has minimal overhead** — Only a few BigDecimal comparisons per candidate.

For well-balanced RSA semiprimes (p ≈ q), expect low rejection rates since the resonance search naturally targets the √N vicinity. Higher rejection rates would be expected for highly unbalanced semiprimes or if the search explores a wider range of candidates.
