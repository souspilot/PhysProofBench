# Review: PI_E_002

## AI review (2026-10-26)

**1. Physics check: PASS.** `R ∝ M^{-1/3}` is the standard
non-relativistic white-dwarf relation. The dimensional-analysis lemma is
correct. Normalizing `G = M = R = 1` by choosing `λM = 1/M`, `λL = 1/R`,
`λT² = GM/R³` gives `P = P(1,1,1)·GM²/R⁴`.

**2. Plug-in check: PASS.** The counter-intuitive sign of the exponent is
the point. Note the source's caveat: the argument needs uniform density
(a single relevant length); for stars with a dense core it fails. That
condition is encoded in the statement through `Pc` depending only on
`(G, M, R)`.

**3. Formalization check: GOOD (after one revision during review).** The
first draft gave `P = CGM²/R⁴` as a hypothesis, which made the main
theorem algebra. It now takes only `DimCovariant Pc`, so the prover must
*do* the dimensional analysis. `DimCovariant` is a reusable Core
definition candidate for all of category E. Non-vacuity:
`Pc G M R = G M²/R⁴`, `Rad M = (K/G) M^{-1/3}`. Encoding note: `0 < Pc 1 1 1`
is needed to exclude the degenerate `Pc ≡ 0`.

**4. Category check: PASS.** Dimensional analysis in its purest form.

**Verdict: accept.** Promote `DimCovariant` to `Core/` if more E items use it.

## Human review

- [ ] accept / revise / reject:
- reason:
