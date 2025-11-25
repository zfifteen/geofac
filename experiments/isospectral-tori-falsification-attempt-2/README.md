# Technical Design: Isospectral Tori Falsification Experiment - Attempt 2

## 1. Objective

Attempt to falsify the hypothesis that non-isometric isospectral flat tori in dimensions ≥4 preserve curvature-divisor metrics under GVA embeddings and yield accelerated factor detection via parallel QMC cross-validation.

**Hypothesis Under Test**:
> Non-isometric isospectral flat tori in dimensions ≥4 preserve curvature-divisor metrics under GVA embeddings and yield accelerated factor detection via parallel QMC cross-validation.

## 2. Falsification Criteria

| Criterion | Threshold | Falsifies If |
|-----------|-----------|--------------|
| Metric preservation ratio | < 0.95 | Preservation claim fails |
| Runtime ratio | > 1.1 | Acceleration claim fails |
| Success threshold | ≥ 2/3 tests | Overall hypothesis fails |

## 3. Target

**127-bit Challenge Semiprime** (validation gate whitelist):

```
N = 137524771864208156028430259349934309717
p = 10508623501177419659
q = 13086849276577416863
```

This target satisfies the validation gates:
- ✅ 127-bit whitelist exception (not subject to [10^14, 10^18] range)
- ✅ Known factors for verification
- ✅ Canonical test case for geofac

## 4. Test Cases

| Test ID | Dimension | Choir Size | Lattice Type |
|---------|-----------|------------|--------------|
| TC-4D | 4 | 2 | Even quadratic forms (tridiagonal) |
| TC-6D | 6 | 3 | Tridiagonal Cartan-type |
| TC-8D | 8 | 4 | Tridiagonal Cartan-type |

## 5. Methodology

### 5.1 Isospectral Tori Construction

1. **Generate base Gram matrix** using tridiagonal even quadratic form:
   ```
   G = [2, 1, 0, ...]
       [1, 2, 1, ...]
       [0, 1, 2, ...]
       ...
   ```

2. **Apply orthogonal deformation** Q G Q^T where Q is a rotation matrix in paired planes (preserves eigenvalues under similarity transform).

3. **Verify isospectrality** by comparing Laplace eigenvalues (tolerance: 10^-8).

4. **Verify non-isometry** by comparing Frobenius norm of Gram matrix difference.

### 5.2 GVA Embedding

Discrete curvature: κ(n) = d(n) × ln(n+1) / e²

Where:
- d(n) = divisor count (4 for n = p × q with p ≠ q)
- Adaptive precision: max(200, bitLength × 4 + 200) = 708 dps for 127-bit

### 5.3 Metric Preservation

For semiprime n = p × q:
1. Embed n, p, q into each choir member
2. Compute geodesic distances
3. Compare expected ratio κ(n)/(κ(p)+κ(q)) with actual geometric ratio
4. Preservation = min(expected/actual, actual/expected)

### 5.4 QMC Probing

- **Sampler**: Sobol sequences with Owen scrambling
- **Samples**: 5000 per torus
- **Seed**: 42 (fixed for reproducibility)
- **Cross-validation**: Compute overlap of high-amplitude resonances across choir

### 5.5 Statistical Validation

Kolmogorov-Smirnov test on preservation ratios:
- Null hypothesis: ratios follow uniform distribution (random behavior)
- α = 0.05

## 6. Implementation

### 6.1 Directory Structure

```
experiments/isospectral-tori-falsification-attempt-2/
├── INDEX.md                    # Navigation
├── README.md                   # This document
├── EXPERIMENT_REPORT.md        # Complete findings
├── config.yaml                 # Configuration
├── src/
│   ├── __init__.py
│   ├── falsification_test.py   # Main runner
│   ├── torus_construction.py   # Lattice generators
│   ├── gva_embedding.py        # GVA and curvature
│   └── qmc_probe.py            # QMC sampling
└── data/
    ├── test_cases.json         # Test configurations
    └── results/                # Output artifacts
```

### 6.2 Dependencies

- Python 3.12+
- numpy
- scipy
- mpmath
- PyYAML

### 6.3 Precision Requirements

| Scale | Bit Length | Precision (dps) |
|-------|------------|-----------------|
| p, q | 64-bit | 456 |
| N | 127-bit | 708 |

Formula: precision = max(200, bitLength × 4 + 200)

## 7. Running the Experiment

```bash
cd experiments/isospectral-tori-falsification-attempt-2
python3 src/falsification_test.py
```

Output:
- Console summary
- JSON report in `data/results/`

## 8. References

- **Schiemann (1990)**: Ternary Positive Definite Quadratic Forms are Determined by Their Theta Series
- **Conway-Sloane (1992)**: Four-Dimensional Lattices With the Same Theta Series
- **GVA**: https://github.com/zfifteen/z-sandbox
