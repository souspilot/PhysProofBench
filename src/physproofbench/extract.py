"""Extract Lean source from a model completion. plan.md §8: "one rule (last
fenced ```lean block; if absent, the whole completion) and log when the
fallback fires."
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_FENCED_LEAN_BLOCK = re.compile(r"```lean\s*\n(.*?)```", re.DOTALL)


@dataclass
class Extraction:
    lean: str
    used_fallback: bool


def extract_lean(completion: str) -> Extraction:
    blocks = _FENCED_LEAN_BLOCK.findall(completion)
    if blocks:
        return Extraction(lean=blocks[-1].strip() + "\n", used_fallback=False)
    return Extraction(lean=completion.strip() + "\n", used_fallback=True)
