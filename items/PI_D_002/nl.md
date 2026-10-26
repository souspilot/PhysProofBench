# PI_D_002: Circular orbits around a ring of potential minima

*Paraphrased from USAPhO 2023, A2 b (official solution by the AAPT committee).*

## statement

A particle of charge `-q`, mass `m`, moves in a horizontal plane. A large
charge `Q` sits a distance `R` below the origin, so for `r ≪ R` the particle
feels `V ≈ (k/2) r²` with `k = qQ/(4πε₀R³)`. Circular orbits then have
`ω_c = √(k/m)` at any radius. Now fix a charge `-q` at the origin. Find
the angular frequency of a circular orbit of radius `r₀ + δ`, `δ ≪ r₀`,
where `r₀` is the radius of the potential minimum.

## proof

`V(r) = (k/2)r² + κ/r` with `κ = q²/4πε₀` has a ring of minima at
`r₀ = (κ/k)^{1/3}`, where `V''(r₀) = 3k`. **[Physical decision]** A circular
orbit needs a net inward force `mΩ²r = V'(r)`. At `r₀` this force vanishes,
so near the ring it comes only from the linear restoring term
`V'(r₀+δ) ≈ 3kδ`. Hence `Ω² ≈ 3kδ/(m r₀)`, i.e. `Ω ≈ √3 ω_c √(δ/r₀)`. That is
much slower than `ω_c`, and it vanishes as `δ → 0`.
