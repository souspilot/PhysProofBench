import PhysProofBench.Core.Ising
import Mathlib.Analysis.Convex.Function

-- PHYSPROOFBENCH-ITEM: SM_03_005_001
-- PHYSPROOFBENCH-DECL: isingPressureFree_convex

open PhysProofBench

/-- For every finite `Λ ⊂ ℤᵈ`, the finite-volume Ising pressure with free
boundary condition, `(β, h) ↦ ψ^∅_Λ(β, h)`, is jointly convex on `β ≥ 0`,
`h ∈ ℝ`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Lemma 3.5, p. 84, free boundary condition case. See `docs/SOURCE.md` for the
edition.) -/
theorem isingPressureFree_convex {d : ℕ} (Λ : Finset (Site d)) :
    ConvexOn ℝ (Set.Ici (0 : ℝ) ×ˢ Set.univ)
      (fun p : ℝ × ℝ => isingPressureFree Λ p.1 p.2) := by
  sorry
