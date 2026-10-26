# Physics-Intuition Set (draft design, 2026-10-26)

Status: **proposal, awaiting maintainer sign-off.** Nothing here is
collected yet. This doc fixes *what we are looking for* before we look.

## Motivation

Existing items (Friedli–Velenik, canaries) are mathematics that happens to
live in a physics book: once the statement is written, no physical judgment
is needed. The goal of this set is the opposite: problems where **knowing
the formulas and the mathematics is not enough** — the solver has to make a
physical decision (which quantity is small, which effect can be dropped,
which regime applies), and that decision is what makes the Lean proof go
through.

The set is meant to serve as (1) an evaluation and (2) a training
environment (RL with Lean-kernel reward) for an open model.

## The admission test

An item qualifies only if all four hold:

1. **Physical decision.** The solution contains at least one step that is a
   physics judgment, not algebra: choosing a small parameter, dropping a
   term/effect, picking a limit, linearizing about the right state,
   identifying the relevant scale.
2. **Plug-in fails.** A solver who substitutes into the "obvious" textbook
   formula either gets the wrong answer, gets no answer, or cannot justify
   its validity. We record this as the item's *plug-in trap*.
3. **Checkable decision.** The formal statement makes the decision
   verifiable: a wrong regime or a wrong leading term makes the theorem
   false (or unprovable), not merely sub-optimal.
4. **Credible source.** The problem and its solution come from a source
   with expert standing (see Sources). Fresh problems are a last resort and
   need a named expert reviewer.

Explicitly **excluded**: formula substitution ("find the period of a 2 m
pendulum"); pure math in physics clothing; approximations that are only
numerical rounding; problems whose only difficulty is a long computation.

## Categories (proposed: 5)

Each category comes with its natural Lean shape. Target ~10 items each;
the split can move once we see what sources supply.

| # | Category | The intuitive move | Typical Lean shape |
|---|---|---|---|
| A | **Leading-order expansion** | Identify the small parameter and expand (sin θ ≈ θ, v ≪ c, weak field, thin shell). | Exact model + regime hypothesis `ε ≤ ε₀` ⇒ explicit error bound; or `=o[𝓝 0]`. |
| B | **Limiting regimes** | Know what survives in a limit (high/low T, near/far field, dilute, large N, short/long time). | `Tendsto` / `~[atTop]` / `IsEquivalent` on the exact expression. |
| C | **Model reduction (neglect an effect)** | Justify dropping a physical effect when a dimensionless ratio is small (massless spring, drag, recoil, radiation reaction, quasi-static). | Full model vs reduced model; difference bounded in terms of the ratio. |
| D | **Linearization & stability** | Find the equilibrium, linearize, read off frequency/stability (effective potential, normal modes, small oscillations). | Exact ODE/potential; statement about the second derivative / linearized frequency, or a stability predicate. |
| E | **Scaling & dimensional analysis** | Get the functional form from dimensions or self-similarity before (or instead of) solving. | Invariance-under-rescaling hypothesis ⇒ `f x = C * x^a`; exponent is the content. |

Open question for review: a sixth candidate, **symmetry / conservation
shortcuts** (Gauss, virial theorem, adiabatic invariants), is clearly
physics knowledge but usually yields *exact* statements; keep it out unless
it carries an approximation (adiabatic invariance does).

### What the prover supplies (tagged per item)

- `shape: bound_given` — regime and approximate answer are in the
  statement; the prover proves the error bound. Tests justification.
- `shape: answer_blank` — the statement has a hole for the leading term or
  exponent (`∃ a, ...` with the answer pinned by a uniqueness lemma, or a
  separate equality check). Tests the intuition directly.
- `shape: regime_blank` — the prover must supply the regime condition
  (e.g. the threshold ε₀) under which the claim holds.

## Sources (in priority order)

Olympiad / graduate level, chosen for expert-written solutions and for
systematic coverage across physics:

1. **Graduate qualifying-exam collections:** Lim Yung-Kuo (ed.), *Problems
   and Solutions on* Mechanics / Electromagnetism / Optics / Thermodynamics
   & Statistical Mechanics / Quantum Mechanics / Atomic, Nuclear & Particle
   Physics / Solid State; Cahn & Nadgorny, *A Guide to Physics Problems*
   (Parts 1–2); Cronin, Greenberg & Telegdi, *University of Chicago
   Graduate Problems in Physics*; Newbury et al., *Princeton Problems in
   Physics with Solutions*.
2. **Olympiads:** IPhO archive with official solutions; APhO; USAPhO
   (AAPT); Physics Cup; J. Kalda's olympiad study guides (strong on
   approximation ideas).
3. **Textbooks with worked approximation problems:** Morin, *Introduction
   to Classical Mechanics*; Landau & Lifshitz (Mechanics, Fluid Mechanics,
   Statistical Physics problems); Jackson; Sakurai.

Copyright rules from `plan.md` §2.1 still apply: paraphrase, cite, no
verbatim transcription. Contamination note: all of these are likely in
training data; we record `contamination_risk` per item and prefer
paraphrased/re-parameterized statements.

## Item record

Items follow the general item schema, `docs/SCHEMA.md`: `items/PI_<cat>_<nnn>/`
with `meta.yaml` (intuition fields such as `shape`, `small_parameter`,
`regime`, `intuition_move`, `plug_in_trap`, `expected_answer`,
`contamination_risk` and the source live under `metadata`), `nl.md`
(paraphrased problem and expert solution, with the physical decision step
marked), `review.md`, and optionally `variants.lean`. The gold Lean
statement is `PhysProofBench/Items/<id>.lean` on each pin.

Category `T` holds trivial environment-check items (`docs/SCHEMA.md`).

## Review protocol

Status flow: `candidate → ai_reviewed → human_approved | rejected`.

**AI review** (independent passes, results written to `review.md`):

1. *Physics check* — is the expert solution correct, and is the regime
   stated correctly?
2. *Plug-in check* — attempt the problem by pure formula substitution; does
   it fail as claimed? (If it succeeds, reject.)
3. *Formalization check* — does the Lean sketch capture the decision, or
   could it be proved without making it? Any hidden/strengthened
   hypotheses?
4. *Category check* — right category, and is the "intuitive move" the real
   crux?

**Human review** (maintainer): accept / revise / reject with a one-line
reason, against the four admission criteria above.

## Plan for the first 50

1. Sign-off on this doc (categories, admission test, sources).
2. Pilot: **2 items per category (10)**, full review, to calibrate the
   rubric before scaling.
3. Collect the remaining 40, review in batches of 10.
