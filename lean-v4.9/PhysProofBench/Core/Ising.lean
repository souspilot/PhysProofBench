import Mathlib
import PhysProofBench.Core.Spin

/-!
# The Ising model in finite volume

Friedli–Velenik, ch. 3. Two finite-volume versions are provided:

* free boundary condition on a finite `Λ ⊂ ℤᵈ` (Definition 3.1, pressure as in
  Definition 3.4);
* the one-dimensional chain `{0, …, n-1}` with periodic boundary condition
  (the torus used in the proof of Theorem 3.9).

Convention: `β` and `h` sit inside the Hamiltonian, as in the source, so the
Boltzmann weight is `exp (-H)`.
-/

namespace PhysProofBench

/-- A vertex of `ℤᵈ`. -/
abbrev Site (d : ℕ) := Fin d → ℤ

/-- `i ∼ j`: nearest neighbours in `ℤᵈ` (ℓ¹ distance 1). -/
def IsNearestNeighbor {d : ℕ} (i j : Site d) : Prop :=
  ∑ k, |i k - j k| = 1

instance {d : ℕ} : DecidableRel (@IsNearestNeighbor d) := fun i j => by
  unfold IsNearestNeighbor; infer_instance

/-- Free-boundary Ising Hamiltonian `H^∅_{Λ;β,h}` (Friedli–Velenik §3.1):
`-β Σ_{{i,j} ∈ E_Λ} ωᵢωⱼ - h Σ_{i ∈ Λ} ωᵢ`. The edge sum is written over
ordered pairs and halved, so each unordered edge `{i,j}` counts once. -/
noncomputable def isingHamiltonianFree {d : ℕ} (Λ : Finset (Site d)) (β h : ℝ)
    (ω : Λ → Bool) : ℝ :=
  -β * ((1 / 2) * ∑ i : Λ, ∑ j : Λ,
      if IsNearestNeighbor (i : Site d) (j : Site d) then spin (ω i) * spin (ω j) else 0)
    - h * ∑ i : Λ, spin (ω i)

/-- Free-boundary partition function `Z^∅_{Λ;β,h}` (Definition 3.1). -/
noncomputable def isingPartitionFree {d : ℕ} (Λ : Finset (Site d)) (β h : ℝ) : ℝ :=
  ∑ ω : Λ → Bool, Real.exp (-isingHamiltonianFree Λ β h ω)

/-- Free-boundary finite-volume pressure `ψ^∅_Λ(β,h) = |Λ|⁻¹ log Z^∅_{Λ;β,h}`
(Definition 3.4). -/
noncomputable def isingPressureFree {d : ℕ} (Λ : Finset (Site d)) (β h : ℝ) : ℝ :=
  (1 / (Λ.card : ℝ)) * Real.log (isingPartitionFree Λ β h)

/-- Periodic one-dimensional Ising Hamiltonian on `{0, …, n-1}` (the torus
`Tₙ` of Friedli–Velenik §3.3): `-β Σᵢ ωᵢωᵢ₊₁ - h Σᵢ ωᵢ`, indices mod `n`. -/
noncomputable def isingChainHamiltonianPer (n : ℕ) (β h : ℝ) (ω : Fin n → Bool) : ℝ :=
  -β * ∑ i, spin (ω i) * spin (ω (finRotate n i)) - h * ∑ i, spin (ω i)

/-- Periodic one-dimensional partition function `Z^per_{Vₙ;β,h}`. -/
noncomputable def isingChainPartitionPer (n : ℕ) (β h : ℝ) : ℝ :=
  ∑ ω : Fin n → Bool, Real.exp (-isingChainHamiltonianPer n β h ω)

/-- Periodic one-dimensional finite-volume pressure `n⁻¹ log Z^per_{Vₙ;β,h}`. -/
noncomputable def isingChainPressurePer (n : ℕ) (β h : ℝ) : ℝ :=
  (1 / (n : ℝ)) * Real.log (isingChainPartitionPer n β h)

end PhysProofBench
