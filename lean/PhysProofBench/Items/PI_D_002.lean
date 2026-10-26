import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_D_002
-- PHYSPROOFBENCH-DECL: PI_D_002

open Real Filter Topology Asymptotics

namespace PhysProofBench.PI_D_002

/-! PI_D_002 (draft). Charge `-q` (mass `m`) confined to a plane, a large
charge `Q` a distance `R` below the origin, and a fixed charge `-q` at the
origin. For `r ≪ R` the in-plane potential is `V r = (k/2) r² + κ / r`
(`k = qQ/(4πε₀R³)`, `κ = q²/(4πε₀)`), with a ring of minima at `r₀`.
Without the origin charge, circular orbits have `ω_c = √(k/m)` at every radius. -/

noncomputable def V (k κ r : ℝ) : ℝ := k / 2 * r ^ 2 + κ / r

end PhysProofBench.PI_D_002

open PhysProofBench.PI_D_002

/-- `answer_blank`: a circular orbit just outside the ring, radius `r₀ + δ`,
has angular frequency `Ω ≈ c ω_c (δ/r₀)^p`. (Expected `c = √3`, `p = 1/2`;
the plug-in answers `Ω = ω_c` or `Ω = √3 ω_c` are wrong.) -/
theorem PI_D_002 (m k κ : ℝ) (hm : 0 < m) (hk : 0 < k) (hκ : 0 < κ)
    (r₀ : ℝ) (hr₀ : 0 < r₀) (hmin : deriv (V k κ) r₀ = 0)
    (Ω : ℝ → ℝ) (hΩ : ∀ δ, 0 < δ → 0 ≤ Ω δ)
    (hcirc : ∀ δ, 0 < δ → m * Ω δ ^ 2 * (r₀ + δ) = deriv (V k κ) (r₀ + δ)) :
    ∃ c p : ℝ, 0 < c ∧ 0 < p ∧
      (fun δ => Ω δ - c * Real.sqrt (k / m) * (δ / r₀) ^ p)
        =o[𝓝[>] 0] (fun δ => (δ / r₀) ^ p) := by
  sorry
