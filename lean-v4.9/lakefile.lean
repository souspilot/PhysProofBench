import Lake
open Lake DSL

-- Second Mathlib pin (docs/DECISIONS.md, "Two Mathlib pins"): Lean 4.9-era
-- Mathlib, the version today's specialist provers (Goedel-Prover-V2,
-- Pythagoras-Prover) were trained and evaluated on. Same Core and item
-- statements as ../lean (v4.34), ported only where the older API differs.
package PhysProofBench

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.9.0-rc1"

@[default_target]
lean_lib PhysProofBench where
  globs := #[.submodules `PhysProofBench]

lean_lib PhysProofBenchSolutions where
  globs := #[.submodules `PhysProofBenchSolutions]
