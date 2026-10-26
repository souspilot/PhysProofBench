# Review: PI_B_002

## AI review (2026-10-26)

**1. Physics check: PASS.** With `I_k = t(B_k - B_{k-1})/μ₀` (Ampère, turn
density `1/t`), force per length `I_k·(B_k+B_{k-1})/2`, and hoop tension
`f·r_k`, the per-layer inequality matches the official one exactly.
Telescoping and the Riemann-sum limit are correct. The numeric part
(`≈ 23 T` for `a = 0.1 m`, `b = 0.3 m`, copper) is consistent.

**2. Plug-in check: PASS.** The single-layer result `B² ≤ (π/2)σμ₀ t/a`
does not extend by "using total thickness". The log comes from the
layered pressure-difference argument.

**3. Formalization check: CONCERN.** The key physical move ("each layer
sees the average field, hence only the pressure jump") is *supplied* as
hypothesis `hstress`. After that, the bound is algebra and the limit is
a Riemann sum. The Lean task tests mathematics, not the physics.
Options: (a) state the force on a current sheet only via fields at the
wire's location and let the prover derive the averaging (hard to
formalize cleanly); (b) accept as a "B, mostly math" item. Non-vacuity:
`I ≡ 0, B ≡ 0` satisfies every hypothesis, but that is fine because the
conclusion is an upper bound. A reviewer may want an achievability
statement too.

**4. Category check: PASS (B, thin-wire limit), but the regime is easy;
the intuition is in the modelling.**

**Verdict: revise.** Good physics, but the current Lean form gives the
physics away. Either reformulate (a) or swap it for an item where the limit
itself is the physical decision.

## Human review

- [ ] accept / revise / reject:
- reason:
