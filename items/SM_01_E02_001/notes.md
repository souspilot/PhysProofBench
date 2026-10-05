# Notes: SM_01_E02_001

## Formalization decisions

- Stated as `ConcaveOn ℝ PosOrthant S`. That includes convexity of the
  orthant, which is true, and it is Mathlib's idiomatic form of the source's
  inequality (1.8).
- Homogeneity is a hypothesis here (it is the conclusion of Exercise 1.1,
  item `SM_01_E01_001`), stated for all real `t > 0` on the orthant.
- With homogeneity and superadditivity as hypotheses the proof is short. The
  difficulty of this item is in the modeling, not the Lean.
  `docs/GRADING.md`'s L3b dumb-tactic probe may flag autoformalized versions
  as `suspected_trivial`. That is expected and is itself informative.
- **No `## proof` in `nl.md`.** The source leaves this as an exercise and
  gives no proof, so per `plan.md` §4 `nl.proof` is omitted. Only the
  `no_nl_proof` conditions (A1, B1) apply to this item.

## Hidden assumptions

See `meta.yaml` `hidden_assumptions`: `superadditivity` (modeling), `positive_orthant` (domain).

## Witness

Any linear `S` (e.g. `U + V + N`) is homogeneous and additive, hence superadditive, so the hypotheses are jointly satisfiable. The ideal-gas entropy is a nonlinear physical witness.

## Difficulty

`difficulty.decl_count` (3) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.
