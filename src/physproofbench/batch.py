"""Batch runs in two independent phases: generate (GPU side), grade (CPU side).

The phases share nothing but a run directory, so they can run on different
machines (e.g. a GPU node serving vLLM and a CPU node with Lean, over a
shared filesystem), at different times, or concurrently:

    <run_dir>/
      config.json                  generation settings (checked on resume)
      plan.json                    every planned sample + each item's gold hash
      status.json                  generation state: generating | finished |
                                   aborted | interrupted
      prompts/<item>__<cond>.txt   rendered prompts, for inspection
      samples/<item>/<cond>/<idx>/
        completion.json            raw text, reasoning, usage, finish_reason
        reasoning.txt              thinking trace, when the server returns one
        candidate.lean             extracted Lean
        error.json                 last failed request (retried on resume)
        grade.json                 L0-L2 verdict (grading.GradeReport.to_dict)
      summary.json / summary.md    written by report.py

`generate_run` never touches Lean; `grade_run` never calls a model. Every
file is written atomically (temp file + rename) as soon as its sample
finishes, and both phases skip work that is already done, so re-running
either one after a crash, Ctrl-C, or a dead server costs only what was in
flight. `grade_run(follow=True)` keeps polling while `status.json` says
generation is still running, grading samples as they land.

Not yet here (plan.md §8): `autoform` mode (B1/B2 need the L3 bridge), and
L2.3 statement preservation (the L0 text gate is the statement check).
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import traceback
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from .extract import extract_lean
from .grading import GRADING_VERSION, grade_submission
from .lean.sandbox import DEFAULT_MEMORY_CAP_BYTES
from .models.openai_client import (
    Completion,
    complete,
    complete_continuation,
    get_client,
)
from .render import (
    TEMPLATE_VERSION,
    gold_statement_prefix,
    load_core_source,
    render_proof_prompt,
    template_hash,
)
from .run import _extract_nl_section
from .schema import ItemMeta, load_item_meta

CONDITIONS = ("no_nl_proof", "with_nl_proof")
GENERATING = "generating"


@dataclass
class GenerationConfig:
    """Everything that changes what the model is asked or how it samples.

    Stored in `config.json`; resuming a run with a different value is refused
    (see `check_resume_compatible`), because mixing samples generated under
    different settings silently corrupts pass@k. Items, conditions and the
    sample count are *not* part of it: a run can be extended with more of
    any of them.
    """

    model: str
    temperature: float = 0.6
    top_p: float | None = 0.95
    top_k: int | None = 20
    max_tokens: int | None = 32768
    enable_thinking: bool | None = None
    core_in_context: bool = True
    seed: int = 0
    mode: str = "proof"
    template_version: str = TEMPLATE_VERSION
    # Lean project = Mathlib pin ("lean": v4.34; "lean-v4.9": Lean 4.9-era).
    # Prompts, gold statements and grading all come from this project.
    lean_project: str = "lean"


# Defaults for GenerationConfig fields added after runs already existed: a
# stored config without the key means the default, not a settings change.
_CONFIG_FIELD_DEFAULTS = {"lean_project": "lean"}


def gold_path(meta: ItemMeta, lean_project_dir: Path) -> Path:
    """The item's gold file inside `lean_project_dir` (the pin). `lean_file`
    in meta.yaml is written relative to the main pin, `lean/`."""
    rel = Path(meta.lean_file)
    if rel.parts and rel.parts[0] == "lean":
        rel = Path(*rel.parts[1:])
    return lean_project_dir / rel


def pin_info(lean_project_dir: Path) -> dict:
    """Toolchain and Mathlib revision of a Lean project, for run metadata."""
    info: dict = {"lean_project": lean_project_dir.name}
    toolchain = lean_project_dir / "lean-toolchain"
    if toolchain.exists():
        info["lean_toolchain"] = toolchain.read_text(encoding="utf-8").strip()
    manifest = _read_json(lean_project_dir / "lake-manifest.json") or {}
    for pkg in manifest.get("packages", []):
        if pkg.get("name") == "mathlib":
            info["mathlib_rev"] = pkg.get("rev")
    return info


@dataclass(frozen=True)
class SampleTask:
    item_id: str
    condition: str
    index: int

    def dir(self, run_dir: Path) -> Path:
        return run_dir / "samples" / self.item_id / self.condition / f"{self.index:03d}"


@dataclass
class PromptInfo:
    text: str
    hash: str


@dataclass
class Plan:
    tasks: list[SampleTask]
    prompts: dict[tuple[str, str], PromptInfo]
    metas: dict[str, ItemMeta]
    # sha of each item's gold Lean file, so the grading side can check it
    # grades against the same statement the model was shown.
    gold_shas: dict[str, str] = field(default_factory=dict)
    # (item_id, condition, reason) for combinations that cannot run.
    skipped: list[tuple[str, str, str]] = field(default_factory=list)


# --- small IO helpers --------------------------------------------------------


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _write_json(path: Path, data: dict) -> None:
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _set_status(run_dir: Path, state: str, **extra) -> None:
    _write_json(run_dir / "status.json", {"state": state, "updated": time.time(), **extra})


def generation_state(run_dir: Path) -> str | None:
    return (_read_json(run_dir / "status.json") or {}).get("state")


def _status_age_s(run_dir: Path) -> float:
    updated = (_read_json(run_dir / "status.json") or {}).get("updated")
    return time.time() - updated if updated else float("inf")


# --- planning ----------------------------------------------------------------


def sample_seed(base_seed: int, task: SampleTask) -> int:
    """Per-sample seed, stable across resumes and independent of scheduling
    order, so a regenerated sample is reproducible given the same server."""
    digest = hashlib.sha256(
        f"{base_seed}|{task.item_id}|{task.condition}|{task.index}".encode()
    ).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def resolve_items(items_dir: Path, selection: list[str] | None) -> list[str]:
    available = sorted(p.parent.name for p in items_dir.glob("*/meta.yaml"))
    if not selection:
        return available
    unknown = [i for i in selection if i not in available]
    if unknown:
        raise ValueError(f"unknown item ids: {unknown}")
    return selection


def build_plan(
    *,
    config: GenerationConfig,
    item_ids: list[str],
    conditions: list[str],
    samples: int,
    items_dir: Path,
    lean_project_dir: Path,
) -> Plan:
    plan = Plan(tasks=[], prompts={}, metas={})
    for item_id in item_ids:
        item_dir = items_dir / item_id
        meta = load_item_meta(item_dir / "meta.yaml")
        plan.metas[item_id] = meta
        if config.mode not in meta.modes:
            for cond in conditions:
                plan.skipped.append((item_id, cond, f"item has no {config.mode!r} mode"))
            continue
        gold_text = gold_path(meta, lean_project_dir).read_text(encoding="utf-8")
        plan.gold_shas[item_id] = _sha(gold_text)
        gold_prefix = gold_statement_prefix(gold_text)
        core_source = None
        if config.core_in_context and meta.core_deps:
            core_source = load_core_source(lean_project_dir, meta.core_deps)
        for cond in conditions:
            nl_proof = None
            if cond == "with_nl_proof":
                if meta.nl.proof is None:
                    plan.skipped.append(
                        (item_id, cond, "source gives no proof (nl.proof absent)"))
                    continue
                nl_proof = _extract_nl_section(
                    (item_dir / "nl.md").read_text(encoding="utf-8"), "proof"
                )
            text = render_proof_prompt(
                gold_statement_lean=gold_prefix,
                condition=cond,
                nl_proof=nl_proof,
                core_source=core_source,
            )
            plan.prompts[(item_id, cond)] = PromptInfo(text=text, hash=template_hash(text))
            plan.tasks.extend(SampleTask(item_id, cond, i) for i in range(samples))
    return plan


def check_resume_compatible(run_dir: Path, config: GenerationConfig) -> None:
    """Refuse to add samples to a run generated under different settings."""
    existing = _read_json(run_dir / "config.json")
    if existing is None:
        return
    stored = existing.get("generation", {})
    current = asdict(config)
    diffs = {k: (stored.get(k, _CONFIG_FIELD_DEFAULTS.get(k)), v) for k, v in current.items()
             if stored.get(k, _CONFIG_FIELD_DEFAULTS.get(k)) != v}
    if diffs:
        lines = "\n".join(f"  {k}: run has {a!r}, now {b!r}" for k, (a, b) in diffs.items())
        raise ValueError(
            f"{run_dir} was generated with different settings:\n{lines}\n"
            "Use a new --run-dir, or pass the original settings to resume."
        )


def _write_plan(run_dir: Path, plan: Plan) -> None:
    """Merge `plan` into `plan.json`: a run can be extended by later
    `generate` calls with more items, conditions or samples."""
    stored = _read_json(run_dir / "plan.json") or {"tasks": [], "gold_shas": {}}
    tasks = {(t["item_id"], t["condition"], t["index"]) for t in stored["tasks"]}
    tasks |= {(t.item_id, t.condition, t.index) for t in plan.tasks}
    _write_json(run_dir / "plan.json", {
        "tasks": [{"item_id": i, "condition": c, "index": n} for i, c, n in sorted(tasks)],
        "gold_shas": {**stored["gold_shas"], **plan.gold_shas},
    })


def read_plan(run_dir: Path) -> tuple[list[SampleTask], dict[str, str]]:
    stored = _read_json(run_dir / "plan.json")
    if stored is None:
        raise FileNotFoundError(
            f"{run_dir / 'plan.json'} not found -- is this a run directory written "
            "by `physproofbench generate`?"
        )
    tasks = [SampleTask(t["item_id"], t["condition"], t["index"]) for t in stored["tasks"]]
    return tasks, stored["gold_shas"]


# --- phase 1: generation (model only, no Lean) ---------------------------------


@dataclass
class GenerateStats:
    planned: int = 0
    to_generate: int = 0
    generated: int = 0
    errors: int = 0
    aborted: bool = False
    started: float = field(default_factory=time.monotonic)


def _completion_is_current(task_dir: Path, prompt_hash: str) -> bool:
    record = _read_json(task_dir / "completion.json")
    return record is not None and record.get("prompt_hash") == prompt_hash


def generate_run(
    *,
    config: GenerationConfig,
    plan: Plan,
    run_dir: Path,
    concurrency: int = 16,
    request_timeout: float | None = 7200.0,
    max_consecutive_errors: int = 5,
    log: Callable[[str], None] = print,
    complete_fn: Callable[..., Completion] = complete,
) -> GenerateStats:
    """Generate every sample in `plan` that has no current completion.

    A completion is current if it was generated from the identical prompt
    (same item text, condition and template). `max_consecutive_errors`
    failed requests in a row (server down, wrong model name, ...) stop new
    requests from being sent; finished samples stay on disk.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    check_resume_compatible(run_dir, config)
    # Keep other keys (e.g. `forced_answer`) when extending a run.
    _write_json(run_dir / "config.json",
                {**(_read_json(run_dir / "config.json") or {}), "generation": asdict(config),
                 "pin": pin_info(Path(config.lean_project))})
    # Mark the run as generating *before* publishing plan.json: a grader
    # following this run starts as soon as plan.json exists, and would exit
    # at once if it saw no "generating" status.
    _set_status(run_dir, GENERATING, planned=len(plan.tasks))
    _write_plan(run_dir, plan)
    for (item_id, cond), prompt in plan.prompts.items():
        _atomic_write(run_dir / "prompts" / f"{item_id}__{cond}.txt", prompt.text)

    stats = GenerateStats(planned=len(plan.tasks))
    todo = [t for t in plan.tasks
            if not _completion_is_current(t.dir(run_dir), plan.prompts[(t.item_id, t.condition)].hash)]
    stats.to_generate = len(todo)
    log(f"[generate] {stats.planned} samples planned, {len(todo)} to generate "
        f"({stats.planned - len(todo)} already done)")
    _set_status(run_dir, GENERATING, planned=stats.planned, remaining=len(todo))

    lock = threading.Lock()
    abort = threading.Event()
    consecutive_errors = 0
    # A custom complete_fn (tests) brings its own transport.
    client = get_client(request_timeout) if todo and complete_fn is complete else None

    def progress() -> str:
        mins = (time.monotonic() - stats.started) / 60
        return f"{stats.generated}/{stats.to_generate} done, {stats.errors} errors, {mins:.1f} min"

    def do_generate(task: SampleTask) -> None:
        nonlocal consecutive_errors
        if abort.is_set():
            return
        task_dir = task.dir(run_dir)
        prompt = plan.prompts[(task.item_id, task.condition)]
        seed = sample_seed(config.seed, task)
        try:
            result = complete_fn(
                prompt.text,
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                enable_thinking=config.enable_thinking,
                timeout=request_timeout,
                top_p=config.top_p,
                top_k=config.top_k,
                seed=seed,
                client=client,
            )
        except Exception as exc:  # noqa: BLE001 -- recorded, re-tried on resume
            _write_json(task_dir / "error.json",
                        {"error": f"{type(exc).__name__}: {exc}", "time": time.time()})
            with lock:
                stats.errors += 1
                consecutive_errors += 1
                log(f"[generate] {task.item_id} {task.condition} #{task.index}: "
                    f"ERROR {type(exc).__name__}: {exc}")
                if consecutive_errors >= max_consecutive_errors and not abort.is_set():
                    abort.set()
                    stats.aborted = True
                    log(f"[generate] {consecutive_errors} consecutive request failures; "
                        "not sending further requests. Fix the server and re-run the "
                        "same command to resume.")
            return

        extraction = extract_lean(result.text)
        if result.reasoning:
            _atomic_write(task_dir / "reasoning.txt", result.reasoning)
        _atomic_write(task_dir / "candidate.lean", extraction.lean)
        # completion.json last: its presence marks the sample as done, for
        # resumes and for a grader following this run.
        _write_json(task_dir / "completion.json", {
            "item_id": task.item_id,
            "condition": task.condition,
            "index": task.index,
            "prompt_hash": prompt.hash,
            "seed": seed,
            "served_model": result.model,
            "text": result.text,
            "finish_reason": result.finish_reason,
            "had_reasoning": bool(result.reasoning),
            "reasoning_chars": len(result.reasoning or ""),
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "elapsed_s": result.elapsed_s,
            "used_extraction_fallback": extraction.used_fallback,
            "unterminated_fence": extraction.unterminated_fence,
            "candidate_sha": _sha(extraction.lean),
        })
        (task_dir / "error.json").unlink(missing_ok=True)
        with lock:
            consecutive_errors = 0
            stats.generated += 1
            log(f"[generate] {task.item_id} {task.condition} #{task.index}: "
                f"finish={result.finish_reason} tokens={result.completion_tokens} "
                f"{result.elapsed_s or 0:.0f}s | {progress()}")
            _set_status(run_dir, GENERATING, planned=stats.planned,
                        remaining=stats.to_generate - stats.generated)

    try:
        if todo:
            with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
                for future in [pool.submit(do_generate, t) for t in todo]:
                    future.result()
    except KeyboardInterrupt:
        _set_status(run_dir, "interrupted")
        log("[generate] interrupted; finished samples are saved. Re-run the same "
            "command to resume.")
        # In-flight HTTP requests can't be cancelled; exit without waiting.
        os._exit(130)

    _set_status(run_dir, "aborted" if stats.aborted else "finished",
                planned=stats.planned, remaining=stats.to_generate - stats.generated)
    log(f"[generate] {'aborted' if stats.aborted else 'done'}: {progress()}")
    return stats


# --- phase 2: grading (Lean only, no model) -------------------------------------


@dataclass
class GradeStats:
    graded: int = 0
    passed: int = 0
    # Items skipped because this checkout's gold file differs from the one
    # the samples were generated against.
    gold_mismatch: list[str] = field(default_factory=list)
    started: float = field(default_factory=time.monotonic)


def _grade_is_current(task_dir: Path, regrade_timeouts: bool = False) -> bool:
    grade = _read_json(task_dir / "grade.json")
    completion = _read_json(task_dir / "completion.json")
    if grade is None or completion is None:
        return False
    if regrade_timeouts and grade.get("compile_timed_out"):
        return False
    return (
        grade.get("grading_version") == GRADING_VERSION
        and grade.get("verdict") != "grader_error"
        and grade.get("candidate_sha") == completion.get("candidate_sha")
    )


def grade_run(
    *,
    run_dir: Path,
    items_dir: Path,
    lean_project_dir: Path,
    grade_workers: int = 2,
    compile_timeout: float = 300.0,
    memory_cap_bytes: int | None = DEFAULT_MEMORY_CAP_BYTES,
    diagnose_statement_edits: bool = True,
    regrade_timeouts: bool = False,
    follow: bool = False,
    poll_interval: float = 30.0,
    stale_after: float = 3 * 3600.0,
    log: Callable[[str], None] = print,
    grade_fn: Callable[..., object] = grade_submission,
) -> GradeStats:
    """Grade every generated sample of the run that lacks a current grade.

    With `follow`, keep polling for new completions until `status.json` says
    generation is no longer running and nothing is left to grade -- so this
    can start on a CPU node as soon as `generate` starts on a GPU node.
    `generate` touches `status.json` after every sample; if it has not done
    so for `stale_after` seconds (the generating process was killed without
    a chance to record it), following stops. Each sample is attempted at
    most once per call, so a persistent `grader_error` cannot loop.
    A grade is current if it was made under this `GRADING_VERSION`, for the
    same extracted candidate, and was not a `grader_error`.
    """
    if follow and not (run_dir / "plan.json").exists():
        # The grader may be started before `generate` has written anything.
        log(f"[grade] waiting for `generate` to start writing {run_dir} ...")
        while not (run_dir / "plan.json").exists():
            time.sleep(poll_interval)
    stored_config = _read_json(run_dir / "config.json")
    if stored_config is None:
        raise FileNotFoundError(f"{run_dir / 'config.json'} not found")
    config = GenerationConfig(**stored_config["generation"])
    stats = GradeStats()
    lock = threading.Lock()
    metas: dict[str, ItemMeta] = {}

    def check_items(item_ids: set[str], gold_shas: dict[str, str]) -> None:
        for item_id in sorted(item_ids - metas.keys() - set(stats.gold_mismatch)):
            meta = load_item_meta(items_dir / item_id / "meta.yaml")
            local = _sha(gold_path(meta, lean_project_dir).read_text(encoding="utf-8"))
            if gold_shas.get(item_id) != local:
                stats.gold_mismatch.append(item_id)
                log(f"[grade] SKIPPING {item_id}: its gold Lean file in this checkout "
                    "differs from the one the samples were generated against. Put both "
                    "machines on the same commit.")
            else:
                metas[item_id] = meta

    def do_grade(task: SampleTask) -> None:
        task_dir = task.dir(run_dir)
        completion = _read_json(task_dir / "completion.json") or {}
        meta = metas[task.item_id]
        try:
            if not completion.get("text", "").strip():
                # Nothing to grade: grading "" would report a misleading
                # statement_edited gate failure (see run.py).
                record = {"verdict": "no_output", "grading_version": GRADING_VERSION}
            else:
                record = grade_fn(
                    lean_project_dir=lean_project_dir,
                    submission_path=task_dir / "candidate.lean",
                    gold_path=gold_path(meta, lean_project_dir),
                    decl_name=meta.decl_name,
                    mode=config.mode,
                    timeout=compile_timeout,
                    memory_cap_bytes=memory_cap_bytes,
                    diagnose_statement_edits=diagnose_statement_edits,
                ).to_dict()
        except Exception:  # noqa: BLE001 -- recorded, re-tried on the next run
            record = {"verdict": "grader_error", "grading_version": GRADING_VERSION,
                      "error": traceback.format_exc()}
        record["candidate_sha"] = completion.get("candidate_sha")
        _write_json(task_dir / "grade.json", record)
        with lock:
            stats.graded += 1
            stats.passed += record["verdict"] == "pass"
            mins = (time.monotonic() - stats.started) / 60
            log(f"[grade] {task.item_id} {task.condition} #{task.index}: {record['verdict']}"
                + (f" {record['gate_failures']}" if record.get("gate_failures") else "")
                + f" | {stats.graded} graded, {stats.passed} pass, {mins:.1f} min")

    in_flight: dict[SampleTask, Future] = {}
    attempted: set[SampleTask] = set()
    announced = False
    try:
        with ThreadPoolExecutor(max_workers=max(1, grade_workers)) as pool:
            while True:
                tasks, gold_shas = read_plan(run_dir)
                check_items({t.item_id for t in tasks}, gold_shas)
                ready = [
                    t for t in tasks
                    if t.item_id in metas and t not in attempted
                    and (t.dir(run_dir) / "completion.json").exists()
                    and not _grade_is_current(t.dir(run_dir), regrade_timeouts)
                ]
                if not announced:
                    done = sum((t.dir(run_dir) / "completion.json").exists() for t in tasks)
                    log(f"[grade] {len(tasks)} samples planned, {done} generated, "
                        f"{len(ready)} to grade now"
                        + (" (following generation)" if follow else ""))
                    announced = True
                for t in ready:
                    attempted.add(t)
                    in_flight[t] = pool.submit(do_grade, t)
                if not in_flight:
                    if follow and generation_state(run_dir) == GENERATING:
                        if _status_age_s(run_dir) > stale_after:
                            log(f"[grade] status.json says generating but has not been "
                                f"updated for over {stale_after / 3600:.1f} h; assuming "
                                "the generator died. Stopping.")
                            break
                        time.sleep(poll_interval)
                        continue
                    break
                # Wake when a grade finishes, or after poll_interval to look
                # for new completions.
                finished, _ = wait(list(in_flight.values()), timeout=poll_interval,
                                   return_when=FIRST_COMPLETED)
                for t, f in list(in_flight.items()):
                    if f in finished:
                        f.result()
                        del in_flight[t]
    except KeyboardInterrupt:
        log("[grade] interrupted; finished grades are saved. Re-run to resume.")
        os._exit(130)

    log(f"[grade] done: {stats.graded} graded, {stats.passed} pass "
        f"(generation state: {generation_state(run_dir)})")
    return stats


# --- phase 1b: continuing truncated reasoning (model only) --------------------
#
# Both functions below continue a sample's reasoning at the token level
# (`openai_client.complete_continuation`): chat prompt + "<think>\n" +
# reasoning so far [+ suffix], sent to the completions endpoint. Continuing a
# sampled prefix is itself a sample from the model, so an extended trace is
# as valid as one generated in one go with the larger budget.

# Qwen's documented early-exit for a thinking budget: append this to the
# truncated reasoning and let the model write its final answer. The exact
# text is part of the protocol; it is recorded in config.json.
FORCE_ANSWER_PHRASE = (
    "\n\nConsidering the limited time by the user, I have to give the solution "
    "based on the thinking directly now.\n</think>\n\n"
)

# Kept free on top of `answer_reserve` when extending: the phrase above and
# re-tokenizing the reasoning text (which need not reproduce the original
# token ids exactly) both consume a little context.
RESERVE_SLACK_TOKENS = 512


def split_thinking(generated: str) -> tuple[str, str, bool]:
    """(more reasoning, answer, closed) for raw text generated while inside
    a `<think>` block: everything before `</think>` is reasoning."""
    if "</think>" in generated:
        before, after = generated.split("</think>", 1)
        return before, after.lstrip("\n"), True
    return generated, "", False


def _truncated_while_thinking(record: dict) -> bool:
    """Ran out of budget before writing any answer (a forced answer, if
    any, doesn't count as the model's own)."""
    return (
        record.get("finish_reason") == "length"
        and bool(record.get("had_reasoning"))
        and (not record.get("text", "").strip() or bool(record.get("forced_answer")))
    )


def _needs_forced_answer(record: dict, redo_capped: bool = False) -> bool:
    """Truncated while thinking and not yet forced -- or, with
    `redo_capped`, forced but cut off by the (smaller) answer budget."""
    if not _truncated_while_thinking(record):
        return False
    if not record.get("forced_answer"):
        return True
    return redo_capped and record.get("forced_finish_reason") == "length"


def _load_prompt(run_dir: Path, task: SampleTask, record: dict) -> str | None:
    """The stored prompt for `task`, or None if it isn't the one the sample
    was generated from."""
    path = run_dir / "prompts" / f"{task.item_id}__{task.condition}.txt"
    prompt = path.read_text(encoding="utf-8") if path.exists() else ""
    return prompt if template_hash(prompt) == record.get("prompt_hash") else None


@dataclass
class ContinueStats:
    eligible: int = 0
    done: int = 0
    copied: int = 0
    errors: int = 0
    skipped: int = 0
    aborted: bool = False


def _run_pool(todo, fn, concurrency, label, log) -> None:
    try:
        if todo:
            with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
                for future in [pool.submit(fn, *t) for t in todo]:
                    future.result()
    except KeyboardInterrupt:
        log(f"[{label}] interrupted; finished samples are saved. Re-run to resume.")
        os._exit(130)


class _ErrorBrake:
    """Stop sending requests after `limit` consecutive failures."""

    def __init__(self, limit: int, label: str, stats: ContinueStats, log):
        self.limit, self.label, self.stats, self.log = limit, label, stats, log
        self.lock = threading.Lock()
        self.event = threading.Event()
        self.consecutive = 0

    def failed(self, task: SampleTask, exc: Exception, task_dir: Path) -> None:
        _write_json(task_dir / f"{self.label}_error.json",
                    {"error": f"{type(exc).__name__}: {exc}", "time": time.time()})
        with self.lock:
            self.stats.errors += 1
            self.consecutive += 1
            self.log(f"[{self.label}] {task.item_id} {task.condition} #{task.index}: "
                     f"ERROR {type(exc).__name__}: {exc}")
            if self.consecutive >= self.limit and not self.event.is_set():
                self.event.set()
                self.stats.aborted = True
                self.log(f"[{self.label}] {self.consecutive} consecutive failures; stopping. "
                         "Re-run the same command to resume.")

    def ok(self) -> None:
        with self.lock:
            self.consecutive = 0


def force_answers(
    *,
    run_dir: Path,
    answer_tokens: int = 8192,
    concurrency: int = 24,
    request_timeout: float | None = 7200.0,
    max_consecutive_errors: int = 5,
    items: list[str] | None = None,
    limit: int | None = None,
    log: Callable[[str], None] = print,
    complete_fn: Callable[..., Completion] = complete_continuation,
) -> ContinueStats:
    """For each sample that exhausted its budget mid-reasoning, append
    `FORCE_ANSWER_PHRASE` to its reasoning and let the model write a final
    answer of up to `answer_tokens` tokens.

    The answer replaces the sample's (empty) one: `completion.json` gains
    `forced_answer: true` and `forced_*` fields, the raw generation goes to
    `forced.json`, and `candidate.lean` / `candidate_sha` are rewritten, so
    `grade-run` grades the forced answer. The original `finish_reason`
    ("length") is kept. Settings are recorded in `config.json` under
    `forced_answer`.

    Calling again with a *larger* `answer_tokens` upgrades the run: answers
    that hit the old cap are re-forced, the rest are kept (an answer that
    ended within the smaller budget would have ended identically with more).
    A smaller budget, or a different phrase, is refused.
    """
    stored = _read_json(run_dir / "config.json")
    if stored is None:
        raise FileNotFoundError(f"{run_dir / 'config.json'} not found")
    config = GenerationConfig(**stored["generation"])
    if config.enable_thinking is False:
        raise ValueError("this run was generated with thinking disabled; nothing to force")
    settings = {"answer_tokens": answer_tokens, "phrase": FORCE_ANSWER_PHRASE}
    previous = stored.get("forced_answer")
    redo_capped = False
    if previous is not None:
        same_phrase = previous.get("phrase") == FORCE_ANSWER_PHRASE
        old_tokens = previous.get("answer_tokens", 0)
        if not same_phrase or answer_tokens < old_tokens:
            raise ValueError(
                f"{run_dir} already has forced answers made with {previous}; refusing to "
                f"mix in answers made with {settings} (only raising --answer-tokens is "
                "allowed: it re-forces the answers that hit the old cap)."
            )
        redo_capped = answer_tokens > old_tokens
        if redo_capped:
            settings["upgraded_from"] = previous.get("upgraded_from", []) + [old_tokens]
            log(f"[force] raising the answer budget {old_tokens} -> {answer_tokens}: "
                "re-forcing answers that hit the old cap")
        else:
            settings = previous
    _write_json(run_dir / "config.json", {**stored, "forced_answer": settings})

    tasks, _ = read_plan(run_dir)
    stats = ContinueStats()
    todo = []
    for task in tasks:
        if items and task.item_id not in items:
            continue
        record = _read_json(task.dir(run_dir) / "completion.json")
        if record is None or not _needs_forced_answer(record, redo_capped):
            continue
        stats.eligible += 1
        prompt = _load_prompt(run_dir, task, record)
        if prompt is None:
            stats.skipped += 1
            log(f"[force] SKIPPING {task.item_id} {task.condition} #{task.index}: stored "
                "prompt doesn't match the one the sample was generated from")
            continue
        reasoning = (task.dir(run_dir) / "reasoning.txt").read_text(encoding="utf-8")
        todo.append((task, prompt, reasoning))
    if limit is not None:
        todo = todo[:limit]
    log(f"[force] {stats.eligible} samples ran out of budget while thinking; forcing "
        f"answers for {len(todo)} (answer budget {answer_tokens} tokens)")

    brake = _ErrorBrake(max_consecutive_errors, "force", stats, log)
    lock = threading.Lock()
    client = get_client(request_timeout) if todo and complete_fn is complete_continuation else None

    def do_force(task: SampleTask, prompt: str, reasoning: str) -> None:
        if brake.event.is_set():
            return
        task_dir = task.dir(run_dir)
        try:
            result = complete_fn(
                prompt, "<think>\n" + reasoning.rstrip() + FORCE_ANSWER_PHRASE,
                model=config.model, max_tokens=answer_tokens,
                enable_thinking=config.enable_thinking, temperature=config.temperature,
                top_p=config.top_p, top_k=config.top_k,
                seed=sample_seed(config.seed, task) ^ 1, timeout=request_timeout,
                client=client,
            )
        except Exception as exc:  # noqa: BLE001 -- recorded, re-tried on the next call
            brake.failed(task, exc, task_dir)
            return
        # The prefix already closed `</think>`; a stray one in the output
        # would mean the model went back to thinking -- keep what follows.
        answer = split_thinking(result.text)[1] if "</think>" in result.text else result.text
        _write_json(task_dir / "forced.json", {
            "generated": result.text, "finish_reason": result.finish_reason,
            "max_tokens_sent": result.max_tokens_sent,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "elapsed_s": result.elapsed_s, **settings,
        })
        extraction = extract_lean(answer)
        _atomic_write(task_dir / "candidate.lean", extraction.lean)
        record = _read_json(task_dir / "completion.json") or {}
        record.update({
            "text": answer,
            "forced_answer": True,
            "forced_finish_reason": result.finish_reason,
            "forced_completion_tokens": result.completion_tokens,
            "forced_elapsed_s": result.elapsed_s,
            "used_extraction_fallback": extraction.used_fallback,
            "unterminated_fence": extraction.unterminated_fence,
            "candidate_sha": _sha(extraction.lean),
        })
        _write_json(task_dir / "completion.json", record)
        (task_dir / "force_error.json").unlink(missing_ok=True)
        brake.ok()
        if result.max_tokens_sent is not None and result.max_tokens_sent < answer_tokens:
            log(f"[force] WARNING {task.item_id} {task.condition} #{task.index}: only "
                f"{result.max_tokens_sent} of {answer_tokens} answer tokens fit the context "
                "window (extend with a larger --answer-reserve)")
        with lock:
            stats.done += 1
            log(f"[force] {task.item_id} {task.condition} #{task.index}: "
                f"finish={result.finish_reason} tokens={result.completion_tokens} "
                f"lean={'yes' if not extraction.used_fallback else 'no'} "
                f"{result.elapsed_s or 0:.0f}s | {stats.done}/{len(todo)}")

    _run_pool(todo, do_force, concurrency, "force", log)
    log(f"[force] done: {stats.done} forced, {stats.errors} errors")
    return stats


def extend_run(
    *,
    source_dir: Path,
    run_dir: Path,
    max_tokens: int,
    answer_reserve: int = 8192,
    concurrency: int = 8,
    request_timeout: float | None = None,
    max_consecutive_errors: int = 5,
    items: list[str] | None = None,
    samples: int | None = None,
    log: Callable[[str], None] = print,
    complete_fn: Callable[..., Completion] = complete_continuation,
) -> ContinueStats:
    """Build `run_dir` as `source_dir` regenerated with a larger total
    budget `max_tokens`, without paying again for what the source already
    generated.

    Samples that ended within the source's budget are copied as-is (they
    would have ended identically with more room). Samples that ran out
    mid-reasoning are continued from where they stopped, with up to
    `max_tokens` minus what they already used, always leaving
    `answer_reserve` tokens of context free so `force_answers` can still
    get an answer from any that run out again. `run_dir`'s config records
    the new budget and `extended_from`; resuming is safe.
    """
    src_stored = _read_json(source_dir / "config.json")
    if src_stored is None:
        raise FileNotFoundError(f"{source_dir / 'config.json'} not found")
    src_config = GenerationConfig(**src_stored["generation"])
    if src_config.max_tokens and max_tokens <= src_config.max_tokens:
        raise ValueError(f"new budget {max_tokens} is not larger than the source's "
                         f"{src_config.max_tokens}")
    from dataclasses import replace

    config = replace(src_config, max_tokens=max_tokens)
    check_resume_compatible(run_dir, config)
    run_dir.mkdir(parents=True, exist_ok=True)
    origin = {"run_dir": str(source_dir), "max_tokens": src_config.max_tokens,
              "answer_reserve": answer_reserve}
    stored = _read_json(run_dir / "config.json") or {}
    if stored.get("extended_from") not in (None, origin):
        raise ValueError(f"{run_dir} was extended from {stored['extended_from']}, not {origin}")
    _write_json(run_dir / "config.json",
                {**stored, "generation": asdict(config), "extended_from": origin})

    src_tasks, gold_shas = read_plan(source_dir)
    tasks = [t for t in src_tasks
             if (not items or t.item_id in items) and (samples is None or t.index < samples)]
    plan = Plan(tasks=tasks, prompts={}, metas={},
                gold_shas={i: s for i, s in gold_shas.items() if any(t.item_id == i for t in tasks)})
    _set_status(run_dir, GENERATING, planned=len(tasks))  # before plan.json; see generate_run
    _write_plan(run_dir, plan)
    for item_id, cond in {(t.item_id, t.condition) for t in tasks}:
        name = f"{item_id}__{cond}.txt"
        if (source_dir / "prompts" / name).exists():
            _atomic_write(run_dir / "prompts" / name,
                          (source_dir / "prompts" / name).read_text(encoding="utf-8"))

    stats = ContinueStats()
    todo = []
    for task in tasks:
        src_dir, dst_dir = task.dir(source_dir), task.dir(run_dir)
        dst = _read_json(dst_dir / "completion.json")
        if dst is not None and (dst.get("extended") or not _truncated_while_thinking(dst)):
            continue  # already done in a previous call
        src = _read_json(src_dir / "completion.json")
        if src is None:
            stats.skipped += 1
            continue
        if not _truncated_while_thinking(src):
            for name in ("completion.json", "candidate.lean", "reasoning.txt"):
                if (src_dir / name).exists():
                    _atomic_write(dst_dir / name, (src_dir / name).read_text(encoding="utf-8"))
            stats.copied += 1
            continue
        stats.eligible += 1
        prompt = _load_prompt(source_dir, task, src)
        if prompt is None:
            stats.skipped += 1
            log(f"[extend] SKIPPING {task.item_id} {task.condition} #{task.index}: stored "
                "prompt doesn't match the one the sample was generated from")
            continue
        todo.append((task, prompt, src))
    log(f"[extend] {len(tasks)} samples: {stats.copied} copied (ended within the old "
        f"budget), {len(todo)} to continue up to {max_tokens} total tokens")
    _set_status(run_dir, GENERATING, planned=len(tasks), remaining=len(todo))

    brake = _ErrorBrake(max_consecutive_errors, "extend", stats, log)
    lock = threading.Lock()
    client = get_client(request_timeout) if todo and complete_fn is complete_continuation else None

    def do_extend(task: SampleTask, prompt: str, src: dict) -> None:
        if brake.event.is_set():
            return
        src_dir, dst_dir = task.dir(source_dir), task.dir(run_dir)
        reasoning = (src_dir / "reasoning.txt").read_text(encoding="utf-8")
        used = src.get("completion_tokens") or 0
        seed = sample_seed(config.seed, task) ^ 2
        try:
            result = complete_fn(
                prompt, "<think>\n" + reasoning,
                model=config.model, max_tokens=max_tokens - used,
                reserve_tokens=answer_reserve + RESERVE_SLACK_TOKENS,
                enable_thinking=config.enable_thinking,
                temperature=config.temperature, top_p=config.top_p, top_k=config.top_k,
                seed=seed, timeout=request_timeout, client=client,
            )
        except Exception as exc:  # noqa: BLE001 -- recorded, re-tried on the next call
            brake.failed(task, exc, dst_dir)
            return
        more, answer, closed = split_thinking(result.text)
        full_reasoning = reasoning + more
        extraction = extract_lean(answer)
        _atomic_write(dst_dir / "reasoning.txt", full_reasoning)
        _atomic_write(dst_dir / "candidate.lean", extraction.lean)
        record = {k: v for k, v in src.items() if not k.startswith("forced")}
        record.update({
            "text": answer,
            "finish_reason": result.finish_reason,
            "reasoning_chars": len(full_reasoning),
            "completion_tokens": used + (result.completion_tokens or 0),
            "elapsed_s": (src.get("elapsed_s") or 0) + (result.elapsed_s or 0),
            "used_extraction_fallback": extraction.used_fallback,
            "unterminated_fence": extraction.unterminated_fence,
            "candidate_sha": _sha(extraction.lean),
            "extended": {"from_run": str(source_dir), "source_tokens": used,
                         "added_tokens": result.completion_tokens, "closed_thinking": closed,
                         "max_tokens_sent": result.max_tokens_sent,
                         "continuation_seed": seed},
        })
        _write_json(dst_dir / "completion.json", record)
        (dst_dir / "extend_error.json").unlink(missing_ok=True)
        brake.ok()
        with lock:
            stats.done += 1
            log(f"[extend] {task.item_id} {task.condition} #{task.index}: "
                f"finish={result.finish_reason} +{result.completion_tokens} tokens "
                f"(total {record['completion_tokens']}) answered={'yes' if closed else 'no'} "
                f"{result.elapsed_s or 0:.0f}s | {stats.done}/{len(todo)}")
            _set_status(run_dir, GENERATING, planned=len(tasks),
                        remaining=len(todo) - stats.done)

    _run_pool(todo, do_extend, concurrency, "extend", log)
    _set_status(run_dir, "aborted" if stats.aborted else "finished",
                planned=len(tasks), remaining=len(todo) - stats.done)
    log(f"[extend] done: {stats.done} continued, {stats.copied} copied, {stats.errors} errors")
    return stats
