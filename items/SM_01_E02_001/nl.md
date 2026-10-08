# SM_01_E02_001 — Entropy is concave

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Exercise 1.2, p. 8 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

Let `S(U, V, N)` be a thermodynamic entropy that is positively homogeneous of
degree one (the result of the previous exercise) and superadditive: merging two
systems with macrostates `X` and `Y` into one gives entropy at least
`S(X) + S(Y)`. Then `S` is concave. For any macrostates `X₁`, `X₂` and any
`α` between 0 and 1, `S(αX₁ + (1-α)X₂) ≥ α S(X₁) + (1-α) S(X₂)`.

## proof

Following the source's solution to Exercise 1.2 (Appendix C); paraphrased, not transcribed.

Take macrostates `X₁, X₂` and `α ∈ (0, 1)`; the endpoint cases `α = 0, 1` are
trivial. The combined macrostate `α X₁ + (1-α) X₂` can be split into the two
parts `α X₁` and `(1-α) X₂`. Superadditivity (in the source: the entropy of
the whole is the maximum over all ways of partitioning it, so it is at least
the value of this particular partition) gives
`S(α X₁ + (1-α) X₂) ≥ S(α X₁) + S((1-α) X₂)`.
By positive homogeneity the right-hand side equals `α S(X₁) + (1-α) S(X₂)`,
which is the concavity inequality.
