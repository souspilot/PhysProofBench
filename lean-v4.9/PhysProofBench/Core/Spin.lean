import Mathlib

/-!
# Ising spins

Friedli–Velenik use spins `ωᵢ ∈ {-1, 1}` (§1.4, ch. 2–3). We encode a spin as
a `Bool` (`true ↦ +1`, `false ↦ -1`) so that configuration spaces
`Λ → Bool` are finite types with no side conditions; `spin` recovers the
real value `±1` used in Hamiltonians.
-/

namespace PhysProofBench

/-- The real value `±1` of a spin encoded as a `Bool`: `true ↦ 1`, `false ↦ -1`. -/
def spin (b : Bool) : ℝ := if b then 1 else -1

end PhysProofBench
