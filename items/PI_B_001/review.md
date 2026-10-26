# Review: PI_B_001

## AI review (2026-10-26)

**1. Physics check: PASS, with a finding against the source.** Recomputed
`Q₁, Q₂, W` and `η/η_C = (1+β)ln α / ((5/2)β + (1+β)ln α)`. This ratio is a
function of `x = β/((1+β)ln α)` alone, so `η → η_C ⇔ x → 0`. The official
solution's extra requirement `|Q₃| ≪ |Q₄|` (giving `β ≪ ln α`) does not
affect the efficiency. It coincides with the sharp condition when `β = O(1)`
but is strictly stronger when `β ≫ 1`. Example: `β = 1000, ln α = 100`
gives `η/η_C ≈ 0.976`, whereas `β/ln α = 10`. The official answer is an
acceptable *sufficient* condition, but a grader using it as the answer key
would mark the sharp answer wrong. **Flag for the human reviewer.**

**2. Plug-in check: PASS.** "Every reversible cycle has Carnot efficiency"
is a classic misconception that the item directly targets. A solver must
reason about *where* heat enters.

**3. Formalization check: OK with notes.**
- The cycle's heats are given as definitions with comments. Deriving
  `c_p = 5R/2` and the isothermal heat is left out, which is acceptable
  because the intuition here is the regime, not the heat bookkeeping.
- The `Filter` formulation captures "regime" without fixing a path to the
  limit. Good. `hF` guarantees `ln α > 0` and positive denominators eventually.
- Shape is really `bound_given` (the regime is in the statement). A
  `regime_blank` version can't be stated in Lean without restricting the
  class of admissible conditions; the companion theorem instead tests
  whether the prover can tell the sharp condition from the official one.
- Non-vacuity: `F = atTop` along `(e^n, 1)` satisfies `hF`.

**4. Category check: PASS.** Limiting regime of a thermodynamic cycle.

**Verdict: accept, and record the source discrepancy.** It shows the value
of formal statements: Lean forces the sharp condition where the informal
solution was loose.

## Human review

- [ ] accept / revise / reject:
- reason:
- [ ] agree that the official condition `β ≪ ln α` is non-sharp?
