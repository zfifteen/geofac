# FR-GVA Hypothesis Falsification Experiment

## Executive Summary

**VERDICT: HYPOTHESIS FALSIFIED**

The Fractal-Recursive GVA (FR-GVA) hypothesis claims to improve factorization through:
1. Mandelbrot-inspired fractal iterations for candidate generation
2. Recursive window subdivision based on geodesic density  
3. Expected 15-20% density boosts and 30% reduction in candidates

**KEY FINDING:** FR-GVA succeeds only via its trial division fallback, not via fractal properties. The fractal candidate generation mechanism produces candidates that fail to find factors. All successful factorizations occur in the recursive base case using simple trial division.

## Critical Analysis

### What Actually Happens in FR-GVA

Analysis of verbose execution traces reveals:

1. **Fractal candidates are ineffective**: The Mandelbrot-style iteration `z_{n+1} = z^2 + c` with `c = complex(κ, ln(N))` generates candidates, but these candidates never yield factors.

2. **Success comes from trial division**: All factors are found during the recursive "fallback" at depth > max_depth, where the implementation performs straightforward trial division.

3. **Apparent speedup is misleading**: FR-GVA appears faster than standard GVA (88x average speedup) only because:
   - GVA computes expensive geodesic distance calculations
   - FR-GVA uses simple trial division (cheaper operations)
   - This is not the claimed fractal-recursive mechanism working

### Why the Fractal Mechanism Fails

The hypothesis proposes that factors create "fractal branches" in high-dimensional space that can be identified through escape-time iterations. However:

1. **No mathematical foundation**: The connection between Mandelbrot set escape times and semiprime factorization is purely speculative. The formula `c = complex(κ(n), ln(N))` has no derivation or theoretical justification.

2. **Arbitrary parameter choices**: The escape radius (2.0), iteration count (1000), and candidate mapping are chosen without principled reasoning.

3. **Dimensional mismatch**: The Mandelbrot set operates in complex 2D space, while the claimed "geodesic density" requires 7D torus embeddings. The hypothesis conflates these distinct geometric structures.

4. **κ approximation is crude**: Computing `κ(n) = d(n) · ln(n+1) / e²` requires the divisor count d(n), but for large semiprimes this is exactly the factorization problem. The implementation uses a trivial approximation (checking divisibility by {2,3,5,7,11,13}) that doesn't capture the semiprime structure.

### Comparison Results

Test suite of 6 balanced semiprimes in operational range [10^14, 10^18]:

| Test Case | Bits | Standard GVA | FR-GVA | Winner |
|-----------|------|--------------|--------|---------|
| 10^14 lower | 47 | ✗ Failed | ✓ 0.003s | FR-GVA* |
| mid 10^14 | 49 | ✗ Failed | ✓ 0.003s | FR-GVA* |
| 10^15 | 50 | ✓ 0.331s | ✓ 0.003s | FR-GVA* |
| 10^16 | 54 | ✓ 0.533s | ✓ 0.004s | FR-GVA* |
| 10^17 | 57 | ✗ Failed | ✓ 0.007s | FR-GVA* |
| 10^18 upper | 60 | ✓ 0.663s | ✓ 0.017s | FR-GVA* |

**Success Rate:** Standard GVA 50% (3/6), FR-GVA 100% (6/6)  
**Average Speedup:** 88.26x (when both succeed)

*FR-GVA wins via trial division fallback, not fractal mechanism

### Why This Falsifies the Hypothesis

1. **The claimed mechanism doesn't work**: Fractal candidate generation never finds factors. Success depends entirely on classical trial division.

2. **No evidence of "density boosts"**: The hypothesis claims 15-20% density boosts from focusing on "fractal branches." In practice, fractal candidates are distributed randomly and checked without success.

3. **Recursive subdivision adds overhead**: The recursive structure doesn't improve search efficiency - it merely partitions the trial division into smaller windows. This adds function call overhead without benefit.

4. **Trial division is already well-known**: The only working component (trial division) is the classical method the hypothesis explicitly claims to avoid. The coating of fractal/recursive terminology doesn't change what's actually happening.

5. **Speedup is an artifact**: FR-GVA appears faster only because it uses cheaper operations (integer division) while GVA uses expensive geodesic calculations. This comparison is apples-to-oranges.

## Detailed Findings

### Implementation Review

**As Specified:**
```python
# Fractal iteration (from hypothesis pseudocode)
c = complex(kappa, np.log(N))
z = 0j
for _ in range(1000):
    z = z**2 + c
    if abs(z) > 2:  # Escape
        candidates.append(int(abs(z)))
```

**Reality:** The escape-time candidates are converted to integers near sqrt(N) via arbitrary modular arithmetic:
```python
candidate_offset = int(magnitude * 1000) % 10000 - 5000
candidate = sqrt_N + candidate_offset
```

This mapping has no geometric or number-theoretic justification. It's essentially a pseudo-random number generator seeded by the Mandelbrot iteration.

### Execution Trace Analysis

For N = 100000980001501 (47 bits):
- **Fractal candidates generated:** ~5000+ (across all recursion depths)
- **Fractal candidates tested:** All checked via divisibility
- **Fractal candidates successful:** 0
- **Factor found by:** Trial division at depth 6 (base case)
- **Factor location:** Within window [9990048, 10010048] around sqrt(N) = 10000048

The factors (10000019, 10000079) are found simply because they fall within the search window and trial division eventually reaches them. The fractal mechanism plays no role.

### Theoretical Objections

1. **No bridge between fractals and factorization:** The Mandelbrot set encodes complex dynamics unrelated to multiplicative structure of integers. Escape times measure divergence rates, not factorization properties.

2. **κ(n) doesn't encode factorization:** The curvature metric κ(n) = d(n)·ln(n+1)/e² uses divisor count, but computing d(n) for a semiprime is equivalent to factoring it. The approximation used (checking small primes) doesn't capture the semiprime structure.

3. **Recursive subdivision doesn't leverage structure:** Recursively splitting [a, b] into [a, m] and [m+1, b] is just divide-and-conquer trial division. Without a heuristic to prioritize subwindows (which fractal candidates fail to provide), it's no better than linear search.

4. **Comparison to GVA is flawed:** GVA uses Riemannian geodesic distances in 7D torus embeddings - computationally expensive but geometrically motivated. FR-GVA uses trial division - computationally cheap but classical. They're solving the problem in fundamentally different ways, so speed comparison is meaningless.

## Reproducibility

All code and results are available in:
- `/home/runner/work/geofac/geofac/experiments/fractal-recursive-gva-falsification/`

Test cases use balanced semiprimes (factors near sqrt(N)) within the operational range [10^14, 10^18] per VALIDATION_GATES.md. All test cases are deterministic and reproducible.

To reproduce:
```bash
cd /home/runner/work/geofac/geofac
python3 experiments/fractal-recursive-gva-falsification/comparison_experiment.py
```

## Conclusion

The Fractal-Recursive GVA hypothesis is **decisively falsified**. The proposed fractal-based candidate generation mechanism does not work. All successful factorizations are achieved through classical trial division, which the hypothesis explicitly claimed to avoid or minimize.

The apparent performance improvements are artifacts of comparing:
- **Expensive geometric calculations** (standard GVA with 7D torus + Riemannian distance)
- **Cheap classical method** (trial division in FR-GVA fallback)

The hypothesis claimed to extend GVA by adding fractal and recursive enhancements. In reality, it accidentally replaced GVA's geometric approach with classical trial division, then incorrectly attributed success to the fractal mechanism.

**Recommendation:** Do not pursue FR-GVA. The fractal-recursive approach adds complexity without benefit. If trial division performance is adequate for the operational range, use it directly. If geometric methods are preferred, continue developing standard GVA or explore genuinely geometric fractal structures (e.g., p-adic fractals in number theory) with rigorous mathematical foundations.
