# Precision Sweep — 127-bit Challenge

Objective: determine whether higher arithmetic precision sharpens or diffuses
the GVA geodesic resonance near the 127-bit challenge factors.

This experiment sweeps mpmath precision from 100–400 dps while holding k,
window, and candidates constant. It measures peak amplitude and residual of the
geodesic distance profile around the known factor. A peak that tightens then
loosens beyond ~260 dps suggests the kernel needs curvature/shape correction
rather than more sampling.

## How to run

```bash
cd experiments/precision-sweep-127bit
python run_precision_sweep.py
```

Outputs (written to this directory):
- `precision_sweep_127bit.jsonl` — header + one record per precision
- `precision_sweep_127bit.png` — residual, width, amplitude vs dps (260 dps marker)

## Metrics captured
- `peak_amp`: max 1/(1+distance) amplitude in the window
- `peak_width`: contiguous integer width where amplitude ≥ half the peak
- `best_residual`: minimum torus distance observed
- `found`: whether the peak is at the true factor (p or q)
- `candidates`: total candidates scanned (fixed window)
- `ms`: runtime for that precision sweep

## Interpretation guide
- **Sampling-limited**: residual keeps falling and peak_amp/width keep
  improving through 400 dps.
- **Model-limited (curvature issue)**: residual bottoms out near ~260 dps while
  peak_amp stops improving or shrinks and width broadens.

## Next steps
- If model-limited behavior appears, prototype a small curvature term in the
  kernel (see PR description) and re-run the sweep for comparison.
