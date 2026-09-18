# Build Plan: a Lean 4 Physics Formalization Benchmark

*Implementation spec, written to be handed to Claude Code as the top-level brief. Everything below is a requirement or a decision to be made explicitly; where a Lean or Mathlib API detail is uncertain it is marked **VERIFY** and must be checked against the pinned toolchain before being relied on.*

> **Editor's note (M0, post-implementation).** This file is the original brief; it's been lightly edited in place — renamed throughout, book and seed item swapped for the ones actually decided on, §10/§12 annotated with status — rather than kept frozen, since the maintainer asked for it to track real decisions. For day-to-day current state, prefer `README.md` and `docs/` (`SOURCE.md`, `DECISIONS.md`, `GRADING.md`, `TAXONOMY.md`, `PROMPTS.md`), which are the living docs and move faster than this file. M0 (§10) is complete as of this edit.

Name used throughout: **PhysProofBench** (renamed from this doc's original working name `PhysForm` to match the project directory — see `docs/DECISIONS.md`), consistent across the package, the CLI, and the Lean library.

---

## 1. What this benchmark is

A benchmark of physics theorems from textbooks, formalized in Lean 4, that measures two capabilities at once:

1. **Proof synthesis.** Given a gold Lean statement, produce a proof.
2. **Autoformalization.** Given only natural-language text, produce both the statement and the proof.

Each capability is tested in two information conditions: **with** the textbook's natural-language proof, and **without** it (statement only). This gives a 2 × 2 condition matrix, and every item in the benchmark can be run in all four conditions from the same stored data.

| | `no_nl_proof` | `with_nl_proof` |
|---|---|---|
| **`proof`** (gold Lean statement given) | A1: pure theorem proving | A2: proof translation |
| **`autoform`** (no Lean given) | B1: statement + proof from a claim | B2: full autoformalization of a worked proof |

The design targets three things existing physics benchmarks do not do together: both task types on the same items; per-item tagging by *proof kind* (exact / approximation / hidden assumption); and a repeatable ingestion pipeline aimed at covering a whole book.

### 1.1 Prior art to imitate and to differ from

Read these before designing anything; they encode hard-won lessons.

- **AxQM** (arXiv:2609.05157, repo `Axiomatic-AI/AxQM`) — textbook-scale proof synthesis, private solution library, grading by Lean kernel plus `sorry` and axiom audits. Copy: the census-of-one-book approach, the private solutions, the dependency ledger, the proof-length difficulty scale. Differ: AxQM is proof synthesis only, and finite-dimensional QM only.
- **Lean4PHYS / LeanPhysBench** (arXiv:2510.26094, repo `ShirleyLIYuxin/Lean4PHYS`) — unit system, textbook problems turned into proof obligations. Copy: the units/dimensions layer and the with-library vs without-library ablation. Differ: many of its statements hand the physical law to the prover as a hypothesis; we want that to be a tagged, deliberate choice rather than the default.
- **FormalPhysics / FormalScience** (arXiv:2604.23002, ACL 2026, repo `jmeadows17/formal-science`) — statement autoformalization with a semantic-drift taxonomy (notational collapse, abstraction elevation, proof strategy substitution, implicit premise selection) and four judged axes (formal validity, formal quality, logical preservation, mathematical consistency). Copy: the axes and the drift taxonomy, as the grading vocabulary for autoformalization mode.
- **"Faults in Our Formal Benchmarking"** (arXiv:2606.29493) — catalogue of defects in existing Lean benchmarks. Use as the QA checklist for our own items.
- **Physlib** (`leanprover-community/physlib`, formerly PhysLean/HepLean) — the physics library to depend on where it helps; also the source of the informal / semiformal / formal three-tier convention worth copying for items we cannot yet state.

---

## 2. Source text and the first book

**Decided (M0):** the census book is Friedli & Velenik, *Statistical Mechanics: A Mathematical Introduction* ("SM" — "Revised version, August 22 2017" draft, `book/main.pdf`), not the continuum-mechanics text this section originally proposed. The book actually present in the repository is SM; the maintainer confirmed it as the target rather than switching to a continuum-mechanics text to match this section's original example. Full citation, edition caveats, and the coverage ledger live in `docs/SOURCE.md`; the reasoning and the resulting seed-item swap (§9) are recorded in `docs/DECISIONS.md`.

*(Original text, for context: "The seed item (§9) is Theorem 2.2.1, characterization of rigid motions, from a continuum mechanics textbook... Continuum mechanics is a good choice — it is mathematically precise, mostly finite-dimensional tensor analysis, and full of category-3 modeling assumptions." SM turned out to fit the same requirements — rigorous, proof-first, self-contained early chapters — without requiring a book swap from what was already in the repo.)*

### 2.1 Copyright rules (non-negotiable)

The repository must never contain scanned pages, OCR dumps, or verbatim textbook prose beyond short attributed quotations. Concretely:

- `nl_statement` and `nl_proof` fields are **paraphrases written by the contributor**, not transcriptions. They may follow the source's logical structure and reuse its equation numbering by reference (e.g. "eqn. 2.17 of the source").
- Store a citation (`source.book`, `source.edition`, `source.chapter`, `source.item_label`, `source.pages`) so a reader can find the original.
- Quotations, if genuinely needed for a definition, stay under 15 words and are marked as quotations.
- Put this rule in `CONTRIBUTING.md` and enforce it in review; add a CI lint that flags any `nl_*` field longer than a configurable threshold (default 1,500 characters) for human attention, since over-long fields are usually transcriptions.

---

## 3. Repository layout

```
physproofbench/
├── README.md
├── CONTRIBUTING.md
├── docs/
│   ├── SOURCE.md              # which book, which edition, coverage ledger
│   ├── TAXONOMY.md            # proof_kind tags, drift categories, rubric text
│   ├── GRADING.md             # exact grading contract (see §6)
│   └── PROMPTS.md             # frozen prompt templates, versioned
├── lean/
│   ├── lakefile.toml          # or lakefile.lean; pin Mathlib + optional Physlib
│   ├── lean-toolchain         # pinned toolchain, e.g. leanprover/lean4:v4.x.y
│   ├── PhysProofBench/
│   │   ├── Core/              # shared defs used by many items
│   │   │   ├── Probability.lean  # M0: IsProbDist, shannonEntropy, uniformDist (SM ch.1)
│   │   │   ├── Units.lean     # dimensions/units layer (see §5.3) -- not yet needed, see docs/DECISIONS.md
│   │   │   ├── Kinematics.lean   # continuum-mechanics example from this doc's original draft; not built
│   │   │   └── Tensors.lean      # ditto -- neither applies to SM's early chapters
│   │   └── Items/             # PUBLIC: one file per item, statement + `sorry`
│   │       └── SM_01_009_001.lean  # M0 seed item (Friedli-Velenik Lemma 1.9)
│   └── PhysProofBenchSolutions/     # PRIVATE (separate repo, git submodule): proofs
│       └── SM_01_009_001.lean
├── items/
│   └── SM_01_009_001/
│       ├── meta.yaml          # schema in §4
│       ├── nl.md              # paraphrased statement + proof
│       └── notes.md           # formalization decisions, hypotheses added, gaps
├── src/physproofbench/              # Python package
│   ├── cli.py                 # `physproofbench` entry point
│   ├── schema.py              # pydantic models for meta.yaml + submissions
│   ├── render.py              # item + condition -> prompt
│   ├── models/                # LLM adapters (anthropic, openai, local/vllm)
│   ├── run.py                 # generation loop, caching, parallelism
│   ├── lean/
│   │   ├── sandbox.py         # compile a file, timeouts, resource limits
│   │   ├── repl.py            # optional: leanprover-community/repl driver
│   │   ├── gates.py           # L0 syntactic gates (§6.1)
│   │   ├── audit.py           # sorry / axiom / env-diff audits (§6.2)
│   │   └── bridge.py          # gold<->candidate implication checks (§6.3)
│   ├── judge/                 # LLM-judge rubric scoring (§6.4)
│   ├── report.py              # metrics, tables, plots
│   └── ingest/                # book -> items pipeline (§7)
├── runs/                      # generated: one directory per evaluation run
├── tests/                     # pytest; includes golden-file tests for graders
└── .github/workflows/ci.yml
```

Two repositories, not one: `physproofbench` (public, statements with `sorry`) and `physproofbench-solutions` (private, reference proofs), the latter included as a submodule for maintainers. CI in the public repo must pass without the submodule.

---

## 4. Item schema

`items/<id>/meta.yaml`, validated by `physproofbench.schema`. Example below is the original illustrative `CM` (continuum-mechanics) draft, kept as-is since the schema shape didn't change; for a real, implemented example see `items/SM_01_009_001/meta.yaml`. One id-convention wrinkle found in practice: `<BOOK>_<CHAPTER>_<SECTION>_<SEQ>` below assumes numbering is per-section, which holds for `CM` but not for `SM` (Friedli–Velenik numbers definitions/lemmas/theorems consecutively per *chapter*) — see `docs/SOURCE.md`'s per-book id-convention subsection for how `SM` adapts it.

```yaml
id: CM_02_002_001            # <BOOK>_<CHAPTER>_<SECTION>_<SEQ>, stable forever
schema_version: 1
status: active               # active | draft | retired | semiformal
source:
  book: CM                   # key into docs/SOURCE.md
  chapter: 2
  item_label: "Theorem 2.2.1"
  pages: [142, 144]
topic: [continuum-mechanics, kinematics, rigid-motion]

# --- what kind of physics proof this is (our distinguishing axis) ---
proof_kind: exact            # exact | approximation | hidden_assumption | mixed
approximation:               # present iff proof_kind touches `approximation`
  flavor: null               # disguised_limit | controlled | uncontrolled
  encoding: null             # model_substitution | asymptotic | error_bound | postulate
hidden_assumptions:          # assumptions the source does not state; see §5.2
  - id: convexity
    kind: domain             # regularity | domain | modeling | validity_range
    lean: "Convex ℝ V₀"
    justification: source_implied     # source_stated | source_implied | encoding_artifact | strengthening
    note: "Source footnote: the segment joining the two points stays inside the body."
  - id: c2_regularity
    kind: regularity
    lean: "∀ t, ContDiffOn ℝ 2 (χ t) V₀"
    justification: source_implied
    note: "The source's short route assumes χ twice differentiable in X."

# --- task wiring ---
lean_file: lean/PhysProofBench/Items/CM_02_002_001.lean
decl_name: rigid_motion_tfae
solution_file: lean/PhysProofBenchSolutions/CM_02_002_001.lean
imports_physlib: false
modes: [proof, autoform]       # some items may be proof-only
nl:
  statement: nl.md#statement   # anchors inside items/<id>/nl.md
  proof: nl.md#proof           # omit if the source gives no proof

# --- difficulty + bookkeeping ---
difficulty:
  decl_count: 37               # declarations the reference proof needs beyond Core
  band: large                  # very_small|small|moderate|large|very_large, from decl_count
depends_on: [CM_02_001_004]    # other item ids used by the reference proof
core_deps: [PhysProofBench.Core.Kinematics]
library_gaps: ["arc length of a curve in EuclideanSpace: partial Mathlib support"]
contributed_by: "..."
reviewed_by: ["...", "..."]    # require >= 2 distinct reviewers before `active`
```

Rules the schema must enforce:

- `id` is immutable; retiring an item sets `status: retired` and never reuses the id.
- `status: active` requires two reviewers, a compiling statement, a `sorry`-free solution, and a passing axiom audit.
- `hidden_assumptions[].justification: strengthening` blocks `active` status unless `notes.md` explains why it is unavoidable. This is the hypothesis-discipline audit, borrowed from arXiv:2606.20642, applied to our own gold statements.

---

## 5. The Lean side

### 5.1 Project and pinning

- `lean-toolchain` and `lakefile` pin exact Mathlib and (optionally) Physlib commits. Record them in `docs/SOURCE.md` and in every run's metadata; results are only comparable within a pin. **Done (M0):** `lean/lean-toolchain` = `leanprover/lean4:v4.34.0`, `lean/lakefile.toml` pins Mathlib tag `v4.34.0` (commit `5ed2965...`, full hash in `docs/SOURCE.md`); `imports_physlib: false` for the seed item.
- Provide `physproofbench lean build` to build once and cache `.olean`s; every item compile reuses that build. Cold builds of Mathlib are slow, so CI must cache `lean/.lake`. Not yet built as a CLI subcommand — for now, `lake build PhysProofBench` from `lean/` does this directly, and `lake exe cache get` fetches precompiled Mathlib oleans instead of building from source (used for M0; cut the seed item's build from hours to ~90s).
- **VERIFY** early whether depending on Physlib forces a Mathlib version conflict. Still open — not exercised in M0, since SM's early chapters don't need Physlib.

### 5.2 `PhysProofBench.Core`

A small shared library so items do not each redefine the wheel. It must stay small and reviewed; a bug here contaminates many items (AxQM's defence is exactly this reuse argument, so track it: a script should report, for each item, the fraction of its dependency closure shared with other items).

Contents to start (original draft, written against the continuum-mechanics placeholder book):

- `Core/Tensors.lean` — conventions for second-order tensors as `E3 →ₗ[ℝ] E3` or `Matrix (Fin 3) (Fin 3) ℝ`. **Pick one and document it**; mixing the two is the main source of pain. Provide the bridge lemmas. *Not built — SM doesn't need tensors this early; revisit if a later chapter does.*
- `Core/Kinematics.lean` — `IsRotation`, deformation gradient, right Cauchy–Green, Green–Lagrange strain, `IsRigidMotion`. *Not built, same reason.*
- `Core/Units.lean` — dimension-tracked quantities. Options: reuse Lean4PHYS's unit system, reuse Tao's `UnitSystem`, or write a minimal one. **VERIFY** licence compatibility (Lean4PHYS's library is Apache-2.0 but its dataset carries a restrictive licence — do not vendor the dataset). *Not built — SM's early chapters are dimensionless; see `docs/DECISIONS.md` item 3.*
- `Core/Approx.lean` — the piece no existing library has: idiomatic wrappers for stating approximations. At minimum, notation and lemmas for "f agrees with g to first order at 0" built on `Asymptotics.IsLittleO`, and a `HasErrorBound` predicate for explicit-bound statements. This is what makes `proof_kind: approximation` items expressible. *Not built — no `approximation` item exists yet.*

**Built instead (M0), for `SM`:** `Core/Probability.lean` — `IsProbDist`, `uniformDist`, `shannonEntropy` for finite probability spaces (Friedli–Velenik §1.2), plus the bridge lemma to Mathlib's `Real.negMulLog`. This is the actual first `Core` file; the four above are this section's original example for a different book and haven't been started.

### 5.3 Item file conventions

Public item file (`lean/PhysProofBench/Items/<id>.lean`) — original example below (continuum-mechanics placeholder); see `lean/PhysProofBench/Items/SM_01_009_001.lean` for the real, implemented one:

```lean
import PhysProofBench.Core.Kinematics
-- PHYSPROOFBENCH-ITEM: CM_02_002_001
-- PHYSPROOFBENCH-DECL: rigid_motion_tfae

/-- <docstring: the informal statement, paraphrased> -/
theorem rigid_motion_tfae
    (V₀ : Set E3) (hopen : IsOpen V₀) (hconv : Convex ℝ V₀) (hne : V₀.Nonempty)
    ... : List.TFAE [...] := by
  sorry
```

Requirements:

- Exactly one declaration per item file, named by `decl_name`, with `sorry` as the entire proof.
- The file must compile (with the expected `sorry` warning) in CI. A statement that does not elaborate scores every model zero and is the worst possible bug.
- The solution file in the private repo proves the same declaration with the identical signature. CI in the private repo checks signature equality against the public file (compare pretty-printed types after `set_option pp.all true`, or better, use the implication check from §6.3 in both directions).

---

## 6. Grading

`docs/GRADING.md` is the contract; the code in `src/physproofbench/lean/` implements it. Grading is layered. Layers L0–L2 are deterministic and apply to both modes; L3–L4 apply to autoformalization mode only.

**Status (M0): L0–L2 implemented (`src/physproofbench/lean/{gates,sandbox,audit}.py`) and tested end-to-end against real Lean compilation. `docs/GRADING.md` is now the authoritative, up-to-date contract — this section is kept for historical context; where the two disagree, `docs/GRADING.md` wins.**

### L0. Syntactic gates (`gates.py`)

Reject before compiling if the submission contains any of:

- `sorry`, `admit`, `stop`
- an `axiom` declaration
- `native_decide`, `implemented_by`, `unsafe`, `extern`
- `set_option maxHeartbeats 0` beyond a configured cap, or `set_option` that disables checks (**VERIFY** the current list; at minimum flag `debug.skipKernelTC`) — implemented for `debug.skipKernelTC` and a `maxHeartbeats` cap; the rest of "current list" is still open, expand if a submission is found gaming something not on this list.
- in `proof` mode: any edit to the statement region, detected by diffing the submission against the item file up to the `:= by` marker, *and* independently by the L2 implication check (belt and braces — text diffs are easy to defeat).

Each gate failure is recorded with its reason; gates are reported separately from compile failures so you can distinguish cheating from incapacity.

### L1. Kernel check (`sandbox.py`)

Compile the submission against the pinned build, in a sandbox with:

- wall-clock timeout (default 300 s, per-item overridable in `meta.yaml`)
- memory cap — **VERIFY note:** `RLIMIT_AS` reliably fails to set on macOS (`setrlimit` raises "current limit exceeds maximum limit" even though `getrlimit` reports both limits as unlimited — a longstanding Darwin quirk). Enforced on Linux only for now; rely on the timeout on macOS. Should work as intended in Linux CI — re-verify there.
- **no network access** (models occasionally emit `import`s of nonexistent packages or shell-outs) — implemented via `sandbox-exec` on macOS only; **still a real gap on Linux**, where CI should use a container or `firejail`/`bwrap` instead (not yet built).

Record: exit status, stderr, elapsed time, and the full diagnostic list. Uses plain `lake env lean <file>` with text-output parsing rather than `--json` (not evaluated either way yet — text parsing was sufficient for M0's needs); the `repl.py` per-tactic driver isn't built.

### L2. Audits (`audit.py`)

For the submitted declaration `D`:

1. **`sorry` closure.** `D` and everything it depends on must be `sorry`-free. Implement via `#print axioms D` and check that `sorryAx` does not appear (**VERIFY** the exact axiom name on the pinned version) — **confirmed**: on Lean `v4.34.0`, `sorryAx` is indeed the name, and the printed message format is `'<decl>' depends on axioms: [propext, Classical.choice, Quot.sound]` (or `'<decl>' does not depend on any axioms`) — verified live against the seed item's real solution, not just assumed. See `items/SM_01_009_001/notes.md`.
2. **Axiom audit.** The axiom set must be a subset of `{propext, Classical.choice, Quot.sound}`. Anything else fails.
3. ~~**Environment diff.**~~ **Resolved, per this section's own suggestion:** checking `#print axioms` on the top-level declaration alone is sufficient and transitively covers dependencies — confirmed against the seed item's real (non-trivial) proof, which pulls in several `have`s and Mathlib lemmas and still reports exactly the standard three axioms at the top level. No separate environment-walk audit was built; audits 1 and 2 above are implemented as one `audit_axioms` function.
4. **Statement preservation (proof mode).** Generate a checker file. **One real bug found and fixed here:** Lean 4 does **not** auto-namespace a declaration by its file/module path — a top-level `theorem foo` in `Submission.lean` is accessible after `import Submission` as bare `foo`, not `Submission.foo`, so the naive version of this checker (below, as originally drafted) does not typecheck. Fixed by having the harness wrap the submission's source in `namespace Submission ... end Submission` (`audit.namespace_wrap`) before building it — a build-time transformation, never something the model writes itself — and by dropping the gold import entirely (only the gold's *type* is needed, spliced as text; importing it too would put a second identically-named top-level declaration in scope). See `docs/GRADING.md`'s L2.3 section and `tests/test_statement_preservation.py` for the corrected, compile-tested version. Original (buggy) sketch, kept for the historical record of what was wrong with it:

   ```lean
   import PhysProofBench.Items.CM_02_002_001   -- gold statement, `sorry`-free not required
   import Submission
   example : <gold type, spliced textually from the item file> := Submission.rigid_motion_tfae
   ```

   If this typechecks, the submission proves at least the gold statement. This defeats statement tampering regardless of textual tricks.

A run passes L2 iff all applicable audits pass. **Headline metric for `proof` mode = fraction of items passing L0+L1+L2, at pass@k.**

Note: L2.3 (statement preservation) is implemented and independently tested (`tests/test_statement_preservation.py`), but as of M0 it is not yet wired into the automatic `grade_submission` orchestration in `grading.py` — it needs the ingestion/run machinery (M1) to manage placing gold and submission as properly-named Lean modules. Call `audit.build_statement_preservation_source` / `audit.namespace_wrap` directly until then.

### L3. Statement equivalence (autoformalization mode) (`bridge.py`)

The model wrote its own statement `S_cand`; the gold is `S_gold`. Attempt, in both directions, to discharge

```lean
example : S_gold := by <tactics>   -- using the candidate declaration
example : S_cand := by <tactics>   -- using the gold declaration
```

Escalating strategies, stopping at the first success:

1. `exact <decl>` (statements are literally the same up to defeq)
2. `exact?`, `aesop`, `tauto`, `simp_all` with a short timeout
3. an optional **prover-assisted bridge**: hand both statements to a configured prover model with a bounded budget, in a separate, clearly-labelled configuration (this is model-assisted grading and must be reported as such)

Outcomes: `equivalent` (both directions), `stronger`, `weaker`, `incomparable`, `unknown`. Only `equivalent` counts toward the strict metric; the others are reported separately, because "weaker" is exactly where abstraction elevation hides.

### L3b. Vacuity probes

Independent of the gold comparison, run cheap trivia detectors on `S_cand`:

- **Dumb-tactic probe.** Can `simp`, `aesop`, `norm_num`, or `rfl` alone close the statement? If yes, flag `suspected_trivial`.
- **Hypothesis-inconsistency probe.** Try to derive `False` from the hypotheses alone with a bounded automation budget. A success is a hard fail.
- **Witness probe (per item, authored once).** Each item ships a concrete instance in the *gold* vocabulary — for the rigid-motion item, rotation about the z-axis by `ωt` on the open unit ball. If the candidate statement is judged equivalent at L3, the same witness must instantiate it. If the candidate is incomparable, record that the witness could not be transported, and send to L4.

These probes are heuristics. Report them as flags, never as silent score adjustments.

### L4. Faithfulness judging (`judge/`)

For autoformalization submissions that compile, score four axes, following FormalPhysics:

- **FV** formal validity — from L1/L2, deterministic.
- **FQ** formal quality — is the code well-structured and reusable?
- **LP** logical preservation — does it capture the logical structure of the informal claim?
- **MC** mathematical consistency — are the objects and operations the right ones?

Plus our drift labels, multi-select: `notational_collapse`, `abstraction_elevation`, `proof_strategy_substitution`, `implicit_premise_selection`, `quantifier_error`, `missing_hypothesis`, `extra_hypothesis`.

Requirements on the judging code:

- Two independent judges from different model families; report inter-judge agreement (Cohen's κ or the φ coefficient) in every run. FormalScience found some conclusions to be judge-dependent; if agreement is low, the number is not reportable.
- Judges see: the paraphrased NL statement, the candidate Lean, the gold Lean, and the L3 verdict. Prompts frozen in `docs/PROMPTS.md` and versioned; changing a judge prompt bumps `grading_version` and invalidates cross-run comparisons.
- A human adjudication queue: `physproofbench judge review --run <id> --disagreements` opens the cases where judges disagree, writes decisions to `runs/<id>/adjudication.jsonl`, and those decisions become regression fixtures in `tests/`.

### Reported metrics

Per run, per condition (A1/A2/B1/B2), overall and sliced by `proof_kind`, `difficulty.band`, chapter, and `imports_physlib`:

- pass@1 and pass@k (report k and sampling temperature)
- gate-failure rate, compile rate, audit-failure rate, broken out
- autoformalization only: L3 verdict distribution, FV/FQ/LP/MC, drift-label frequencies
- cost: tokens and wall-clock per item

Two ablations worth building in from the start, since both are known to move results: **library-in-context on/off** (put `PhysProofBench.Core` source in the prompt or not), and **NL proof on/off** (the condition axis itself).

---

## 7. Ingestion pipeline: from a book to items

The goal is a census of one book, so the pipeline must be cheap per item and resumable. Target throughput: one contributor should be able to take a chapter from PDF to reviewed items in days, not weeks.

### Stages

**S1. Item extraction.** `physproofbench ingest extract --book SM --chapter 1` produces a `ledger.csv` of every numbered item in the chapter (theorem, lemma, example, exercise) with label, pages, and a one-line paraphrased description. Human-in-the-loop: the extraction may be LLM-assisted from the PDF, but a human confirms the ledger. The ledger is the coverage denominator — it must include items we will *not* formalize.

**S2. Triage.** Each ledger row gets `triage ∈ {formalizable, out_of_scope, blocked}` with a reason. `out_of_scope` covers essay prompts, plotting, numerical computation, and anything requiring machinery we have ruled out. `blocked` records a specific library gap and feeds `docs/GAPS.md`. Report coverage as *formalized / formalizable / total*, and never hide the denominator.

**S3. Paraphrase.** Write `nl.md` with `## statement` and `## proof` anchors, in the contributor's own words (§2.1).

**S4. Statement drafting.** LLM-assisted drafting is fine, but the draft must be accompanied by the `hidden_assumptions` list and every added hypothesis classified. Provide `physproofbench ingest draft <id>` to scaffold the files and open the right editor buffers.

**S5. Proof.** Write the reference proof in the private repo. Agent assistance is expected; guard against hypothesis creep by re-running the L2 statement-preservation check after every session, so the statement cannot drift to meet the proof.

**S6. Review.** Two reviewers, using the checklist in `docs/REVIEW.md`:

- Quantifier order, especially `∃` outside `∀` where the physics demands it.
- Are all three of: hypotheses necessary, hypotheses jointly satisfiable (witness), conclusion not assumed?
- Is the conclusion a definitional unfolding? (the `distanceTraveled = ½at²` failure mode)
- Do units/dimensions typecheck where the Core layer applies?
- Is `proof_kind` right, and for approximations, is the chosen `encoding` the honest one?

**S7. Promote.** `physproofbench ingest promote <id>` runs all CI checks and flips `status: active`.

### Tooling requirements

- Every stage is resumable and idempotent; state lives in the files, not in the tool.
- `physproofbench ingest status --book SM` prints the coverage table by chapter.
- `physproofbench item new` scaffolds from a template so schema drift is impossible.
- Contamination control: reference proofs live only in the private repo, and the public repo publishes statements, difficulty bands, and the dependency ledger — mirroring AxQM's arrangement. Add a CI job in the private repo that fails if a solution file is ever added to the public tree.

---

## 8. Runner and reproducibility

- `physproofbench run --items all --mode proof --condition no_nl_proof --model <name> -k 8` writes `runs/<timestamp>-<slug>/` containing: resolved config, prompt hashes, raw completions, extracted Lean, per-item grading JSON, and a summary table.
- Prompts are rendered from frozen templates in `docs/PROMPTS.md`; the template hash goes into run metadata. **Prompts are part of the benchmark**: changing them changes the numbers.
- Extraction of Lean from a completion is its own failure mode. Specify one rule (last fenced ```lean block; if absent, the whole completion) and log when the fallback fires.
- Cache by `(item, condition, model, template_hash, sample_index)` so reruns are cheap.
- Parallelism over items with a configurable Lean-compile worker pool; Lean builds are memory-hungry, so default to `min(4, cpu_count // 2)`.
- Results schema is stable and versioned (`grading_version`, `pin_hash`); `physproofbench report` regenerates tables from stored JSON without re-running models.

---

## 9. Seed item (build this first, end to end)

**Built (M0): `SM_01_009_001`**, not `CM_02_002_001` below — that item is from the continuum-mechanics placeholder book and was never started; per §2/`docs/DECISIONS.md` the census book is `SM` (Friedli–Velenik), so the seed item was picked from its ch. 1 instead.

- **Item:** Lemma 1.9 (p. 21) — the uniform distribution on a finite, nonempty set of microstates `Ω` is the *unique* probability distribution maximizing Shannon entropy `S(μ) = -Σ_ω μ(ω) log μ(ω)`, with maximal value `log|Ω|`.
- **NL statement / proof (paraphrased):** `items/SM_01_009_001/nl.md`.
- **Tags:** `proof_kind: exact` — no hidden assumptions; the source's own hypotheses (`Ω` finite, `μ` a distribution) are exactly what got formalized.
- **Gold statement:** `lean/PhysProofBench/Items/SM_01_009_001.lean`, declaration `shannonEntropy_le_log_card`. Not split into sub-items — unlike the rigid-motion TFAE below, this is a single inequality-plus-iff, not a multi-step equivalence chain, so splitting wasn't warranted.
- **Reference proof:** `lean/PhysProofBenchSolutions/SM_01_009_001.lean` (private repo), `sorry`-free, axioms `{propext, Classical.choice, Quot.sound}`. Uses `Mathlib.Analysis.Convex.Jensen`'s `StrictConcaveOn.map_sum_eq_iff_of_nonneg` (equality case of Jensen's inequality) applied to Mathlib's own `Real.negMulLog`, which is already proven strictly concave on `[0,∞)` — no concavity proof was written from scratch. Full derivation and the design decisions behind it: `items/SM_01_009_001/notes.md`.
- **Witness:** not needed — no hidden assumptions to make jointly satisfiable, and existence of the maximizer (the uniform distribution itself) is immediate for any finite nonempty `Ω`.
- Did **not** need `Core/Tensors.lean`, `Core/Kinematics.lean`, `Core/Units.lean`, or `Core/Approx.lean` (§5.2) — built `Core/Probability.lean` instead. Did not need Physlib.

*(Original text below, kept for context on the continuum-mechanics book this section was originally written against — not built, and not planned unless `CM` becomes a later `source.book`.)*

`CM_02_002_001` — characterization of rigid motions. Use it to exercise every part of the system before scaling.

- **NL statement** (paraphrased): for a body with nonempty open convex reference configuration `V₀` and a motion `χ` twice continuously differentiable in `X` and orientation-preserving, the following are equivalent: (i) distances between material points are preserved at all times; (ii) `χ(X,t) = Q(t)X + c(t)` with `Q(t)` a rotation; (iii) the Green–Lagrange strain vanishes, i.e. `C = I`.
- **NL proof** (paraphrased): the source's cycle (i) ⟹ (ii) ⟹ (iii) ⟹ (i) — differentiate the distance identity twice to get `F(X₂,t)ᵀF(X₁,t) = I`, set `X₂ = X₁` to get orthogonality, conclude `F` depends on `t` alone, use `det F > 0` to get a rotation, integrate; then `C = QᵀQ = I`; then the arc-length argument with two opposing inequalities. Include the source's shorter (iii) ⟹ (ii) route via the indicial identity and index permutation, noting it assumes twice-differentiability.
- **Tags**: `proof_kind: hidden_assumption` (convexity and the `C²` regularity are both unstated in the source).
- **Draft gold statement**: as sketched in `items/CM_02_002_001/notes.md`; it uses `List.TFAE`, quantifies `Q` and `c` outside `∀ X`, and requires `det = 1` rather than mere orthogonality. **This draft is unverified — typecheck it first and expect to fix the inner-product notation, the `ContinuousLinearMap` → `LinearMap` coercion inside `LinearMap.det`, and the `ContDiffOn` argument order.**
- **Witness**: rotation by `ωt` about the z-axis plus a translation, on the open unit ball.
- **Split the item.** As a single TFAE it is likely all-or-nothing. Ship it as five items sharing `Core`: `(ii)⟹(i)`, `(ii)⟹(iii)`, `(iii)⟹(i)`, `(i)⟹(ii)`, and the full TFAE, with `depends_on` wired up. This is also the first real test of the dependency ledger.

Expect `(iii) ⟹ (i)` to be the hard one: the source's arc-length argument needs curve length in `EuclideanSpace`, where Mathlib support is partial (**VERIFY** `eVariationOn` and the path-length API). If it proves impractical, record it in `docs/GAPS.md`, mark that sub-item `status: semiformal` (statement fixed, proof open, following Physlib's convention), and keep it out of the scored set until it closes.

---

## 10. Milestones and acceptance criteria

**M0 — skeleton (target: 1 item). ✅ Done.**
Lean project builds against pinned Mathlib; `CM_02_002_001` sub-items compile with `sorry`; at least one has a `sorry`-free reference proof in the private repo; `physproofbench` CLI installs; `physproofbench grade` runs L0–L2 on a hand-written correct submission and on three hand-written cheating submissions (a `sorry`, a `native_decide`, a tampered statement) and classifies all four correctly.
*Acceptance: `pytest` green; those four fixtures live in `tests/fixtures/` forever.*
*(Actual: seed item is `SM_01_009_001`, not `CM_02_002_001` — see §9. All other acceptance criteria met as literally written: 32 tests green, including the four required fixtures in `tests/fixtures/`.)*

**M1 — both modes, one model.**
Prompt templates frozen; all four conditions runnable; L3 bridge checks and L3b vacuity probes implemented; one real model evaluated on the seed items; a `runs/` directory with a readable summary table.
*Acceptance: `physproofbench report` reproduces the table from stored JSON with models disabled.*

**M2 — grading hardened.**
Two judges wired up with agreement statistics; adjudication queue; `docs/GRADING.md` matches the code; regression fixtures from adjudicated disagreements.
*Acceptance: κ reported; a deliberately drifted submission (physics moved into hypotheses) is caught by at least one of L3/L3b/L4 and labelled `abstraction_elevation`.*

**M3 — one chapter, censused.**
Ingestion pipeline S1–S7 exercised on a full chapter; coverage table published; ≥ 25 active items; ≥ 3 items tagged `approximation` with distinct `encoding` values, to prove `Core/Approx.lean` is usable.
*Acceptance: a second contributor takes an item from S1 to `active` using only the docs.*

**M4 — book-scale and release.**
Remaining chapters ingested; baselines for several models across all four conditions; contamination controls verified; README with the coverage table, the metric definitions, and a submission protocol; licence chosen (code Apache-2.0; item data CC BY-NC, mirroring comparable releases — **confirm with the maintainer**).

---

## 11. Risks, and what to do about them

| Risk | Mitigation |
|---|---|
| A gold statement is subtly wrong, so everyone scores 0 (or 100) | Two reviewers; witness probe; reuse metric; publish a defect-report channel and a fix cadence |
| Mathlib churn breaks statements | Hard pin; scheduled bump PRs where CI re-verifies every solution; `pin_hash` in every result |
| Solutions leak into training data | Private solutions repo; publish only statements; watch for suspiciously identical proofs across models |
| Judge noise dominates the autoformalization numbers | Two judges + κ; deterministic L3 as the headline; judges as secondary |
| Physics content collapses into trivial math (notational collapse) | Drift labels; witness probes; `Core` types that make the collapse a type error where possible |
| Ingestion stalls at S5 because proofs are hard | `semiformal` status keeps statements useful; `docs/GAPS.md` turns blockers into library contributions |
| Scope creep into "all of physics" | The census is one book; other books are separate `source.book` keys and separate milestones |

---

## 12. Open questions for the maintainer

Answer these before M2; record answers in `docs/DECISIONS.md`. Status as of M0:

1. ~~Which book is the census target, and which edition?~~ **Answered:** `SM` — Friedli & Velenik, *Statistical Mechanics: A Mathematical Introduction*, "Revised version, August 22 2017" draft. `docs/SOURCE.md#sm`, `docs/DECISIONS.md` item 1. (ISBN still unconfirmed — flagged there, not blocking.)
2. ~~Tensors as `Matrix (Fin 3) (Fin 3) ℝ` or as linear maps on `EuclideanSpace ℝ (Fin 3)`?~~ **Moot for now:** `SM` doesn't need tensors this early. `docs/DECISIONS.md` item 2 — revisit if a later chapter needs them.
3. Do items carry units/dimensions by default, or only where the physics turns on them? **Still open** — `docs/DECISIONS.md` item 3. `SM`'s early chapters are dimensionless, so this hasn't been forced yet.
4. Is prover-assisted bridging (L3 step 3) allowed in the headline configuration, or reported only as a secondary number? **Still open** — L3 (`bridge.py`) isn't built yet (M1).
5. For `proof_kind: approximation` items, is the gold encoding fixed per item, or may a submission choose any of the four encodings and be judged on the choice? **Still open** — no `approximation` item exists yet.
6. Public licence for the item data, and the policy on accepting community items from other books. **Still open**, deferred to M4 per §10.