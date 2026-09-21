"""Extract Lean source from a model completion. plan.md §8: "one rule (last
fenced ```lean block; if absent, the whole completion) and log when the
fallback fires."

Refinement found from a real Qwen3 run: models often open a ```lean fence
and never close it (truncation, a stray EOS, or a runaway generation). The
last opening fence is still the model's clear intent, so the text after it
is taken as the block and `unterminated_fence` is set, rather than falling
back to the whole completion with a literal ```lean line left in the file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_OPEN_FENCE = re.compile(r"```lean[ \t]*\r?\n")


@dataclass
class Extraction:
    lean: str
    # No ```lean fence at all: the whole completion was used.
    used_fallback: bool
    # A ```lean fence was opened but never closed.
    unterminated_fence: bool = False


def extract_lean(completion: str) -> Extraction:
    opens = list(_OPEN_FENCE.finditer(completion))
    if not opens:
        return Extraction(lean=completion.strip() + "\n", used_fallback=True)
    body = completion[opens[-1].end() :]
    close = body.find("```")
    if close == -1:
        return Extraction(
            lean=body.strip() + "\n", used_fallback=False, unterminated_fence=True
        )
    return Extraction(lean=body[:close].strip() + "\n", used_fallback=False)
