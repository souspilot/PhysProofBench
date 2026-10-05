# SM_01_006_001 — Ideal gas entropy from its equations of state

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Example 1.6, p. 9-10 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

An ideal gas obeys two equations of state, `pv = k_B T` and `e = c k_B T`
(`e`: energy per particle, `v`: volume per particle, `c`: specific heat
constant). Rewritten as statements about the entropy per particle `s(e, v)`,
they say `∂s/∂e = 1/T = c k_B / e` and `∂s/∂v = p/T = k_B / v`. Assuming these
hold for all positive `e` and `v`, the entropy is determined up to a constant:
`s(e, v) - s(e₀, v₀) = c k_B log(e/e₀) + k_B log(v/v₀)` for any reference
point `(e₀, v₀)`.

## proof

Divide the two equations of state by `T` to express `1/T` and `p/T` in terms of
`e` and `v`. These are the partial derivatives of the entropy per particle, so
`ds = (c k_B / e) de + (k_B / v) dv`. Integrating from a reference point
`(e₀, v₀)` gives `s(e, v) - s₀ = c k_B log(e/e₀) + k_B log(v/v₀)`. Multiplying by
`N` and using homogeneity gives the fundamental relation for `S(U, V, N)`.
