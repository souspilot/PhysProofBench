# Notes: SM_01_E05_001

## Formalization decisions

- The source phrases this as "show that there exists a critical temperature
  `T_c` ... such that ...", with the explicit value `8a/(27 k_B b)` given. The
  gold statement fixes that value rather than quantifying it existentially.
  Otherwise the existential would be satisfiable by a wrong `T_c`, weakening
  the item.
- "Decreasing everywhere" is formalized as `StrictAntiOn ... (Set.Ioi b)`.
  That is true for `T > T_c`, where `∂p/∂v < 0` on all of `v > b`.
- "Increasing on some interval" is formalized as `StrictMonoOn` on a
  nondegenerate closed interval `[v₁, v₂] ⊂ (b, ∞)`.
- `0 < T` is required in the second clause because `T` is a temperature. The
  claim also holds for `T ≤ 0`, so this hypothesis only restricts the claim to
  its physical range.
- The pressure is written inline as a lambda, not as a `Core` definition. It
  is used only here, and inline keeps the item file self-contained. It is
  written twice rather than with `let`, because the L2.3 signature parser
  (`audit.parse_theorem_signature`) stops at the first depth-0 `:=`.

## Hidden assumptions

None. `proof_kind: exact`. The source states `a, b > 0` and `v > b`.

## Witness

Not needed (no added hypotheses).

## Difficulty

`difficulty.decl_count` (12) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.

## NL proof source

`nl.md#proof` follows the source's solution to Exercise 1.5 (Appendix C), with its graphical argument written out (2026-10-08). It was added so
the `with_nl_proof` conditions apply to this item.
