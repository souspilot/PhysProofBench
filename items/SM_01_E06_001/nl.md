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
