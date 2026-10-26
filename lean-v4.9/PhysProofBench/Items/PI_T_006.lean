import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_T_006
-- PHYSPROOFBENCH-DECL: kinetic_energy_double_speed

/-! Trivial environment check (a definition before the statement (`unfold`, `ring`)); not a physics item. -/

namespace PhysProofBench.PI_T_006

noncomputable def kineticEnergy (m v : ℝ) : ℝ := m * v ^ 2 / 2

end PhysProofBench.PI_T_006

open PhysProofBench.PI_T_006

theorem kinetic_energy_double_speed (m v : ℝ) :
    kineticEnergy m (2 * v) = 4 * kineticEnergy m v := by
  sorry
