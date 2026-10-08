import Mathlib
import PhysProofBench.Core.Thermo

-- PHYSPROOFBENCH-ITEM: SM_01_E02_001
-- PHYSPROOFBENCH-DECL: entropy_concave

open PhysProofBench

/-- A thermodynamic entropy `S(U, V, N)` that is positively homogeneous of
degree one and superadditive (merging two systems never lowers the total
entropy) is concave on the positive orthant.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Exercise 1.2, eqn. (1.8), p. 8. See `docs/SOURCE.md` for the edition, and
`items/SM_01_E02_001/notes.md` for the added hypotheses.) -/
theorem entropy_concave (S : ℝ × ℝ × ℝ → ℝ)
    (hhom : ∀ t : ℝ, 0 < t → ∀ X ∈ PosOrthant, S (t • X) = t * S X)
    (hsup : ∀ X ∈ PosOrthant, ∀ Y ∈ PosOrthant, S X + S Y ≤ S (X + Y)) :
    ConcaveOn ℝ PosOrthant S := by
  sorry
