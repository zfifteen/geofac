# Resonance Drift Hypothesis Experiment

## Quick Navigation

Start here: **[EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md)** - Complete findings and verdict

Supporting documents:
- **[README.md](README.md)** - Experiment design, methodology, and barriers
- **[THEORETICAL_ANALYSIS.md](THEORETICAL_ANALYSIS.md)** - Mathematical analysis and falsification criteria

Code artifacts:
- **[ResonanceDriftExperiment.java](../../src/test/java/com/geofac/experiments/ResonanceDriftExperiment.java)** - Data collection framework
- **[regression_analysis.py](regression_analysis.py)** - Statistical analysis script

Data files:
- **[data_collection.log](data_collection.log)** - Placeholder for empirical data (empty - collection infeasible)
- **plots/** - Directory for visualizations (empty - no data to plot)

## TL;DR

**Hypothesis**: Optimal k scales with ln(N), not constant across scales

**Attempted**: Collect k-success data → regression analysis → predict 127-bit k

**Result**: UNTESTABLE - no empirical data, computational barriers, validation gate restrictions

**Deliverable**: Complete experimental framework + theoretical analysis documenting why hypothesis cannot be falsified

**Recommendation**: Acknowledge static k ∈ [0.25, 0.45] as unvalidated assumption

---

Read [EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md) for complete details.
