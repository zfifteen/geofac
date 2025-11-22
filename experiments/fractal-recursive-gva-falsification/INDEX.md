# Fractal-Recursive GVA Falsification Experiment

## Quick Navigation

**Start here:** [EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md) - Complete findings and verdict

Supporting documents:
- [README.md](README.md) - Experiment design, methodology, and test corpus
- [THEORETICAL_ANALYSIS.md](THEORETICAL_ANALYSIS.md) - Mathematical critique of the hypothesis

Code artifacts:
- [fr_gva_implementation.py](fr_gva_implementation.py) - FR-GVA implementation following hypothesis specifications
- [comparison_experiment.py](comparison_experiment.py) - Rigorous comparison framework and test suite

## TL;DR

**Hypothesis:** Fractal-Recursive GVA improves factorization via Mandelbrot-style iterations and recursive subdivision

**Method:** Compare FR-GVA vs. standard GVA on 6 balanced semiprimes in [10^14, 10^18]

**Result:** ❌ **HYPOTHESIS FALSIFIED**

**Key Finding:** FR-GVA succeeds only via trial division fallback, not fractal mechanism. Fractal candidates never find factors.

**Verdict:** The proposed fractal-recursive approach does not work as claimed. Success is due to classical trial division, not geometric fractal properties.

---

## Executive Summary (from EXPERIMENT_SUMMARY.md)

The Fractal-Recursive GVA (FR-GVA) hypothesis claimed to improve factorization through:
1. Mandelbrot-inspired fractal iterations for candidate generation
2. Recursive window subdivision based on geodesic density
3. Expected 15-20% density boosts and 30% reduction in candidates

**Critical finding:** Analysis of execution traces reveals that all successful factorizations occur via the trial division fallback at maximum recursion depth. The fractal candidate generation mechanism produces thousands of candidates, but **zero of these candidates yield factors**.

The apparent 88x average speedup of FR-GVA over standard GVA is an artifact: FR-GVA uses cheap trial division while GVA uses expensive geodesic distance calculations. This is not evidence that the fractal-recursive mechanism works - it's evidence that trial division is faster than geometric methods on small numbers.

**Comparison results:**
- Standard GVA: 50% success rate (3/6 test cases)
- FR-GVA: 100% success rate (6/6 test cases) via trial division only
- Average speedup: 88.26x (irrelevant - different algorithms)

**Theoretical objections:**
1. No mathematical bridge between Mandelbrot escape times and factorization
2. κ(n) computation requires knowing divisors (equivalent to factoring)
3. Recursive subdivision is just divide-and-conquer trial division
4. Fractal candidates are pseudo-randomly distributed with no geometric significance

**Conclusion:** The hypothesis is decisively falsified. The fractal mechanism does not work. All success is due to classical methods the hypothesis claimed to avoid.

---

## Reproducibility

To reproduce the experiment:

```bash
cd /home/runner/work/geofac/geofac

# Run full comparison experiment (6 test cases, ~3 minutes)
python3 experiments/fractal-recursive-gva-falsification/comparison_experiment.py

# Test FR-GVA implementation only with verbose output
python3 experiments/fractal-recursive-gva-falsification/fr_gva_implementation.py
```

All test cases are deterministic balanced semiprimes with known factors. Results are fully reproducible.

---

## Files

| File | Purpose |
|------|---------|
| INDEX.md (this file) | Navigation and TL;DR |
| EXPERIMENT_SUMMARY.md | Complete findings, analysis, and verdict |
| README.md | Experiment design and methodology |
| THEORETICAL_ANALYSIS.md | Mathematical critique of hypothesis |
| fr_gva_implementation.py | FR-GVA implementation (hypothesis specification) |
| comparison_experiment.py | Test suite and comparison framework |

---

Read [EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md) for complete details.
