"""
Precision sweep for the 127-bit challenge (CHALLENGE_127).

Runs a lightweight, deterministic probe of the GVA kernel at varying
mpmath precisions (100 → 400 dps) while holding all other parameters
constant. Instead of a full factor search (too expensive for CI), it
measures how the geodesic amplitude profile around the known factor
changes with precision. A tightening-then-diffusing peak can signal a
curvature/shape issue rather than a sampling deficit.

Outputs
-------
- precision_sweep_127bit.jsonl : one JSON record per precision with metrics
- precision_sweep_127bit.png   : plot of residual, peak width, amplitude vs dps

Metrics
-------
- peak_amp: max 1/(1+distance) amplitude across the window
- peak_width: contiguous integer width where amplitude ≥ 0.5 * peak_amp
- best_residual: minimum torus distance observed (proxy for fit)
- found: whether the peak aligns with the true factor (p or q)
- candidates: number of candidates evaluated in the fixed window
- ms: runtime in milliseconds for the sweep at that precision

This harness is deterministic (no RNG/QMC seeds required). It reuses the
existing GVA embedding and distance functions from gva_factorization.py.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List
import sys

import mpmath as mp

# Ensure project root is on PYTHONPATH when running from this directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gva_factorization import embed_torus_geodesic, riemannian_distance

# Challenge parameters
CHALLENGE_127 = int("137524771864208156028430259349934309717")
P_TRUE = int("10508623501177419659")
Q_TRUE = int("13086849276577416863")

# Precision grid
DPS_LIST = [100, 140, 180, 220, 240, 260, 280, 320, 360, 400]

# Curvature correction knobs (variant 2 in PR guidance)
CURVATURE_ALPHA = 1e-3
CURVATURE_BETA = 0.1

# Fixed sampling window around the known factor. Width is small to keep the
# harness fast but still wide enough to observe peak shape changes.
OFFSETS = list(range(-500, 501, 10))  # 101 candidates, +/-500 around p_true
K_VALUE = 0.35  # use common k from prior experiments


@dataclass
class SweepResult:
    dps: int
    peak_amp: float
    peak_width: int
    best_residual: float
    refine_iters: int
    found: bool
    candidates: int
    ms: float
    peak_candidate: int
    variant: str  # 'baseline' or 'curvature'

    @staticmethod
    def header() -> Dict[str, str]:
        return {
            "type": "precision_sweep",
            "N": str(CHALLENGE_127),
            "p_true": str(P_TRUE),
            "q_true": str(Q_TRUE),
            "k": K_VALUE,
            "offset_range": f"{OFFSETS[0]}..{OFFSETS[-1]} step {OFFSETS[1]-OFFSETS[0]}",
            "curvature_alpha": CURVATURE_ALPHA,
            "curvature_beta": CURVATURE_BETA,
        }


def compute_peak_width(candidates: List[int], amplitudes: List[mp.mpf], peak_idx: int) -> int:
    peak_amp = amplitudes[peak_idx]
    half = peak_amp / 2

    start_idx = peak_idx
    while start_idx > 0 and amplitudes[start_idx - 1] >= half:
        start_idx -= 1

    end_idx = peak_idx
    last_idx = len(amplitudes) - 1
    while end_idx < last_idx and amplitudes[end_idx + 1] >= half:
        end_idx += 1

    return candidates[end_idx] - candidates[start_idx]


def apply_curvature(dist: mp.mpf) -> mp.mpf:
    """
    Minimal curvature correction: add small term scaled by ln(N)/N^beta.
    This follows the PR guidance (option 1) with fixed alpha, beta.
    """
    kappa = mp.log(CHALLENGE_127) / (mp.power(CHALLENGE_127, CURVATURE_BETA))
    return dist + (CURVATURE_ALPHA * kappa)


def run_once(dps: int, variant: str) -> SweepResult:
    mp.mp.dps = dps
    t0 = time.time()

    # Precompute embedding of N once per precision
    N_coords = embed_torus_geodesic(CHALLENGE_127, K_VALUE)

    candidates: List[int] = []
    amplitudes: List[mp.mpf] = []
    residuals: List[mp.mpf] = []

    for offset in OFFSETS:
        candidate = P_TRUE + offset
        cand_coords = embed_torus_geodesic(candidate, K_VALUE)
        dist = riemannian_distance(N_coords, cand_coords)
        if variant == "curvature":
            dist = apply_curvature(dist)
        amp = mp.mpf(1) / (mp.mpf(1) + dist)

        candidates.append(candidate)
        amplitudes.append(amp)
        residuals.append(dist)

    # Identify peak
    peak_idx = max(range(len(amplitudes)), key=lambda i: amplitudes[i])
    peak_amp = float(amplitudes[peak_idx])
    best_residual = float(residuals[peak_idx])
    peak_width = compute_peak_width(candidates, amplitudes, peak_idx)

    result = SweepResult(
        dps=dps,
        peak_amp=peak_amp,
        peak_width=int(peak_width),
        best_residual=best_residual,
        refine_iters=0,
        found=candidates[peak_idx] in (P_TRUE, Q_TRUE),
        candidates=len(candidates),
        ms=(time.time() - t0) * 1000.0,
        peak_candidate=candidates[peak_idx],
        variant=variant,
    )

    return result


def write_jsonl(results: List[SweepResult], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(SweepResult.header()) + "\n")
        for r in results:
            f.write(json.dumps(asdict(r)) + "\n")


def make_plot(results: List[SweepResult], path: Path) -> None:
    import matplotlib.pyplot as plt

    def series(field: str, variant: str) -> List[float]:
        return [getattr(r, field) for r in results if r.variant == variant]

    dps = [r.dps for r in results if r.variant == "baseline"]

    fig, ax1 = plt.subplots(figsize=(8, 4.5))

    ax1.plot(dps, series("best_residual", "baseline"), marker="o", color="#d62728", label="residual (base)")
    ax1.plot(dps, series("best_residual", "curvature"), marker="o", linestyle="--", color="#ff9896", label="residual (curv)")
    ax1.set_xlabel("mpmath precision (dps)")
    ax1.set_ylabel("Residual (torus distance)", color="#d62728")
    ax1.tick_params(axis="y", labelcolor="#d62728")

    ax2 = ax1.twinx()
    ax2.plot(dps, series("peak_amp", "baseline"), marker="s", color="#1f77b4", label="peak_amp (base)")
    ax2.plot(dps, series("peak_amp", "curvature"), marker="s", linestyle="--", color="#aec7e8", label="peak_amp (curv)")
    ax2.plot(dps, series("peak_width", "baseline"), marker="^", color="#2ca02c", label="peak_width (base)")
    ax2.plot(dps, series("peak_width", "curvature"), marker="^", linestyle="--", color="#98df8a", label="peak_width (curv)")
    ax2.set_ylabel("Amplitude / Width", color="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#1f77b4")

    ax1.axvline(260, color="#ff7f0e", linestyle="--", linewidth=1.2, label="260 dps")

    lines = ax1.get_lines() + ax2.get_lines()
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right")

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    out_dir = Path(__file__).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for variant in ("baseline", "curvature"):
        results.extend(run_once(dps, variant) for dps in DPS_LIST)

    jsonl_path = out_dir / "precision_sweep_127bit.jsonl"
    plot_path = out_dir / "precision_sweep_127bit.png"

    write_jsonl(results, jsonl_path)
    make_plot(results, plot_path)

    print(f"Wrote {jsonl_path} and {plot_path}")


if __name__ == "__main__":
    main()
