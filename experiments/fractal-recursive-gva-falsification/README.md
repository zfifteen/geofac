# Fractal-Recursive GVA Falsification Experiment

## Objective

Attempt to falsify the hypothesis that integrating Mandelbrot-inspired fractal iterations and recursive window subdivision (FR-GVA) improves factorization performance over standard Geodesic Validation Assault (GVA).

## Hypothesis Under Test

**Claimed by proponent:**

> "Fractal-Recursive GVA (FR-GVA) integrates fractals via Mandelbrot-inspired iterations for candidate generation, and recursion for adaptive window subdivision. This could reduce fallbacks by focusing sampling on high-curvature 'fractal branches' in the torus, avoiding exhaustive trial division."

**Specific claims:**
1. **Fractal integration**: Model factor search as iterations z_{n+1} = z_n² + c, where c derives from κ(n). Escape time thresholds gate candidates.
2. **Recursive integration**: Recursively subdivide local windows based on geodesic density. Base case: trial division if depth > max; recursive case: sample sub-windows.
3. **Expected impact**: 15-20% density boosts, cutting max_candidates by 30% for 110+ bits, minimizing fallbacks.
4. **Small-scale validation**: Claimed to factor N=899 in 12 iterations vs. 50+ for basic QMC.

## Experimental Design

### Falsification Criteria

The hypothesis is falsified if any of the following hold:

1. **Failure criterion 1:** FR-GVA success rate ≤ standard GVA success rate on balanced semiprimes in operational range
2. **Failure criterion 2:** FR-GVA does not achieve 30% reduction in computational cost (measured by time or candidates tested)
3. **Failure criterion 3:** Fractal candidate generation mechanism does not contribute to successful factorizations (all success via trial division fallback)
4. **Failure criterion 4:** FR-GVA is slower than standard GVA when both succeed

At least one falsification criterion must be violated for the hypothesis to be considered supported.

### Test Corpus

**Operational Range:** [10^14, 10^18] per VALIDATION_GATES.md

**Test Cases:** 6 balanced semiprimes spanning the range:

| N | Label | Bits | p | q | Balance |
|---|-------|------|---|---|---------|
| 100000980001501 | 10^14 lower | 47 | 10000019 | 10000079 | p,q ≈ sqrt(N) |
| 500000591440213 | mid 10^14 | 49 | 22360687 | 22360699 | p,q ≈ sqrt(N) |
| 1000000088437283 | 10^15 | 50 | 31622777 | 31622779 | p,q ≈ sqrt(N) |
| 10000004400000259 | 10^16 | 54 | 100000007 | 100000037 | p,q ≈ sqrt(N) |
| 100000010741094833 | 10^17 | 57 | 316227767 | 316227799 | p,q ≈ sqrt(N) |
| 1000000016000000063 | 10^18 upper | 60 | 1000000007 | 1000000009 | p,q ≈ sqrt(N) |

**Rationale:** Balanced semiprimes (factors near sqrt(N)) are the hardest case for factorization algorithms. If FR-GVA works, it should excel here. Using the operational range ensures compliance with repository validation gates.

### Implementation

#### Standard GVA (Baseline)
From `gva_factorization.py`:
- 7D torus embedding using golden ratio powers
- Riemannian geodesic distance computation
- Geodesic-guided search with adaptive sampling
- Parameters: k ∈ {0.30, 0.35, 0.40}, max_candidates = 50000

#### FR-GVA (Proposed Method)
From hypothesis pseudocode:
- **Fractal iteration:**
  ```python
  c = complex(κ(n), ln(N))
  z = 0
  for i in range(1000):
      z = z² + c
      if |z| > 2:
          candidates.append(int(|z|))
  ```
- **Recursive subdivision:**
  ```python
  def fr_gva(N, depth):
      if depth > max_depth:
          return trial_division_fallback(N)
      κ = compute_kappa(N)
      if κ > threshold:
          # Generate fractal candidates
          # Test candidates
      # Recurse on subwindows
  ```
- **Parameters:** max_depth = 5, κ_threshold = 0.525

### Metrics

1. **Success rate:** Fraction of test cases where method finds correct factors
2. **Runtime:** Wall-clock time to factor (or timeout)
3. **Speedup:** ratio = GVA_time / FR-GVA_time (when both succeed)
4. **Mechanism attribution:** Which component (fractal candidates vs. trial division) finds factors

### Procedure

1. Implement FR-GVA following hypothesis specifications
2. For each test case N:
   - Run standard GVA with verbose=False
   - Run FR-GVA with verbose=False
   - Record success/failure, runtime, factors found
3. Analyze with verbose=True to determine mechanism attribution
4. Compute aggregate statistics and compare to falsification criteria

## Methodology Notes

### Precision and Determinism

- Adaptive precision: `max(50, N.bit_length() × 4 + 200)` decimal places
- Fixed seeds for any pseudo-random components
- Reproducible test cases (known p, q for verification)

### Fair Comparison

- Both methods get same max_candidates budget (50000)
- Both methods get same timeout (60 seconds)
- Both use mpmath with same precision settings
- Test on identical hardware/environment

### Threats to Validity

**Internal validity:**
- Implementation bugs in FR-GVA could cause false negatives
  - Mitigation: Follow hypothesis pseudocode exactly; test with known small example (N=899)
- Parameters (max_depth, κ_threshold) may be poorly tuned
  - Mitigation: Use values from hypothesis; if FR-GVA fails, try alternative values and document

**External validity:**
- Test cases may not represent full operational range
  - Mitigation: Sample evenly from 10^14 to 10^18 across 6 cases
- Balanced semiprimes may not represent all semiprime types
  - Mitigation: This is the standard hard case; if method fails here, it fails generally

**Construct validity:**
- "Success" defined as finding correct factors with verification p×q == N
- "Speedup" measured as wall-clock time ratio (crude but practical)
- "Mechanism" determined by verbose trace inspection (qualitative but clear)

## Barriers and Limitations

### What This Experiment Can Test

✓ Whether FR-GVA factors balanced semiprimes in [10^14, 10^18]  
✓ Whether FR-GVA is faster than standard GVA  
✓ Whether fractal candidates contribute to factorization  
✓ Whether recursive subdivision improves efficiency  

### What This Experiment Cannot Test

✗ Performance on 110+ bit semiprimes (outside operational range, too slow)  
✗ Performance on unbalanced semiprimes (p << q) - different factorization regime  
✗ Behavior on the 127-bit CHALLENGE_127 (single data point, not a test suite)  
✗ Alternative fractal formulations (beyond what hypothesis specifies)  

### Computational Constraints

- Timeout per test case: 60 seconds
- Total experiment runtime budget: ~5 minutes
- If both methods fail on all cases, experiment is inconclusive (but suggests neither method is adequate)

## Related Work

- **Standard GVA:** Implemented in `gva_factorization.py`, documented in `GVA_README.md`
- **Validation gates:** `docs/VALIDATION_GATES.md` defines operational range and test standards
- **Existing experiments:** `experiments/resonance-drift-hypothesis/` established template for experiment structure

## Expected Outcomes

**If hypothesis is TRUE:**
- FR-GVA success rate ≥ GVA success rate
- FR-GVA speedup ≥ 1.3x (30% improvement claimed)
- Fractal candidates contribute to finding factors
- Verbose traces show factors found via fractal mechanism, not trial division

**If hypothesis is FALSE:**
- FR-GVA success rate < GVA success rate, OR
- FR-GVA is slower than GVA (speedup < 1.0), OR
- All factors found via trial division fallback (fractal candidates ineffective), OR
- FR-GVA fails on most/all test cases

## Conclusion

This experiment provides a rigorous test of the FR-GVA hypothesis within the repository's operational constraints. Results will clearly support or falsify the claimed performance improvements. See [EXPERIMENT_SUMMARY.md](EXPERIMENT_SUMMARY.md) for findings and verdict.
