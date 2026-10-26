import PhysProofBench.Items.PI_B_001

open Real Filter Topology
open PhysProofBench.PI_B_001

/-! Companion statements for PI_B_001: drafts, not graded. -/

/-- The official solution's condition `β ≪ ln α` is sufficient but not
necessary: there is a regime approaching Carnot where `β / ln α ↛ 0`. -/
theorem PI_B_001_official_not_necessary :
    ∃ F : Filter (ℝ × ℝ), F.NeBot ∧ (∀ᶠ p in F, 1 < p.1 ∧ 0 < p.2) ∧
      Tendsto (fun p => efficiency p.1 p.2 / carnot p.2) F (𝓝 1) ∧
      ¬ Tendsto (fun p => p.2 / Real.log p.1) F (𝓝 0) := by
  sorry
