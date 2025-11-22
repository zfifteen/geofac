# 127-Bit Challenge with Fractal-Segment Masking Experiment

## Objective

Attempt to factorize the 127-bit challenge semiprime using the PR #93 fractal-segment scoring mechanism ("Fractal Mask") to increase hit-probability on distant-factor semiprimes.

**Target:** N₁₂₇ = 137524771864208156028430259349934309717

**Known Factors (for verification):**
- p = 10508623501177419659
- q = 13086849276577416863

## Hypothesis Under Test

The fractal-segment masking mechanism from PR #93 provides segment-level discrimination that allows GVA to succeed on moderately distant-factor semiprimes by:

1. **Segment-level discrimination:** Only scan the most promising slices of the search band, not the entire band uniformly
2. **Hard filtering before candidate allocation:** Ensure no wastage on trivially invalid candidates (parity, small-prime divisibility, band constraints)
3. **Better budget compression:** For moderately distant factors, spending 80-90% of candidates on the "wrong half" kills vanilla GVA; PR #93 stops this
4. **GVA true resonance computation:** The fractal layer is guidance—not numerical contaminant

## Experimental Design

### Configuration Parameters

Per the technical memo recommendations:

**Segmenting:**
- Total segments: 64 (coarse)
- Top-K retained: 6–8
- Minimum random segments: 1 (mandatory coverage)

**Candidate Budget:**
- Max candidates: 650,000 (scaled from 125-bit 550k baseline)

**Precision:**
- 800 dps (127-bit requires 750-800, using 800 to avoid underflow)

**Valid Candidate Gates:**
- Parity check
- Small-prime sieve (first ~150 primes)
- Band boundaries (scaled to 127 bits)

**K-values for multi-sweep:**
- k ∈ {0.30, 0.35, 0.40}

### Success Indicators

The fractal mask is performing well if:
- window_coverage_pct < 15% at >100k candidates
- At least one segment with recurrent high scoring pattern across k-sweeps
- Candidate offsets clustering ≤ 200k around a specific band

### Abort Criteria

If 650k candidates reached without significant amplitude in any segment:
- Mask failed
- Would require rerun with top_k = 10

## Methodology

1. **Compute band:** Derive 127-bit search band around √N
2. **Fractal scoring pass:** Score all segments, log distribution
3. **Select top-K:** Choose 6–8 highest-scoring segments with enforced diversity
4. **GVA kernel sweep:** Run standard GVA within each segment (golden-ratio QMC, Dirichlet kernels, multi-k sweep)
5. **Validate:** Verify p·q = N₁₂₇, log metrics

### Metrics Tracked

- segments_scored: Number of segments evaluated
- segments_searched: Number of top-K segments searched
- candidates_tested: Actual candidates tested
- window_coverage_pct: Percentage of window covered
- hit_amplitude: Geodesic score at hit location (if found)
- segment_index: Which segment contained the factor (if found)

## Expected Outcome

Given:
- Pure GVA success at 125 bits with wide margin
- 130-bit almost ready
- Fractal mask preferentially eliminates dead zones
- 127-bit target only +2 bits over known success
- Known improvement for distant factors (PR #93)

→ Realistic to expect successful 127-bit factorization if factor gap is not pathological beyond mask's reach.

## Risk Assessment

**Primary risk:** Fractal mask points all top-K segments to wrong half of band
- Mitigation: Enforce mandatory coverage of 1-2 low-scoring segments by uniform spacing

**Secondary risk:** Kernel amplitude too weak when factors far from √N
- Mitigation: Allow multi-k scaling (0.28-0.40), increase inner window density by +10%

**Tertiary risk:** Precision underflow
- Mitigation: 800-850 dps eliminates this

## References

- PR #93 implementation: `experiments/fractal-recursive-gva-falsification/fr_gva_implementation.py`
- GVA baseline: `gva_factorization.py`
- Validation gates: `docs/VALIDATION_GATES.md`
- Coding standards: `CODING_STYLE.md`
