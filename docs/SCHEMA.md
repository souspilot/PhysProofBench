# Item schema (v2, 2026-10-26)

One directory per item: `items/<id>/`.

| File | Required | Purpose |
|---|---|---|
| `meta.yaml` | yes | fields below |
| `nl.md` | yes | `## statement` and (optional) `## proof` sections |
| `review.md` | for the intuition set | AI and human review record |
| `variants.lean` | no | companion statements (drafts, not graded) |
| `notes.md` | no | formalization notes |

The gold Lean file lives in each pin at `PhysProofBench/Items/<id>.lean`.
Everything up to the first `:= by` is the statement given to the model, so
it holds exactly one theorem, preceded by any definitions it needs (in
`namespace PhysProofBench.<id>`, so names can't clash across items). Each
file carries the `-- PHYSPROOFBENCH-ITEM:` and `-- PHYSPROOFBENCH-DECL:`
tags. The text of each statement must be identical on every pin (`tests/test_pins.py`).

## `meta.yaml`

Top-level fields are only what the pipeline acts on:

```yaml
id: PI_D_001                 # = directory name
status: draft                # draft | active | retired (active needs 2 reviewers)
role: benchmark              # benchmark | canary (canaries: separate report, never scored)
category: D                  # report grouping: A-E, T (trivial), SM, CAN
lean_file: lean/PhysProofBench/Items/PI_D_001.lean
decl_name: PI_D_001          # theorem graded and axiom-audited
modes: [proof]               # proof | autoform
core_deps: []                # PhysProofBench.Core modules put in the prompt
reviewed_by: []
metadata:                    # free-form; carried, never interpreted by the pipeline
  source: {collection: USAPhO, year: 2024, item_label: "...", url: "..."}
  topic: [...]
  shape: answer_blank
  expected_answer: {...}
  intuition_move: "..."
  plug_in_trap: "..."
  review_status: ai_reviewed
```

Whether an item has an NL proof (for the `with_nl_proof` condition) is read
from `nl.md`, not declared.

## Trivial items (category `T`)

`PI_T_*` are one-line, physics-flavoured statements that any working model
should prove. They test the technical environment, not physics: prompt,
extraction, statement gate, compile on each pin, axiom audit, report. Unlike
canaries, they are ordinary `benchmark` items: they run with the main
problems by default and appear in the same tables as their own category
`T`. Their reference proofs are in `tests/fixtures/reference_proofs/`
(used by `scripts/oracle_server.py`), and they use only long-stable tactics
(`norm_num`, `linarith`, `positivity`, `ring`, basic rewriting) so they
compile on every pin.

## Migration from v1

v1's book-centred fields (`source`, `topic`, `proof_kind`, `approximation`,
`hidden_assumptions`, `difficulty`, `solution_file`, `nl` anchors,
`schema_version`, ...) moved under `metadata` unchanged for the existing
SM and CAN items. Reports group by `category` instead of `proof_kind`.
