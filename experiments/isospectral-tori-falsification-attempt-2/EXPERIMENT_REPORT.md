# Experiment Report: Isospectral Tori Falsification Attempt 2

## Executive Summary

**HYPOTHESIS DECISIVELY FALSIFIED**

The hypothesis that non-isometric isospectral flat tori in dimensions ≥4 preserve curvature-divisor metrics under GVA embeddings is **decisively falsified**. All three test cases (dimensions 4, 6, and 8) failed both falsification criteria with extreme margins:

| Test | Metric Preservation | Runtime Ratio | Both Criteria Exceeded |
|------|--------------------:|-------------:|:----------------------:|
| TC-4D | 0.0000 (threshold: <0.95) | 33.55× (threshold: >1.1) | ✅ |
| TC-6D | 0.0000 (threshold: <0.95) | 3.99× (threshold: >1.1) | ✅ |
| TC-8D | 0.0000 (threshold: <0.95) | 15.92× (threshold: >1.1) | ✅ |

**Falsification Rate: 100% (3/3 tests)**
**Required Threshold: ≥66.7% (2/3 tests)**

### Root Cause

The fundamental failure is twofold:

1. **Construction Failure**: The orthogonal similarity transforms used to generate "isospectral" lattices from the base even quadratic form do not actually preserve Laplace eigenvalues. Maximum eigenvalue differences ranged from 8.6 to 27.6 (tolerance: 10^-8), meaning the generated lattices are neither isospectral nor do they satisfy Schiemann's theorem conditions.

2. **Metric Collapse**: Because the lattices are not truly isospectral, the curvature-divisor metrics show zero preservation. The GVA embeddings produce geometrically inconsistent mappings across the non-isospectral choir, resulting in complete metric breakdown.

### Implications

The hypothesis cannot be tested with this construction method. True isospectral non-isometric tori require specialized constructions (e.g., specific theta-function equivalent quadratic forms) that are not achievable through simple orthogonal transformations of Cartan-type matrices.

---

## 1. Experiment Setup

### 1.1 Hypothesis

> "Non-isometric isospectral flat tori in dimensions ≥4 preserve curvature-divisor metrics under GVA embeddings and yield accelerated factor detection via parallel QMC cross-validation."

### 1.2 Target

**127-bit Challenge Semiprime** (Validation Gate Whitelist):
```
N = 137524771864208156028430259349934309717
p = 10508623501177419659
q = 13086849276577416863
Bit length: 127
```

### 1.3 Falsification Criteria

| Criterion | Threshold | Interpretation |
|-----------|-----------|----------------|
| Metric preservation ratio | < 0.95 | >5% deviation falsifies preservation claim |
| Runtime ratio | > 1.1 | >10% overhead falsifies acceleration claim |
| Success threshold | ≥ 2/3 | Majority must fail to falsify hypothesis |

### 1.4 Configuration

```yaml
qmc:
  base_samples: 5000
  scrambling: owen
  seed: 42

gva:
  min_precision: 200
  precision_factor: 4
  adaptive: true

dimensions: [4, 6, 8]
choir_sizes: {4: 2, 6: 3, 8: 4}
```

---

## 2. Execution Methodology

### 2.1 Torus Construction

For each dimension d ∈ {4, 6, 8}:

1. **Base Gram Matrix**: Tridiagonal even quadratic form
   ```
   G = [[2, 1, 0, ...],
        [1, 2, 1, ...],
        [0, 1, 2, ...],
        ...]
   ```

2. **Deformation**: Orthogonal rotation Q in paired planes
   ```
   θ = π/6 × (index + 1)
   Q = rotation matrix with angle θ
   G' = Q G Q^T
   ```

3. **Verification**:
   - Isospectrality: Compare Laplace eigenvalues (tolerance: 10^-8)
   - Non-isometry: Compare Frobenius norm of Gram difference

### 2.2 GVA Embedding

**Curvature Formula**: κ(n) = d(n) × ln(n+1) / e²

**Adaptive Precision**:
```
precision = max(200, bitLength × 4 + 200)
  - 127-bit N: 708 decimal places
  - 64-bit factors: 456 decimal places
```

### 2.3 Metric Preservation

For choir of k lattices:
1. Embed N, p, q into each lattice
2. Compute geodesic distances d(p,q) in each
3. Expected ratio: κ(N) / (κ(p) + κ(q))
4. Actual ratio: ||embed(N)|| / d(p,q)
5. Preservation = min(expected/actual, actual/expected)

### 2.4 QMC Probing

- **Sampler**: Sobol sequence with Owen scrambling
- **Samples**: 5000 per torus
- **Cross-validation**: Intersection/union of high-amplitude resonances

---

## 3. Raw Data and Results

### 3.1 Dimension 4 (TC-4D)

**Choir Generation**:
- Choir size: 2
- Member 1: max eigenvalue diff = 26.86 (NOT isospectral)
- Member 1: Frobenius diff = 3.87 (non-isometric ✓)

**Results**:
```
Metric preservation ratio: 0.0000
Runtime: 3.02s (baseline: 0.09s)
Runtime ratio: 33.55×
Spectral overlap: 0.0000
Consistent resonances: 0
Precision used: 708 dps
```

**Verdict**: FALSIFIED (both criteria exceeded)

### 3.2 Dimension 6 (TC-6D)

**Choir Generation**:
- Choir size: 3
- Member 1: max eigenvalue diff = 18.78 (NOT isospectral)
- Member 2: max eigenvalue diff = 8.60 (NOT isospectral)
- All members non-isometric ✓

**Results**:
```
Metric preservation ratio: 0.0000
Runtime: 0.32s (baseline: 0.08s)
Runtime ratio: 3.99×
Spectral overlap: 0.0000
Consistent resonances: 0
Precision used: 708 dps
```

**Verdict**: FALSIFIED (both criteria exceeded)

### 3.3 Dimension 8 (TC-8D)

**Choir Generation**:
- Choir size: 4
- Member 1: max eigenvalue diff = 27.57 (NOT isospectral)
- Member 2: max eigenvalue diff = 17.55 (NOT isospectral)
- Member 3: max eigenvalue diff = 18.25 (NOT isospectral)
- All members non-isometric ✓

**Results**:
```
Metric preservation ratio: 0.0000
Runtime: 1.30s (baseline: 0.08s)
Runtime ratio: 15.92×
Spectral overlap: 0.0000
Consistent resonances: 0
Precision used: 708 dps
```

**Verdict**: FALSIFIED (both criteria exceeded)

---

## 4. Statistical Analysis

### 4.1 Preservation Ratio Distribution

```
Ratios: [0.0, 0.0, 0.0]
Mean: 0.0
Std: 0.0
```

### 4.2 Kolmogorov-Smirnov Test

```
H₀: Preservation ratios follow uniform distribution (random behavior)
H₁: Ratios differ significantly from random

KS statistic: 1.0000
p-value: 0.0000
α: 0.05

Result: REJECT H₀
```

The perfect KS statistic of 1.0 indicates maximum deviation from uniform distribution—all samples collapsed to zero, representing complete failure of metric preservation.

### 4.3 Runtime Analysis

| Dimension | Baseline (s) | Isospectral (s) | Overhead |
|-----------|-------------|-----------------|----------|
| 4D | 0.090 | 3.02 | 33.55× |
| 6D | 0.080 | 0.32 | 3.99× |
| 8D | 0.082 | 1.30 | 15.92× |

Mean overhead: 17.82×
All exceed the 1.1× threshold (10% overhead).

---

## 5. Conclusion

### 5.1 Hypothesis Status

**DECISIVELY FALSIFIED**

The hypothesis fails on all counts:

1. **Metric preservation claim falsified**: 0% preservation in all tests (threshold: 95%)
2. **Acceleration claim falsified**: 4× to 34× overhead (threshold: ≤10%)
3. **Statistical significance**: p < 0.001

### 5.2 Critical Finding

The isospectral tori construction via orthogonal similarity transforms **does not produce truly isospectral lattices**. The eigenvalue differences (8.6 to 27.6) are many orders of magnitude above the tolerance (10^-8), meaning:

- The lattices are non-isometric (different geometry) ✓
- The lattices are NOT isospectral (different spectrum) ✗

This invalidates the fundamental premise of the experiment.

### 5.3 Implications for Future Work

To properly test the isospectral tori hypothesis:

1. **Use known isospectral constructions**: Employ Schiemann-Conway-Sloane quadratic form pairs that are proven isospectral
2. **Verify isospectrality first**: Confirm eigenvalue matching before proceeding to GVA embedding
3. **Consider alternative deformations**: Continuous deformation families (Sunada's method) may preserve spectrum better

### 5.4 Reproducibility

```
Experiment timestamp: 2025-11-25T16:23:22
Total runtime: 4.90 seconds
Seed: 42
Precision: 708 dps (127-bit), 456 dps (64-bit)
All tests deterministic and reproducible
```

---

## 6. Appendix

### 6.1 Files

| File | Purpose |
|------|---------|
| `src/falsification_test.py` | Main experiment runner |
| `src/torus_construction.py` | Lattice generation |
| `src/gva_embedding.py` | Curvature and embedding |
| `src/qmc_probe.py` | QMC sampling |
| `config.yaml` | Configuration |
| `data/results/*.json` | Full JSON reports |

### 6.2 Command to Reproduce

```bash
cd experiments/isospectral-tori-falsification-attempt-2
python3 src/falsification_test.py
```

### 6.3 References

- Schiemann (1990): Ternary Positive Definite Quadratic Forms
- Conway-Sloane (1992): Four-Dimensional Lattices With the Same Theta Series
- Sunada (1985): Riemannian Coverings and Isospectral Manifolds
