import PhysProofBench.Core.Spin

-- PHYSPROOFBENCH-ITEM: CAN_00_002_001
-- PHYSPROOFBENCH-DECL: spin_mul_self

open PhysProofBench

/-- Canary item (pipeline sanity check, not scored): a spin squared is one,
`ωᵢ² = 1` for `ωᵢ ∈ {-1, 1}`. -/
theorem spin_mul_self (b : Bool) : spin b * spin b = 1 := by
  sorry
