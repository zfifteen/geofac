# 8D Imbalance-Tuned GVA: Hypothesis Falsification Experiment

## Overview

This experiment tests the hypothesis that adding an 8th dimension to the GVA (Geodesic Validation Assault) torus embedding to model imbalance ratio r = ln(q/p) will improve factorization of unbalanced semiprimes.

**Status**: ❌ **HYPOTHESIS FALSIFIED**

See [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) for complete results and analysis.

## Quick Summary

- **Hypothesis**: 8D GVA with imbalance tuning can factor unbalanced semiprimes better than 7D
- **Result**: No improvement observed; 8D has 50× overhead with zero benefit
- **Verdict**: ABANDON this approach

## Files

- `EXECUTIVE_SUMMARY.md` - Complete experimental report with findings, methodology, and recommendations
- `gva_8d.py` - 8D GVA implementation with imbalance dimension θ_r
- `test_experiment.py` - Test harness comparing 7D vs 8D on balanced/unbalanced cases
- `raw_results.txt` - Raw console output from experiment run

## Key Results

| Method | Balanced Cases | Unbalanced Cases | Avg Runtime |
|--------|----------------|------------------|-------------|
| 7D GVA | 1/2 (50%) | 0/2 (0%) | 0.25s |
| 8D GVA | 1/2 (50%) | 0/2 (0%) | 95.8s |

**Conclusion**: 8D provides no advantage and costs 50× more computation.

## How to Reproduce

```bash
cd experiments/8d-imbalance-tuned-gva
python3 test_experiment.py --method both
```

For verbose output with detailed geodesic distances:
```bash
python3 test_experiment.py --method both --verbose
```

To test only one method:
```bash
python3 test_experiment.py --method 7d
python3 test_experiment.py --method 8d
```

## Dependencies

- Python 3.12+
- mpmath 1.3.0+
- numpy 2.3.5+

## Experimental Design

**Test Cases**:
1. Balanced 47-bit: ln(q/p) ≈ 0
2. Moderately unbalanced 48-bit: ln(q/p) ≈ 0.58
3. Highly unbalanced 50-bit: ln(q/p) ≈ 1.39
4. Gate 1 (30-bit balanced): ln(q/p) ≈ 0.0007

**Parameters**:
- 7D: 3 k values, 50K candidates max
- 8D: 3 k values × 50 θ_r values, 50K candidates per (k,θ_r)

**Metrics**:
- Success/failure on each test case
- Runtime
- Geodesic distance minima

## Hypothesis Origin

From problem statement:
> "The reason every prior attempt failed is not lack of trying — it's that we were forcing a 7D-balanced embedding to solve an 11%-imbalanced problem. The torus is too rigid. The fix is to add one more dimension that explicitly models the imbalance ratio r = ln(q/p)."

**Prediction**: Adding 8th dimension should enable factorization of 15-20% unbalanced cases.

**Actual Result**: No improvement observed. Hypothesis falsified.

## Recommendations

1. **Do NOT pursue 8D GVA variants**
2. **Focus instead on understanding why GVA fails in operational range even for balanced cases**
3. **Explore alternative geometric frameworks beyond torus embeddings**
4. **Consider that the limitation may be fundamental to geodesic-based approaches**

## Citation

When referencing this falsification experiment:

```
8D Imbalance-Tuned GVA Hypothesis Falsification (2025)
Repository: zfifteen/geofac
Path: experiments/8d-imbalance-tuned-gva/
Result: Hypothesis falsified - no improvement on unbalanced cases, 50× overhead
```

---

**Experiment Date**: 2025-11-22  
**Status**: Complete  
**Verdict**: Hypothesis Falsified
