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

## proof

Following the source's solution to Exercise 1.5 (Appendix C), with its graphical argument written out; paraphrased, not transcribed.

Differentiate the isotherm: `∂p/∂v = -k_B T/(v - b)² + 2a/v³` for `v > b`. It
vanishes exactly when `k_B T = g(v)`, where `g(v) = 2a(v - b)²/v³`. On `v > b`
the function `g` starts at `0` as `v → b`, increases to its maximum at
`v = 3b`, where `g(3b) = 8a/(27b)`, and decreases back to `0` as `v → ∞`. The
sign of `∂p/∂v` is the sign of `g(v) - k_B T`.

If `k_B T > 8a/(27b)`, i.e. `T > T_c`, then `g(v) < k_B T` everywhere, so
`∂p/∂v < 0` on all of `v > b` and pressure strictly decreases.

If `0 < T < T_c`, the horizontal line at height `k_B T` cuts the graph of `g`
twice. Between the two crossings `g(v) > k_B T`, so `∂p/∂v > 0` and pressure
strictly increases on an interval. The critical case is the tangency of the
line with the top of the graph, which gives `T_c = 8a/(27 k_B b)`.
