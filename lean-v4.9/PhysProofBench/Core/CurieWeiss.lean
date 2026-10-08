import Mathlib
import PhysProofBench.Core.Spin

/-!
# The Curie–Weiss model

Friedli–Velenik, ch. 2: `N` spins, each interacting with all others (the
mean-field replacement of the nearest-neighbour Ising model in dimension `d`).
-/

namespace PhysProofBench

/-- Curie–Weiss Hamiltonian (Friedli–Velenik Definition 2.1, eqn. (2.2)):
`-(dβ/N) Σ_{i,j=1}^N ωᵢωⱼ - h Σᵢ ωᵢ`. The double sum includes `i = j`, as in
the source. -/
noncomputable def cwHamiltonian (d N : ℕ) (β h : ℝ) (ω : Fin N → Bool) : ℝ :=
  -((d : ℝ) * β / N) * ∑ i, ∑ j, spin (ω i) * spin (ω j) - h * ∑ i, spin (ω i)

/-- Curie–Weiss partition function `Z^CW_{N;β,h}`. -/
noncomputable def cwPartition (d N : ℕ) (β h : ℝ) : ℝ :=
  ∑ ω : Fin N → Bool, Real.exp (-cwHamiltonian d N β h ω)

/-- Curie–Weiss Gibbs distribution `μ^CW_{N;β,h}` (weight of one configuration). -/
noncomputable def cwGibbs (d N : ℕ) (β h : ℝ) (ω : Fin N → Bool) : ℝ :=
  Real.exp (-cwHamiltonian d N β h ω) / cwPartition d N β h

/-- `μ^CW_{N;β,h}(A)`, the Gibbs probability of a set of configurations. -/
noncomputable def cwProb (d N : ℕ) (β h : ℝ) (A : Set (Fin N → Bool)) : ℝ :=
  ∑ ω : Fin N → Bool, A.indicator (cwGibbs d N β h) ω

/-- Magnetization density `m_N = N⁻¹ Σᵢ ωᵢ`. -/
noncomputable def magnetization {N : ℕ} (ω : Fin N → Bool) : ℝ :=
  (1 / (N : ℝ)) * ∑ i, spin (ω i)

/-- Inverse critical temperature of the Curie–Weiss model, `β_c(d) = 1/(2d)`
(Theorem 2.2). -/
noncomputable def cwCriticalBeta (d : ℕ) : ℝ := 1 / (2 * (d : ℝ))

/-- The entropy function `s(m)` of Definition 2.4:
`-((1-m)/2) log((1-m)/2) - ((1+m)/2) log((1+m)/2)`, for `m ∈ [-1,1]`.
`Real.log 0 = 0` gives `0 log 0 = 0` at `m = ±1`. -/
noncomputable def cwEntropy (m : ℝ) : ℝ :=
  -((1 - m) / 2) * Real.log ((1 - m) / 2) - ((1 + m) / 2) * Real.log ((1 + m) / 2)

end PhysProofBench
