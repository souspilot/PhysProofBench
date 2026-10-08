import Mathlib

-- PHYSPROOFBENCH-ITEM: SM_01_E05_001
-- PHYSPROOFBENCH-DECL: vanDerWaals_critical_temperature

/-- Van der Waals isotherms `p(v, T) = k_B T / (v - b) - a / v²` on `v > b`
change behaviour at the critical temperature `T_c = 8a / (27 k_B b)`: above
`T_c` pressure is strictly decreasing in the specific volume `v`; below `T_c`
(and at positive temperature) there is a nondegenerate interval of volumes on
which pressure is strictly increasing.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Exercise 1.5, eqn. (1.23), p. 15. See `docs/SOURCE.md` for the edition.) -/
theorem vanDerWaals_critical_temperature (a b kB : ℝ) (ha : 0 < a) (hb : 0 < b)
    (hkB : 0 < kB) :
    (∀ T : ℝ, 8 * a / (27 * kB * b) < T →
      StrictAntiOn (fun v : ℝ => kB * T / (v - b) - a / v ^ 2) (Set.Ioi b)) ∧
    (∀ T : ℝ, 0 < T → T < 8 * a / (27 * kB * b) →
      ∃ v₁ v₂ : ℝ, b < v₁ ∧ v₁ < v₂ ∧
        StrictMonoOn (fun v : ℝ => kB * T / (v - b) - a / v ^ 2) (Set.Icc v₁ v₂)) := by
  sorry
