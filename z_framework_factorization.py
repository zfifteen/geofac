"""
Z-Framework Geometric Resonance Factorization
==============================================

Implements geometric resonance factorization for the 127-bit challenge number
using Z-framework principles and high-precision arithmetic.

CHALLENGE:
    N = 137524771864208156028430259349934309717
    p = 10508623501177419659
    q = 13086849276577416863

Z-FRAMEWORK PRIMITIVES:
    Z = n(Δₙ/Δₘₐₓ)           - Normalized frame shift
    κ(n) = d(n)·ln(n+1)/e²   - Divisor-based scaling
    θ′(n,k) = φ·((n mod φ)/φ)^k - Geodesic transformation

GEOMETRIC RESONANCE:
    Search around sqrt(N) using quasi-random sampling (Sobol/Halton),
    score candidates with Gaussian kernel resonance, and use phase-corrected
    snap to integer values.

PRECISION:
    Uses mpmath with precision = max(50, N.bit_length() * 4 + 200)
    to ensure < 1e-16 relative error.

REPRODUCIBILITY:
    All parameters logged: precision, seeds, thresholds, sample counts.
    Deterministic quasi-random sequences ensure reproducible results.
"""

import mpmath as mp
from typing import Tuple, List, Optional
from math import e, log, sqrt
import time


class ZFrameworkFactorization:
    """
    Implements geometric resonance factorization using Z-framework principles.
    
    This class provides Z-framework primitives and a complete factorization
    algorithm for the 127-bit challenge number.
    """
    
    # Challenge number constants
    CHALLENGE_127 = 137524771864208156028430259349934309717
    KNOWN_P = 10508623501177419659
    KNOWN_Q = 13086849276577416863
    
    # Z-framework constants
    E_SQUARED = e ** 2
    GOLDEN_RATIO = (1 + sqrt(5)) / 2  # φ ≈ 1.618
    
    def __init__(self, N: int, precision: Optional[int] = None, seed: int = 42, 
                 skip_validation: bool = False):
        """
        Initialize Z-framework factorization for number N.
        
        Args:
            N: Number to factor (must be in valid range)
            precision: Decimal precision (default: max(50, N.bit_length() * 4 + 200))
            seed: Random seed for reproducibility
            skip_validation: Skip range validation (for testing only)
            
        Raises:
            ValueError: If N is not in valid range [1e14, 1e18] except 127-bit challenge
        """
        self.N = N
        self.seed = seed
        
        # Validate N is in operational range or is the 127-bit challenge
        if not skip_validation:
            if N != self.CHALLENGE_127:
                if not (1e14 <= N <= 1e18):
                    raise ValueError(
                        f"N must be in [1e14, 1e18] or be the 127-bit challenge. Got N={N}"
                    )
        
        # Set adaptive precision
        bit_length = N.bit_length()
        self.precision = precision if precision else max(50, bit_length * 4 + 200)
        
        # Set mpmath precision (locally per computation)
        self.sqrt_N = None
        
        # Log configuration
        self._log_config()
    
    def _log_config(self):
        """Log configuration parameters for reproducibility."""
        print(f"Z-Framework Factorization Configuration:")
        print(f"  N = {self.N}")
        print(f"  N.bit_length() = {self.N.bit_length()}")
        print(f"  Precision (decimal digits) = {self.precision}")
        print(f"  Seed = {self.seed}")
        print(f"  sqrt(N) ≈ {int(sqrt(self.N))}")
        print()
    
    def compute_Z(self, n: int, delta_n: float) -> mp.mpf:
        """
        Compute Z-framework normalization: Z = n(Δₙ/Δₘₐₓ)
        
        Args:
            n: Frame-dependent integer
            delta_n: Measured frame shift at n
            
        Returns:
            Normalized Z value
            
        Raises:
            ValueError: If delta_max is zero (division guard)
        """
        with mp.workdps(self.precision):
            delta_max = mp.mpf(self.E_SQUARED)
            
            if delta_max == 0:
                raise ValueError("Division by zero: Δₘₐₓ cannot be zero")
            
            n_mp = mp.mpf(n)
            delta_n_mp = mp.mpf(delta_n)
            
            Z = n_mp * (delta_n_mp / delta_max)
            return Z
    
    def compute_kappa(self, n: int) -> mp.mpf:
        """
        Compute κ(n) = d(n)·ln(n+1)/e² with zero division guards.
        
        Note: Uses simplified logarithmic approximation d(n) ≈ log(n) for
        divisor count rather than exact τ(n) for efficiency.
        
        Args:
            n: Integer for divisor computation
            
        Returns:
            Divisor-based scaling value
            
        Raises:
            ValueError: If n < 1
        """
        if n < 1:
            raise ValueError(f"n must be >= 1, got n={n}")
        
        with mp.workdps(self.precision):
            # Simplified logarithmic approximation for divisor count
            # More efficient than exact τ(n) = number of divisors
            d_n = mp.log(n) if n > 1 else mp.mpf(1)
            ln_term = mp.log(n + 1)
            e_squared = mp.mpf(self.E_SQUARED)
            
            kappa = (d_n * ln_term) / e_squared
            return kappa
    
    def compute_theta_prime(self, n: int, k: float) -> mp.mpf:
        """
        Compute θ′(n,k) = φ·((n mod φ)/φ)^k with k ≈ 0.3
        
        Args:
            n: Integer parameter
            k: Geodesic exponent (typically ~0.3)
            
        Returns:
            Geodesic-transformed value
        """
        with mp.workdps(self.precision):
            phi = mp.mpf(self.GOLDEN_RATIO)
            n_mp = mp.mpf(n)
            k_mp = mp.mpf(k)
            
            # Compute (n mod φ) / φ
            n_mod_phi = n_mp % phi
            ratio = n_mod_phi / phi
            
            # θ′(n,k) = φ · ratio^k
            theta_prime = phi * mp.power(ratio, k_mp)
            return theta_prime
    
    def _van_der_corput_sequence(self, n_samples: int, dim: int = 1) -> List[List[float]]:
        """
        Generate Van der Corput quasi-random sequence for deterministic sampling.
        
        Note: This is a simplified 1D Van der Corput sequence (base-2).
        For multi-dimensional Sobol sequences, use scipy.stats.qmc.Sobol.
        
        Args:
            n_samples: Number of samples to generate
            dim: Dimension of sequence (currently only 1D supported)
            
        Returns:
            List of quasi-random samples in [0, 1]^dim
        """
        # Van der Corput sequence in base 2
        samples = []
        for i in range(n_samples):
            result = 0.0
            base = 0.5
            n = i + 1
            while n > 0:
                if n % 2 == 1:
                    result += base
                base /= 2
                n //= 2
            samples.append([result])
        return samples
    
    def _halton_sequence(self, n_samples: int, base: int = 2) -> List[float]:
        """
        Generate Halton quasi-random sequence for deterministic sampling.
        
        Args:
            n_samples: Number of samples to generate
            base: Prime base for Halton sequence
            
        Returns:
            List of quasi-random samples in [0, 1]
        """
        def halton(index, base):
            """Compute Halton sequence value."""
            result = 0.0
            f = 1.0 / base
            i = index
            while i > 0:
                result += f * (i % base)
                i //= base
                f /= base
            return result
        
        return [halton(i + 1, base) for i in range(n_samples)]
    
    def _gaussian_kernel_resonance(self, x: mp.mpf, center: mp.mpf, sigma: mp.mpf) -> mp.mpf:
        """
        Compute Gaussian kernel resonance score.
        
        Args:
            x: Point to evaluate
            center: Center of resonance
            sigma: Kernel width
            
        Returns:
            Resonance score in [0, 1]
        """
        with mp.workdps(self.precision):
            diff = x - center
            exponent = -(diff ** 2) / (2 * sigma ** 2)
            return mp.exp(exponent)
    
    def _phase_corrected_snap(self, x: mp.mpf) -> int:
        """
        Phase-corrected snap to nearest integer.
        
        Args:
            x: High-precision value to snap
            
        Returns:
            Nearest integer
        """
        with mp.workdps(self.precision):
            # Round to nearest integer with phase correction
            # If fractional part is very close to 0.5, use geometric correction
            frac = x - mp.floor(x)
            
            if abs(frac - mp.mpf(0.5)) < mp.mpf(1e-10):
                # Near half-integer: use golden ratio phase correction
                phase = mp.fmod(x * mp.mpf(self.GOLDEN_RATIO), mp.mpf(1))
                if phase < mp.mpf(0.5):
                    return int(mp.floor(x))
                else:
                    return int(mp.ceil(x))
            else:
                # Standard rounding
                return int(mp.nint(x))
    
    def _check_causality(self, velocity: float, c: float):
        """
        Enforce causality constraint: |v| < c
        
        Args:
            velocity: Velocity to check
            c: Speed limit (invariant)
            
        Raises:
            ValueError: If causality is violated
        """
        if abs(velocity) >= c:
            raise ValueError(
                f"Causality violation: |v| = {abs(velocity)} >= c = {c}"
            )
    
    def geometric_resonance_search(
        self,
        n_samples: int = 10000,
        sigma_factor: float = 0.01,
        threshold: float = 0.85,
        k: float = 0.3,
        timeout_seconds: float = 300.0
    ) -> Optional[Tuple[int, int]]:
        """
        Search for factors using geometric resonance around sqrt(N).
        
        Args:
            n_samples: Number of quasi-random samples
            sigma_factor: Gaussian kernel width factor (relative to sqrt(N))
            threshold: Minimum resonance score to evaluate
            k: Geodesic exponent for θ′(n,k)
            timeout_seconds: Maximum search time
            
        Returns:
            Tuple (p, q) if factors found, None otherwise
        """
        print(f"Geometric Resonance Search:")
        print(f"  Samples = {n_samples}")
        print(f"  Sigma factor = {sigma_factor}")
        print(f"  Threshold = {threshold}")
        print(f"  k (geodesic exponent) = {k}")
        print(f"  Timeout = {timeout_seconds}s")
        print()
        
        start_time = time.time()
        
        with mp.workdps(self.precision):
            sqrt_N_mp = mp.sqrt(mp.mpf(self.N))
            sigma = sqrt_N_mp * mp.mpf(sigma_factor)
            
            print(f"Search center: sqrt(N) ≈ {float(sqrt_N_mp):.2f}")
            print(f"Kernel width: σ ≈ {float(sigma):.2f}")
            print()
            
            # Generate quasi-random samples (Halton sequence)
            samples = self._halton_sequence(n_samples, base=2)
            
            # Search window: sqrt(N) ± 3σ
            search_min = sqrt_N_mp - 3 * sigma
            search_max = sqrt_N_mp + 3 * sigma
            search_range = search_max - search_min
            
            candidates_evaluated = 0
            high_resonance_count = 0
            
            for i, sample in enumerate(samples):
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    print(f"Timeout after {timeout_seconds}s")
                    break
                
                # Map sample to search range
                candidate_mp = search_min + mp.mpf(sample) * search_range
                
                # Compute resonance score
                resonance = self._gaussian_kernel_resonance(
                    candidate_mp, sqrt_N_mp, sigma
                )
                
                # Apply threshold
                if resonance < mp.mpf(threshold):
                    continue
                
                high_resonance_count += 1
                
                # Apply Z-framework transformations
                candidate_int = self._phase_corrected_snap(candidate_mp)
                
                # Compute κ and θ′ for geometric enhancement
                if candidate_int >= 1:
                    try:
                        kappa = self.compute_kappa(candidate_int)
                        theta = self.compute_theta_prime(candidate_int, k)
                        
                        # Geometric correction
                        corrected = candidate_mp * (mp.mpf(1) + kappa / mp.mpf(1e6))
                        candidate_int = self._phase_corrected_snap(corrected)
                    except (ValueError, ZeroDivisionError):
                        pass
                
                # Test candidate
                if candidate_int > 1 and self.N % candidate_int == 0:
                    p = candidate_int
                    q = self.N // candidate_int
                    
                    elapsed = time.time() - start_time
                    print(f"SUCCESS after {elapsed:.2f}s!")
                    print(f"  Candidates evaluated: {candidates_evaluated}")
                    print(f"  High resonance hits: {high_resonance_count}")
                    print(f"  Found p = {p}")
                    print(f"  Found q = {q}")
                    print(f"  Verification: p * q = {p * q}")
                    print(f"  Match: {p * q == self.N}")
                    print()
                    
                    return (p, q)
                
                candidates_evaluated += 1
                
                # Progress report
                if (i + 1) % 1000 == 0:
                    elapsed = time.time() - start_time
                    print(f"Progress: {i + 1}/{n_samples} samples, "
                          f"{high_resonance_count} high resonance, "
                          f"{elapsed:.1f}s elapsed")
        
        print(f"No factors found after {n_samples} samples")
        return None
    
    def factor(
        self,
        n_samples: int = 10000,
        sigma_factor: float = 0.01,
        threshold: float = 0.85,
        k: float = 0.3,
        timeout_seconds: float = 300.0
    ) -> Optional[Tuple[int, int]]:
        """
        Factor N using geometric resonance with Z-framework principles.
        
        This is the main entry point for factorization.
        
        Args:
            n_samples: Number of quasi-random samples
            sigma_factor: Gaussian kernel width factor
            threshold: Minimum resonance score
            k: Geodesic exponent
            timeout_seconds: Maximum search time
            
        Returns:
            Tuple (p, q) where p * q == N, or None if not found
        """
        print("=" * 80)
        print("Z-FRAMEWORK GEOMETRIC RESONANCE FACTORIZATION")
        print("=" * 80)
        print()
        
        result = self.geometric_resonance_search(
            n_samples=n_samples,
            sigma_factor=sigma_factor,
            threshold=threshold,
            k=k,
            timeout_seconds=timeout_seconds
        )
        
        if result:
            p, q = result
            self.verify_factorization(p, q)
        
        return result
    
    def verify_factorization(self, p: int, q: int) -> bool:
        """
        Verify factorization: p * q == N with both integer and mpmath precision.
        
        Args:
            p: First factor
            q: Second factor
            
        Returns:
            True if verification passes
            
        Raises:
            AssertionError: If verification fails
        """
        print("=" * 80)
        print("VERIFICATION")
        print("=" * 80)
        print()
        
        # Integer verification
        product_int = p * q
        match_int = (product_int == self.N)
        
        print(f"Integer arithmetic:")
        print(f"  p = {p}")
        print(f"  q = {q}")
        print(f"  p * q = {product_int}")
        print(f"  N     = {self.N}")
        print(f"  Match: {match_int}")
        print()
        
        # High-precision verification with mpmath
        with mp.workdps(self.precision):
            p_mp = mp.mpf(p)
            q_mp = mp.mpf(q)
            N_mp = mp.mpf(self.N)
            product_mp = p_mp * q_mp
            
            relative_error = abs(product_mp - N_mp) / N_mp
            
            print(f"High-precision mpmath verification:")
            print(f"  Precision: {self.precision} decimal digits")
            print(f"  p * q = {product_mp}")
            print(f"  N     = {N_mp}")
            print(f"  Relative error: {float(relative_error):.2e}")
            print(f"  Error < 1e-16: {relative_error < mp.mpf(1e-16)}")
        
        print()
        
        assert match_int, f"Integer verification failed: {product_int} != {self.N}"
        assert relative_error < mp.mpf(1e-16), \
            f"High-precision verification failed: relative error {float(relative_error):.2e}"
        
        print("✅ Verification PASSED")
        print("=" * 80)
        print()
        
        return True


def factor_127bit_challenge(
    n_samples: int = 10000,
    sigma_factor: float = 0.01,
    threshold: float = 0.85,
    k: float = 0.3,
    timeout_seconds: float = 300.0
) -> Optional[Tuple[int, int]]:
    """
    Factor the 127-bit challenge number using Z-framework geometric resonance.
    
    Args:
        n_samples: Number of quasi-random samples
        sigma_factor: Gaussian kernel width factor
        threshold: Minimum resonance score
        k: Geodesic exponent
        timeout_seconds: Maximum search time
        
    Returns:
        Tuple (p, q) where p * q == N, or None if not found
    """
    factorizer = ZFrameworkFactorization(
        N=ZFrameworkFactorization.CHALLENGE_127,
        seed=42
    )
    
    return factorizer.factor(
        n_samples=n_samples,
        sigma_factor=sigma_factor,
        threshold=threshold,
        k=k,
        timeout_seconds=timeout_seconds
    )


if __name__ == "__main__":
    print("Z-Framework Factorization Demo")
    print()
    print("Factoring 127-bit challenge number...")
    print(f"N = {ZFrameworkFactorization.CHALLENGE_127}")
    print()
    
    result = factor_127bit_challenge(
        n_samples=20000,
        sigma_factor=0.01,
        threshold=0.80,
        k=0.3,
        timeout_seconds=600.0
    )
    
    if result:
        p, q = result
        print(f"Factors found: p = {p}, q = {q}")
    else:
        print("No factors found within budget")
