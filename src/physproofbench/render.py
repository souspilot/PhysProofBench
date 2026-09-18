"""Prompt rendering. Templates are frozen text, kept in sync with
docs/PROMPTS.md by hand for now (see TEMPLATE_VERSION) -- changing either
without the other is a bug. See docs/PROMPTS.md for the full template set
and the versioning/hashing contract; only A1/A2 (proof mode) are
implemented here so far.
"""

from __future__ import annotations

import hashlib

TEMPLATE_VERSION = "v1"

_A1 = """\
You are given a Lean 4 theorem statement from a physics textbook. Prove it.

Do not modify the statement (the signature, hypotheses, or conclusion). Reply
with only a `:= by ...` proof (or a complete replacement for the `sorry`)
that typechecks against the statement below, using Mathlib{core_note}.

```lean
{gold_statement_lean}
```
{core_source_block}

Reply with a single ```lean fenced code block containing the complete file
(imports through the closed proof). No commentary outside the code block.
"""

_A2_NL_PARAGRAPH = """\
Here is the textbook's own proof, in natural language, for reference. It may
use different notation or take a different path than is convenient in Lean;
you do not have to follow it exactly.

{nl_proof}

"""


def gold_statement_prefix(item_lean_text: str) -> str:
    """The item file's text up to and including the `:= by` marker -- the
    statement, without the `sorry` that follows it, so a model can continue
    writing the proof from exactly that point."""
    marker = ":= by"
    idx = item_lean_text.find(marker)
    if idx == -1:
        raise ValueError(f"no {marker!r} marker found in item Lean source")
    return item_lean_text[: idx + len(marker)]


def render_proof_prompt(
    *,
    gold_statement_lean: str,
    condition: str,
    nl_proof: str | None = None,
    core_source: str | None = None,
) -> str:
    """Render the A1/A2 (`proof` mode) prompt for one item.

    `condition` is `"no_nl_proof"` (A1) or `"with_nl_proof"` (A2, requires
    `nl_proof`).
    """
    if condition not in ("no_nl_proof", "with_nl_proof"):
        raise ValueError(f"unknown condition: {condition!r}")
    if condition == "with_nl_proof" and not nl_proof:
        raise ValueError("condition 'with_nl_proof' requires nl_proof")

    core_note = " + PhysProofBench.Core source, if included below" if core_source else ""
    core_source_block = f"```lean\n{core_source}\n```\n" if core_source else ""
    prompt = _A1.format(
        gold_statement_lean=gold_statement_lean,
        core_note=core_note,
        core_source_block=core_source_block,
    )
    if condition == "with_nl_proof":
        marker = f"```lean\n{gold_statement_lean}\n```\n"
        prelude = _A2_NL_PARAGRAPH.format(nl_proof=nl_proof)
        prompt = prompt.replace(marker, prelude + marker, 1)
    return prompt


def template_hash(rendered_prompt: str) -> str:
    """Hash stored in run metadata (docs/PROMPTS.md's versioning contract)."""
    return hashlib.sha256(rendered_prompt.encode("utf-8")).hexdigest()[:16]
