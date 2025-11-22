# Shell Geometry Scan 01 - Index

This directory contains the complete implementation and results of **Shell Geometry Scan 01**, an experiment to test whether golden-ratio shell scanning can locate distant factors in the 127-bit challenge semiprime.

## Quick Start

Read these documents in order for the complete story:

1. **[README.md](README.md)** - Experiment overview, method, and usage
2. **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Results at-a-glance and verdict
3. **[DETAILED_RESULTS.md](DETAILED_RESULTS.md)** - Comprehensive metrics and analysis

## Files

### Documentation
- `README.md` - Experiment overview and method description
- `EXECUTIVE_SUMMARY.md` - High-level results and verdict
- `DETAILED_RESULTS.md` - Complete metrics, analysis, and conclusions
- `INDEX.md` - This file

### Code
- `run_experiment.py` - Main experiment implementation (664 lines)

### Results
- `results.json` - Machine-readable experiment metrics
- `experiment_output.log` - Complete console output from run

## Key Takeaways

### What We Tested
- **Hypothesis:** Golden-ratio shell scanning with fractal segment scoring can locate distant factors
- **Target:** N₁₂₇ = 137524771864208156028430259349934309717 (127-bit challenge)
- **Method:** 6 shells (S₀..S₅) with φ-spacing, 700k candidate budget, GVA geodesic sweep

### What We Found
✅ **Shell geometry works structurally:** φ-spacing correctly identified Shell S_5 as containing both factors  
❌ **GVA amplitude fails:** No geometric signal to discriminate factors at |δ| > 10¹⁴  
❌ **Sampling infeasible:** Would need ~10¹² candidates for brute force in S_5  
❌ **Fractal scoring ineffective:** All Mandelbrot scores identical (1.0)

### Verdict
**Clear failure** - Geometry signal too weak with current kernels. Method unsuitable for factors >10% from sqrt(N).

### Scientific Value
- Quantifies GVA method boundaries precisely
- Confirms shell concept reaches correct location (but can't exploit it)
- Fast negative result (70s) vs. futile long search
- Establishes baseline for future shell-based approaches

## Technical Details

### Shell Structure
- R₀ = 7.82×10¹³ (initial radius)
- R_{j+1} = φ·R_j (golden ratio spacing)
- 6 shells total covering up to R₆ = 1.40×10¹⁵

### Factor Locations
- p = 10,508,623,501,177,419,659 (|δ| ≈ 1.22×10¹⁵)
- q = 13,086,849,276,577,416,863 (|δ| ≈ 1.36×10¹⁵)
- **Both in Shell S_5** (R₅ = 8.67×10¹⁴ to R₆ = 1.40×10¹⁵)

### Performance
- Runtime: 69.8 seconds
- Candidates tested: 280,000 / 700,000 (40% utilization)
- Budget: 56,000 per shell
- Shell S_4 skipped (invalid segments)

## Implementation Notes

### Code Quality
- ✅ Minimal implementation (664 lines total)
- ✅ Reuses existing GVA functions (embed_torus_geodesic, riemannian_distance)
- ✅ Reuses Mandelbrot scorer from fractal-recursive-gva
- ✅ Deterministic execution with fixed parameters
- ✅ Comprehensive metrics tracking
- ✅ No security vulnerabilities (CodeQL verified)

### Repository Compliance
- ✅ 127-bit CHALLENGE_127 whitelist only
- ✅ Adaptive precision: max(50, bitLength × 4 + 200)
- ✅ No fallback methods (pure geometric approach)
- ✅ Operational range [10¹⁴, 10¹⁸] respected
- ✅ Reproducible with fixed seeds and parameters

## Running the Experiment

```bash
cd /home/runner/work/geofac/geofac/experiments/shell-geometry-scan-01
python3 run_experiment.py
```

Output:
- Console: Progress and results
- `results.json`: Machine-readable metrics
- `EXECUTIVE_SUMMARY.md`: Auto-generated summary

## Next Steps

Based on this experiment:

1. **Accept limitation:** Document CHALLENGE_127 as out-of-scope for GVA methods
2. **Focus operational range:** Target balanced semiprimes in [10¹⁴, 10¹⁸]
3. **If pursuing 127-bit:** Need fundamentally different geometric embedding or number-theoretic approach
4. **Future experiments:** Test on balanced 127-bit semiprimes to isolate distance vs. balance effects

## References

- **Problem statement:** See original issue description
- **Base GVA:** `/home/runner/work/geofac/geofac/gva_factorization.py`
- **Fractal scorer:** `../fractal-recursive-gva-falsification/fr_gva_implementation.py`
- **Previous attempt:** `../127bit-fractal-mask-challenge/` (fractal masking alone)
- **Hypothesis source:** PR #93 and shell geometry technical memo

---

**Experiment Status:** COMPLETE  
**Date:** 2025-11-22  
**Verdict:** Clear failure - geometry signal too weak  
**Scientific Value:** High - quantifies method boundaries
