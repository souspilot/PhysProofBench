import PhysProofBench.Core.Probability

-- PHYSPROOFBENCH-ITEM: SM_01_009_001
-- PHYSPROOFBENCH-DECL: shannonEntropy_le_log_card

open PhysProofBench

/-- The uniform distribution on a finite, nonempty set of microstates `Ω` is
the *unique* probability distribution maximizing Shannon entropy, and its
entropy is `log |Ω|`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Lemma 1.9, p. 21. See `docs/SOURCE.md` for the edition.) -/
theorem shannonEntropy_le_log_card {Ω : Type*} [Fintype Ω] [Nonempty Ω]
    (μ : Ω → ℝ) (hμ : IsProbDist μ) :
    shannonEntropy μ ≤ Real.log (Fintype.card Ω) ∧
      (shannonEntropy μ = Real.log (Fintype.card Ω) ↔ ∀ ω, μ ω = uniformDist ω) := by
  sorry
