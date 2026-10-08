# SM_01_E06_001 — Shannon entropy is concave

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Exercise 1.6, p. 21 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

Take a finite set of microstates `Ω` and two probability distributions `μ`, `ν`
on it. For any mixing weight `α` between 0 and 1, form the mixture that puts
weight `α μ(ω) + (1-α) ν(ω)` on each microstate. The Shannon entropy of the
mixture is at least the same convex combination of the two entropies,
`α S(μ) + (1-α) S(ν)`. In other words, `S` is a concave function on the set of
probability distributions.

## proof

Following the source's solution to Exercise 1.6 (Appendix C); paraphrased, not transcribed.

Write the Shannon entropy as a sum over microstates, `S(μ) = Σ_ω ψ(μ(ω))`,
with `ψ(x) = -x log x`. The function `ψ` is concave on `[0, ∞)`. For two
distributions `μ, ν` and `α ∈ [0, 1]`, apply concavity of `ψ` at each
microstate:
`ψ(α μ(ω) + (1-α) ν(ω)) ≥ α ψ(μ(ω)) + (1-α) ψ(ν(ω))`.
Summing over `ω` gives `S(α μ + (1-α) ν) ≥ α S(μ) + (1-α) S(ν)`.
