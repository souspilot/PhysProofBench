import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_T_003
-- PHYSPROOFBENCH-DECL: ohm_current

/-! Trivial environment check (division by a nonzero quantity); not a physics item. -/

theorem ohm_current (V I R : ℝ) (hR : R ≠ 0) (h : V = I * R) : I = V / R := by
  rw [h, mul_div_assoc, div_self hR, mul_one]
