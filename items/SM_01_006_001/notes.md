# Notes: SM_01_006_001

## Formalization decisions

- **Per-particle form only.** The source goes on to reassemble
  `S(U, V, N) = N s₀ + N k_B log[(U/U₀)^c (V/V₀) (N/N₀)^{-(c+1)}]` via
  homogeneity. That second step is plain algebra given the per-particle
  result plus Exercise 1.1, so it is left out to keep this item focused on
  the integration.
- Partial derivatives are `HasDerivAt` of the one-variable slices
  `e' ↦ s e' v` and `v' ↦ s e v'`. No joint differentiability is assumed.
  Integrating along one coordinate and then the other needs only these, so
  the hypothesis is weaker than the source's differentiable `S`.
- The constants `c`, `k_B` carry no sign hypotheses. The identity holds for
  any real values, and adding `0 < c`, `0 < k_B` would be extra hypotheses the
  proof does not use.

## Hidden assumptions

See `meta.yaml` `hidden_assumptions`: `global_equations_of_state` (domain).

## Witness

`s(e, v) = c k_B log e + k_B log v` satisfies both derivative hypotheses on the whole quadrant.

## Difficulty

`difficulty.decl_count` (6) is an **estimate** made while
drafting the statement. No reference proof exists yet. Replace it with the
real count once the private solution is written.

## Reference proof

None yet: statement-only item (`status: draft`). The gold statement compiles
with `sorry` against the pinned toolchain (`lake build PhysProofBench`).

## Open for review

- Not yet through the two-reviewer process (`reviewed_by: []`).
- Check fidelity of the formalization decisions above against the source.
