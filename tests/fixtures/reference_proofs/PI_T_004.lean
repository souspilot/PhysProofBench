import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_T_004
-- PHYSPROOFBENCH-DECL: half_life_count

/-! Trivial environment check (existential answer (`answer_blank` shape)); not a physics item. -/

theorem half_life_count : ∃ n : ℕ, (1 / 2 : ℝ) ^ n = 1 / 8 := by
  exact ⟨3, by norm_num⟩
