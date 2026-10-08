# CAN_00_003_001 — Hard-core lattice gas partition function

Canary item: a trivial pipeline sanity check, not part of the
benchmark (`docs/SOURCE.md#can`). Statement and proof written by the
contributor.

## statement

For the hard-core lattice gas in `V` cells, the grand canonical partition function `Σ_{N=0}^{V} (V choose N) e^{βμN}` equals `(1 + e^{βμ})^V`.

## proof

Write `e^{βμN} = (e^{βμ})^N`. The sum is then exactly the binomial expansion of `(1 + e^{βμ})^V`.
