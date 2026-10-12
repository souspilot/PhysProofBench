import PhysProofBench.Core.LatticeGas

-- PHYSPROOFBENCH-ITEM: CAN_00_003_001
-- PHYSPROOFBENCH-DECL: hardCoreGrandPartition_eq

open PhysProofBench

/-- Canary item (pipeline sanity check, not scored): the grand canonical
partition function of the hard-core lattice gas in `V` cells is
`(1 + e^{βμ})^V` (binomial theorem; Friedli–Velenik §1.3.2). -/
theorem hardCoreGrandPartition_eq (V : ℕ) (β μ : ℝ) :
    hardCoreGrandPartition V β μ = (1 + Real.exp (β * μ)) ^ V := by
  rw [hardCoreGrandPartition, add_comm 1 (Real.exp (β * μ)), add_pow]
  refine Finset.sum_congr rfl fun N _ => ?_
  rw [one_pow, mul_one, ← Real.exp_nat_mul]
  ring_nf

