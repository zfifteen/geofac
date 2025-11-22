"""
FR-GVA vs Standard GVA Comparison Experiment
=============================================

Rigorous comparison of Fractal-Recursive GVA against standard GVA
on validation-compliant test cases.

Metrics compared:
- Factorization success rate
- Candidates tested (proxy for computational cost)
- Runtime performance
- Memory/precision requirements

Test cases selected from operational range [10^14, 10^18].
"""

import sys
import time
from typing import Dict, Optional, Tuple, List
import mpmath as mp

# Import both implementations
sys.path.insert(0, '/home/runner/work/geofac/geofac')
sys.path.insert(0, '/home/runner/work/geofac/geofac/experiments/fractal-recursive-gva-falsification')
from gva_factorization import gva_factor_search
from fr_gva_implementation import (
    fr_gva_factor_search, RANGE_MIN, RANGE_MAX, GATE_1_30BIT, GATE_2_60BIT
)

mp.mp.dps = 50


def generate_test_semiprimes() -> List[Tuple[int, str, int, int]]:
    """
    Generate test semiprimes within operational range [10^14, 10^18].
    
    Returns list of (N, label, p, q) tuples where N = p*q.
    These are balanced semiprimes with factors near sqrt(N).
    """
    test_cases = []
    
    # 10^14 lower bound (47 bits)
    test_cases.append((100000980001501, "10^14 lower", 10000019, 10000079))
    
    # Mid 10^14 (49 bits)
    test_cases.append((500000591440213, "mid 10^14", 22360687, 22360699))
    
    # 10^15 (50 bits)
    test_cases.append((1000000088437283, "10^15", 31622777, 31622779))
    
    # 10^16 (54 bits)
    test_cases.append((10000004400000259, "10^16", 100000007, 100000037))
    
    # 10^17 (57 bits)
    test_cases.append((100000010741094833, "10^17", 316227767, 316227799))
    
    # 10^18 upper bound (60 bits)
    test_cases.append((1000000016000000063, "10^18 upper", 1000000007, 1000000009))
    
    return test_cases


def run_single_comparison(N: int, label: str, expected_p: int, expected_q: int,
                         timeout: float = 60.0) -> Dict:
    """
    Run both GVA and FR-GVA on a single test case.
    
    Returns comparison metrics dictionary.
    """
    result = {
        'N': N,
        'label': label,
        'bit_length': N.bit_length(),
        'expected_factors': (expected_p, expected_q),
        'gva': {},
        'fr_gva': {}
    }
    
    print(f"\n{'='*70}")
    print(f"Test: {label}")
    print(f"N = {N} ({N.bit_length()} bits)")
    print(f"Expected: {expected_p} × {expected_q}")
    print(f"{'='*70}")
    
    # Test standard GVA
    print("\n[1] Standard GVA:")
    try:
        start_time = time.time()
        gva_result = gva_factor_search(N, k_values=[0.30, 0.35, 0.40],
                                       max_candidates=50000, verbose=False,
                                       allow_any_range=True)
        gva_time = time.time() - start_time
        
        if gva_result:
            p, q = gva_result
            success = (p * q == N) and ((p == expected_p and q == expected_q) or 
                                       (p == expected_q and q == expected_p))
            result['gva'] = {
                'success': success,
                'factors': (p, q),
                'time': gva_time,
                'verified': p * q == N
            }
            print(f"  ✓ Found: {p} × {q}")
            print(f"  Time: {gva_time:.3f}s")
            print(f"  Verified: {p * q == N}")
        else:
            result['gva'] = {
                'success': False,
                'factors': None,
                'time': gva_time,
                'verified': False
            }
            print(f"  ✗ No factors found")
            print(f"  Time: {gva_time:.3f}s")
    except Exception as e:
        result['gva'] = {
            'success': False,
            'error': str(e),
            'time': None,
            'verified': False
        }
        print(f"  ✗ Error: {e}")
    
    # Test FR-GVA
    print("\n[2] FR-GVA (Fractal-Recursive):")
    try:
        start_time = time.time()
        fr_gva_result = fr_gva_factor_search(N, max_depth=5, 
                                             kappa_threshold=0.525,
                                             max_candidates=50000,
                                             verbose=False,
                                             allow_any_range=True)
        fr_gva_time = time.time() - start_time
        
        if fr_gva_result:
            p, q = fr_gva_result
            success = (p * q == N) and ((p == expected_p and q == expected_q) or 
                                       (p == expected_q and q == expected_p))
            result['fr_gva'] = {
                'success': success,
                'factors': (p, q),
                'time': fr_gva_time,
                'verified': p * q == N
            }
            print(f"  ✓ Found: {p} × {q}")
            print(f"  Time: {fr_gva_time:.3f}s")
            print(f"  Verified: {p * q == N}")
        else:
            result['fr_gva'] = {
                'success': False,
                'factors': None,
                'time': fr_gva_time,
                'verified': False
            }
            print(f"  ✗ No factors found")
            print(f"  Time: {fr_gva_time:.3f}s")
    except Exception as e:
        result['fr_gva'] = {
            'success': False,
            'error': str(e),
            'time': None,
            'verified': False
        }
        print(f"  ✗ Error: {e}")
    
    # Comparison
    print("\n[Comparison]:")
    if result['gva'].get('success') and result['fr_gva'].get('success'):
        speedup = result['gva']['time'] / result['fr_gva']['time'] if result['fr_gva']['time'] > 0 else float('inf')
        print(f"  Both successful")
        print(f"  GVA time: {result['gva']['time']:.3f}s")
        print(f"  FR-GVA time: {result['fr_gva']['time']:.3f}s")
        print(f"  Speedup: {speedup:.2f}x {'(FR-GVA faster)' if speedup > 1 else '(GVA faster)'}")
        result['speedup'] = speedup
    elif result['gva'].get('success'):
        print(f"  ✓ GVA succeeded, ✗ FR-GVA failed")
        result['speedup'] = None
    elif result['fr_gva'].get('success'):
        print(f"  ✗ GVA failed, ✓ FR-GVA succeeded")
        result['speedup'] = None
    else:
        print(f"  ✗ Both failed")
        result['speedup'] = None
    
    return result


def print_summary(results: List[Dict]):
    """
    Print executive summary of all comparison results.
    """
    print("\n" + "="*70)
    print("EXECUTIVE SUMMARY")
    print("="*70)
    
    total = len(results)
    gva_success = sum(1 for r in results if r['gva'].get('success', False))
    fr_gva_success = sum(1 for r in results if r['fr_gva'].get('success', False))
    
    print(f"\nTest Cases: {total}")
    print(f"Standard GVA Success Rate: {gva_success}/{total} ({100*gva_success/total:.0f}%)")
    print(f"FR-GVA Success Rate: {fr_gva_success}/{total} ({100*fr_gva_success/total:.0f}%)")
    
    # Compute speedup statistics for cases where both succeeded
    speedups = [r['speedup'] for r in results if r.get('speedup') is not None]
    
    if speedups:
        avg_speedup = sum(speedups) / len(speedups)
        print(f"\nAverage Speedup (both successful): {avg_speedup:.2f}x")
        
        if avg_speedup > 1.3:
            print("→ FR-GVA shows significant speedup (>30%)")
        elif avg_speedup > 1.0:
            print("→ FR-GVA shows modest speedup")
        elif avg_speedup > 0.7:
            print("→ FR-GVA and GVA have similar performance")
        else:
            print("→ FR-GVA is slower than standard GVA")
    else:
        print("\nNo cases where both methods succeeded - cannot compute speedup")
    
    # Detailed verdict
    print("\n" + "-"*70)
    print("VERDICT ON HYPOTHESIS")
    print("-"*70)
    
    if fr_gva_success == 0:
        print("❌ HYPOTHESIS FALSIFIED")
        print("   FR-GVA failed on all test cases within operational range.")
        print("   The fractal-recursive approach does not improve factorization.")
    elif fr_gva_success < gva_success:
        print("❌ HYPOTHESIS FALSIFIED")
        print("   FR-GVA has lower success rate than standard GVA.")
        print(f"   FR-GVA: {fr_gva_success}/{total}, GVA: {gva_success}/{total}")
    elif speedups and avg_speedup < 1.0:
        print("❌ HYPOTHESIS FALSIFIED")
        print("   FR-GVA is slower than standard GVA.")
        print(f"   Average speedup: {avg_speedup:.2f}x (< 1.0)")
        print("   Expected 30% reduction in candidates not achieved.")
    elif speedups and avg_speedup >= 1.3:
        print("✓ HYPOTHESIS SUPPORTED")
        print("   FR-GVA shows significant speedup over standard GVA.")
        print(f"   Average speedup: {avg_speedup:.2f}x (≥ 1.3)")
        print("   Claims of 30% improvement are consistent with results.")
    else:
        print("⚠ INCONCLUSIVE")
        print("   Results do not clearly support or falsify the hypothesis.")
        if speedups:
            print(f"   Speedup ({avg_speedup:.2f}x) is modest but not significant.")
        print("   More extensive testing or different metrics may be needed.")
    
    print("\n" + "="*70)


def main():
    """
    Run full comparison experiment.
    """
    print("="*70)
    print("FR-GVA vs Standard GVA Comparison Experiment")
    print("="*70)
    print("\nObjective: Falsify the hypothesis that Fractal-Recursive GVA")
    print("           improves factorization performance over standard GVA.")
    print("\nHypothesis Claims:")
    print("  - 15-20% density boosts")
    print("  - 30% reduction in max_candidates")
    print("  - Reduced fallbacks")
    print("\nTest Strategy:")
    print("  - Compare on semiprimes within operational range [10^14, 10^18]")
    print("  - Measure success rate, runtime, and speedup")
    print("  - Use identical parameters where applicable")
    
    # Generate test cases
    test_cases = generate_test_semiprimes()
    
    print(f"\nTest Cases: {len(test_cases)}")
    for N, label, p, q in test_cases:
        print(f"  - {label}: N={N} ({N.bit_length()} bits)")
    
    # Run comparisons
    results = []
    for N, label, p, q in test_cases:
        result = run_single_comparison(N, label, p, q, timeout=60.0)
        results.append(result)
    
    # Print summary and verdict
    print_summary(results)


if __name__ == "__main__":
    main()
