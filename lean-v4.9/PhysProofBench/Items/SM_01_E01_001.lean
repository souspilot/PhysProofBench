import Mathlib
import PhysProofBench.Core.Thermo

-- PHYSPROOFBENCH-ITEM: SM_01_E01_001
-- PHYSPROOFBENCH-DECL: entropy_positively_homogeneous

open PhysProofBench

/-- A thermodynamic entropy `S(U, V, N)` that scales correctly under
combining `n` identical copies of a system (`S(nX) = n S(X)` for every positive
integer `n`) and is continuous is positively homogeneous of degree one:
`S(tU, tV, tN) = t S(U, V, N)` for all real `t > 0`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Exercise 1.1, eqn. (1.7), p. 7. See `docs/SOURCE.md` for the edition, and
`items/SM_01_E01_001/notes.md` for the added hypotheses.) -/
theorem entropy_positively_homogeneous (S : ℝ × ℝ × ℝ → ℝ)
    (hcont : ContinuousOn S PosOrthant)
    (hint : ∀ n : ℕ, 0 < n → ∀ X ∈ PosOrthant, S ((n : ℝ) • X) = n * S X) :
    ∀ t : ℝ, 0 < t → ∀ X ∈ PosOrthant, S (t • X) = t * S X := by
  sorry
