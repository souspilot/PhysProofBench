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


def strip_lean_comments(text: str) -> str:
    """Remove `-- line`, `/- block -/` (nested) and `/-- doc -/` comments,
    leaving string literals intact. Lean block comments nest."""
    out: list[str] = []
    i, n, depth = 0, len(text), 0
    while i < n:
        two = text[i : i + 2]
        if depth > 0:
            if two == "/-":
                depth += 1
                i += 2
            elif two == "-/":
                depth -= 1
                i += 2
            else:
                i += 1
            continue
        if two == "/-":
            depth = 1
            i += 2
            out.append(" ")
        elif two == "--":
            while i < n and text[i] != "\n":
                i += 1
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i : j + 1])
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


# Extra `import Mathlib` / `import Mathlib.Foo.Bar` (and `import Aesop`, a
# Mathlib dependency) lines only add
# declarations to the environment; they cannot redefine or shadow anything the
# gold statement depends on, and models add them routinely (the prompt says
# "using Mathlib"). Any other added import still counts as an edit.
_MATHLIB_IMPORT = re.compile(r"(?<![\w.])import (?:Mathlib|Aesop)(?:\.[\w.]+)*(?![\w.])")
# `set_option maxHeartbeats N` (alone, or as `... in` before the theorem) only
# changes the elaboration budget, never the statement; the wall-clock
# compile timeout still bounds it. Specialist provers' training header
# includes `set_option maxHeartbeats 400000` / `0`.
_MAX_HEARTBEATS_LINE = re.compile(r"(?<![\w.])set_option maxHeartbeats \d+(?:\s+in)?(?![\w.])")


def _canonical(text: str) -> str:
    """Comment-, whitespace- and Mathlib-import-insensitive form, for
    comparing statements."""
    stripped = _MATHLIB_IMPORT.sub(" ", strip_lean_comments(text))
    stripped = _MAX_HEARTBEATS_LINE.sub(" ", stripped)
    return " ".join(stripped.split())


def _statement_prefix(text: str) -> str | None:
    """Canonical text up to (and excluding) the first `:= by`, or None."""
    canon = _canonical(text)
    idx = canon.find(_STATEMENT_MARKER)
    if idx == -1:
        return None
    return canon[:idx].strip()


_IMPORT_LINE = re.compile(r"^\s*import\s+\S+\s*$")
_OPEN_LINE = re.compile(r"^\s*open\s+\S.*$")
_DECL_START = ("/--", "theorem ", "lemma ")


def _head(lines: list[str]) -> list[str]:
    """Lines before the item's docstring/declaration."""
    out = []
    for line in lines:
        if line.lstrip().startswith(_DECL_START):
            break
        out.append(line)
    return out


def restore_item_preamble(submission_text: str, gold_text: str) -> tuple[str, bool]:
    """Put the item's own setup lines -- its `import`s and `open`s, which
    the benchmark fixes and which are not part of what a model is asked to
    prove -- in front of the submission if it dropped any.

    Specialist provers always emit their fixed training header
    (`import Mathlib`, `import Aesop`, `set_option maxHeartbeats ...`) and
    drop everything else above the theorem, including
    `import PhysProofBench.Core.X` / `open PhysProofBench`. Without them the
    item's definitions don't exist, so the file can't compile, and the
    statement gate reports an edit although the theorem is unchanged.

    Only lines missing from the submission are added: the item's imports
    first (the submission's own imports follow), then its missing `open`s.
    Nothing else changes, so anything a submission *adds* before the theorem
    (other imports, `open`s, definitions) is still caught by the gate.
    Returns (text, whether anything was restored).
    """
    gold_head = _head(gold_text.splitlines())
    gold_imports = [l.strip() for l in gold_head if _IMPORT_LINE.match(l)]
    gold_opens = [l.strip() for l in gold_head if _OPEN_LINE.match(l)]
    lines = submission_text.splitlines()
    sub_imports = [l.strip() for l in lines if _IMPORT_LINE.match(l)]
    body = [l for l in lines if not _IMPORT_LINE.match(l)]
    sub_opens = {l.strip() for l in _head(body) if _OPEN_LINE.match(l)}
    missing_imports = [i for i in gold_imports if i not in sub_imports]
    missing_opens = [o for o in gold_opens if o not in sub_opens]
    if not missing_imports and not missing_opens:
        return submission_text, False
    imports = gold_imports + [i for i in sub_imports if i not in gold_imports]
    parts = ["\n".join(imports), ""]
    if missing_opens:
        parts += ["\n".join(missing_opens), ""]
    parts.append("\n".join(body).strip("\n"))
    return "\n".join(parts) + "\n", True


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
        if sub_prefix is None or sub_prefix != gold_prefix:
            failures.append("gate: statement_edited")

    return GateResult(passed=not failures, failures=failures)
