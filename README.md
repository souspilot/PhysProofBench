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
tampered statement), classifying all four correctly; `pytest` is green (40
tests as of the latest change below, including real Lean compilation, not
mocks).

Since then, a minimal single-item M1 slice: `physproofbench run --item <id>
--model <name> [--condition no_nl_proof|with_nl_proof]` renders the A1/A2
prompt (`render.py`), calls an OpenAI-compatible endpoint (`models/
openai_client.py` — reads `OPENAI_API_KEY`/`OPENAI_BASE_URL`, so it works
against a local vLLM server), extracts the last fenced ` ```lean ` block
(`extract.py`), and grades it (L0–L2), writing prompt/completion/candidate/
grade JSON under `runs/`. Not the full `plan.md` §8 runner — one item, one
sample, no pass@k, no caching/parallelism, no multi-item summary table.

While building and testing `run` end to end (not just unit tests) against a
real local server, found and fixed a real bug in `lean/sandbox.py`:
`lake env lean <file>` re-runs Lake's own dependency-freshness check on
every invocation, and when that check's network access fails (as it always
does under this module's `no_network=True` macOS sandboxing), Lake doesn't
fail gracefully — it deletes and tries to re-clone the entire Mathlib
checkout. Fixed by resolving the Lake environment once (`resolve_lake_env`)
and invoking the raw `lean` binary directly for every compile after that,
which needs no network at all. Also closed `subprocess.run`'s `stdin`
(`DEVNULL`) — left open, it caused `lake env lean` to hang when invoked from
Python (as opposed to an interactive shell) at all, sandboxed or not.

Not yet built: M1's ingestion/report/judge machinery
(`src/physproofbench/{ingest,judge}/` are empty directories reserving the
layout from `plan.md` §3; `report.py` doesn't exist; only A1/A2 proof-mode
prompts are implemented, not B1/B2 autoform). L2.3 statement-preservation
checking is implemented (`lean/audit.py`) and tested end-to-end, but not yet
wired automatically into `grading.py` (see its docstring). No chapter has
been censused. See `plan.md` for the full milestone list and
`docs/DECISIONS.md` for choices made so far.

## License

Not yet chosen — see `docs/DECISIONS.md` item 6 (deferred to M4).
