import Mathlib

-- PHYSPROOFBENCH-ITEM: CAN_00_005_001
-- PHYSPROOFBENCH-DECL: canary_sq_expand

/-- Canary item (pipeline sanity check, not scored), plain Mathlib with no
PhysProofBench definitions: `x² - 2x + 1 = (x - 1)² ≥ 0`. -/
theorem canary_sq_expand (x : ℝ) : 0 ≤ x ^ 2 - 2 * x + 1 := by
  nlinarith [sq_nonneg (x - 1)]
