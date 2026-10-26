# Review: PI_E_001

## AI review (2026-10-26)

**1. Physics check: PASS.** `ε(t) = -(1/2)(2πGM/t)^{2/3}` and
`dε/dt = (1/3)(2πGM)^{2/3} t^{-5/3}` give `n = 5/3`, the canonical TDE
fall-back law. Literature caveat: real light curves deviate from `t^{-5/3}`
at early times and when the energy distribution isn't flat. The problem's
uniformity assumption is stated, so it's not hidden.

**2. Plug-in check: PASS (moderate).** No formula for this is on a
standard sheet; the solver must chain Kepler III with a change of variables.
A model that has memorized "TDEs go as t^{-5/3}" can state the answer, but
still has to prove it in Lean. That makes it a good recall-vs-derivation probe.

**3. Formalization check: OK with notes.**
- `Mret` is defined through `sSup` of the energies that have returned. This
  works because the period is increasing in `ε`, but the prover must
  establish that. That is a fair part of the task, though heavier than the
  physics.
- `keplerPeriod` hard-codes Kepler's law in terms of `ε`. Acceptable as
  "laws given".
- Non-vacuity: `Mret t := μ(ε(t) - ε_min)`.
- Uniqueness of `n`: `C t^{-n}` for all `t` in an interval pins `n`.

**4. Category check: PASS.** Scaling argument. Arguably also B (late-time
regime), but the content is the power law.

**Verdict: accept.**

## Human review

- [ ] accept / revise / reject:
- reason:
