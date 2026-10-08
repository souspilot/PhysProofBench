"""Thinking-budget curves (generation side; never runs Lean).

A model that thinks at length is not worse at proving than one that thinks
briefly, but a single fixed token cap makes it look so: it is cut off and
judged on a forced answer. Instead, the benchmark reports pass rate as a
function of the thinking budget, measured on the *same* traces:

    physproofbench budget-curve --from runs/R --budgets 4096,8192,16384,32768

creates one derived run per budget, `runs/R@think<B>`. For each sample:

- if its reasoning ended on its own within B thinking tokens (the model
  closed `</think>` and answered), that natural answer is kept, since the
  same sample under a B-token budget would have ended identically;
- otherwise its reasoning is cut at exactly B tokens (counted with the
  server's tokenizer) and an answer is forced with `FORCE_ANSWER_PHRASE`;
- if the trace is shorter than B but was itself cut off (e.g. a 32k-budget
  sample asked about B = 64k), the sample can't be evaluated at B and is
  skipped. Use `extend` first to grow the traces.

Each derived run is graded with `grade-run` like any other, and
`physproofbench curve runs/R@think*` tabulates the pass rates.
"""

from __future__ import annotations

import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .batch import (
    FORCE_ANSWER_PHRASE,
    GENERATING,
    GenerationConfig,
    Plan,
    _atomic_write,
    _read_json,
    _run_pool,
    _set_status,
    _sha,
    _truncated_while_thinking,
    _write_json,
    _write_plan,
    read_plan,
    sample_seed,
    split_thinking,
)
from .extract import extract_lean
from .models.openai_client import (
    Completion,
    complete_continuation,
    count_and_truncate_tokens,
    get_client,
)
from .render import template_hash


@dataclass
class CurveStats:
    budget: int
    natural: int = 0
    forced: int = 0
    skipped_short_trace: int = 0
    errors: int = 0


def budget_run_dir(source_dir: Path, budget: int) -> Path:
    return source_dir.parent / f"{source_dir.name}@think{budget}"


def budget_curve(
    *,
    source_dir: Path,
    budgets: list[int],
    answer_tokens: int = 16384,
    concurrency: int = 16,
    request_timeout: float | None = None,
    items: list[str] | None = None,
    log: Callable[[str], None] = print,
    continue_fn: Callable[..., Completion] = complete_continuation,
    count_fn: Callable[..., tuple[int, str]] = count_and_truncate_tokens,
) -> list[CurveStats]:
    src_stored = _read_json(source_dir / "config.json")
    if src_stored is None:
        raise FileNotFoundError(f"{source_dir / 'config.json'} not found")
    config = GenerationConfig(**src_stored["generation"])
    tasks, gold_shas = read_plan(source_dir)
    tasks = [t for t in tasks if not items or t.item_id in items]

    # Token count of each sample's reasoning (once, shared by all budgets).
    lengths: dict = {}
    for task in tasks:
        d = task.dir(source_dir)
        record = _read_json(d / "completion.json")
        if record is None or not (d / "reasoning.txt").exists():
            continue
        n, _ = count_fn((d / "reasoning.txt").read_text(encoding="utf-8"), 1 << 60,
                        model=config.model)  # count only, no truncation
        lengths[task] = (n, record)
    client = get_client(request_timeout) if continue_fn is complete_continuation else None

    results = []
    for budget in sorted(budgets):
        run_dir = budget_run_dir(source_dir, budget)
        settings = {"from_run": str(source_dir), "thinking_budget": budget,
                    "answer_tokens": answer_tokens, "phrase": FORCE_ANSWER_PHRASE}
        stored = _read_json(run_dir / "config.json")
        if stored is not None and stored.get("budget_curve") != settings:
            raise ValueError(f"{run_dir} was made with {stored.get('budget_curve')}, "
                             f"not {settings}")
        run_dir.mkdir(parents=True, exist_ok=True)
        _write_json(run_dir / "config.json", {"generation": asdict(config),
                                              "budget_curve": settings})
        _set_status(run_dir, GENERATING, planned=len(tasks))
        _write_plan(run_dir, Plan(tasks=tasks, prompts={}, metas={}, gold_shas=gold_shas))
        for name in {f"{t.item_id}__{t.condition}.txt" for t in tasks}:
            if (source_dir / "prompts" / name).exists():
                _atomic_write(run_dir / "prompts" / name,
                              (source_dir / "prompts" / name).read_text(encoding="utf-8"))

        stats = CurveStats(budget=budget)
        todo = []
        for task, (n, record) in lengths.items():
            dst = task.dir(run_dir)
            if (dst / "completion.json").exists():
                continue  # done in an earlier call
            truncated = _truncated_while_thinking(record)
            if not truncated and n <= budget:
                # Ended on its own within the budget: keep the natural answer.
                for name in ("completion.json", "candidate.lean", "reasoning.txt"):
                    src = task.dir(source_dir) / name
                    if src.exists():
                        _atomic_write(dst / name, src.read_text(encoding="utf-8"))
                stats.natural += 1
            elif n < budget:
                stats.skipped_short_trace += 1
            else:
                todo.append((task, record))
        log(f"[curve] budget {budget}: {stats.natural} natural answers kept, "
            f"{len(todo)} to force, {stats.skipped_short_trace} traces too short")
        lock = threading.Lock()

        def do_force(task, record, budget=budget, run_dir=run_dir, stats=stats):
            src_dir, dst = task.dir(source_dir), task.dir(run_dir)
            prompt = (source_dir / "prompts" /
                      f"{task.item_id}__{task.condition}.txt").read_text(encoding="utf-8")
            if template_hash(prompt) != record.get("prompt_hash"):
                log(f"[curve] SKIPPING {task.item_id} {task.condition} #{task.index}: "
                    "stored prompt doesn't match")
                return
            reasoning = (src_dir / "reasoning.txt").read_text(encoding="utf-8")
            try:
                _, cut = count_fn(reasoning, budget, model=config.model)
                result = continue_fn(
                    prompt, "<think>\n" + cut.rstrip() + FORCE_ANSWER_PHRASE,
                    model=config.model, max_tokens=answer_tokens,
                    enable_thinking=config.enable_thinking, temperature=config.temperature,
                    top_p=config.top_p, top_k=config.top_k,
                    seed=sample_seed(config.seed, task) ^ (budget * 7919),
                    timeout=request_timeout, client=client,
                )
            except Exception as exc:  # noqa: BLE001 -- retried on the next call
                _write_json(dst / "curve_error.json",
                            {"error": f"{type(exc).__name__}: {exc}", "time": time.time()})
                with lock:
                    stats.errors += 1
                log(f"[curve] {task.item_id} {task.condition} #{task.index} @{budget}: "
                    f"ERROR {type(exc).__name__}: {exc}")
                return
            answer = split_thinking(result.text)[1] if "</think>" in result.text \
                else result.text
            extraction = extract_lean(answer)
            _atomic_write(dst / "reasoning.txt", cut)
            _atomic_write(dst / "candidate.lean", extraction.lean)
            _write_json(dst / "completion.json", {
                **{k: v for k, v in record.items() if not k.startswith(("forced", "extended"))},
                "text": answer,
                "finish_reason": "length",
                "thinking_budget": budget,
                "forced_answer": True,
                "forced_finish_reason": result.finish_reason,
                "forced_completion_tokens": result.completion_tokens,
                "reasoning_chars": len(cut),
                "used_extraction_fallback": extraction.used_fallback,
                "unterminated_fence": extraction.unterminated_fence,
                "candidate_sha": _sha(extraction.lean),
            })
            (dst / "curve_error.json").unlink(missing_ok=True)
            with lock:
                stats.forced += 1
            log(f"[curve] {task.item_id} {task.condition} #{task.index} @{budget}: "
                f"forced, finish={result.finish_reason} tokens={result.completion_tokens}")

        _run_pool(todo, do_force, concurrency, "curve", log)
        _set_status(run_dir, "finished", planned=len(tasks))
        results.append(stats)
    return results


def curve_table(run_dirs: list[Path], items_dir: Path) -> str:
    """Markdown table: pass@1 / pass@k per thinking budget and condition."""
    from .report import summarize

    rows = []
    for d in run_dirs:
        cfg = (_read_json(d / "config.json") or {}).get("budget_curve") or {}
        s = summarize(d, items_dir)
        for cond, agg in s["aggregates"].get("condition", {}).items():
            rows.append((cfg.get("thinking_budget", 0), cond, agg, s["ks"],
                         s["totals"]["forced_answers"], s["totals"]["samples"],
                         s["totals"]["graded"]))
    rows.sort(key=lambda r: (r[1], r[0]))
    ks = sorted({k for r in rows for k in r[3]})
    lines = ["| thinking budget | condition | items solved | "
             + " | ".join(f"pass@{k}" for k in ks) + " | forced / samples | graded |",
             "|---|---|---|" + "---|" * len(ks) + "---|---|"]
    for budget, cond, agg, _, forced, n, graded in rows:
        vals = " | ".join("–" if agg.get(f"pass@{k}") is None else f"{agg[f'pass@{k}']:.2f}"
                          for k in ks)
        lines.append(f"| {budget} | {cond} | {agg['items_solved']}/{agg['items']} | {vals} | "
                     f"{forced}/{n} | {graded} |")
    return "\n".join(lines) + "\n"
