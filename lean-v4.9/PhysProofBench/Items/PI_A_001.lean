import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_A_001
-- PHYSPROOFBENCH-DECL: PI_A_001

open Real Filter Topology Asymptotics

namespace PhysProofBench.PI_A_001

/-! PI_A_001 (draft statement, not yet proved). A charged particle in a uniform
magnetic field moves on a circle of radius `r`. After path length `ℓ` its
straight-line displacement is the chord `2 r sin (ℓ / (2 r))`. -/

noncomputable def chord (r ℓ : ℝ) : ℝ := 2 * r * Real.sin (ℓ / (2 * r))

end PhysProofBench.PI_A_001

open PhysProofBench.PI_A_001

/-- `answer_blank`: the prover must supply the leading nontrivial term of the
excess path length `ℓ - chord`. (Expected: `C = 1 / (24 r²)`, `n = 3`; the
first-order term vanishes.) `C ≠ 0` makes `(C, n)` unique. -/
theorem PI_A_001 (r : ℝ) (hr : 0 < r) :
    ∃ C : ℝ, ∃ n : ℕ, C ≠ 0 ∧
      (fun ℓ => ℓ - chord r ℓ - C * ℓ ^ n) =o[𝓝 0] (fun ℓ => ℓ ^ n) := by
  sorry
