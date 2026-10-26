import PhysProofBench.Items.PI_E_002

open Real
open PhysProofBench.PI_E_002

/-! Companion statements for PI_E_002: drafts, not graded. -/

theorem PI_E_002_dimensional (P : ℝ → ℝ → ℝ → ℝ) (hP : DimCovariant P) :
    ∃ C : ℝ, ∀ G M R : ℝ, 0 < G → 0 < M → 0 < R → P G M R = C * G * M ^ 2 / R ^ 4 := by
  sorry
