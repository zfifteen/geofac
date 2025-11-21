# Geofac Experiments

This directory contains research experiments for the geofac geometric resonance factorization project.

## Current Experiments

### [resonance-drift-hypothesis/](resonance-drift-hypothesis/)

**Status**: Complete - Framework ready, hypothesis untestable

**Objective**: Test whether optimal resonance parameter k scales with N or remains constant

**Key Finding**: Cannot be falsified due to lack of empirical k-success data. Current k ∈ [0.25, 0.45] is an unvalidated assumption.

**Start here**: [resonance-drift-hypothesis/INDEX.md](resonance-drift-hypothesis/INDEX.md)

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
