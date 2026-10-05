# Notes: SM_03_005_001

## Formalization decisions

- **Only the free boundary condition is covered (`_001`).** The source states
  the lemma for every boundary condition type (free, periodic, `+`, `-`,
  general `η`). Those need more `Core` (boundary configurations, the torus in
  `ℤᵈ`) and can be later sub-items `_002`, `_003`, ... sharing this
  statement's shape.
- Domain `Set.Ici 0 ×ˢ Set.univ` matches the source's `β ∈ ℝ≥0`, `h ∈ ℝ`. The
  function is in fact convex on all of `ℝ²` (log-sum-exp of affine maps).
  Stating it there would be a correct but stronger claim than the source's,
  so the source's domain is kept.
- Spins are `Bool` (`Core/Spin.lean`); `spin` maps them to `±1`. The edge sum
  `Σ_{{i,j} ∈ E_Λ}` runs over ordered pairs and is halved
  (`Core/Ising.lean`), which counts each unordered nearest-neighbour edge
  exactly once.
- `Λ` may be empty. Then `|Λ| = 0`, the pressure is the junk value `0`, and
  convexity holds trivially. No nonemptiness hypothesis was added.

## Hidden assumptions

None. `proof_kind: exact`.

## Witness

Not needed (no added hypotheses).

## Difficulty

`difficulty.decl_count` (8) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.
