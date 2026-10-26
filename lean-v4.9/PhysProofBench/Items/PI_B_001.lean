import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_B_001
-- PHYSPROOFBENCH-DECL: PI_B_001

open Real Filter Topology

namespace PhysProofBench.PI_B_001

/-! PI_B_001 (draft). One mole of monatomic ideal gas, cycle: isobaric heating
`T₀ → (1+β)T₀` at `P₀`, isothermal expansion to `P₀/α`, isobaric cooling,
isothermal compression. Heats in units of `P₀V₀`. -/

/-- Heat absorbed: isobaric step `c_p ΔT = (5/2) β`, isothermal step `(1+β) ln α`. -/
noncomputable def heatIn (α β : ℝ) : ℝ := 5 / 2 * β + (1 + β) * Real.log α
/-- Net work: the two isobaric works cancel; isotherms give `β ln α`. -/
noncomputable def work (α β : ℝ) : ℝ := β * Real.log α
noncomputable def efficiency (α β : ℝ) : ℝ := work α β / heatIn α β
noncomputable def carnot (β : ℝ) : ℝ := 1 - 1 / (1 + β)

end PhysProofBench.PI_B_001

open PhysProofBench.PI_B_001

/-- The sharp regime: the cycle approaches Carnot efficiency (between its own
extreme temperatures) exactly when `β / ((1+β) ln α) → 0`, i.e. when the heat
taken in at non-maximal temperature is negligible. -/
theorem PI_B_001 (F : Filter (ℝ × ℝ)) (hF : ∀ᶠ p in F, 1 < p.1 ∧ 0 < p.2) :
    Tendsto (fun p => efficiency p.1 p.2 / carnot p.2) F (𝓝 1) ↔
      Tendsto (fun p => p.2 / ((1 + p.2) * Real.log p.1)) F (𝓝 0) := by
  sorry
