"""L2 audits: sorry closure, axiom audit, statement preservation.

See docs/GRADING.md#l2-audits-auditpy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
SORRY_AXIOM = "sorryAx"

_NO_AXIOMS_PATTERN = re.compile(r"does not depend on any axioms")
_DEPENDS_ON_PATTERN = re.compile(r"depends on axioms:\s*\[([^\]]*)\]")

_OPEN_TO_CLOSE = {"(": ")", "{": "}", "[": "]"}
_CLOSE_CHARS = set(_OPEN_TO_CLOSE.values())


@dataclass
class AxiomAuditResult:
    passed: bool
    axioms: list[str] | None
    failures: list[str] = field(default_factory=list)


def parse_print_axioms_output(text: str, decl_name: str) -> set[str] | None:
    """Parse the message produced by `#print axioms {decl_name}`.

    Returns the set of axiom names, or None if no such message was found in
    `text` (e.g. the compile failed before reaching the `#print axioms`
    command).

    Known Lean 4 output shapes (VERIFY against the pinned toolchain if this
    ever stops matching — see docs/GRADING.md L2.2):
      "'decl' does not depend on any axioms"
      "'decl' depends on axioms: [propext, Classical.choice]"
    """
    if _NO_AXIOMS_PATTERN.search(text):
        return set()
    match = _DEPENDS_ON_PATTERN.search(text)
    if match is None:
        return None
    names = [n.strip() for n in match.group(1).split(",") if n.strip()]
    return set(names)


def audit_axioms(compile_output: str, decl_name: str) -> AxiomAuditResult:
    axioms = parse_print_axioms_output(compile_output, decl_name)
    if axioms is None:
        return AxiomAuditResult(
            passed=False,
            axioms=None,
            failures=["audit: print_axioms_output_not_found"],
        )
    failures = []
    if SORRY_AXIOM in axioms:
        failures.append("audit: sorry_in_axiom_closure")
    disallowed = axioms - ALLOWED_AXIOMS - {SORRY_AXIOM}
    if disallowed:
        failures.append(f"audit: disallowed_axioms:{','.join(sorted(disallowed))}")
    return AxiomAuditResult(passed=not failures, axioms=sorted(axioms), failures=failures)


def build_axiom_check_source(decl_name: str) -> str:
    """Line to append to a compiled file to trigger the L2.1/L2.2 audits."""
    return f"\n#print axioms {decl_name}\n"


# --- L2.3: statement preservation (proof mode) -----------------------------
#
# Best-effort textual splice of a `theorem`/`lemma` declaration's binders and
# result type into a standalone `example`, applying the submission's
# declaration to the same explicit-binder names. Does not handle every Lean
# binder shape (anonymous constructor patterns, notation-defined binders);
# treat a parse failure as "could not build the checker", not as a grading
# verdict, and fall back to the L0 text-diff gate in that case.


class SignatureParseError(ValueError):
    pass


def _skip_ws(text: str, i: int) -> int:
    while i < len(text) and text[i].isspace():
        i += 1
    return i


def _find_decl_start(text: str, decl_name: str) -> int:
    pattern = re.compile(
        r"(?:theorem|lemma)\s+" + re.escape(decl_name) + r"(?![\w'!?])"
    )
    match = pattern.search(text)
    if match is None:
        raise SignatureParseError(f"declaration {decl_name!r} not found")
    return match.end()


def _find_separator_colon(text: str, start: int) -> int:
    """Index of the depth-0 `:` separating binders from the result type."""
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c in _OPEN_TO_CLOSE:
            depth += 1
        elif c in _CLOSE_CHARS:
            depth -= 1
        elif c == ":" and depth == 0:
            if text[i : i + 2] == ":=":
                raise SignatureParseError(
                    "reached ':=' before finding a binder/result-type separator"
                )
            return i
        i += 1
    raise SignatureParseError("no depth-0 ':' found before end of text")


def _find_terminator(text: str, start: int) -> int:
    """Index of the depth-0 `:=` ending the result type."""
    depth = 0
    i = start
    while i < len(text) - 1:
        c = text[i]
        if c in _OPEN_TO_CLOSE:
            depth += 1
        elif c in _CLOSE_CHARS:
            depth -= 1
        elif c == ":" and text[i + 1] == "=" and depth == 0:
            return i
        i += 1
    raise SignatureParseError("no depth-0 ':=' found before end of text")


def _split_binder_groups(binder_text: str) -> list[str]:
    groups: list[str] = []
    depth = 0
    current: list[str] = []
    for c in binder_text:
        if c in _OPEN_TO_CLOSE:
            if depth == 0 and current and "".join(current).strip():
                # stray text between groups that isn't whitespace
                pass
            depth += 1
            current.append(c)
        elif c in _CLOSE_CHARS:
            depth -= 1
            current.append(c)
            if depth == 0:
                groups.append("".join(current))
                current = []
        else:
            if depth > 0:
                current.append(c)
    if current and "".join(current).strip():
        raise SignatureParseError(f"unbalanced binder text: {binder_text!r}")
    return groups


def _explicit_names_in_group(group: str) -> list[str]:
    """Explicit ('(' ... ')') binder names in a single group, else []."""
    if not group.startswith("("):
        return []
    inner = group[1:-1]
    colon_idx = _find_separator_colon(inner, 0) if ":" in inner else None
    if colon_idx is None:
        # binder with no explicit type ascription, e.g. `(n)`
        head = inner
    else:
        head = inner[:colon_idx]
    return [tok for tok in head.split() if tok != "_"]


@dataclass
class ParsedSignature:
    binder_groups: list[str]
    result_type: str
    explicit_arg_names: list[str]


def parse_theorem_signature(gold_text: str, decl_name: str) -> ParsedSignature:
    header_start = _find_decl_start(gold_text, decl_name)
    sep = _find_separator_colon(gold_text, header_start)
    binder_text = gold_text[header_start:sep].strip()
    term_start = sep + 1
    terminator = _find_terminator(gold_text, term_start)
    result_type = gold_text[term_start:terminator].strip()
    groups = _split_binder_groups(binder_text) if binder_text else []
    explicit_names: list[str] = []
    for g in groups:
        explicit_names.extend(_explicit_names_in_group(g))
    return ParsedSignature(
        binder_groups=groups, result_type=result_type, explicit_arg_names=explicit_names
    )


_IMPORT_LINE = re.compile(r"(?m)^import\s+\S+\s*$")


def namespace_wrap(lean_text: str, namespace: str) -> str:
    """Wrap all non-`import` content of `lean_text` in `namespace ... end`.

    Item files and submissions (plan.md §5.3) declare their theorem at the
    top level, with no `namespace` block -- so a bare `import`ed module does
    NOT make its declarations accessible as `Module.decl` (Lean 4 does not
    auto-namespace by file/module path). To let the L2.3 checker refer to a
    submission's declaration unambiguously as `{submission_module}.{decl}`,
    the harness places the submission under a module whose source has been
    wrapped this way -- never by asking the model to write the wrapping
    itself.
    """
    import_lines = []
    body_lines = []
    in_imports = True
    for line in lean_text.splitlines():
        if in_imports and (line.strip() == "" or _IMPORT_LINE.match(line)):
            import_lines.append(line)
            continue
        in_imports = False
        body_lines.append(line)
    imports = "\n".join(import_lines).rstrip()
    body = "\n".join(body_lines).strip()
    prefix = f"{imports}\n\n" if imports else ""
    return f"{prefix}namespace {namespace}\n\n{body}\n\nend {namespace}\n"


def build_statement_preservation_source(
    *,
    submission_module: str,
    gold_text: str,
    decl_name: str,
) -> str:
    """Lean source for the L2.3 checker file.

    Typechecking this file means `submission_module.decl_name` proves at
    least the gold statement, independent of any textual tampering. The
    gold's type is spliced in as text (not imported) -- see
    docs/GRADING.md#l2-audits-auditpy -- both because that's sufficient
    (only the *type* is needed, never the gold's proof term) and because
    importing a second top-level declaration of the same name would collide
    with the submission's. `submission_module`'s source must already be
    wrapped via `namespace_wrap` before it is built, or `{submission_module}.
    {decl_name}` will not resolve.
    """
    sig = parse_theorem_signature(gold_text, decl_name)
    binders = " ".join(sig.binder_groups)
    args = " ".join(sig.explicit_arg_names)
    applied = f"{submission_module}.{decl_name}" + (f" {args}" if args else "")
    header = f"example {binders}".rstrip()
    return (
        f"import {submission_module}\n\n"
        f"{header} : {sig.result_type} := {applied}\n"
    )
