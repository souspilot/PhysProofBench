import PhysProofBench.Core.Thermo
import Mathlib.Analysis.Convex.Function

-- PHYSPROOFBENCH-ITEM: SM_01_E03_001
-- PHYSPROOFBENCH-DECL: freeEnergyHat_concave_convex

open PhysProofBench

/-- If the entropy `S(U, V, N)` is concave and the infimum defining
`F̂(β, V, N) = inf_U {βU - S(U, V, N)}` is finite, then `F̂` is concave in the
intensive variable `β > 0` and jointly convex in the extensive variables
`(V, N)`.

(Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
Exercise 1.3, with `F̂` from eqn. (1.15), p. 11–12. See `docs/SOURCE.md` for
the edition, and `items/SM_01_E03_001/notes.md` for the added hypotheses.) -/
theorem freeEnergyHat_concave_convex (S : ℝ × ℝ × ℝ → ℝ)
    (hS : ConcaveOn ℝ PosOrthant S)
    (hbdd : ∀ β : ℝ, 0 < β → ∀ V : ℝ, 0 < V → ∀ N : ℝ, 0 < N →
      BddBelow (Set.range fun U : Set.Ioi (0 : ℝ) => β * (U : ℝ) - S ((U : ℝ), V, N))) :
    (∀ V : ℝ, 0 < V → ∀ N : ℝ, 0 < N →
      ConcaveOn ℝ (Set.Ioi 0) (fun β : ℝ => freeEnergyHat S β V N)) ∧
    (∀ β : ℝ, 0 < β →
      ConvexOn ℝ {p : ℝ × ℝ | 0 < p.1 ∧ 0 < p.2} (fun p : ℝ × ℝ => freeEnergyHat S β p.1 p.2)) := by
  sorry
