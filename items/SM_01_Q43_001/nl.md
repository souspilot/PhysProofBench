# SM_01_Q43_001 — Ideal gas law from the hard-core lattice gas

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, eqn. (1.43) and following Taylor expansion (§1.3.2), p. 34 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

Model a gas as `V` cells, each holding at most one particle, with no other
interaction (the hard-core lattice gas), in the grand canonical ensemble at
inverse temperature `β > 0` and chemical potential `μ`. Let `p` be the pressure
`(βV)⁻¹ log Θ` and `ρ` the expected fraction of occupied cells. Then:

- pressure and density are tied by the exact isotherm `βp = -log(1 - ρ)`, for
  every `μ`;
- in the dilute regime (`μ → -∞`, so `ρ → 0`), `βp = ρ + O(ρ²)`. With
  `k_B T = 1/β` this is the ideal gas law `p = ρ k_B T` up to a second-order
  correction.

## proof

Since there is no interaction, the grand canonical partition function is a
binomial sum and equals `(1 + e^{βμ})^V`, so the pressure is
`β⁻¹ log(1 + e^{βμ})`. Differentiating `log Θ` in `μ` gives the mean particle
number, so the density is `e^{βμ} / (1 + e^{βμ})`. Solving this for `e^{βμ}` and
substituting back gives `βp = -log(1 - ρ)`. Expanding the logarithm for small
`ρ` gives `βp = ρ + O(ρ²)`, i.e. the ideal gas law.
