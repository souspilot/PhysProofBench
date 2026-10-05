"""Compiler-feedback repair rounds (generation side; never runs Lean).

A repair run is a run directory derived from a graded source run. Round 0 of
each sample is the source's answer and grade; each failed sample then gets up
to `rounds` more attempts. In a round the model sees the original prompt, its
latest answer (the final answer only -- chat templates drop earlier
reasoning), and a feedback message built from that answer's grade: Lean's
errors with line numbers and goal states, the submitted file numbered, or the
gate/audit failure explained. Only the latest attempt is shown, not the whole
history, so prompts stay bounded.

Grading stays with `grade-run`, so the two sides can run on different nodes
and pipeline per sample:

    GPU node:  physproofbench repair --from <graded run> --run-dir R --follow
    CPU node:  physproofbench grade-run --run-dir R --follow

`repair` starts a sample's next round as soon as its current attempt has a
failing grade; `grade-run` grades each new attempt as it lands. A sample
stops at its first pass, or after `rounds` repairs. Each round's generation
follows the same thinking-budget protocol as `generate` + `force-answer`:
up to `max_tokens` for thinking and answer, and if that runs out mid-thought,
a forced answer of up to `answer_tokens`.

Layout per sample (on top of batch.py's):

    completion.json   latest attempt; `repair_round` = r (0 = from source)
    attempts/<r>/     attempt r archived when round r+1 starts:
                      completion.json, candidate.lean, grade.json,
                      reasoning.txt, forced.json, feedback.txt (the feedback
                      that round r+1 was given)

Results are "pass within r repair rounds" -- a different metric from one-shot
pass@k, reported separately by report.py.
"""

from __future__ import annotations

import os
import re
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from .batch import (
    FORCE_ANSWER_PHRASE,
    GENERATING,
    GenerationConfig,
    Plan,
    SampleTask,
    _atomic_write,
    _grade_is_current,
    _read_json,
    _set_status,
    _sha,
    _write_json,
    _write_plan,
    read_plan,
    sample_seed,
    split_thinking,
)
from .extract import extract_lean
from .models.openai_client import Completion, complete, complete_continuation, get_client
from .render import template_hash

# Bump when the feedback text changes: it is part of the protocol.
FEEDBACK_VERSION = "fb-v1"

MAX_ERRORS_SHOWN = 12
MAX_ERROR_CHARS = 1500
MAX_FEEDBACK_ERROR_CHARS = 9000

_DIAG = re.compile(
    r"^(?P<path>[^\n]*?):(?P<line>\d+):(?P<col>\d+): (?P<kind>error|warning)"
    r"(?:\((?P<code>[\w.]+)\))?: ?",
    re.MULTILINE,
)
_AXIOMS_LINE = re.compile(r"^'[^'\n]*' (?:depends on axioms|does not depend on any axioms).*$",
                          re.MULTILINE)

GATE_EXPLANATIONS = {
    "gate: statement_edited": (
        "The text before `:= by` no longer matches the given statement. Keep the "
        "imports, `open` lines and theorem statement exactly as given (dropping "
        "comments/docstrings and adding `import Mathlib...` lines is fine). Do not add "
        "declarations before the theorem: put helper lemmas inside the proof with `have`."
    ),
    "gate: sorry_present": "The file contains `sorry`. Give a complete proof.",
    "gate: admit_present": "The file contains `admit`. Give a complete proof.",
    "gate: stop_present": "The file contains `stop`. Give a complete proof.",
    "gate: axiom_declared": "The file declares an `axiom`, which is not allowed.",
}


@dataclass
class RepairConfig:
    rounds: int = 3
    max_tokens: int = 16384
    answer_tokens: int = 16384
    feedback_version: str = FEEDBACK_VERSION
    history: str = "latest_attempt_only"


def compiler_errors(output: str) -> list[tuple[int, int, str]]:
    """(line, col, message) for each `error` diagnostic in Lean's output; the
    message keeps its following lines (e.g. the goal state)."""
    matches = list(_DIAG.finditer(output))
    errors = []
    for i, m in enumerate(matches):
        if m.group("kind") != "error":
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(output)
        body = _AXIOMS_LINE.sub("", output[m.end():end]).strip()
        if m.group("code"):
            body = f"[{m.group('code')}] {body}"
        errors.append((int(m.group("line")), int(m.group("col")), body))
    return errors


def _numbered(text: str) -> str:
    lines = text.rstrip("\n").split("\n")
    width = len(str(len(lines)))
    return "\n".join(f"{i + 1:>{width}} | {line}" for i, line in enumerate(lines))


def build_feedback(grade: dict, candidate: str) -> str:
    """The user message for a repair round, from the latest attempt's grade."""
    verdict = grade.get("verdict")
    parts = ["Your previous answer was checked against the Lean 4 / Mathlib version "
             "used by this benchmark and was not accepted."]
    if verdict == "no_output" or not candidate.strip():
        parts.append("Your reply contained no Lean code.")
    elif verdict == "gate_fail":
        reasons = grade.get("gate_failures") or []
        parts.append("It was rejected before compiling:")
        parts += [f"- {GATE_EXPLANATIONS.get(r, r)}" for r in reasons]
    elif verdict == "audit_fail":
        parts.append(f"It compiled, but its axioms were {grade.get('axioms')}; only propext, "
                     "Classical.choice and Quot.sound are allowed (no `sorry`).")
    elif verdict == "compile_fail":
        if grade.get("compile_timed_out"):
            parts.append("Compilation timed out. Avoid expensive automation "
                         "(large `simp`/`nlinarith`/`decide` calls).")
        errors = compiler_errors(grade.get("compiler_output") or "")
        if errors:
            shown, budget = [], MAX_FEEDBACK_ERROR_CHARS
            for line, col, msg in errors[:MAX_ERRORS_SHOWN]:
                entry = f"line {line}, column {col}:\n{msg[:MAX_ERROR_CHARS]}"
                if len(entry) > budget:
                    break
                shown.append(entry)
                budget -= len(entry)
            parts.append(f"Lean reported {len(errors)} error(s); the first {len(shown)}:")
            parts += shown
        elif not grade.get("compile_timed_out"):
            out = (grade.get("compiler_output") or "").strip()
            parts.append("Lean failed with:\n" + out[:MAX_FEEDBACK_ERROR_CHARS])
    if candidate.strip():
        parts.append("The file that was checked, with line numbers:\n```lean\n"
                     + _numbered(candidate) + "\n```")
    parts.append("Fix the proof. Reply with a single ```lean fenced code block containing "
                 "the complete corrected file (imports through the closed proof), keeping "
                 "the theorem statement exactly as given. No commentary outside the code "
                 "block.")
    return "\n\n".join(parts)


# --- run setup -------------------------------------------------------------------

_SAMPLE_FILES = ("completion.json", "candidate.lean", "grade.json", "reasoning.txt",
                 "forced.json")


def init_repair_run(
    *, source_dir: Path, run_dir: Path, rcfg: RepairConfig,
    items: list[str] | None = None, samples: int | None = None,
) -> tuple[GenerationConfig, list[SampleTask]]:
    src_stored = _read_json(source_dir / "config.json")
    if src_stored is None:
        raise FileNotFoundError(f"{source_dir / 'config.json'} not found")
    config = GenerationConfig(**src_stored["generation"])
    origin = {"from_run": str(source_dir), **asdict(rcfg)}
    stored = _read_json(run_dir / "config.json")
    if stored is not None and stored.get("repair") != origin:
        raise ValueError(f"{run_dir} is a repair run with settings {stored.get('repair')}; "
                         f"refusing to continue it with {origin}. Use a new --run-dir.")
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(run_dir / "config.json", {
        **{k: v for k, v in src_stored.items() if k != "repair"},
        "generation": asdict(config), "repair": origin,
    })
    src_tasks, gold_shas = read_plan(source_dir)
    tasks = [t for t in src_tasks
             if (not items or t.item_id in items) and (samples is None or t.index < samples)]
    _set_status(run_dir, GENERATING, planned=len(tasks))  # before plan.json (batch.generate_run)
    _write_plan(run_dir, Plan(tasks=tasks, prompts={}, metas={}, gold_shas={
        i: s for i, s in gold_shas.items() if any(t.item_id == i for t in tasks)}))
    for item_id, cond in {(t.item_id, t.condition) for t in tasks}:
        name = f"{item_id}__{cond}.txt"
        if (source_dir / "prompts" / name).exists():
            _atomic_write(run_dir / "prompts" / name,
                          (source_dir / "prompts" / name).read_text(encoding="utf-8"))
    for task in tasks:
        dst = task.dir(run_dir)
        if (dst / "completion.json").exists():
            continue  # already initialized (resume)
        src = task.dir(source_dir)
        if not (src / "completion.json").exists():
            continue
        for name in _SAMPLE_FILES:
            if (src / name).exists():
                _atomic_write(dst / name, (src / name).read_text(encoding="utf-8"))
        record = _read_json(dst / "completion.json")
        record["repair_round"] = 0
        _write_json(dst / "completion.json", record)
    return config, tasks


def sample_state(task_dir: Path, rounds: int) -> str:
    """'missing' | 'awaiting_grade' | 'passed' | 'exhausted' | 'needs_repair'."""
    record = _read_json(task_dir / "completion.json")
    if record is None:
        return "missing"
    if not _grade_is_current(task_dir):
        return "awaiting_grade"
    grade = _read_json(task_dir / "grade.json") or {}
    if grade.get("verdict") == "pass":
        return "passed"
    if record.get("repair_round", 0) >= rounds:
        return "exhausted"
    return "needs_repair"


# --- the round driver ----------------------------------------------------------------


@dataclass
class RepairStats:
    attempts: int = 0
    errors: int = 0
    aborted: bool = False
    states: dict = field(default_factory=dict)


def repair_run(
    *,
    source_dir: Path,
    run_dir: Path,
    rcfg: RepairConfig,
    concurrency: int = 12,
    request_timeout: float | None = None,
    follow: bool = True,
    poll_interval: float = 30.0,
    max_consecutive_errors: int = 5,
    items: list[str] | None = None,
    samples: int | None = None,
    log: Callable[[str], None] = print,
    chat_fn: Callable[..., Completion] = complete,
    continue_fn: Callable[..., Completion] = complete_continuation,
) -> RepairStats:
    """Run repair rounds until every sample has passed or used `rounds`
    repairs. With `follow`, wait for `grade-run` to grade each new attempt;
    without it, do one pass over samples that currently need a repair and
    return."""
    config, tasks = init_repair_run(source_dir=source_dir, run_dir=run_dir, rcfg=rcfg,
                                    items=items, samples=samples)
    stats = RepairStats()
    lock = threading.Lock()
    abort = threading.Event()
    consecutive = 0
    real_client = chat_fn is complete or continue_fn is complete_continuation
    client = get_client(request_timeout) if real_client else None

    def attempt(task: SampleTask) -> bool:
        """True iff a new attempt was written."""
        nonlocal consecutive
        if abort.is_set():
            return False
        d = task.dir(run_dir)
        record = _read_json(d / "completion.json")
        grade = _read_json(d / "grade.json")
        r = record.get("repair_round", 0)
        prompt_path = run_dir / "prompts" / f"{task.item_id}__{task.condition}.txt"
        prompt = prompt_path.read_text(encoding="utf-8")
        if template_hash(prompt) != record.get("prompt_hash"):
            log(f"[repair] SKIPPING {task.item_id} {task.condition} #{task.index}: stored "
                "prompt doesn't match the sample's")
            return False
        candidate = (d / "candidate.lean").read_text(encoding="utf-8") \
            if (d / "candidate.lean").exists() else ""
        feedback = build_feedback(grade, candidate)
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": record.get("text") or "(no answer)"},
            {"role": "user", "content": feedback},
        ]
        seed = sample_seed(config.seed, task) ^ (1000 + r + 1)
        common = dict(model=config.model, temperature=config.temperature,
                      top_p=config.top_p, top_k=config.top_k, timeout=request_timeout,
                      client=client)
        forced = None
        try:
            result = chat_fn("", messages=messages, max_tokens=rcfg.max_tokens,
                             enable_thinking=config.enable_thinking, seed=seed, **common)
            reasoning, answer = result.reasoning or "", result.text
            if result.finish_reason == "length" and not answer.strip() and reasoning:
                forced = continue_fn(
                    None, "<think>\n" + reasoning.rstrip() + FORCE_ANSWER_PHRASE,
                    messages=messages, max_tokens=rcfg.answer_tokens,
                    enable_thinking=config.enable_thinking, seed=seed ^ 1, **common)
                answer = split_thinking(forced.text)[1] if "</think>" in forced.text \
                    else forced.text
        except Exception as exc:  # noqa: BLE001 -- retried on the next pass
            _write_json(d / "repair_error.json",
                        {"error": f"{type(exc).__name__}: {exc}", "round": r + 1,
                         "time": time.time()})
            with lock:
                stats.errors += 1
                consecutive += 1
                log(f"[repair] {task.item_id} {task.condition} #{task.index} round {r + 1}: "
                    f"ERROR {type(exc).__name__}: {exc}")
                if consecutive >= max_consecutive_errors and not abort.is_set():
                    abort.set()
                    stats.aborted = True
                    log("[repair] too many consecutive failures; stopping. Re-run the "
                        "same command to resume.")
            return False

        # Archive attempt r, then write attempt r+1 (completion.json last, so
        # a following grader only ever sees a complete attempt).
        archive = d / "attempts" / str(r)
        for name in _SAMPLE_FILES:
            if (d / name).exists():
                _atomic_write(archive / name, (d / name).read_text(encoding="utf-8"))
        _atomic_write(archive / "feedback.txt", feedback)
        (d / "forced.json").unlink(missing_ok=True)
        if reasoning:
            _atomic_write(d / "reasoning.txt", reasoning)
        else:
            (d / "reasoning.txt").unlink(missing_ok=True)
        if forced is not None:
            _write_json(d / "forced.json", {
                "generated": forced.text, "finish_reason": forced.finish_reason,
                "max_tokens_sent": forced.max_tokens_sent,
                "completion_tokens": forced.completion_tokens,
                "elapsed_s": forced.elapsed_s,
            })
        extraction = extract_lean(answer)
        _atomic_write(d / "candidate.lean", extraction.lean)
        _write_json(d / "completion.json", {
            "item_id": task.item_id, "condition": task.condition, "index": task.index,
            "prompt_hash": record.get("prompt_hash"),
            "repair_round": r + 1,
            "seed": seed,
            "served_model": result.model,
            "text": answer,
            "finish_reason": result.finish_reason,
            "had_reasoning": bool(reasoning),
            "reasoning_chars": len(reasoning),
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "elapsed_s": result.elapsed_s,
            "forced_answer": forced is not None,
            "forced_finish_reason": forced.finish_reason if forced else None,
            "forced_completion_tokens": forced.completion_tokens if forced else None,
            "used_extraction_fallback": extraction.used_fallback,
            "unterminated_fence": extraction.unterminated_fence,
            "candidate_sha": _sha(extraction.lean),
            "feedback_sha": _sha(feedback),
        })
        (d / "repair_error.json").unlink(missing_ok=True)
        with lock:
            consecutive = 0
            stats.attempts += 1
            log(f"[repair] {task.item_id} {task.condition} #{task.index} round {r + 1}: "
                f"finish={result.finish_reason}{' +forced' if forced else ''} "
                f"lean={'yes' if not extraction.used_fallback else 'no'} "
                f"({grade.get('verdict')} before)")
        return True

    in_flight: dict[SampleTask, Future] = {}
    # Per-sample give-ups within this call (prompt mismatch, repeated request
    # errors): not resubmitted every poll; a later call retries them.
    gave_up: dict[SampleTask, int] = {}
    last_note = 0.0
    try:
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
            while True:
                states = {t: sample_state(t.dir(run_dir), rcfg.rounds) for t in tasks}
                stats.states = {s: sum(v == s for v in states.values())
                                for s in set(states.values())}
                for t, s in states.items():
                    if (s == "needs_repair" and t not in in_flight and not abort.is_set()
                            and gave_up.get(t, 0) < 2):
                        in_flight[t] = pool.submit(attempt, t)
                for t, f in list(in_flight.items()):
                    if f.done():
                        if not f.result():
                            gave_up[t] = gave_up.get(t, 0) + 1
                        del in_flight[t]
                # Re-read: attempts may have finished and been graded meanwhile.
                states = {t: sample_state(t.dir(run_dir), rcfg.rounds) for t in tasks}
                stats.states = {s: sum(v == s for v in states.values())
                                for s in set(states.values())}
                pending = sum(1 for t, s in states.items() if s == "needs_repair"
                              and gave_up.get(t, 0) < 2 and not abort.is_set())
                stuck = sum(1 for t, s in states.items()
                            if s == "needs_repair" and gave_up.get(t, 0) >= 2)
                waiting = stats.states.get("awaiting_grade", 0)
                active = bool(in_flight) or bool(pending) or (
                    follow and waiting and not abort.is_set())
                if stuck and not active:
                    log(f"[repair] {stuck} sample(s) failed twice this call (see their "
                        "repair_error.json); re-run to retry them.")
                _set_status(run_dir, GENERATING if active else
                            ("aborted" if abort.is_set() else "finished"),
                            planned=len(tasks), states=stats.states)
                if not active:
                    break
                if not follow and not in_flight:
                    break  # one pass: everything that needed a round has had one
                if time.monotonic() - last_note > 600:
                    log(f"[repair] states: {stats.states}"
                        + (" (waiting for `grade-run --follow` on these)" if waiting else ""))
                    last_note = time.monotonic()
                time.sleep(min(poll_interval, 5.0) if (in_flight or pending) else poll_interval)
    except KeyboardInterrupt:
        _set_status(run_dir, "interrupted")
        log("[repair] interrupted; finished attempts are saved. Re-run to resume.")
        os._exit(130)
    log(f"[repair] done: {stats.attempts} attempts this call; states {stats.states}")
    return stats


def attempt_history(task_dir: Path) -> list[str]:
    """Verdicts of attempts 0..r in order (current attempt last, if graded)."""
    verdicts = []
    attempts = task_dir / "attempts"
    if attempts.exists():
        for sub in sorted(attempts.iterdir(), key=lambda p: int(p.name)):
            verdicts.append((_read_json(sub / "grade.json") or {}).get("verdict"))
    if _grade_is_current(task_dir):
        verdicts.append((_read_json(task_dir / "grade.json") or {}).get("verdict"))
    return verdicts

