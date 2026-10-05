# SM_02_002_001 — Curie–Weiss magnetization concentrates at zero above T_c

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Theorem 2.2 (part 1), p. 60 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

The Curie–Weiss model replaces the nearest-neighbour Ising interaction in
dimension `d` by a mean-field one: each of `N` spins interacts equally with
every other spin, with strength `dβ/N`. Take zero external field and an
inverse temperature `β` between `0` and the critical value `β_c = 1/(2d)`
(i.e. at or above the critical temperature). Then the magnetization density
`m_N` (average spin) concentrates at zero exponentially fast. For each
tolerance `ε > 0` there is a rate `c > 0` such that, for all large enough `N`,
the Gibbs probability that `|m_N| < ε` is at least `1 - 2e^{-cN}`.

## proof

The magnetization only takes the values `-1 + 2k/N`, and the number of
configurations with a given value is a binomial coefficient. Since the
Hamiltonian depends on the configuration only through `m_N`, the law of `m_N`
is explicit. Using the Stirling-type bounds on binomial coefficients (eqn. 2.11 of
the source), the probability that `m_N` lies in a set `J` behaves like
`exp(-N · inf_J I)` on an exponential scale. Here `I` is a nonnegative rate
function built from the free energy `f(m) = -dβm² - s(m)`, and it vanishes
exactly at the global minimizers of `f`. Setting the derivative of `f` to zero
gives the mean-field equation `m = tanh(2dβm)`. When `2dβ ≤ 1` its only
solution is `m = 0`, so `I` is strictly positive, and bounded away from zero,
on the complement of `(-ε, ε)`. That complement is two intervals, which
accounts for the factor 2 in the final bound.
