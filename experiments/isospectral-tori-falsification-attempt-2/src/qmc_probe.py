"""
Quasi-Monte Carlo Probing with Sobol Sequences and Owen Scrambling

Implements QMC probing across isospectral tori for resonance cross-validation.
"""

import numpy as np
from scipy.stats import qmc
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Regularization constant for numerical stability
REGULARIZATION_EPS = 1e-10

# Decimal precision for resonance comparison (avoids floating-point issues)
# This affects cross-validation by determining how close resonances must be
# to be considered "the same". Higher values = stricter matching.
RESONANCE_DECIMAL_PRECISION = 6


class QMCProbe:
    """
    QMC probe using Sobol sequences with Owen scrambling.
    
    Fixed seed ensures deterministic, reproducible behavior.
    """
    
    def __init__(self, dimension: int, n_samples: int = 10000,
                 scramble: bool = True, seed: int = 42):
        """
        Initialize QMC probe.
        
        Args:
            dimension: Search space dimension
            n_samples: Number of samples
            scramble: Use Owen scrambling
            seed: Fixed seed for reproducibility
        """
        self.dimension = dimension
        self.n_samples = n_samples
        self.scramble = scramble
        self.seed = seed
        
        self.sampler = qmc.Sobol(d=dimension, scramble=scramble, seed=seed)
        
        logger.info(f"QMC: dim={dimension}, samples={n_samples}, "
                   f"scramble={scramble}, seed={seed}")
    
    def generate_samples(self, n: Optional[int] = None) -> np.ndarray:
        """
        Generate Sobol sequence samples in [0,1]^d.
        
        Args:
            n: Number of samples (default: self.n_samples)
        
        Returns:
            (n, d) array of samples
        """
        n = n or self.n_samples
        samples = self.sampler.random(n)
        logger.debug(f"Generated {n} Sobol samples")
        return samples
    
    def compute_resonance_amplitude(self, sample: np.ndarray, n: int,
                                     gram: np.ndarray) -> float:
        """
        Compute resonance amplitude at sample point.
        
        Uses exponential decay from √n with lattice contribution.
        
        Args:
            sample: Sample point in [0,1]^d
            n: Target semiprime
            gram: Gram matrix of torus
        
        Returns:
            Amplitude in [0, 1]
        """
        sqrt_n = float(n) ** 0.5
        
        # Scale first coordinate to search window around sqrt(n)
        search_width = 0.1 * sqrt_n
        candidate = sqrt_n - search_width + sample[0] * 2 * search_width
        
        # Resonance: exponential decay from sqrt(n)
        distance_factor = np.exp(-np.abs(candidate - sqrt_n) / sqrt_n)
        
        # Lattice contribution
        basis = np.linalg.cholesky(gram + REGULARIZATION_EPS * np.eye(gram.shape[0]))
        scaled = basis @ sample[:self.dimension]
        lattice_factor = 1.0 / (1.0 + np.linalg.norm(scaled))
        
        return float(distance_factor * lattice_factor)
    
    def probe_torus(self, n: int, gram: np.ndarray,
                    n_samples: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Probe a single torus with QMC samples.
        
        Args:
            n: Target semiprime
            gram: Gram matrix of torus
            n_samples: Number of samples
        
        Returns:
            (samples, amplitudes)
        """
        n_samples = n_samples or self.n_samples
        samples = self.generate_samples(n_samples)
        
        amplitudes = np.array([
            self.compute_resonance_amplitude(s, n, gram)
            for s in samples
        ])
        
        logger.debug(f"Probed torus: mean_amp={np.mean(amplitudes):.4f}, "
                    f"max_amp={np.max(amplitudes):.4f}")
        
        return samples, amplitudes
    
    def probe_choir(self, n: int, choir: List[np.ndarray],
                    n_samples: Optional[int] = None) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Probe multiple tori (choir) sequentially.
        
        Args:
            n: Target semiprime
            choir: List of Gram matrices
            n_samples: Samples per torus
        
        Returns:
            List of (samples, amplitudes) per torus
        """
        logger.info(f"Probing choir of {len(choir)} tori")
        
        results = []
        for i, gram in enumerate(choir):
            # Reset sampler for each torus with different seed
            self.sampler = qmc.Sobol(d=self.dimension, scramble=self.scramble,
                                     seed=self.seed + i)
            result = self.probe_torus(n, gram, n_samples)
            results.append(result)
        
        return results
    
    def cross_validate_resonances(self, results: List[Tuple[np.ndarray, np.ndarray]],
                                   threshold: float = 0.8) -> Tuple[float, int]:
        """
        Cross-validate resonances across tori.
        
        High-amplitude samples appearing consistently indicate preserved metrics.
        
        Args:
            results: List of (samples, amplitudes) per torus
            threshold: Amplitude threshold for resonance
        
        Returns:
            (overlap_ratio, n_consistent_resonances)
        """
        if not results:
            return 0.0, 0
        
        # Find high-amplitude samples in each torus
        resonance_sets = []
        for samples, amplitudes in results:
            high_idx = np.where(amplitudes > threshold)[0]
            # Round to configurable precision to avoid floating-point issues
            resonances = set(np.round(
                samples[high_idx, 0], 
                decimals=RESONANCE_DECIMAL_PRECISION
            ))
            resonance_sets.append(resonances)
        
        if len(resonance_sets) < 2:
            return 1.0, len(resonance_sets[0]) if resonance_sets else 0
        
        # Intersection and union
        common = set.intersection(*resonance_sets)
        union = set.union(*resonance_sets)
        
        overlap = len(common) / len(union) if union else 0.0
        
        logger.info(f"Cross-validation: overlap={overlap:.4f}, "
                   f"consistent={len(common)}")
        
        return overlap, len(common)
    
    def convergence_error(self, amplitudes: np.ndarray,
                          window: int = 100) -> float:
        """
        Estimate QMC convergence error via running mean stability.
        
        Args:
            amplitudes: Amplitude array
            window: Window size for running mean
        
        Returns:
            Relative error estimate
        """
        if len(amplitudes) < 2 * window:
            return 1.0
        
        running_mean = np.convolve(amplitudes, 
                                   np.ones(window) / window, 
                                   mode='valid')
        
        if len(running_mean) == 0 or np.mean(running_mean) == 0:
            return 1.0
        
        error = np.std(running_mean) / (np.abs(np.mean(running_mean)) + 1e-10)
        
        logger.debug(f"Convergence error: {error:.4e}")
        return float(error)


def demonstrate():
    """Demonstrate QMC probing."""
    logging.basicConfig(level=logging.INFO)
    
    probe = QMCProbe(dimension=4, n_samples=1000, scramble=True, seed=42)
    
    # Simple identity lattice
    gram = np.eye(4) * 2
    
    n = 1073217479  # 30-bit gate
    samples, amplitudes = probe.probe_torus(n, gram)
    
    print(f"\nQMC Probe Results:")
    print(f"  Mean amplitude: {np.mean(amplitudes):.4f}")
    print(f"  Max amplitude: {np.max(amplitudes):.4f}")
    print(f"  Convergence error: {probe.convergence_error(amplitudes):.4e}")


if __name__ == "__main__":
    demonstrate()
