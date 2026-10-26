import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_T_002
-- PHYSPROOFBENCH-DECL: uniform_motion_position

/-! Trivial environment check (hypotheses (`subst`, `linarith`)); not a physics item. -/

theorem uniform_motion_position (x x₀ v t : ℝ) (hx : x = x₀ + v * t) (hx₀ : x₀ = 1)
    (hv : v = 2) (ht : t = 3) : x = 7 := by
  sorry
