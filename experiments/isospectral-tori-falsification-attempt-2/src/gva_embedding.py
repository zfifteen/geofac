"""
GVA Embedding and Curvature Computation

Implements GVA (Geometric Value Analysis) embedding for integers into
toroidal coordinates with discrete curvature κ(n) = d(n) * ln(n+1) / e².

Precision follows: max(configured, N.bitLength * 4 + 200)
"""

import numpy as np
import mpmath as mp
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Regularization constant for numerical stability
REGULARIZATION_EPS = 1e-10


class GVAEmbedding:
    """
    GVA embedding for integers into high-dimensional tori.
    
    Uses adaptive precision: precision = max(base, bitLength * 4 + 200)
    """
    
    def __init__(self, base_precision: int = 200):
        """
        Initialize GVA embedding.
        
        Args:
            base_precision: Minimum decimal precision
        """
        self.base_precision = base_precision
        self._set_precision(base_precision)
        logger.info(f"Initialized GVA: base_precision={base_precision}")
    
    def _set_precision(self, precision: int):
        """Set mpmath precision."""
        self.current_precision = precision
        mp.mp.dps = precision
    
    def adaptive_precision(self, n: int) -> int:
        """
        Compute adaptive precision for given n.
        
        Formula: max(base_precision, bitLength * 4 + 200)
        
        Args:
            n: Target integer
        
        Returns:
            Required precision in decimal digits
        """
        bit_length = n.bit_length()
        required = max(self.base_precision, bit_length * 4 + 200)
        
        if required != self.current_precision:
            self._set_precision(required)
            logger.info(f"Adaptive precision: {required} dps for {bit_length}-bit n")
        
        return required
    
    def divisor_count(self, n: int, p: Optional[int] = None, 
                       q: Optional[int] = None) -> int:
        """
        Compute divisor count d(n).
        
        Args:
            n: Integer
            p: Optional first factor (for known semiprimes)
            q: Optional second factor
        
        Returns:
            Number of divisors
        """
        if n <= 0:
            return 0
        
        # Fast path: known semiprime
        if p is not None and q is not None:
            return 3 if p == q else 4  # 1, p, q, pq or 1, p, p²
        
        # Small n: direct computation
        if n < 10**6:
            count = sum(1 for i in range(1, int(n**0.5) + 1) if n % i == 0)
            count *= 2
            if int(n**0.5)**2 == n:
                count -= 1
            return count
        
        # Large unknown: assume prime (d=2)
        logger.debug(f"Assuming d(n)=2 for large n={n}")
        return 2
    
    def curvature(self, n: int, p: Optional[int] = None, 
                   q: Optional[int] = None) -> mp.mpf:
        """
        Compute discrete curvature κ(n) = d(n) * ln(n+1) / e².
        
        Args:
            n: Integer
            p: Optional first factor
            q: Optional second factor
        
        Returns:
            Curvature as high-precision float
        """
        self.adaptive_precision(n)
        
        d_n = self.divisor_count(n, p, q)
        kappa = mp.mpf(d_n) * mp.log(mp.mpf(n) + 1) / (mp.e ** 2)
        
        logger.debug(f"κ({n}) = {d_n} * ln({n}+1) / e² = {float(kappa):.6e}")
        return kappa
    
    def embed_in_torus(self, n: int, gram: np.ndarray) -> np.ndarray:
        """
        Embed integer n into torus defined by Gram matrix.
        
        Uses golden ratio quasi-random distribution scaled by curvature.
        
        Args:
            n: Integer to embed
            gram: Gram matrix defining the torus
        
        Returns:
            Toroidal coordinates (d-dimensional)
        """
        d = gram.shape[0]
        self.adaptive_precision(n)
        
        kappa = float(self.curvature(n))
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        
        # Quasi-random coordinates via golden ratio
        coords = np.array([(float(n) * (phi ** (i + 1))) % 1.0 for i in range(d)])
        coords *= kappa
        
        # Project onto fundamental domain
        basis = self._gram_to_basis(gram)
        try:
            lattice_coords = np.linalg.solve(basis, coords)
        except np.linalg.LinAlgError:
            lattice_coords = np.linalg.lstsq(basis, coords, rcond=None)[0]
        
        lattice_coords = lattice_coords % 1.0  # Periodic boundary
        embedded = basis @ lattice_coords
        
        return embedded
    
    def _gram_to_basis(self, gram: np.ndarray) -> np.ndarray:
        """Convert Gram matrix to basis via Cholesky."""
        try:
            return np.linalg.cholesky(gram)
        except np.linalg.LinAlgError:
            return np.linalg.cholesky(gram + REGULARIZATION_EPS * np.eye(gram.shape[0]))
    
    def geodesic_distance(self, coords1: np.ndarray, coords2: np.ndarray,
                           gram: np.ndarray) -> float:
        """
        Compute geodesic distance on flat torus.
        
        Uses minimum image convention for periodic boundaries.
        
        Args:
            coords1: First point
            coords2: Second point
            gram: Gram matrix of the torus
        
        Returns:
            Geodesic distance
        """
        basis = self._gram_to_basis(gram)
        
        try:
            lat1 = np.linalg.solve(basis, coords1)
            lat2 = np.linalg.solve(basis, coords2)
        except np.linalg.LinAlgError:
            lat1 = np.linalg.lstsq(basis, coords1, rcond=None)[0]
            lat2 = np.linalg.lstsq(basis, coords2, rcond=None)[0]
        
        # Minimum image: wrap to [-0.5, 0.5]
        diff = lat1 - lat2
        diff = diff - np.round(diff)
        
        euclidean_diff = basis @ diff
        return float(np.linalg.norm(euclidean_diff))
    
    def metric_preservation_ratio(self, n: int, p: int, q: int,
                                   choir: List[np.ndarray]) -> float:
        """
        Compute metric preservation ratio across isospectral choir.
        
        Measures how well curvature relationships are preserved under
        the GVA embedding into different isospectral tori.
        
        Args:
            n: Semiprime (n = p * q)
            p: First factor
            q: Second factor
            choir: List of isospectral Gram matrices
        
        Returns:
            Preservation ratio (1.0 = perfect preservation)
        """
        if len(choir) < 2:
            return 1.0
        
        self.adaptive_precision(n)
        
        # Compute curvatures
        kappa_n = float(self.curvature(n, p, q))
        kappa_p = float(self.curvature(p))
        kappa_q = float(self.curvature(q))
        
        # Expected relationship: κ(n) relates to κ(p) + κ(q)
        expected_ratio = kappa_n / (kappa_p + kappa_q) if (kappa_p + kappa_q) > 0 else 0
        
        # Embed in each choir member and measure distances
        ratios = []
        for gram in choir:
            coords_n = self.embed_in_torus(n, gram)
            coords_p = self.embed_in_torus(p, gram)
            coords_q = self.embed_in_torus(q, gram)
            
            dist_pq = self.geodesic_distance(coords_p, coords_q, gram)
            dist_n_origin = np.linalg.norm(coords_n)
            
            if dist_pq > 0 and dist_n_origin > 0:
                actual_ratio = dist_n_origin / dist_pq
                preservation = min(expected_ratio / actual_ratio, 
                                   actual_ratio / expected_ratio) if actual_ratio > 0 else 0
                ratios.append(preservation)
        
        mean_preservation = np.mean(ratios) if ratios else 0.0
        
        logger.info(f"Metric preservation: {mean_preservation:.4f} (n={n})")
        return float(mean_preservation)


def demonstrate():
    """Demonstrate GVA embedding."""
    logging.basicConfig(level=logging.INFO)
    
    # Define constants locally to avoid import issues when run as script
    CHALLENGE_127 = 137524771864208156028430259349934309717
    CHALLENGE_127_P = 10508623501177419659
    CHALLENGE_127_Q = 13086849276577416863
    
    gva = GVAEmbedding(base_precision=200)
    
    print("\n=== GVA Curvature Demo ===")
    
    # Small semiprime
    p_small, q_small = 32749, 32771
    n_small = p_small * q_small
    
    kappa = gva.curvature(n_small, p_small, q_small)
    print(f"κ({n_small}) = {float(kappa):.6e}")
    
    # 127-bit challenge
    precision = gva.adaptive_precision(CHALLENGE_127)
    print(f"\n127-bit challenge precision: {precision} dps")
    
    kappa_127 = gva.curvature(CHALLENGE_127, CHALLENGE_127_P, CHALLENGE_127_Q)
    print(f"κ(CHALLENGE_127) = {float(kappa_127):.6e}")


if __name__ == "__main__":
    demonstrate()
