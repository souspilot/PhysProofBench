# PI_B_002: Strength limit of a multi-layer electromagnet

*Paraphrased from USAPhO 2025, A3 b, d (official solution by the AAPT committee).*

## statement

A solenoid is wound from many layers of round wire of diameter `t` and
tensile strength `σ`, filling the radii from `a` to `b`. Adjacent layers
barely don't touch, and the current in each layer is tuned so all wires are
equally stressed. Show that the field inside satisfies
`B² ≤ (π/2) σ μ₀ Σ_k t/r_k`, and that in the thin-wire limit this becomes
`B_max² = (π/2) σ μ₀ ln(b/a)`.

## proof

The magnetic field `B` exerts an outward pressure `B²/2μ₀` on the winding.
**[Physical decision]** A layer with field `B_k` inside and `B_{k-1}` outside
only feels the *difference* `(B_k² - B_{k-1}²)/2μ₀`. Equivalently, its
current sits in the average field `(B_k + B_{k-1})/2`. Hoop balance at
radius `r_k` against tension `(π/4)t²σ` gives
`B_k² - B_{k-1}² ≤ (π/2)σμ₀ t/r_k`. Summing telescopes to the bound, and as
`t → 0` the sum is a Riemann sum for `∫_a^b du/u = ln(b/a)`.
