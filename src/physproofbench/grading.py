"""Orchestrates L0 gates -> L1 compile -> L2 axiom audit for a submission.

L2.3 (statement preservation) is implemented in `lean/audit.py` but not yet
wired in here automatically — it needs the gold and submission text placed
as importable Lean modules, which the ingestion/run machinery (later
milestones) will manage. Call `audit.build_statement_preservation_source`
directly until then.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .lean.audit import (
    AxiomAuditResult,
    SignatureParseError,
    audit_axioms,
    build_axiom_check_source,
    build_same_file_gold_check,
)
from .lean.gates import GateResult, check_gates
from .lean.sandbox import DEFAULT_MEMORY_CAP_BYTES, CompileResult, compile_file

Verdict = Literal["pass", "gate_fail", "compile_fail", "audit_fail"]

# Bump whenever a change to grading could change a verdict (docs/GRADING.md).
# The batch runner re-grades stored samples whose grade was produced under a
# different version.
GRADING_VERSION = "2"

# Compiler output kept in grade records; full logs of failing compiles can be
# megabytes of elaboration traces, and the first errors are what matters.
_COMPILER_OUTPUT_LIMIT = 20_000


@dataclass
class GradeReport:
    verdict: Verdict
    gate: GateResult
    compile: CompileResult | None = None
    axiom_audit: AxiomAuditResult | None = None
    # Set only for gate_fail == [statement_edited] with diagnosis on; see
    # `_diagnose_statement_edit`. Never changes the verdict.
    statement_edit_diagnostic: dict | None = None

    def to_dict(self) -> dict:
        """JSON-serializable record, as stored in `grade.json`."""
        compile_output = None
        if self.compile is not None and not self.compile.ok:
            compile_output = (self.compile.stdout + "\n" + self.compile.stderr).strip()
            compile_output = compile_output[:_COMPILER_OUTPUT_LIMIT]
        return {
            "verdict": self.verdict,
            "grading_version": GRADING_VERSION,
            "gate_failures": self.gate.failures,
            "compile_ok": self.compile.ok if self.compile else None,
            "compile_timed_out": self.compile.timed_out if self.compile else None,
            "compile_elapsed_s": self.compile.elapsed_s if self.compile else None,
            "compiler_output": compile_output,
            "axioms": self.axiom_audit.axioms if self.axiom_audit else None,
            "audit_failures": self.axiom_audit.failures if self.axiom_audit else [],
            "statement_edit_diagnostic": self.statement_edit_diagnostic,
        }


def grade_submission(
    *,
    lean_project_dir: Path,
    submission_path: Path,
    gold_path: Path | None,
    decl_name: str,
    mode: str = "proof",
    timeout: float = 300.0,
    memory_cap_bytes: int | None = DEFAULT_MEMORY_CAP_BYTES,
    diagnose_statement_edits: bool = False,
) -> GradeReport:
    """L0 -> L1 -> L2 for one submission file.

    `diagnose_statement_edits`: when the *only* gate failure is
    `statement_edited`, additionally compile the submission and check
    whether its declaration still proves the gold type, recording the result
    in `statement_edit_diagnostic`. The verdict stays `gate_fail`. Costs up
    to two extra compiles for such submissions; meant for pilot studies
    measuring how often the text gate rejects otherwise-correct proofs.
    """
    submission_text = submission_path.read_text(encoding="utf-8")
    gold_text = gold_path.read_text(encoding="utf-8") if gold_path else None

    gate = check_gates(submission_text, mode=mode, gold_text=gold_text)
    if not gate.passed:
        report = GradeReport(verdict="gate_fail", gate=gate)
        if (
            diagnose_statement_edits
            and gold_text is not None
            and gate.failures == ["gate: statement_edited"]
        ):
            report.statement_edit_diagnostic = _diagnose_statement_edit(
                lean_project_dir, submission_text, gold_text, decl_name,
                timeout=timeout, memory_cap_bytes=memory_cap_bytes,
            )
        return report

    compile_result = _compile_text(
        lean_project_dir,
        submission_text + build_axiom_check_source(decl_name),
        timeout=timeout,
        memory_cap_bytes=memory_cap_bytes,
    )

    if not compile_result.ok:
        return GradeReport(verdict="compile_fail", gate=gate, compile=compile_result)

    axiom_audit = audit_axioms(
        compile_result.stdout + "\n" + compile_result.stderr, decl_name
    )
    if not axiom_audit.passed:
        return GradeReport(
            verdict="audit_fail", gate=gate, compile=compile_result, axiom_audit=axiom_audit
        )

    return GradeReport(
        verdict="pass", gate=gate, compile=compile_result, axiom_audit=axiom_audit
    )


def _compile_text(
    lean_project_dir: Path, text: str, *, timeout: float, memory_cap_bytes: int | None
) -> CompileResult:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".lean", delete=False, dir=lean_project_dir, encoding="utf-8"
    ) as f:
        f.write(text)
        temp_path = Path(f.name)
    try:
        return compile_file(
            lean_project_dir, temp_path, timeout=timeout, memory_cap_bytes=memory_cap_bytes
        )
    finally:
        temp_path.unlink(missing_ok=True)


def _diagnose_statement_edit(
    lean_project_dir: Path,
    submission_text: str,
    gold_text: str,
    decl_name: str,
    *,
    timeout: float,
    memory_cap_bytes: int | None,
) -> dict:
    """Would this gate-rejected submission otherwise pass?

    `would_pass` is True iff it compiles, its axioms audit clean, and its
    `decl_name` proves the gold type (`audit.build_same_file_gold_check`).
    """
    result: dict = {"compiles": None, "axioms_ok": None, "proves_gold_type": None,
                    "would_pass": False}
    compiled = _compile_text(
        lean_project_dir, submission_text + build_axiom_check_source(decl_name),
        timeout=timeout, memory_cap_bytes=memory_cap_bytes,
    )
    result["compiles"] = compiled.ok
    if not compiled.ok:
        return result
    audit = audit_axioms(compiled.stdout + "\n" + compiled.stderr, decl_name)
    result["axioms_ok"] = audit.passed
    if not audit.passed:
        return result
    try:
        check = build_same_file_gold_check(gold_text, decl_name)
    except SignatureParseError as exc:
        result["proves_gold_type"] = None
        result["error"] = f"could not parse gold signature: {exc}"
        return result
    checked = _compile_text(
        lean_project_dir, submission_text + check,
        timeout=timeout, memory_cap_bytes=memory_cap_bytes,
    )
    result["proves_gold_type"] = checked.ok
    result["would_pass"] = checked.ok
    return result
