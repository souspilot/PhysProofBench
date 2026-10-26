import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_C_001
-- PHYSPROOFBENCH-DECL: PI_C_001

open Real intervalIntegral

/-! PI_C_001 (draft). Unicyclist on a circular track of radius `R` (to the
contact point), leaning inward at angle `θ`, modelled as a uniform rod of
mass `m`, length `h`. In the frame co-rotating at `ω` the rod is static: the
torque about the contact point of the (position-dependent) centrifugal force
balances gravity's. The point-mass model gives `ω² = (g/R) tan θ`. -/

/-- `answer_blank`: the universal finite-size correction coefficient `c`.
(Expected: `c = 2/3`. Placing the centrifugal force at the centre of mass
gives the wrong `c = 1/2`.) -/
theorem PI_C_001 :
    ∃ c : ℝ, ∀ m g R h θ ω : ℝ, 0 < m → 0 < g → 0 < h → h < R → 0 < θ → θ < π / 2 →
      (∫ s in (0 : ℝ)..h, m / h * ω ^ 2 * (R - s * Real.sin θ) * (s * Real.cos θ))
          - m * g * (h / 2) * Real.sin θ = 0 →
      ω ^ 2 = g / R * Real.tan θ / (1 - c * (h / R) * Real.sin θ) := by
  sorry
