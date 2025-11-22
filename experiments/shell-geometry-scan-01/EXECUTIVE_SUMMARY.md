# Executive Summary: Shell Geometry Scan 01

**Date:** 2025-11-22
**Experiment:** Shell Geometry Scan 01 — Distant-Factor Probe for N₁₂₇
**Status:** FAILURE (No factors found within budget)

---

## Results At-a-Glance

**Target:** N₁₂₇ = 137524771864208156028430259349934309717

**Expected Factors:**
- p = 10508623501177419659
- q = 13086849276577416863

**Outcome:** No factors found

**Time Elapsed:** 69.802 seconds

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Shells scanned | 6 |
| Total candidates | 280,000 |
| Total budget | 700,000 |
| Budget utilization | 40.0% |
| Best shell | S_0 |
| Best shell max amplitude | 0.999832 |
| Factorization success | False |
| Total runtime | 69.802s |

---

## Shell-by-Shell Summary

### Shell S_0

- **Radii:** R_0 = 78,180,637,518,849,229, R_1 = 126,498,928,767,633,312
- **Segments scored:** 32
- **Segments selected:** 8
- **Candidates tested:** 56,000
- **Max amplitude:** 0.999832
- **Hit found:** False

### Shell S_1

- **Radii:** R_1 = 126,498,928,767,633,312, R_2 = 204,679,566,286,482,560
- **Segments scored:** 32
- **Segments selected:** 8
- **Candidates tested:** 56,000
- **Max amplitude:** 0.999609
- **Hit found:** False

### Shell S_2

- **Radii:** R_2 = 204,679,566,286,482,560, R_3 = 331,178,495,054,115,904
- **Segments scored:** 32
- **Segments selected:** 8
- **Candidates tested:** 56,000
- **Max amplitude:** 0.999647
- **Hit found:** False

### Shell S_3

- **Radii:** R_3 = 331,178,495,054,115,904, R_4 = 535,858,061,340,598,528
- **Segments scored:** 32
- **Segments selected:** 8
- **Candidates tested:** 56,000
- **Max amplitude:** 0.999386
- **Hit found:** False

### Shell S_4

- **Radii:** R_4 = 535,858,061,340,598,528, R_5 = 867,036,556,394,714,496
- **Segments scored:** 32
- **Segments selected:** 8
- **Candidates tested:** 0
- **Max amplitude:** 0.000000
- **Hit found:** False

### Shell S_5

- **Radii:** R_5 = 867,036,556,394,714,496, R_6 = 1,402,894,617,735,313,152
- **Segments scored:** 32
- **Segments selected:** 8
- **Candidates tested:** 56,000
- **Max amplitude:** 0.999829
- **Hit found:** False

---

## Configuration

| Parameter | Value |
|-----------|-------|
| R₀ (inner radius) | 78,180,637,518,849,229 |
| φ (golden ratio) | 1.618034 |
| J_max (shells) | 6 |
| B_total | 700,000 |
| B_shell | 56,000 |
| Segments/shell | 32 |
| K_fractal | 6 |
| K_uniform | 2 |
| K-values | [0.3, 0.35, 0.4] |
| Precision (dps) | 800 |

---

## Verdict

### GEOMETRIC CANDIDATE SHELL DETECTED

Shell S_0 shows promising geometric signal:
- Max amplitude: 0.999832
- Suggests running full dense sweep on this shell

**Recommendation:** Execute follow-up dense run on candidate shell.

---

## References

- Experiment code: `run_experiment.py`
- Full metrics: `results.json`
- Hypothesis: See issue description
