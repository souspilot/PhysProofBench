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

Item set: **12 items** from chapters 1–3 (`items/`), 4 each of
`proof_kind` `exact`, `approximation` and `hidden_assumption`, all `status:
draft`. All 12 gold statements compile (`lake build PhysProofBench`), but
only the seed `SM_01_009_001` has a reference proof so far; the other 11 are
statement-only. See `docs/DECISIONS.md` ("First item batch") and
`docs/SOURCE.md`'s coverage table.

Not yet built: M1's ingestion/report/judge machinery
(`src/physproofbench/{ingest,judge}/` are empty directories reserving the
layout from `plan.md` §3; `report.py` doesn't exist; only A1/A2 proof-mode
prompts are implemented, not B1/B2 autoform). L2.3 statement-preservation
checking is implemented (`lean/audit.py`) and tested end-to-end, but not yet
wired automatically into `grading.py` (see its docstring). No chapter has
been censused. See `plan.md` for the full milestone list and
`docs/DECISIONS.md` for choices made so far.

## Running a batch (pilot study)

A batch run has two phases, run as separate commands so GPU time is never
spent waiting on Lean:

- **`physproofbench generate`** (GPU side) sends every item × condition ×
  sample to an OpenAI-compatible server (e.g. vLLM). It needs no Lean.
- **`physproofbench grade-run`** (CPU side) grades the stored completions
  with Lean. It never calls a model.

They communicate only through the run directory (layout in
`src/physproofbench/batch.py`). They can run on different nodes sharing a
filesystem, one after the other, or at the same time: `grade-run --follow`
grades samples as they land and stops once generation finishes. Both phases
save each sample as it completes and skip finished work, so re-running the
**same command** resumes after a crash, Ctrl-C or a dead server. `generate`
refuses to mix in samples made with different settings, and `grade-run`
refuses to grade an item whose gold statement differs in its checkout from
the one the model was shown.

GPU side (Python ≥ 3.11, no Lean needed):

```bash
pip install -e .
export OPENAI_BASE_URL=http://localhost:8000/v1   # no API key needed for local vLLM
physproofbench preflight --model <served-model-name>   # server, model name, context budget
physproofbench generate --model <served-model-name> --run-dir runs/pilot -k 4
```

CPU side (same commit of this repo, Lean installed):

```bash
pip install -e .
cd lean && lake exe cache get && lake build Mathlib PhysProofBench && cd ..
physproofbench lean-check                              # env + one real compile, timed
physproofbench grade-run --run-dir runs/pilot --follow # or without --follow, after generate
physproofbench report --run-dir runs/pilot             # rebuild summary.md any time
```

Generation defaults: Qwen3-style thinking sampling (`--temperature 0.6
--top-p 0.95 --top-k 20`), `--max-tokens 32768`, 16 concurrent requests, and
the item's `PhysProofBench.Core` source in the prompt (`--core-in-context`).
`generate` re-checks the server and context budget before sending anything,
and `--dry-run` writes the prompts without sending anything. Grading
defaults: 2 parallel Lean compiles (`--grade-workers`), `--compile-timeout
300`. `grade-run --regrade-timeouts` re-grades timed-out compiles after
raising the timeout. `<run-dir>/summary.md` reports pass@1/pass@k per item
and condition, verdict breakdowns, truncations, and how many gate rejections
were otherwise-correct proofs (`docs/GRADING.md`, statement-edit diagnostic).

## License

Not yet chosen — see `docs/DECISIONS.md` item 6 (deferred to M4).
