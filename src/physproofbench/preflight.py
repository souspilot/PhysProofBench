"""Checks to run before spending GPU time on a batch run.

Each check returns a `Check`; `physproofbench preflight` prints them all and
exits non-zero if any failed. They exercise the same code paths a run uses
(same client, same sandbox, same memory cap), so a pass here means the run's
plumbing works, not merely that the tools are installed.
"""

from __future__ import annotations

import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from .grading import grade_submission
from .lean.sandbox import DEFAULT_MEMORY_CAP_BYTES, find_lake, resolve_lake_env
from .models.openai_client import complete, get_client

# Rough chars-per-token for Lean + English prompts; deliberately low (more
# tokens per char than typical) so the context-length check errs safe.
_CHARS_PER_TOKEN = 3.0


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    warning: bool = False  # ok, but worth a look


def _proxy_check(base_url: str | None) -> Check | None:
    """Flag the classic cluster trap: HTTP(S)_PROXY set, and NO_PROXY not
    covering a local server, so the client sends localhost traffic to the
    proxy and stalls until it times out."""
    if not base_url:
        return None
    host = urlparse(base_url).hostname or ""
    proxies = {k: v for k, v in os.environ.items()
               if k.lower() in ("http_proxy", "https_proxy", "all_proxy") and v}
    if not proxies:
        return None
    no_proxy = ",".join(os.environ.get(k, "") for k in ("NO_PROXY", "no_proxy"))
    covered = any(h.strip() and (host == h.strip() or host.endswith(h.strip().lstrip("*")))
                  for h in no_proxy.split(","))
    if covered:
        return None
    return Check("proxy", True,
                 f"{sorted(proxies)} set and NO_PROXY does not cover {host!r}: requests "
                 "to the model server will go through the proxy and may hang. Run "
                 f"`export NO_PROXY={host},localhost,127.0.0.1 no_proxy={host},"
                 "localhost,127.0.0.1`.", warning=True)


def check_endpoint(
    model: str,
    *,
    connect_timeout: float = 15.0,
    request_timeout: float = 120.0,
    on_check: Callable[[Check], None] | None = None,
) -> tuple[list[Check], int | None]:
    """Server reachable, `model` served, one tiny request round-trips.
    Returns the checks and the server's `max_model_len` (vLLM), if reported.

    Each check is passed to `on_check` as soon as it completes, so a slow
    or unreachable server shows up immediately rather than as silence.
    Listing models gets a short timeout (the server either answers at once
    or isn't there); only the test generation gets the longer one."""
    checks: list[Check] = []

    def add(check: Check) -> None:
        checks.append(check)
        if on_check:
            on_check(check)

    base_url = os.environ.get("OPENAI_BASE_URL")
    add(Check("server URL", bool(base_url),
              base_url or "OPENAI_BASE_URL is not set, so requests would go to "
              "api.openai.com. For a local vLLM server: "
              "`export OPENAI_BASE_URL=http://localhost:8000/v1`."))
    if not base_url:
        return checks, None
    proxy = _proxy_check(base_url)
    if proxy:
        add(proxy)
    try:
        models = get_client(connect_timeout).models.list().data
    except Exception as exc:  # noqa: BLE001
        add(Check("endpoint reachable", False,
                  f"{type(exc).__name__}: {exc}. Is vLLM up? Check its log for "
                  "'Application startup complete' and try "
                  f"`curl {base_url.rstrip('/')}/models`."))
        return checks, None
    ids = [m.id for m in models]
    add(Check("endpoint reachable", True, f"serving {ids}"))
    match = next((m for m in models if m.id == model), None)
    if match is None:
        add(Check("model served", False, f"{model!r} not in {ids} "
                  "(--model must equal vLLM's --served-model-name)"))
        return checks, None
    max_len = getattr(match, "max_model_len", None)
    add(Check("model served", True, f"{model!r}, max_model_len={max_len}"))
    try:
        out = complete("Reply with the single word: ready", model=model, max_tokens=64,
                       client=get_client(request_timeout))
        add(Check(
            "test request", True,
            f"{out.elapsed_s:.1f}s, finish={out.finish_reason}, "
            f"reasoning returned separately: {out.reasoning is not None}",
        ))
    except Exception as exc:  # noqa: BLE001
        add(Check("test request", False, f"{type(exc).__name__}: {exc}"))
    return checks, max_len


def check_context_budget(
    prompt_chars: int, max_tokens: int | None, max_model_len: int | None
) -> Check:
    est_prompt = int(prompt_chars / _CHARS_PER_TOKEN)
    if max_model_len is None:
        return Check("context budget", True,
                     f"longest prompt ~{est_prompt} tokens; server max_model_len unknown",
                     warning=True)
    if not max_tokens or max_tokens <= 0:
        return Check("context budget", True,
                     f"uncapped generation; longest prompt ~{est_prompt} tokens leaves "
                     f"~{max_model_len - est_prompt} tokens before the context is full")
    need = est_prompt + max_tokens
    if need > max_model_len:
        return Check("context budget", False,
                     f"longest prompt ~{est_prompt} + max_tokens {max_tokens} = {need} "
                     f"> max_model_len {max_model_len}: vLLM would reject those requests. "
                     f"Lower --max-tokens to <= {max_model_len - est_prompt}.")
    return Check("context budget", True,
                 f"longest prompt ~{est_prompt} + max_tokens {max_tokens} <= {max_model_len}")


def _core_modules(lean_project_dir: Path) -> list[str]:
    core = lean_project_dir / "PhysProofBench" / "Core"
    return sorted(f"PhysProofBench.Core.{p.stem}" for p in core.glob("*.lean"))


def check_lean_env(lean_project_dir: Path) -> list[Check]:
    """Fast (seconds) checks that the grading environment is complete:
    lake, the resolved Lake env, Mathlib's umbrella `.olean`, and an
    up-to-date build of every PhysProofBench module. Without these, every
    sample would be graded `compile_fail` -- recorded as a real verdict, not
    retried -- so `grade-run` runs this before grading anything."""
    checks: list[Check] = []
    try:
        lake = find_lake()
        checks.append(Check("lake found", True, lake))
    except FileNotFoundError as exc:
        return [Check("lake found", False, str(exc))]
    try:
        env = resolve_lake_env(lean_project_dir)
        from .lean.sandbox import lean_binary

        checks.append(Check("lake env", bool(lean_binary(env)), f"lean={lean_binary(env)}"))
    except Exception as exc:  # noqa: BLE001
        return checks + [Check("lake env", False, str(exc))]

    # Build outputs live in `.lake/build/lib/lean/` (current Lake) or
    # `.lake/build/lib/` (Lake of the Lean 4.9 era, the `lean-v4.9` pin).
    def first_existing(*paths: Path) -> Path:
        return next((p for p in paths if p.exists()), paths[0])

    mathlib_lib = lean_project_dir / ".lake/packages/mathlib/.lake/build/lib"
    mathlib_olean = first_existing(mathlib_lib / "lean/Mathlib.olean", mathlib_lib / "Mathlib.olean")
    checks.append(Check(
        "Mathlib.olean (umbrella)", mathlib_olean.exists(),
        "present" if mathlib_olean.exists() else
        "missing: submissions with `import Mathlib` will all fail L1. Run "
        "`lake exe cache get && lake build Mathlib` in lean/ (docs/GRADING.md L1).",
    ))

    build_dir = first_existing(lean_project_dir / ".lake/build/lib/lean",
                               lean_project_dir / ".lake/build/lib")
    stale = []
    for src in sorted((lean_project_dir / "PhysProofBench").rglob("*.lean")):
        olean = build_dir / src.relative_to(lean_project_dir).with_suffix(".olean")
        if not olean.exists() or olean.stat().st_mtime < src.stat().st_mtime:
            stale.append(str(src.relative_to(lean_project_dir)))
    checks.append(Check(
        "PhysProofBench built", not stale,
        "all Core and Item modules up to date" if not stale else
        f"missing or stale: {stale}. Run `lake build PhysProofBench` in lean/.",
    ))
    return checks


def check_lean(
    lean_project_dir: Path,
    *,
    memory_cap_bytes: int | None = DEFAULT_MEMORY_CAP_BYTES,
    compile_timeout: float = 300.0,
) -> list[Check]:
    """`check_lean_env`, then grade a trivially correct submission through
    the real pipeline. `compile_timeout` should be the run's own; the control
    compile is allowed twice that, so a slow machine is reported, not failed."""
    checks = check_lean_env(lean_project_dir)
    if not all(c.ok for c in checks):
        return checks

    # Positive control: what a typical model submission does (import all of
    # Mathlib plus the item's Core modules), graded through the real
    # pipeline -- sandbox, memory cap, `#print axioms` parsing included.
    imports = "\n".join(f"import {m}" for m in ["Mathlib", *_core_modules(lean_project_dir)])
    source = (f"{imports}\n\ntheorem physproofbench_preflight : (2 : ℝ) + 2 = 4 := by\n"
              "  norm_num\n")
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = Path(f.name)
    try:
        start = time.monotonic()
        report = grade_submission(
            lean_project_dir=lean_project_dir, submission_path=path, gold_path=None,
            decl_name="physproofbench_preflight", mode="autoform",
            timeout=2 * compile_timeout, memory_cap_bytes=memory_cap_bytes,
        )
        elapsed = time.monotonic() - start
    finally:
        path.unlink(missing_ok=True)
    if report.verdict == "pass":
        slow = elapsed > compile_timeout / 3
        checks.append(Check(
            "grade a correct submission", True,
            f"pass in {elapsed:.0f}s (≈ per-sample grading cost floor)"
            + (f"; that is over a third of --compile-timeout {compile_timeout:.0f}s, so "
               "real proofs may time out and be misgraded as compile_fail. Raise "
               "--compile-timeout, or lower --grade-workers if compiles contend for "
               "CPU/IO." if slow else ""),
            warning=slow,
        ))
    else:
        detail = f"verdict {report.verdict}"
        if report.compile is not None:
            out = (report.compile.stdout + report.compile.stderr).strip()
            detail += f"; compiler output: {out[:1500]}"
            if "memory" in out.lower() or "mmap" in out.lower() or "alloc" in out.lower():
                detail += ("\nLooks memory-related: retry with a larger --memory-cap-gb, "
                           "or 0 to disable the cap.")
        checks.append(Check("grade a correct submission", False, detail))
    return checks
