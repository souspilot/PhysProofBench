"""End-to-end check that a generated L2.3 checker file actually compiles.

Unlike test_audit_parsing.py (which tests the text-splicing logic in
isolation), this proves the generated Lean source -- including the
namespace-wrapped submission module it depends on -- is real, typecheckable
Lean, not just plausible-looking text.
"""

import subprocess
from pathlib import Path

from physproofbench.lean.audit import build_statement_preservation_source, namespace_wrap
from physproofbench.lean.sandbox import compile_file, find_lake

FIXTURES = Path(__file__).parent / "fixtures"
GOLD = FIXTURES / "gold.lean"
SUBMISSIONS = FIXTURES / "submissions"

SUBMISSION_MODULE = "GraderFixtures.Submission"


def _submission_path(lean_project_dir: Path) -> Path:
    return lean_project_dir / "GraderFixtures" / "Submission.lean"


def _checker_path(lean_project_dir: Path) -> Path:
    return lean_project_dir / "GraderFixtures" / "Checker.lean"


def test_statement_preservation_checker_compiles_for_correct_submission(
    lean_project_dir,
):
    submission_path = _submission_path(lean_project_dir)
    checker_path = _checker_path(lean_project_dir)
    try:
        wrapped = namespace_wrap(
            (SUBMISSIONS / "correct.lean").read_text(encoding="utf-8"),
            SUBMISSION_MODULE,
        )
        submission_path.write_text(wrapped, encoding="utf-8")
        # The checker imports the submission module by name, which needs an
        # actual .olean on the search path -- `lake env lean` alone won't
        # build it.
        subprocess.run(
            [find_lake(), "build", SUBMISSION_MODULE],
            cwd=lean_project_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        checker_src = build_statement_preservation_source(
            submission_module=SUBMISSION_MODULE,
            gold_text=GOLD.read_text(encoding="utf-8"),
            decl_name="add_comm'",
        )
        checker_path.write_text(checker_src, encoding="utf-8")

        result = compile_file(lean_project_dir, checker_path)
        assert result.ok, result.stdout + result.stderr
    finally:
        submission_path.unlink(missing_ok=True)
        checker_path.unlink(missing_ok=True)


def test_statement_preservation_checker_rejects_weaker_submission(lean_project_dir):
    """A submission proving a strictly weaker statement must NOT typecheck
    against the gold's stronger type."""
    submission_path = _submission_path(lean_project_dir)
    checker_path = _checker_path(lean_project_dir)
    try:
        wrapped = namespace_wrap(
            "theorem add_comm' (a b : Nat) : a + b = a + b := by rfl\n",
            SUBMISSION_MODULE,
        )
        submission_path.write_text(wrapped, encoding="utf-8")
        subprocess.run(
            [find_lake(), "build", SUBMISSION_MODULE],
            cwd=lean_project_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        checker_src = build_statement_preservation_source(
            submission_module=SUBMISSION_MODULE,
            gold_text=GOLD.read_text(encoding="utf-8"),
            decl_name="add_comm'",
        )
        checker_path.write_text(checker_src, encoding="utf-8")

        result = compile_file(lean_project_dir, checker_path)
        assert not result.ok
    finally:
        submission_path.unlink(missing_ok=True)
        checker_path.unlink(missing_ok=True)
