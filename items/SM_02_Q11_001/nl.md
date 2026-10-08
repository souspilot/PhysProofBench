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

## proof

Following the source's main-text remark that (2.11) follows from Stirling's formula, expanded by the contributor using the source's Lemma B.3 (the source leaves it as Exercise 2.1 and gives no solution); paraphrased, not transcribed.

If `k = 0` or `k = N`, the binomial coefficient is `1` and `s(m) = 0` (with
`0 log 0 = 0`), so both bounds hold for any `c₋ ≤ 1 ≤ c₊`.

For `1 ≤ k ≤ N - 1`, write `p = k/N`, so that `m = 2p - 1` and
`s(m) = -p log p - (1-p) log(1-p)`. The source's two-sided Stirling bounds
(Lemma B.3: `n!` lies between `e^{1/(12n+1)}` and `e^{1/(12n)}` times
`√(2πn) nⁿ e⁻ⁿ`) apply to `N!`, `k!` and `(N-k)!`. In the ratio
`N!/(k!(N-k)!)`, the factors `nⁿ e⁻ⁿ` combine exactly into
`p^{-k} (1-p)^{-(N-k)} = e^{N s(m)}`. What remains is the square-root
prefactor `√(N/(2π k(N-k)))`, times correction factors bounded above and
below by absolute constants. Since `k(N-k) ≥ N - 1 ≥ N/2` and `k(N-k) ≤ N²/4`,
the prefactor lies between a constant times `N^{-1/2}` and an absolute
constant. This gives `c₋ N^{-1/2} e^{N s(m)} ≤ (N choose k) ≤ c₊ e^{N s(m)}`.
