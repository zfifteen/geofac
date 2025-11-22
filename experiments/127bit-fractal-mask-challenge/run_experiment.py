"""
127-Bit Challenge with Fractal-Segment Masking
================================================

Applies PR #93 fractal-segment scoring mechanism to the 127-bit challenge
semiprime. This extends the segment-based approach with parameters tuned
for the 127-bit scale and moderately distant factors.

Target: N₁₂₇ = 137524771864208156028430259349934309717
Known factors: p = 10508623501177419659, q = 13086849276577416863

Configuration per technical memo:
- Segments: 64
- Top-K: 6-8 with diversity enforcement
- Min random segments: 1
- Precision: 800 dps
- Max candidates: 650,000
- K-values: [0.30, 0.35, 0.40]
"""

import mpmath as mp
from typing import Tuple, Optional, List, Dict
import time
from math import log, e

# 127-bit challenge
CHALLENGE_127 = 137524771864208156028430259349934309717
EXPECTED_P = 10508623501177419659
EXPECTED_Q = 13086849276577416863

# Configuration for 127-bit run
SEGMENTS = 64
TOP_K = 8
MIN_RANDOM_SEGMENTS = 1
PRECISION = 800
MAX_CANDIDATES = 650000
K_VALUES = [0.30, 0.35, 0.40]

# Segment scoring parameters
RELATIVE_POS_SCALE = 0.1
LOG_N_SCALE = 1e-20
ESCAPE_WEIGHT = 0.6
MAGNITUDE_WEIGHT = 0.4
MAGNITUDE_SCALE = 10.0
MANDELBROT_ITERATIONS = 100
ESCAPE_RADIUS = 2.0

# Prefilter: first 150 primes
SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
    421, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509,
    521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613,
    617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709,
    719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821,
    823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887
]


def embed_torus_geodesic(n: int, k: float, dimensions: int = 7) -> List[mp.mpf]:
    """Embed integer n into 7D torus using geodesic mapping."""
    phi = mp.mpf(1 + mp.sqrt(5)) / 2
    coords = []
    for d in range(dimensions):
        phi_power = phi ** (d + 1)
        coord = mp.fmod(n * phi_power, 1)
        if k != 1.0:
            coord = mp.power(coord, k)
            coord = mp.fmod(coord, 1)
        coords.append(coord)
    return coords


def riemannian_distance(p1: List[mp.mpf], p2: List[mp.mpf]) -> mp.mpf:
    """Compute Riemannian geodesic distance on 7D torus."""
    if len(p1) != len(p2):
        raise ValueError("Points must have same dimension")
    dist_sq = mp.mpf(0)
    for c1, c2 in zip(p1, p2):
        diff = abs(c1 - c2)
        wrap_diff = mp.mpf(1) - diff
        min_diff = min(diff, wrap_diff)
        dist_sq += min_diff * min_diff
    return mp.sqrt(dist_sq)


def is_valid_candidate(candidate: int, N: int, sqrt_N: int, 
                       n_prime_factors: set) -> bool:
    """
    Hard prefilter for candidate validity.
    Checks: parity, small-prime divisibility, band constraints.
    """
    if candidate <= 1 or candidate >= N:
        return False
    
    # Parity check
    if N % 2 == 1 and candidate % 2 == 0:
        return False
    
    # Small prime divisibility (first 150 primes)
    for prime in SMALL_PRIMES:
        if prime >= candidate:
            break
        if prime in n_prime_factors:
            continue
        if candidate % prime == 0:
            return False
    
    return True


def score_segment_with_mandelbrot(segment_start: int, segment_end: int, 
                                   N: int, sqrt_N: int) -> float:
    """
    Compute Mandelbrot-based interest score for a segment.
    Uses monotone mapping that preserves locality.
    """
    segment_center = (segment_start + segment_end) // 2
    relative_pos = (segment_center - sqrt_N) / sqrt_N if sqrt_N > 0 else 0
    
    # Kappa approximation for large semiprime
    kappa = 0.5  # Simplified for 127-bit
    
    c = complex(kappa + relative_pos * RELATIVE_POS_SCALE, 
                log(N) * LOG_N_SCALE)
    
    z = 0j
    escape_count = 0
    total_magnitude = 0.0
    
    for iteration in range(MANDELBROT_ITERATIONS):
        z = z**2 + c
        magnitude = abs(z)
        total_magnitude += magnitude
        
        if magnitude > ESCAPE_RADIUS:
            escape_count += 1
            z = z / (magnitude / ESCAPE_RADIUS)
    
    avg_magnitude = total_magnitude / MANDELBROT_ITERATIONS
    escape_ratio = escape_count / MANDELBROT_ITERATIONS
    
    score = (escape_ratio * ESCAPE_WEIGHT + 
             min(avg_magnitude / MAGNITUDE_SCALE, 1.0) * MAGNITUDE_WEIGHT)
    
    return min(score, 1.0)


def select_diverse_segments(segment_scores: List[Tuple[float, int, int]], 
                            top_k: int, min_separation: int) -> List[Tuple[float, int, int]]:
    """
    Select top-K segments with diversity enforcement.
    Ensures segments are not overly adjacent.
    """
    if not segment_scores:
        return []
    
    selected = []
    segment_scores_sorted = sorted(segment_scores, reverse=True, key=lambda x: x[0])
    
    for score, start, end in segment_scores_sorted:
        if len(selected) >= top_k:
            break
        
        # Check separation from already selected segments
        too_close = False
        for _, sel_start, sel_end in selected:
            # Check if segments overlap or are too close
            if abs(start - sel_start) < min_separation:
                too_close = True
                break
        
        if not too_close:
            selected.append((score, start, end))
    
    return selected


def search_segment_with_gva(N: int, sqrt_N: int, N_coords: List[mp.mpf], 
                            k: float, segment_start: int, segment_end: int,
                            n_prime_factors: set, metrics: Dict, 
                            verbose: bool = False) -> Optional[Tuple[int, int]]:
    """
    Search a segment using GVA geodesic-guided approach.
    """
    candidates_with_dist = []
    
    # Sample candidates in segment with adaptive stride
    segment_size = segment_end - segment_start
    stride = max(1, segment_size // 1000)
    
    for candidate in range(segment_start, segment_end, stride):
        if not is_valid_candidate(candidate, N, sqrt_N, n_prime_factors):
            continue
        
        # Compute geodesic distance
        cand_coords = embed_torus_geodesic(candidate, k)
        dist = riemannian_distance(N_coords, cand_coords)
        
        candidates_with_dist.append((float(dist), candidate))
    
    # Sort by distance
    candidates_with_dist.sort()
    
    # Test top candidates
    for dist, candidate in candidates_with_dist:
        if metrics['candidates_tested'] >= MAX_CANDIDATES:
            break
        
        metrics['candidates_tested'] += 1
        
        if N % candidate == 0:
            if verbose:
                print(f"    ✓ Factor found: {candidate} (distance: {dist:.6f})")
            return (candidate, N // candidate)
    
    return None


def run_127bit_challenge(verbose: bool = True) -> Optional[Tuple[int, int]]:
    """
    Execute 127-bit challenge with fractal-segment masking.
    """
    N = CHALLENGE_127
    
    print("=" * 70)
    print("127-Bit Challenge with Fractal-Segment Masking")
    print("=" * 70)
    print(f"N = {N}")
    print(f"Bit length: {N.bit_length()}")
    print(f"Expected factors: {EXPECTED_P} × {EXPECTED_Q}")
    print()
    print("Configuration:")
    print(f"  Segments: {SEGMENTS}")
    print(f"  Top-K: {TOP_K}")
    print(f"  Min random segments: {MIN_RANDOM_SEGMENTS}")
    print(f"  Precision: {PRECISION} dps")
    print(f"  Max candidates: {MAX_CANDIDATES:,}")
    print(f"  K-values: {K_VALUES}")
    print(f"  Prefilters: parity, first {len(SMALL_PRIMES)} primes, band")
    print()
    
    # Set precision
    mp.mp.dps = PRECISION
    
    with mp.workdps(PRECISION):
        start_time = time.time()
        
        # Compute search band
        sqrt_N = int(mp.sqrt(N))
        
        # For 127-bit, use expanded window
        # Based on 125-bit ladder, scale up slightly
        bit_length = N.bit_length()
        window = max(800000, sqrt_N // 150)
        
        window_start = max(2, sqrt_N - window)
        window_end = min(N - 1, sqrt_N + window)
        
        print(f"Search band:")
        print(f"  sqrt(N) = {sqrt_N}")
        print(f"  Window: [{window_start}, {window_end}]")
        print(f"  Window size: ±{window:,}")
        print()
        
        # Pre-compute N's prime factors
        n_prime_factors = {p for p in SMALL_PRIMES if N % p == 0}
        
        # Phase 1: Score all segments
        print(f"Phase 1: Scoring {SEGMENTS} segments...")
        segment_size = (window_end - window_start) // SEGMENTS
        segment_scores = []
        
        for i in range(SEGMENTS):
            seg_start = window_start + i * segment_size
            seg_end = seg_start + segment_size if i < SEGMENTS - 1 else window_end
            
            score = score_segment_with_mandelbrot(seg_start, seg_end, N, sqrt_N)
            segment_scores.append((score, seg_start, seg_end))
        
        # Sort and show distribution
        segment_scores_sorted = sorted(segment_scores, reverse=True, key=lambda x: x[0])
        
        print(f"Segment score distribution:")
        print(f"  Top score: {segment_scores_sorted[0][0]:.4f}")
        print(f"  Median score: {segment_scores_sorted[len(segment_scores_sorted)//2][0]:.4f}")
        print(f"  Bottom score: {segment_scores_sorted[-1][0]:.4f}")
        print()
        
        # Phase 2: Select top-K segments with diversity
        print(f"Phase 2: Selecting top-{TOP_K} segments with diversity...")
        min_separation = segment_size * 2  # Enforce at least 2-segment gap
        selected_segments = select_diverse_segments(segment_scores_sorted, TOP_K, min_separation)
        
        # Add random low-scoring segments for coverage
        remaining = [s for s in segment_scores_sorted if s not in selected_segments]
        if remaining and MIN_RANDOM_SEGMENTS > 0:
            # Pick from bottom half by uniform spacing
            bottom_half = remaining[len(remaining)//2:]
            step = max(1, len(bottom_half) // MIN_RANDOM_SEGMENTS)
            for i in range(0, len(bottom_half), step):
                if len(selected_segments) >= TOP_K + MIN_RANDOM_SEGMENTS:
                    break
                selected_segments.append(bottom_half[i])
        
        print(f"Selected {len(selected_segments)} segments:")
        for i, (score, start, end) in enumerate(selected_segments):
            offset_start = start - sqrt_N
            offset_end = end - sqrt_N
            print(f"  {i+1}. Score={score:.4f}, range=[{offset_start:+,} to {offset_end:+,}]")
        print()
        
        # Calculate coverage
        covered = sum(end - start for _, start, end in selected_segments)
        total = window_end - window_start
        coverage_pct = (covered / total * 100) if total > 0 else 0
        
        print(f"Window coverage: {coverage_pct:.2f}%")
        print()
        
        # Initialize metrics
        metrics = {
            'segments_scored': len(segment_scores),
            'segments_searched': 0,
            'candidates_tested': 0,
            'window_coverage_pct': coverage_pct
        }
        
        # Phase 3: Multi-k sweep over selected segments
        print(f"Phase 3: GVA kernel sweep over selected segments...")
        
        for k in K_VALUES:
            print(f"\nTesting k = {k}")
            
            # Embed N in 7D torus
            N_coords = embed_torus_geodesic(N, k)
            
            for seg_idx, (score, seg_start, seg_end) in enumerate(selected_segments):
                if metrics['candidates_tested'] >= MAX_CANDIDATES:
                    print(f"  Reached max candidates limit")
                    break
                
                metrics['segments_searched'] += 1
                
                if verbose:
                    offset = seg_start - sqrt_N
                    print(f"  Searching segment {seg_idx+1} (offset {offset:+,}, score {score:.4f})...")
                
                result = search_segment_with_gva(N, sqrt_N, N_coords, k, 
                                                seg_start, seg_end,
                                                n_prime_factors, metrics, verbose)
                
                if result:
                    elapsed = time.time() - start_time
                    p, q = result
                    
                    print()
                    print("=" * 70)
                    print("✓ FACTOR FOUND!")
                    print("=" * 70)
                    print(f"N = {N}")
                    print(f"p = {p}")
                    print(f"q = {q}")
                    print(f"Verification: p × q = {p * q}")
                    print(f"Match: {p * q == N}")
                    print()
                    print(f"Details:")
                    print(f"  k-value: {k}")
                    print(f"  Segment index: {seg_idx + 1}")
                    print(f"  Segment score: {score:.4f}")
                    print(f"  Time elapsed: {elapsed:.3f}s")
                    print()
                    print(f"Metrics:")
                    print(f"  Segments scored: {metrics['segments_scored']}")
                    print(f"  Segments searched: {metrics['segments_searched']}")
                    print(f"  Candidates tested: {metrics['candidates_tested']:,}")
                    print(f"  Window coverage: {metrics['window_coverage_pct']:.2f}%")
                    print("=" * 70)
                    
                    return result
            
            if metrics['candidates_tested'] >= MAX_CANDIDATES:
                break
        
        # No factor found
        elapsed = time.time() - start_time
        print()
        print("=" * 70)
        print("✗ NO FACTOR FOUND")
        print("=" * 70)
        print(f"Time elapsed: {elapsed:.3f}s")
        print()
        print(f"Final Metrics:")
        print(f"  Segments scored: {metrics['segments_scored']}")
        print(f"  Segments searched: {metrics['segments_searched']}")
        print(f"  Candidates tested: {metrics['candidates_tested']:,}")
        print(f"  Window coverage: {metrics['window_coverage_pct']:.2f}%")
        print("=" * 70)
        
        return None


def main():
    """Run the 127-bit challenge experiment."""
    result = run_127bit_challenge(verbose=True)
    
    if result:
        p, q = result
        expected_match = {p, q} == {EXPECTED_P, EXPECTED_Q}
        
        print()
        print("Validation:")
        print(f"  Expected: {EXPECTED_P} × {EXPECTED_Q}")
        print(f"  Found: {p} × {q}")
        print(f"  Match: {expected_match}")
        
        return 0 if expected_match else 1
    else:
        print()
        print("Experiment conclusion: Fractal mask insufficient for this configuration.")
        print("Next steps: Try top_k=10 or expand window further.")
        return 1


if __name__ == "__main__":
    exit(main())
