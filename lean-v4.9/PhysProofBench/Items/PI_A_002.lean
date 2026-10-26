import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_A_002
-- PHYSPROOFBENCH-DECL: PI_A_002

open Real Filter Topology Asymptotics

namespace PhysProofBench.PI_A_002

/-! PI_A_002 (draft). Einstein solid: `3N` oscillators, `m` quanta of energy
`ε` each. Entropy (in units of `k_B`) is given; the temperature is fixed by
the first law `dE = T dS`, i.e. `dS/dm = ε / (k_B T)`. -/

noncomputable def einsteinEntropy (N m : ℝ) : ℝ :=
  (3 * N + m) * Real.log (3 * N + m) - m * Real.log m

end PhysProofBench.PI_A_002

open PhysProofBench.PI_A_002

/-- `answer_blank`: leading quantum correction to Dulong–Petit at high `T`.
The prover supplies `b, n` with `C_V / (3 N k_B) = 1 + b α^n + o(α^n)`,
`α = ε / (k_B T)`. (Expected: `b = -1/12`, `n = 2`.) -/
theorem PI_A_002 (N ε kB : ℝ) (hN : 0 < N) (hε : 0 < ε) (hk : 0 < kB)
    (m : ℝ → ℝ) (hm_pos : ∀ T, 0 < T → 0 < m T)
    (hfirst : ∀ T, 0 < T → HasDerivAt (einsteinEntropy N) (ε / (kB * T)) (m T))
    (hdiff : ∀ T, 0 < T → DifferentiableAt ℝ m T) :
    ∃ b : ℝ, ∃ n : ℕ, b ≠ 0 ∧ 0 < n ∧
      (fun T => deriv (fun T' => ε * m T') T / (3 * N * kB) - 1
          - b * (ε / (kB * T)) ^ n)
        =o[atTop] (fun T => (ε / (kB * T)) ^ n) := by
  sorry
