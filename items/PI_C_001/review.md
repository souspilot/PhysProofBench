# Review: PI_C_001

## AI review (2026-10-26)

**1. Physics check: PASS.** Recomputed the integral and the balance: the
result is `c = 2/3`. The rotating-frame treatment is valid because the rod is
at rest there, so there is no Coriolis term. Wheel gyroscopics are excluded
by the rod model; that's a stated modelling choice, not a hidden assumption.

**2. Plug-in check: PASS (strong).** Lumping the centrifugal force at the
CM gives `ω² = g tan θ/(R - (h/2) sin θ)`, so `c = 1/2`. That is a
plausible-looking wrong answer, and exactly the misconception the item
targets.

**3. Formalization check: CONCERN.** The statement hands over the
distributed centrifugal torque integral, which *is* the physical insight.
With it given, the task reduces to evaluating a polynomial integral, so the
trap is defused by the statement itself. Fix: state the hypothesis as
"static in the rotating frame" with the force density per element
(`dm · ω² · (distance to axis)`) and let the prover assemble the torque, or
give the body as a measure and require the prover to choose the reduction.
Non-vacuity: `ω² = g tan θ/(R - (2/3)h sin θ) > 0` exists for `h < R`.

**4. Category check: PASS.** A textbook case of model reduction with a
finite-size correction.

**Verdict: revise.** The physics is excellent, but the Lean form must not
contain the torque integral. Contamination risk is high (2014).

## Human review

- [ ] accept / revise / reject:
- reason:
