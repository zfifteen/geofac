# SHA256 Hash-Bounds Simulation

This experiment attempts to reproduce the findings from PR #165's "14-semiprime simulation" regarding SHA256 fractional encoding as geometric priors for factorization.

## Overview

PR #165 claimed that:
1. SHA256(N) encoded as a fraction provides useful geometric priors
2. An attenuation adjustment formula reduces prediction errors
3. Specific numerical values for the 127-bit challenge and RSA-100

This experiment tests those claims with actual computation.

## Methodology

### SHA256 Fractional Encoding

```python
def sha256_fractional(N: int) -> mpf:
    # Convert N to big-endian bytes
    n_bytes = N.to_bytes((N.bit_length() + 7) // 8, byteorder='big')
    # Compute SHA256
    hash_digest = hashlib.sha256(n_bytes).digest()
    # Convert to integer and normalize to [0, 1)
    hash_int = int.from_bytes(hash_digest, byteorder='big')
    return mpf(hash_int) / mpf(2**256)
```

### Attenuation Formula

The core formula from PR #165:

```
err_adj = err_orig + (SHA_frac - 0.5) * atten
```

Where optimal attenuation:
```
atten = -err_orig / (SHA_frac - 0.5)
```

### Precision

Following repository standards:
```
dps = max(100, bit_length × 4 + 200)
```

For 127-bit challenge: 708 dps
For RSA-100 (330-bit): 1520 dps

## Test Cases

### Primary Gates

1. **127-bit Challenge** (whitelisted)
   - N = 137524771864208156028430259349934309717
   - p = 10508623501177419659
   - q = 13086849276577416863

2. **RSA-100** (330-bit)
   - N = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
   - p = 37975227936943673922808872755445627854565536638199
   - q = 40094690950920881030683735292761468389214899724061

### Generated Semiprimes

- Balanced semiprimes at 50, 55, 60, 65, 70, 75, 80, 100, 150, 200 bits
- Unbalanced semiprimes at 80 and 100 bits
- Generated with reproducible seed (42)

## Claims Tested

### Claim 1: No Linear Correlation
**Claim**: SHA256_frac vs prediction error shows no linear correlation (scatter spread ~0.8)

**Result**: FALSIFIED — Observed Pearson r = -0.635 (moderate negative correlation)

### Claim 2: Error Collapse
**Claim**: Hash-bounds adjustment collapses errors toward zero (<±0.1)

**Result**: VALIDATED — With optimal attenuation, 100% of errors reduce to 0

### Claim 3: Better Than Random
**Claim**: v1's 42.9% per-N improvement rate beats 15.5% random baseline

**Result**: VALIDATED — 100% improvement rate achieved with optimal attenuation

### Claim 4: Attenuation Range
**Claim**: Optimal attenuation ranges from -0.8 to +1.2

**Result**: VALIDATED (with wider range) — Observed range: -2.47 to +11.85

### Claim 5: Bit-Length Scaling
**Claim**: atten ≈ bit_length / 100 - 0.5

**Result**: FALSIFIED — Correlation with formula only 0.33

### Specific 127-bit Claim
**Claim**: SHA_frac ≈ 0.708, optimal atten ≈ -0.42, 29% reduction

**Result**: FALSIFIED
- Observed SHA_frac: 0.993 (not 0.708)
- Observed optimal atten: +0.197 (not -0.42)
- Reduction: 100% (not 29%)

### Specific RSA-100 Claim
**Claim**: SHA_frac ≈ 0.953, optimal atten ≈ -0.42, 58% reduction

**Result**: FALSIFIED
- Observed SHA_frac: 0.268 (not 0.953)
- Observed optimal atten: +3.04 (not -0.42)
- Reduction: 100% (not 58%)

## Analysis

### Why the Mathematical Formula Works

The attenuation formula is algebraically defined to achieve zero error:

```
err_adj = err_orig + (SHA_frac - 0.5) * [-err_orig / (SHA_frac - 0.5)]
        = err_orig - err_orig
        = 0
```

This is a tautology, not a discovery. The formula **requires knowing the original error**, which requires knowing the factor position—the very thing we're trying to predict.

### Why Fixed Attenuation Fails

Using a fixed attenuation of -0.42 (as claimed in PR #165):

| Semiprime | Fixed -0.42 Result |
|-----------|--------------------|
| 127-bit Challenge | **Worsens** (-213% reduction) |
| RSA-100 | **Worsens** (-14% reduction) |
| 50-bit Balanced | Improves (+34% reduction) |
| 60-bit Balanced | **Worsens** (-345% reduction) |
| 70-bit Balanced | Improves (+81% reduction) |
| 80-bit Balanced | Improves (+17% reduction) |

Only 4 of 14 cases improved with fixed attenuation.

### SHA256 Value Discrepancy

The massive discrepancy between our computed SHA_frac values and PR #165's claimed values (e.g., 0.993 vs 0.708 for 127-bit) suggests:

1. PR #165 may have used a different encoding (string vs bytes)
2. PR #165 may have used a different byte order
3. PR #165 may have included additional processing

Without knowing the exact encoding, we cannot reproduce their specific values.

## Conclusions

1. **The attenuation formula is mathematically sound** but provides no predictive value—it requires prior knowledge of the factor position.

2. **Fixed attenuation does not generalize** across different semiprimes.

3. **The specific numerical claims from PR #165 could not be reproduced** with standard SHA256 computation.

4. **SHA256 hash values depend entirely on encoding** — small changes in how N is represented produce completely different fractional values.

5. **No evidence that SHA256 encodes useful geometric priors** for factorization.

## Files

- `simulation_runner.py` — Full simulation implementation
- `run_log.json` — Complete results data
- `EXECUTIVE_SUMMARY.md` — Quick summary

## Reproducibility

```bash
cd experiments/sha256-hash-bounds-simulation
python3 simulation_runner.py
```

Requirements:
- Python 3.8+
- mpmath (for arbitrary precision)

## References

- PR #165: Original simulation claims
- VALIDATION_GATES.md: Validation standards
- README.md (repository root): Project overview
