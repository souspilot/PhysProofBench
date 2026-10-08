"""Compiler-feedback repair rounds: feedback text, the round driver, and its
interplay with a concurrently following grader. Fake model, fake grader."""

import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from physproofbench.batch import (
    FORCE_ANSWER_PHRASE,
    GenerationConfig,
    build_plan,
    generate_run,
    grade_run,
)
from physproofbench.models.openai_client import Completion
from physproofbench.repair import (
    RepairConfig,
    build_feedback,
    compiler_errors,
    repair_run,
)
from physproofbench.report import summarize

REPO = Path(__file__).parent.parent
ITEMS, LEAN = REPO / "items", REPO / "lean"

# Shape of a real failure from the first pilot (SM_01_E02_001).
LEAN_OUTPUT = """/scratch/x/lean/tmpqq.lean:11:8: error: Tactic `introN` failed: There are no additional binders or `let` bindings in the goal to introduce

S : ℝ × ℝ × ℝ → ℝ
⊢ ConcaveOn ℝ PosOrthant S
/scratch/x/lean/tmpqq.lean:20:2: warning: unused variable `h`
/scratch/x/lean/tmpqq.lean:25:20: error(lean.unknownIdentifier): Unknown identifier `univ`
'entropy_concave' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]"""


def test_compiler_errors_parses_errors_with_goals_and_drops_warnings():
    errs = compiler_errors(LEAN_OUTPUT)
    assert [(l, c) for l, c, _ in errs] == [(11, 8), (25, 20)]
    assert "⊢ ConcaveOn ℝ PosOrthant S" in errs[0][2]
    assert errs[1][2].startswith("[lean.unknownIdentifier] Unknown identifier `univ`")
    assert "depends on axioms" not in errs[1][2]


def test_feedback_for_compile_fail_and_gate_fail():
    fb = build_feedback({"verdict": "compile_fail", "compiler_output": LEAN_OUTPUT},
                        "import Mathlib\ntheorem x : True := by\n  trivial\n")
    assert "Lean reported 2 error(s)" in fb and "line 11, column 8" in fb
    assert "\n2 | theorem x : True := by" in fb
    assert "/scratch" not in fb  # no grader paths leak into the prompt
    fb = build_feedback({"verdict": "gate_fail", "gate_failures": ["gate: statement_edited"]},
                        "lemma h : True := trivial\n")
    assert "put helper lemmas inside the proof with `have`" in fb


class Model:
    """Chat stand-in: initial answers are wrong; repair answers say `fixed`
    unless `never_fix`. With `think_too_long`, repair rounds run out of
    budget mid-thought (exercising the forced-answer path)."""

    def __init__(self, never_fix=False, think_too_long=False):
        self.never_fix, self.think_too_long = never_fix, think_too_long
        self.calls, self.lock = [], threading.Lock()

    def __call__(self, prompt, **kw):
        with self.lock:
            self.calls.append(kw)
        if kw.get("messages") is None:
            return Completion(text="```lean\nwrong\n```", model="m", finish_reason="stop")
        if self.think_too_long:
            return Completion(text="", model="m", finish_reason="length", reasoning="hmm")
        body = "still wrong" if self.never_fix else "fixed"
        return Completion(text=f"```lean\n{body}\n```", model="m", finish_reason="stop",
                          reasoning="I see the error")


class Continuation:
    def __init__(self):
        self.calls = []

    def __call__(self, prompt, prefix, **kw):
        self.calls.append({"prefix": prefix, **kw})
        return Completion(text="```lean\nfixed\n```", model="m", finish_reason="stop")


def grader(**kw):
    text = Path(kw["submission_path"]).read_text()
    if "fixed" in text:
        return SimpleNamespace(to_dict=lambda: {"verdict": "pass", "grading_version": "2"})
    return SimpleNamespace(to_dict=lambda: {
        "verdict": "compile_fail", "grading_version": "2", "compiler_output": LEAN_OUTPUT})


def _graded_source(tmp_path, samples=1):
    src = tmp_path / "src"
    config = GenerationConfig(model="m")
    plan = build_plan(config=config, item_ids=["SM_01_009_001"], conditions=["no_nl_proof"],
                      samples=samples, items_dir=ITEMS, lean_project_dir=LEAN)
    generate_run(config=config, plan=plan, run_dir=src, complete_fn=Model(), log=lambda s: None)
    grade_run(run_dir=src, items_dir=ITEMS, lean_project_dir=LEAN, grade_fn=grader,
              log=lambda s: None)
    return src


def _run_both(src, dst, rcfg, model, cont=None):
    """GPU side and CPU side concurrently, both following."""
    out = {}

    def gpu():
        out["repair"] = repair_run(source_dir=src, run_dir=dst, rcfg=rcfg, follow=True,
                                   poll_interval=0.05, chat_fn=model,
                                   continue_fn=cont or Continuation(), log=lambda s: None)

    t = threading.Thread(target=gpu)
    t.start()
    while not (dst / "plan.json").exists():
        pass
    out["grade"] = grade_run(run_dir=dst, items_dir=ITEMS, lean_project_dir=LEAN,
                             grade_fn=grader, follow=True, poll_interval=0.05,
                             log=lambda s: None)
    t.join(timeout=30)
    assert not t.is_alive()
    return out


def test_repair_fixes_in_one_round(tmp_path):
    src = _graded_source(tmp_path, samples=2)
    dst = tmp_path / "rep"
    model = Model()
    out = _run_both(src, dst, RepairConfig(rounds=3), model)
    assert out["repair"].attempts == 2 and out["grade"].passed == 2
    d = dst / "samples/SM_01_009_001/no_nl_proof/000"
    assert json.loads((d / "completion.json").read_text())["repair_round"] == 1
    assert json.loads((d / "attempts/0/grade.json").read_text())["verdict"] == "compile_fail"
    feedback = (d / "attempts/0/feedback.txt").read_text()
    assert "line 11, column 8" in feedback
    repair_call = [c for c in model.calls if c.get("messages")][0]
    roles = [m["role"] for m in repair_call["messages"]]
    assert roles == ["user", "assistant", "user"]
    assert repair_call["messages"][1]["content"] == "```lean\nwrong\n```"
    assert repair_call["messages"][2]["content"] == feedback
    # Source run untouched; report shows the per-round gain.
    assert json.loads((src / "samples/SM_01_009_001/no_nl_proof/000/completion.json")
                      .read_text()).get("repair_round") is None
    rounds = summarize(dst, ITEMS)["repair"]["by_round"]
    assert rounds[0]["no_nl_proof"]["pass@1"] == 0.0
    assert rounds[1]["no_nl_proof"]["pass@1"] == 1.0
    assert json.loads((dst / "status.json").read_text())["state"] == "finished"


def test_repair_stops_after_rounds(tmp_path):
    src = _graded_source(tmp_path)
    dst = tmp_path / "rep"
    out = _run_both(src, dst, RepairConfig(rounds=2), Model(never_fix=True))
    d = dst / "samples/SM_01_009_001/no_nl_proof/000"
    assert out["repair"].attempts == 2 and out["grade"].passed == 0
    assert json.loads((d / "completion.json").read_text())["repair_round"] == 2
    assert sorted(p.name for p in (d / "attempts").iterdir()) == ["0", "1"]
    assert out["repair"].states == {"exhausted": 1}


def test_repair_forces_an_answer_when_a_round_runs_out(tmp_path):
    src = _graded_source(tmp_path)
    cont = Continuation()
    out = _run_both(src, tmp_path / "rep", RepairConfig(rounds=1), Model(think_too_long=True),
                    cont)
    assert out["grade"].passed == 1
    call = cont.calls[0]
    assert call["prefix"] == "<think>\nhmm" + FORCE_ANSWER_PHRASE
    assert [m["role"] for m in call["messages"]] == ["user", "assistant", "user"]
    record = json.loads((tmp_path / "rep/samples/SM_01_009_001/no_nl_proof/000/completion.json")
                        .read_text())
    assert record["forced_answer"] is True


def test_repair_refuses_changed_settings(tmp_path):
    src = _graded_source(tmp_path)
    dst = tmp_path / "rep"
    repair_run(source_dir=src, run_dir=dst, rcfg=RepairConfig(rounds=1), follow=False,
               chat_fn=Model(), continue_fn=Continuation(), log=lambda s: None)
    with pytest.raises(ValueError, match="refusing to continue"):
        repair_run(source_dir=src, run_dir=dst, rcfg=RepairConfig(rounds=2), follow=False,
                   chat_fn=Model(), continue_fn=Continuation(), log=lambda s: None)
