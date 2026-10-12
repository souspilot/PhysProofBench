# CAN_00_006_001 — Powers of two grow at least linearly

Canary item: a trivial pipeline sanity check in plain Mathlib (no
PhysProofBench definitions), not part of the benchmark
(`docs/SOURCE.md#can`). Written by the contributor.

## statement

For every natural number `n`, `n + 1 ≤ 2ⁿ`.

## proof

Induction on `n`. For `n = 0`, both sides equal `1`. If `n + 1 ≤ 2ⁿ`, then `2ⁿ⁺¹ = 2 · 2ⁿ ≥ 2(n + 1) ≥ n + 2`.
