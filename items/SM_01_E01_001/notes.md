# Notes: SM_01_E01_001

## Formalization decisions

- The macrostate `X = (U, V, N)` is `ℝ × ℝ × ℝ`, and scaling is `t • X`. All
  hypotheses and the conclusion are restricted to the open positive orthant
  `PosOrthant` (`Core/Thermo.lean`), which scaling by `t > 0` preserves.
- What the source actually derives homogeneity *from* is informal (the
  postulate plus the extremum principle). The gold statement makes the
  premises explicit: an integer-scaling law (the modeling content) plus
  continuity (the regularity needed for the source's hint, ℚ then ℝ).
- Continuity is assumed, not differentiability. That is weaker than the
  postulate grants, hence a weaker hypothesis and a stronger theorem, and it
  is exactly what the proof needs.
- The source gives only a hint, not a proof, so `nl.proof` is omitted.
- **No `## proof` in `nl.md`.** The source leaves this as an exercise and
  gives no proof, so per `plan.md` §4 `nl.proof` is omitted. Only the
  `no_nl_proof` conditions (A1, B1) apply to this item.

## Hidden assumptions

See `meta.yaml` `hidden_assumptions`: `integer_scaling` (modeling), `continuity` (regularity), `positive_orthant` (domain).

## Witness

`S(U, V, N) = U + V + N` (or any linear function) satisfies both hypotheses on `PosOrthant`, so they are jointly satisfiable. The ideal-gas entropy `N (c log(U/N) + log(V/N))` is a physical witness.

## Difficulty

`difficulty.decl_count` (10) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.
