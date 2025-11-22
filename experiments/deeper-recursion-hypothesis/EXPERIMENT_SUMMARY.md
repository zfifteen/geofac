# Deeper Recursion Hypothesis - Experiment Summary

## Executive Summary

**Hypothesis Tested**: Extending fractal-recursive geodesic search to 3+ stages with dynamic thresholds can reduce runtime below baseline (< 4.027s) on 110+ bit semiprimes while maintaining factor recovery.

**Verdict**: **DECISIVELY FALSIFIED**

**Key Finding**: The 3-stage recursive approach achieved 1.19× speedup (3.40s vs 4.07s) but **failed to recover the factors**. Multi-stage uniform segmentation is fundamentally incompatible with ultra-localized geodesic signals in 110-bit balanced semiprimes.

## Results at a Glance

| Method | Runtime | Speedup | Factors Found | Verdict |
|--------|---------|---------|---------------|---------|
| **Baseline GVA** | 4.065s | 1.00× | ✓ Correct | Reference |
| **2-Stage** (PR #92) | 4.538s | 0.90× | ✗ Failed | Slower + Wrong |
| **3-Stage** (Hypothesis) | 3.402s | **1.19×** | ✗ Failed | **Faster but Wrong** |

**Critical Issue**: 3-stage was faster than baseline but **incorrect** → hypothesis falsified on correctness grounds.

## Why It Failed: The Localization Problem

### The Scale Mismatch

**Search window**: ±180 trillion around √N  
**Factor location**: offset **-38** from √N (within ±100)  
**Segment size (3-stage Stage 1)**: 45 trillion per segment  
**Sample spacing**: ~900 billion between samples

**Probability of detecting factor with uniform sampling**: ~0%

### Adaptive Sampling is Not Optional

**Baseline GVA** succeeds because:
- Step size **1** for ±100 around √N (guaranteed to hit offset -38)
- Progressively sparse sampling farther away
- Found factor at geodesic distance 0.000905 (highly localized signal)

**Multi-stage approaches** fail because:
- Uniform sampling every 225-900 billion positions
- Cannot detect signals localized within ±100 of √N
- Geodesic peaks are too narrow to be captured by coarse grids

### Attempted Fix Would Defeat Purpose

To make multi-stage work, Stage 1 would need:
- Segments < 1 billion near √N (to capture localized signals)
- Dense sampling (100+ samples) in inner segments
- Adaptive segment sizing (small near center, large farther out)

**Result**: Stage 1 becomes as expensive as baseline → no computational savings.

## Detailed Results

### Test Case

- **N** = 1296000000000003744000000000001183
- **Bits**: 110
- **Factors**: p = 36000000000000013, q = 36000000000000091
- **Gap**: 78
- **Balance**: p ≈ q ≈ √N (hardest case for factorization)

### Baseline GVA (Control)

- **Runtime**: 4.065s
- **Sampled**: 1403 candidates
- **Tested**: 1115 candidates
- **Coverage**: 100%
- **Result**: ✓ Factors found at offset -38
- **Geodesic distance**: 0.000905 (minimum)

### 2-Stage GVA (PR #92 Simulation)

- **Runtime**: 4.538s (slower than baseline)
- **Stage 1**: 4.51s, 1600 samples (32 segments × 50)
- **Stage 2**: 0.03s, 50,000 tested (top 16 segments)
- **Coverage**: 50%
- **Result**: ✗ Factors not found
- **Failure mode**: Factor-bearing segment (15 of 32) likely scored in bottom half due to uniform sampling missing offset -38

### 3-Stage GVA (Hypothesis Test)

- **Runtime**: 3.402s (**1.19× faster than baseline**)
- **Stage 1**: 1.12s, 400 samples (8 segments × 50)
- **Stage 2**: 2.25s, 800 samples (16 subsegments × 50)
- **Stage 3**: 0.03s, 50,000 tested (8 final regions)
- **Coverage**: 25%
- **Result**: ✗ Factors not found
- **Max Stage 2 score**: 1.683 (above threshold 0.7, so no early exit)
- **Failure mode**: Uniform sampling at Stage 1/2 missed offset -38 in huge segments

## Hypothesis Falsification Criteria

### Primary Criterion: Correctness (FAILED)

✗ 3-stage did not recover correct factors  
✗ Cannot verify p × q = N  
**→ Hypothesis falsified on correctness grounds**

### Secondary Criterion: Runtime (PASSED but irrelevant)

✓ 3-stage runtime (3.40s) < baseline (4.07s)  
✓ Speedup: 1.19×  
**→ But speedup is meaningless without correctness**

### Tertiary Criterion: Efficiency vs 2-Stage (PASSED but irrelevant)

✓ 3-stage runtime (3.40s) < 2-stage (4.54s)  
✓ Reduced Stage 1 overhead (1.12s vs 4.51s)  
**→ Demonstrates optimization, but still fails correctness**

## Comparison to PR #92 Analysis

**Problem statement claimed**:
- PR #92 2-stage: 9.076s runtime, 50% coverage, **factors found** ✓
- Baseline: 4.027s runtime, 100% coverage, factors found ✓

**Our results**:
- Our 2-stage: 4.538s runtime, 50% coverage, **factors NOT found** ✗
- Our baseline: 4.065s runtime, 100% coverage, factors found ✓

**Discrepancy**: Our 2-stage is faster than PR #92's (4.5s vs 9.1s) but fails on correctness, while PR #92's succeeded.

**Likely explanation**: PR #92's 2-stage implementation used adaptive segment sizing or non-uniform sampling, not the naive uniform segmentation we implemented based on problem statement description. The problem statement may have simplified or omitted critical implementation details.

**Implication**: Our implementation demonstrates the **failure mode** of uniform segmentation, validating the need for adaptive approaches.

## Theoretical Consistency

Results align with theoretical predictions:

**From THEORETICAL_ANALYSIS.md**: "Pessimistic scenario (no benefit): Runtime ≥9s, hypothesis FALSIFIED" had 60% prior probability.

**Observed**: Runtime was better than predicted (3.4s, not 9s), but **correctness failed** (not predicted explicitly but implied as a risk).

**Revised theory**: Uniform multi-stage segmentation has two independent failure modes:
1. **Overhead dominance** (if Stage 1 is expensive) → slow but potentially correct
2. **Localization failure** (if sampling misses factor regions) → potentially fast but incorrect

Our results hit failure mode #2.

## Methodological Notes

### What Worked

✓ Experimental design was rigorous and reproducible  
✓ Test case matched PR #92 baseline exactly  
✓ All three methods ran on identical hardware/environment  
✓ Clear falsification criteria defined upfront  
✓ Failure mode identified and explained  

### What We Learned

1. **Adaptive sampling is essential** for 110-bit balanced semiprimes, not optional
2. **Speedup without correctness is meaningless** in factorization
3. **Uniform segmentation fails** on localized geodesic signals
4. **Multi-stage can reduce overhead** but introduces new failure modes
5. **PR #92's success** suggests non-uniform implementation (not documented)

### Threats to Validity Addressed

**Implementation bugs**: Verified segment calculations, factor locations, geodesic distances  
**Parameter tuning**: Tested with threshold 0.7 (from density profiling guidance)  
**Test case validity**: Matched PR #92 baseline runtime (4.065s vs 4.027s ✓)  
**Hardware variance**: Minimal (all methods on same system, ~0.01s variance)

## Recommendations

### DO NOT Pursue

- ✗ Uniform multi-stage segmentation on 110+ bit semiprimes
- ✗ Deeper recursion (4+, 5+ stages) without addressing localization
- ✗ Fixed-size segments over trillion-scale windows

### DO Pursue (If Revisiting)

- ✓ Adaptive segment sizing (mimic baseline's density-based strategy)
- ✓ Hybrid: adaptive sampling for Stage 1, multi-stage for refinement within promising regions
- ✓ Profile actual geodesic density distribution (we did this, see density_profile.json)
- ✓ Test on numbers where factors are less localized (but beware operational range constraints)

### Fundamental Insight

**Multi-stage recursion is not a general optimization** for geodesic-based factorization. It only works when:
1. Geodesic signals are distributed broadly enough for coarse sampling to detect
2. Segment size is small enough relative to signal localization
3. Sample count per segment is high enough to achieve adequate coverage

For 110-bit balanced semiprimes with factors within ±100 of √N and search windows of ±180 trillion, **these conditions cannot be met** with tractable segment counts.

## Conclusion

The deeper recursion hypothesis is **decisively falsified**. While 3-stage recursion achieved a 1.19× speedup, it failed the primary test: **recovering the correct factors**. The failure is not a bug but a fundamental incompatibility between uniform coarse segmentation and ultra-localized geodesic signals.

**Key takeaway**: For 110-bit balanced semiprimes, adaptive sampling near √N is not an optimization but a **necessity**. Multi-stage uniform segmentation cannot detect factor signatures localized within orders of magnitude smaller than segment sizes.

**Experimental Success**: Despite falsifying the hypothesis, this experiment succeeded in:
1. Rigorously testing the hypothesis with clear criteria
2. Identifying the precise failure mode (localization mismatch)
3. Quantifying the trade-off (1.19× speedup, 0% correctness)
4. Providing actionable insights for future research

The hypothesis is false, but the experiment achieved its scientific goal: **advancing understanding through rigorous empirical falsification**.

---

**Status**: Complete  
**Verdict**: Hypothesis decisively falsified  
**Artifacts**: See experiment_results.json, density_profile.json (if generated), RESULTS.md  
**Next Steps**: Document findings and close experiment
