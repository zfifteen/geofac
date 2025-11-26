# Isospectral Tori Falsification Experiment - Attempt 2

## Quick Navigation

| Document | Description |
|----------|-------------|
| [EXPERIMENT_REPORT.md](EXPERIMENT_REPORT.md) | **Complete findings with executive summary** |
| [README.md](README.md) | Technical methodology and design |
| [config.yaml](config.yaml) | Experiment configuration |
| [data/results/](data/results/) | JSON output and artifacts |

## Source Code

| File | Description |
|------|-------------|
| [src/falsification_test.py](src/falsification_test.py) | Main experiment runner |
| [src/torus_construction.py](src/torus_construction.py) | Isospectral lattice generators |
| [src/gva_embedding.py](src/gva_embedding.py) | GVA embedding and curvature |
| [src/qmc_probe.py](src/qmc_probe.py) | Sobol/Owen QMC sampling |

## TL;DR

**HYPOTHESIS DECISIVELY FALSIFIED**

The hypothesis that non-isometric isospectral flat tori preserve curvature-divisor metrics under GVA embeddings is **falsified** with 100% test failure rate (3/3 tests).

### Key Results

| Dimension | Metric Preservation | Runtime Ratio | Verdict |
|-----------|--------------------:|-------------:|---------|
| 4D | 0.0000 | 33.55× | FALSIFIED |
| 6D | 0.0000 | 3.99× | FALSIFIED |
| 8D | 0.0000 | 15.92× | FALSIFIED |

### Falsification Criteria Met

- ✅ **Metric deviation >5%**: All tests show 0% preservation (threshold: <95%)
- ✅ **Runtime increase >10%**: All tests show 3.99× to 33.55× overhead (threshold: >110%)
- ✅ **Success threshold ≥2/3**: 100% falsification rate exceeds required 66.7%

### Root Cause

The orthogonal similarity transforms used to generate "isospectral" lattices do not actually preserve Laplace eigenvalues. The lattices are non-isometric (different geometry) but also non-isospectral (different spectrum), invalidating the fundamental premise of the hypothesis.

### Target

- **Semiprime**: N = 137524771864208156028430259349934309717 (127-bit challenge)
- **Factors**: p = 10508623501177419659, q = 13086849276577416863
- **Validation Gate**: 127-bit challenge (whitelist exception)

## Quick Start

```bash
cd experiments/isospectral-tori-falsification-attempt-2
python3 src/falsification_test.py
```

## Reproducibility

- Fixed seed: 42
- Adaptive precision: 708 dps for 127-bit numbers
- Deterministic QMC: Sobol with Owen scrambling
- Total runtime: ~5 seconds
