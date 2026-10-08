import Mathlib
import PhysProofBench.Core.Probability

-- PHYSPROOFBENCH-ITEM: CAN_00_001_001
-- PHYSPROOFBENCH-DECL: uniformDist_isProbDist

open PhysProofBench

/-- Canary item (pipeline sanity check, not scored): the uniform
distribution on a finite nonempty set is a probability distribution. -/
theorem uniformDist_isProbDist {Ω : Type*} [Fintype Ω] [Nonempty Ω] :
    IsProbDist (uniformDist : Ω → ℝ) := by
  sorry
