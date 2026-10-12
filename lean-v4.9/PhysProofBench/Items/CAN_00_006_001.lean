import Mathlib

-- PHYSPROOFBENCH-ITEM: CAN_00_006_001
-- PHYSPROOFBENCH-DECL: canary_succ_le_two_pow

/-- Canary item (pipeline sanity check, not scored), plain Mathlib with no
PhysProofBench definitions: `n + 1 ≤ 2ⁿ` for every natural number `n`. -/
theorem canary_succ_le_two_pow (n : ℕ) : n + 1 ≤ 2 ^ n := by
  sorry
