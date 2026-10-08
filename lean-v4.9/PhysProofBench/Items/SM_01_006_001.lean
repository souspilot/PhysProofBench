import Mathlib

-- PHYSPROOFBENCH-ITEM: SM_01_006_001
-- PHYSPROOFBENCH-DECL: idealGas_entropy_per_particle

/-- Ideal gas: if the entropy per particle `s(e, v)` (energy per particle `e`,
specific volume `v`) has partial derivatives `∂s/∂e = c k_B / e` and
`∂s/∂v = k_B / v` throughout `e, v > 0` (the two equations of state
`1/T = c k_B / e`, `p/T = k_B / v`), then
`s(e, v) - s(e₀, v₀) = c k_B log(e/e₀) + k_B log(v/v₀)` for all positive
`e, v, e₀, v₀`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Example 1.6, p. 9–10. See `docs/SOURCE.md` for the edition, and
`items/SM_01_006_001/notes.md` for the added hypotheses.) -/
theorem idealGas_entropy_per_particle (s : ℝ → ℝ → ℝ) (c kB : ℝ)
    (he : ∀ e : ℝ, 0 < e → ∀ v : ℝ, 0 < v → HasDerivAt (fun e' => s e' v) (c * kB / e) e)
    (hv : ∀ e : ℝ, 0 < e → ∀ v : ℝ, 0 < v → HasDerivAt (fun v' => s e v') (kB / v) v) :
    ∀ e : ℝ, 0 < e → ∀ v : ℝ, 0 < v → ∀ e₀ : ℝ, 0 < e₀ → ∀ v₀ : ℝ, 0 < v₀ →
      s e v - s e₀ v₀ = c * kB * Real.log (e / e₀) + kB * Real.log (v / v₀) := by
  sorry
