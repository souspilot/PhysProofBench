# Prompt templates

**Prompts are part of the benchmark.** Changing a template's text bumps its
version tag below and invalidates cross-run comparisons at that tag. `render.py`
hashes the rendered template and stores the hash in every run's metadata;
`physproofbench report` refuses to compare runs at different template hashes
without an explicit `--allow-mismatched-templates` flag.

Placeholders: `{item_id}`, `{gold_statement_lean}` (item file up to `:= by`),
`{nl_statement}`, `{nl_proof}`, `{core_source}` (only when the
library-in-context ablation is on), `{candidate_lean}`, `{candidate_nl}`.

## `proof` mode

### A1 — `no_nl_proof` (v1)

```
You are given a Lean 4 theorem statement from a physics textbook. Prove it.

Do not modify the statement (the signature, hypotheses, or conclusion). Reply
with only a `:= by ...` proof (or a complete replacement for the `sorry`)
that typechecks against the statement below, using Mathlib{ + PhysProofBench.Core
source, if included below}.

```lean
{gold_statement_lean}
```
{core_source, if library-in-context is on}

Reply with a single ```lean fenced code block containing the complete file
(imports through the closed proof). No commentary outside the code block.
```

### A2 — `with_nl_proof` (v1)

Same as A1, with this paragraph inserted before the statement:

```
Here is the textbook's own proof, in natural language, for reference. It may
use different notation or take a different path than is convenient in Lean;
you do not have to follow it exactly.

{nl_proof}
```

## `autoform` mode

### B1 — `no_nl_proof` (v1)

```
You are given a natural-language physics claim. Formalize it in Lean 4 —
write both the statement and the proof.

{nl_statement}
{core_source, if library-in-context is on}

Reply with a single ```lean fenced code block containing the complete file:
imports, the theorem statement (choose your own declaration name and
signature), and a complete `sorry`-free proof. No commentary outside the code
block.
```

### B2 — `with_nl_proof` (v1)

Same as B1, with the textbook proof appended:

```
Here is the textbook's own proof of this claim, in natural language:

{nl_proof}
```

## Judge prompts (L4, v1)

Two independent judges, different model families. Each sees: the paraphrased
NL statement, the candidate Lean, the gold Lean, and the L3 verdict — never
the other judge's score.

```
You are scoring a Lean 4 autoformalization of a physics claim against a
reference (gold) formalization. Score four axes, each 0-4, with a one-sentence
justification per axis:

- Formal Quality (FQ): is the code well-structured, idiomatic Mathlib, and
  reusable — independent of whether the statement matches the gold?
- Logical Preservation (LP): does the candidate capture the logical structure
  (quantifiers, hypothesis/conclusion split) of the informal claim?
- Mathematical Consistency (MC): are the objects and operations the
  mathematically correct ones for this physics?

(Formal Validity is not scored here — it's computed deterministically from
compilation and audit results.)

Then select every applicable drift label from: notational_collapse,
abstraction_elevation, proof_strategy_substitution, implicit_premise_selection,
quantifier_error, missing_hypothesis, extra_hypothesis. See docs/TAXONOMY.md
for definitions. Select none if none apply.

Natural-language claim:
{nl_statement}

Gold Lean:
```lean
{gold_statement_lean}
```

Candidate Lean:
```lean
{candidate_lean}
```

L3 statement-equivalence verdict: {l3_verdict}

Reply as JSON: {{"fq": int, "fq_reason": str, "lp": int, "lp_reason": str,
"mc": int, "mc_reason": str, "drift_labels": [str, ...]}}
```

## Changelog

- v1 (this file, initial): first frozen templates, written alongside the M0
  skeleton. No runs have used these yet, so no invalidation history.
