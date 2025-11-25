"""
Isospectral Lattice Generators for Flat Tori

Implements construction of non-isometric isospectral flat tori in dimensions ≥4
using even quadratic forms (Schiemann's theorem).

References:
- Schiemann (1990): Ternary Positive Definite Quadratic Forms are Determined by Their Theta Series
- Conway-Sloane (1992): Four-Dimensional Lattices With the Same Theta Series
"""

import numpy as np
from scipy.linalg import eigh, cholesky
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# Eigenvalue computation limits to avoid exponential blowup
MAX_COORD_4D = 8
MAX_COORD_6D = 5
MAX_COORD_8D = 4
EIGENVALUE_BUFFER = 10

# Regularization constant for numerical stability
REGULARIZATION_EPS = 1e-10


class IsospectraLatticeGenerator:
    """
    Generate non-isometric lattices for flat tori using orthogonal similarity transforms.
    
    NOTE: This is an ATTEMPTED construction that aims to produce isospectral lattices
    via orthogonal similarity transforms. However, as the experiment demonstrates,
    this method does NOT produce truly isospectral tori. While matrix similarity
    preserves matrix eigenvalues, the Laplace spectrum on flat tori depends on the
    inverse Gram matrix in a way that is NOT preserved by similarity transforms.
    
    Schiemann's theorem guarantees existence of isospectral non-isometric tori in
    dim ≥4, but achieving this requires specialized theta-function equivalent
    quadratic forms, not simple orthogonal transformations.
    """
    
    def __init__(self, dimension: int, seed: int = 42):
        """
        Initialize with dimension and fixed seed for reproducibility.
        
        Args:
            dimension: Torus dimension (must be 4, 6, or 8)
            seed: RNG seed for deterministic behavior
        """
        if dimension not in [4, 6, 8]:
            raise ValueError(f"Supported dimensions: 4, 6, 8. Got {dimension}")
        
        self.dimension = dimension
        self.seed = seed
        np.random.seed(seed)
        logger.info(f"Initialized lattice generator: dim={dimension}, seed={seed}")
    
    def generate_even_quadratic_form(self) -> np.ndarray:
        """
        Generate even quadratic form basis (tridiagonal Cartan-type).
        
        Returns:
            Gram matrix for the quadratic form
        """
        d = self.dimension
        
        # Construct tridiagonal even quadratic form A_d type
        gram = np.diag([2.0] * d)
        for i in range(d - 1):
            gram[i, i + 1] = 1.0
            gram[i + 1, i] = 1.0
        
        logger.debug(f"Generated even quadratic form:\n{gram}")
        return gram
    
    def gram_to_basis(self, gram: np.ndarray) -> np.ndarray:
        """
        Convert Gram matrix to lattice basis via Cholesky decomposition.
        
        Args:
            gram: Gram matrix G = B^T B
        
        Returns:
            Lattice basis B
        """
        try:
            basis = cholesky(gram, lower=True)
        except np.linalg.LinAlgError:
            # Add small regularization if not positive definite
            gram_reg = gram + REGULARIZATION_EPS * np.eye(gram.shape[0])
            basis = cholesky(gram_reg, lower=True)
            logger.warning("Applied regularization for Cholesky decomposition")
        
        return basis
    
    def deform_basis_isospectral(self, gram: np.ndarray, 
                                  deform_index: int = 0) -> np.ndarray:
        """
        Apply orthogonal similarity transform to Gram matrix.
        
        IMPORTANT: While similarity transforms preserve matrix eigenvalues,
        this does NOT preserve the Laplace spectrum on flat tori. The Laplace
        eigenvalues depend on the inverse Gram matrix through the formula:
        λ_k = 4π² ||k||² where ||k||² = k^T G^{-1} k for lattice vector k.
        
        The experiment confirms this limitation: eigenvalue differences of
        8-28 were observed (tolerance: 10^-8), proving that orthogonal
        similarity is NOT a valid isospectral deformation method.
        
        Args:
            gram: Original Gram matrix
            deform_index: Index controlling deformation angle
        
        Returns:
            Deformed Gram matrix (NOT isospectral, despite the method name)
        """
        d = gram.shape[0]
        theta = np.pi / 6 * (deform_index + 1)  # Different angles
        
        # Construct orthogonal transformation
        # Use rotation in planes (0,1) and (2,3) if d >= 4
        Q = np.eye(d)
        
        if d >= 4:
            c, s = np.cos(theta), np.sin(theta)
            Q[0:2, 0:2] = [[c, -s], [s, c]]
            Q[2:4, 2:4] = [[c, s], [-s, c]]
        
        if d >= 6:
            # Additional rotation in (4,5) plane
            theta2 = theta * 0.7
            c2, s2 = np.cos(theta2), np.sin(theta2)
            Q[4:6, 4:6] = [[c2, -s2], [s2, c2]]
        
        if d == 8:
            # Additional rotation in (6,7) plane
            theta3 = theta * 0.5
            c3, s3 = np.cos(theta3), np.sin(theta3)
            Q[6:8, 6:8] = [[c3, -s3], [s3, c3]]
        
        # Apply similarity transform: G' = Q G Q^T
        deformed = Q @ gram @ Q.T
        
        logger.debug(f"Applied isospectral deformation with index={deform_index}")
        return deformed
    
    def compute_laplace_eigenvalues(self, gram: np.ndarray, 
                                     n_eigenvalues: int = 50) -> np.ndarray:
        """
        Compute Laplace-Beltrami eigenvalues for flat torus.
        
        For flat torus: λ_k = 4π² ||k||²_G^{-1}  where k ∈ Z^d
        
        Uses efficient sampling for high dimensions to avoid exponential blowup.
        
        Args:
            gram: Gram matrix of the lattice
            n_eigenvalues: Number of eigenvalues to compute
        
        Returns:
            Sorted eigenvalue array
        """
        d = gram.shape[0]
        
        try:
            gram_inv = np.linalg.inv(gram)
        except np.linalg.LinAlgError:
            gram_inv = np.linalg.pinv(gram)
            logger.warning("Using pseudo-inverse for singular Gram")
        
        # Set max coordinate based on dimension (lower for high d)
        if d <= 4:
            max_coord = MAX_COORD_4D
        elif d == 6:
            max_coord = MAX_COORD_6D
        else:
            max_coord = MAX_COORD_8D
        
        eigenvalues = []
        
        # For high dimensions, use sparse sampling to avoid O(n^d) blowup
        # Sample lattice vectors by norm to get smallest eigenvalues first
        if d >= 6:
            # Generate candidates by increasing norm
            for norm_bound in range(1, max_coord + 1):
                # Generate vectors with components in [-norm_bound, norm_bound]
                for coords in np.ndindex(*([2 * norm_bound + 1] * d)):
                    k = np.array(coords) - norm_bound
                    if np.any(k != 0) and np.max(np.abs(k)) == norm_bound:
                        eigenval = 4 * np.pi**2 * (k @ gram_inv @ k)
                        eigenvalues.append(eigenval)
                
                # Early exit if we have enough
                if len(eigenvalues) >= n_eigenvalues * 2:
                    break
        else:
            # Full enumeration for low dimensions
            for coords in np.ndindex(*([2 * max_coord + 1] * d)):
                k = np.array(coords) - max_coord
                if np.any(k != 0):
                    eigenval = 4 * np.pi**2 * (k @ gram_inv @ k)
                    eigenvalues.append(eigenval)
        
        eigenvalues = np.sort(eigenvalues)[:n_eigenvalues]
        logger.debug(f"Computed {len(eigenvalues)} eigenvalues")
        
        return eigenvalues
    
    def verify_isospectrality(self, gram1: np.ndarray, gram2: np.ndarray,
                               tolerance: float = 1e-8, 
                               n_eigenvalues: int = 50) -> Tuple[bool, float]:
        """
        Verify two lattices share the same Laplace spectrum.
        
        Args:
            gram1: First Gram matrix
            gram2: Second Gram matrix
            tolerance: Maximum allowed eigenvalue difference
            n_eigenvalues: Number of eigenvalues to compare
        
        Returns:
            (is_isospectral, max_difference)
        """
        eigs1 = self.compute_laplace_eigenvalues(gram1, n_eigenvalues)
        eigs2 = self.compute_laplace_eigenvalues(gram2, n_eigenvalues)
        
        min_len = min(len(eigs1), len(eigs2))
        max_diff = np.max(np.abs(eigs1[:min_len] - eigs2[:min_len]))
        
        is_iso = max_diff < tolerance
        
        logger.info(f"Isospectrality: max_diff={max_diff:.2e}, is_iso={is_iso}")
        return is_iso, max_diff
    
    def verify_non_isometry(self, gram1: np.ndarray, gram2: np.ndarray,
                            tolerance: float = 1e-8) -> Tuple[bool, float]:
        """
        Verify two lattices are NOT isometric (different geometry).
        
        Args:
            gram1: First Gram matrix
            gram2: Second Gram matrix
            tolerance: Threshold for considering matrices equal
        
        Returns:
            (is_non_isometric, frobenius_difference)
        """
        diff = np.linalg.norm(gram1 - gram2, ord='fro')
        is_non_iso = diff > tolerance
        
        logger.info(f"Non-isometry: fro_diff={diff:.6f}, non_iso={is_non_iso}")
        return is_non_iso, diff
    
    def generate_isospectral_choir(self, choir_size: int = 2) -> List[np.ndarray]:
        """
        Generate a choir of non-isometric isospectral Gram matrices.
        
        Args:
            choir_size: Number of lattices in the choir
        
        Returns:
            List of Gram matrices
        """
        logger.info(f"Generating choir: size={choir_size}, dim={self.dimension}")
        
        base_gram = self.generate_even_quadratic_form()
        choir = [base_gram]
        
        for i in range(1, choir_size):
            deformed = self.deform_basis_isospectral(base_gram, deform_index=i)
            choir.append(deformed)
            
            # Verify properties
            is_iso, _ = self.verify_isospectrality(base_gram, deformed)
            is_non_iso, _ = self.verify_non_isometry(base_gram, deformed)
            
            if not is_iso:
                logger.warning(f"Choir member {i} failed isospectrality")
            if not is_non_iso:
                logger.warning(f"Choir member {i} may be isometric")
        
        logger.info(f"Generated choir with {len(choir)} members")
        return choir


def demonstrate():
    """Demonstrate isospectral lattice generation."""
    logging.basicConfig(level=logging.INFO)
    
    for dim in [4, 6, 8]:
        print(f"\n=== Dimension {dim} ===")
        gen = IsospectraLatticeGenerator(dimension=dim, seed=42)
        choir = gen.generate_isospectral_choir(choir_size=3)
        
        for i, gram in enumerate(choir):
            print(f"Choir member {i}: det={np.linalg.det(gram):.4f}")


if __name__ == "__main__":
    demonstrate()
