# Review: PI_A_002

## AI review (2026-10-26)

**1. Physics check: PASS.** Independently verified the exact
`C_V/(3Nk_B) = α²e^α/(e^α-1)² = 1 - α²/12 + α⁴/240 - …`, matching `b = -1/12, n = 2`.
`dS/dm = ln((3N+m)/m)` is correct for the given entropy.

**2. Plug-in check: PASS (strong).** Two natural shortcuts both fail. Quoting
Dulong–Petit gives no correction. Expanding `m` to first order gives `E`
linear in `T` and hence `C_V = 3Nk_B` exactly: the linear-in-α term is
absent, which tempts a wrong `n = 1`. The solver has to track orders.

**3. Formalization check: OK with notes.**
- Starting from entropy plus the first law (rather than the closed form of
  `C_V`) keeps the thermodynamic step inside the task. Good.
- `hdiff` (differentiability of `m(T)`) is an `encoding_artifact`; it
  follows from the implicit function theorem, but providing it is harmless.
- `hm_pos` and `hfirst` pin `m(T) = 3N/(e^α - 1)` uniquely (`ln((3N+m)/m)`
  is strictly decreasing in `m > 0`). Non-vacuity witness: that `m`.
- Uniqueness of `(b, n)`: holds because `b ≠ 0` and `n > 0`.

**4. Category check: PASS.** Leading-order expansion, specifically the
classical limit of a quantum system. A crisp "physics regime" item.

**Verdict: accept.** It's the strongest of the two category-A items.

## Human review

- [ ] accept / revise / reject:
- reason:
