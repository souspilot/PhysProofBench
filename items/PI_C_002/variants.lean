import PhysProofBench.Items.PI_C_002

open Real Filter Topology
open PhysProofBench.PI_C_002

/-! Companion statements for PI_C_002: drafts, not graded. -/

/-- Integrated entropy for this gas (sketch: deriving it from the first law
`T dS = dE + P dV` with `P = N k T / V - a N² / V²` is part of the intended
task; a revision should state those as hypotheses on an unknown `S`). -/
noncomputable def entropy (N k T V : ℝ) : ℝ := N * k * (Real.log V + 3 / 2 * Real.log T)

theorem PI_C_002_entropy (N k a T V : ℝ) (hN : 0 < N) (hk : 0 < k) (hT : 0 < T)
    (hV : 0 < V) (ha : 0 ≤ a) (hsmall : a * N / (V * k * T) ≤ 1 / 2) :
    |entropy N k (T - a * N / (3 * k * V)) (2 * V) - entropy N k T V
        - (N * k * Real.log 2 - a * N ^ 2 / (2 * V * T))|
      ≤ N * k * (a * N / (V * k * T)) ^ 2 := by
  sorry
