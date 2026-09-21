"""Minimal single-item runner: render -> call model -> extract -> grade.

This is NOT yet the full plan.md §8 runner (no pass@k, no caching, no
parallelism, no multi-item `runs/<timestamp>-<slug>/` summary table) -- it's
the smallest real slice needed to validate the model-calling plumbing end to
end on one item. Extend towards the full §8 spec rather than duplicating
this when that's built.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .extract import extract_lean
from .grading import GradeReport, grade_submission
from .models.openai_client import complete
from .render import gold_statement_prefix, render_proof_prompt, template_hash
from .schema import load_item_meta


@dataclass
class RunResult:
    item_id: str
    model: str
    condition: str
    template_hash: str
    used_extraction_fallback: bool
    # None when the model returned no content at all (nothing to grade).
    grade: GradeReport | None
    run_dir: Path
    finish_reason: str | None = None
    had_reasoning: bool = False


def _extract_nl_section(nl_md_text: str, anchor: str) -> str:
    """Pull the `## statement` or `## proof` section out of an nl.md file
    (the `nl.statement`/`nl.proof` anchors from meta.yaml, plan.md §4)."""
    pattern = re.compile(
        rf"^## {re.escape(anchor)}\s*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(nl_md_text)
    if not match:
        raise ValueError(f"no '## {anchor}' section found in nl.md")
    return match.group(1).strip()


def run_item_once(
    *,
    item_id: str,
    model: str,
    condition: str = "no_nl_proof",
    items_dir: Path,
    lean_project_dir: Path,
    out_dir: Path,
    temperature: float = 0.0,
    max_tokens: int | None = 16384,
    enable_thinking: bool | None = None,
    timeout: float | None = 3600.0,
) -> RunResult:
    item_dir = items_dir / item_id
    meta = load_item_meta(item_dir / "meta.yaml")

    repo_root = items_dir.parent
    gold_path = repo_root / meta.lean_file
    gold_text = gold_path.read_text(encoding="utf-8")
    gold_prefix = gold_statement_prefix(gold_text)

    nl_proof = None
    if condition == "with_nl_proof":
        nl_proof = _extract_nl_section(
            (item_dir / "nl.md").read_text(encoding="utf-8"), "proof"
        )

    prompt = render_proof_prompt(
        gold_statement_lean=gold_prefix, condition=condition, nl_proof=nl_proof
    )
    prompt_hash = template_hash(prompt)

    completion = complete(
        prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        enable_thinking=enable_thinking,
        timeout=timeout,
    )
    extraction = extract_lean(completion.text)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / f"{timestamp}-{item_id}-{condition}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (run_dir / "completion_raw.txt").write_text(completion.text, encoding="utf-8")
    if completion.reasoning:
        (run_dir / "reasoning.txt").write_text(completion.reasoning, encoding="utf-8")
    (run_dir / "candidate.lean").write_text(extraction.lean, encoding="utf-8")
    (run_dir / "meta.json").write_text(
        json.dumps(
            {
                "item_id": item_id,
                "model": model,
                "condition": condition,
                "mode": "proof",
                "template_version": "v1",
                "template_hash": prompt_hash,
                "temperature": temperature,
                # null = uncapped (server-side context limit only)
                "max_tokens": max_tokens if max_tokens and max_tokens > 0 else None,
                "enable_thinking": enable_thinking,
                "finish_reason": completion.finish_reason,
                "had_reasoning": bool(completion.reasoning),
                "used_extraction_fallback": extraction.used_fallback,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    if not completion.text.strip():
        # Nothing to grade. Grading the empty string would report a
        # misleading gate failure (statement_edited) for what is really a
        # truncated or empty generation.
        return RunResult(
            item_id=item_id,
            model=model,
            condition=condition,
            template_hash=prompt_hash,
            used_extraction_fallback=extraction.used_fallback,
            grade=None,
            run_dir=run_dir,
            finish_reason=completion.finish_reason,
            had_reasoning=bool(completion.reasoning),
        )

    report = grade_submission(
        lean_project_dir=lean_project_dir,
        submission_path=run_dir / "candidate.lean",
        gold_path=gold_path,
        decl_name=meta.decl_name,
        mode="proof",
    )
    (run_dir / "grade.json").write_text(
        json.dumps(
            {
                "verdict": report.verdict,
                "gate_failures": report.gate.failures,
                "compile_ok": report.compile.ok if report.compile else None,
                "axioms": report.axiom_audit.axioms if report.axiom_audit else None,
                "audit_failures": (
                    report.axiom_audit.failures if report.axiom_audit else []
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return RunResult(
        item_id=item_id,
        model=model,
        condition=condition,
        template_hash=prompt_hash,
        used_extraction_fallback=extraction.used_fallback,
        grade=report,
        run_dir=run_dir,
        finish_reason=completion.finish_reason,
        had_reasoning=bool(completion.reasoning),
    )
