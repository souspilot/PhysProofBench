"""Summaries of a batch run, rebuilt from the stored JSON alone (no model
calls), per plan.md §8 / M1's acceptance criterion.

Reads `<run_dir>/samples/*/*/*/{completion,grade}.json` and `config.json`;
writes `summary.json` and `summary.md` next to them.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

from .schema import load_item_meta

VERDICTS = ("pass", "gate_fail", "compile_fail", "audit_fail", "no_output", "grader_error")


def pass_at_k(n: int, c: int, k: int) -> float | None:
    """Unbiased pass@k estimator (Chen et al. 2021): probability that at
    least one of k samples drawn without replacement from n, of which c pass,
    passes. None when fewer than k samples exist."""
    if n < k or k <= 0:
        return None
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def _read(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def collect_records(run_dir: Path) -> list[dict]:
    records = []
    for sample_dir in sorted((run_dir / "samples").glob("*/*/*")):
        completion = _read(sample_dir / "completion.json")
        error = _read(sample_dir / "error.json")
        grade = _read(sample_dir / "grade.json")
        if completion is None and error is None:
            continue
        item_id, condition = sample_dir.parent.parent.name, sample_dir.parent.name
        rec = {
            "item_id": item_id,
            "condition": condition,
            "index": int(sample_dir.name),
            "generated": completion is not None,
            "finish_reason": (completion or {}).get("finish_reason"),
            "completion_tokens": (completion or {}).get("completion_tokens"),
            "elapsed_s": (completion or {}).get("elapsed_s"),
            "used_extraction_fallback": (completion or {}).get("used_extraction_fallback"),
            "verdict": None,
            "gate_failures": [],
            "compile_timed_out": None,
            "statement_edited_would_pass": False,
            "forced_answer": bool((completion or {}).get("forced_answer")),
            "extended": bool((completion or {}).get("extended")),
            "repair_round": (completion or {}).get("repair_round"),
            # First attempt (round) that passed, for repair runs; None if none.
            "pass_round": None,
        }
        if grade is not None and completion is not None and (
            grade.get("candidate_sha") == completion.get("candidate_sha")
        ):
            rec["verdict"] = grade.get("verdict")
            rec["gate_failures"] = grade.get("gate_failures") or []
            rec["compile_timed_out"] = grade.get("compile_timed_out")
            diag = grade.get("statement_edit_diagnostic") or {}
            rec["statement_edited_would_pass"] = bool(diag.get("would_pass"))
        if rec["repair_round"] is not None:
            from .repair import attempt_history

            history = attempt_history(sample_dir)
            rec["pass_round"] = history.index("pass") if "pass" in history else None
        records.append(rec)
    return records


def _group_stats(recs: list[dict], ks: list[int]) -> dict:
    graded = [r for r in recs if r["verdict"] is not None]
    n, c = len(graded), sum(r["verdict"] == "pass" for r in graded)
    tokens = [r["completion_tokens"] for r in recs if r["completion_tokens"] is not None]
    out = {
        "samples": len(recs),
        "generated": sum(r["generated"] for r in recs),
        "graded": n,
        "passed": c,
        "verdicts": dict(Counter(r["verdict"] for r in graded)),
        "truncated": sum(r["finish_reason"] == "length" for r in recs),
        # Answers obtained with `force-answer` after the thinking budget ran out.
        "forced_answers": sum(r["forced_answer"] for r in recs),
        "forced_passed": sum(r["forced_answer"] and r["verdict"] == "pass" for r in recs),
        "extended": sum(r["extended"] for r in recs),
        "no_lean_fence": sum(bool(r["used_extraction_fallback"]) for r in recs),
        "compile_timeouts": sum(bool(r["compile_timed_out"]) for r in graded),
        # Rejected by the L0 text gate as statement_edited, yet compiling,
        # axiom-clean and proving the gold type (grading.py diagnostic).
        "statement_edited_would_pass": sum(r["statement_edited_would_pass"] for r in graded),
        "median_completion_tokens": statistics.median(tokens) if tokens else None,
        "max_completion_tokens": max(tokens) if tokens else None,
    }
    for k in ks:
        out[f"pass@{k}"] = pass_at_k(n, c, k)
    return out


def _mean_over_items(per_item: list[dict], key: str) -> float | None:
    vals = [s[key] for s in per_item if s.get(key) is not None]
    return sum(vals) / len(vals) if vals else None


def summarize(run_dir: Path, items_dir: Path) -> dict:
    config = _read(run_dir / "config.json") or {}
    all_records = collect_records(run_dir)
    max_n = max(
        (len(v) for v in _by(all_records, ("item_id", "condition")).values()), default=0
    )
    ks = sorted({1, max_n} - {0})

    kinds: dict[str, str] = {}
    roles: dict[str, str] = {}
    for item_id in {r["item_id"] for r in all_records}:
        meta_path = items_dir / item_id / "meta.yaml"
        meta = load_item_meta(meta_path) if meta_path.exists() else None
        kinds[item_id] = meta.proof_kind if meta else "?"
        roles[item_id] = meta.role if meta else "benchmark"
    # Canaries are pipeline checks: kept out of every benchmark number.
    records = [r for r in all_records if roles[r["item_id"]] != "canary"]
    canary_records = [r for r in all_records if roles[r["item_id"]] == "canary"]

    per_cell = {
        f"{item}|{cond}": {"item_id": item, "condition": cond, "proof_kind": kinds[item],
                           **_group_stats(recs, ks)}
        for (item, cond), recs in sorted(_by(records, ("item_id", "condition")).items())
    }
    # Aggregates average per-item pass@k (each item weighted equally),
    # the standard benchmark headline, rather than pooling samples.
    aggregates = {}
    for label, keyfn in (
        ("condition", lambda s: s["condition"]),
        ("proof_kind x condition", lambda s: f"{s['proof_kind']} | {s['condition']}"),
    ):
        groups: dict[str, list[dict]] = defaultdict(list)
        for cell in per_cell.values():
            groups[keyfn(cell)].append(cell)
        aggregates[label] = {
            g: {
                "items": len(cells),
                "items_solved": sum(c["passed"] > 0 for c in cells),
                **{f"pass@{k}": _mean_over_items(cells, f"pass@{k}") for k in ks},
            }
            for g, cells in sorted(groups.items())
        }
    repair = _repair_summary(records, ks, config)
    gate_reasons = Counter(f for r in records if r["verdict"] == "gate_fail" for f in r["gate_failures"])
    status = _read(run_dir / "status.json") or {}
    planned = len((_read(run_dir / "plan.json") or {}).get("tasks", []))
    return {
        "run_dir": str(run_dir),
        "generation_state": status.get("state"),
        "planned": planned,
        "generation": config.get("generation"),
        "ks": ks,
        "totals": _group_stats(records, ks),
        "per_item_condition": per_cell,
        "aggregates": aggregates,
        "gate_failure_reasons": dict(gate_reasons.most_common()),
        "repair": repair,
        "canaries": _canary_summary(canary_records, ks),
    }


def _canary_summary(records: list[dict], ks: list[int]) -> dict | None:
    if not records:
        return None
    cells = {f"{i}|{c}": {"item_id": i, "condition": c, **_group_stats(recs, ks)}
             for (i, c), recs in sorted(_by(records, ("item_id", "condition")).items())}
    items = sorted({r["item_id"] for r in records})
    solved = [i for i in items if any(r["item_id"] == i and r["verdict"] == "pass"
                                      for r in records)]
    return {"items": len(items), "items_solved": len(solved),
            "unsolved": [i for i in items if i not in solved], "cells": cells}


def _repair_summary(records: list[dict], ks: list[int], config: dict) -> dict | None:
    """Per condition, mean over items of pass@k counting a sample as passed
    if it passed within r repair rounds, for r = 0..rounds."""
    settings = config.get("repair")
    if not settings or not any(r["repair_round"] is not None for r in records):
        return None
    rounds = settings.get("rounds", 0)
    by_round: dict = {}
    for r_max in range(rounds + 1):
        by_cond: dict[str, list[dict]] = defaultdict(list)
        for (item, cond), recs in _by(records, ("item_id", "condition")).items():
            n = len(recs)
            c = sum(r["pass_round"] is not None and r["pass_round"] <= r_max for r in recs)
            by_cond[cond].append({f"pass@{k}": pass_at_k(n, c, k) for k in ks}
                                 | {"solved": c > 0})
        by_round[r_max] = {
            cond: {"items": len(cells), "items_solved": sum(c["solved"] for c in cells),
                   **{f"pass@{k}": _mean_over_items(cells, f"pass@{k}") for k in ks}}
            for cond, cells in sorted(by_cond.items())
        }
    pending = sum(r["repair_round"] is not None and r["verdict"] is None for r in records)
    return {"settings": settings, "by_round": by_round, "ungraded_attempts": pending}


def _by(records: list[dict], keys: tuple[str, ...]) -> dict:
    groups: dict = defaultdict(list)
    for r in records:
        groups[tuple(r[k] for k in keys)].append(r)
    return groups


def _fmt(x) -> str:
    if x is None:
        return "–"
    if isinstance(x, float):
        return f"{x:.2f}"
    return str(x)


def render_markdown(summary: dict) -> str:
    ks = summary["ks"]
    gen = summary.get("generation") or {}
    lines = [f"# Run summary: `{summary['run_dir']}`", ""]
    if gen:
        lines += [
            "Generation: " + ", ".join(f"`{k}={v}`" for k, v in gen.items()),
            "",
        ]
    canaries = summary.get("canaries")
    if canaries:
        ok = canaries["items_solved"] == canaries["items"]
        lines += [
            f"**Pipeline canaries: {canaries['items_solved']}/{canaries['items']} trivial "
            f"items solved at least once** "
            + ("(pipeline looks healthy)." if ok else
               f"-- unsolved: {', '.join(canaries['unsolved'])}. Check these before "
               "trusting any benchmark number below."),
            "",
        ]
    t = summary["totals"]
    ungraded = t["generated"] - t["graded"]
    lines += [
        f"Generation state: **{summary.get('generation_state')}**; "
        f"{t['generated']}/{summary.get('planned')} planned samples generated, "
        f"{ungraded} not yet graded."
        + (" Numbers below are partial." if ungraded or summary.get("generation_state")
           != "finished" else ""),
        "",
        f"Samples: {t['samples']} ({t['generated']} generated, {t['graded']} graded, "
        f"{t['passed']} passed). Truncated at token limit: {t['truncated']}. "
        f"No ```lean fence: {t['no_lean_fence']}. Compile timeouts: {t['compile_timeouts']}. "
        f"Rejected as statement_edited but otherwise correct: {t['statement_edited_would_pass']}. "
        f"Answers forced after the thinking budget (`force-answer`): {t['forced_answers']} "
        f"({t['forced_passed']} passed).",
        "",
        "## By condition (mean over items)",
        "",
    ]
    for label, groups in summary["aggregates"].items():
        lines += [f"### {label}", "",
                  "| group | items | solved | " + " | ".join(f"pass@{k}" for k in ks) + " |",
                  "|---|---|---|" + "---|" * len(ks)]
        for g, s in groups.items():
            lines.append(f"| {g} | {s['items']} | {s['items_solved']} | "
                         + " | ".join(_fmt(s[f'pass@{k}']) for k in ks) + " |")
        lines.append("")
    lines += [
        "## Per item",
        "",
        "| item | kind | condition | n | pass | " + " | ".join(f"pass@{k}" for k in ks)
        + " | " + " | ".join(VERDICTS[1:]) + " | edited-but-correct | truncated | median tokens |",
        "|---|---|---|---|---|" + "---|" * len(ks) + "---|" * (len(VERDICTS) - 1) + "---|---|---|",
    ]
    for cell in summary["per_item_condition"].values():
        v = cell["verdicts"]
        lines.append(
            f"| {cell['item_id']} | {cell['proof_kind']} | {cell['condition']} | "
            f"{cell['graded']} | {cell['passed']} | "
            + " | ".join(_fmt(cell[f"pass@{k}"]) for k in ks) + " | "
            + " | ".join(str(v.get(x, 0)) for x in VERDICTS[1:])
            + f" | {cell['statement_edited_would_pass']} | {cell['truncated']}"
            f" | {_fmt(cell['median_completion_tokens'])} |"
        )
    repair = summary.get("repair")
    if repair:
        lines += ["", "## Repair rounds (pass within r rounds of compiler feedback)", "",
                  f"Settings: {repair['settings']}. Attempts awaiting a grade: "
                  f"{repair['ungraded_attempts']}.", "",
                  "| rounds | condition | items | solved | "
                  + " | ".join(f"pass@{k}" for k in ks) + " |",
                  "|---|---|---|---|" + "---|" * len(ks)]
        for r_max, conds in repair["by_round"].items():
            for cond, s in conds.items():
                lines.append(f"| ≤{r_max} | {cond} | {s['items']} | {s['items_solved']} | "
                             + " | ".join(_fmt(s[f'pass@{k}']) for k in ks) + " |")
    if summary["gate_failure_reasons"]:
        lines += ["", "## Gate failure reasons", ""]
        lines += [f"- `{r}`: {n}" for r, n in summary["gate_failure_reasons"].items()]
    return "\n".join(lines) + "\n"


def write_report(run_dir: Path, items_dir: Path) -> str:
    summary = summarize(run_dir, items_dir)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    md = render_markdown(summary)
    (run_dir / "summary.md").write_text(md, encoding="utf-8")
    return md
