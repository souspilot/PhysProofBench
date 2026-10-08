# CAN_00_001_001 — Uniform distribution is a probability distribution

Canary item: a trivial pipeline sanity check, not part of the
benchmark (`docs/SOURCE.md#can`). Statement and proof written by the
contributor.

## statement

On a finite, nonempty set `Ω`, the uniform distribution (weight `1/|Ω|` on every point) is a probability distribution: all weights are nonnegative and they sum to one.

## proof

Each weight `1/|Ω|` is positive because `|Ω| ≥ 1`. There are `|Ω|` equal weights, so they sum to `|Ω| · (1/|Ω|) = 1`.
