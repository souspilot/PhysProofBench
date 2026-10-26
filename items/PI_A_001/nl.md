# PI_A_001: Excess path length of a slightly bent trajectory

*Paraphrased from USAPhO 2023, B3 c.i (official solution by the AAPT committee).*

## statement

A neutral-looking particle carrying a tiny charge travels from a supernova to
Earth, a straight-line distance `d`, through a uniform magnetic field
perpendicular to the line of sight. Its path is an arc of a circle whose
radius `r` is much larger than `d`. To leading nontrivial order in `d/r`, how
much longer is the arc `ℓ` than the straight-line distance `d`?

## proof

The arc subtends angle `ℓ/r`, so the chord is `d = 2r sin(ℓ/(2r))`.
**[Physical decision]** The first-order term of the sine reproduces `ℓ`
exactly and cancels, so the first non-vanishing effect comes from the cubic
term: `ℓ - d ≈ ℓ³/(24 r²)`. Since `ℓ ≈ d` at this order, `ℓ - d ≈ d³/(24 r²)`.
The error is bounded by the quintic Taylor term, `ℓ⁵/(1920 r⁴)`.
