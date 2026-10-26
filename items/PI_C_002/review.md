# Review: PI_C_002

## AI review (2026-10-26)

**1. Physics check: PASS.** `T' = T - aN/(3kV)` confirmed. Entropy: verified
`dS = (dE + P dV)/T = (3/2)Nk dT/T + Nk dV/V` for this `E` and `P`, so
`S` has the ideal-gas form and `ΔS = Nk ln 2 + (3/2)Nk ln(1 - ε/3)`. To
first order this is `Nk ln 2 - aN²/(2VT)`, matching the official answer.
The stated error bound `Nk ε²` holds for `ε ≤ 1/2` (actual remainder
`≈ Nk ε²/12`). *Aside:* the official part c (a Bernoulli argument for the
wall pressure) is heuristic, but this item does not depend on it.

**2. Plug-in check: PASS.** The ideal-gas answer (`ΔT = 0`,
`ΔS = Nk ln 2`) is the obvious plug-in and is wrong at first order.

**3. Formalization check: OK for `T'`, CONCERN for entropy.**
- The `T'` theorem: `answer_blank` with a universal `c` is unique (take
  `a, N ≠ 0`). Non-vacuity: solve for `T'` directly.
- The entropy companion *gives* `S = Nk(ln V + (3/2) ln T)`, which skips the
  thermodynamic derivation (the interesting step: the attraction
  drops out of `S`). Revise it to state the first law and equation of state
  as hypotheses on an unknown `S`.

**4. Category check: PASS.** Reduced model = ideal gas, correction =
first order in interaction strength.

**Verdict: accept the `T'` statement; revise the entropy companion.**

## Human review

- [ ] accept / revise / reject:
- reason:
