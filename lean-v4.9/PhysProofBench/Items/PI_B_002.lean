import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_B_002
-- PHYSPROOFBENCH-DECL: PI_B_002_bound

open Real Filter Topology BigOperators

namespace PhysProofBench.PI_B_002

/-! PI_B_002 (draft). Multi-layer electromagnet: `N` coaxial layers of wire of
diameter `t = (b - a)/N`, layer `k = 1..N` (numbered from outside) at radius
`b - t k`. `B k` is the field just inside layer `k` (`B 0 = 0` outside).
Ampère: a layer with current `I k` and turn density `1/t` raises the field by
`μ₀ I k / t`. The wire feels the average field `(B (k-1) + B k)/2`; hoop
tension `I · B_avg · radius` must not exceed tensile strength × area. -/

noncomputable def layerRadius (a b : ℝ) (N k : ℕ) : ℝ := b - (b - a) / N * k

end PhysProofBench.PI_B_002

open PhysProofBench.PI_B_002

theorem PI_B_002_bound (a b σ μ₀ : ℝ) (ha : 0 < a) (hab : a < b) (hσ : 0 < σ)
    (hμ : 0 < μ₀) (N : ℕ) (hN : 0 < N) (B I : ℕ → ℝ) (hB0 : B 0 = 0)
    (hamp : ∀ k ∈ Finset.Icc 1 N, B k - B (k - 1) = μ₀ * I k / ((b - a) / N))
    (hstress : ∀ k ∈ Finset.Icc 1 N,
      I k * ((B (k - 1) + B k) / 2) * layerRadius a b N k
        ≤ π / 4 * ((b - a) / N) ^ 2 * σ) :
    B N ^ 2 ≤ π / 2 * σ * μ₀ *
      ∑ k ∈ Finset.Icc 1 N, ((b - a) / N) / layerRadius a b N k := by
  sorry
