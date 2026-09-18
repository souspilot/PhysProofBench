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

from .lean.audit import AxiomAuditResult, audit_axioms, build_axiom_check_source
from .lean.gates import GateResult, check_gates
from .lean.sandbox import CompileResult, compile_file

Verdict = Literal["pass", "gate_fail", "compile_fail", "audit_fail"]


@dataclass
class GradeReport:
    verdict: Verdict
    gate: GateResult
    compile: CompileResult | None = None
    axiom_audit: AxiomAuditResult | None = None


def grade_submission(
    *,
    lean_project_dir: Path,
    submission_path: Path,
    gold_path: Path | None,
    decl_name: str,
    mode: str = "proof",
    timeout: float = 300.0,
) -> GradeReport:
    submission_text = submission_path.read_text(encoding="utf-8")
    gold_text = gold_path.read_text(encoding="utf-8") if gold_path else None

    gate = check_gates(submission_text, mode=mode, gold_text=gold_text)
    if not gate.passed:
        return GradeReport(verdict="gate_fail", gate=gate)

    with tempfile.NamedTemporaryFile(
        "w", suffix=".lean", delete=False, dir=lean_project_dir, encoding="utf-8"
    ) as f:
        f.write(submission_text)
        f.write(build_axiom_check_source(decl_name))
        temp_path = Path(f.name)
    try:
        compile_result = compile_file(lean_project_dir, temp_path, timeout=timeout)
    finally:
        temp_path.unlink(missing_ok=True)

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
