# SM_01_009_001 — Maximum entropy is uniform

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Lemma 1.9, p. 21 (see `docs/SOURCE.md#sm`). Paraphrased per
`CONTRIBUTING.md` — not a transcription.

## statement

Fix a finite, nonempty set of microstates `Ω`. A probability distribution on
`Ω` is a function assigning each microstate a nonnegative weight so that the
weights sum to one. Among *all* such distributions, the uniform one — every
microstate weighted equally, `1/|Ω|` — is the unique distribution that
maximizes the Shannon entropy `S(μ) = -Σ_ω μ(ω) log μ(ω)`, and its entropy
value there equals `log |Ω|`.

## proof

Write `ψ(x) = -x log x`. Because `ψ` is concave on `[0, ∞)`, Jensen's
inequality applied with the *uniform* weights `1/|Ω|` over the *points*
`μ(ω)` gives

  (1/|Ω|) Σ_ω ψ(μ(ω))  ≤  ψ( (1/|Ω|) Σ_ω μ(ω) )  =  ψ(1/|Ω|),

using that the `μ(ω)` sum to 1. The left side is `S(μ)/|Ω|` and the right
side is `(1/|Ω|) log|Ω|`, so `S(μ) ≤ log|Ω|`.

Jensen's inequality is an equality exactly when the averaged points all
coincide — here, when `μ` is constant across `Ω`. A constant distribution
summing to 1 over `|Ω|` microstates must be the uniform one. So equality
`S(μ) = log|Ω|` holds iff `μ` is the uniform distribution, proving both
existence and uniqueness of the maximizer at once.

(This is the standard finite-alphabet maximum-entropy argument; the source
notes it justifies treating the microcanonical ensemble as the uniform
distribution on its energy shell, via the Maximum Entropy Principle.)
