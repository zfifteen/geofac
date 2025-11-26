# Executive Summary — Precision Sweep (127-bit)

**Result:** Precision is **not** the bottleneck. From 100→400 dps, the GVA
geodesic peak around the known factor is completely flat: peak amplitude
0.9637, width 1,000, residual 0.03768, and the peak stays offset by 290 from
pₜᵣᵤₑ. No improvement appears past the suggested 260 dps mark.

**Implication:** Raising precision alone will not recover the 127-bit signal.
The stable residual and broad peak indicate a shape/curvature issue in the
kernel, not arithmetic noise or sampling density.

**Curvature probe:** Added a minimal curvature term (`alpha=1e-3`, `beta=0.1`).
It barely changes the metrics (peak_amp 0.96368, residual 0.037689, same offset
−290). Conclusion: a stronger or differently shaped correction is required.

**Evidence (from `precision_sweep_127bit.jsonl`):**
- `best_residual`: baseline 0.037676, curvature 0.037689 for all dps
- `peak_amp`: baseline 0.963692, curvature 0.963679 for all dps
- `peak_width`: 1000 integers (±500 window) for all dps, both variants
- `found`: false; peak sits at 10508623501177419369 (offset −290)

**Next actions:**
1) Prototype a small curvature correction term in the kernel (see PR body) and
   re-run the sweep to see if the peak recenters/narrows. The current minimal
   term was too weak to move the signal.
2) Add a CI micro-check running dps {180, 240, 260} to guard against regressions
   once curvature tweaks are applied.
