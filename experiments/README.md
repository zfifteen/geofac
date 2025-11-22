# Geofac Experiments

This directory contains research experiments for the geofac geometric resonance factorization project.

## Current Experiments

### [fractal-recursive-gva-falsification/](fractal-recursive-gva-falsification/)

**Status**: Complete - Hypothesis decisively falsified

**Objective**: Falsify the hypothesis that Fractal-Recursive GVA (Mandelbrot-inspired iterations + recursive subdivision) improves factorization

**Key Finding**: Hypothesis falsified. FR-GVA succeeds only via trial division fallback, not fractal mechanism. Zero fractal candidates find factors. Apparent 88x speedup is artifact of comparing geometric (GVA) vs. classical (trial division) methods.

**Start here**: [fractal-recursive-gva-falsification/INDEX.md](fractal-recursive-gva-falsification/INDEX.md)

---

### [resonance-drift-hypothesis/](resonance-drift-hypothesis/)

**Status**: Complete - Framework ready, hypothesis untestable

**Objective**: Test whether optimal resonance parameter k scales with N or remains constant

**Key Finding**: Cannot be falsified due to lack of empirical k-success data. Current k ∈ [0.25, 0.45] is an unvalidated assumption.

**Start here**: [resonance-drift-hypothesis/INDEX.md](resonance-drift-hypothesis/INDEX.md)

---

### [deeper-recursion-hypothesis/](deeper-recursion-hypothesis/)

**Status**: Complete - Hypothesis decisively falsified

**Objective**: Test whether 3-stage recursion with dynamic thresholds can reduce runtime below baseline on 110-bit semiprimes while maintaining factor recovery

**Key Finding**: Hypothesis falsified. 3-stage achieved 1.19× speedup (3.40s vs 4.07s) but failed to recover factors. Multi-stage uniform segmentation is fundamentally incompatible with ultra-localized geodesic signals - adaptive sampling near √N is a necessity, not an optimization.

**Start here**: [deeper-recursion-hypothesis/INDEX.md](deeper-recursion-hypothesis/INDEX.md)

---

### [weyl-law-remainder-oscillations/](weyl-law-remainder-oscillations/)

**Status**: (Pre-existing experiment)

---

## Experiment Guidelines

Each experiment should include:
1. **INDEX.md** - Navigation guide and TL;DR
2. **EXPERIMENT_SUMMARY.md** - Complete findings and verdict
3. **README.md** - Design, methodology, and setup
4. **Code artifacts** - Implementation (Java/Python/etc.)
5. **Data files** - Results, logs, or placeholders if infeasible
6. **Theoretical analysis** - When empirical validation is blocked

## Adding New Experiments

```bash
mkdir experiments/your-experiment-name
cd experiments/your-experiment-name
# Create INDEX.md, README.md, etc.
```

Follow the structure established by `resonance-drift-hypothesis/` for consistency.
