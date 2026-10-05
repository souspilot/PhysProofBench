import PhysProofBench.Core.CurieWeiss
import Mathlib.Analysis.SpecialFunctions.Pow.Real

-- PHYSPROOFBENCH-ITEM: SM_02_Q11_001
-- PHYSPROOFBENCH-DECL: choose_exp_cwEntropy_bounds

open PhysProofBench

/-- Stirling-type two-sided bound on binomial coefficients: there are
constants `c₋, c₊ > 0` such that for every `N ≥ 1` and `k ∈ {0, …, N}`, writing
`m = 2k/N - 1` for the corresponding magnetization,
`c₋ N^{-1/2} e^{N s(m)} ≤ (N choose k) ≤ c₊ e^{N s(m)}`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
eqn. (2.11) and Exercise 2.1, p. 62. See `docs/SOURCE.md` for the edition.) -/
theorem choose_exp_cwEntropy_bounds :
    ∃ cminus cplus : ℝ, 0 < cminus ∧ 0 < cplus ∧
      ∀ N : ℕ, 1 ≤ N → ∀ k : ℕ, k ≤ N →
        cminus * (N : ℝ) ^ (-(1 / 2 : ℝ)) *
            Real.exp (N * cwEntropy (2 * (k : ℝ) / N - 1)) ≤ (N.choose k : ℝ) ∧
          (N.choose k : ℝ) ≤ cplus * Real.exp (N * cwEntropy (2 * (k : ℝ) / N - 1)) := by
  sorry
