# Geometric Resonance Hypothesis Validation

## Multi-Scale Test Results

**Status**: **FALSIFIED AT ALL SCALES** (10, 20, 30, 40, 50, 60, 127 bits)

| Bit Size | κ Pass | θ' Pass | Overall | κ Difference | θ' Rel. Diff |
|----------|--------|---------|---------|--------------|--------------|
| 9        | ✗      | ✗       | FAIL    | 2.85e-02     | 10.84%       |
| 19       | ✗      | ✗       | FAIL    | 1.04e-03     | 35.42%       |
| 29       | ✗      | ✗       | FAIL    | 9.89e-05     | 20.02%       |
| 39       | ✗      | ✗       | FAIL    | 1.65e-05     | 9.57%        |
| 49       | ✗      | ✗       | FAIL    | 4.84e-07     | 26.60%       |
| 59       | ✗      | ✗       | FAIL    | 1.41e-08     | 30.68%       |
| 127      | ✗      | ✗       | FAIL    | 5.94e-02     | 19.85%       |

**Legend**: κ = curvature invariant (threshold: < 1e-16), θ' = geometric resolution (threshold: < 1%)

**Conclusion**: The hypothesis does not hold at any tested scale. Both the curvature invariant and geometric resolution conditions fail across the entire range from 10 bits to 127 bits.

## Executive Summary

**Status**: **FALSIFIED**  
**Date**: 2025-11-16T18:34:19Z  
**Precision**: 720 decimal places  
**Tests**: 7 bit sizes (9, 19, 29, 39, 49, 59, 127 bits)

This gist validates the geometric resonance hypothesis proposed in `.github/conversations.md` against multiple scales, including the official Gate 1 target from `docs/VALIDATION_GATES.md`.

## Hypothesis Under Test

From `.github/conversations.md`:

1. **Curvature hypothesis**: For semiprime factors p and q, the curvature values κ(p) and κ(q) should be nearly identical (within threshold 1e-16), where:
   - κ(n) = σ₀(n) · ln(n+1) / e²
   - σ₀(n) = count of divisors of n

2. **Geometric resolution hypothesis**: The geometric resolution values θ'(p, 0.3) and θ'(q, 0.3) should be approximately equal, where:
   - θ'(n, k) = φ · ((n mod φ) / φ)^k
   - φ = golden ratio ≈ 1.618...
   - k = 0.3

## Gate 1 Target (Official)

From `docs/VALIDATION_GATES.md`:

- **N** = 137524771864208156028430259349934309717
- **p** = 10508623501177419659 (prime factor)
- **q** = 13086849276577416863 (prime factor)
- **Verification**: p × q = N ✓

## Results

### Curvature Analysis

```
σ₀(p) = 2 (p is prime)
σ₀(q) = 2 (q is prime)
σ₀(N) = 4 (N = p×q is semiprime)

κ(p) = 11.8550264860353795749503870549618920...
κ(q) = 11.9144147611049502635148492917903955...
κ(N) = 47.5388824942806596768375934267894177...

|κ(p) - κ(q)| = 0.0593882750695706885644622368285...
```

**Hypothesis 1**: |κ(p) - κ(q)| < 1e-16  
**Result**: **FAIL** (difference is ~0.059, far exceeding threshold)

### Geometric Resolution Analysis

```
φ = 1.61803398874989484820458683436563...

p mod φ = 1.06137373640417816661717355652315...
q mod φ = 0.50752659843465639754361108027959...
N mod φ = 0.68409770315651935636573330876921...

θ'(p, 0.3) = 1.42577780315180820588575012215146...
θ'(q, 0.3) = 1.14269148320515771577336576134033...

|θ'(p, 0.3) - θ'(q, 0.3)| = 0.28308631994665049011238436081112...
Relative difference = 19.85% (0.1985...)
```

**Hypothesis 2**: θ'(p, 0.3) ≈ θ'(q, 0.3) with relative difference < 1%  
**Result**: **FAIL** (relative difference is ~19.85%, far exceeding threshold)

## Conclusion

### Multi-Scale Analysis

Testing across 7 bit sizes (9, 19, 29, 39, 49, 59, 127 bits) reveals that **the hypothesis fails at all scales**:

- **Curvature invariant**: All tests fail the κ threshold (< 1e-16). Differences range from 1.41e-08 (59 bits) to 5.94e-02 (127 bits), consistently exceeding the threshold by many orders of magnitude.

- **Geometric resolution**: All tests fail the θ' threshold (< 1%). Relative differences range from 9.57% (39 bits) to 35.42% (19 bits), consistently exceeding the 1% threshold by factors of 10-35×.

- **Scale dependency**: While κ differences generally decrease with bit size (suggesting factors become more similar), θ' differences show no consistent pattern and remain unacceptably large across all scales.

### Gate 1 Specific Results

Both components of the geometric resonance hypothesis are **falsified** when tested against the Gate 1 challenge semiprime:

1. The curvature values κ(p) and κ(q) differ by approximately 0.059, which is **10¹⁴ times larger** than the proposed threshold of 1e-16.

2. The geometric resolution values θ'(p, 0.3) and θ'(q, 0.3) differ by approximately 19.85% in relative terms, which is **nearly 20 times larger** than the 1% threshold.

These results indicate that the hypothesis—as formulated—does not hold at any tested scale. The curvature and geometric resolution properties of the prime factors p and q are not sufficiently similar to support the claim that "resonance amplitude peaks align with low κ(n) for semiprimes."

## Artifacts

1. **`validate_hypothesis.py`**: Python validation script for Gate 1 (127-bit) with mpmath (720 decimal places precision)
2. **`validate_multi_scale.py`**: Python validation script for multi-scale testing (10-127 bits)
3. **`results.json`**: Complete numerical results for Gate 1 in JSON format
4. **`multi_scale_results.json`**: Complete numerical results for all scales in JSON format
5. **`validation_run.log`**: Full console output from Gate 1 validation run
6. **`multi_scale_run.log`**: Full console output from multi-scale validation run
7. **`README.md`**: This summary document

## Methodology

- **Precision**: 720 decimal places (exceeds requirement: 127 bits × 4 + 200 = 708)
- **Factors**: Official Gate 1 factors from `docs/VALIDATION_GATES.md`
- **Libraries**: Python 3 with mpmath for arbitrary-precision arithmetic
- **Reproducibility**: All parameters, seeds, and thresholds are explicitly documented
- **Validation**: Product check p × q = N verified before analysis

## Scope and Limitations

This gist addresses only the specific formulations stated in `.github/conversations.md`:
- The curvature function κ(n) = σ₀(n) · ln(n+1) / e²
- The geometric resolution θ'(n, k) = φ · ((n mod φ) / φ)^k with k = 0.3
- The threshold criteria (1e-16 for curvature, 1% for geometric resolution)

Alternative formulations, different threshold values, or modifications to the functions may yield different results and would require separate validation.

## Recommendations

Based on these multi-scale results:

1. **Do not integrate** the curvature-guided sampling enhancement into the main factorization algorithm. The underlying hypothesis does not hold at any tested scale from 10 bits to 127 bits.

2. **Re-examine** the mathematical foundations of the hypothesis. The observed pattern suggests:
   - κ(p) and κ(q) differences decrease with bit size but never approach the required threshold
   - θ' differences show no consistent convergence and remain large across all scales
   - The hypothesis may require fundamentally different formulations or threshold criteria

3. **Consider alternative metrics** if pursuing geometric approaches. The current formulations do not exhibit the required invariance properties for semiprime factors at any tested scale.

## Reproducibility

To reproduce the single-scale validation (Gate 1):

```bash
cd gists/geometric-resonance-hypothesis
pip3 install mpmath
python3 validate_hypothesis.py
```

Expected output: Validation completes with "HYPOTHESIS FALSIFIED" conclusion and generates `results.json`.

To reproduce the multi-scale validation (10-127 bits):

```bash
cd gists/geometric-resonance-hypothesis
pip3 install mpmath sympy
python3 validate_multi_scale.py
```

Expected output: Tests at 7 bit sizes, all showing "FAIL", and generates `multi_scale_results.json`.
python3 validate_hypothesis.py
```

Expected output: Validation completes with "HYPOTHESIS FALSIFIED" conclusion and generates `results.json`.
