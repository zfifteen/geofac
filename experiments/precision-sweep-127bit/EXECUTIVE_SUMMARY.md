# Executive Summary — Precision Sweep (127-bit)

**Result:** Precision is **not** the bottleneck. From 100→400 dps, the GVA
geodesic peak around the known factor is completely flat: peak amplitude
0.9637, width 1,000, residual 0.03768, and the peak stays offset by 290 from
pₜᵣᵤₑ. No improvement appears past the suggested 260 dps mark.

**Implication:** Raising precision alone will not recover the 127-bit signal.
The stable residual and broad peak indicate a shape/curvature issue in the
kernel, not arithmetic noise or sampling density.

**Evidence (from `precision_sweep_127bit.jsonl`):**
- `best_residual`: 0.03768 for all dps ∈ [100, 400]
- `peak_amp`: 0.96369 for all dps
- `peak_width`: 1000 integers (±500 window) for all dps
- `found`: false; peak sits at 10508623501177419369 (offset −290)

**Next actions:**
1) Prototype a small curvature correction term in the kernel (see PR body) and
   re-run the sweep to see if the peak recenters/narrows.
2) Add a CI micro-check running dps {180, 240, 260} to guard against regressions
   once curvature tweaks are applied.
