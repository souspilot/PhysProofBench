# SM_03_005_001 — Finite-volume Ising pressure is convex

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Lemma 3.5, p. 84 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

Consider the Ising model on a finite set of sites `Λ` in `ℤᵈ`, with free
boundary condition: spins `±1` on the sites of `Λ`, nearest-neighbour coupling
of strength `β` inside `Λ` only, and external field `h`. Its finite-volume
pressure is `ψ_Λ(β, h) = |Λ|⁻¹ log Z_Λ(β, h)`. The claim is that `ψ_Λ` is
jointly convex in the pair `(β, h)`, on `β ≥ 0` and all real `h`.

## proof

The Hamiltonian depends affinely on the pair `(β, h)`, so each Boltzmann weight
`exp(-H)` is the exponential of an affine function of the parameters. For a
mixture `α(β₁, h₁) + (1-α)(β₂, h₂)`, split each weight as a product of the
`α`-th power of the first weight and the `(1-α)`-th power of the second, then
apply Hölder's inequality to the sum over configurations. This bounds the
partition function at the mixed parameters by the product of the two partition
functions raised to the powers `α` and `1-α`. Taking logarithms and dividing by
`|Λ|` gives convexity of `ψ_Λ`.
