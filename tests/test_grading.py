"""The M0 acceptance fixture set (plan.md §10):

`physproofbench grade` must classify a hand-written correct submission and
three hand-written cheating submissions (a `sorry`, a `native_decide`, a
tampered statement) correctly. These fixtures live in tests/fixtures/
forever -- do not delete or "clean up" them even if they look redundant with
newer tests.
"""

from pathlib import Path

import pytest

from physproofbench.grading import grade_submission

FIXTURES = Path(__file__).parent / "fixtures"
GOLD = FIXTURES / "gold.lean"
SUBMISSIONS = FIXTURES / "submissions"


@pytest.mark.parametrize(
    "filename,expected_verdict",
    [
        ("correct.lean", "pass"),
        ("has_sorry.lean", "gate_fail"),
        ("native_decide.lean", "gate_fail"),
        ("tampered_statement.lean", "gate_fail"),
    ],
)
def test_m0_fixture_classified_correctly(lean_project_dir, filename, expected_verdict):
    report = grade_submission(
        lean_project_dir=lean_project_dir,
        submission_path=SUBMISSIONS / filename,
        gold_path=GOLD,
        decl_name="add_comm'",
        mode="proof",
    )
    assert report.verdict == expected_verdict, (
        f"{filename}: expected {expected_verdict}, got {report.verdict} "
        f"(gate={report.gate.failures}, "
        f"compile_ok={report.compile.ok if report.compile else None}, "
        f"audit={report.axiom_audit.failures if report.axiom_audit else None})"
    )


def test_correct_submission_has_empty_axiom_set(lean_project_dir):
    report = grade_submission(
        lean_project_dir=lean_project_dir,
        submission_path=SUBMISSIONS / "correct.lean",
        gold_path=GOLD,
        decl_name="add_comm'",
        mode="proof",
    )
    assert report.verdict == "pass"
    assert report.axiom_audit is not None
    assert report.axiom_audit.axioms == []
