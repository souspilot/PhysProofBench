import Mathlib.Analysis.SpecialFunctions.Log.NegMulLog
import Mathlib.Analysis.Convex.Jensen
import Mathlib.Data.Fintype.Card

/-!
# Finite probability distributions and Shannon entropy

Friedli–Velenik, *Statistical Mechanics: A Mathematical Introduction*,
§1.2 (p. 18-21): a finite set of microstates `Ω`, the set `M1(Ω)` of
probability distributions on it (a distribution is a function `μ : Ω → ℝ`
with `μ(ω) ≥ 0` and `∑ μ(ω) = 1`), and the Shannon entropy `S_Sh`
(Definition 1.8). Shared here because later sections (microcanonical,
canonical ensembles) reuse both.
-/

namespace PhysProofBench

variable {Ω : Type*} [Fintype Ω]

/-- `μ` is a probability distribution on the finite set `Ω`: matches
Friedli–Velenik's `M1(Ω)` (§1.2, eqn. (1.25)-(1.26) surrounding text). -/
def IsProbDist (μ : Ω → ℝ) : Prop :=
  (∀ ω, 0 ≤ μ ω) ∧ ∑ ω, μ ω = 1

/-- The uniform distribution on `Ω`. -/
noncomputable def uniformDist [Nonempty Ω] : Ω → ℝ := fun _ => 1 / Fintype.card Ω

/-- Shannon entropy (Friedli–Velenik, Definition 1.8, eqn. (1.27)).
`Real.log 0 = 0` gives the standard `0 log 0 := 0` convention for free. -/
noncomputable def shannonEntropy (μ : Ω → ℝ) : ℝ :=
  -∑ ω, μ ω * Real.log (μ ω)

/-- Bridge to Mathlib's `Real.negMulLog` (`x ↦ -x log x`), which carries the
concavity facts (`concaveOn_negMulLog`, `strictConcaveOn_negMulLog`) used to
prove `shannonEntropy_le_log_card`. -/
theorem shannonEntropy_eq_sum_negMulLog (μ : Ω → ℝ) :
    shannonEntropy μ = ∑ ω, Real.negMulLog (μ ω) := by
  simp [shannonEntropy, Real.negMulLog, Finset.sum_neg_distrib]

end PhysProofBench
