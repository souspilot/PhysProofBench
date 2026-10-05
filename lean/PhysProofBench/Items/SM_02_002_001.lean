import PhysProofBench.Core.CurieWeiss
import Mathlib.Order.Filter.AtTopBot.Basic

-- PHYSPROOFBENCH-ITEM: SM_02_002_001
-- PHYSPROOFBENCH-DECL: cw_magnetization_concentrates_subcritical

open PhysProofBench

/-- Curie–Weiss model in zero field, at or above the critical temperature
(`0 ≤ β ≤ β_c(d) = 1/(2d)`): the magnetization density concentrates at zero
exponentially fast. For every `ε > 0` there is `c > 0` such that, for all
large enough `N`, `μ^CW_{N;β,0}(|m_N| < ε) ≥ 1 - 2e^{-cN}`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Theorem 2.2, part 1, p. 60. See `docs/SOURCE.md` for the edition.) -/
theorem cw_magnetization_concentrates_subcritical (d : ℕ) (hd : 1 ≤ d) (β : ℝ)
    (hβ₀ : 0 ≤ β) (hβ : β ≤ cwCriticalBeta d) (ε : ℝ) (hε : 0 < ε) :
    ∃ c : ℝ, 0 < c ∧ ∀ᶠ N : ℕ in Filter.atTop,
      1 - 2 * Real.exp (-c * N) ≤ cwProb d N β 0 {ω | |magnetization ω| < ε} := by
  sorry
