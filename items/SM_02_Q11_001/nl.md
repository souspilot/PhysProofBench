# SM_02_Q11_001 — Stirling bounds on binomial coefficients

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, eqn. (2.11) / Exercise 2.1, p. 62 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

For a system of `N` spins, the number of configurations with exactly `k`
up-spins is the binomial coefficient `(N choose k)`. The corresponding
magnetization is `m = 2k/N - 1`. Let
`s(m) = -((1-m)/2) log((1-m)/2) - ((1+m)/2) log((1+m)/2)` be the
Curie–Weiss entropy function. The claim is that `(N choose k)` equals
`e^{N s(m)}` up to at most a polynomial factor, uniformly. There exist
constants `c₋, c₊ > 0` such that, for every `N ≥ 1` and every `k` from `0` to
`N`, `c₋ N^{-1/2} e^{N s(m)} ≤ (N choose k) ≤ c₊ e^{N s(m)}`.
