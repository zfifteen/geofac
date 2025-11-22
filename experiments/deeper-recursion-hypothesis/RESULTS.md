# Deeper Recursion Hypothesis - Experimental Results

## Executive Summary

**Hypothesis**: 3-stage recursion with dynamic thresholds can reduce runtime below baseline on 110-bit semiprimes.

**Verdict**: **FALSIFIED**

**Key Finding**: While 3-stage achieved faster runtime (3.40s vs 4.07s baseline, 1.19× speedup), it **failed to recover the factors**. The multi-stage approach suffers from a fatal flaw: uniform coarse sampling over huge segments misses the ultra-localized factor-bearing regions that require dense sampling near √N.

## Experimental Setup

### Test Case
- **N** = 1296000000000003744000000000001183 (110 bits)
- **Factors**: p = 36000000000000013, q = 36000000000000091
- **Gap**: 78
- **Factor location**: offset -38 from √N = 36000000000000051
- **Search window**: ±180,000,000,000,000 (±180 trillion)

### Methods Tested

1. **Baseline GVA**: Standard geodesic-guided search with adaptive sampling
   - Ultra-dense sampling near √N (step 1 for ±100)
   - Progressively sparser farther away
   - 3 k-values tested: [0.30, 0.35, 0.40]

2. **2-Stage GVA** (PR #92 simulation):
   - Stage 1: 32 segments, 50 samples each (1600 total)
   - Stage 2: Top 16 segments (50%), exhaustive search
   - Segment size: 11.25 trillion per segment

3. **3-Stage GVA** (Hypothesis):
   - Stage 1: 8 segments, 50 samples each (400 total)
   - Stage 2: 4 subsegments × 4 top regions, 50 samples each (800 total)
   - Stage 3: Top 8 final regions, exhaustive search
   - Segment size (Stage 1): 45 trillion per segment
   - Dynamic threshold: 0.7 (not triggered for early exit)

## Results

### Runtime Comparison

| Method | Runtime | vs Baseline | Speedup | Success |
|--------|---------|-------------|---------|---------|
| Baseline | 4.065s | baseline | 1.00× | ✓ CORRECT |
| 2-Stage | 4.538s | +0.473s | 0.90× | ✗ FAILED |
| 3-Stage | 3.402s | -0.663s | **1.19×** | ✗ FAILED |

### Candidate Efficiency

| Method | Total Candidates | Coverage | Factors Found |
|--------|-----------------|----------|---------------|
| Baseline | ~50,000 | 100% | ✓ (offset -38) |
| 2-Stage | 51,600 | 50% | ✗ |
| 3-Stage | 51,200 | 25% | ✗ |

### Stage Breakdown (3-Stage)

| Stage | Time | Samples/Tested | Purpose |
|-------|------|----------------|---------|
| 1 (Very Coarse) | 1.12s | 400 samples | Score 8 segments, select top 4 |
| 2 (Medium) | 2.25s | 800 samples | Refine 4 → 16 subsegments, select top 8 |
| 3 (Fine) | 0.03s | 50,000 tested | Exhaustive search in 8 regions |

**Total**: 3.40s (1.19× faster than baseline)

## Analysis

### Why Did 3-Stage Fail Despite Being Faster?

The 3-stage approach was **faster but incorrect** due to a fundamental mismatch between sampling strategy and factor location:

#### Problem 1: Uniform Sampling Misses Localized Factors

**Factor location**: offset -38 from √N (extremely close)

**2-stage sampling**:
- Segment 15 (contains factor): range [-11.25T, 0]
- Sampling: 50 points uniformly spaced = 225 billion apart
- Probability of hitting offset -38 in a 50-sample uniform grid over 11.25 trillion: **~0%**

**3-stage Stage 1 sampling**:
- Segment 3 (contains factor): range [-45T, 0]
- Sampling: 50 points uniformly spaced = 900 billion apart
- Probability of hitting offset -38: **~0%**

**Baseline sampling**:
- Ultra-dense near √N: step size 1 for ±100 (guaranteed to hit offset -38)
- Sampled 1403 candidates total, found factor at distance 0.000905

#### Problem 2: Geodesic Distance is Highly Localized

The baseline found:
- **Minimum geodesic distance**: 0.000905 (at factor offset -38)
- **Distance at factor**: 0.6021 (from N to p embedding)

This implies the geodesic signal is extremely localized - only candidates very close to the factor have low distance. Coarse uniform sampling hundreds of billions away from the factor cannot detect this signal.

#### Problem 3: Segment Scoring Failure

**2-stage**: Factor in segment 15 of 32
- Top 16 selected = 50% coverage
- If segment 15 scored in bottom half, factor region pruned

**3-stage**: Factor in segment 3 of 8
- Top 4 selected = 50% coverage
- Must score in top 4 to proceed
- At Stage 2: subdivide into 4 subsegments, factor in one subsegment
- Top 2 per parent selected
- Even if Stage 1 passed, Stage 2 could still prune

**Root cause**: Uniform sampling does not capture the localized geodesic peak at offset -38 when sampling every 225-900 billion positions.

### Why Was 3-Stage Faster?

Despite failing, 3-stage was faster because:

1. **Reduced Stage 1 overhead**: 400 samples (1.12s) vs 2-stage's 1600 samples (4.51s)
2. **Efficient pruning**: 25% coverage vs 50% or 100%
3. **Stage 3 exhaustive search was fast**: 0.03s (same as 2-stage's Stage 2)

The speedup came from computational savings, not from finding factors more efficiently.

## Implications

### Hypothesis Falsification

The hypothesis is **decisively falsified** on multiple grounds:

1. ✗ **Correctness failure**: 3-stage did not recover factors (primary failure)
2. ✗ **Coverage-correctness tradeoff**: 25% coverage insufficient for uniform coarse sampling
3. ✗ **2-stage also failed**: Even 50% coverage with 32 segments failed

### Fundamental Problem Identified

**Multi-stage uniform segmentation is incompatible with localized geodesic signals.**

For a 110-bit semiprime with factor offset -38 from √N:
- Baseline uses step size 1 near √N (hits factor immediately)
- 2-stage uses uniform sample every 225 billion (misses factor)
- 3-stage uses uniform sample every 900 billion (misses factor even more)

**Scaling issue**: Search window is 360 trillion, but factor is within 100 of center. Uniform segmentation cannot bridge this 12-order-of-magnitude gap with tractable sample counts.

### What Would Be Required to Fix It?

To make multi-stage recursion work, the coarse sampling must be:

1. **Adaptive**: Dense near √N, sparse farther away (mimicking baseline)
2. **Non-uniform segments**: Smaller segments near center, larger farther out
3. **Much finer Stage 1**: Need segments < 1 billion to have any hope of detecting geodesic signal with 50 samples

**Example fix for 2-stage**:
- Inner region ±10,000: 20 segments, 100 samples each (dense)
- Middle region ±100 million: 8 segments, 50 samples each
- Outer region to window: 4 segments, 20 samples each (sparse)

This would mimic baseline's adaptive strategy while still using coarse-to-fine.

However, this defeats the purpose: **if coarse sampling must be as dense as baseline near √N, there's no computational savings**.

## Comparison to PR #92 Analysis

The problem statement referenced PR #92, which reported:
- **Baseline**: 4.027s, 1403 sampled, 1115 tested, 100% coverage, factors found
- **2-stage**: 9.076s, 1600 + 1149 = 2749 samples, 50% coverage, factors found

**Our results**:
- **Baseline**: 4.065s (matches PR #92 ✓)
- **2-stage**: 4.538s (faster than PR #92's 9.076s but failed to find factors ✗)

**Discrepancy**: PR #92 claims 2-stage found factors with 50% coverage. Our 2-stage did not.

**Possible explanations**:
1. PR #92 may have used adaptive segment sizing (not specified)
2. PR #92 may have used different sampling strategy within segments
3. Our implementation is uniform segmentation (as described in problem statement)
4. The 110-bit test case may be different (problem gives only N, not segment details from PR #92)

**Key point**: Our uniform segmentation 2-stage replicates the overhead (stage 1 time ~4.5s) but fails on correctness, suggesting PR #92 used a more sophisticated approach than naive uniform segments.

## Theoretical Consistency

Results are consistent with theoretical predictions in THEORETICAL_ANALYSIS.md:

**Predicted**: "Pessimistic scenario - no benefit, hypothesis FALSIFIED" had 60% prior probability.

**Reasoning**: "Adding another stage adds more overhead... 110-bit case may not have enough scale for amortization."

**Observed**: 3-stage was faster (unexpected) but failed on correctness (expected risk).

**Conclusion**: Theory underestimated the localization problem but correctly identified overhead as a key issue.

## Lessons Learned

### What This Experiment Proved

1. ✓ **Multi-stage can be faster** (if correctness is ignored)
2. ✓ **Pruning reduces coverage** (25% vs 100%)
3. ✓ **Uniform segmentation fails** on ultra-localized geodesic signals
4. ✓ **Adaptive sampling is essential** for 110-bit balanced semiprimes

### What This Experiment Did Not Prove

1. ✗ Whether adaptive multi-stage could work (not tested)
2. ✗ Whether PR #92's 2-stage actually used uniform segments (unknown)
3. ✗ Whether deeper recursion helps on different number types (not tested)

### Recommendations for Future Work

**DO NOT pursue**:
- Uniform segmentation multi-stage approaches
- Deeper recursion (4+, 5+ stages) with uniform sampling
- Fixed-size segments over huge windows

**DO pursue**:
- Adaptive segment sizing (mimicking baseline's density-based sampling)
- Hybrid approaches: adaptive sampling for Stage 1, then multi-stage within promising regions
- Different number types where factors are less localized (but this violates operational range)

## Conclusion

The deeper recursion hypothesis is **falsified**. While 3-stage recursion achieved a 1.19× speedup in runtime, it failed the primary criterion: **recovering the correct factors**. The failure mode is clear and reproducible: uniform coarse sampling over trillion-scale segments cannot detect geodesic signals localized within hundreds of positions.

The experiment successfully demonstrates that **runtime improvement without correctness is meaningless** in factorization algorithms. The baseline GVA's adaptive sampling strategy is not an optimization - it is a necessity for detecting ultra-localized factor signatures in the 110-bit regime.

**Final verdict**: Hypothesis decisively falsified. Multi-stage uniform segmentation is not viable for 110-bit balanced semiprimes.
