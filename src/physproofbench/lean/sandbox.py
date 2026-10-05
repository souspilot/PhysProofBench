"""L1 kernel check: compile a submission against the pinned Mathlib build.

See docs/GRADING.md#l1-kernel-check-sandboxpy. Runs the raw `lean` binary
(not `lake env lean`) with a wall-clock timeout and (best-effort) no network
access -- see `resolve_lake_env`'s docstring for why not `lake env lean`.

Network sandboxing is currently implemented for macOS only, via
`sandbox-exec`. On other platforms `compile_file` still enforces the
timeout and memory cap but does NOT block network access — this is a known
gap (see the TODO below) to close before running untrusted model output in
CI on Linux; use a container or `firejail`/`bwrap` there instead.
"""

from __future__ import annotations

import functools
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT_S = 300.0
DEFAULT_MEMORY_CAP_BYTES = 32 * 1024 * 1024 * 1024  # 32 GiB virtual; see _memory_cap_wrapper

# elan's default install location. `lake` may not be on PATH even when
# installed (observed: some subprocess environments don't inherit the shell
# profile that adds ~/.elan/bin) -- fall back to this before giving up.
_ELAN_DEFAULT_BIN = Path.home() / ".elan" / "bin"


def find_lake() -> str:
    found = shutil.which("lake")
    if found:
        return found
    candidate = _ELAN_DEFAULT_BIN / "lake"
    if candidate.exists():
        return str(candidate)
    raise FileNotFoundError(
        "lake not found on PATH or in ~/.elan/bin -- install elan "
        "(https://github.com/leanprover/elan) first"
    )


_ENV_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


@functools.lru_cache(maxsize=8)
def _resolve_lake_env_cached(lean_project_dir_str: str) -> tuple[tuple[str, str], ...]:
    proc = subprocess.run(
        [find_lake(), "env"],
        cwd=lean_project_dir_str,
        capture_output=True,
        text=True,
        timeout=600,
        stdin=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"`lake env` failed to resolve the workspace at {lean_project_dir_str}:\n"
            f"{proc.stderr}"
        )
    env: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        match = _ENV_LINE.match(line)
        if match:
            env[match.group(1)] = match.group(2)
    return tuple(sorted(env.items()))


def resolve_lake_env(lean_project_dir: Path) -> dict[str, str]:
    """Resolve `lean_project_dir`'s Lake environment (LEAN_PATH, the LEAN
    binary path, DYLD/LD_LIBRARY_PATH, etc.) via a bare `lake env`, and
    cache it per directory for the life of this process.

    Deliberately *not* used to run `lake env lean <file>` per compile.
    Found in practice: `lake env lean <file>` re-runs Lake's own
    dependency-freshness check on every invocation, and when that check's
    network access fails (as it does under this module's own
    `no_network=True` sandboxing, and once even in an unsandboxed subprocess
    — see `compile_file`'s stdin note below) Lake doesn't fail gracefully:
    it reports "mathlib: URL has changed" and attempts to delete and
    re-clone the entire Mathlib checkout. Resolving the environment once,
    then invoking the plain `lean` binary directly for every subsequent
    compile, sidesteps that check entirely -- `lean` itself does no
    dependency management and touches no network. This is also just faster:
    no repeated Lakefile elaboration per grading call.
    """
    return dict(_resolve_lake_env_cached(str(lean_project_dir)))


_SANDBOX_PROFILE = """
(version 1)
(deny default)
(allow file-read*)
(allow file-write* (subpath "/tmp") (subpath "/private/tmp") (subpath "/var/folders"))
(allow file-write* (subpath (param "PROJECT_DIR")))
(allow process-fork process-exec)
(allow sysctl-read)
(allow mach-lookup)
(allow iokit-open)
(deny network*)
"""


@dataclass
class CompileResult:
    ok: bool
    stdout: str
    stderr: str
    elapsed_s: float
    timed_out: bool
    returncode: int | None


def _memory_cap_wrapper(base: list[str], memory_cap_bytes: int | None) -> list[str]:
    """Prefix `base` with a shell `ulimit -v` when a memory cap applies.

    Linux only: RLIMIT_AS is flaky-to-broken on macOS (setrlimit reliably
    raises "current limit exceeds maximum limit" even though getrlimit
    reports both limits as unlimited -- a longstanding Darwin quirk), so
    there we rely on the wall-clock timeout.

    Done with a `bash -c 'ulimit -v ...; exec ...'` wrapper rather than
    `subprocess`'s `preexec_fn`, which Python documents as unsafe when the
    parent has threads -- and the batch runner grades from a thread pool.

    The cap limits *virtual* address space, and a Lean process importing all
    of Mathlib maps several GB of `.olean` files, so caps that look generous
    for resident memory can still fail the compile spuriously.
    `physproofbench preflight` compiles a real `import Mathlib` file under the
    same cap to catch that before a run.
    """
    if not memory_cap_bytes or platform.system() != "Linux":
        return base
    kib = memory_cap_bytes // 1024
    return ["bash", "-c", f'ulimit -v {kib} && exec "$@"', "lean-sandbox", *base]


def _build_command(
    lean_bin: str,
    file_path: Path,
    *,
    lean_project_dir: Path,
    no_network: bool,
    memory_cap_bytes: int | None = None,
) -> list[str]:
    base = _memory_cap_wrapper([lean_bin, str(file_path)], memory_cap_bytes)
    if no_network and platform.system() == "Darwin":
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sb", delete=False) as f:
            f.write(_SANDBOX_PROFILE)
            profile_path = f.name
        return [
            "sandbox-exec",
            "-f",
            profile_path,
            "-D",
            f"PROJECT_DIR={lean_project_dir}",
            *base,
        ]
    return base


def compile_file(
    lean_project_dir: Path,
    file_path: Path,
    *,
    timeout: float = DEFAULT_TIMEOUT_S,
    memory_cap_bytes: int | None = DEFAULT_MEMORY_CAP_BYTES,
    no_network: bool = True,
) -> CompileResult:
    """Compile `file_path` against `lean_project_dir`'s resolved environment.

    `file_path` need not live inside `lean_project_dir`, but the module it
    declares must resolve against that project's dependencies (Mathlib etc.)
    for imports to succeed. See `resolve_lake_env` for why this runs the raw
    `lean` binary rather than `lake env lean`/`lake lean`.

    `stdin` is deliberately closed below (`DEVNULL`). Without it, `lean`
    invoked via `subprocess` (as opposed to an interactive shell) was
    observed to hang reading stdin.
    """
    env_vars = resolve_lake_env(lean_project_dir)
    lean_bin = env_vars.get("LEAN")
    if not lean_bin:
        raise RuntimeError(
            f"`lake env` at {lean_project_dir} did not report a LEAN binary path"
        )
    command = _build_command(
        lean_bin,
        file_path,
        lean_project_dir=lean_project_dir,
        no_network=no_network,
        memory_cap_bytes=memory_cap_bytes,
    )
    child_env = {**os.environ, **env_vars}
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            cwd=lean_project_dir,
            env=child_env,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        return CompileResult(
            ok=False,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + "\n[physproofbench] timed out",
            elapsed_s=elapsed,
            timed_out=True,
            returncode=None,
        )
    elapsed = time.monotonic() - start
    return CompileResult(
        ok=proc.returncode == 0,
        stdout=proc.stdout,
        stderr=proc.stderr,
        elapsed_s=elapsed,
        timed_out=False,
        returncode=proc.returncode,
    )
