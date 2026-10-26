import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_E_001
-- PHYSPROOFBENCH-DECL: PI_E_001

open Real

namespace PhysProofBench.PI_E_001

/-! PI_E_001 (draft). Tidal disruption: bound debris has specific orbital
energy `ε` spread uniformly (density `μ` per unit energy) on `[ε_min, 0)`.
Each fragment returns after one Kepler period `T(ε) = 2π √(a³ / (G M))`,
`a = -G M / (2 ε)`. `Mret t` is the mass returned by time `t`. -/

noncomputable def keplerPeriod (G M ε : ℝ) : ℝ :=
  2 * π * Real.sqrt ((-(G * M) / (2 * ε)) ^ 3 / (G * M))

end PhysProofBench.PI_E_001

open PhysProofBench.PI_E_001

/-- `answer_blank`: the fallback rate (∝ luminosity) is a power law `t^(-n)`
after the first return. (Expected `n = 5/3`.) -/
theorem PI_E_001 :
    ∃ n : ℝ, ∀ (G M μ εmin : ℝ) (Mret : ℝ → ℝ), 0 < G → 0 < M → 0 < μ → εmin < 0 →
      (∀ t, keplerPeriod G M εmin < t →
        Mret t = μ * (sSup {ε | ε < 0 ∧ keplerPeriod G M ε ≤ t} - εmin)) →
      ∃ C > 0, ∀ t, keplerPeriod G M εmin < t → HasDerivAt Mret (C * t ^ (-n)) t := by
  sorry
