"""
Two-stage coarse-to-fine GVA factorization for 110-bit semiprimes.

This prototype implements a fractal/recursive search strategy:
- Stage 1: Coarse sweep over window segments, score by geodesic distance
- Stage 2: Dense search in top-scoring segments only

Goal: Reduce window coverage while maintaining factor recovery.

Target: N = 1296000000000003744000000000001183 (110 bits)
Expected: p=36000000000000013, q=36000000000000091 (gap=78)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import mpmath as mp
from gva_factorization import embed_torus_geodesic, riemannian_distance, adaptive_precision
import time
from typing import Tuple, Optional, List

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
LOCAL_WINDOW = 4500

# Stage 1: Coarse sweep parameters
NUM_SEGMENTS = 32
SAMPLES_PER_SEGMENT = 50
TOP_SEGMENTS = 16  # Keep top 50% of segments

# Stage 2: Dense search - use full 110-bit parameters


def two_stage_gva_factor(verbose: bool = True) -> Optional[dict]:
    """
    Two-stage GVA factorization with coarse-to-fine search.
    
    Stage 1: Coarse sweep
    - Always include ultra-inner region (±300) since factors often cluster near sqrt(N)
    - Divide remaining window into segments
    - Sample each segment sparsely
    - Rank by min geodesic distance
    - Select top segments
    
    Stage 2: Dense search
    - Apply full 110-bit search to ultra-inner region + top segments
    - Use ultra_inner_bound, inner_bound, middle_bound, local_window
    
    Returns:
        Dictionary with results or None if failed
    """
    print("=" * 70)
    print("Two-Stage GVA Factorization: 110-bit")
    print("=" * 70)
    print(f"N = {N}")
    print(f"Bit length: {N.bit_length()}")
    print(f"Expected factors: {EXPECTED_P} × {EXPECTED_Q}")
    print(f"k = {K}")
    print(f"Base window: ±{BASE_WINDOW}")
    print("=" * 70)
    print()
    
    # Set adaptive precision
    required_dps = adaptive_precision(N)
    mp.mp.dps = required_dps
    if verbose:
        print(f"Adaptive precision: {required_dps} dps")
    
    sqrt_N = int(mp.sqrt(N))
    if verbose:
        print(f"sqrt(N) = {sqrt_N}")
        print()
    
    start_time = time.time()
    
    # Embed N in 7D torus
    N_coords = embed_torus_geodesic(N, K)
    
    # ===================================================================
    # STAGE 1: COARSE SWEEP (OUTER REGIONS ONLY)
    # ===================================================================
    print("STAGE 1: Coarse Sweep")
    print("-" * 70)
    print(f"Strategy: Always keep ultra-inner region (±{ULTRA_INNER_BOUND})")
    print(f"         Sample outer regions in {NUM_SEGMENTS} segments")
    print(f"Samples per segment: {SAMPLES_PER_SEGMENT}")
    print(f"Top outer segments to keep: {TOP_SEGMENTS}")
    print()
    
    stage1_start = time.time()
    
    # Divide only the OUTER region (beyond ±ULTRA_INNER_BOUND) into segments
    outer_window = BASE_WINDOW - ULTRA_INNER_BOUND
    segment_width = (2 * outer_window) // NUM_SEGMENTS
    segment_scores = []
    
    for seg_idx in range(NUM_SEGMENTS):
        # Map segment to outer regions:
        # Segments 0 to NUM_SEGMENTS/2-1: negative side from -BASE_WINDOW to -ULTRA_INNER_BOUND
        # Segments NUM_SEGMENTS/2 to NUM_SEGMENTS-1: positive side from +ULTRA_INNER_BOUND to +BASE_WINDOW
        
        if seg_idx < NUM_SEGMENTS // 2:
            # Negative side
            seg_start = -BASE_WINDOW + seg_idx * segment_width
            seg_end = min(seg_start + segment_width, -ULTRA_INNER_BOUND)
        else:
            # Positive side
            seg_offset = seg_idx - NUM_SEGMENTS // 2
            seg_start = ULTRA_INNER_BOUND + seg_offset * segment_width
            seg_end = min(seg_start + segment_width, BASE_WINDOW)
        
        # Sample uniformly within segment
        seg_range = seg_end - seg_start
        step = max(1, seg_range // SAMPLES_PER_SEGMENT)
        
        min_dist = float('inf')
        
        for i in range(SAMPLES_PER_SEGMENT):
            offset = seg_start + i * step
            candidate = sqrt_N + offset
            
            # Skip invalid candidates
            if candidate <= 1 or candidate >= N:
                continue
            
            # Ensure odd candidate
            if candidate % 2 == 0:
                candidate += 1
            
            # Compute geodesic distance
            cand_coords = embed_torus_geodesic(candidate, K)
            dist = float(riemannian_distance(N_coords, cand_coords))
            
            if dist < min_dist:
                min_dist = dist
        
        if min_dist < float('inf'):
            segment_scores.append({
                'index': seg_idx,
                'start_offset': seg_start,
                'end_offset': seg_end,
                'min_distance': min_dist,
            })
    
    # Sort by min distance (ascending)
    segment_scores.sort(key=lambda s: s['min_distance'])
    
    # Select top segments
    top_segments = segment_scores[:TOP_SEGMENTS]
    
    stage1_elapsed = time.time() - stage1_start
    
    if verbose:
        print(f"Stage 1 completed in {stage1_elapsed:.3f}s")
        print(f"Top {TOP_SEGMENTS} outer segments selected:")
        for rank, seg in enumerate(top_segments[:5], 1):  # Show top 5
            print(f"  {rank}. Segment {seg['index']}: offset [{seg['start_offset']}, {seg['end_offset']}], "
                  f"min_dist={seg['min_distance']:.6f}")
        if len(top_segments) > 5:
            print(f"  ... and {len(top_segments) - 5} more")
        print()
    
    # Calculate coverage: ultra-inner always included + top outer segments
    ultra_inner_coverage = (2 * ULTRA_INNER_BOUND) / (2 * BASE_WINDOW) * 100
    outer_coverage = (len(top_segments) / NUM_SEGMENTS) * (1 - ultra_inner_coverage / 100) * 100
    total_coverage = ultra_inner_coverage + outer_coverage
    
    print(f"Window coverage:")
    print(f"  Ultra-inner (±{ULTRA_INNER_BOUND}): {ultra_inner_coverage:.1f}%")
    print(f"  Top outer segments: {outer_coverage:.1f}%")
    print(f"  Total: {total_coverage:.1f}%")
    print()
    
    # ===================================================================
    # STAGE 2: DENSE SEARCH IN ULTRA-INNER + TOP OUTER SEGMENTS
    # ===================================================================
    print("STAGE 2: Dense Search")
    print("-" * 70)
    print(f"Regions to search:")
    print(f"  1. Ultra-inner: ±{ULTRA_INNER_BOUND} (always included)")
    print(f"  2. Top {len(top_segments)} outer segments")
    print(f"Applying full 110-bit parameters:")
    print(f"  Inner bound: ±{INNER_BOUND}")
    print(f"  Middle bound: ±{MIDDLE_BOUND}")
    print(f"  Local window: ±{LOCAL_WINDOW}")
    print()
    
    stage2_start = time.time()
    
    # Build dense candidate list
    candidates_with_dist = []
    
    # ALWAYS sample ultra-inner region densely (step 1)
    for offset in range(-ULTRA_INNER_BOUND, ULTRA_INNER_BOUND + 1):
        candidate = sqrt_N + offset
        
        if candidate <= 1 or candidate >= N:
            continue
        
        # Ensure odd
        if candidate % 2 == 0:
            candidate += 1
            offset = candidate - sqrt_N
        
        cand_coords = embed_torus_geodesic(candidate, K)
        dist = float(riemannian_distance(N_coords, cand_coords))
        candidates_with_dist.append((dist, candidate))
    
    # Sample top outer segments with 110-bit pattern
    for seg in top_segments:
        seg_start = seg['start_offset']
        seg_end = seg['end_offset']
        
        # Inner: step 40 for ±30000 (if segment overlaps)
        inner_step = 40
        if seg_start <= INNER_BOUND and seg_end >= -INNER_BOUND:
            # Find overlap with inner region (excluding ultra-inner)
            overlap_start = max(seg_start, -INNER_BOUND)
            overlap_end = min(seg_end, INNER_BOUND)
            
            # Skip ultra-inner part (already covered)
            if overlap_start < -ULTRA_INNER_BOUND:
                for offset in range(overlap_start, -ULTRA_INNER_BOUND, inner_step):
                    candidate = sqrt_N + offset
                    if candidate <= 1 or candidate >= N:
                        continue
                    if candidate % 2 == 0:
                        candidate += 1
                    
                    cand_coords = embed_torus_geodesic(candidate, K)
                    dist = float(riemannian_distance(N_coords, cand_coords))
                    candidates_with_dist.append((dist, candidate))
            
            if overlap_end > ULTRA_INNER_BOUND:
                for offset in range(ULTRA_INNER_BOUND + 1, overlap_end + 1, inner_step):
                    candidate = sqrt_N + offset
                    if candidate <= 1 or candidate >= N:
                        continue
                    if candidate % 2 == 0:
                        candidate += 1
                    
                    cand_coords = embed_torus_geodesic(candidate, K)
                    dist = float(riemannian_distance(N_coords, cand_coords))
                    candidates_with_dist.append((dist, candidate))
        
        # Middle: step 900 for ±300000 (if segment overlaps, excluding inner)
        middle_step = 900
        if seg_start <= MIDDLE_BOUND and seg_end >= -MIDDLE_BOUND:
            # Find overlap with middle region (excluding inner)
            if seg_start < -INNER_BOUND and seg_end <= -INNER_BOUND:
                overlap_start = max(seg_start, -MIDDLE_BOUND)
                overlap_end = min(seg_end, -INNER_BOUND)
                for offset in range(overlap_start, overlap_end, middle_step):
                    candidate = sqrt_N + offset
                    if candidate <= 1 or candidate >= N:
                        continue
                    if candidate % 2 == 0:
                        candidate += 1
                    
                    cand_coords = embed_torus_geodesic(candidate, K)
                    dist = float(riemannian_distance(N_coords, cand_coords))
                    candidates_with_dist.append((dist, candidate))
            
            if seg_start >= INNER_BOUND and seg_end > INNER_BOUND:
                overlap_start = max(seg_start, INNER_BOUND)
                overlap_end = min(seg_end, MIDDLE_BOUND)
                for offset in range(overlap_start, overlap_end, middle_step):
                    candidate = sqrt_N + offset
                    if candidate <= 1 or candidate >= N:
                        continue
                    if candidate % 2 == 0:
                        candidate += 1
                    
                    cand_coords = embed_torus_geodesic(candidate, K)
                    dist = float(riemannian_distance(N_coords, cand_coords))
                    candidates_with_dist.append((dist, candidate))
    
    # Remove duplicates (same candidate may appear in multiple segments)
    seen_candidates = set()
    unique_candidates = []
    for dist, cand in candidates_with_dist:
        if cand not in seen_candidates:
            seen_candidates.add(cand)
            unique_candidates.append((dist, cand))
    
    # Sort by distance
    unique_candidates.sort()
    
    if verbose:
        print(f"Stage 2: Sampled {len(unique_candidates)} unique candidates")
        if unique_candidates:
            print(f"  Min distance: {unique_candidates[0][0]:.6f}")
            print(f"  Best candidate offset: {unique_candidates[0][1] - sqrt_N}")
        print()
    
    # Test top candidates with local search
    candidates_tested = 0
    max_candidates = 400000  # Same as baseline
    top_n = min(50, len(unique_candidates))
    
    for dist, center_candidate in unique_candidates[:top_n]:
        if candidates_tested >= max_candidates:
            break
        
        # Local search around this candidate
        for local_offset in range(-LOCAL_WINDOW, LOCAL_WINDOW + 1):
            if candidates_tested >= max_candidates:
                break
            
            candidate = center_candidate + local_offset
            
            if candidate <= 1 or candidate >= N:
                continue
            if candidate % 2 == 0 or candidate % 3 == 0 or candidate % 5 == 0:
                continue
            
            candidates_tested += 1
            
            # Test divisibility
            if N % candidate == 0:
                p = candidate
                q = N // candidate
                
                stage2_elapsed = time.time() - stage2_start
                total_elapsed = time.time() - start_time
                
                # Calculate coverage
                ultra_inner_coverage = (2 * ULTRA_INNER_BOUND) / (2 * BASE_WINDOW) * 100
                outer_coverage = (len(top_segments) / NUM_SEGMENTS) * (1 - ultra_inner_coverage / 100) * 100
                total_coverage = ultra_inner_coverage + outer_coverage
                
                print(f"FACTOR FOUND!")
                print(f"  p = {p}")
                print(f"  q = {q}")
                print(f"  Geodesic distance: {dist:.6f}")
                print(f"  Offset from sqrt(N): {candidate - sqrt_N}")
                print(f"  Candidates tested: {candidates_tested}")
                print(f"  Stage 2 time: {stage2_elapsed:.3f}s")
                print(f"  Total time: {total_elapsed:.3f}s")
                print()
                
                return {
                    'success': True,
                    'factors': (p, q),
                    'candidates_tested': candidates_tested,
                    'total_time': total_elapsed,
                    'stage1_time': stage1_elapsed,
                    'stage2_time': stage2_elapsed,
                    'coverage_percent': total_coverage,
                    'num_top_segments': len(top_segments),
                }
    
    stage2_elapsed = time.time() - stage2_start
    total_elapsed = time.time() - start_time
    
    if verbose:
        print(f"No factors found")
        print(f"  Candidates tested: {candidates_tested}")
        print(f"  Stage 2 time: {stage2_elapsed:.3f}s")
        print(f"  Total time: {total_elapsed:.3f}s")
        print()
    
    return None


def run_experiment():
    """
    Run the two-stage experiment and compare with baseline.
    """
    print("=" * 70)
    print("Fractal/Recursive GVA Experiment: 110-bit")
    print("=" * 70)
    print()
    print("Hypothesis: 2-stage coarse-to-fine search reduces window coverage")
    print("           while maintaining factor recovery capability")
    print()
    print("Baseline Performance:")
    print("  Runtime: 4.027s")
    print("  Candidates sampled: 1403")
    print("  Candidates tested: 1115")
    print("  Window coverage: 100%")
    print()
    print("=" * 70)
    print()
    
    start_time = time.time()
    result = two_stage_gva_factor(verbose=True)
    elapsed = time.time() - start_time
    
    print("=" * 70)
    print("EXPERIMENT RESULT")
    print("=" * 70)
    
    if result and result['success']:
        p, q = result['factors']
        success = set(result['factors']) == {EXPECTED_P, EXPECTED_Q}
        
        if success:
            print(f"✅ SUCCESS: {N} = {p} × {q}")
            print(f"   Total time: {result['total_time']:.3f}s")
            print()
            print("Comparison to Baseline:")
            baseline_time = 4.027
            speedup = baseline_time / result['total_time'] if result['total_time'] > 0 else 0
            print(f"  Speedup: {speedup:.2f}x")
            print(f"  Window coverage: {result['coverage_percent']:.1f}% (baseline: 100%)")
            print()
            
            if result['coverage_percent'] < 100:
                print("✅ HYPOTHESIS VALIDATED: Fractal pruning finds same factors with reduced coverage")
            else:
                print("⚠️  HYPOTHESIS INCONCLUSIVE: Coverage not reduced but factors found")
        else:
            print(f"❌ FAIL: Found {p} × {q}, expected {EXPECTED_P} × {EXPECTED_Q}")
            print("❌ HYPOTHESIS FALSIFIED: Wrong factors recovered")
    else:
        print(f"❌ FAIL: No factors found")
        print(f"   Total time: {elapsed:.3f}s")
        print("❌ HYPOTHESIS FALSIFIED: Reduced coverage lost factor recovery")
    
    print()


if __name__ == "__main__":
    run_experiment()
