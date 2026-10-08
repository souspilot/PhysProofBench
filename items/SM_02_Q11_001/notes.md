# Notes: SM_02_Q11_001

## Formalization decisions

- **Approximation encoding: `error_bound`, flavor `controlled`.** The source
  states the bound as a direct consequence of Stirling's formula and leaves it
  as Exercise 2.1. This is the one item in the set whose approximation is an
  explicit two-sided numeric bound rather than a limit or big-O.
- Constants are existentially quantified, as in the source. Checked
  numerically while drafting (not a proof): `c₋ = 1/√2`, `c₊ = 1` satisfy both
  bounds for all `N < 400`, with the lower bound tight at `k = 1`.
- `N^{-1/2}` is `(N : ℝ) ^ (-(1/2 : ℝ))` (`Real.rpow`).
- `m = ±1` (`k = 0` or `k = N`) relies on Mathlib's `Real.log 0 = 0`, which
  gives the `0 log 0 = 0` convention, as in `Core/Probability.lean`.

## Hidden assumptions

None beyond the approximation encoding above.

## Witness

Not needed (no added hypotheses).

## Difficulty

`difficulty.decl_count` (30) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.

## NL proof source

`nl.md#proof` follows the source's main-text remark that (2.11) follows from Stirling's formula, expanded by the contributor using the source's Lemma B.3 (the source leaves it as Exercise 2.1 and gives no solution) (2026-10-08). It was added so
the `with_nl_proof` conditions apply to this item.
