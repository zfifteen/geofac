# Copilot instructions (geofac)

Purpose: Repository-wide rules for GitHub Copilot (Chat/CLI/editor) to enforce this codebase’s invariants and style.

Authoritative sources
- CODING_STYLE.md (canonical style and invariants)
- README.md (project overview, boundaries)

Non‑negotiable invariants
- Validation gate: work only on semiprimes in [1e14, 1e18]. Outside this range allowed only for the 127‑bit whitelist: CHALLENGE_127 = 137524771864208156028430259349934309717.
- No classical fallbacks: do not propose or insert Pollard’s Rho, trial division, ECM, or sieve methods.
- Deterministic/quasi‑deterministic methods only (e.g., Sobol/Halton sampling, Gaussian kernel resonance, phase‑corrected snap). No stochastic “try until it works.”
- Precision is explicit and adaptive: precision = max(configured, N.bitLength() × 4 + 200). In Java use BigDecimal with explicit MathContext; in Python use mpmath/mpfr with explicit mp.dps/bits. Log the chosen precision.

Reproducibility requirements
- Pin seeds; log exact parameters, thresholds, sample counts, and timeouts; include timestamps; export artifacts when applicable.
- Tests/benchmarks must state scale, parameters, and success criteria explicitly in output.

Coding style (what to generate)
- Smallest possible change; delete scaffolding that outlives its usefulness; no speculative “just in case” branches.
- Flatten control flow with guard clauses; prefer pure functions; collapse unearned branches.
- Names are plain language and precise; small, literal interfaces; code reads linearly.
- Use only RSA challenge numbers for semiprimes; no synthetic look‑alikes.

Scope and docs
- Label prototypes and narrow scope intentionally; define success criteria in measurable terms.
- Keep docs slim and canonical; reference CODING_STYLE.md and README.md instead of duplicating content.

Commits/PRs Copilot should suggest
- Single, surgical diffs tied to a demonstrated failure mode.
- Commit message format: 
  fix: <what> for <scale/domain>
  Root cause: <exact failure mode>
  Fix: <minimal change>
  Impact: <measurable improvement>
  Tested: <exact parameters, scale, result>
  Artifact: <where proof lives>

Default refusals
- Refuse requests that violate the gate/whitelist, add classical fallbacks, or broaden scope without proof.

References
- ./CODING_STYLE.md
- ./README.md

Timestamp
- 2025-11-13T02:26:04.322Z
