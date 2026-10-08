# Notes: SM_01_E06_001

## Formalization decisions

- Stated as the explicit two-point inequality the source writes, not as
  Mathlib's `ConcaveOn ℝ {μ | IsProbDist μ} shannonEntropy`. `ConcaveOn` also
  bundles convexity of the domain, which the source does not ask for, and
  would make the gold statement slightly stronger than the exercise.
- `Ω` is not required to be nonempty. The claim is trivially true for empty `Ω`
  (no distributions exist), so no hypothesis was added.
- Reuses `IsProbDist` and `shannonEntropy` from `Core/Probability.lean` (see
  `SM_01_009_001`). The natural proof goes through
  `shannonEntropy_eq_sum_negMulLog` and `Real.concaveOn_negMulLog`.

## Hidden assumptions

None. `proof_kind: exact`.

## Witness

Not needed (no added hypotheses).

## Difficulty

`difficulty.decl_count` (5) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.

## NL proof source

`nl.md#proof` follows the source's solution to Exercise 1.6 (Appendix C) (2026-10-08). It was added so
the `with_nl_proof` conditions apply to this item.
