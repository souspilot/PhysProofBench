import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_C_002
-- PHYSPROOFBENCH-DECL: PI_C_002

open Real Filter Topology

namespace PhysProofBench.PI_C_002

/-! PI_C_002 (draft). "Real" monatomic gas with weak pairwise attraction and
negligible atomic volume; mean-field energy `E = (3/2) N k T - a N² / V`.
Free (Joule) expansion `V → 2V` in an insulated container conserves `E`.
For an ideal gas (`a = 0`) the temperature is unchanged. -/

noncomputable def energy (N k a T V : ℝ) : ℝ := 3 / 2 * N * k * T - a * N ^ 2 / V

end PhysProofBench.PI_C_002

open PhysProofBench.PI_C_002

/-- `answer_blank`: the cooling coefficient `c` in `T' = T - c a N / (k V)`.
(Expected: `c = 1/3`.) -/
theorem PI_C_002 :
    ∃ c : ℝ, ∀ N k a T V T' : ℝ, 0 < N → 0 < k → 0 < V →
      energy N k a T' (2 * V) = energy N k a T V →
      T' = T - c * a * N / (k * V) := by
  sorry
