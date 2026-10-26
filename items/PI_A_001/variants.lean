import PhysProofBench.Items.PI_A_001

open Real Filter Topology Asymptotics
open PhysProofBench.PI_A_001

/-! Companion statements for PI_A_001: drafts, not graded. -/

/-- `bound_given` variant: explicit error bound, valid for all `ℓ ≥ 0`. -/
theorem PI_A_001_bound (r ℓ : ℝ) (hr : 0 < r) (hℓ : 0 ≤ ℓ) :
    |ℓ - chord r ℓ - ℓ ^ 3 / (24 * r ^ 2)| ≤ ℓ ^ 5 / (1920 * r ^ 4) := by
  sorry
