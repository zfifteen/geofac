"""
Falsification Test Runner

Orchestrates the isospectral tori falsification experiment for the
127-bit challenge semiprime.

Falsification Criteria:
- Metric deviation >5% (preservation ratio <0.95) falsifies preservation claim
- Runtime increase >10% (ratio >1.1) falsifies acceleration claim
- Success threshold: ≥2/3 test cases show deviation
"""

import json
import logging
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import yaml
from scipy import stats

# Ensure parent path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from torus_construction import IsospectraLatticeGenerator
from gva_embedding import GVAEmbedding
from qmc_probe import QMCProbe

logger = logging.getLogger(__name__)

# 127-bit challenge constants
CHALLENGE_127 = 137524771864208156028430259349934309717
CHALLENGE_127_P = 10508623501177419659
CHALLENGE_127_Q = 13086849276577416863


class FalsificationExperiment:
    """
    Main experiment runner for isospectral tori falsification.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize experiment with configuration.
        
        Args:
            config_path: Path to YAML config (uses defaults if None)
        """
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()
        
        self.results_dir = Path(self.config['output']['results_dir'])
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results = []
        self.experiment_log = []
        
        logger.info("Initialized FalsificationExperiment")
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'experiment': {
                'name': 'isospectral-tori-falsification-attempt-2',
                'version': '1.0',
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            'thresholds': {
                'metric_preservation': 0.95,
                'runtime_ratio': 1.1,
                'success_rate': 2/3
            },
            'qmc': {
                'base_samples': 5000,
                'scrambling': 'owen'
            },
            'gva': {
                'min_precision': 200,
                'precision_factor': 4
            },
            'statistics': {
                'ks_test_alpha': 0.05
            },
            'output': {
                'results_dir': 'data/results'
            }
        }
    
    def log_event(self, event: str, details: Dict = None):
        """Log experiment event with timestamp."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'details': details or {}
        }
        self.experiment_log.append(entry)
        logger.info(f"[{event}] {details}")
    
    def run_baseline(self, n: int, dimension: int, 
                     n_samples: int = 5000) -> Dict:
        """
        Run baseline test with identity lattice (isometric torus).
        
        Args:
            n: Target semiprime
            dimension: Torus dimension
            n_samples: QMC sample count
        
        Returns:
            Baseline results dict
        """
        self.log_event('baseline_start', {'dimension': dimension, 'n': n})
        
        start = time.time()
        
        # Identity Gram matrix (isometric baseline)
        gram = np.eye(dimension) * 2  # Scaled identity
        
        qmc = QMCProbe(dimension=dimension, n_samples=n_samples,
                       scramble=True, seed=42)
        
        samples, amplitudes = qmc.probe_torus(n, gram)
        
        runtime = time.time() - start
        
        baseline = {
            'dimension': dimension,
            'runtime_seconds': runtime,
            'mean_amplitude': float(np.mean(amplitudes)),
            'max_amplitude': float(np.max(amplitudes)),
            'convergence_error': float(qmc.convergence_error(amplitudes)),
            'n_samples': n_samples
        }
        
        self.log_event('baseline_complete', baseline)
        return baseline
    
    def run_isospectral_test(self, dimension: int, choir_size: int,
                             baseline: Dict) -> Dict:
        """
        Run isospectral test for given dimension.
        
        Args:
            dimension: Torus dimension (4, 6, or 8)
            choir_size: Number of isospectral tori
            baseline: Baseline results for comparison
        
        Returns:
            Test results dict
        """
        n = CHALLENGE_127
        p = CHALLENGE_127_P
        q = CHALLENGE_127_Q
        
        self.log_event('isospectral_test_start', {
            'dimension': dimension,
            'choir_size': choir_size,
            'n_bits': n.bit_length()
        })
        
        start = time.time()
        
        # Generate isospectral choir
        gen = IsospectraLatticeGenerator(dimension=dimension, seed=42)
        choir = gen.generate_isospectral_choir(choir_size=choir_size)
        
        # Verify isospectrality
        iso_checks = []
        for i in range(1, len(choir)):
            is_iso, max_diff = gen.verify_isospectrality(choir[0], choir[i])
            is_non_iso, fro_diff = gen.verify_non_isometry(choir[0], choir[i])
            iso_checks.append({
                'member': i,
                'isospectral': is_iso,
                'max_eigenvalue_diff': float(max_diff),
                'non_isometric': is_non_iso,
                'frobenius_diff': float(fro_diff)
            })
        
        # GVA metric preservation
        gva = GVAEmbedding(base_precision=self.config['gva']['min_precision'])
        precision_used = gva.adaptive_precision(n)
        
        preservation_ratio = gva.metric_preservation_ratio(n, p, q, choir)
        
        # QMC probing
        qmc = QMCProbe(dimension=dimension,
                       n_samples=self.config['qmc']['base_samples'],
                       scramble=True, seed=42)
        
        probe_results = qmc.probe_choir(n, choir)
        
        overlap_ratio, n_resonances = qmc.cross_validate_resonances(probe_results)
        
        runtime = time.time() - start
        
        # Compute metrics
        runtime_ratio = runtime / baseline['runtime_seconds']
        
        falsified_by_metric = preservation_ratio < self.config['thresholds']['metric_preservation']
        falsified_by_runtime = runtime_ratio > self.config['thresholds']['runtime_ratio']
        
        result = {
            'test_id': f'TC-{dimension}D',
            'dimension': dimension,
            'choir_size': choir_size,
            'n': str(n),
            'p': str(p),
            'q': str(q),
            'n_bits': n.bit_length(),
            'precision_used': precision_used,
            
            # Core metrics
            'metric_preservation_ratio': preservation_ratio,
            'runtime_seconds': runtime,
            'runtime_ratio': runtime_ratio,
            'spectral_overlap_ratio': overlap_ratio,
            'n_consistent_resonances': n_resonances,
            
            # Isospectrality verification
            'isospectrality_checks': iso_checks,
            
            # Falsification results
            'threshold_metric': self.config['thresholds']['metric_preservation'],
            'threshold_runtime': self.config['thresholds']['runtime_ratio'],
            'falsified_by_metric': falsified_by_metric,
            'falsified_by_runtime': falsified_by_runtime,
            'falsified': falsified_by_metric or falsified_by_runtime
        }
        
        self.log_event('isospectral_test_complete', {
            'test_id': result['test_id'],
            'preservation': preservation_ratio,
            'runtime_ratio': runtime_ratio,
            'falsified': result['falsified']
        })
        
        return result
    
    def statistical_validation(self, results: List[Dict]) -> Dict:
        """
        Run statistical validation on results.
        
        Performs Kolmogorov-Smirnov test on preservation ratios.
        
        Args:
            results: List of test results
        
        Returns:
            Statistical validation dict
        """
        preservation_ratios = [r['metric_preservation_ratio'] for r in results]
        
        # KS test against uniform distribution (null: random behavior)
        ks_stat, p_value = stats.kstest(preservation_ratios, 'uniform')
        
        alpha = self.config['statistics']['ks_test_alpha']
        rejects_null = p_value < alpha
        
        validation = {
            'n_samples': len(preservation_ratios),
            'preservation_ratios': preservation_ratios,
            'mean_preservation': float(np.mean(preservation_ratios)),
            'std_preservation': float(np.std(preservation_ratios)),
            'ks_statistic': float(ks_stat),
            'p_value': float(p_value),
            'alpha': alpha,
            'rejects_null_hypothesis': rejects_null,
            'interpretation': ('Preservation ratios differ significantly from random' 
                              if rejects_null else 
                              'Preservation ratios consistent with random behavior')
        }
        
        self.log_event('statistical_validation', validation)
        return validation
    
    def run_experiment(self) -> Dict:
        """
        Run the complete falsification experiment.
        
        Tests dimensions 4, 6, 8 with the 127-bit challenge semiprime.
        
        Returns:
            Complete experiment report
        """
        experiment_start = time.time()
        
        self.log_event('experiment_start', {
            'challenge': str(CHALLENGE_127),
            'p': str(CHALLENGE_127_P),
            'q': str(CHALLENGE_127_Q),
            'bits': CHALLENGE_127.bit_length()
        })
        
        # Test configurations: (dimension, choir_size)
        test_configs = [
            (4, 2),
            (6, 3),
            (8, 4)
        ]
        
        all_results = []
        
        for dimension, choir_size in test_configs:
            # Baseline for this dimension
            baseline = self.run_baseline(CHALLENGE_127, dimension,
                                         self.config['qmc']['base_samples'])
            
            # Isospectral test
            result = self.run_isospectral_test(dimension, choir_size, baseline)
            result['baseline'] = baseline
            all_results.append(result)
        
        # Statistical validation
        stat_validation = self.statistical_validation(all_results)
        
        # Summary
        n_total = len(all_results)
        n_falsified = sum(1 for r in all_results if r['falsified'])
        falsification_rate = n_falsified / n_total if n_total > 0 else 0
        
        hypothesis_falsified = falsification_rate >= self.config['thresholds']['success_rate']
        
        experiment_runtime = time.time() - experiment_start
        
        report = {
            'experiment': self.config['experiment'],
            'timestamp': datetime.now().isoformat(),
            'hypothesis': (
                "Non-isometric isospectral flat tori in dimensions ≥4 preserve "
                "curvature-divisor metrics under GVA embeddings and yield "
                "accelerated factor detection via parallel QMC cross-validation."
            ),
            'target': {
                'n': str(CHALLENGE_127),
                'p': str(CHALLENGE_127_P),
                'q': str(CHALLENGE_127_Q),
                'bits': CHALLENGE_127.bit_length(),
                'validation_gate': '127-bit challenge'
            },
            'falsification_criteria': {
                'metric_threshold': self.config['thresholds']['metric_preservation'],
                'runtime_threshold': self.config['thresholds']['runtime_ratio'],
                'success_threshold': self.config['thresholds']['success_rate']
            },
            'summary': {
                'total_tests': n_total,
                'falsified_count': n_falsified,
                'falsification_rate': falsification_rate,
                'hypothesis_falsified': hypothesis_falsified,
                'total_runtime_seconds': experiment_runtime
            },
            'test_results': all_results,
            'statistical_validation': stat_validation,
            'experiment_log': self.experiment_log
        }
        
        self.log_event('experiment_complete', {
            'falsified': hypothesis_falsified,
            'rate': falsification_rate,
            'runtime': experiment_runtime
        })
        
        return report
    
    def save_report(self, report: Dict, filename: str = None):
        """Save report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'falsification_report_{timestamp}.json'
        
        output_path = self.results_dir / filename
        
        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_types(v) for v in obj]
            return obj
        
        clean_report = convert_types(report)
        
        with open(output_path, 'w') as f:
            json.dump(clean_report, f, indent=2)
        
        logger.info(f"Report saved: {output_path}")
        return str(output_path)


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Determine config path
    script_dir = Path(__file__).parent.parent
    config_path = script_dir / 'config.yaml'
    
    if not config_path.exists():
        config_path = None
        logger.info("Using default configuration")
    
    # Run experiment
    experiment = FalsificationExperiment(str(config_path) if config_path else None)
    report = experiment.run_experiment()
    
    # Save report
    report_path = experiment.save_report(report)
    
    # Print summary
    print("\n" + "=" * 70)
    print("ISOSPECTRAL TORI FALSIFICATION EXPERIMENT - RESULTS")
    print("=" * 70)
    print(f"\nTarget: 127-bit challenge (N = {CHALLENGE_127})")
    print(f"Hypothesis: {report['hypothesis'][:80]}...")
    print(f"\nFalsification Criteria:")
    print(f"  - Metric preservation < {report['falsification_criteria']['metric_threshold']}")
    print(f"  - Runtime ratio > {report['falsification_criteria']['runtime_threshold']}")
    print(f"  - Success threshold: {report['falsification_criteria']['success_threshold']:.1%}")
    
    print(f"\nResults by Dimension:")
    for result in report['test_results']:
        status = "FALSIFIED" if result['falsified'] else "SUPPORTED"
        print(f"  {result['test_id']}: preservation={result['metric_preservation_ratio']:.4f}, "
              f"runtime_ratio={result['runtime_ratio']:.4f} -> {status}")
    
    print(f"\nSummary:")
    print(f"  Total tests: {report['summary']['total_tests']}")
    print(f"  Falsified: {report['summary']['falsified_count']}")
    print(f"  Falsification rate: {report['summary']['falsification_rate']:.1%}")
    
    verdict = "FALSIFIED" if report['summary']['hypothesis_falsified'] else "NOT FALSIFIED"
    print(f"\n  >>> HYPOTHESIS: {verdict} <<<")
    
    print(f"\nStatistical Validation:")
    print(f"  KS statistic: {report['statistical_validation']['ks_statistic']:.4f}")
    print(f"  p-value: {report['statistical_validation']['p_value']:.4f}")
    print(f"  Interpretation: {report['statistical_validation']['interpretation']}")
    
    print(f"\nReport saved to: {report_path}")
    print("=" * 70)
    
    return report


if __name__ == "__main__":
    main()
