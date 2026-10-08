import Mathlib
import PhysProofBench.Core.Ising

-- PHYSPROOFBENCH-ITEM: SM_03_009_001
-- PHYSPROOFBENCH-DECL: isingChain_pressure_formula

open PhysProofBench

/-- The pressure of the one-dimensional Ising model, computed on the periodic
chain `{0, …, n-1}` as `n → ∞`, is
`log (e^β cosh h + √(e^{2β} cosh² h - 2 sinh 2β))` for every `β ≥ 0` and
`h ∈ ℝ`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Theorem 3.9, eqn. (3.10), p. 90, along the periodic volumes used in its
proof. See `docs/SOURCE.md` for the edition.) -/
theorem isingChain_pressure_formula (β h : ℝ) (hβ : 0 ≤ β) :
    Filter.Tendsto (fun n : ℕ => isingChainPressurePer n β h) Filter.atTop
      (nhds (Real.log (Real.exp β * Real.cosh h +
        Real.sqrt (Real.exp (2 * β) * Real.cosh h ^ 2 - 2 * Real.sinh (2 * β))))) := by
  sorry
