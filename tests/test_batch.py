"""Two-phase batch runner and report: resume semantics, error handling,
following a live run, summaries.

No model server and no Lean: generation goes through a fake `complete_fn`,
grading through a fake `grade_fn`.
"""

import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from physproofbench.batch import (
    GenerationConfig,
    build_plan,
    generate_run,
    grade_run,
    read_plan,
    sample_seed,
)
from physproofbench.models.openai_client import Completion
from physproofbench.render import load_core_source
from physproofbench.report import pass_at_k, summarize, write_report

REPO = Path(__file__).parent.parent
ITEMS = REPO / "items"
LEAN = REPO / "lean"


def _plan(config, items=("SM_01_009_001", "SM_01_E06_001"), samples=2,
          conditions=("no_nl_proof", "with_nl_proof")):
    return build_plan(config=config, item_ids=list(items), conditions=list(conditions),
                      samples=samples, items_dir=ITEMS, lean_project_dir=LEAN)


class FakeModel:
    def __init__(self, fail_times=0):
        self.calls = []
        self.fail_times = fail_times

    def __call__(self, prompt, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) <= self.fail_times:
            raise ConnectionError("server down")
        return Completion(text="```lean\ntheorem x : True := trivial\n```",
                          model="m", finish_reason="stop", reasoning="think",
                          prompt_tokens=10, completion_tokens=20, elapsed_s=1.0)


def _run(tmp_path, config, plan, model, **kw):
    return generate_run(config=config, plan=plan, run_dir=tmp_path, concurrency=2,
                        complete_fn=model, log=lambda s: None, **kw)


class FakeGrader:
    """Stands in for grading.grade_submission; passes the seed item only."""

    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail
        self.lock = threading.Lock()

    def __call__(self, **kwargs):
        with self.lock:
            self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("lake exploded")
        verdict = "pass" if kwargs["decl_name"] == "shannonEntropy_le_log_card" else "compile_fail"
        return SimpleNamespace(to_dict=lambda: {"verdict": verdict, "grading_version": "2",
                                                "gate_failures": []})


def _grade(tmp_path, grader, **kw):
    return grade_run(run_dir=tmp_path, items_dir=ITEMS, lean_project_dir=LEAN,
                     grade_fn=grader, log=lambda s: None, **kw)


def test_plan_skips_with_nl_proof_when_source_has_no_proof():
    plan = _plan(GenerationConfig(model="m"))
    # SM_01_E06_001 is an exercise: no nl.proof, so no A2 cell.
    assert ("SM_01_E06_001", "with_nl_proof") not in plan.prompts
    assert any(s[:2] == ("SM_01_E06_001", "with_nl_proof") for s in plan.skipped)
    assert len(plan.tasks) == 3 * 2


def test_resume_skips_finished_samples(tmp_path):
    config = GenerationConfig(model="m")
    plan = _plan(config)
    first = FakeModel()
    _run(tmp_path, config, plan, first)
    assert len(first.calls) == 6
    sample = tmp_path / "samples/SM_01_009_001/no_nl_proof/000"
    record = json.loads((sample / "completion.json").read_text())
    assert record["finish_reason"] == "stop"
    assert (sample / "candidate.lean").read_text() == "theorem x : True := trivial\n"
    assert (sample / "reasoning.txt").read_text() == "think"

    again = FakeModel()
    _run(tmp_path, config, plan, again)
    assert again.calls == []

    # Extending the run to more samples generates only the new ones.
    more = FakeModel()
    _run(tmp_path, config, _plan(config, samples=3), more)
    assert len(more.calls) == 3


def test_changed_prompt_is_regenerated(tmp_path):
    config = GenerationConfig(model="m")
    plan = _plan(config, items=("SM_01_009_001",), conditions=("no_nl_proof",), samples=1)
    _run(tmp_path, config, plan, FakeModel())
    key = ("SM_01_009_001", "no_nl_proof")
    plan.prompts[key].hash = "different"
    redo = FakeModel()
    _run(tmp_path, config, plan, redo)
    assert len(redo.calls) == 1


def test_resume_refuses_different_generation_settings(tmp_path):
    config = GenerationConfig(model="m")
    _run(tmp_path, config, _plan(config, samples=1), FakeModel())
    hotter = GenerationConfig(model="m", temperature=1.0)
    with pytest.raises(ValueError, match="temperature"):
        _run(tmp_path, hotter, _plan(hotter, samples=1), FakeModel())


def test_consecutive_errors_abort_and_resume_retries(tmp_path):
    config = GenerationConfig(model="m")
    plan = _plan(config, items=("SM_01_009_001",), conditions=("no_nl_proof",), samples=4)
    down = FakeModel(fail_times=100)
    stats = generate_run(config=config, plan=plan, run_dir=tmp_path, concurrency=1,
                         max_consecutive_errors=2, complete_fn=down, log=lambda s: None)
    assert stats.aborted
    assert len(down.calls) == 2  # stopped sending after two failures in a row
    assert json.loads((tmp_path / "status.json").read_text())["state"] == "aborted"
    assert (tmp_path / "samples/SM_01_009_001/no_nl_proof/000/error.json").exists()

    up = FakeModel()
    _run(tmp_path, config, plan, up)
    assert len(up.calls) == 4
    assert not (tmp_path / "samples/SM_01_009_001/no_nl_proof/000/error.json").exists()


def test_sampling_settings_reach_the_request(tmp_path):
    config = GenerationConfig(model="m", temperature=0.7, top_p=0.9, top_k=5,
                              max_tokens=1000, enable_thinking=True, seed=3)
    plan = _plan(config, items=("SM_01_009_001",), conditions=("no_nl_proof",), samples=2)
    model = FakeModel()
    _run(tmp_path, config, plan, model)
    call = model.calls[0]
    assert (call["temperature"], call["top_p"], call["top_k"], call["max_tokens"],
            call["enable_thinking"]) == (0.7, 0.9, 5, 1000, True)
    seeds = sorted(c["seed"] for c in model.calls)
    expected = sorted(sample_seed(3, t) for t in plan.tasks)
    assert seeds == expected and seeds[0] != seeds[1]


def test_core_source_in_prompt_by_default():
    with_core = _plan(GenerationConfig(model="m"), items=("SM_03_005_001",),
                      conditions=("no_nl_proof",), samples=1)
    text = with_core.prompts[("SM_03_005_001", "no_nl_proof")].text
    assert "def isingPressureFree" in text and "def spin" in text
    assert "do not copy or redefine" in text
    without = _plan(GenerationConfig(model="m", core_in_context=False),
                    items=("SM_03_005_001",), conditions=("no_nl_proof",), samples=1)
    assert "def isingPressureFree" not in without.prompts[("SM_03_005_001", "no_nl_proof")].text


def test_load_core_source_orders_dependencies_first():
    src = load_core_source(LEAN, ["PhysProofBench.Core.Ising"])
    assert src.index("Core/Spin.lean") < src.index("Core/Ising.lean")


def test_pass_at_k():
    assert pass_at_k(4, 0, 1) == 0.0
    assert pass_at_k(4, 4, 4) == 1.0
    assert pass_at_k(4, 1, 1) == pytest.approx(0.25)
    assert pass_at_k(4, 1, 4) == 1.0
    assert pass_at_k(4, 2, 2) == pytest.approx(1 - 1 / 6)
    assert pass_at_k(2, 1, 4) is None


def test_report_from_stored_results(tmp_path, monkeypatch):
    config = GenerationConfig(model="m")
    plan = _plan(config, samples=2)
    _run(tmp_path, config, plan, FakeModel())
    # Grade by hand: one pass for the seed's A1 cell, gate_fail elsewhere.
    for task in plan.tasks:
        d = task.dir(tmp_path)
        sha = json.loads((d / "completion.json").read_text())["candidate_sha"]
        verdict = "pass" if (task.item_id, task.condition, task.index) == (
            "SM_01_009_001", "no_nl_proof", 0) else "gate_fail"
        (d / "grade.json").write_text(json.dumps({
            "verdict": verdict, "candidate_sha": sha,
            "gate_failures": [] if verdict == "pass" else ["gate: statement_edited"],
            "statement_edit_diagnostic": None if verdict == "pass" else {"would_pass": True},
        }))
    summary = summarize(tmp_path, ITEMS)
    cell = summary["per_item_condition"]["SM_01_009_001|no_nl_proof"]
    assert cell["passed"] == 1 and cell["pass@1"] == pytest.approx(0.5)
    assert cell["pass@2"] == 1.0
    assert summary["gate_failure_reasons"] == {"gate: statement_edited": 5}
    assert summary["totals"]["statement_edited_would_pass"] == 5
    md = write_report(tmp_path, ITEMS)
    assert "SM_01_E06_001" in md and (tmp_path / "summary.json").exists()


def test_generate_writes_plan_and_status(tmp_path):
    config = GenerationConfig(model="m")
    _run(tmp_path, config, _plan(config, samples=1), FakeModel())
    tasks, gold_shas = read_plan(tmp_path)
    assert len(tasks) == 3 and set(gold_shas) == {"SM_01_009_001", "SM_01_E06_001"}
    assert json.loads((tmp_path / "status.json").read_text())["state"] == "finished"
    # Extending the run merges into plan.json rather than replacing it.
    _run(tmp_path, config, _plan(config, items=("SM_03_005_001",), samples=1), FakeModel())
    tasks, gold_shas = read_plan(tmp_path)
    assert len(tasks) == 5 and "SM_03_005_001" in gold_shas


def test_grade_run_grades_once_and_resumes(tmp_path):
    config = GenerationConfig(model="m")
    _run(tmp_path, config, _plan(config, samples=2), FakeModel())
    grader = FakeGrader()
    stats = _grade(tmp_path, grader)
    assert stats.graded == 6 and stats.passed == 4
    assert all(c["diagnose_statement_edits"] for c in grader.calls)
    again = FakeGrader()
    assert _grade(tmp_path, again).graded == 0 and again.calls == []


def test_grader_errors_are_recorded_retried_later_but_not_looped(tmp_path):
    config = GenerationConfig(model="m")
    _run(tmp_path, config, _plan(config, items=("SM_01_009_001",),
                                  conditions=("no_nl_proof",), samples=2), FakeModel())
    broken = FakeGrader(fail=True)
    _grade(tmp_path, broken, follow=True, poll_interval=0.01)
    assert len(broken.calls) == 2  # once each, no retry loop within a call
    grade = json.loads((tmp_path / "samples/SM_01_009_001/no_nl_proof/000/grade.json").read_text())
    assert grade["verdict"] == "grader_error" and "lake exploded" in grade["error"]
    fixed = FakeGrader()
    assert _grade(tmp_path, fixed).passed == 2


def test_grade_run_skips_items_whose_gold_changed(tmp_path):
    config = GenerationConfig(model="m")
    _run(tmp_path, config, _plan(config, samples=1), FakeModel())
    plan_path = tmp_path / "plan.json"
    stored = json.loads(plan_path.read_text())
    stored["gold_shas"]["SM_01_E06_001"] = "not-this-checkout"
    plan_path.write_text(json.dumps(stored))
    stats = _grade(tmp_path, FakeGrader())
    assert stats.gold_mismatch == ["SM_01_E06_001"]
    assert stats.graded == 2  # the seed item's two cells only


def test_grade_run_follows_a_live_generation(tmp_path):
    config = GenerationConfig(model="m")
    plan = _plan(config, items=("SM_01_009_001",), conditions=("no_nl_proof",), samples=3)

    class SlowModel(FakeModel):
        def __call__(self, prompt, **kwargs):
            time.sleep(0.3)
            return super().__call__(prompt, **kwargs)

    # Generation starts first (writes plan/status), grading follows it.
    gen = threading.Thread(target=generate_run, kwargs=dict(
        config=config, plan=plan, run_dir=tmp_path, concurrency=1,
        complete_fn=SlowModel(), log=lambda s: None))
    gen.start()
    while not (tmp_path / "status.json").exists():
        time.sleep(0.01)
    grader = FakeGrader()
    stats = _grade(tmp_path, grader, follow=True, poll_interval=0.05)
    gen.join()
    assert stats.graded == 3 and stats.passed == 3


def test_follow_stops_when_generator_status_goes_stale(tmp_path):
    config = GenerationConfig(model="m")
    _run(tmp_path, config, _plan(config, items=("SM_01_009_001",),
                                  conditions=("no_nl_proof",), samples=1), FakeModel())
    # Simulate a generator killed without recording it: "generating", long ago.
    (tmp_path / "status.json").write_text(json.dumps({"state": "generating", "updated": 0}))
    stats = _grade(tmp_path, FakeGrader(), follow=True, poll_interval=0.01, stale_after=60)
    assert stats.graded == 1


def test_follow_waits_for_generate_to_create_the_run(tmp_path):
    run_dir = tmp_path / "not-yet"
    config = GenerationConfig(model="m")
    plan = _plan(config, items=("SM_01_009_001",), conditions=("no_nl_proof",), samples=1)

    def late_generate():
        time.sleep(0.3)
        generate_run(config=config, plan=plan, run_dir=run_dir, complete_fn=FakeModel(),
                     log=lambda s: None)

    gen = threading.Thread(target=late_generate)
    gen.start()
    stats = grade_run(run_dir=run_dir, items_dir=ITEMS, lean_project_dir=LEAN,
                      grade_fn=FakeGrader(), follow=True, poll_interval=0.05,
                      log=lambda s: None)
    gen.join()
    assert stats.graded == 1
