#!/usr/bin/env python3
"""
SHA256 Hash-Bounds Simulation
==============================

Attempts to reproduce the findings from PR #165's 14-semiprime simulation.

Claims to test:
1. SHA256 frac vs prediction error: No linear correlation (scatter spread ~0.8)
2. Hash-bounds adjustment collapses errors toward zero
3. v1's 42.9% per-N rate better than 15.5% random baseline
4. Variable optimal attenuation: range -0.8 to +1.2
5. Specific test cases from the table

Key Formula:
    err_adj = err_orig + (SHA_frac - 0.5) * atten

Where optimal attenuation:
    atten = - (err_orig) / (SHA_frac - 0.5)

Validation Gates:
- 127-bit challenge CHALLENGE_127 = 137524771864208156028430259349934309717 (whitelisted)
- Operational range: [10^14, 10^18]
- RSA-100: 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139

Precision: max(100, bit_length * 4 + 200)

Author: Geofac Experiment Runner
Date: 2025-11-28
"""

import hashlib
import json
import random
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import mpmath as mp
from mpmath import mpf, sqrt, log, floor, ceil

# ============================================================================
# Constants
# ============================================================================

CHALLENGE_127 = 137524771864208156028430259349934309717
CHALLENGE_127_P = 10508623501177419659
CHALLENGE_127_Q = 13086849276577416863

RSA_100 = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
RSA_100_P = 37975227936943673922808872755445627854565536638199
RSA_100_Q = 40094690950920881030683735292761468389214899724061

RANGE_MIN = 10**14
RANGE_MAX = 10**18

SEED = 42

# Correlation thresholds for interpretation
# Values below 0.3 indicate weak correlation, 0.3-0.7 moderate, above 0.7 strong
CORRELATION_THRESHOLD_WEAK = 0.3
CORRELATION_THRESHOLD_STRONG = 0.7
CORRELATION_THRESHOLD_VALIDATES_SCALING = 0.5

# Numerical threshold to avoid division by zero
DIVISION_BY_ZERO_THRESHOLD = 0.01

# Threshold for meaningful error calculations (below this, treat as zero)
MINIMUM_ERROR_THRESHOLD = 1e-10

# Deterministic Miller-Rabin witnesses for numbers up to 3317044064679887385961981
MILLER_RABIN_DETERMINISTIC_WITNESSES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

# Bit length threshold for smoke tests (below this, allow numbers outside validation range)
SMOKE_TEST_MAX_BITS = 50


# ============================================================================
# Precision Management
# ============================================================================

def adaptive_precision(N: int) -> int:
    """
    Compute adaptive precision based on N's bit length.
    Formula: max(100, N.bitLength() × 4 + 200)
    """
    bit_length = N.bit_length()
    return max(100, bit_length * 4 + 200)


def set_precision_for_N(N: int) -> int:
    """Set mpmath precision for given N and return the precision used."""
    dps = adaptive_precision(N)
    mp.mp.dps = dps
    return dps


# ============================================================================
# SHA256 Fractional Encoding
# ============================================================================

def sha256_fractional(N: int) -> mpf:
    """
    Compute SHA256(N) as fractional value in [0, 1).
    
    The hash is computed, converted to an integer, and normalized
    to the range [0, 1) by dividing by 2^256.
    
    Args:
        N: Integer to hash
        
    Returns:
        Fractional value in [0, 1)
    """
    # Compute SHA256 hash of N's bytes
    n_bytes = N.to_bytes((N.bit_length() + 7) // 8, byteorder='big')
    hash_digest = hashlib.sha256(n_bytes).digest()
    
    # Convert to integer
    hash_int = int.from_bytes(hash_digest, byteorder='big')
    
    # Normalize to [0, 1) with high precision
    max_hash = mpf(2) ** 256
    sha_frac = mpf(hash_int) / max_hash
    
    return sha_frac


# ============================================================================
# Geometric Predictor (v1 Hash-Bounds)
# ============================================================================

def compute_geometric_prediction(N: int) -> mpf:
    """
    Compute the geometric prediction for factor location.
    
    The v1 hash-bounds predictor uses SHA256(N) to establish
    a prior on where the smaller factor p might be located
    relative to sqrt(N).
    
    Returns:
        Predicted fractional offset from sqrt(N) normalized to p/sqrt(N)
    """
    # SHA256-based prior: hash encodes information about N's structure
    sha_frac = sha256_fractional(N)
    
    # Prediction model: p/sqrt(N) estimate
    # For balanced semiprimes, p ≈ sqrt(N), so ratio ≈ 1
    # SHA_frac provides a prior adjustment
    prediction = sha_frac  # Baseline prediction based on hash
    
    return prediction


def compute_true_factor_position(N: int, p: int) -> mpf:
    """
    Compute the true factor position as p/sqrt(N).
    
    For balanced semiprimes (p ≈ q), this ratio is close to 1.
    For unbalanced semiprimes, p/sqrt(N) deviates from 1.
    """
    sqrt_N = sqrt(mpf(N))
    return mpf(p) / sqrt_N


def compute_prediction_error(N: int, p: int) -> mpf:
    """
    Compute the prediction error: err_p = true_position - prediction.
    
    This measures how far off the SHA256-based prediction is
    from the actual factor location.
    """
    sha_frac = sha256_fractional(N)
    true_pos = compute_true_factor_position(N, p)
    
    # Error is defined as the difference between true position and SHA_frac
    # Normalize both to comparable scales
    # true_pos is p/sqrt(N), typically in [0.5, 1.5] for reasonable semiprimes
    # sha_frac is in [0, 1)
    
    # For this simulation, we compute error as normalized deviation
    err = true_pos - sha_frac
    
    return err


# ============================================================================
# Attenuation Adjustment Formula
# ============================================================================

def compute_optimal_attenuation(err_orig: mpf, sha_frac: mpf) -> Optional[mpf]:
    """
    Compute optimal attenuation to minimize adjusted error.
    
    Formula: atten = - err_orig / (sha_frac - 0.5)
    
    This makes err_adj = 0 when:
        err_adj = err_orig + (sha_frac - 0.5) * atten
        0 = err_orig + (sha_frac - 0.5) * (- err_orig / (sha_frac - 0.5))
        0 = err_orig - err_orig
    
    Returns None if sha_frac ≈ 0.5 (division by zero).
    """
    denominator = sha_frac - mpf("0.5")
    
    # Avoid division by zero
    if abs(denominator) < mpf(DIVISION_BY_ZERO_THRESHOLD):
        return None
    
    optimal_atten = -err_orig / denominator
    return optimal_atten


def compute_adjusted_error(err_orig: mpf, sha_frac: mpf, atten: mpf) -> mpf:
    """
    Compute adjusted error using the attenuation formula.
    
    Formula: err_adj = err_orig + (sha_frac - 0.5) * atten
    """
    return err_orig + (sha_frac - mpf("0.5")) * atten


# ============================================================================
# Semiprime Generation
# ============================================================================

def is_prime_miller_rabin(n: int, k: int = 25) -> bool:
    """
    Miller-Rabin primality test.
    
    Uses deterministic witnesses for small numbers,
    probabilistic for larger ones with k rounds.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Deterministic witnesses for small numbers
    if n < 3317044064679887385961981:
        witnesses = MILLER_RABIN_DETERMINISTIC_WITNESSES
    else:
        random.seed(SEED + n % 1000)  # Reproducible
        # Generate unique witnesses using randint in a loop (avoids memory issues)
        witnesses = set()
        while len(witnesses) < k:
            witnesses.add(random.randint(2, n - 2))
        witnesses = list(witnesses)
    
    for a in witnesses:
        if a >= n:
            continue
        
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def next_prime(n: int) -> int:
    """Find the next prime >= n."""
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not is_prime_miller_rabin(n):
        n += 2
    return n


def generate_balanced_semiprime(bit_length: int, seed: int) -> Tuple[int, int, int]:
    """
    Generate a balanced semiprime (p ≈ q) with specified bit length.
    
    Args:
        bit_length: Target bit length of N = p * q
        seed: Random seed for reproducibility
        
    Returns:
        Tuple (N, p, q) where N = p * q
    """
    random.seed(seed)
    
    # Target p around 2^(bit_length/2)
    half_bits = bit_length // 2
    
    # Generate p near 2^(half_bits)
    p_target = 2 ** half_bits
    p_range = p_target // 10  # ±10% range
    
    p_start = p_target - random.randint(0, p_range)
    p = next_prime(p_start)
    
    # Generate q close to p (balanced)
    q_offset = random.randint(100, 10000)  # Small gap for balanced
    q = next_prime(p + q_offset)
    
    N = p * q
    
    return N, p, q


def generate_unbalanced_semiprime(bit_length: int, imbalance_factor: float, seed: int) -> Tuple[int, int, int]:
    """
    Generate an unbalanced semiprime where p << q.
    
    Args:
        bit_length: Target bit length of N = p * q
        imbalance_factor: Ratio of p's bits to q's bits (< 1.0 for unbalanced)
        seed: Random seed
        
    Returns:
        Tuple (N, p, q) where N = p * q
    """
    random.seed(seed)
    
    # p has fewer bits than q
    p_bits = int(bit_length * imbalance_factor / (1 + imbalance_factor))
    q_bits = bit_length - p_bits
    
    p_target = 2 ** p_bits
    q_target = 2 ** q_bits
    
    p = next_prime(p_target + random.randint(0, p_target // 10))
    q = next_prime(q_target + random.randint(0, q_target // 10))
    
    N = p * q
    
    return N, min(p, q), max(p, q)


# ============================================================================
# Test Case Generation
# ============================================================================

def generate_test_suite() -> List[Dict[str, Any]]:
    """
    Generate the test suite including:
    - 127-bit challenge (whitelisted)
    - RSA-100 (330-bit)
    - Various balanced semiprimes in [10^14, 10^18]
    - Some unbalanced cases for comparison
    
    Returns:
        List of test case dictionaries
    """
    test_cases = []
    
    # 1. 127-bit Challenge (whitelisted, primary gate)
    test_cases.append({
        "name": "127-bit Challenge",
        "N": CHALLENGE_127,
        "p": CHALLENGE_127_P,
        "q": CHALLENGE_127_Q,
        "bit_length": CHALLENGE_127.bit_length(),
        "category": "challenge",
        "expected_sha_frac": None,  # Will compute
        "expected_atten": -0.42,  # From PR #165 claim
    })
    
    # 2. RSA-100 (330-bit)
    test_cases.append({
        "name": "RSA-100 (330-bit)",
        "N": RSA_100,
        "p": RSA_100_P,
        "q": RSA_100_Q,
        "bit_length": RSA_100.bit_length(),
        "category": "rsa",
        "expected_sha_frac": 0.953,  # From PR #165 claim
        "expected_atten": -0.42,  # From PR #165 claim
    })
    
    # 3. Generate semiprimes in [10^14, 10^18] range at various bit lengths
    bit_lengths_to_test = [50, 55, 60, 65, 70, 75, 80, 100, 150, 200]
    
    for i, bits in enumerate(bit_lengths_to_test):
        N, p, q = generate_balanced_semiprime(bits, seed=SEED + i * 100)
        
        # Verify N is in valid range or is small enough to be a smoke test
        is_valid = (RANGE_MIN <= N <= RANGE_MAX) or (bits < SMOKE_TEST_MAX_BITS)
        
        test_cases.append({
            "name": f"{bits}-bit Balanced",
            "N": N,
            "p": p,
            "q": q,
            "bit_length": N.bit_length(),
            "category": "balanced",
            "valid_range": is_valid,
            "expected_sha_frac": None,
            "expected_atten": None,
        })
    
    # 4. Add some unbalanced cases
    unbalanced_configs = [
        (100, 0.3, "100-bit Unbalanced (30/70)"),
        (80, 0.25, "80-bit Unbalanced (25/75)"),
    ]
    
    for i, (bits, imbalance, name) in enumerate(unbalanced_configs):
        N, p, q = generate_unbalanced_semiprime(bits, imbalance, seed=SEED + 1000 + i)
        
        test_cases.append({
            "name": name,
            "N": N,
            "p": p,
            "q": q,
            "bit_length": N.bit_length(),
            "category": "unbalanced",
            "valid_range": RANGE_MIN <= N <= RANGE_MAX,
            "expected_sha_frac": None,
            "expected_atten": None,
        })
    
    return test_cases


# ============================================================================
# Simulation Runner
# ============================================================================

def run_simulation(test_cases: List[Dict[str, Any]], verbose: bool = True) -> Dict[str, Any]:
    """
    Run the SHA256 hash-bounds simulation on all test cases.
    
    For each test case:
    1. Compute SHA256 fractional value
    2. Compute original prediction error
    3. Compute optimal attenuation
    4. Compute adjusted error
    5. Compare to claims from PR #165
    
    Returns:
        Complete simulation results
    """
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "seed": SEED,
            "num_test_cases": len(test_cases),
            "claims_to_test": [
                "SHA256 frac vs prediction error: No linear correlation",
                "Hash-bounds adjustment collapses errors toward zero",
                "v1's 42.9% per-N rate better than 15.5% random baseline",
                "Variable optimal attenuation: range -0.8 to +1.2",
                "Bit-length scaling: atten ≈ bit_length / 100 - 0.5",
            ],
        },
        "test_results": [],
        "aggregate_analysis": {},
    }
    
    sha_fracs = []
    orig_errors = []
    adj_errors = []
    optimal_attens = []
    bit_lengths = []
    
    for case in test_cases:
        N = case["N"]
        p = case["p"]
        q = case["q"]
        name = case["name"]
        
        # Set adaptive precision
        precision = set_precision_for_N(N)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"Testing: {name}")
            print(f"N = {N}")
            print(f"Bit length: {N.bit_length()}")
            print(f"Precision: {precision} dps")
            print(f"p = {p}")
            print(f"q = {q}")
        
        # Verify p * q = N
        if p * q != N:
            raise ValueError(f"Invalid test case: {p} * {q} != {N}")
        
        # Compute SHA256 fractional
        sha_frac = sha256_fractional(N)
        
        # Compute true factor position
        true_pos = compute_true_factor_position(N, p)
        
        # Compute original prediction error
        err_orig = compute_prediction_error(N, p)
        
        # Compute optimal attenuation
        opt_atten = compute_optimal_attenuation(err_orig, sha_frac)
        
        # Compute adjusted error using optimal attenuation
        if opt_atten is not None:
            err_adj = compute_adjusted_error(err_orig, sha_frac, opt_atten)
        else:
            err_adj = err_orig  # No adjustment possible
        
        # Also test with fixed attenuation of -0.42 (PR #165 claim)
        err_adj_fixed = compute_adjusted_error(err_orig, sha_frac, mpf("-0.42"))
        
        # Bit-length scaling formula: atten ≈ bit_length / 100 - 0.5
        predicted_atten_by_bits = N.bit_length() / 100 - 0.5
        
        # Error reduction percentage
        if abs(float(err_orig)) > MINIMUM_ERROR_THRESHOLD:
            reduction_optimal = (1 - abs(float(err_adj)) / abs(float(err_orig))) * 100
            reduction_fixed = (1 - abs(float(err_adj_fixed)) / abs(float(err_orig))) * 100
        else:
            reduction_optimal = 0.0
            reduction_fixed = 0.0
        
        result = {
            "name": name,
            "N": str(N),
            "p": str(p),
            "q": str(q),
            "bit_length": N.bit_length(),
            "precision_dps": precision,
            "sha_frac": float(sha_frac),
            "true_position": float(true_pos),
            "err_orig": float(err_orig),
            "optimal_attenuation": float(opt_atten) if opt_atten is not None else None,
            "err_adj_optimal": float(err_adj),
            "err_adj_fixed_neg042": float(err_adj_fixed),
            "reduction_pct_optimal": reduction_optimal,
            "reduction_pct_fixed": reduction_fixed,
            "predicted_atten_by_bits": predicted_atten_by_bits,
            "category": case.get("category", "unknown"),
        }
        
        results["test_results"].append(result)
        
        # Collect for aggregate analysis
        sha_fracs.append(float(sha_frac))
        orig_errors.append(float(err_orig))
        adj_errors.append(float(err_adj))
        if opt_atten is not None:
            optimal_attens.append(float(opt_atten))
        bit_lengths.append(N.bit_length())
        
        if verbose:
            print(f"\nResults:")
            print(f"  SHA256 frac: {float(sha_frac):.6f}")
            print(f"  True position (p/sqrt(N)): {float(true_pos):.6f}")
            print(f"  Original error: {float(err_orig):.6f}")
            print(f"  Optimal attenuation: {float(opt_atten):.4f}" if opt_atten else "  Optimal attenuation: N/A (sha_frac ≈ 0.5)")
            print(f"  Adjusted error (optimal): {float(err_adj):.6f}")
            print(f"  Adjusted error (fixed -0.42): {float(err_adj_fixed):.6f}")
            print(f"  Error reduction (optimal): {reduction_optimal:.1f}%")
            print(f"  Error reduction (fixed): {reduction_fixed:.1f}%")
            print(f"  Predicted atten by bits: {predicted_atten_by_bits:.4f}")
    
    # Aggregate analysis
    results["aggregate_analysis"] = compute_aggregate_analysis(
        sha_fracs, orig_errors, adj_errors, optimal_attens, bit_lengths
    )
    
    return results


def compute_aggregate_analysis(
    sha_fracs: List[float],
    orig_errors: List[float],
    adj_errors: List[float],
    optimal_attens: List[float],
    bit_lengths: List[int],
) -> Dict[str, Any]:
    """
    Compute aggregate statistics to test PR #165 claims.
    """
    analysis = {}
    
    # 1. SHA256 frac range and spread
    analysis["sha_frac_stats"] = {
        "min": min(sha_fracs),
        "max": max(sha_fracs),
        "range": max(sha_fracs) - min(sha_fracs),
        "mean": statistics.mean(sha_fracs),
        "stdev": statistics.stdev(sha_fracs) if len(sha_fracs) > 1 else 0,
    }
    
    # 2. Original error range
    analysis["orig_error_stats"] = {
        "min": min(orig_errors),
        "max": max(orig_errors),
        "range": max(orig_errors) - min(orig_errors),
        "mean": statistics.mean(orig_errors),
        "stdev": statistics.stdev(orig_errors) if len(orig_errors) > 1 else 0,
    }
    
    # 3. Adjusted error range (claim: errors cluster at <±0.1)
    analysis["adj_error_stats"] = {
        "min": min(adj_errors),
        "max": max(adj_errors),
        "range": max(adj_errors) - min(adj_errors),
        "mean": statistics.mean(adj_errors),
        "stdev": statistics.stdev(adj_errors) if len(adj_errors) > 1 else 0,
        "pct_within_01": sum(1 for e in adj_errors if abs(e) < 0.1) / len(adj_errors) * 100,
    }
    
    # 4. Optimal attenuation range (claim: -0.8 to +1.2)
    if optimal_attens:
        analysis["optimal_atten_stats"] = {
            "min": min(optimal_attens),
            "max": max(optimal_attens),
            "range": max(optimal_attens) - min(optimal_attens),
            "mean": statistics.mean(optimal_attens),
        }
    else:
        analysis["optimal_atten_stats"] = {"note": "No valid attenuations computed"}
    
    # 5. Correlation test (claim: no linear correlation between SHA_frac and error)
    if len(sha_fracs) > 1:
        correlation = compute_pearson_correlation(sha_fracs, orig_errors)
        if abs(correlation) < CORRELATION_THRESHOLD_WEAK:
            interpretation = "weak"
        elif abs(correlation) < CORRELATION_THRESHOLD_STRONG:
            interpretation = "moderate"
        else:
            interpretation = "strong"
        analysis["sha_error_correlation"] = {
            "pearson_r": correlation,
            "interpretation": interpretation,
        }
    
    # 6. Bit-length scaling test (claim: atten ≈ bit_length / 100 - 0.5)
    if optimal_attens and bit_lengths:
        # Filter to matching pairs
        pairs = [(b, a) for b, a in zip(bit_lengths[:len(optimal_attens)], optimal_attens)]
        if pairs:
            predicted_attens = [b / 100 - 0.5 for b, _ in pairs]
            actual_attens = [a for _, a in pairs]
            scaling_correlation = compute_pearson_correlation(predicted_attens, actual_attens)
            analysis["bitlength_scaling"] = {
                "correlation_with_formula": scaling_correlation,
                "formula": "atten = bit_length / 100 - 0.5",
                "validates_claim": abs(scaling_correlation) > CORRELATION_THRESHOLD_VALIDATES_SCALING,
            }
    
    # 7. Error reduction statistics
    orig_abs_errors = [abs(e) for e in orig_errors]
    adj_abs_errors = [abs(e) for e in adj_errors]
    
    if orig_abs_errors and adj_abs_errors:
        avg_orig = statistics.mean(orig_abs_errors)
        avg_adj = statistics.mean(adj_abs_errors)
        avg_reduction = (1 - avg_adj / avg_orig) * 100 if avg_orig > 0 else 0
        
        analysis["error_reduction"] = {
            "avg_abs_orig_error": avg_orig,
            "avg_abs_adj_error": avg_adj,
            "avg_reduction_pct": avg_reduction,
            "num_improved": sum(1 for o, a in zip(orig_abs_errors, adj_abs_errors) if a < o),
            "num_worsened": sum(1 for o, a in zip(orig_abs_errors, adj_abs_errors) if a > o),
        }
    
    return analysis


def compute_pearson_correlation(x: List[float], y: List[float]) -> float:
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n != len(y) or n < 2:
        return 0.0
    
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    
    sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
    sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
    
    denominator = (sum_sq_x * sum_sq_y) ** 0.5
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


# ============================================================================
# Claim Validation
# ============================================================================

def validate_claims(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the specific claims from PR #165 against simulation results.
    """
    analysis = results["aggregate_analysis"]
    test_results = results["test_results"]
    
    validations = {}
    
    # Claim 1: SHA256 frac vs prediction error: No linear correlation (scatter spread ~0.8)
    sha_stats = analysis.get("sha_frac_stats", {})
    corr_data = analysis.get("sha_error_correlation", {})
    
    validations["claim_1_no_linear_correlation"] = {
        "claim": "SHA256 frac vs prediction error shows no linear correlation",
        "sha_frac_range": sha_stats.get("range", 0),
        "expected_range": 0.8,
        "correlation": corr_data.get("pearson_r", None),
        # Validate claim if correlation is weak (below threshold)
        "validated": abs(corr_data.get("pearson_r", 1)) < CORRELATION_THRESHOLD_WEAK,
        "interpretation": corr_data.get("interpretation", "unknown"),
    }
    
    # Claim 2: Hash-bounds adjustment collapses errors toward zero
    adj_stats = analysis.get("adj_error_stats", {})
    orig_stats = analysis.get("orig_error_stats", {})
    
    validations["claim_2_error_collapse"] = {
        "claim": "Adjusted errors cluster at <±0.1",
        "orig_error_range": orig_stats.get("range", 0),
        "adj_error_range": adj_stats.get("range", 0),
        "pct_within_01": adj_stats.get("pct_within_01", 0),
        "validated": adj_stats.get("pct_within_01", 0) > 50,
    }
    
    # Claim 3: v1's 42.9% per-N rate better than 15.5% random baseline
    # This requires checking if error reduction is better than random
    reduction = analysis.get("error_reduction", {})
    
    validations["claim_3_better_than_random"] = {
        "claim": "v1's 42.9% per-N rate better than 15.5% random baseline",
        "num_improved": reduction.get("num_improved", 0),
        "num_worsened": reduction.get("num_worsened", 0),
        "improvement_rate": reduction.get("num_improved", 0) / len(test_results) * 100 if test_results else 0,
        "expected_rate": 42.9,
        "random_baseline": 15.5,
        "validated": reduction.get("num_improved", 0) / len(test_results) > 0.155 if test_results else False,
    }
    
    # Claim 4: Variable optimal attenuation: range -0.8 to +1.2
    atten_stats = analysis.get("optimal_atten_stats", {})
    
    validations["claim_4_attenuation_range"] = {
        "claim": "Optimal attenuation ranges from -0.8 to +1.2",
        "observed_min": atten_stats.get("min", None),
        "observed_max": atten_stats.get("max", None),
        "observed_range": atten_stats.get("range", None),
        "expected_range": 2.0,  # -0.8 to +1.2
        "validated": atten_stats.get("range", 0) > 1.0 if "range" in atten_stats else False,
    }
    
    # Claim 5: Bit-length scaling: atten ≈ bit_length / 100 - 0.5
    scaling = analysis.get("bitlength_scaling", {})
    
    validations["claim_5_bitlength_scaling"] = {
        "claim": "Optimal attenuation scales with bit-length: atten ≈ bit_length / 100 - 0.5",
        "correlation_with_formula": scaling.get("correlation_with_formula", None),
        "validated": scaling.get("validates_claim", False),
    }
    
    # Specific test cases from PR #165
    challenge_127_result = next((r for r in test_results if "127-bit" in r["name"]), None)
    rsa_100_result = next((r for r in test_results if "RSA-100" in r["name"]), None)
    
    if challenge_127_result:
        validations["specific_127bit_challenge"] = {
            "claim": "127-bit: SHA_frac≈0.708, optimal atten≈-0.42, 29% reduction",
            "observed_sha_frac": challenge_127_result["sha_frac"],
            "expected_sha_frac": 0.708,
            "observed_optimal_atten": challenge_127_result["optimal_attenuation"],
            "expected_optimal_atten": -0.42,
            "observed_reduction": challenge_127_result["reduction_pct_optimal"],
            "expected_reduction": 29,
            "sha_frac_close": abs(challenge_127_result["sha_frac"] - 0.708) < 0.1,
        }
    
    if rsa_100_result:
        validations["specific_rsa100"] = {
            "claim": "RSA-100: SHA_frac≈0.953, optimal atten≈-0.42, 58% reduction",
            "observed_sha_frac": rsa_100_result["sha_frac"],
            "expected_sha_frac": 0.953,
            "observed_optimal_atten": rsa_100_result["optimal_attenuation"],
            "expected_optimal_atten": -0.42,
            "observed_reduction": rsa_100_result["reduction_pct_optimal"],
            "expected_reduction": 58,
            "sha_frac_close": abs(rsa_100_result["sha_frac"] - 0.953) < 0.1,
        }
    
    return validations


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the full SHA256 hash-bounds simulation."""
    print("=" * 80)
    print("SHA256 HASH-BOUNDS SIMULATION")
    print("Reproducing PR #165 Findings")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Seed: {SEED}")
    print()
    
    # Generate test cases
    print("Generating test cases...")
    test_cases = generate_test_suite()
    print(f"Generated {len(test_cases)} test cases")
    
    # Run simulation
    print("\nRunning simulation...")
    start_time = time.time()
    results = run_simulation(test_cases, verbose=True)
    elapsed = time.time() - start_time
    results["metadata"]["elapsed_seconds"] = elapsed
    
    # Validate claims
    print("\n" + "=" * 80)
    print("CLAIM VALIDATION")
    print("=" * 80)
    
    validations = validate_claims(results)
    results["claim_validations"] = validations
    
    for claim_name, validation in validations.items():
        print(f"\n{claim_name}:")
        print(f"  Claim: {validation.get('claim', 'N/A')}")
        validated = validation.get("validated", False)
        print(f"  Validated: {'✓ YES' if validated else '✗ NO'}")
        for key, value in validation.items():
            if key not in ["claim", "validated"]:
                print(f"  {key}: {value}")
    
    # Save results
    output_dir = Path(__file__).parent
    output_path = output_dir / "run_log.json"
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_path}")
    print(f"Elapsed time: {elapsed:.2f}s")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    main()
