# PhysProofBench

A benchmark of physics theorems, formalized in Lean 4, that measures two
capabilities at once:

1. **Proof synthesis** — given a gold Lean statement, produce a proof.
2. **Autoformalization** — given only natural-language text, produce both
   the statement and the proof.

Each is tested with and without the textbook's own natural-language proof,
giving a 2×2 condition matrix (see `plan.md` §1) runnable from the same
stored item data.

The census book is Friedli & Velenik's *Statistical Mechanics: A
Mathematical Introduction* — see `docs/SOURCE.md`.

Full design spec: `plan.md`. Living docs as the project develops:
`docs/SOURCE.md` (which book, coverage ledger), `docs/TAXONOMY.md`
(`proof_kind`, drift labels, difficulty bands), `docs/GRADING.md` (the exact
grading contract), `docs/PROMPTS.md` (frozen, versioned prompt templates),
`docs/DECISIONS.md` (answers to the plan's open questions).

## Repository layout

- `lean/PhysProofBench/` — public Lean library: `Core/` (shared defs) and
  `Items/` (one file per item, statement + `sorry`).
- `items/<id>/` — `meta.yaml` (schema, see `plan.md` §4), `nl.md`
  (paraphrased statement + proof), `notes.md` (formalization decisions).
- `src/physproofbench/` — the Python package and `physproofbench` CLI:
  ingestion, running models, grading, reporting.
- `runs/` — one directory per evaluation run (generated, not committed
  beyond `.gitkeep`-style placeholders).
- `tests/` — pytest, including golden-file grader fixtures in
  `tests/fixtures/` that must classify correctly forever (see `plan.md`
  M0 acceptance criteria).

Reference proofs live in a **separate, private repository**,
`physproofbench-solutions` (locally: `../physproofbench-solutions`), included
here as a git submodule for maintainers. This public repo's CI must pass
without that submodule checked out.

## Status

M0 (`plan.md` §10) complete: Lean project builds against pinned Mathlib
(`v4.34.0`); the seed item `SM_01_009_001` (Friedli–Velenik Lemma 1.9 —
uniform distribution maximizes Shannon entropy) compiles publicly with
`sorry` and has a `sorry`-free reference proof in the private repo, axioms
`{propext, Classical.choice, Quot.sound}`; the `physproofbench` CLI installs
and `physproofbench grade` runs L0–L2 against a hand-written correct
submission and three cheating submissions (`sorry`, `native_decide`, a
tampered statement), classifying all four correctly; `pytest` is green (32
tests, including real Lean compilation, not mocks).

Not yet built: M1's ingestion/run/report/judge/model-adapter machinery
(`src/physproofbench/{ingest,judge,models}/` are empty directories reserving
the layout from `plan.md` §3; `run.py` and `report.py` don't exist yet).
L2.3 statement-preservation checking is implemented (`lean/audit.py`) and
tested end-to-end, but not yet wired automatically into `grading.py` (see
its docstring). No chapter has been censused. See `plan.md` for the full
milestone list and `docs/DECISIONS.md` for choices made so far.

## License

Not yet chosen — see `docs/DECISIONS.md` item 6 (deferred to M4).
