"""L1 kernel check: compile a submission against the pinned Mathlib build.

See docs/GRADING.md#l1-kernel-check-sandboxpy. Runs `lake env lean <file>`
with a wall-clock timeout and (best-effort) no network access.

Network sandboxing is currently implemented for macOS only, via
`sandbox-exec`. On other platforms `compile_file` still enforces the
timeout and memory cap but does NOT block network access — this is a known
gap (see the TODO below) to close before running untrusted model output in
CI on Linux; use a container or `firejail`/`bwrap` there instead.
"""

from __future__ import annotations

import platform
import resource
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TIMEOUT_S = 300.0
DEFAULT_MEMORY_CAP_BYTES = 8 * 1024 * 1024 * 1024  # 8 GiB

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


def _memory_cap_preexec(memory_cap_bytes: int):
    # RLIMIT_AS is flaky-to-broken on macOS (setrlimit reliably raises
    # "current limit exceeds maximum limit" even though getrlimit reports
    # both limits as unlimited -- a longstanding Darwin quirk, not a bug in
    # this code). Enforce it only on Linux; rely on the wall-clock timeout
    # elsewhere on macOS. Revisit if this is ever run in CI on Linux, where
    # it should work and should be turned on for real.
    if platform.system() != "Linux":
        return None

    def _set_limits() -> None:
        resource.setrlimit(resource.RLIMIT_AS, (memory_cap_bytes, memory_cap_bytes))

    return _set_limits


def _build_command(
    lean_project_dir: Path, file_path: Path, *, no_network: bool
) -> list[str]:
    base = [find_lake(), "env", "lean", str(file_path)]
    if no_network and platform.system() == "Darwin":
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sb", delete=False
        ) as f:
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
    memory_cap_bytes: int = DEFAULT_MEMORY_CAP_BYTES,
    no_network: bool = True,
) -> CompileResult:
    """Compile `file_path` with `lake env lean`, in `lean_project_dir`.

    `file_path` need not live inside `lean_project_dir`, but the module it
    declares must resolve against that project's dependencies (Mathlib etc.)
    for imports to succeed.
    """
    command = _build_command(lean_project_dir, file_path, no_network=no_network)
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            cwd=lean_project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            preexec_fn=_memory_cap_preexec(memory_cap_bytes),
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
