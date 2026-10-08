import PhysProofBench.Core.CurieWeiss

-- PHYSPROOFBENCH-ITEM: CAN_00_004_001
-- PHYSPROOFBENCH-DECL: cwPartition_pos

open PhysProofBench

/-- Canary item (pipeline sanity check, not scored): the Curie–Weiss
partition function is positive (a sum of exponentials over a nonempty set of
configurations). -/
theorem cwPartition_pos (d N : ℕ) (β h : ℝ) : 0 < cwPartition d N β h := by
  sorry
