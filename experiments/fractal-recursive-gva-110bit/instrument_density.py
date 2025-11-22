"""
Instrument candidate density vs radius for 110-bit GVA baseline.

This tool logs the distribution of candidate geodesic distances across
different radii from sqrt(N), helping understand the fractal structure
and inform coarse-to-fine search strategies.

Target: N = 1296000000000003744000000000001183 (110 bits)
Expected: p=36000000000000013, q=36000000000000091 (gap=78)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import mpmath as mp
from gva_factorization import embed_torus_geodesic, riemannian_distance, adaptive_precision
import time
import json

# Configure test parameters
N = 1296000000000003744000000000001183
EXPECTED_P = 36000000000000013
EXPECTED_Q = 36000000000000091
K = 0.30  # Pin k value for consistency

# 110-bit parameters from gva_factorization.py
BASE_WINDOW = 600000
ULTRA_INNER_BOUND = 300
INNER_BOUND = 30000
MIDDLE_BOUND = 300000

# Segment configuration for density analysis
NUM_SEGMENTS = 32  # Divide window into segments
SAMPLES_PER_SEGMENT = 50


def analyze_density_profile():
    """
    Analyze candidate density distribution across radial segments.
    
    Returns:
        Dictionary with density metrics and segment-wise statistics.
    """
    print("=" * 70)
    print("GVA Density Profile Analysis: 110-bit")
    print("=" * 70)
    print(f"N = {N}")
    print(f"Bit length: {N.bit_length()}")
    print(f"Expected factors: {EXPECTED_P} × {EXPECTED_Q}")
    print(f"Factor gap: {EXPECTED_Q - EXPECTED_P}")
    print(f"k = {K}")
    print(f"Base window: ±{BASE_WINDOW}")
    print(f"Segments: {NUM_SEGMENTS}")
    print(f"Samples per segment: {SAMPLES_PER_SEGMENT}")
    print("=" * 70)
    print()
    
    # Set adaptive precision
    required_dps = adaptive_precision(N)
    mp.mp.dps = required_dps
    print(f"Adaptive precision: {required_dps} dps")
    print()
    
    sqrt_N = int(mp.sqrt(N))
    print(f"sqrt(N) = {sqrt_N}")
    print(f"Factor offset from sqrt(N): p={EXPECTED_P - sqrt_N}, q={EXPECTED_Q - sqrt_N}")
    print()
    
    start_time = time.time()
    
    # Embed N in 7D torus
    N_coords = embed_torus_geodesic(N, K)
    
    # Define segments: divide [-BASE_WINDOW, +BASE_WINDOW] into NUM_SEGMENTS
    segment_width = (2 * BASE_WINDOW) // NUM_SEGMENTS
    
    print(f"Segment width: {segment_width}")
    print()
    print("Analyzing segments...")
    print()
    
    segment_stats = []
    
    for seg_idx in range(NUM_SEGMENTS):
        # Segment boundaries
        seg_start = -BASE_WINDOW + seg_idx * segment_width
        seg_end = seg_start + segment_width
        seg_center = (seg_start + seg_end) // 2
        
        # Sample uniformly within segment
        step = max(1, segment_width // SAMPLES_PER_SEGMENT)
        
        distances = []
        candidates = []
        
        for i in range(SAMPLES_PER_SEGMENT):
            offset = seg_start + i * step
            candidate = sqrt_N + offset
            
            # Skip invalid candidates
            if candidate <= 1 or candidate >= N:
                continue
            
            # Ensure odd candidate
            if candidate % 2 == 0:
                candidate += 1
            
            # Skip small prime factors (but don't skip everything)
            # For large numbers, most won't have these factors anyway
            
            # Compute geodesic distance
            cand_coords = embed_torus_geodesic(candidate, K)
            dist = float(riemannian_distance(N_coords, cand_coords))
            
            distances.append(dist)
            candidates.append(candidate)
            
            # Check if this is one of the expected factors
            if candidate == EXPECTED_P or candidate == EXPECTED_Q:
                print(f"  ✓ Factor found in segment {seg_idx}: offset={offset}, dist={dist:.6f}")
        
        if distances:
            min_dist = min(distances)
            max_dist = max(distances)
            avg_dist = sum(distances) / len(distances)
            
            # Check if segment contains a factor
            contains_factor = any(c in [EXPECTED_P, EXPECTED_Q] for c in candidates)
            
            segment_stats.append({
                'segment_index': seg_idx,
                'offset_range': [seg_start, seg_end],
                'center_offset': seg_center,
                'num_samples': len(distances),
                'min_distance': min_dist,
                'max_distance': max_dist,
                'avg_distance': avg_dist,
                'contains_factor': contains_factor,
            })
    
    elapsed = time.time() - start_time
    
    # Sort segments by min distance
    segment_stats.sort(key=lambda s: s['min_distance'])
    
    print()
    print("=" * 70)
    print("Segment Ranking by Min Geodesic Distance")
    print("=" * 70)
    print(f"{'Rank':<6} {'Seg':<5} {'Center':<10} {'Min Dist':<12} {'Avg Dist':<12} {'Factor?':<8}")
    print("-" * 70)
    
    for rank, seg in enumerate(segment_stats, 1):
        factor_mark = "YES" if seg['contains_factor'] else "no"
        print(f"{rank:<6} {seg['segment_index']:<5} {seg['center_offset']:<10} "
              f"{seg['min_distance']:<12.6f} {seg['avg_distance']:<12.6f} {factor_mark:<8}")
    
    print()
    print("=" * 70)
    print("Analysis Summary")
    print("=" * 70)
    
    # Find which rank contains the factors
    factor_segments = [s for s in segment_stats if s['contains_factor']]
    if factor_segments:
        factor_ranks = [segment_stats.index(s) + 1 for s in factor_segments]
        print(f"Segments containing factors: rank {factor_ranks}")
        print(f"Top-N needed to capture factors: {max(factor_ranks)}")
        coverage_percent = (max(factor_ranks) / NUM_SEGMENTS) * 100
        print(f"Window coverage needed: {coverage_percent:.1f}%")
    else:
        print("WARNING: Factors not found in sampled segments")
    
    print(f"Total segments: {NUM_SEGMENTS}")
    print(f"Samples per segment: {SAMPLES_PER_SEGMENT}")
    print(f"Total samples: {sum(s['num_samples'] for s in segment_stats)}")
    print(f"Analysis time: {elapsed:.3f}s")
    print()
    
    # Save results to JSON
    results = {
        'metadata': {
            'N': str(N),
            'bit_length': N.bit_length(),
            'expected_p': EXPECTED_P,
            'expected_q': EXPECTED_Q,
            'factor_gap': EXPECTED_Q - EXPECTED_P,
            'k': K,
            'base_window': BASE_WINDOW,
            'sqrt_N': sqrt_N,
            'precision_dps': required_dps,
            'num_segments': NUM_SEGMENTS,
            'samples_per_segment': SAMPLES_PER_SEGMENT,
            'elapsed_seconds': elapsed,
        },
        'segments': segment_stats,
    }
    
    output_path = '/home/runner/work/geofac/geofac/experiments/fractal-recursive-gva-110bit/density_profile.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: density_profile.json")
    print()
    
    return results


if __name__ == "__main__":
    analyze_density_profile()
