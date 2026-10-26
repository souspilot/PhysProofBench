import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_E_002
-- PHYSPROOFBENCH-DECL: PI_E_002

open Real

namespace PhysProofBench.PI_E_002

/-! PI_E_002 (draft). White dwarf of mass `M`, radius `R`, roughly uniform
density. (1) Dimensional analysis: the central pressure depends only on
`G, M, R`, so it must be `C · G M² / R⁴`. (2) Non-relativistic electron
degeneracy pressure `P = K ρ^(5/3)` with `ρ ∝ M/R³` then fixes `R ∝ M^n`. -/

/-- Dimensional covariance: changing the mass/length/time units by `λM, λL, λT`
rescales the number for a quantity of dimension `L^a M^b T^c` by
`λL^a λM^b λT^c`. `G : L³ M⁻¹ T⁻²`, pressure `: M L⁻¹ T⁻²`. -/
def DimCovariant (P : ℝ → ℝ → ℝ → ℝ) : Prop :=
  ∀ G M R lM lL lT : ℝ, 0 < G → 0 < M → 0 < R → 0 < lM → 0 < lL → 0 < lT →
    P (G * lL ^ 3 / (lM * lT ^ 2)) (M * lM) (R * lL) = P G M R * (lM / (lL * lT ^ 2))

end PhysProofBench.PI_E_002

open PhysProofBench.PI_E_002

/-- `answer_blank`: the mass–radius exponent. The central pressure is only
known to be dimensionally covariant (no `G M² / R⁴` given); degeneracy
pressure of the uniform-density star supplies the other side.
(Expected `n = -1/3`.) -/
theorem PI_E_002 :
    ∃ n : ℝ, ∀ (Pc : ℝ → ℝ → ℝ → ℝ) (G K : ℝ) (Rad : ℝ → ℝ), DimCovariant Pc →
      0 < G → 0 < K → 0 < Pc 1 1 1 →
      (∀ M, 0 < M → 0 < Rad M ∧ Pc G M (Rad M) = K * (M / Rad M ^ 3) ^ ((5 : ℝ) / 3)) →
      ∀ M, 0 < M → Rad M = Rad 1 * M ^ n := by
  sorry
