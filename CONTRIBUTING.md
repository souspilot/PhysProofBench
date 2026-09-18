# Contributing

## Copyright rules (non-negotiable)

This repository must never contain scanned pages, OCR dumps, or verbatim
textbook prose beyond short attributed quotations.

- `nl_statement` and `nl_proof` fields (the `## statement` / `## proof`
  sections of `items/<id>/nl.md`) are **paraphrases written by the
  contributor**, not transcriptions. They may follow the source's logical
  structure and reuse its equation numbering by reference (e.g. "eqn. 1.28 of
  the source"), but the wording must be your own.
- Every item cites its source via `source.book` (a key into
  `docs/SOURCE.md`), `source.chapter`, `source.item_label`, and
  `source.pages`, so a reader can find the original.
- Quotations, if genuinely needed for a definition, stay under 15 words and
  are marked as quotations (wrap them in `> "..."` in `nl.md`).
- CI lints any `nl_*` field longer than 1,500 characters (configurable) and
  flags it for human review — over-long fields are usually transcriptions in
  disguise, not paraphrases.

If you're unsure whether a paraphrase is close enough to the source to be a
problem, err toward rewriting it further from a different angle, or ask a
reviewer before merging.

## Item lifecycle

See `plan.md` §7 for the full ingestion pipeline (S1–S7) and §4 for the item
schema. In short: extract → triage → paraphrase → draft the Lean statement →
prove it (private repo) → two-reviewer review → promote to `status: active`.

## Solutions stay private

Reference proofs (`lean/PhysProofBenchSolutions/` via the
`physproofbench-solutions` submodule) never get merged into this public
repo. Public item files (`lean/PhysProofBench/Items/*.lean`) contain a
statement and `sorry`, nothing more.
