# SHA256 Hash-Bounds Simulation: Executive Summary

**HYPOTHESIS PARTIALLY VALIDATED — SPECIFIC CLAIMS FROM PR #165 NOT REPRODUCED**

## Conclusion

This experiment attempted to reproduce the findings from PR #165's 14-semiprime simulation. While the *general mechanism* of the attenuation adjustment formula works mathematically (achieving 100% error reduction when optimal attenuation is applied), the **specific numerical claims** from PR #165 could not be reproduced.

## Key Findings

### What We Found (Validated)

| Claim | Status | Details |
|-------|--------|---------|
| Error collapse to zero with optimal attenuation | ✓ VALIDATED | 100% of adjusted errors < ±0.1 |
| Improvement better than random baseline | ✓ VALIDATED | 100% improvement rate (all 14 test cases) |
| Variable optimal attenuation | ✓ VALIDATED | Range: -2.47 to +11.85 (wider than claimed) |

### What We Could NOT Reproduce (Falsified)

| Claim | Status | Expected | Observed |
|-------|--------|----------|----------|
| SHA_frac ↔ error: no linear correlation | ✗ FALSIFIED | r < 0.3 | r = -0.635 (moderate negative) |
| 127-bit SHA_frac ≈ 0.708 | ✗ FALSIFIED | 0.708 | 0.993 |
| 127-bit optimal atten ≈ -0.42 | ✗ FALSIFIED | -0.42 | +0.197 |
| RSA-100 SHA_frac ≈ 0.953 | ✗ FALSIFIED | 0.953 | 0.268 |
| RSA-100 optimal atten ≈ -0.42 | ✗ FALSIFIED | -0.42 | +3.04 |
| Bit-length scaling formula | ✗ FALSIFIED | r > 0.5 | r = 0.33 |

## Critical Observation

The discrepancy in SHA256 fractional values suggests that PR #165 may have used a **different encoding or hash computation method** than what we implemented. Our implementation:

1. Converts N to big-endian bytes
2. Computes SHA256 of those bytes
3. Interprets the hash as a 256-bit integer
4. Divides by 2^256 to get a value in [0, 1)

If PR #165 used a different representation (e.g., string encoding, different byte order, salt), the SHA_frac values would differ substantially—which matches our observations.

## Mathematical Truth

The attenuation formula **mathematically guarantees** perfect error correction when optimal attenuation is used:

```
err_adj = err_orig + (SHA_frac - 0.5) * atten

When atten = -err_orig / (SHA_frac - 0.5):
  err_adj = err_orig + (SHA_frac - 0.5) * [-err_orig / (SHA_frac - 0.5)]
  err_adj = err_orig - err_orig
  err_adj = 0
```

This is a **tautology**, not an empirical discovery. The formula is defined to make the adjusted error zero.

## Implications for Factorization

The hash-bounds adjustment provides **no predictive power** for factorization because:

1. **Optimal attenuation requires knowing err_orig**, which requires knowing the true factor position
2. **Fixed attenuation (-0.42)** worsens predictions in most cases (only 4/14 improved)
3. **No universal attenuation** exists that works across different semiprimes

## Test Cases

| Name | Bits | SHA_frac | Orig Error | Optimal Atten | Adj Error |
|------|------|----------|------------|---------------|-----------|
| 127-bit Challenge | 127 | 0.993 | -0.097 | +0.197 | 0.000 |
| RSA-100 | 330 | 0.268 | +0.705 | +3.041 | 0.000 |
| 50-bit Balanced | 50 | 0.722 | +0.278 | -1.249 | 0.000 |
| 60-bit Balanced | 60 | 0.964 | +0.036 | -0.077 | 0.000 |
| 80-bit Balanced | 80 | 0.644 | +0.356 | -2.470 | 0.000 |
| 100-bit Balanced | 100 | 0.047 | +0.953 | +2.105 | 0.000 |
| 100-bit Unbalanced | 101 | 0.581 | -0.581 | +7.181 | 0.000 |
| 80-bit Unbalanced | 81 | 0.259 | -0.259 | -1.071 | 0.000 |

## Reproducibility

- **Seed**: 42
- **Precision**: Adaptive (max(100, bit_length × 4 + 200))
- **127-bit Challenge**: 137524771864208156028430259349934309717
- **RSA-100**: 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
- **Timestamp**: 2025-11-28

## Files

- `simulation_runner.py` — Main simulation code
- `run_log.json` — Full results data
- `README.md` — Methodology details

---

*Experiment conducted following geofac validation gates: 127-bit challenge (whitelisted) + [10^14, 10^18] operational range. No classical fallbacks used.*
