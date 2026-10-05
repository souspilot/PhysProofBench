"""`physproofbench` CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click

from .grading import grade_submission
from .run import run_item_once

_GiB = 1024**3


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
@click.option(
    "--max-tokens",
    type=int,
    default=16384,
    show_default=True,
    help="Completion budget. Reasoning models spend it on thinking first. "
    "0 or -1 = no cap (limited only by the model's context window).",
)
@click.option(
    "--timeout",
    type=float,
    default=3600.0,
    show_default=True,
    help="Client-side request timeout in seconds; 0 = none. Retries are off.",
)
@click.option(
    "--thinking/--no-thinking",
    "thinking",
    default=None,
    help="Send chat_template_kwargs.enable_thinking (Qwen3-style templates via "
    "vLLM). Default: leave the server/model default alone.",
)
def run(
    item_id: str,
    model: str,
    condition: str,
    items_dir: Path,
    lean_project: Path,
    out_dir: Path,
    temperature: float,
    max_tokens: int,
    timeout: float,
    thinking: bool | None,
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
        max_tokens=max_tokens,
        enable_thinking=thinking,
        timeout=timeout if timeout > 0 else None,
    )
    click.echo(f"run dir: {result.run_dir}")
    click.echo(f"template hash: {result.template_hash}")
    click.echo(f"finish_reason: {result.finish_reason}")
    if result.grade is None:
        click.echo(
            "verdict: no_output -- the model returned empty content, so there "
            "was nothing to grade."
        )
        if result.finish_reason == "length":
            click.echo(
                "  Token budget exhausted"
                + (" while thinking (see reasoning.txt)" if result.had_reasoning else "")
                + (
                    ". Uncapped, so the context window was exhausted; try "
                    "--no-thinking or a shorter prompt."
                    if max_tokens <= 0
                    else f". Raise --max-tokens (now {max_tokens}, 0 = no cap) "
                    "or try --no-thinking."
                )
            )
        raise SystemExit(2)
    if result.finish_reason == "length":
        click.echo(
            "WARNING: generation hit the token limit; the Lean block may be "
            "truncated. Consider a larger --max-tokens."
        )
    if result.unterminated_fence:
        click.echo(
            "WARNING: the ```lean fence was opened but never closed; graded "
            "everything after it."
        )
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


# --- batch runs (pilot studies) ---------------------------------------------


def _csv(value: str | None) -> list[str] | None:
    if value is None or value.strip().lower() in ("", "all"):
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def _generation_options(f):
    """Options that define a run's GenerationConfig (shared by `batch` and
    `preflight`, so preflight checks the settings the run will use)."""
    options = [
        click.option("--model", required=True,
                     help="Must equal vLLM's --served-model-name."),
        click.option("--items", default="all", show_default=True,
                     help="Comma-separated item ids, or 'all'."),
        click.option("--conditions", default="no_nl_proof,with_nl_proof", show_default=True,
                     help="Comma-separated: no_nl_proof (A1), with_nl_proof (A2)."),
        click.option("--temperature", type=float, default=0.6, show_default=True),
        click.option("--top-p", type=float, default=0.95, show_default=True),
        click.option("--top-k", type=int, default=20, show_default=True,
                     help="vLLM extension; -1 = disabled."),
        click.option("--max-tokens", type=int, default=32768, show_default=True,
                     help="Per-sample completion budget, thinking included. "
                     "0 = uncapped (up to the context window)."),
        click.option("--thinking/--no-thinking", "thinking", default=None,
                     help="chat_template_kwargs.enable_thinking. Default: server default."),
        click.option("--core-in-context/--no-core-in-context", default=True,
                     show_default=True,
                     help="Put the source of the item's PhysProofBench.Core modules in "
                     "the prompt (docs/PROMPTS.md {core_source}). Without it the model "
                     "never sees what Core definitions mean."),
        click.option("--seed", type=int, default=0, show_default=True,
                     help="Base seed; each sample gets a stable derived seed."),
        click.option("--items-dir", type=click.Path(exists=True, path_type=Path),
                     default=Path("items"), show_default=True),
        click.option("--lean-project", type=click.Path(exists=True, path_type=Path),
                     default=Path("lean"), show_default=True),
    ]
    for option in reversed(options):
        f = option(f)
    return f


def _build_config_and_plan(model, items, conditions, temperature, top_p, top_k,
                           max_tokens, thinking, core_in_context, seed, items_dir,
                           lean_project, samples):
    from .batch import CONDITIONS, GenerationConfig, build_plan, resolve_items

    conds = _csv(conditions) or list(CONDITIONS)
    bad = [c for c in conds if c not in CONDITIONS]
    if bad:
        raise click.BadParameter(f"unknown conditions {bad}; choose from {CONDITIONS}")
    config = GenerationConfig(
        model=model,
        temperature=temperature,
        top_p=top_p,
        top_k=None if top_k is not None and top_k < 0 else top_k,
        max_tokens=max_tokens if max_tokens > 0 else None,
        enable_thinking=thinking,
        core_in_context=core_in_context,
        seed=seed,
    )
    plan = build_plan(
        config=config,
        item_ids=resolve_items(items_dir, _csv(items)),
        conditions=conds,
        samples=samples,
        items_dir=items_dir,
        lean_project_dir=lean_project,
    )
    return config, plan


def _print_plan(plan, samples: int) -> None:
    cells = len(plan.prompts)
    click.echo(f"plan: {cells} item x condition cells x {samples} samples = "
               f"{len(plan.tasks)} generations")
    for item_id, cond, reason in plan.skipped:
        click.echo(f"  skip {item_id} {cond}: {reason}")
    longest = max((len(p.text) for p in plan.prompts.values()), default=0)
    click.echo(f"  longest prompt: {longest} chars")


@main.command()
@_generation_options
@click.option("--samples", "-k", type=int, default=4, show_default=True,
              help="Only used to size the plan shown.")
def preflight(model, items, conditions, temperature, top_p, top_k, max_tokens, thinking,
              core_in_context, seed, items_dir, lean_project, samples):
    """Generation side (GPU node): check the model server before `generate`.

    Server reachable, --model served, one test request round-trips, and the
    longest prompt plus --max-tokens fits the context window. Needs no Lean.
    `generate` re-runs the fast part of this itself before sending anything;
    the grading side has its own check, `lean-check`.
    """
    from .preflight import check_context_budget, check_endpoint

    config, plan = _build_config_and_plan(
        model, items, conditions, temperature, top_p, top_k, max_tokens, thinking,
        core_in_context, seed, items_dir, lean_project, samples)
    _print_plan(plan, samples)
    checks, max_len = check_endpoint(model, on_check=lambda c: _echo_checks([c]))
    if max_len is not None or all(c.ok for c in checks):
        longest = max((len(p.text) for p in plan.prompts.values()), default=0)
        budget = check_context_budget(longest, config.max_tokens, max_len)
        checks.append(budget)
        _echo_checks([budget])
    raise SystemExit(0 if all(c.ok for c in checks) else 1)


def _echo_checks(checks) -> None:
    for c in checks:
        mark = "OK  " if c.ok and not c.warning else ("WARN" if c.ok else "FAIL")
        click.echo(f"[{mark}] {c.name}: {c.detail}")


@main.command()
@_generation_options
@click.option("--run-dir", required=True, type=click.Path(path_type=Path),
              help="Run directory; re-running with the same one resumes it.")
@click.option("--samples", "-k", type=int, default=4, show_default=True,
              help="Samples per item x condition (pass@k).")
@click.option("--concurrency", type=int, default=16, show_default=True,
              help="Concurrent requests to the server (vLLM batches them).")
@click.option("--request-timeout", type=float, default=7200.0, show_default=True,
              help="Client-side seconds per request; 0 = none.")
@click.option("--max-consecutive-errors", type=int, default=5, show_default=True,
              help="Stop sending requests after this many failures in a row.")
@click.option("--dry-run", is_flag=True,
              help="Render and save prompts, print the plan, call nothing.")
def generate(model, items, conditions, temperature, top_p, top_k, max_tokens, thinking,
             core_in_context, seed, items_dir, lean_project, run_dir, samples,
             concurrency, request_timeout, max_consecutive_errors, dry_run):
    """Generation side (GPU node): sample completions for many items.

    Calls the model only -- never Lean. Each sample is saved as it finishes;
    re-run the identical command to resume after an interruption or a server
    failure. Grade with `grade-run`, on any machine with Lean (it can follow
    this run while it is still generating).
    """
    from .batch import check_resume_compatible, generate_run
    from .preflight import check_context_budget, check_endpoint

    config, plan = _build_config_and_plan(
        model, items, conditions, temperature, top_p, top_k, max_tokens, thinking,
        core_in_context, seed, items_dir, lean_project, samples)
    _print_plan(plan, samples)
    if dry_run:
        for (item_id, cond), prompt in plan.prompts.items():
            path = run_dir / "prompts" / f"{item_id}__{cond}.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(prompt.text, encoding="utf-8")
        click.echo(f"dry run: prompts written to {run_dir / 'prompts'}; nothing sent.")
        return
    try:
        check_resume_compatible(run_dir, config)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    checks, max_len = check_endpoint(model, on_check=lambda c: _echo_checks([c]))
    if all(c.ok for c in checks):
        longest = max((len(p.text) for p in plan.prompts.values()), default=0)
        budget = check_context_budget(longest, config.max_tokens, max_len)
        checks.append(budget)
        _echo_checks([budget])
    if not all(c.ok for c in checks):
        raise click.ClickException("preflight failed; nothing sent.")
    stats = generate_run(
        config=config, plan=plan, run_dir=run_dir, concurrency=concurrency,
        request_timeout=request_timeout or None,
        max_consecutive_errors=max_consecutive_errors,
        log=lambda s: click.echo(s),
    )
    click.echo(f"next: physproofbench grade-run --run-dir {run_dir}  (on a machine with Lean)")
    raise SystemExit(1 if stats.aborted else 0)


def _grading_options(f):
    options = [
        click.option("--items-dir", type=click.Path(exists=True, path_type=Path),
                     default=Path("items"), show_default=True),
        click.option("--lean-project", type=click.Path(exists=True, path_type=Path),
                     default=Path("lean"), show_default=True),
        click.option("--compile-timeout", type=float, default=300.0, show_default=True),
        click.option("--memory-cap-gb", type=float, default=32.0, show_default=True,
                     help="Virtual-memory cap per Lean compile (Linux only); 0 = none."),
    ]
    for option in reversed(options):
        f = option(f)
    return f


@main.command("lean-check")
@_grading_options
def lean_check(items_dir, lean_project, compile_timeout, memory_cap_gb):
    """Grading side (CPU node): check Lean before `grade-run`.

    Lake environment, Mathlib's umbrella .olean, an up-to-date
    PhysProofBench build, then grades a trivially correct `import Mathlib`
    submission through the real sandbox and memory cap, reporting how long
    one compile takes. Needs no model server.
    """
    from .preflight import check_lean

    checks = check_lean(lean_project, memory_cap_bytes=int(memory_cap_gb * _GiB) or None,
                        compile_timeout=compile_timeout)
    _echo_checks(checks)
    raise SystemExit(0 if all(c.ok for c in checks) else 1)


@main.command("grade-run")
@click.option("--run-dir", required=True, type=click.Path(path_type=Path),
              help="With --follow it may not exist yet; grading waits for `generate`.")
@_grading_options
@click.option("--grade-workers", type=int, default=2, show_default=True,
              help="Parallel Lean compiles (each importing Mathlib needs several GB).")
@click.option("--follow", is_flag=True,
              help="Keep grading new samples while `generate` is still running on "
              "this run (e.g. on another node over a shared filesystem).")
@click.option("--poll-interval", type=float, default=30.0, show_default=True,
              help="Seconds between checks for new completions with --follow.")
@click.option("--regrade-timeouts", is_flag=True,
              help="Also re-grade samples whose compile timed out (e.g. with a "
              "larger --compile-timeout).")
def grade_run(run_dir, items_dir, lean_project, compile_timeout, memory_cap_gb,
              grade_workers, follow, poll_interval, regrade_timeouts):
    """Grading side (CPU node): grade a run's stored completions.

    Never calls the model. Grades every sample without a current grade and
    writes <run-dir>/summary.md. Safe to re-run: finished grades are kept,
    and samples are re-graded only if their grade is missing, stale (a
    newer grading version) or a grader error.
    """
    from .batch import grade_run as _grade_run
    from .preflight import check_lean_env
    from .report import write_report

    if not follow and not (run_dir / "plan.json").exists():
        raise click.ClickException(
            f"{run_dir} has no plan.json: not a run written by `physproofbench "
            "generate` (or generation hasn't started; use --follow to wait for it).")

    checks = check_lean_env(lean_project)
    if not all(c.ok for c in checks):
        _echo_checks(checks)
        raise click.ClickException(
            "Lean environment incomplete; grading now would record every sample as "
            "compile_fail. Fix the above (see `physproofbench lean-check`).")
    stats = _grade_run(
        run_dir=run_dir, items_dir=items_dir, lean_project_dir=lean_project,
        grade_workers=grade_workers, compile_timeout=compile_timeout,
        memory_cap_bytes=int(memory_cap_gb * _GiB) or None,
        regrade_timeouts=regrade_timeouts, follow=follow, poll_interval=poll_interval,
        log=lambda s: click.echo(s),
    )
    click.echo(write_report(run_dir, items_dir))
    raise SystemExit(1 if stats.gold_mismatch else 0)


@main.command()
@click.option("--run-dir", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--items-dir", type=click.Path(exists=True, path_type=Path),
              default=Path("items"), show_default=True)
def report(run_dir, items_dir):
    """Rebuild <run-dir>/summary.{md,json} from stored results (no model, no Lean)."""
    from .report import write_report

    click.echo(write_report(run_dir, items_dir))
