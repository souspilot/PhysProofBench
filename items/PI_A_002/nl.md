# PI_A_002: Quantum correction to the heat capacity of an Einstein solid

*Paraphrased from USAPhO 2024, B2 a (official solution by the AAPT committee).*

## statement

A solid of `N` atoms is modelled as `3N` quantum oscillators of frequency
`ω` holding `m` quanta in total, so `E = ħω m`. Its entropy is
`S/k_B = (3N+m) ln(3N+m) - m ln m` (up to a constant). Using `dE = T dS`,
find the heat capacity at high temperature in the form
`C_V ≈ 3Nk_B (1 + b αⁿ)` with `α = ħω/(k_B T)`, i.e. determine `b` and `n`.

## proof

From `dE = T dS`: `ħω = k_B T ln((3N+m)/m)`, so `m = 3N/(e^α - 1)`.
**[Physical decision]** In the classical regime `α ≪ 1`. Because
`m ≈ 3N/α` has a `1/α` prefactor, the denominator must be expanded to
second order: `m ≈ 3N(1/α - 1/2 + α/12)`. Then
`E ≈ 3N(k_B T - ħω/2 + ħ²ω²/(12 k_B T))`, and differentiating gives
`C_V ≈ 3Nk_B(1 - α²/12)`. So `b = -1/12`, `n = 2`. (Exactly,
`C_V = 3Nk_B α² e^α/(e^α-1)²`.)
