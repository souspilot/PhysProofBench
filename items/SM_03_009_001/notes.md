# Notes: SM_03_009_001

## Formalization decisions

- **Only the periodic sequence of volumes is covered (`_001`).** The source
  defines `ψ(β, h)` as the thermodynamic limit, which (by Theorem 3.6) is the
  same along any van Hove sequence and for any boundary condition. The proof
  specializes to the torus `{0, …, n-1}`, and so does this gold statement.
  Stating it for arbitrary sequences and boundary conditions would bundle
  Theorem 3.6 into this item.
- **Approximation encoding: `asymptotic` (`Tendsto`), flavor
  `disguised_limit`.** The source states an exact formula for a limiting
  quantity (the pressure of the infinite chain). The only "approximation" is
  the idealization of a large finite chain by its limit, which is exactly
  what `disguised_limit` means in `docs/TAXONOMY.md`.
- Periodic neighbours use `finRotate n` (`i ↦ i + 1 mod n`). For `n = 1` the
  single site is its own neighbour, and for `n = 2` the two sites are joined
  twice. Both agree with the trace formula `Z_n = Tr(Aⁿ)`, which holds for
  every `n ≥ 1`; this was checked numerically for `n = 1, 2, 5, 10` while
  drafting.
- The formula keeps the source's form `e^{2β} cosh² h - 2 sinh 2β` under the
  square root, rather than the equivalent `e^{2β} sinh² h + e^{-2β}`.

## Hidden assumptions

None beyond the approximation encoding above.

## Witness

Not needed (no added hypotheses).

## Difficulty

`difficulty.decl_count` (25) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.
