"""Physics-only test (generation side; never runs Lean).

Asks for an item's result from its plain-language statement alone: no Lean,
no comments and no expert proof. This separates the physical decision from
the ability to write a proof. Answers are kept verbatim for review next to
the expected answer and the plug-in trap; symbolic answers are not auto-scored.

    physproofbench physics-only --model M --run-dir runs/P -k 8

Layout: `<run>/config.json`, `<run>/samples/<item>/<index>.json`, and
`<run>/summary.md`. Re-running the same command resumes.
"""

from __future__ import annotations

import re
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import yaml

from .batch import FORCE_ANSWER_PHRASE, _read_json, _write_json, split_thinking
from .models.openai_client import Completion, complete, complete_continuation, get_client

PROMPT_VERSION = "physics-v1"
PROMPT = """\
Solve the following physics problem. Give your reasoning, then end your reply
with one line beginning `FINAL ANSWER:` that states the requested result
explicitly, including any numerical coefficients and exponents.

Problem:

{statement}
"""

_FINAL = re.compile(r"FINAL ANSWER:\s*(.+)", re.IGNORECASE)


@dataclass
class PhysicsConfig:
    model: str
    max_tokens: int = 32768
    answer_tokens: int = 8192
    enable_thinking: bool | None = None
    reasoning_effort: str | None = None
    temperature: float = 0.6
    top_p: float | None = 0.95
    top_k: int | None = 20
    force_answer: bool = True
    seed: int = 0
    prompt_version: str = PROMPT_VERSION


@dataclass
class PhysicsItem:
    item_id: str
    statement: str
    expected: object
    trap: str


def load_items(items_dir: Path, items: list[str] | None = None) -> list[PhysicsItem]:
    """Items with a `## statement` and `shape: answer_blank`, or exactly `items`."""
    found = []
    for meta_path in sorted(items_dir.glob("*/meta.yaml")):
        item_id = meta_path.parent.name
        if items and item_id not in items:
            continue
        metadata = yaml.safe_load(meta_path.read_text(encoding="utf-8")).get("metadata") or {}
        if not items and metadata.get("shape") != "answer_blank":
            continue
        nl = (meta_path.parent / "nl.md").read_text(encoding="utf-8")
        match = re.search(r"^## statement\s*\n(.*?)(?=^## |\Z)", nl, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(f"{item_id}: nl.md has no `## statement` section")
        found.append(PhysicsItem(item_id, match.group(1).strip(),
                                 metadata.get("expected_answer"),
                                 metadata.get("plug_in_trap") or ""))
    return found


def final_answer(text: str) -> str | None:
    """The last `FINAL ANSWER:` line, without Markdown emphasis."""
    answers = _FINAL.findall(text.replace("*", ""))
    return answers[-1].strip() if answers else None


def run_physics_only(
    *,
    config: PhysicsConfig,
    items: list[PhysicsItem],
    run_dir: Path,
    samples: int,
    concurrency: int = 16,
    max_consecutive_errors: int = 5,
    log: Callable[[str], None] = print,
    chat_fn: Callable[..., Completion] = complete,
    continue_fn: Callable[..., Completion] = complete_continuation,
) -> dict:
    stored = _read_json(run_dir / "config.json")
    if stored is not None and stored != asdict(config):
        raise ValueError(f"{run_dir} was made with {stored}; use a new --run-dir.")
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(run_dir / "config.json", asdict(config))
    client = get_client(None) if chat_fn is complete else None
    common = dict(model=config.model, temperature=config.temperature, top_p=config.top_p,
                  top_k=config.top_k, timeout=None, client=client,
                  enable_thinking=config.enable_thinking)
    lock = threading.Lock()
    abort = threading.Event()
    stats = {"done": 0, "errors": 0, "aborted": False}
    consecutive = 0

    def one(item: PhysicsItem, index: int) -> None:
        nonlocal consecutive
        if abort.is_set():
            return
        path = run_dir / "samples" / item.item_id / f"{index:03d}.json"
        prompt = PROMPT.format(statement=item.statement)
        seed = (zlib.crc32(item.item_id.encode()) + config.seed * 1009 + index) % (2 ** 31)
        forced = None
        try:
            result = chat_fn(prompt, max_tokens=config.max_tokens, seed=seed,
                             reasoning_effort=config.reasoning_effort, **common)
            reasoning, answer = result.reasoning or "", result.text
            if (config.force_answer and result.finish_reason == "length"
                    and not answer.strip() and reasoning):
                forced = continue_fn(prompt, "<think>\n" + reasoning.rstrip() + FORCE_ANSWER_PHRASE,
                                     max_tokens=config.answer_tokens, seed=seed ^ 1, **common)
                answer = split_thinking(forced.text)[1] if "</think>" in forced.text \
                    else forced.text
        except Exception as exc:  # noqa: BLE001 -- retried when the command is re-run
            with lock:
                stats["errors"] += 1
                consecutive += 1
                log(f"[physics] {item.item_id} #{index}: ERROR {type(exc).__name__}: {exc}")
                if consecutive >= max_consecutive_errors and not abort.is_set():
                    abort.set()
                    stats["aborted"] = True
                    log("[physics] too many consecutive failures; stopping. Re-run to resume.")
            return
        _write_json(path, {
            "item_id": item.item_id, "index": index, "seed": seed, "prompt": prompt,
            "served_model": result.model, "answer": answer, "reasoning": reasoning,
            "final_answer": final_answer(answer),
            "finish_reason": result.finish_reason,
            "forced_answer": forced is not None,
            "forced_finish_reason": forced.finish_reason if forced else None,
            "completion_tokens": result.completion_tokens,
            "forced_completion_tokens": forced.completion_tokens if forced else None,
            "time": time.time(),
        })
        with lock:
            consecutive = 0
            stats["done"] += 1
            log(f"[physics] {item.item_id} #{index}: finish={result.finish_reason}"
                f"{' +forced' if forced else ''} final={final_answer(answer)!r}")

    todo = [(item, i) for item in items for i in range(samples)
            if not (run_dir / "samples" / item.item_id / f"{i:03d}.json").exists()]
    log(f"[physics] {len(items)} items x {samples} samples: {len(todo)} to generate")
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        list(pool.map(lambda task: one(*task), todo))
    write_summary(run_dir, items, samples)
    log(f"[physics] done: {stats}; see {run_dir / 'summary.md'}")
    return stats


def _cell(value: object) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def write_summary(run_dir: Path, items: list[PhysicsItem], samples: int) -> None:
    """Answers for review; correctness is judged by a reader, not here."""
    config = _read_json(run_dir / "config.json") or {}
    lines = [f"# Physics-only answers: `{run_dir}`", "",
             f"Settings: `{config}`", "",
             "Answers are unscored. Compare each with the expected answer and the trap.", ""]
    for item in items:
        records = [_read_json(run_dir / "samples" / item.item_id / f"{i:03d}.json")
                   for i in range(samples)]
        records = [r for r in records if r]
        lines += [f"## {item.item_id}", "",
                  f"- Expected: {_cell(item.expected)}",
                  f"- Trap: {_cell(item.trap)}",
                  f"- Samples: {len(records)}/{samples}; forced after the thinking budget: "
                  f"{sum(bool(r['forced_answer']) for r in records)}; "
                  f"no `FINAL ANSWER` line: {sum(not r['final_answer'] for r in records)}", "",
                  "| # | finish | forced | tokens | final answer |", "|---|---|---|---|---|"]
        for r in records:
            lines.append(f"| {r['index']} | {r['finish_reason']} | "
                         f"{'yes' if r['forced_answer'] else 'no'} | {r['completion_tokens']} | "
                         f"{_cell(r['final_answer'] or '(none)')} |")
        lines.append("")
    (run_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
