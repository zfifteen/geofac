"""
8D Imbalance-Tuned GVA Implementation
=====================================

Tests the hypothesis that adding an 8th dimension to model imbalance ratio
r = ln(q/p) enables GVA to factor unbalanced semiprimes.

Core idea:
- Standard 7D GVA assumes r ≈ 0 (balanced factors near sqrt(N))
- When r ≠ 0, optimal phases shift proportional to r
- 8th coordinate θ_r ∈ [-0.6, 0.6] samples imbalance directly
- Shear term added to phase accumulator: φ_k + k·θ_r/2

Expected result:
- If hypothesis is TRUE: 8D shows lower geodesic min for unbalanced cases
- If hypothesis is FALSE: 8D performs same or worse than 7D
"""

import mpmath as mp
from typing import Tuple, Optional, List
import time
from math import log, sqrt

# Configure high precision
mp.mp.dps = 50

# Validation gates (from parent gva_factorization.py)
GATE_1_30BIT = 1073217479
GATE_2_60BIT = 1152921470247108503
CHALLENGE_127 = 137524771864208156028430259349934309717

RANGE_MIN = 10**14
RANGE_MAX = 10**18


def adaptive_precision(N: int) -> int:
    """Compute adaptive precision: max(50, N.bitLength() × 4 + 200)"""
    bit_length = N.bit_length()
    return max(50, bit_length * 4 + 200)


def embed_torus_8d(n: int, k: float, theta_r: float) -> List[mp.mpf]:
    """
    Embed integer n into 8D torus with imbalance coordinate.
    
    Args:
        n: Integer to embed
        k: Geodesic exponent [0.25, 0.45]
        theta_r: Imbalance parameter ∈ [-0.6, 0.6]
        
    Returns:
        8D coordinates: [7D standard coords, θ_r]
    """
    phi = mp.mpf(1 + mp.sqrt(5)) / 2  # Golden ratio
    
    coords = []
    for d in range(7):  # First 7 dimensions: standard GVA
        phi_power = phi ** (d + 1)
        coord = mp.fmod(n * phi_power, 1)
        
        # Apply geodesic exponent
        if k != 1.0:
            coord = mp.power(coord, k)
            coord = mp.fmod(coord, 1)
        
        # Add shear term based on imbalance
        shear = (d + 1) * theta_r / 2.0
        coord = mp.fmod(coord + shear, 1)
        
        coords.append(coord)
    
    # 8th dimension: imbalance coordinate (normalized to [0,1))
    theta_r_norm = (theta_r + 0.6) / 1.2  # Map [-0.6, 0.6] → [0, 1)
    coords.append(mp.mpf(theta_r_norm))
    
    return coords


def riemannian_distance_8d(p1: List[mp.mpf], p2: List[mp.mpf]) -> mp.mpf:
    """
    Riemannian distance on 8D torus.
    Uses flat torus metric with periodic boundary.
    """
    if len(p1) != 8 or len(p2) != 8:
        raise ValueError("Points must be 8-dimensional")
    
    dist_sq = mp.mpf(0)
    for c1, c2 in zip(p1, p2):
        diff = abs(c1 - c2)
        wrap_diff = mp.mpf(1) - diff
        min_diff = min(diff, wrap_diff)
        dist_sq += min_diff * min_diff
    
    return mp.sqrt(dist_sq)


def gva_8d_factor_search(N: int, 
                         k_values: Optional[List[float]] = None,
                         theta_r_samples: int = 50,
                         theta_r_range: Tuple[float, float] = (-0.6, 0.6),
                         max_candidates: int = 10000,
                         verbose: bool = False,
                         allow_any_range: bool = False) -> Optional[Tuple[int, int]]:
    """
    8D GVA factorization with imbalance tuning.
    
    Strategy:
    1. Sample θ_r grid over imbalance range
    2. For each (k, θ_r) pair, embed N and candidates
    3. Find candidates with minimal geodesic distance
    4. Test divisibility
    
    Args:
        N: Semiprime to factor
        k_values: Geodesic exponents to test
        theta_r_samples: Number of θ_r values to sample
        theta_r_range: Range for θ_r parameter
        max_candidates: Max candidates per (k, θ_r)
        verbose: Enable logging
        allow_any_range: Allow N outside operational range
        
    Returns:
        (p, q) if found, else None
    """
    # Validate range
    if not allow_any_range and N != CHALLENGE_127 and not (RANGE_MIN <= N <= RANGE_MAX):
        raise ValueError(f"N must be in [{RANGE_MIN}, {RANGE_MAX}] or CHALLENGE_127")
    
    # Quick even check
    if N % 2 == 0:
        return (2, N // 2)
    
    # Set adaptive precision
    required_dps = adaptive_precision(N)
    with mp.workdps(required_dps):
        if verbose:
            print(f"N = {N}")
            print(f"Bit length: {N.bit_length()}")
            print(f"Adaptive precision: {required_dps} dps")
            print(f"8D mode: sampling {theta_r_samples} θ_r values in {theta_r_range}")
        
        if k_values is None:
            k_values = [0.30, 0.35, 0.40]
        
        sqrt_N = int(mp.sqrt(N))
        bit_length = N.bit_length()
        
        # Search window (same as 7D for fair comparison)
        if bit_length <= 40:
            base_window = max(1000, sqrt_N // 1000)
        elif bit_length <= 60:
            base_window = max(10000, sqrt_N // 5000)
        elif bit_length <= 85:
            base_window = max(100000, sqrt_N // 1000)
        else:
            base_window = max(200000, sqrt_N // 500)
        
        if verbose:
            print(f"Search window: ±{base_window} around sqrt(N) = {sqrt_N}")
        
        # Generate θ_r samples using Sobol-like spacing
        theta_r_min, theta_r_max = theta_r_range
        theta_r_vals = [theta_r_min + i * (theta_r_max - theta_r_min) / (theta_r_samples - 1)
                        for i in range(theta_r_samples)]
        
        start_time = time.time()
        min_geodesic_overall = float('inf')
        best_theta_r = None
        
        for k in k_values:
            if verbose:
                print(f"\nTesting k = {k}")
            
            for theta_r in theta_r_vals:
                # Embed N with this (k, θ_r)
                N_coords = embed_torus_8d(N, k, theta_r)
                
                # Sample candidates and compute distances
                candidates_tested = 0
                min_geodesic = float('inf')
                
                # Dense sampling near sqrt(N)
                sample_offsets = []
                
                # Ultra-inner: step 1 for ±100
                for offset in range(-100, 101):
                    sample_offsets.append(offset)
                
                # Inner: step 10 for ±5000
                for offset in range(-5000, -100, 10):
                    sample_offsets.append(offset)
                for offset in range(101, 5001, 10):
                    sample_offsets.append(offset)
                
                # Middle: step 100 for ±50000
                for offset in range(-50000, -5000, 100):
                    sample_offsets.append(offset)
                for offset in range(5001, 50001, 100):
                    sample_offsets.append(offset)
                
                # Outer: sparser to window
                if base_window > 50000:
                    step_outer = max(1000, (base_window - 50000) // 100)
                    for offset in range(-base_window, -50000, step_outer):
                        sample_offsets.append(offset)
                    for offset in range(50001, base_window + 1, step_outer):
                        sample_offsets.append(offset)
                
                for offset in sample_offsets:
                    if candidates_tested >= max_candidates:
                        break
                    
                    candidate = sqrt_N + offset
                    if candidate <= 1 or candidate >= N:
                        continue
                    if candidate % 2 == 0 or candidate % 3 == 0 or candidate % 5 == 0:
                        continue
                    
                    candidates_tested += 1
                    
                    # Compute geodesic distance
                    cand_coords = embed_torus_8d(candidate, k, theta_r)
                    dist = riemannian_distance_8d(N_coords, cand_coords)
                    
                    if dist < min_geodesic:
                        min_geodesic = float(dist)
                    
                    # Test divisibility
                    if N % candidate == 0:
                        p = candidate
                        q = N // candidate
                        elapsed = time.time() - start_time
                        
                        if verbose:
                            print(f"\n✓ Factor found!")
                            print(f"  p = {p}")
                            print(f"  q = {q}")
                            print(f"  k = {k}, θ_r = {theta_r:.4f}")
                            print(f"  Geodesic distance: {dist:.6e}")
                            print(f"  Candidates tested: {candidates_tested}")
                            print(f"  Elapsed: {elapsed:.3f}s")
                        
                        return (p, q)
                
                if min_geodesic < min_geodesic_overall:
                    min_geodesic_overall = min_geodesic
                    best_theta_r = theta_r
        
        elapsed = time.time() - start_time
        if verbose:
            print(f"\nNo factors found.")
            print(f"Min geodesic overall: {min_geodesic_overall:.6e} (θ_r={best_theta_r:.4f})")
            print(f"Elapsed: {elapsed:.3f}s")
    
    return None


def compute_imbalance_ratio(p: int, q: int) -> float:
    """Compute ln(q/p), assumes q >= p"""
    if p > q:
        p, q = q, p
    return log(q / p)
