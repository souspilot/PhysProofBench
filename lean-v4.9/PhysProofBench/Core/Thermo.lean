import Mathlib

/-!
# Equilibrium thermodynamics: entropy functions `S(U, V, N)`

Friedli–Velenik §1.1. A thermodynamic entropy is a function of the macrostate
`X = (U, V, N)`. We model it as `S : ℝ × ℝ × ℝ → ℝ` and restrict every
hypothesis and conclusion to the open positive orthant `U, V, N > 0`, the
physical domain of the book's examples (e.g. the ideal gas, Example 1.6).
-/

namespace PhysProofBench

/-- The open positive orthant `{(U, V, N) | U > 0, V > 0, N > 0}`. -/
def PosOrthant : Set (ℝ × ℝ × ℝ) :=
  {X | 0 < X.1 ∧ 0 < X.2.1 ∧ 0 < X.2.2}

/-- `F̂(β, V, N) = inf_U {βU - S(U, V, N)}` (Friedli–Velenik eqn. (1.15)),
the infimum taken over `U > 0`. If the set is unbounded below, Lean's `iInf`
returns a junk value, so statements about `freeEnergyHat` must assume the
infimum is finite. -/
noncomputable def freeEnergyHat (S : ℝ × ℝ × ℝ → ℝ) (β V N : ℝ) : ℝ :=
  ⨅ U : Set.Ioi (0 : ℝ), (β * (U : ℝ) - S ((U : ℝ), V, N))

end PhysProofBench
