import subprocess
from pathlib import Path

import pytest

from physproofbench.lean.sandbox import find_lake

FIXTURES = Path(__file__).parent / "fixtures"
LEAN_PROJECT = FIXTURES / "lean_project"


@pytest.fixture(scope="session")
def lean_available() -> bool:
    try:
        find_lake()
        return True
    except FileNotFoundError:
        return False


@pytest.fixture(scope="session")
def lean_project_dir(lean_available: bool) -> Path:
    if not lean_available:
        pytest.skip("lake not found on PATH or in ~/.elan/bin")
    subprocess.run(
        [find_lake(), "build"],
        cwd=LEAN_PROJECT,
        check=True,
        capture_output=True,
        text=True,
    )
    return LEAN_PROJECT
