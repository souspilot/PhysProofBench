# Grading contract

This is the authoritative spec for how a submission is scored. The code in
`src/physproofbench/lean/` implements it; if code and doc disagree, this doc
wins and the code has a bug. Bumping `grading_version` (in `runs/<id>/`
metadata) is required whenever this contract changes in a way that could move
scores.

Grading is layered. L0–L2 are deterministic and apply to both `proof` and
`autoform` modes. L3–L4 apply to `autoform` mode only.

## L0. Syntactic gates (`gates.py`)

Reject the submission before compiling if it contains, as raw text:

- `sorry`, `admit`, `stop`
- an `axiom` declaration
- `native_decide`, `implemented_by`, `unsafe`, `extern`
- `set_option maxHeartbeats` set above a configured cap (default: no cap
  beyond what the item's own `meta.yaml` allows), or any `set_option` that
  disables a check — at minimum `debug.skipKernelTC`
- (`proof` mode only) any edit to the statement region: the submission is
  diffed against the item file up to its `:= by` marker. The diff ignores
  comments (including docstrings) and whitespace, but nothing else: an added
  `import`, `open`, or `def` before the theorem still counts as an edit, since
  it could change what the statement means. (Models routinely drop or
  rewrite the item's tag comments and docstring; a comment-sensitive diff
  rejected otherwise-valid answers. Found on a real Qwen3 run.) This is a *belt*
  check; the *braces* check is the independent L2.4 implication check below —
  text diffs alone are easy to defeat.

Each gate failure is recorded with a machine-readable reason
(`gate: sorry_present`, `gate: axiom_declared`, `gate: forbidden_tactic:
native_decide`, `gate: statement_edited`, ...). Gate failures are reported
separately from compile failures, because they distinguish cheating /
malformed submissions from ordinary incapacity to prove the theorem.

## L1. Kernel check (`sandbox.py`)

Compile the submission against the pinned Mathlib build (currently `v4.34.0`,
see `docs/SOURCE.md` / `lean/lakefile.toml`), in a sandbox with:

- a wall-clock timeout (default 300s, overridable per item in `meta.yaml`)
- a memory cap
- no network access (models occasionally emit `import`s of nonexistent
  packages, or attempt to shell out)

Record: exit status, stderr, elapsed time, and the full diagnostic list.

Implementation note: the submission is compiled with the raw `lean` binary,
not `lake env lean <file>`. The Lake environment (`LEAN_PATH` and friends) is
resolved once per workspace via a bare `lake env` (`sandbox.resolve_lake_env`)
and cached; each individual compile then invokes `lean` directly with that
environment. This isn't just an optimization — `lake env lean <file>`
re-runs Lake's own dependency-freshness check on every call, and when that
check's network access fails (as it does under this sandbox's
`no_network=True`), Lake responds by deleting and attempting to re-clone the
entire Mathlib checkout rather than failing gracefully. Found by testing the
grading pipeline against a real model endpoint, not merely unit-tested.

## L2. Audits (`audit.py`)

For the submitted declaration `D`:

1. **`sorry` closure.** `D` must be `sorry`-free, transitively. Checked via
   `#print axioms D` and confirming `sorryAx` does not appear in the
   printed axiom list.
2. **Axiom audit.** The printed axiom set must be a subset of
   `{propext, Classical.choice, Quot.sound}` (Lean 4 / Mathlib's standard
   three). Anything else fails. `#print axioms D` is transitive over `D`'s
   dependencies, so checking the top-level declaration is sufficient — no
   separate environment walk is needed.
3. **Statement preservation (`proof` mode only).** Generate a checker file
   that imports the submission and states the gold's type as text (not via
   import — see below):

   ```lean
   import Submission

   example <gold's binder groups, copied verbatim> : <gold's result type,
     copied verbatim> := Submission.<decl_name> <gold's explicit binder names>
   ```

   If this typechecks, the submission proves at least the gold statement,
   regardless of any textual tampering the submission attempted.

   Two non-obvious implementation details (`lean/audit.py`), both **VERIFY**-
   confirmed against the pinned toolchain by `tests/test_statement_preservation.py`:

   - Lean 4 does **not** auto-namespace a declaration by its file/module
     path — a top-level `theorem foo` in `Submission.lean` is accessible
     after `import Submission` as bare `foo`, not `Submission.foo`. Item
     files and submissions are top-level, unnamespaced (plan.md §5.3), so
     the harness wraps the submission's source in `namespace Submission ...
     end Submission` (`audit.namespace_wrap`) before building it, purely as
     a build-time transformation — the model never writes this wrapping
     itself.
   - The gold file is **not** imported into the checker at all: only its
     *type* is needed (spliced as text via `audit.parse_theorem_signature`),
     and importing it would put a second top-level declaration of the same
     `decl_name` in scope, which is at best redundant and at worst
     ambiguous.

A run passes L2 iff all applicable audits pass.

**Headline metric for `proof` mode = fraction of items passing L0+L1+L2, at
pass@k.**

## L3. Statement equivalence (`autoform` mode) (`bridge.py`)

The model wrote its own statement `S_cand`; the gold is `S_gold`. Attempt, in
both directions:

```lean
example : S_gold := by <tactics>   -- using the candidate declaration
example : S_cand := by <tactics>   -- using the gold declaration
```

Escalating strategies, stopping at the first success: (1) `exact <decl>`,
(2) `exact?` / `aesop` / `tauto` / `simp_all` with a short timeout,
(3) an optional prover-assisted bridge (a separate, clearly-labelled
model-assisted configuration — see `docs/DECISIONS.md` item 4, still open).

Outcomes: `equivalent` (both directions succeed), `stronger`, `weaker`,
`incomparable`, `unknown`. Only `equivalent` counts toward the strict metric.

## L3b. Vacuity probes

Independent of the gold comparison:

- **Dumb-tactic probe.** Can `simp`, `aesop`, `norm_num`, or `rfl` alone
  close `S_cand`? Flag `suspected_trivial` if so.
- **Hypothesis-inconsistency probe.** Try to derive `False` from `S_cand`'s
  hypotheses alone, bounded automation budget. Success is a hard fail.
- **Witness probe.** Each item ships a concrete instance in the gold
  vocabulary (see `items/<id>/notes.md`). If `S_cand` is `equivalent` at L3,
  the same witness must instantiate it.

Report these as flags, never as silent score adjustments.

## L4. Faithfulness judging (`judge/`)

For `autoform` submissions that compile, two independent judges (different
model families) score four axes, following the FormalScience taxonomy:

- **FV** formal validity — deterministic, from L1/L2.
- **FQ** formal quality — well-structured, idiomatic, reusable code?
- **LP** logical preservation — does it capture the informal claim's logical
  structure?
- **MC** mathematical consistency — right objects and operations?

Plus multi-select drift labels: `notational_collapse`, `abstraction_elevation`,
`proof_strategy_substitution`, `implicit_premise_selection`,
`quantifier_error`, `missing_hypothesis`, `extra_hypothesis`.

Report inter-judge agreement (Cohen's κ) every run; if agreement is low, the
FQ/LP/MC numbers for that run are not reportable on their own. Judge prompts
are frozen in `docs/PROMPTS.md`; changing one bumps `grading_version`.

## Reported metrics

Per run, per condition (A1/A2/B1/B2 — see `plan.md` §1), overall and sliced
by `proof_kind`, `difficulty.band`, chapter, and `imports_physlib`:

- pass@1 and pass@k (report k and sampling temperature)
- gate-failure rate, compile rate, audit-failure rate, broken out
- (`autoform` only) L3 verdict distribution, FV/FQ/LP/MC, drift-label
  frequencies
- cost: tokens and wall-clock per item

Two ablations built in from the start: library-in-context on/off (put
`PhysProofBench.Core` source in the prompt or not), and NL-proof on/off (the
condition axis itself).
