import Mathlib

/-!
# The hard-core lattice gas (grand canonical, finite volume)

Friedli–Velenik §1.3.2: `V` cells, at most one particle per cell, no
interaction (`H ≡ 0`). Configurations with `N` particles number
`Nat.choose V N`, so the grand canonical partition function at inverse
temperature `β` and chemical potential `μ` is
`Θ_{V;β,μ} = Σ_{N=0}^V (V choose N) e^{βμN}`.
-/

namespace PhysProofBench

/-- Grand canonical partition function `Θ_{Λ;β,μ}` of the hard-core lattice
gas in a box of `V` cells. -/
noncomputable def hardCoreGrandPartition (V : ℕ) (β μ : ℝ) : ℝ :=
  ∑ N ∈ Finset.range (V + 1), (V.choose N : ℝ) * Real.exp (β * μ * N)

/-- Finite-volume pressure `(βV)⁻¹ log Θ_{Λ;β,μ}` (eqn. (1.41) before the limit). -/
noncomputable def hardCorePressure (V : ℕ) (β μ : ℝ) : ℝ :=
  1 / (β * V) * Real.log (hardCoreGrandPartition V β μ)

/-- Finite-volume particle density `⟨N_Λ⟩ / V` under the grand canonical
distribution. -/
noncomputable def hardCoreDensity (V : ℕ) (β μ : ℝ) : ℝ :=
  (1 / (V : ℝ)) *
    ((∑ N ∈ Finset.range (V + 1), (N : ℝ) * (V.choose N : ℝ) * Real.exp (β * μ * N)) /
      hardCoreGrandPartition V β μ)

end PhysProofBench
