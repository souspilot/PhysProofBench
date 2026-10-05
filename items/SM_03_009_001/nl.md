# SM_03_009_001 — Pressure of the one-dimensional Ising model

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Theorem 3.9, p. 90-91 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

Take the one-dimensional Ising model on a ring of `n` sites (periodic boundary
condition), with nearest-neighbour coupling `β ≥ 0` and field `h`. As the ring
grows (`n → ∞`), the pressure `n⁻¹ log Z_n` converges to
`log(e^β cosh h + √(e^{2β} cosh² h - 2 sinh 2β))`. In particular, the limiting
pressure is an explicit analytic function of `h`, so the 1D model has no
phase transition.

## proof

On a ring, the partition function is a sum over spins of a product of factors,
each depending on two neighbouring spins. That is exactly the trace of the
`n`-th power of a 2×2 "transfer matrix" whose entries are
`exp(±β ± h)`-type Boltzmann factors. Diagonalizing this matrix, the partition
function equals `λ₊ⁿ + λ₋ⁿ`, where `λ± = e^β cosh h ± √(e^{2β} cosh² h - 2 sinh 2β)`
are its eigenvalues. Since `λ₊ > |λ₋|`, the `λ₊ⁿ` term dominates, and
`n⁻¹ log Z_n → log λ₊`.
