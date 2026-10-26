# PI_D_001: Oscillating piston that shares heat with the gas

*Paraphrased from USAPhO 2024, B2 b (official solution by the AAPT committee).*

## statement

A vertical cylinder in vacuum holds a monatomic ideal gas under a heavy
piston made of a classical solid. Gas and piston contain the same number of
atoms, the gas's mass is negligible, and gas and piston stay in thermal
equilibrium with each other but exchange no heat with anything else. At
equilibrium the gas column has height `h`. Find the angular frequency of
small vertical oscillations of the piston, in terms of `g` and `h` only.

## proof

**[Physical decision]** The process is adiabatic for the *combined* system,
and the solid piston stores heat (`3nR`) without doing work. So
`(3/2 nR + 3nR) dT = -P dV`, which with `PV = nRT` gives `PV^γ = const`,
`γ = C_P/C_V = (5/2 + 3)/(3/2 + 3) = 11/9`. Linearizing the net force about
equilibrium: `F ≈ -(γP₀A/h) z`. Equilibrium gives `P₀A = Mg`, so
`ω² = γg/h = 11g/(9h)`.
