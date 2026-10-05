# SM_01_E05_001 — Van der Waals critical temperature

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Exercise 1.5, p. 15 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

The Van der Waals equation of state (eqn. 1.23 of the source) gives the pressure
of a gas as a function of specific volume `v` and temperature `T`:
`p(v, T) = k_B T / (v - b) - a / v²`, for `v > b`, where `a > 0` (attraction
strength) and `b > 0` (excluded volume) are constants. Set
`T_c = 8a / (27 k_B b)`. Then:

- if `T > T_c`, pressure strictly decreases as `v` increases, over the whole
  range `v > b`;
- if `0 < T < T_c`, there is some interval of volumes `[v₁, v₂]` with
  `b < v₁ < v₂` on which pressure strictly *increases* with `v`. This is the
  unphysical region that violates thermodynamic stability.
