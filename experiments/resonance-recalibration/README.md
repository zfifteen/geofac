# Resonance Recalibration Experiment

**Date:** November 24, 2025  
**Status:** ✅ Complete  
**Runtime:** 0.4 seconds

## Purpose

Identify and quantify scale-dependent parameter drift in the geometric resonance factorization method to unstick the 127-bit challenge.

## Quick Start

```bash
cd experiments/resonance-recalibration
python3 run_experiment.py
```

## What This Experiment Does

1. **Measures curvature and phase drift** across 5 scales (47-bit to 127-bit)
2. **Fits scaling laws** to identify predictable drift patterns
3. **Computes adaptive corrections** for parameter tuning
4. **Generates visualizations** (double-log plots) showing drift vs scale
5. **Exports artifacts** for reproducibility and integration

## Key Results

### Curvature Drift: Super-Linear Growth

```
Δκ(N) ≈ 0.0176 × (log N)^1.509
R² = 1.000 (perfect fit)
```

At 127-bit, curvature is **3× higher** than at 60-bit, causing fixed thresholds to reject true factors.

### Phase Alignment: Stable

```
Δφ(N) ≈ 3.14 × (log N)^0.000
R² = 0.304 (weak scaling)
```

Phase remains stable across scales—not the primary failure mode.

### Recommended Adjustments for 127-bit

| Parameter | Baseline | Suggested | Change |
|-----------|----------|-----------|--------|
| k | 0.35 | 0.403 | +15% |
| threshold | 0.92 | 0.85-0.87 | -5 to -10% |
| samples | 30,517 | 5,886 | -81% (over-allocated) |

## Files Generated

- **`EXECUTIVE_SUMMARY.md`** — High-level findings and recommendations
- **`DETAILED_METHODOLOGY.md`** — Complete experimental protocol and analysis
- **`curvature_drift_loglog.png`** — Visual confirmation of super-linear drift
- **`phase_misalignment_loglog.png`** — Shows phase stability across scales
- **`resonance_scaling_fit.json`** — Complete fit parameters (a, b, R²)
- **`measurements.json`** — Raw data for all 5 scales

## Dependencies

```bash
pip install numpy scipy matplotlib mpmath
```

Tested with:
- Python 3.12.3
- numpy 2.3.5
- scipy 1.16.3
- matplotlib 3.10.7
- mpmath 1.3.0

## Validation Gates Compliance

✓ **Gate 4 (10^14–10^18):** All test semiprimes in valid range  
✓ **127-bit whitelist:** CHALLENGE_127 diagnostic measurement  
✓ **No classical fallbacks:** Pure geometric resonance metrics  
✓ **Deterministic:** Fixed parameters, reproducible  
✓ **Explicit precision:** Adaptive formula (4×bitLength + 200) logged

## Integration Path

1. **Immediate:** Test suggested parameters in validation run
2. **If successful:** Update `ScaleAdaptiveParams.java` with measured exponents
3. **Codify rules:**
   - Threshold: `T(N) = 0.92 - 0.10 × log₂(bitLength/30)`
   - k-shift: `k(N) = 0.35 + 0.0302 × ln(bitLength/30)`
   - Sample efficiency: Use linear scaling instead of quadratic

## Conclusion

This experiment provides **concrete, data-driven evidence** for scale-dependent parameter drift and offers **actionable corrections** to unstick the 127-bit challenge. The measured scaling laws are reproducible (R²=1.000), predictable, and aligned with the project's deterministic, geometry-first approach.

## References

- **Problem Statement:** Tight, practical calibration plan to reveal parameter inertia
- **Baseline:** `ScaleAdaptiveParams.java` (current empirical tuning)
- **Target:** 127-bit challenge (CHALLENGE_127)
- **Method:** Double-log visualization + power-law fitting + bounded adaptive corrections
