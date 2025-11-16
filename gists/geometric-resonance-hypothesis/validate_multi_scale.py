#!/usr/bin/env python3
"""
Multi-scale validation of geometric resonance hypothesis.

Tests the hypothesis at multiple bit sizes: 10, 20, 30, 40, 50, 60, and 127 bits.

Hypothesis:
- For semiprime n=pq, |κ(p) - κ(q)| < 1e-16
- For semiprime n=pq, θ'(p, 0.3) ≈ θ'(q, 0.3) with relative diff < 1%

where:
- κ(n) = σ₀(n) · ln(n+1) / e²
- θ'(n, k) = φ · ((n mod φ) / φ)^k
"""

from mpmath import mp, log, e, mpf
from sympy import nextprime
import json
from datetime import datetime

# Set precision high enough for all tests
mp.dps = 720

# Golden ratio φ ≈ 1.618...
phi = (1 + mp.sqrt(5)) / 2

def mod_phi(n):
    """Compute n mod φ for the geometric resolution formula."""
    quotient = mp.floor(n / phi)
    return n - quotient * phi

def compute_kappa(n):
    """Compute κ(n) = σ₀(n) · ln(n+1) / e²"""
    # For prime n, σ₀(n) = 2
    sigma_n = mpf(2)
    return sigma_n * log(n + 1) / (e ** 2)

def compute_theta_prime(n, k):
    """Compute θ'(n, k) = φ · ((n mod φ) / φ)^k"""
    return phi * ((mod_phi(n) / phi) ** k)

def generate_semiprime_at_bitsize(bits):
    """Generate a semiprime with approximately the specified bit size."""
    # Generate two primes of roughly bits/2 size
    half_bits = bits // 2
    
    # Start from 2^(half_bits-1) to get primes in the right range
    start = 2 ** (half_bits - 1)
    
    p = nextprime(start)
    q = nextprime(p + 1)
    
    N = p * q
    actual_bits = N.bit_length() if hasattr(N, 'bit_length') else len(bin(int(N))) - 2
    
    return p, q, N, actual_bits

def test_hypothesis_at_bitsize(bits, official_factors=None):
    """Test hypothesis at a specific bit size."""
    if official_factors:
        # Use provided factors (for 127-bit case)
        N, p, q, actual_bits = official_factors
    else:
        # Generate factors
        p, q, N, actual_bits = generate_semiprime_at_bitsize(bits)
    
    # Verify it's a semiprime
    assert p * q == N, f"Product check failed: {p} * {q} != {N}"
    
    # Compute κ values
    kappa_p = compute_kappa(p)
    kappa_q = compute_kappa(q)
    kappa_diff = abs(kappa_p - kappa_q)
    
    # Test hypothesis 1: curvature
    kappa_threshold = mpf('1e-16')
    hypothesis_1_pass = kappa_diff < kappa_threshold
    
    # Compute θ' values
    k = mpf('0.3')
    theta_prime_p = compute_theta_prime(p, k)
    theta_prime_q = compute_theta_prime(q, k)
    theta_diff = abs(theta_prime_p - theta_prime_q)
    relative_theta_diff = theta_diff / max(theta_prime_p, theta_prime_q)
    
    # Test hypothesis 2: geometric resolution
    theta_threshold = mpf('0.01')  # 1%
    hypothesis_2_pass = relative_theta_diff < theta_threshold
    
    return {
        'bit_size': actual_bits,
        'N': str(N),
        'p': str(p),
        'q': str(q),
        'kappa_p': float(kappa_p),
        'kappa_q': float(kappa_q),
        'kappa_diff': float(kappa_diff),
        'kappa_pass': hypothesis_1_pass,
        'theta_prime_p': float(theta_prime_p),
        'theta_prime_q': float(theta_prime_q),
        'theta_diff': float(theta_diff),
        'relative_theta_diff': float(relative_theta_diff),
        'theta_pass': hypothesis_2_pass,
        'overall_pass': hypothesis_1_pass and hypothesis_2_pass
    }

# Official Gate 1 factors (127-bit)
N_127 = mpf('137524771864208156028430259349934309717')
p_127 = mpf('10508623501177419659')
q_127 = mpf('13086849276577416863')
actual_bits_127 = 127

print("=" * 80)
print("MULTI-SCALE GEOMETRIC RESONANCE HYPOTHESIS VALIDATION")
print("=" * 80)
print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
print(f"Precision: {mp.dps} decimal places")
print()

# Test at various bit sizes
bit_sizes = [10, 20, 30, 40, 50, 60]
results = []

print("RESULTS SUMMARY")
print("=" * 80)
print(f"{'Bits':<6} {'κ Pass':<8} {'θ\' Pass':<9} {'Overall':<9} {'κ Diff':<15} {'θ\' Rel%':<12}")
print("-" * 80)

# Test smaller sizes
for bits in bit_sizes:
    result = test_hypothesis_at_bitsize(bits)
    results.append(result)
    
    kappa_status = "✓" if result['kappa_pass'] else "✗"
    theta_status = "✓" if result['theta_pass'] else "✗"
    overall_status = "PASS" if result['overall_pass'] else "FAIL"
    
    print(f"{result['bit_size']:<6} {kappa_status:<8} {theta_status:<9} {overall_status:<9} "
          f"{result['kappa_diff']:<15.2e} {result['relative_theta_diff']*100:<12.2f}")

# Test Gate 1 (127-bit)
result_127 = test_hypothesis_at_bitsize(127, (N_127, p_127, q_127, actual_bits_127))
results.append(result_127)

kappa_status = "✓" if result_127['kappa_pass'] else "✗"
theta_status = "✓" if result_127['theta_pass'] else "✗"
overall_status = "PASS" if result_127['overall_pass'] else "FAIL"

print(f"{result_127['bit_size']:<6} {kappa_status:<8} {theta_status:<9} {overall_status:<9} "
      f"{result_127['kappa_diff']:<15.2e} {result_127['relative_theta_diff']*100:<12.2f}")

print()
print("Legend: κ = curvature invariant, θ' = geometric resolution")
print("        κ threshold: < 1e-16, θ' threshold: < 1%")
print()

# Detailed results
print("=" * 80)
print("DETAILED RESULTS BY BIT SIZE")
print("=" * 80)

for result in results:
    print()
    print(f"{'─' * 80}")
    print(f"BIT SIZE: {result['bit_size']}")
    print(f"{'─' * 80}")
    print(f"N = {result['N']}")
    print(f"p = {result['p']}")
    print(f"q = {result['q']}")
    print()
    print(f"Curvature Analysis:")
    print(f"  κ(p) = {result['kappa_p']:.6f}")
    print(f"  κ(q) = {result['kappa_q']:.6f}")
    print(f"  |κ(p) - κ(q)| = {result['kappa_diff']:.6e}")
    print(f"  Hypothesis 1 (< 1e-16): {'PASS ✓' if result['kappa_pass'] else 'FAIL ✗'}")
    print()
    print(f"Geometric Resolution Analysis:")
    print(f"  θ'(p, 0.3) = {result['theta_prime_p']:.6f}")
    print(f"  θ'(q, 0.3) = {result['theta_prime_q']:.6f}")
    print(f"  Relative difference = {result['relative_theta_diff']*100:.2f}%")
    print(f"  Hypothesis 2 (< 1%): {'PASS ✓' if result['theta_pass'] else 'FAIL ✗'}")
    print()
    print(f"Overall: {'VALIDATED ✓' if result['overall_pass'] else 'FALSIFIED ✗'}")

# Export results
output = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'precision_decimal_places': mp.dps,
    'test_bit_sizes': [r['bit_size'] for r in results],
    'results': results,
    'summary': {
        'total_tests': len(results),
        'passed': sum(1 for r in results if r['overall_pass']),
        'failed': sum(1 for r in results if not r['overall_pass'])
    }
}

with open('multi_scale_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print()
print("=" * 80)
print("OVERALL CONCLUSION")
print("=" * 80)
print()

passed_count = output['summary']['passed']
total_count = output['summary']['total_tests']

if passed_count == 0:
    print("✗ HYPOTHESIS FALSIFIED AT ALL SCALES")
    print()
    print("The geometric resonance hypothesis does not hold at any tested bit size")
    print("from 10 bits to 127 bits. Both the curvature invariant and geometric")
    print("resolution conditions fail across the entire range.")
elif passed_count == total_count:
    print("✓ HYPOTHESIS VALIDATED AT ALL SCALES")
    print()
    print("The geometric resonance hypothesis holds consistently across all tested")
    print("bit sizes from 10 bits to 127 bits.")
else:
    print(f"⚠ HYPOTHESIS PARTIALLY VALIDATED ({passed_count}/{total_count} scales)")
    print()
    print(f"The hypothesis holds at {passed_count} out of {total_count} tested scales.")
    print("This suggests scale-dependent behavior that requires further investigation.")

print()
print(f"Results exported to: multi_scale_results.json")
print()
print("=" * 80)
