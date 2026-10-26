# PI_C_001: Leaning unicyclist, point mass vs. extended rider

*Paraphrased from USAPhO 2014, A1 (official solution by the AAPT committee).*

## statement

A unicyclist rides around a circular track of radius `R` (measured to the
contact point), leaning inward at angle `θ` to the vertical. Treated as a
point mass, they need `ω² = (g/R) tan θ`. Now model them as a uniform rod of
length `h` (not negligible compared with `R`). Find the corrected `ω`; in
particular the coefficient `c` in `ω² = (g/R) tan θ / (1 - c (h/R) sin θ)`.

## proof

In the co-rotating frame the rod is static, so torques about the contact
point balance. **[Physical decision]** The centrifugal force on an element at
distance `s` along the rod is proportional to its distance `R - s sin θ` from
the axis, so it cannot be lumped at the centre of mass. Its torque is
`∫₀ʰ (m/h) ω² (R - s sin θ)(s cos θ) ds = mω²h cos θ (R/2 - h sin θ/3)`.
Gravity contributes `-mg(h/2) sin θ`. Setting the sum to zero gives
`ω² = (g/R) tan θ / (1 - (2h/3R) sin θ)`, so `c = 2/3`. As `h/R → 0`
this reduces to the point-mass model.
