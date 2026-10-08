import Mathlib
import PhysProofBench.Core.LatticeGas

-- PHYSPROOFBENCH-ITEM: SM_01_Q43_001
-- PHYSPROOFBENCH-DECL: hardCore_idealGasLaw

open PhysProofBench Asymptotics

/-- For the hard-core lattice gas in `V ≥ 1` cells at inverse temperature
`β > 0`, pressure and density satisfy the isotherm `βp = -log(1 - ρ)` exactly,
and in the dilute limit (chemical potential `μ → -∞`, so `ρ → 0`) this reduces
to the ideal gas law: `βp = ρ + O(ρ²)`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
§1.3.2, eqn. (1.43) and the Taylor expansion after it, p. 34. See
`docs/SOURCE.md` for the edition.) -/
theorem hardCore_idealGasLaw (β : ℝ) (hβ : 0 < β) (V : ℕ) (hV : 1 ≤ V) :
    (∀ μ : ℝ, hardCorePressure V β μ = -(1 / β) * Real.log (1 - hardCoreDensity V β μ)) ∧
    (fun μ : ℝ => β * hardCorePressure V β μ - hardCoreDensity V β μ) =O[Filter.atBot]
      (fun μ : ℝ => hardCoreDensity V β μ ^ 2) := by
  sorry
