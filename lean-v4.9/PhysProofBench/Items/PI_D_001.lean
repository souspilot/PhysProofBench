import Mathlib

-- PHYSPROOFBENCH-ITEM: PI_D_001
-- PHYSPROOFBENCH-DECL: PI_D_001

open Real

/-! PI_D_001 (draft). Vertical cylinder in vacuum: `n` moles of monatomic ideal
gas under a piston of mass `M`, area `A`, made of a classical solid with as
many atoms as the gas (heat capacity `3 n R`, no expansion). Gas and piston
stay in thermal equilibrium; no heat to the environment; gas mass negligible.
`T z` is the common temperature when the gas column has height `z`. -/

/-- `answer_blank`: small vertical oscillations about the equilibrium height
`h` have `ω² = γ g / h` for a universal `γ`. (Expected `γ = 11/9`; using the
gas-only adiabatic index `5/3` is the plug-in trap.) -/
theorem PI_D_001 :
    ∃ γ : ℝ, ∀ (n R M A g h : ℝ) (T : ℝ → ℝ), 0 < n → 0 < R → 0 < M → 0 < A →
      0 < g → 0 < h →
      -- first law for gas + piston: (C_gas + C_piston) dT = - P dV, V = A z
      (∀ z, 0 < z → HasDerivAt T (-(n * R * T z / (A * z)) * A / (3 / 2 * n * R + 3 * n * R)) z) →
      -- mechanical equilibrium at height h
      n * R * T h / (A * h) * A = M * g →
      -- ω² = -(1/M) dF/dz with F z = P z · A - M g
      -(deriv (fun z => n * R * T z / (A * z) * A - M * g) h) / M = γ * g / h := by
  sorry
