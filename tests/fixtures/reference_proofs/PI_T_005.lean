import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_T_005
-- PHYSPROOFBENCH-DECL: kinetic_energy_pos

/-! Trivial environment check (positivity side conditions); not a physics item. -/

theorem kinetic_energy_pos (m v : ℝ) (hm : 0 < m) (hv : 0 < v) : 0 < m * v ^ 2 / 2 := by
  positivity
