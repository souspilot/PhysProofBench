# Review: PI_D_001

## AI review (2026-10-26)

**1. Physics check: PASS.** Verified from the Lean hypotheses directly:
`T' = -(2/9)T/z`, `F'(h) = -(11/9) nRT/h² = -(11/9)Mg/h`, so `ω² = (11/9)g/h`.
The assumptions match the source: the thermal coupling between gas and piston
is fast relative to the oscillation, and coupling to the environment is
absent. A real experiment would need those timescale separations; worth a
`hidden_assumptions` note (`source_stated`).

**2. Plug-in check: PASS (strong).** "Adiabatic oscillation of an ideal
gas, γ = 5/3" is the reflex answer, and it is wrong. A good test of whether
the solver identifies the right thermodynamic system.

**3. Formalization check: GOOD.** The statement gives only the first law
for the combined system (heat capacities stated, not γ) and the ideal gas
law. The prover must derive the effective adiabat and linearize, so the
physical content stays inside the task. `answer_blank` over a universal `γ`
is unique. Non-vacuity: `T z = T_h (h/z)^(2/9)` with `nRT_h/h = Mg`.
Minor: the heat capacity `3nR` is entered as a number, not derived from
"same number of atoms, classical solid"; that's acceptable.

**4. Category check: PASS.** Linearization about equilibrium, with a
thermodynamic twist.

**Verdict: accept.** The best Lean form in the pilot: the physics decision is
needed to prove it.

## Human review

- [ ] accept / revise / reject:
- reason:
