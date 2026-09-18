# Notes: SM_01_009_001

## Formalization decisions

- **Representation of `M1(Ω)`.** A distribution is `μ : Ω → ℝ` with
  `IsProbDist μ := (∀ ω, 0 ≤ μ ω) ∧ ∑ ω, μ ω = 1` (`Core/Probability.lean`),
  not Mathlib's `PMF` (which is `ℝ≥0∞`-valued and measure-theoretic — more
  machinery than this book's finite, purely-real setup needs, and further
  from the source's own notation `μ(ω) ≥ 0`, `Σμ(ω) = 1`).
- **`0 log 0 := 0`.** Free from Mathlib's junk value `Real.log 0 = 0`; no
  special-casing needed in `shannonEntropy`'s definition.
- **`shannonEntropy` vs `Real.negMulLog`.** The Core definition
  (`-∑ μ(ω) log μ(ω)`) mirrors the book's Definition 1.8 exactly, for
  readability when checking fidelity against the source. The proof bridges
  to Mathlib's `Real.negMulLog` (`x ↦ -x log x`) via
  `shannonEntropy_eq_sum_negMulLog`, because Mathlib already proves
  `negMulLog` strictly concave on `[0,∞)` — this is where the real work
  (Jensen's inequality, `Mathlib.Analysis.Convex.Jensen`) comes from; no
  concavity proof was written from scratch here.

## Hidden assumptions

None. `proof_kind: exact`. The source's own hypotheses (finite `Ω`,
`μ ∈ M1(Ω)`) are exactly what's formalized; no regularity or domain
assumption was added beyond them.

## `VERIFY` items resolved (plan.md flags these as uncertain until checked)

Checked against the pinned toolchain (`leanprover/lean4:v4.34.0`, Mathlib
tag `v4.34.0`, commit `5ed2965256430c3649e86755f9576b54eca72435`):

- `#print axioms <decl>` output format is
  `'<decl>' depends on axioms: [propext, Classical.choice, Quot.sound]` (or
  `'<decl>' does not depend on any axioms`) — matches what
  `physproofbench/lean/audit.py` parses. Confirmed live against this item's
  solution, not just assumed.
- `sorryAx` is indeed the axiom name Lean emits for `sorry`.
- Checking `#print axioms` on only the top-level declaration is sufficient
  (transitively covers dependencies) — confirmed: the solution's proof pulls
  in several `have`s and Mathlib lemmas, and the top-level check still
  reports exactly the standard three axioms.

## Reference proof

`lean/PhysProofBenchSolutions/SM_01_009_001.lean` (private repo) —
`sorry`-free, axioms = `{propext, Classical.choice, Quot.sound}`, verified
by direct compilation + `#print axioms` during formalization (2026-09-18),
not merely reviewed by eye.

## Open for review (S6 checklist, `docs/REVIEW.md` — not yet written)

- Quantifier order: `∀ ω, μ ω = uniformDist ω` after the `↔` — check this is
  the intended reading (uniqueness as "every point matches uniform", not an
  existential).
- Witness: the uniform distribution itself is trivially in `M1(Ω)` for any
  finite nonempty `Ω` — no witness-satisfiability issue to check here (no
  hidden assumptions to make jointly satisfiable).
- This item has not yet been through the two-reviewer process
  (`meta.yaml` `status: draft`, `reviewed_by: []`).
