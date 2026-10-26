# Physics-Intuition Set: Pilot 1 (10 items, 2026-10-26)

Design: `docs/INTUITION_SET.md`; item format: `docs/SCHEMA.md`. Items:
`items/PI_*` (`meta.yaml`, `nl.md`, `review.md`, sometimes `variants.lean`),
gold statements at `PhysProofBench/Items/PI_*.lean` on both pins. All are
paraphrased from official USAPhO solutions (AAPT), 2014–2025.

## Items and AI verdicts

| Item | Cat | Source | Physical decision | Plug-in trap | AI verdict |
|---|---|---|---|---|---|
| PI_A_001 | A | USAPhO 2023 B3c | arc − chord lives at 3rd order | `sin x ≈ x` ⇒ 0 | accept (calibration, easy) |
| PI_A_002 | A | USAPhO 2024 B2a | classical limit of Einstein solid, 2nd-order bookkeeping | 1st order ⇒ no correction | **accept** |
| PI_B_001 | B | USAPhO 2023 A3a | Carnot iff heat enters at top T | "reversible ⇒ Carnot" | **accept** + source flag |
| PI_B_002 | B | USAPhO 2025 A3d | each layer bears only the pressure jump ⇒ ln(b/a) | single-coil formula | revise (physics in hypotheses) |
| PI_C_001 | C | USAPhO 2014 A1 | centrifugal force not at CM ⇒ c = 2/3 | CM shortcut ⇒ c = 1/2 | revise (physics in hypotheses) |
| PI_C_002 | C | USAPhO 2020 B3 | ideal gas as reduced model; mean-field correction | ideal gas ⇒ ΔT = 0 | **accept** T′; revise entropy part |
| PI_D_001 | D | USAPhO 2024 B2b | piston's heat capacity enters γ_eff = 11/9 | γ = 5/3 | **accept** (best Lean form) |
| PI_D_002 | D | USAPhO 2023 A2b | ring of minima ⇒ Ω ∝ √δ | Ω = ω_c or √3 ω_c | **accept** |
| PI_E_001 | E | USAPhO 2025 A2g | Kepler III + flat energy spread ⇒ t^(−5/3) | t^(−2/3) | **accept** |
| PI_E_002 | E | USAPhO 2024 A2c | dimensional analysis P ~ GM²/R⁴ ⇒ R ∝ M^(−1/3) | R grows with M | **accept** (revised in review) |

Totals: 7 accept, 1 accept-as-calibration, 2 revise, 0 reject.

## What the pilot taught us

**1. The main risk is "physics in the hypotheses".** Once a statement is
formalized, everything is mathematics. Whether an item still tests physics
depends on *what the hypotheses contain*:

- *Good* (D_001, D_002, E_002, A_002): hypotheses are general laws or the
  model at a primitive level (the first law plus heat capacities, Newton's law
  for circular orbits, dimensional covariance, entropy plus `dE = T dS`). The
  conclusion blanks out the answer. The prover has to make the physical
  decision to finish.
- *Bad* (C_001, B_002): the hypothesis is the problem-specific equation
  that already encodes the insight (the distributed centrifugal torque
  integral; the "average field" stress inequality). What remains is calculus.

Proposed new admission criterion: **the physical decision must not be
derivable by reading the hypotheses.** Review question: "Which hypothesis,
if any, already contains the intuitive move?"

**2. `answer_blank` works well; `regime_blank` doesn't.** "Supply the
leading term / exponent / coefficient" is unique and checkable (with a
`≠ 0` or `> 0` guard). "Supply the regime" can't be stated without fixing the
class of admissible conditions (otherwise it is trivially satisfiable).
Replacement for regime items: give a candidate regime and ask the prover to
prove it is *sharp* (iff), or that a given condition is not necessary
(B_001's companion theorem).

**3. Formal statements catch loose expert solutions.** B_001: the official
USAPhO answer (`β ≪ ln α`) is sufficient but not necessary; the sharp
condition is `β/((1+β) ln α) → 0`. This is a feature of the benchmark, but it
means official answer keys can't be used as ground truth without review.

**4. Reusable Core definitions are emerging.** `DimCovariant` (E_002)
should move to `Core/` for all of category E.

## Reference proofs (answer to the maintainer's question)

Proposal: no reference proofs at admission. Require instead:
1. NL statement and NL proof (from the expert source);
2. a Lean statement reviewed as equivalent to the NL statement;
3. a **non-vacuity witness** (a concrete instance satisfying all
   hypotheses; recorded in each `review.md`);
4. for `answer_blank`, the expected answer in `meta.yaml`.

The first kernel-verified model proof becomes the item's reference. Items not
yet shown solvable are reported separately, so an unprovable (mis-stated)
item can't silently count as model failure.

## Limitations of this pilot

- **AI reviews were a single pass by one model in one context,** not
  independent reviewers. Treat them as a first screen.
- **One source.** All 10 items come from USAPhO, because its official solutions
  are freely downloadable. Graduate-level collections (Lim Yung-Kuo,
  Cahn–Nadgorny, Chicago/Princeton problem books) need copies the maintainer
  has access to.
- **Coverage gaps:** no quantum mechanics proper, optics, fluids or special
  relativity items yet.
- **Lean statements are typechecked only** (see below); no proofs.

## Trivial environment-check items (category T)

Six one-line items, `PI_T_001`–`PI_T_006`, run with the main set (not as
canaries) and are reported as category `T`. Each one exercises one part of
the environment: numerals, hypotheses, division by a nonzero quantity, an
existential answer, positivity, and a definition preceding the statement.
Their reference proofs (`tests/fixtures/reference_proofs/`) drive the oracle
pipeline check.

## Typecheck status

Checked 2026-10-26:

- `lake build PhysProofBench` succeeds on **both pins** (Lean/Mathlib v4.34.0
  and v4.9.0-rc1) with all 16 new items; the only warnings are `sorry`.
- Issues the old pin caught, now fixed: `ħω` is not an identifier in Lean
  4.9 (renamed to `ε` in PI_A_002); `positivity` differs between the pins in
  whether it uses a `v ≠ 0` hypothesis (PI_T_005 now uses `0 < v`).
- Companion drafts (`items/*/variants.lean`) typecheck on the main pin.
- Trivial items: reference proofs compile on both pins. An oracle run
  (`scripts/oracle_server.py`, generate + grade-run, both conditions) passes
  **12/12 on each pin**: prompt, extraction, statement gate, compile and axiom
  audit all work end to end.
- `--items all` plans all 34 items (SM, CAN, PI A–E, PI T) together, with 0 skips.
