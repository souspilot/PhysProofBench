import Mathlib
import PhysProofBench.Core.Probability

-- PHYSPROOFBENCH-ITEM: SM_01_E06_001
-- PHYSPROOFBENCH-DECL: shannonEntropy_concave

open PhysProofBench

/-- Shannon entropy is concave on the set of probability distributions of a
finite set `Ω`: mixing two distributions never yields less than the mixed
entropies.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Exercise 1.6, p. 21. See `docs/SOURCE.md` for the edition.) -/
theorem shannonEntropy_concave {Ω : Type*} [Fintype Ω] (μ ν : Ω → ℝ)
    (hμ : IsProbDist μ) (hν : IsProbDist ν) (α : ℝ) (hα₀ : 0 ≤ α) (hα₁ : α ≤ 1) :
    α * shannonEntropy μ + (1 - α) * shannonEntropy ν ≤
      shannonEntropy (fun ω => α * μ ω + (1 - α) * ν ω) := by
  sorry
