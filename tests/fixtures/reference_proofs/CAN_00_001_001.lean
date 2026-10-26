import PhysProofBench.Core.Probability

-- PHYSPROOFBENCH-ITEM: CAN_00_001_001
-- PHYSPROOFBENCH-DECL: uniformDist_isProbDist

open PhysProofBench

/-- Canary item (pipeline sanity check, not scored): the uniform
distribution on a finite nonempty set is a probability distribution. -/
theorem uniformDist_isProbDist {Ω : Type*} [Fintype Ω] [Nonempty Ω] :
    IsProbDist (uniformDist : Ω → ℝ) := by
  refine ⟨fun _ => by unfold uniformDist; positivity, ?_⟩
  have h : (Fintype.card Ω : ℝ) ≠ 0 := by exact_mod_cast Fintype.card_ne_zero
  simp [uniformDist, Finset.sum_const, Finset.card_univ, h]

