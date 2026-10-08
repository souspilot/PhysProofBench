# SM_01_E03_001 — Free energy is concave in β, convex in (V, N)

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Exercise 1.3, p. 11-12 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

From a concave thermodynamic entropy `S(U, V, N)`, define
`F̂(β, V, N) = inf over energies U of {βU - S(U, V, N)}` (a Legendre-type
transform, eqn. 1.15 of the source), and assume this infimum is finite. Then
`F̂` is concave as a function of the intensive variable `β > 0` (for fixed `V`,
`N`), and jointly convex as a function of the extensive variables `(V, N)`
(for fixed `β`).

## proof

Following the source's solution to Exercise 1.3 (Appendix C); the convexity half expands the source's "similar argument"; paraphrased, not transcribed.

Concavity in `β`. Fix `V, N`, two inverse temperatures `β₁, β₂` and
`α ∈ [0, 1]`. For every energy `U`, the quantity
`(αβ₁ + (1-α)β₂) U - S(U, V, N)` splits as
`α (β₁U - S(U, V, N)) + (1-α) (β₂U - S(U, V, N))`, and each bracket is at least
the corresponding infimum `F̂(β₁, V, N)`, respectively `F̂(β₂, V, N)`. Taking
the infimum over `U` on the left gives
`F̂(αβ₁ + (1-α)β₂, V, N) ≥ α F̂(β₁, V, N) + (1-α) F̂(β₂, V, N)`.

Convexity in `(V, N)`. Fix `β` and two points `(V₁, N₁), (V₂, N₂)`. For any
energies `U₁, U₂`, concavity of `S` applied to the mixed macrostate gives
`β(αU₁ + (1-α)U₂) - S(αU₁ + (1-α)U₂, αV₁ + (1-α)V₂, αN₁ + (1-α)N₂)
≤ α (βU₁ - S(U₁, V₁, N₁)) + (1-α) (βU₂ - S(U₂, V₂, N₂))`.
The left side is at least `F̂` at the mixed `(V, N)`. Taking the infimum over
`U₁` and `U₂` on the right gives
`F̂(β, αV₁ + (1-α)V₂, αN₁ + (1-α)N₂) ≤ α F̂(β, V₁, N₁) + (1-α) F̂(β, V₂, N₂)`.
Both steps need the infima to be finite, so that they are real numbers.
