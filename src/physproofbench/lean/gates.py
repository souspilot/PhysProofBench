"""L0 syntactic gates: reject a submission before it ever reaches the compiler.

See docs/GRADING.md#l0-syntactic-gates-gatespy for the contract this
implements. Gate failures are distinct from compile failures (L1): a gate
failure means the submission tried to cheat or is structurally invalid, not
merely that the model failed to prove the theorem.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

FORBIDDEN_TOKENS = ["sorry", "admit", "stop"]
FORBIDDEN_TACTICS = ["native_decide", "implemented_by", "unsafe", "extern"]
FORBIDDEN_SET_OPTIONS = ["debug.skipKernelTC"]

_STATEMENT_MARKER = ":= by"


def _word_pattern(word: str) -> re.Pattern[str]:
    return re.compile(r"(?<![\w.])" + re.escape(word) + r"(?![\w.])")


_FORBIDDEN_TOKEN_PATTERNS = {w: _word_pattern(w) for w in FORBIDDEN_TOKENS}
_FORBIDDEN_TACTIC_PATTERNS = {w: _word_pattern(w) for w in FORBIDDEN_TACTICS}
_AXIOM_PATTERN = re.compile(r"(?m)^\s*axiom\b")
_MAX_HEARTBEATS_PATTERN = re.compile(
    r"set_option\s+maxHeartbeats\s+(\d+)"
)
_SKIP_OPTION_PATTERN = re.compile(
    r"set_option\s+(" + "|".join(re.escape(o) for o in FORBIDDEN_SET_OPTIONS) + r")\b"
)


@dataclass
class GateResult:
    passed: bool
    failures: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.passed


def _statement_prefix(text: str) -> str | None:
    """Text up to (and excluding) the first `:= by` marker, or None if absent."""
    idx = text.find(_STATEMENT_MARKER)
    if idx == -1:
        return None
    return text[:idx]


def _normalize(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def check_gates(
    submission_text: str,
    *,
    mode: str = "proof",
    gold_text: str | None = None,
    max_heartbeats_cap: int | None = None,
) -> GateResult:
    """Run all L0 gates against a submission.

    `mode` is "proof" or "autoform" (see plan.md §1). The statement-edit gate
    only applies in "proof" mode, where a gold statement exists to diff
    against.
    """
    failures: list[str] = []

    for name, pattern in _FORBIDDEN_TOKEN_PATTERNS.items():
        if pattern.search(submission_text):
            failures.append(f"gate: {name}_present")

    if _AXIOM_PATTERN.search(submission_text):
        failures.append("gate: axiom_declared")

    for name, pattern in _FORBIDDEN_TACTIC_PATTERNS.items():
        if pattern.search(submission_text):
            failures.append(f"gate: forbidden_tactic:{name}")

    if _SKIP_OPTION_PATTERN.search(submission_text):
        failures.append("gate: forbidden_set_option:debug.skipKernelTC")

    if max_heartbeats_cap is not None:
        for match in _MAX_HEARTBEATS_PATTERN.finditer(submission_text):
            if int(match.group(1)) > max_heartbeats_cap:
                failures.append("gate: maxHeartbeats_exceeds_cap")
                break

    if mode == "proof" and gold_text is not None:
        gold_prefix = _statement_prefix(gold_text)
        sub_prefix = _statement_prefix(submission_text)
        if gold_prefix is None:
            raise ValueError(
                f"gold_text has no '{_STATEMENT_MARKER}' marker; cannot check "
                "for statement tampering"
            )
        if sub_prefix is None or _normalize(sub_prefix) != _normalize(gold_prefix):
            failures.append("gate: statement_edited")

    return GateResult(passed=not failures, failures=failures)
