# Taxonomy

## `proof_kind`

Tagged per item in `meta.yaml`. This is the axis existing physics benchmarks
don't tag consistently.

- **`exact`** — no approximation, no unstated hypotheses beyond ordinary
  regularity. The gold statement is a faithful, complete formalization of the
  source claim.
- **`approximation`** — the source's claim is itself approximate (a
  perturbative expansion, a large-`N`/thermodynamic limit, a controlled or
  uncontrolled error bound). See `approximation.flavor` /
  `approximation.encoding` below.
- **`hidden_assumption`** — the source's proof relies on a regularity,
  domain, or modeling assumption it does not state. Every such assumption is
  listed in `hidden_assumptions[]` with a `justification`.
- **`mixed`** — both of the above apply.

### `approximation.flavor`

- `disguised_limit` — stated as an approximation but is really an exact
  statement about a limit (e.g. "as `N → ∞`" dressed up as "`≈`").
- `controlled` — an explicit, provable error bound exists and is part of the
  gold statement (`Core/Approx.lean`'s `HasErrorBound`).
- `uncontrolled` — the source asserts closeness without a provable bound;
  the gold statement must encode this honestly (e.g. via `IsLittleO`) rather
  than inventing a bound the source never proves.

### `approximation.encoding`

- `model_substitution` — replace the true model with a simpler one and prove
  something about the simpler model.
- `asymptotic` — `IsLittleO` / `IsBigO` style statement.
- `error_bound` — explicit `HasErrorBound`-style numeric bound.
- `postulate` — the approximation is assumed as a hypothesis, not derived.

### `hidden_assumptions[].justification`

- `source_stated` — the source states it explicitly (shouldn't normally
  appear in `hidden_assumptions`, which is for *unstated* assumptions; use
  this only for borderline cases where it's stated non-adjacently, e.g. in an
  earlier section's running assumptions).
- `source_implied` — a careful reader would infer it's needed, even though
  the source doesn't say so at the point of use.
- `encoding_artifact` — needed only because of how we chose to formalize the
  objects (e.g. `Fintype` where the source leaves finiteness implicit in
  prose), not part of the physics.
- `strengthening` — we added a hypothesis stronger than what's truly needed,
  usually to make the Lean proof tractable. **Blocks `status: active`** per
  `plan.md` §4 unless `notes.md` explains why it's unavoidable.

## Drift labels (autoformalization mode, L4)

From FormalPhysics/FormalScience (arXiv:2604.23002). Multi-select, applied by
judges to a candidate autoformalization relative to the gold:

- `notational_collapse` — distinct source concepts get mapped to the same
  Lean object, losing a distinction the physics needs.
- `abstraction_elevation` — the candidate proves something more general (or
  more abstract) than the source claim, in a way that quietly discards
  physical content.
- `proof_strategy_substitution` — the candidate's proof strategy doesn't
  match the source's, in a way that changes what's actually being shown
  (not merely "a different valid proof").
- `implicit_premise_selection` — the candidate silently picks one of several
  premises the source leaves ambiguous or context-dependent.
- `quantifier_error` — wrong `∀`/`∃` order or scope relative to the physics.
- `missing_hypothesis` — the candidate drops a hypothesis the source needs.
- `extra_hypothesis` — the candidate adds a hypothesis the source doesn't
  need (see `hidden_assumptions[].justification: strengthening` above for
  the gold-side analogue of this failure mode).

## Difficulty bands

`difficulty.band`, derived from `difficulty.decl_count` (declarations the
reference proof needs beyond `Core`):

| Band | `decl_count` |
|---|---|
| `very_small` | 0–2 |
| `small` | 3–7 |
| `moderate` | 8–15 |
| `large` | 16–40 |
| `very_large` | 40+ |

These thresholds are a starting point, not load-bearing — revisit once
enough items exist to see the real distribution.
