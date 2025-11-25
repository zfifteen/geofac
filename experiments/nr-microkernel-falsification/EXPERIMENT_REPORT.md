# NR Microkernel Falsification Experiment Report

**Date**: 2025-11-25T13:50:39.377413

## Executive Summary

**VERDICT: HYPOTHESIS FALSIFIED**

The hypothesis that embedding a Newton-Raphson microkernel inside QMC iterations
improves resonance scan peak detection has been **falsified**.

Key findings:
- **Excessive runtime overhead**: NR(1) = 60.0%, NR(2) = 112.1%
- **Low improvement rate**: NR(1) = 2.2%, NR(2) = 2.2%
- **Majority showed no benefit**: 3/4 criteria met

## Overall Statistics

- **Test cases**: 4
- **Baseline successes**: 4/4
- **NR(1) successes**: 4/4
- **NR(2) successes**: 4/4

### Runtime
- **NR(1) average overhead**: 60.0%
- **NR(2) average overhead**: 112.1%

### Score Analysis
- **NR(1) average score lift**: 1.73%
- **NR(2) average score lift**: 1.73%

### NR Refinement Activity
- **NR(1) total triggers**: 91
- **NR(1) total improvements**: 2
- **NR(1) improvement rate**: 2.2%
- **NR(2) total triggers**: 91
- **NR(2) total improvements**: 2
- **NR(2) improvement rate**: 2.2%

## Per-Test Results

| Test Case | Baseline | NR(1) | NR(2) | NR(1) Overhead | NR(2) Overhead | NR(1) Lift | NR(2) Lift |
|-----------|----------|-------|-------|----------------|----------------|------------|------------|
| Gate 1 (30-bit) | ✓ | ✓ | ✓ | 28.1% | 71.7% | 0.00% | 0.00% |
| Gate 2 (60-bit) | ✓ | ✓ | ✓ | 65.3% | 118.5% | 6.92% | 6.92% |
| Verified 50-bit | ✓ | ✓ | ✓ | 73.1% | 131.2% | 0.00% | 0.00% |
| Verified 64-bit | ✓ | ✓ | ✓ | 73.3% | 127.1% | 0.00% | 0.00% |

## Falsification Criteria Assessment

| Criterion | Met | Details |
|-----------|-----|---------|
| No significant score lift (<1%) | ✗ | NR(1): 1.73%, NR(2): 1.73% |
| Excessive overhead (>15%) | ✓ | NR(1): 60.0%, NR(2): 112.1% |
| Low improvement rate (<20%) | ✓ | NR(1): 2.2%, NR(2): 2.2% |
| Majority no benefit (≥2/3) | ✓ | 3/4 tests |

**Criteria met**: 3/4 (threshold: 2)

## Methodology

### Experiment Design
- **Treatments**: Baseline (NR disabled), NR(1) - 1 step, NR(2) - 2 steps
- **Trigger**: z-score ≥ 1.5 OR top 5% of candidates
- **Tolerance**: Stop early if relative improvement < 1e-6
- **Budget**: Max 64 refines per batch

### Test Cases
1. Gate 1 (30-bit): 1073217479 = 32749 × 32771
2. Gate 2 (60-bit): 1152921470247108503 = 1073741789 × 1073741827
3. Verified 50-bit: 1125899772623531 = 33554393 × 33554467
4. Verified 64-bit: 18446736050711510819 = 4294966297 × 4294966427

### Key Constraints
- No classical fallbacks (pure geometric resonance)
- Deterministic (fixed seeds, fixed NR step budget)
- Same precision path for NR as main scoring

## Reproducibility

Run the experiment:
```bash
cd experiments/nr-microkernel-falsification
python3 experiment_runner.py
```
