"""`physproofbench` CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click

from .grading import grade_submission
from .run import run_item_once


@click.group()
def main() -> None:
    """PhysProofBench: a Lean 4 physics formalization benchmark."""


@main.command()
@click.option(
    "--submission", required=True, type=click.Path(exists=True, path_type=Path)
)
@click.option("--gold", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--decl-name", required=True)
@click.option(
    "--mode", type=click.Choice(["proof", "autoform"]), default="proof", show_default=True
)
@click.option(
    "--lean-project", required=True, type=click.Path(exists=True, path_type=Path)
)
@click.option("--timeout", type=float, default=300.0, show_default=True)
def grade(
    submission: Path,
    gold: Path | None,
    decl_name: str,
    mode: str,
    lean_project: Path,
    timeout: float,
) -> None:
    """Run L0-L2 grading on a single submission file."""
    report = grade_submission(
        lean_project_dir=lean_project,
        submission_path=submission,
        gold_path=gold,
        decl_name=decl_name,
        mode=mode,
        timeout=timeout,
    )
    click.echo(f"verdict: {report.verdict}")
    if report.gate.failures:
        click.echo(f"gate failures: {report.gate.failures}")
    if report.compile is not None and not report.compile.ok:
        click.echo("--- compiler output ---")
        click.echo(report.compile.stdout)
        click.echo(report.compile.stderr)
    if report.axiom_audit is not None:
        click.echo(f"axioms: {report.axiom_audit.axioms}")
        if report.axiom_audit.failures:
            click.echo(f"audit failures: {report.axiom_audit.failures}")
    raise SystemExit(0 if report.verdict == "pass" else 1)


@main.command()
@click.option("--item", "item_id", required=True, help="Item id, e.g. SM_01_009_001")
@click.option("--model", required=True, help="Model name as served at OPENAI_BASE_URL")
@click.option(
    "--condition",
    type=click.Choice(["no_nl_proof", "with_nl_proof"]),
    default="no_nl_proof",
    show_default=True,
)
@click.option(
    "--items-dir",
    type=click.Path(exists=True, path_type=Path),
    default=Path("items"),
    show_default=True,
)
@click.option(
    "--lean-project",
    type=click.Path(exists=True, path_type=Path),
    default=Path("lean"),
    show_default=True,
)
@click.option(
    "--out-dir",
    type=click.Path(path_type=Path),
    default=Path("runs"),
    show_default=True,
)
@click.option("--temperature", type=float, default=0.0, show_default=True)
def run(
    item_id: str,
    model: str,
    condition: str,
    items_dir: Path,
    lean_project: Path,
    out_dir: Path,
    temperature: float,
) -> None:
    """Render a prompt for one item (`proof` mode), call the model at
    OPENAI_BASE_URL, extract the Lean block, and grade it (L0-L2).

    Not the full plan.md §8 runner -- one item, one sample, no pass@k. See
    run.py's docstring.
    """
    result = run_item_once(
        item_id=item_id,
        model=model,
        condition=condition,
        items_dir=items_dir,
        lean_project_dir=lean_project,
        out_dir=out_dir,
        temperature=temperature,
    )
    click.echo(f"run dir: {result.run_dir}")
    click.echo(f"template hash: {result.template_hash}")
    if result.used_extraction_fallback:
        click.echo(
            "WARNING: no ```lean fenced block found in the completion; "
            "graded the raw completion text as a fallback"
        )
    report = result.grade
    click.echo(f"verdict: {report.verdict}")
    if report.gate.failures:
        click.echo(f"gate failures: {report.gate.failures}")
    if report.compile is not None and not report.compile.ok:
        click.echo("--- compiler output ---")
        click.echo(report.compile.stdout)
        click.echo(report.compile.stderr)
    if report.axiom_audit is not None:
        click.echo(f"axioms: {report.axiom_audit.axioms}")
    raise SystemExit(0 if report.verdict == "pass" else 1)
