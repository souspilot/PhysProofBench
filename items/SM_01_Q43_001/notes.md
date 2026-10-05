# Notes: SM_01_Q43_001

## Formalization decisions

- **Finite volume, not the thermodynamic limit.** The source defines `p` and
  `ρ` as `V → ∞` limits. For the hard-core gas both finite-volume quantities
  are already independent of `V` (`Θ = (1 + e^{βμ})^V`), so the gold statement
  quantifies over every `V ≥ 1` instead of taking a limit. This avoids
  building limit machinery for a quantity that is constant in `V`, and loses
  none of the content.
- **Approximation encoding: `asymptotic` (`IsBigO`), flavor `controlled`.**
  The source's "`p = ρ k_B T + O(ρ²)`" is written literally as
  `(β p - ρ) =O[atBot] ρ²`, with `μ → -∞` as the filter. `μ → -∞` is how
  dilution is controlled from the model's own parameters. Using `ρ → 0`
  directly would need `ρ` as the independent variable, which the ensemble
  does not provide.
- `k_B = 1` (the source's convention in most of the book), so `k_B T = 1/β`.
- `hardCoreDensity` is defined as `⟨N⟩/V` directly from the grand canonical
  weights, not via the `∂/∂μ` identity the source uses to compute it. The
  derivative is part of the proof, not the definition.

## Hidden assumptions

None beyond the approximation encoding above.

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
